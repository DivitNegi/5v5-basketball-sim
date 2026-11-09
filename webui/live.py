"""JSON snapshots of the game being played right now, read from the engine's live objects (SIM_CONTEXT)."""
import re
from typing import Dict, List, Optional

import sim_engine

TEAM_YEAR = re.compile(r"^(\d{4}) (.+)$")

FRANCHISE_CODES = [
    ("hawks", "atl"), ("celtics", "bos"), ("brooklyn", "bkn"), ("hornets", "cha"), ("bulls", "chi"), ("cavaliers", "cle"),
    ("cavs", "cle"), ("mavericks", "dal"), ("mavs", "dal"), ("nuggets", "den"), ("pistons", "det"), ("warriors", "gs"),
    ("rockets", "hou"), ("pacers", "ind"), ("clippers", "lac"), ("lakers", "lal"), ("grizzlies", "mem"), ("heat", "mia"),
    ("bucks", "mil"), ("timberwolves", "min"), ("pelicans", "no"), ("knicks", "ny"), ("thunder", "okc"), ("magic", "orl"),
    ("sixers", "phi"), ("76ers", "phi"), ("suns", "phx"), ("blazers", "por"), ("trail blazers", "por"), ("kings", "sac"),
    ("spurs", "sa"), ("raptors", "tor"), ("utah", "utah"), ("jazz", "utah"), ("wizards", "wsh"),
]

# Primary / secondary colours per franchise, for the scoreboard and team accents.
TEAM_COLORS = {
    "atl": ("#E03A3E", "#C1D32F"), "bos": ("#007A33", "#BA9653"), "bkn": ("#2B2B2B", "#FFFFFF"), "cha": ("#1D1160", "#00788C"),
    "chi": ("#CE1141", "#000000"), "cle": ("#860038", "#FDBB30"), "dal": ("#00538C", "#B8C4CA"), "den": ("#0E2240", "#FEC524"),
    "det": ("#C8102E", "#1D42BA"), "gs": ("#1D428A", "#FFC72C"), "hou": ("#CE1141", "#C4CED4"), "ind": ("#002D62", "#FDBB30"),
    "lac": ("#C8102E", "#1D428A"), "lal": ("#552583", "#FDB927"), "mem": ("#5D76A9", "#12173F"), "mia": ("#98002E", "#F9A01B"),
    "mil": ("#00471B", "#EEE1C6"), "min": ("#0C2340", "#78BE20"), "no": ("#0C2340", "#C8102E"), "ny": ("#006BB6", "#F58426"),
    "okc": ("#007AC1", "#EF3B24"), "orl": ("#0077C0", "#C4CED4"), "phi": ("#006BB6", "#ED174C"), "phx": ("#1D1160", "#E56020"),
    "por": ("#E03A3E", "#000000"), "sac": ("#5A2D81", "#63727A"), "sa": ("#C4CED4", "#000000"), "tor": ("#CE1141", "#000000"),
    "utah": ("#002B5C", "#F9A01B"), "wsh": ("#002B5C", "#E31837"),
}


def franchise_code(team_name: str) -> Optional[str]:
    lower = (team_name or "").lower()
    for needle, code in FRANCHISE_CODES:
        if needle in lower:
            return code
    return None


def short_name(team_name: str) -> str:
    match = TEAM_YEAR.match(team_name or "")
    return match.group(2) if match else (team_name or "")


def team_year(team_name: str) -> Optional[str]:
    match = TEAM_YEAR.match(team_name or "")
    return match.group(1) if match else None


def initials(team_name: str) -> str:
    words = [w for w in re.sub(r"[^A-Za-z0-9 ]", " ", short_name(team_name)).split() if not w.isdigit()]
    if not words:
        return "TM"
    if len(words) == 1:
        return words[0][:3].upper()
    return "".join(w[0] for w in words[-2:]).upper()[:3]


def team_identity(team_name: str) -> Dict:
    code = franchise_code(team_name)
    primary, secondary = TEAM_COLORS.get(code or "", ("#3B82F6", "#E2E8F0"))
    return {
        "name": team_name,
        "short": short_name(team_name),
        "year": team_year(team_name),
        "initials": initials(team_name),
        "logo": code,
        "color": primary,
        "color2": secondary,
    }


def _pct(made: int, att: int) -> Optional[float]:
    return round(100.0 * made / att, 1) if att else None


def _energy(player):
    try:
        return round(100 * sim_engine.fatigue_factor(player))   # 100 = fresh; the floor is about 85
    except Exception:
        return None


def player_line(player, slot: Optional[str] = None, on_court: bool = False) -> Dict:
    return {
        "name": player.name,
        "pos": slot or getattr(player, "position", ""),
        "listed": getattr(player, "position", ""),
        "on": on_court,
        "min": round(getattr(player, "minutes", 0) / 60.0, 1),
        "pts": player.pts, "reb": player.reb, "oreb": getattr(player, "oreb_stat", 0), "ast": player.ast,
        "stl": getattr(player, "stl", 0), "blk": getattr(player, "blk_stat", 0), "tov": player.tov, "pf": player.pf,
        "fgm": player.fgm, "fga": player.fga, "tpm": player.tpm, "tpa": player.tpa, "ftm": player.ftm, "fta": player.fta,
        "fgp": _pct(player.fgm, player.fga), "tpp": _pct(player.tpm, player.tpa), "ftp": _pct(player.ftm, player.fta),
        "pm": getattr(player, "plus_minus", 0),
        "out": bool(getattr(player, "fouled_out", False)),
        "rookie": bool(getattr(player, "rookie", False)),
        "starter": bool(getattr(player, "started_game", False)),
        "energy": _energy(player), "stint": round(getattr(player, "current_stint", 0) / 60.0, 1),
    }


def team_totals(team) -> Dict:
    t = sim_engine.accumulate_team_totals(team)
    return {
        "pts": team.score, "reb": t.get("reb", 0), "ast": t.get("ast", 0), "stl": t.get("stl", 0), "blk": t.get("blk", 0),
        "tov": t.get("tov", 0), "pf": t.get("pf", 0),
        "fgm": t.get("fgm", 0), "fga": t.get("fga", 0), "tpm": t.get("tpm", 0), "tpa": t.get("tpa", 0),
        "ftm": t.get("ftm", 0), "fta": t.get("fta", 0),
        "fgp": _pct(t.get("fgm", 0), t.get("fga", 0)), "tpp": _pct(t.get("tpm", 0), t.get("tpa", 0)), "ftp": _pct(t.get("ftm", 0), t.get("fta", 0)),
        "paint": getattr(team, "points_paint", 0), "fastbreak": getattr(team, "fastbreak_pts", 0),
        "second": getattr(team, "second_chance_pts", 0), "timeouts": getattr(team, "timeouts", 0),
    }


def team_block(team) -> Dict:
    on_floor = list(getattr(team, "on_floor", [])[:5])
    if getattr(team, "lock_custom_starting_positions", False):
        slots = [(str(getattr(p, "position", "SF") or "SF").upper(), p) for p in on_floor]
    else:
        ordered = sim_engine.balanced_lineup_order(on_floor)
        slots = list(zip(("PG", "SG", "SF", "PF", "C"), ordered))
    on_ids = {id(p) for p in on_floor}
    court = [player_line(p, slot, True) for slot, p in slots]
    box = [player_line(p, None, id(p) in on_ids) for p in team.roster]
    block = team_identity(team.name)
    block.update({"score": team.score, "court": court, "box": box, "totals": team_totals(team), "ball": getattr(team, "ball_handler_name", None)})
    return block


def live_snapshot() -> Optional[Dict]:
    if getattr(sim_engine, "SILENT_SIM_DEPTH", 0) > 0:
        return None   # a quiet season / All-Star game is not a live game
    ctx = sim_engine.SIM_CONTEXT
    team_a, team_b = ctx.get("teamA"), ctx.get("teamB")
    if team_a is None or team_b is None:
        return None
    possession = ctx.get("possession")
    return {
        "period": ctx.get("period"),
        "clock": ctx.get("period_time"),
        "possession": getattr(possession, "name", None),
        "teams": [team_block(team_a), team_block(team_b)],
    }


# ---------------------------------------------------------------- shot chart, quarter box scores, player card
def _zone(diet: Dict, key: str):
    if key == "rim":
        return [int(diet.get("rim_made", 0)) + int(diet.get("dunk_made", 0)), int(diet.get("rim", 0)) + int(diet.get("dunk", 0))]
    if key == "paint":
        att, made = int(diet.get("paint", 0)), int(diet.get("paint_made", 0))
        if not att:
            att, made = int(diet.get("rim", 0)), int(diet.get("rim_made", 0))
        return [made, att]
    return [int(diet.get(f"{key}_made", 0)), int(diet.get(key, 0))]


def zones(diet: Optional[Dict]) -> Dict:
    diet = diet or {}
    return {k: _zone(diet, k) for k in ("rim", "paint", "mid", "three", "post", "dunk")}


def _teams():
    if getattr(sim_engine, "SILENT_SIM_DEPTH", 0) > 0:
        return (None, None)
    ctx = sim_engine.SIM_CONTEXT
    a, b = ctx.get("teamA"), ctx.get("teamB")
    return (a, b) if a is not None and b is not None else (None, None)


def shots_payload() -> Dict:
    a, b = _teams()
    if a is None:
        return {"teams": []}
    out = []
    for team in (a, b):
        block = team_identity(team.name)
        block["team"] = zones(getattr(team, "shot_diet", {}))
        block["players"] = {p.name: zones(getattr(p, "shot_diet", {})) for p in team.roster if getattr(p, "fga", 0)}
        out.append(block)
    return {"teams": out}


_QKEYS = ("minutes", "pts", "reb", "ast", "stl", "blk", "tov", "oreb", "dreb", "pf", "fgm", "fga", "tpm", "tpa", "ftm", "fta", "plus_minus")
_TKEYS = ("score", "reb", "oreb", "dreb", "ast", "stl", "blk", "tov", "pf", "fgm", "fga", "tpm", "tpa", "ftm", "fta", "points_paint", "fastbreak_pts", "second_chance_pts", "fouls_drawn")


def _player_now(team, p) -> Dict:
    snap = sim_engine.player_quarter_snapshot(team)
    return snap.get(sim_engine.player_stat_key(team, p), {})


def quarters_payload() -> Dict:
    a, b = _teams()
    if a is None:
        return {"teams": [], "period": None}
    period = sim_engine.SIM_CONTEXT.get("period") or 1
    out = []
    for team in (a, b):
        done_team = list(getattr(team, "quarter_team_stats", []) or [])
        done_players = getattr(team, "quarter_player_stats", {}) or {}
        periods = {}
        for row in done_team:
            periods[row["period"]] = {"team": {k: row.get(k, 0) for k in _TKEYS}, "players": {}}
        # the quarter being played: totals so far minus the finished quarters
        cur = sim_engine.team_quarter_snapshot(team)
        completed_periods = {r["period"] for r in done_team}
        if period not in completed_periods:
            live_team = {k: cur.get(k, 0) - sum(r.get(k, 0) for r in done_team) for k in _TKEYS}
            periods[period] = {"team": live_team, "players": {}, "live": True}
        snap = sim_engine.player_quarter_snapshot(team)
        for p in team.roster:
            key = sim_engine.player_stat_key(team, p)
            rows = done_players.get(key, [])
            for r in rows:
                if r["period"] in periods:
                    periods[r["period"]]["players"][p.name] = {k: r.get(k, 0) for k in _QKEYS}
            if period not in completed_periods and period in periods:
                now = snap.get(key, {})
                periods[period]["players"][p.name] = {k: now.get(k, 0) - sum(r.get(k, 0) for r in rows) for k in _QKEYS}
        ident = team_identity(team.name)
        ident["periods"] = {str(k): v for k, v in sorted(periods.items())}
        ident["roster"] = [{"name": p.name, "pos": p.position, "starter": bool(getattr(p, "started_game", False))} for p in team.roster]
        out.append(ident)
    return {"teams": out, "period": period}


def _quarter_periods(quarter):
    """'1'..'4' -> {n}; 'OT' -> every overtime period (5 and up); None/'all' -> None."""
    if not quarter or quarter == "all":
        return None
    if quarter == "OT":
        return {p for p in range(5, 12)}
    try:
        return {int(quarter)}
    except ValueError:
        return None


def _quarter_line(team_name: str, name: str, periods):
    """The player's box line for just those periods (summed), from the same quarter data the Quarters tab shows."""
    entry = next((t for t in quarters_payload().get("teams", []) if t["name"] == team_name), None)
    if entry is None:
        return None
    total = {}
    seen = False
    for key, per in (entry.get("periods") or {}).items():
        if int(key) in periods and name in per.get("players", {}):
            seen = True
            for k, v in per["players"][name].items():
                total[k] = total.get(k, 0) + (v or 0)
    return total if seen else {}


def player_payload(team_name: str, name: str, quarter=None) -> Dict:
    a, b = _teams()
    team = next((t for t in (a, b) if t is not None and t.name == team_name), None)
    if team is None:
        return {"error": "No live game"}
    p = next((x for x in team.roster if x.name == name), None)
    if p is None:
        return {"error": "Unknown player"}
    opp = b if team is a else a
    line = player_line(p, None, any(x is p for x in team.on_floor))
    fga, fta = p.fga, p.fta
    line["ts"] = round(100 * p.pts / (2 * (fga + 0.44 * fta)), 1) if (fga + fta) else None
    line["dreb"] = getattr(p, "dreb_stat", 0)
    ident = team_identity(team.name)
    shots, scope = zones(getattr(p, "shot_diet", {})), "game"
    periods = _quarter_periods(quarter)
    if periods:
        q = _quarter_line(team.name, name, periods) or {}
        mins = q.get("minutes", 0)
        line.update({"min": round(mins / 60.0, 1), "pts": q.get("pts", 0), "reb": q.get("reb", 0), "oreb": q.get("oreb", 0), "dreb": q.get("dreb", 0),
                     "ast": q.get("ast", 0), "stl": q.get("stl", 0), "blk": q.get("blk", 0), "tov": q.get("tov", 0), "pf": q.get("pf", 0),
                     "fgm": q.get("fgm", 0), "fga": q.get("fga", 0), "tpm": q.get("tpm", 0), "tpa": q.get("tpa", 0), "ftm": q.get("ftm", 0), "fta": q.get("fta", 0),
                     "pm": q.get("plus_minus", 0)})
        line["fgp"], line["tpp"], line["ftp"] = _pct(line["fgm"], line["fga"]), _pct(line["tpm"], line["tpa"]), _pct(line["ftm"], line["fta"])
        denom = 2 * (line["fga"] + 0.44 * line["fta"])
        line["ts"] = round(100 * line["pts"] / denom, 1) if denom else None
        qd = getattr(p, "quarter_shot_diet", {}) or {}
        merged = {}
        for n in periods:
            for d in (qd.get(n), qd.get(str(n))):
                for k, v in (d or {}).items():
                    merged[k] = merged.get(k, 0) + v
        shots, scope = zones(merged), "quarter"
    by_quarter = []
    try:
        entry = next((t for t in quarters_payload().get("teams", []) if t["name"] == team.name), None)
        for key, per in sorted((entry or {}).get("periods", {}).items(), key=lambda kv: int(kv[0])):
            by_quarter.append({"period": int(key), "pts": (per.get("players", {}).get(name) or {}).get("pts", 0)})
    except Exception:
        by_quarter = []
    return {
        "by_quarter": by_quarter,
        "scope": scope, "quarter": quarter if periods else None,
        "team": ident, "opp": team_identity(opp.name) if opp else None, "score": [team.score, opp.score if opp else 0],
        "player": line, "archetype": getattr(p, "archetype", ""), "badges": list(getattr(p, "badges", ()) or ()),
        "shots": shots, "defended": zones(getattr(p, "defended_diet", {})),
        "period": sim_engine.SIM_CONTEXT.get("period"), "clock": sim_engine.SIM_CONTEXT.get("period_time"),
    }


def players_for_card():
    a, b = _teams()
    if a is None:
        return []
    return [{"team": t.name, "short": short_name(t.name), "players": [p.name for p in sorted(t.roster, key=lambda x: -x.minutes)]} for t in (a, b)]
