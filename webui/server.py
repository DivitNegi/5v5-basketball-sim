"""HTTP server for the browser UI: static files, a JSON API, a Server-Sent Events stream and team/player images."""
import json
import socket
import mimetypes
import os
import queue
import re
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import sim_engine

from .hub import EventHub
from .runner import rating_summary, SimRunner
from .live import team_identity
from . import live
from .stats import payload as stats_payload

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


_espn_idx = None


def _norm_name(name: str) -> str:
    s = re.sub(r"[^a-z ]", "", name.lower().replace(".", "").replace("'", ""))
    return " ".join(w for w in s.split() if w not in ("jr", "sr", "ii", "iii", "iv"))


def _espn_index():
    """name -> headshot URL for every player on a current ESPN NBA roster (fetched once, kept on disk)."""
    global _espn_idx
    with _headshot_lock:
        if _espn_idx is not None:
            return _espn_idx
    import urllib.request
    path = os.path.join(HEADSHOT_DIR, "espn_index.json")
    idx = {}
    try:
        with open(path, encoding="utf-8") as fh:
            idx = json.load(fh)
    except Exception:
        pass
    if not idx:
        def get(u):
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.load(resp)
        try:
            base = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
            for t in get(base)["sports"][0]["leagues"][0]["teams"]:
                for a in get(f"{base}/{t['team']['id']}/roster").get("athletes", []):
                    href = (a.get("headshot") or {}).get("href")
                    if href and a.get("fullName"):
                        idx[_norm_name(a["fullName"])] = href
            if idx:
                os.makedirs(HEADSHOT_DIR, exist_ok=True)
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(idx, fh)
        except Exception:
            pass
    with _headshot_lock:
        _espn_idx = idx
    return idx


def _wikipedia_image(name: str):
    """Lead photo of the player's Wikipedia article (for retired and international players). Only accepted when the
    article title matches the name and the description says basketball, so a namesake is never shown."""
    import urllib.request
    try:
        q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "pageimages|description", "piprop": "thumbnail", "pithumbsize": 500,
                                    "redirects": 1, "generator": "search", "gsrsearch": f"{name} basketball", "gsrlimit": 3})
        req = urllib.request.Request("https://en.wikipedia.org/w/api.php?" + q, headers={"User-Agent": "5v5SimLocal/1.0 (personal project)"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            pages = json.load(resp).get("query", {}).get("pages", {}).values()
        want = _norm_name(name)
        for pg in sorted(pages, key=lambda x: x.get("index", 9)):
            title = re.sub(r"\(.*?\)", "", pg.get("title", ""))
            if _norm_name(title) == want and "basketball" in (pg.get("description") or "").lower():
                src = (pg.get("thumbnail") or {}).get("source")
                if src:
                    return src
    except Exception:
        pass
    return None


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
    yield os.path.join(HEADSHOT_DIR, f"{safe}_wiki.png"), "wiki"


def _cached_headshot(name: str):
    for path, _url in _headshot_sources(name):
        if os.path.isfile(path):
            return path
    return None


def _download_headshot(name: str):
    import urllib.request
    try:
        for path, url in _headshot_sources(name):
            if url == "wiki":
                url = _wikipedia_image(name)
                if not url:
                    continue
            elif url is None:   # ESPN roster index (their search endpoint no longer returns players)
                url = _espn_index().get(_norm_name(name))
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


_AVG_KEYS = ("games", "minutes", "pts", "reb", "oreb", "ast", "stl", "blk", "tov", "fgm", "fga", "tpm", "tpa", "ftm", "fta", "plus_minus")


def _pc(s, m, a):
    return 100.0 * s.get(m, 0) / s.get(a, 0) if s.get(a, 0) else 0.0


def _ts(s):
    d = 2 * (s.get("fga", 0) + 0.44 * s.get("fta", 0))
    return 100.0 * s.get("pts", 0) / d if d else 0.0


def _p48(s, k):
    m = s.get("minutes", 0) / 60
    return s.get(k, 0) * 48 / m if m > 0 else 0.0


_RANK_VALUE = {
    "GP": lambda s, g: s.get("games", 0), "MIN": lambda s, g: s.get("minutes", 0) / 60 / g, "PTS": lambda s, g: s.get("pts", 0) / g,
    "REB": lambda s, g: s.get("reb", 0) / g, "ORB": lambda s, g: s.get("oreb", 0) / g, "AST": lambda s, g: s.get("ast", 0) / g,
    "STL": lambda s, g: s.get("stl", 0) / g, "BLK": lambda s, g: s.get("blk", 0) / g, "STK": lambda s, g: (s.get("stl", 0) + s.get("blk", 0)) / g,
    "TOV": lambda s, g: s.get("tov", 0) / g, "FG": lambda s, g: s.get("fgm", 0) / g, "FG%": lambda s, g: _pc(s, "fgm", "fga"),
    "3P": lambda s, g: s.get("tpm", 0) / g, "3P%": lambda s, g: _pc(s, "tpm", "tpa"), "FT": lambda s, g: s.get("ftm", 0) / g,
    "FT%": lambda s, g: _pc(s, "ftm", "fta"), "TS%": lambda s, g: _ts(s), "+/-": lambda s, g: s.get("plus_minus", 0) / g,
    "AST/TOV": lambda s, g: s.get("ast", 0) / max(1, s.get("tov", 0)), "STL/TOV": lambda s, g: s.get("stl", 0) / max(1, s.get("tov", 0)),
    "PTS/48": lambda s, g: _p48(s, "pts"), "REB/48": lambda s, g: _p48(s, "reb"), "AST/48": lambda s, g: _p48(s, "ast"),
    "STL/48": lambda s, g: _p48(s, "stl"), "BLK/48": lambda s, g: _p48(s, "blk"),
}
_RANK_MINIMUMS = {"FG%": ("fgm", 300), "FT%": ("ftm", 125), "3P%": ("tpm", 82), "AST/TOV": ("ast", 200), "STL/TOV": ("stl", 82),
                  "PTS/48": ("minutes", 2000), "REB/48": ("minutes", 2000), "AST/48": ("minutes", 2000), "STL/48": ("minutes", 2000), "BLK/48": ("minutes", 2000)}


def _period_stats(stats, period):
    if period is None:
        return stats
    q = stats.get("quarter_stats") or {}
    if period == 5:
        rows = [r for n, r in q.items() if int(n) >= 5]
        if not rows:
            return {}
        merged = {}
        for r in rows:
            for k, v in r.items():
                if isinstance(v, (int, float)):
                    merged[k] = merged.get(k, 0) + v
        merged["games"] = max((r.get("games", 0) for r in rows), default=0)
        return merged
    return q.get(period) or q.get(str(period)) or {}


def _avg_row(s, g, team, name, kind="player", rank=None):
    g = max(1, g)
    ident = team_identity(team)
    return {"kind": kind, "team": team, "short": ident["short"], "logo": ident["logo"], "color": ident["color"], "initials": ident["initials"],
            "name": name, "rank": rank, "gp": s.get("games", 0) or g, "min": s.get("minutes", 0) / 60 / g,
            "pts": s.get("pts", 0) / g, "reb": s.get("reb", 0) / g, "orb": s.get("oreb", 0) / g, "ast": s.get("ast", 0) / g,
            "stl": s.get("stl", 0) / g, "blk": s.get("blk", 0) / g, "tov": s.get("tov", 0) / g,
            "fgm": s.get("fgm", 0) / g, "fga": s.get("fga", 0) / g, "fgp": _pc(s, "fgm", "fga"),
            "tpm": s.get("tpm", 0) / g, "tpa": s.get("tpa", 0) / g, "tpp": _pc(s, "tpm", "tpa"),
            "ftm": s.get("ftm", 0) / g, "fta": s.get("fta", 0) / g, "ftp": _pc(s, "ftm", "fta"),
            "ts": _ts(s), "pm": s.get("plus_minus", 0) / g}


def avg_payload(runner, team="All Teams", quarter="All", rank="Team order", source="Season"):
    sec = runner.sections or {}
    season_p, season_t = sec.get("_season_player_totals") or {}, sec.get("_season_team_totals") or {}
    po_p, po_t = sec.get("_playoff_player_totals") or {}, sec.get("_playoff_team_totals") or {}
    ser_p, ser_t = sec.get("_series_totals") or {}, sec.get("_series_team_totals") or {}
    if not po_p and ser_p and ser_p is not season_p:
        po_p, po_t = ser_p, ser_t
    if not season_p and not po_p:
        players, teams, label = ser_p, ser_t, "Series"
    elif source == "Season" and season_p:
        players, teams, label = season_p, season_t, "Season"
    elif source != "Season" and po_p:
        players, teams, label = po_p, po_t, "Playoffs"
    elif season_p:
        players, teams, label = season_p, season_t, "Season"
    else:
        players, teams, label = po_p, po_t, "Playoffs"
    period = None
    if quarter != "All":
        period = 5 if quarter == "OT" else (int(quarter.replace("Q", "")) if quarter.replace("Q", "").isdigit() else None)
    names = list(players.keys())
    if team != "All Teams":
        names = [team] if team in players else []
    out = {"teams": sorted(players.keys()), "sources": [x for x, ok in (("Season", bool(season_p)), ("Playoffs", bool(po_p))) if ok],
           "source": label, "rows": [], "flat": False}
    if rank in _RANK_VALUE:
        share = 1.0 if period is None else (5 / 48 if period == 5 else 12 / 48)
        entries = []
        for tn in names:
            tp = players.get(tn) or {}
            tg = max((x.get("games", 0) for x in tp.values()), default=0)
            for pn, st in tp.items():
                rs = _period_stats(st, period)
                if not rs:
                    continue
                rule = _RANK_MINIMUMS.get(rank)
                if rule:
                    key, base = rule
                    need = base * min(1.0, max(1, tg * share) / 82)
                    have = rs.get("minutes", 0) / 60 if key == "minutes" else rs.get(key, 0)
                    if have < need:
                        continue
                g = max(1, rs.get("games", 0))
                entries.append((_RANK_VALUE[rank](rs, g), tn, pn, rs, g))
        entries.sort(key=lambda e: e[0], reverse=True)
        out["rows"] = [_avg_row(rs, g, tn, pn, rank=i) for i, (_v, tn, pn, rs, g) in enumerate(entries, 1)]
        out["flat"] = True
        return out
    for tn in names:
        tp = players.get(tn) or {}
        if period is None:
            tot = teams.get(tn) or {}
        else:
            tot = {k: 0 for k in _AVG_KEYS}
            for st in tp.values():
                rs = _period_stats(st, period)
                for k in _AVG_KEYS:
                    if k != "games":
                        tot[k] += rs.get(k, 0)
            tot["games"] = max((st.get("games", 0) for st in tp.values()), default=0)
        row = _avg_row(tot, tot.get("games", 0) or 1, tn, "", kind="team")
        row["min"] = None
        row["name"] = row["short"]
        out["rows"].append(row)
        pr = [(pn, _period_stats(st, period)) for pn, st in tp.items()]
        pr = [(pn, rs) for pn, rs in pr if rs]
        for pn, rs in sorted(pr, key=lambda it: it[1].get("pts", 0) / max(1, it[1].get("games", 1)), reverse=True):
            out["rows"].append(_avg_row(rs, max(1, rs.get("games", 0)), tn, pn))
    return out


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


def compare_payload(runner):
    sec = runner.sections or {}
    totals = sec.get("_season_player_totals") or sec.get("_series_totals") or {}
    keys = ("games", "minutes", "pts", "reb", "ast", "stl", "blk", "tov", "fgm", "fga", "tpm", "tpa", "ftm", "fta", "plus_minus")
    out = {}
    for team, players in totals.items():
        ident = team_identity(team)
        out[team] = {"short": ident["short"], "logo": ident["logo"], "players": {n: {k: st.get(k, 0) for k in keys} for n, st in players.items() if st.get("games", 0)}}
    if out:
        return {"teams": out, "source": "season" if sec.get("_season_player_totals") else "series"}
    # no season/series yet: compare using the game being played
    from . import live
    a, b = live._teams()
    if a is not None:
        for team in (a, b):
            ident = team_identity(team.name)
            players = {}
            for p in team.roster:
                if getattr(p, "minutes", 0) <= 0:
                    continue
                players[p.name] = {"games": 1, "minutes": p.minutes, "pts": p.pts, "reb": p.reb, "ast": p.ast, "stl": getattr(p, "stl", 0),
                                   "blk": getattr(p, "blk_stat", 0), "tov": p.tov, "fgm": p.fgm, "fga": p.fga, "tpm": p.tpm, "tpa": p.tpa,
                                   "ftm": p.ftm, "fta": p.fta, "plus_minus": getattr(p, "plus_minus", 0)}
            out[team.name] = {"short": ident["short"], "logo": ident["logo"], "players": players}
    return {"teams": out, "source": "game"}


def _coach_player(player):
    return {"name": player.name, "pos": player.position, "min": round(getattr(player, "minutes", 0) / 60, 1),
            "pts": player.pts, "reb": player.reb, "ast": player.ast, "pf": player.pf,
            "out": bool(getattr(player, "fouled_out", False))}


def coach_payload():
    teams = [sim_engine.SIM_CONTEXT.get("teamA"), sim_engine.SIM_CONTEXT.get("teamB")]
    rows = []
    for index, team in enumerate(t for t in teams if t is not None):
        ident = team_identity(team.name)
        rows.append({"index": index, "team": ident, "timeouts": getattr(team, "timeouts", 0),
                     "offense": sim_engine.OFFENSIVE_SET_OVERRIDES.get(team.name, getattr(team, "game_plan", {}).get("offense", "balanced")),
                     "defense": sim_engine.DEFENSIVE_SCHEME_OVERRIDES.get(team.name, getattr(team, "game_plan", {}).get("defense", "standard")),
                     "focus": getattr(team, "defensive_focus", None), "timeoutOpen": bool(getattr(team, "coach_timeout_open", False)),
                     "floor": [_coach_player(p) for p in team.on_floor], "bench": [_coach_player(p) for p in team.bench],
                     "queued": [{"out": out_name, "in": in_name} for out_name, in_name in list(getattr(team, "manual_substitution", []) or [])]})
    return {"active": bool(rows), "teams": rows}


def coach_action(data):
    teams = [sim_engine.SIM_CONTEXT.get("teamA"), sim_engine.SIM_CONTEXT.get("teamB")]
    try:
        team = teams[int(data.get("team", 0))]
    except (TypeError, ValueError, IndexError):
        team = None
    if team is None:
        return "No live team is available."
    action = data.get("action")
    if action == "sub":
        return None if sim_engine.gui_substitute(team, str(data.get("out", "")), str(data.get("in", ""))) else None
    if action == "timeout":
        team.manual_timeout_requested = True
        return None
    if action == "subs":
        team.manual_sub_request = True
        return None
    if action == "offense":
        options = ("balanced", "five_out", "four_out_one_in", "three_out_two_in", "post_heavy", "motion", "star_spread")
        current = sim_engine.OFFENSIVE_SET_OVERRIDES.get(team.name, getattr(team, "game_plan", {}).get("offense", "balanced"))
        code = options[(options.index(current) + 1) % len(options)] if current in options else options[0]
        sim_engine.OFFENSIVE_SET_OVERRIDES[team.name] = code
        sim_engine.apply_offensive_set_override(team)
        return None
    if action == "defense":
        options = ("standard", "switch", "drop", "show_recover", "blitz", "stay_home", "top_lock", "pack_paint", "wall_paint", "zone", "load_star")
        current = sim_engine.DEFENSIVE_SCHEME_OVERRIDES.get(team.name, getattr(team, "game_plan", {}).get("defense", "standard"))
        code = options[(options.index(current) + 1) % len(options)] if current in options else options[0]
        sim_engine.DEFENSIVE_SCHEME_OVERRIDES[team.name] = code
        sim_engine.apply_defensive_scheme_override(team)
        return None
    if action == "focus":
        opponent = teams[1] if team is teams[0] else teams[0]
        if opponent is not None and opponent.on_floor:
            target = max(opponent.on_floor, key=lambda p: p.pts + p.usage * 20 + p.shot_tendency * 10)
            team.defensive_focus = target.name
        return None
    return "Unknown coach action."


def fantasy_payload():
    if not sim_engine.fantasy_trade_available():
        return {"active": False, "message": "Start a fantasy draft season to manage lineups and trades."}
    state = sim_engine.FANTASY_TRADE_STATE
    user = state["user_team"]
    line = sim_engine.fantasy_lineup_defaults()
    usage = sim_engine.fantasy_usage_defaults()
    def roster(name):
        return [{**rating_summary(p),
                 "minutes": line["minutes"].get(p.name) if name == user else None,
                 "starter": p.name in line["starters"] if name == user else False,
                 "usage": usage.get(p.name, {}).get("usage") if name == user else None}
                for p in sim_engine.fantasy_trade_roster(name)]
    return {"active": True, "userTeam": user, "teams": list(state["factories"]), "userRoster": roster(user),
            "lineup": line, "usage": usage, "block": list(state.get("block", set())),
            "deadline": state.get("deadline_game"), "deadlinePassed": state.get("deadline_passed"), "log": state.get("log", [])[-20:]}


def replay_payload():
    rows = []
    for order, spec in sorted(sim_engine.SEASON_REPLAY.get("games", {}).items()):
        rows.append({"order": order, "game": order + 1, "teamA": spec[0], "teamB": spec[1],
                     "available": sim_engine.season_replay_available(order)})
    return {"games": rows}


def broadcast_payload():
    rows = []
    for event in list(sim_engine.BROADCAST_EVENTS)[-300:]:
        row = {"kind": event.get("kind", "event")}
        for key, value in event.items():
            if key == "kind":
                continue
            row[key] = getattr(value, "name", str(value)) if not isinstance(value, (str, int, float, bool, type(None))) else value
        rows.append(row)
    return {"events": rows}


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
            if path == "/api/stats":
                return self._json(stats_payload(runner,
                    (params.get("source") or ["Live"])[0],
                    (params.get("kind") or ["averages"])[0],
                    (params.get("team") or ["All teams"])[0],
                    (params.get("quarter") or ["All"])[0]))
            if path == "/api/coach":
                return self._json(coach_payload())
            if path == "/api/fantasy":
                return self._json(fantasy_payload())
            if path == "/api/fantasy/roster":
                team = (params.get("team") or [""])[0]
                if not sim_engine.fantasy_trade_available() or team not in (sim_engine.FANTASY_TRADE_STATE.get("factories") or {}):
                    return self._json({"players": []})
                return self._json({"players": [rating_summary(p) for p in sim_engine.fantasy_trade_roster(team)]})
            if path == "/api/draft":
                return self._json(runner.draft_state())
            if path == "/api/trade/prompt":
                return self._json({"prompt": runner.trade_prompt})
            if path == "/api/replays":
                return self._json(replay_payload())
            if path == "/api/broadcast":
                return self._json(broadcast_payload())
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
            if path == "/api/game/shots":
                return self._json(live.shots_payload())
            if path == "/api/game/quarters":
                return self._json(live.quarters_payload())
            if path == "/api/game/card":
                return self._json(live.player_payload((params.get("team") or [""])[0], (params.get("name") or [""])[0]))
            if path == "/api/game/players":
                return self._json(live.players_for_card())
            if path == "/api/compare":
                return self._json(compare_payload(runner))
            if path == "/api/roster":
                return self._json(roster_payload(runner, (params.get("team") or [""])[0]))
            if path == "/api/season/avg":
                def q(k, d):
                    return (params.get(k) or [d])[0]
                return self._json(avg_payload(runner, q("team", "All Teams"), q("quarter", "All"), q("rank", "Team order"), q("source", "Season")))
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
                error = runner.start(data.get("mode", "Game"), data.get("teamA", ""), data.get("teamB", ""), data.get("rules", "NBA"), data.get("options"))
                return self._json({"ok": error is None, "error": error}, 200 if error is None else 400)
            if path == "/api/control":
                error = runner.control(data.get("action", ""), data.get("value"))
                return self._json({"ok": error is None, "error": error}, 200 if error is None else 400)
            if path == "/api/coach":
                error = coach_action(data)
                runner._push_live(force=True)
                return self._json({"ok": error is None, "error": error, "coach": coach_payload()}, 200 if error is None else 400)
            if path == "/api/trade/respond":
                result = runner.trade_respond(str(data.get("action", "")))
                return self._json(result, 200 if result.get("ok") else 400)
            if path == "/api/draft":
                error = runner.draft_choose(data.get("value"))
                return self._json({"ok": error is None, "error": error}, 200 if error is None else 400)
            if path == "/api/fantasy/lineup":
                result = sim_engine.fantasy_lineup_submit(data.get("starters", []), data.get("positions", {}), data.get("minutes", {}),
                                                          bool(data.get("reset")), rotation=data.get("rotation", []))
                if result.get("ok") and "usage" in data:
                    result = sim_engine.fantasy_usage_submit(data.get("usage") or {})
                return self._json(result, 200 if result.get("ok") else 400)
            if path == "/api/fantasy/trade":
                action = data.get("action")
                if not sim_engine.fantasy_trade_available():
                    return self._json({"ok": False, "error": "No fantasy league is active."}, 400)
                if action == "find":
                    return self._json({"ok": True, "offers": sim_engine.fantasy_trade_find_offers(data.get("userGives", []))})
                if action == "ask":
                    return self._json({"ok": True, "offers": sim_engine.fantasy_trade_find_asks(data.get("team", ""), data.get("aiGives", []))})
                if action == "submit":
                    result = sim_engine.fantasy_trade_submit(data.get("team", ""), data.get("userGives", []), data.get("aiGives", []))
                    return self._json(result, 200 if result.get("ok") else 400)
                if action == "block":
                    block = sim_engine.fantasy_trade_block_toggle(data.get("players", []))
                    return self._json({"ok": True, "block": list(block)})
                return self._json({"ok": False, "error": "Unknown trade action."}, 400)
            self._send(404, b"not found", "text/plain")

    return Handler, runner


class _ExclusiveServer(ThreadingHTTPServer):
    """Windows lets a second server bind a port an old one still holds (SO_REUSEADDR), so the browser reaches the dead
    one and times out. Bind exclusively: a busy port raises, and run() moves on to the next one."""
    allow_reuse_address = False

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def run(open_browser: bool = True, port: int = 8790):
    handler, runner = build_app()
    server = None
    for candidate in range(port, port + 20):
        try:
            server = _ExclusiveServer(("127.0.0.1", candidate), handler)
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
