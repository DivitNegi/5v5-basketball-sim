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


def teams_payload(runner):
    sec = runner.sections or {}
    out = []
    for name, t in (sec.get("_season_team_totals") or {}).items():
        g = max(1, t.get("games", 0))
        ident = team_identity(name)
        poss = t["fga"] + 0.44 * t["fta"] - t["oreb"] + t["tov"]
        opp_poss = t.get("opp_fga", 0) + 0.44 * t.get("opp_fta", 0) - t.get("opp_oreb", 0) + t.get("opp_tov", 0)
        ortg = 100 * t["pts"] / poss if poss else 0
        drtg = 100 * t.get("opp_pts", 0) / opp_poss if opp_poss else 0
        out.append({
            "team": name, "short": ident["short"], "logo": ident["logo"], "color": ident["color"], "initials": ident["initials"],
            "w": t.get("wins", 0), "l": t.get("games", 0) - t.get("wins", 0),
            "pts": _num(t["pts"] / g), "opp": _num(t.get("opp_pts", 0) / g), "diff": _num((t["pts"] - t.get("opp_pts", 0)) / g),
            "ortg": _num(ortg), "drtg": _num(drtg), "net": _num(ortg - drtg), "pace": _num(0.5 * (poss + opp_poss) / g),
            "fgp": _num(100 * t["fgm"] / t["fga"]) if t["fga"] else None, "tpp": _num(100 * t["tpm"] / t["tpa"]) if t["tpa"] else None,
            "ftp": _num(100 * t["ftm"] / t["fta"]) if t["fta"] else None,
            "efg": _num(100 * (t["fgm"] + 0.5 * t["tpm"]) / t["fga"]) if t["fga"] else None,
            "ts": _num(100 * t["pts"] / (2 * (t["fga"] + 0.44 * t["fta"]))) if t["fga"] else None,
            "reb": _num(t["reb"] / g), "ast": _num(t["ast"] / g), "stl": _num(t["stl"] / g), "blk": _num(t["blk"] / g), "tov": _num(t["tov"] / g),
            "oppfg": _num(100 * t.get("opp_fgm", 0) / t["opp_fga"]) if t.get("opp_fga") else None,
            "opp3": _num(100 * t.get("opp_tpm", 0) / t["opp_tpa"]) if t.get("opp_tpa") else None,
        })
    return {"teams": out}


def advanced_payload(runner):
    sec = runner.sections or {}
    totals = sec.get("_season_player_totals") or {}
    teams = sec.get("_season_team_totals") or {}
    out = []
    for team, players in totals.items():
        tt = teams.get(team) or {}
        ident = team_identity(team)
        team_min = tt.get("games", 0) * 240.0
        tposs = tt.get("fga", 0) + 0.44 * tt.get("fta", 0) + tt.get("tov", 0)
        for name, st in players.items():
            mins = st.get("minutes", 0) / 60.0
            if mins < 100:
                continue
            fga, fta, tov = st.get("fga", 0), st.get("fta", 0), st.get("tov", 0)
            tsa = fga + 0.44 * fta
            usg = 100 * (tsa + tov) * (team_min / 5.0) / (mins * tposs) if mins and tposs else None
            out.append({
                "name": name, "team": team, "short": ident["short"], "logo": ident["logo"], "gp": st.get("games", 0), "mpg": _num(mins / max(1, st.get("games", 1))),
                "ts": _num(100 * st.get("pts", 0) / (2 * tsa)) if tsa else None,
                "efg": _num(100 * (st.get("fgm", 0) + 0.5 * st.get("tpm", 0)) / fga) if fga else None,
                "usg": _num(usg), "astto": _num(st.get("ast", 0) / max(1, tov), 2),
                "p36": _num(36 * st.get("pts", 0) / mins), "r36": _num(36 * st.get("reb", 0) / mins), "a36": _num(36 * st.get("ast", 0) / mins),
                "s36": _num(36 * (st.get("stl", 0) + st.get("blk", 0)) / mins),
                "ftr": _num(fta / fga, 2) if fga else None, "tpar": _num(st.get("tpa", 0) / fga, 2) if fga else None,
                "pm": _num(st.get("plus_minus", 0) / max(1, st.get("games", 1))),
            })
    return {"players": out}


def schedule_payload(runner, team):
    sec = runner.sections or {}
    rows = []
    for g in sec.get("_season_games") or []:
        if team and team not in (g.get("home"), g.get("away")):
            continue
        home = g.get("home") == team if team else True
        hs, as_ = g.get("home_score"), g.get("away_score")
        if team:
            mine, theirs = (hs, as_) if home else (as_, hs)
            rows.append({"n": len(rows) + 1, "gid": g.get("gid"), "home": home, "opp": g["away"] if home else g["home"], "mine": mine, "theirs": theirs, "win": mine is not None and mine > theirs})
        else:
            rows.append({"n": g.get("order"), "gid": g.get("gid"), "home": g["home"], "away": g["away"], "hs": hs, "as": as_})
    return {"games": rows}


def highs_payload(runner):
    sec = runner.sections or {}
    fields = sec.get("_season_game_log_fields") or []
    log = sec.get("_season_game_log") or []
    idx = {f: i for i, f in enumerate(fields)}
    cats = {"pts": "Points", "reb": "Rebounds", "ast": "Assists", "stl": "Steals", "blk": "Blocks", "tpm": "Threes made"}
    out = {}
    for key, label in cats.items():
        top = sorted(log, key=lambda r: r[idx[key]], reverse=True)[:10]
        out[key] = {"label": label, "rows": [{"player": r[idx["player"]], "team": r[idx["team"]], "opp": r[idx["opp"]], "value": r[idx[key]],
                                               "line": f"{r[idx['pts']]} pts, {r[idx['reb']]} reb, {r[idx['ast']]} ast", "result": r[idx["result"]]} for r in top]}
    return out


RATING_FIELDS = [
    ("Scoring", [("three_rating", "3PT"), ("mid_rating", "Mid-range"), ("rim_rating", "Finishing"), ("dunk_rating", "Dunking"), ("ft_rating", "Free throw")]),
    ("Playmaking", [("playmaking", "Playmaking"), ("ball_handle", "Ball handle"), ("usage", "Usage")]),
    ("Defense", [("perimeter_def", "Perimeter D"), ("interior_def", "Interior D"), ("steal", "Steals"), ("block", "Blocks")]),
    ("Rebounding & more", [("oreb", "Off. rebound"), ("dreb", "Def. rebound"), ("foul_draw", "Draws fouls"), ("clutchness", "Clutch")]),
    ("Tendencies", [("three_tendency", "Threes"), ("mid_tendency", "Mid-range"), ("drive_tendency", "Drives"), ("post_tendency", "Post"), ("dunk_tendency", "Dunks"), ("shot_tendency", "Shot-taking")]),
]


def _player_card(p):
    import sim_engine
    try:
        ovr = sim_engine.fantasy_ovr_uncapped(p)
    except Exception:
        ovr = None
    groups = []
    for title, fields in RATING_FIELDS:
        groups.append({"title": title, "items": [{"label": label, "value": round(float(getattr(p, key, 0) or 0) * 100)} for key, label in fields]})
    return {
        "name": p.name, "pos": getattr(p, "position", ""), "ovr": ovr, "height": getattr(p, "height", 0), "archetype": getattr(p, "archetype", ""),
        "badges": list(getattr(p, "badges", ()) or ()), "rookie": bool(getattr(p, "rookie", False)),
        "stamina": round(float(getattr(p, "stamina", 0) or 0) * 100), "groups": groups,
    }


def roster_payload(runner, team_name):
    factory = runner.factories.get(team_name)
    if not factory:
        return {"error": "Unknown team"}
    team = factory()
    import sim_engine
    try:
        sim_engine.assign_player_badges(team)
    except Exception:
        pass
    players = sorted((_player_card(p) for p in team.roster), key=lambda c: -(c["ovr"] or 0))
    ident = team_identity(team.name)
    return {"team": ident, "players": players}


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
            if path == "/api/season/teams":
                return self._json(teams_payload(runner))
            if path == "/api/season/advanced":
                return self._json(advanced_payload(runner))
            if path == "/api/season/highs":
                return self._json(highs_payload(runner))
            if path == "/api/season/schedule":
                return self._json(schedule_payload(runner, (params.get("team") or [""])[0]))
            if path == "/api/roster":
                return self._json(roster_payload(runner, (params.get("team") or [""])[0]))
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
