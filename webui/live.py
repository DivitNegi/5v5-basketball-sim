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
    block.update({"score": team.score, "court": court, "box": box, "totals": team_totals(team)})
    return block


def live_snapshot() -> Optional[Dict]:
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
