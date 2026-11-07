"""HTTP server for the browser UI: static files, a JSON API, a Server-Sent Events stream and team/player images."""
import json
import mimetypes
import os
import queue
import re
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .hub import EventHub
from .runner import SimRunner
from .live import team_identity

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, "static")
PROJECT = os.path.dirname(ROOT)
LOGO_DIR = os.path.join(PROJECT, "nba_logo_cache")
HEADSHOT_DIR = os.path.join(PROJECT, "nba_headshot_cache")


_headshot_lock = threading.Lock()
_headshot_jobs = {}        # name -> "pending" | "failed"


def _find_espn_image(value):
    if isinstance(value, dict):
        href = value.get("href")
        if isinstance(href, str) and "espncdn.com" in href and ("headshot" in href or "players" in href):
            return href
        for child in value.values():
            found = _find_espn_image(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_espn_image(child)
            if found:
                return found
    return None


def _fetch(url: str, path: str, timeout: int = 10):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(path + ".part", "wb") as out:
        out.write(resp.read())
    os.replace(path + ".part", path)


def _headshot_sources(name: str):
    """Where the Tk app looks for a player's picture, in its order: a direct URL, the NBA.com id, then an ESPN search."""
    import media_ids
    safe = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    url = media_ids.PLAYER_HEADSHOT_URLS.get(name)
    if url:
        yield os.path.join(HEADSHOT_DIR, f"{safe}_override.png"), url
    pid = media_ids.PLAYER_HEADSHOT_IDS.get(name)
    if pid:
        yield os.path.join(HEADSHOT_DIR, f"{pid}.png"), f"https://cdn.nba.com/headshots/nba/latest/1040x760/{pid}.png"
    yield os.path.join(HEADSHOT_DIR, f"{safe}_espn.png"), None


def _cached_headshot(name: str):
    for path, _url in _headshot_sources(name):
        if os.path.isfile(path):
            return path
    return None


def _download_headshot(name: str):
    import urllib.request
    try:
        for path, url in _headshot_sources(name):
            if url is None:   # ESPN search
                search = f"https://site.api.espn.com/apis/common/v3/search?query={urllib.parse.quote(name)}&limit=8"
                req = urllib.request.Request(search, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    url = _find_espn_image(json.load(resp))
                if not url:
                    continue
            try:
                _fetch(url, path)
                with _headshot_lock:
                    _headshot_jobs.pop(name, None)
                return
            except Exception:
                continue
        raise LookupError(name)
    except Exception:
        with _headshot_lock:
            _headshot_jobs[name] = "failed"


def _num(x, nd=1):
    return round(x, nd) if isinstance(x, (int, float)) else x


def season_payload(runner):
    sec = runner.sections or {}
    standings = sec.get("_season_standings") or runner.season.get("standings") or []
    rows = []
    for r in standings:
        ident = team_identity(r.get("team", ""))
        rows.append({**{k: v for k, v in r.items() if isinstance(v, (int, float, str))}, **{"short": ident["short"], "logo": ident["logo"], "color": ident["color"], "initials": ident["initials"], "year": ident["year"]}})
    awards = sec.get("_season_awards_table") or []
    games = sec.get("_season_games") or []
    return {
        "state": runner.season_state(), "standings": rows, "awards": awards,
        "races": runner.season.get("races") or {},
        "allStar": bool(sec.get("_all_star_game")),
        "games": len(games),
    }


def players_payload(runner):
    sec = runner.sections or {}
    totals = sec.get("_season_player_totals") or {}
    out = []
    for team, players in totals.items():
        ident = team_identity(team)
        for name, st in players.items():
            g = max(1, st.get("games", 0))
            mins = st.get("minutes", 0) / 60.0
            fga, fta, tpa = st.get("fga", 0), st.get("fta", 0), st.get("tpa", 0)
            out.append({
                "name": name, "team": team, "short": ident["short"], "logo": ident["logo"], "color": ident["color"], "gp": st.get("games", 0),
                "mpg": _num(mins / g), "pts": _num(st.get("pts", 0) / g), "reb": _num(st.get("reb", 0) / g), "ast": _num(st.get("ast", 0) / g),
                "stl": _num(st.get("stl", 0) / g), "blk": _num(st.get("blk", 0) / g), "tov": _num(st.get("tov", 0) / g),
                "fgp": _num(100 * st.get("fgm", 0) / fga) if fga else None, "tpp": _num(100 * st.get("tpm", 0) / tpa) if tpa else None,
                "ftp": _num(100 * st.get("ftm", 0) / fta) if fta else None,
                "ts": _num(100 * st.get("pts", 0) / (2 * (fga + 0.44 * fta))) if (fga + fta) else None,
                "pm": _num(st.get("plus_minus", 0) / g), "fga": _num(fga / g), "tpa": _num(tpa / g),
            })
    return {"players": out}


def build_app():
    hub = EventHub()
    runner = SimRunner(hub)

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, format, *args):
            return

        # ------------------------------------------------------------ helpers
        def _send(self, status: int, body: bytes, content_type: str, cache: str = "no-store"):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", cache)
            self.end_headers()
            self.wfile.write(body)

        def _json(self, payload, status: int = 200):
            self._send(status, json.dumps(payload, default=str).encode("utf-8"), "application/json; charset=utf-8")

        def _file(self, path: str, cache: str = "no-cache"):
            if not os.path.isfile(path):
                self._send(404, b"not found", "text/plain")
                return
            with open(path, "rb") as fh:
                body = fh.read()
            ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
            if ctype.startswith("text/") or ctype in ("application/javascript",):
                ctype += "; charset=utf-8"
            self._send(200, body, ctype, cache)

        def _body(self):
            length = int(self.headers.get("Content-Length", "0") or 0)
            raw = self.rfile.read(length) if length else b""
            try:
                return json.loads(raw.decode("utf-8") or "{}")
            except ValueError:
                return {}

        # --------------------------------------------------------------- GET
        def do_GET(self):
            url = urllib.parse.urlparse(self.path)
            path, params = url.path, urllib.parse.parse_qs(url.query)
            if path == "/" or path == "/index.html":
                return self._file(os.path.join(STATIC, "index.html"))
            if path.startswith("/static/"):
                target = os.path.normpath(os.path.join(STATIC, path[len("/static/"):]))
                if not target.startswith(STATIC):
                    return self._send(403, b"forbidden", "text/plain")
                return self._file(target)
            if path == "/api/meta":
                return self._json(runner.meta())
            if path == "/api/state":
                return self._json(runner.state())
            if path == "/api/bracket":
                return self._json(runner.bracket or {})
            if path == "/api/season":
                return self._json(season_payload(runner))
            if path == "/api/season/players":
                return self._json(players_payload(runner))
            if path == "/api/sections":
                return self._json(runner.sections)
            if path == "/media/logo":
                code = re.sub(r"[^a-z]", "", (params.get("code") or [""])[0].lower())
                return self._file(os.path.join(LOGO_DIR, f"{code}.png"), "max-age=86400")
            if path == "/media/headshot":
                name = (params.get("name") or [""])[0].strip()
                cached = _cached_headshot(name) if name else None
                if cached:
                    return self._file(cached, "max-age=86400")
                if not name:
                    return self._send(404, b"no headshot", "text/plain")
                with _headshot_lock:
                    job = _headshot_jobs.get(name)
                    if job is None:
                        _headshot_jobs[name] = "pending"
                        threading.Thread(target=_download_headshot, args=(name,), daemon=True).start()
                        job = "pending"
                if job == "pending":
                    return self._send(202, b"downloading", "text/plain")   # the page asks again in a few seconds
                return self._send(404, b"no headshot", "text/plain")
            if path == "/api/events":
                return self._events()
            self._send(404, b"not found", "text/plain")

        def _events(self):
            client = hub.subscribe()
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            try:
                self.wfile.write(b"retry: 1500\n\n")
                self.wfile.flush()
                while True:
                    try:
                        event = client.get(timeout=15)
                        payload = "data: " + json.dumps(event, default=str) + "\n\n"
                    except queue.Empty:
                        payload = ": keep-alive\n\n"
                    self.wfile.write(payload.encode("utf-8"))
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            finally:
                hub.unsubscribe(client)

        # -------------------------------------------------------------- POST
        def do_POST(self):
            path = urllib.parse.urlparse(self.path).path
            data = self._body()
            if path == "/api/start":
                error = runner.start(data.get("mode", "Game"), data.get("teamA", ""), data.get("teamB", ""), data.get("rules", "NBA"))
                return self._json({"ok": error is None, "error": error}, 200 if error is None else 400)
            if path == "/api/control":
                error = runner.control(data.get("action", ""), data.get("value"))
                return self._json({"ok": error is None, "error": error}, 200 if error is None else 400)
            self._send(404, b"not found", "text/plain")

    return Handler, runner


def run(open_browser: bool = True, port: int = 8790):
    handler, runner = build_app()
    server = None
    for candidate in range(port, port + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), handler)
            break
        except OSError:
            continue
    if server is None:
        print("The browser UI could not find an open local port.")
        return
    server.daemon_threads = True
    url = f"http://127.0.0.1:{server.server_address[1]}"
    print(f"5v5 Simulator (browser UI) running at {url}  -  press Ctrl+C to stop.", file=sys.__stdout__)
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
