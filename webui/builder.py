"""Create Team / Create Player / Edit Player for the web UI: the same tools, rules and engine helpers as the Tk dialogs in gui_app.py.

Create Team: pick 5-10 players from the fantasy pool (every simulator team plus saved custom players), choose each player's version,
order them (the first five start), set positions, and register the team. Like Tk, custom teams live for the life of the server.
Create / Edit Player: the Tk form (ratings 0-100, height, extra badges with levels, go-to shot), previewed with the Tk preview text,
archetype and "shades of" match, saved to the same custom players file."""
import copy
import threading
from typing import Dict, List, Optional

import players_data
import sim_engine
from sim_engine import Player, Team

POSITIONS = ("PG", "SG", "SF", "PF", "C")
LEVELS = (("Bronze", "bronze"), ("Silver", "silver"), ("Gold", "gold"), ("Hall of Fame", "hof"))
LEVEL_LABEL_TO_CODE = dict(LEVELS)
LEVEL_CODE_TO_LABEL = {code: label for label, code in LEVELS}

# the Tk Create Player form, in its order: (field, label, default for a new player)
FIELD_DEFS = [
    ("three_tendency", "3PT Tend", "50"), ("mid_tendency", "MID Tend", "35"), ("drive_tendency", "Drive Tend", "35"),
    ("post_tendency", "Post Tend", "10"), ("dunk_tendency", "Dunk Tend", "20"), ("shot_tendency", "Shot Tend", "65"),
    ("three_rating", "3PT", "80"), ("mid_rating", "MID", "80"), ("rim_rating", "RIM", "80"), ("dunk_rating", "DUNK", "70"),
    ("ft_rating", "FT", "80"), ("usage", "Usage", "22"), ("playmaking", "Playmaking", "60"), ("ball_handle", "Handle", "70"),
    ("steal", "Steal", "55"), ("block", "Block", "45"), ("oreb", "OREB", "45"), ("dreb", "DREB", "55"),
    ("foul_draw", "Foul Draw", "20"), ("foul_rate", "Foul Rate", "20"), ("perimeter_def", "Perimeter Def", "60"),
    ("interior_def", "Interior Def", "50"), ("clutchness", "Clutch", "60"), ("speed", "Speed", "70"),
    ("shot_iq", "Shot IQ", "70"), ("iso_tendency", "Iso Tend", "35"),
]

_lock = threading.Lock()
_pool: Dict = {"sig": None, "players": None}
custom_team_factories: Dict[str, object] = {}   # name -> factory, like Tk's gui_custom_team_factories


# ------------------------------------------------------------------ fantasy pool
def all_pool_players() -> List[Player]:
    """Every player in the fantasy pool (one entry per player, his versions attached), best OVR first. Rebuilt when the custom player file changes."""
    sig = players_data._fantasy_pool_signature()
    with _lock:
        if _pool["players"] is None or _pool["sig"] != sig:
            pools = players_data.build_fantasy_player_pools(None)
            players = [player for player, _desc in sim_engine.available_all_fantasy_players(pools, set())]
            players.sort(key=sim_engine.fantasy_ovr, reverse=True)
            _pool.update(sig=sig, players=players)
        return _pool["players"]


def _versions(player: Player) -> List[Player]:
    versions = list(getattr(player, "fantasy_versions", []) or [player])
    versions.sort(key=sim_engine.fantasy_ovr, reverse=True)
    return versions


def _vid(v: Player) -> str:
    """A version's id: name + team-season, so a saved draft still finds the same player after the pool changes."""
    return f"{v.name}||{_source(v)}"


def _lookup(pid: str) -> Optional[Player]:
    name, _, source = str(pid).partition("||")
    for player in all_pool_players():
        if player.name != name and getattr(player, "fantasy_base_name", None) != name:
            continue
        for v in _versions(player):
            if v.name == name and _source(v) == source:
                return v
    return None


def _source(p: Player) -> str:
    return getattr(p, "source_team", "All-Time")


def _fold(text: str) -> str:
    """Lower-case without accents, so 'jokic' finds Jokić."""
    import unicodedata
    return unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()


def pool_payload(search: str = "", hide_custom: bool = False) -> Dict:
    term = _fold((search or "").strip())
    rows = []
    for i, player in enumerate(all_pool_players()):
        source = _source(player)
        if hide_custom and source == "Custom Player":
            continue
        if term and term not in _fold(player.name) and term not in _fold(source) and term not in player.position.lower():
            continue
        rows.append({"id": _vid(_versions(player)[0]), "name": player.name, "pos": player.position, "ovr": sim_engine.fantasy_ovr(player), "source": source,
                     "versions": [{"id": _vid(v), "label": f"{v.name} | {_source(v)} | {v.position} | OVR {sim_engine.fantasy_ovr(v)}",
                                   "name": v.name, "pos": v.position, "ovr": sim_engine.fantasy_ovr(v), "source": _source(v)}
                                  for j, v in enumerate(_versions(player))]})
        if len(rows) >= 350:   # Tk shows the first 350 matches
            break
    return {"players": rows}


def preview_payload(pid: str) -> Dict:
    return {"text": sim_engine.fantasy_player_preview_text(_lookup(pid))}


# ------------------------------------------------------------------ Create Team
def _reset_runtime(player: Player):
    """Tk's reset_player_runtime_for_swap: a fresh stat line for the cloned player."""
    player.pts = player.reb = player.ast = player.stl = player.blk_stat = player.tov = 0
    player.assist_pts_created = 0
    player.pf = player.fgm = player.fga = player.tpm = player.tpa = player.ftm = player.fta = 0
    player.minutes = 0
    player.fouled_out = False
    player.plus_minus = 0
    player.oreb_stat = 0
    player.dreb_stat = 0
    player.fouls_drawn = 0
    player.double_teams_faced = 0
    player.shot_diet = {}
    player.quarter_shot_diet = {}
    player.defended_diet = {}
    player.defended_matchup_diet = {}
    player.quarter_stats = {}
    player.play_events = []
    player.foul_rest_until = 0
    player.jumper_make_streak = 0
    player.just_caught_fire = False
    player.fourth_fga = 0
    player.limitless_range_attempt = False
    player.heat_check_attempt = False


def _clone(player: Player) -> Player:
    clone = copy.deepcopy(player)
    clone.source_team = getattr(player, "source_team", getattr(player, "team_name", "Fantasy Pool"))
    clone.fantasy_base_name = getattr(player, "fantasy_base_name", player.name)
    _reset_runtime(clone)
    return clone


def create_team(runner, name: str, picks: List[Dict]) -> Dict:
    """picks: [{id, position}] in roster order; the first five start."""
    if runner.active:
        return {"error": "Finish or clear the current sim before creating a team."}
    players = []
    for pick in picks[:10]:
        base = _lookup(pick.get("id"))
        if base is None:
            return {"error": "One of those players is no longer in the pool. Reopen Create Team and pick again."}
        clone = _clone(base)
        pos = str(pick.get("position") or getattr(base, "position", "SF") or "SF").upper()
        clone.position = pos if pos in POSITIONS else "SF"
        clone.secondary_positions = sim_engine.default_secondary_positions(clone.position)
        players.append(clone)
    if len(players) < 5:
        return {"error": "Pick at least 5 players before creating the team."}
    clean = (name or "").strip() or f"Custom Team {len(custom_team_factories) + 1}"
    if clean in runner.factories and clean not in custom_team_factories:
        clean = f"{clean} Custom"
    blueprint = [_clone(p) for p in players]

    def make_custom_team(team_name=clean, roster_blueprint=blueprint):
        roster = [_clone(p) for p in roster_blueprint]
        team = Team(team_name, roster)
        team.lock_custom_starting_positions = True
        team.init_lineup()
        return team

    runner.factories[clean] = make_custom_team
    custom_team_factories[clean] = make_custom_team
    return {"ok": True, "name": clean, "count": len(players)}


# ------------------------------------------------------------------ Create / Edit Player
def form_meta() -> Dict:
    return {
        "fields": [{"key": k, "label": l, "default": d} for k, l, d in FIELD_DEFS],
        "positions": list(POSITIONS),
        "badges": [{"code": code, "label": sim_engine.plan_label(code)} for code in sorted(sim_engine.BADGE_DEFAULT_LEVELS)],
        "levels": [label for label, _ in LEVELS],
        "goTo": [{"code": "", "label": "Auto"}] + [{"code": c, "label": sim_engine.GO_TO_SHOT_PACKS[c]["label"]} for c in sorted(sim_engine.GO_TO_SHOT_PACKS)],
        "path": sim_engine.CUSTOM_PLAYERS_PATH,
        "players": [{"index": i, "name": p.name, "pos": p.position} for i, p in enumerate(players_data.load_custom_fantasy_players())],
    }


def player_form(index: int) -> Dict:
    """A saved custom player as the form shows it (ratings 0-100, height, extra badges, go-to shot)."""
    saved = players_data.load_custom_fantasy_players()
    if not (0 <= index < len(saved)):
        return {"error": "Could not find that custom player to edit."}
    p = saved[index]
    values = {}
    for key, _label, fallback in FIELD_DEFS:
        v = getattr(p, key, None)
        values[key] = str(round(v * 100)) if isinstance(v, float) else fallback
    feet, inches = divmod(int(getattr(p, "height", 78) or 78), 12)
    badges, seen = [], set()
    for badge in getattr(p, "badges", ()) or ():
        base, level = sim_engine.badge_parts(badge)
        if base in sim_engine.BADGE_DEFAULT_LEVELS and level and base not in seen:
            seen.add(base)
            badges.append({"code": base, "level": LEVEL_CODE_TO_LABEL.get(level, "Bronze")})
    go_to = str(getattr(p, "go_to_shot", "") or "")
    return {"index": index, "name": p.name, "position": p.position, "values": values, "feet": feet, "inches": inches,
            "badges": badges, "goTo": go_to if go_to in sim_engine.GO_TO_SHOT_PACKS else ""}


def _record(form: Dict) -> Dict:
    pos = str(form.get("position") or "SG").strip().upper() or "SG"
    try:
        height = int(form.get("feet", 6)) * 12 + int(form.get("inches", 6))
    except (TypeError, ValueError):
        height = 78
    badges = []
    for b in form.get("badges") or []:
        code = str(b.get("code", "")).strip()
        if code in sim_engine.BADGE_DEFAULT_LEVELS:
            badges.append(f"{code}_{LEVEL_LABEL_TO_CODE.get(b.get('level'), 'bronze')}")
    go_to = str(form.get("goTo") or "")
    record = {"name": str(form.get("name") or "").strip() or "Custom Player", "position": pos,
              "secondary_positions": sim_engine.default_secondary_positions(pos), "height": height, "badges": badges,
              "go_to_shot": go_to if go_to in sim_engine.GO_TO_SHOT_PACKS else ""}
    values = form.get("values") or {}
    for key in players_data.CUSTOM_PLAYER_FIELDS:
        record[key] = str(values.get(key, "")).strip()
    return record


def _similarity(a: Player, b: Player) -> float:
    weighted = (("three_rating", 1.20), ("mid_rating", 0.95), ("rim_rating", 1.05), ("dunk_rating", 0.80), ("playmaking", 1.05),
                ("ball_handle", 0.95), ("perimeter_def", 0.85), ("interior_def", 0.85), ("oreb", 0.45), ("dreb", 0.55), ("speed", 0.65),
                ("shot_iq", 0.80), ("three_tendency", 0.50), ("drive_tendency", 0.45), ("post_tendency", 0.45), ("iso_tendency", 0.60))
    total = sum(abs(getattr(a, f, 0.50) - getattr(b, f, 0.50)) * w for f, w in weighted)
    total += abs((getattr(a, "height", 78) or 78) - (getattr(b, "height", 78) or 78)) / 60.0
    if str(getattr(a, "position", "")) != str(getattr(b, "position", "")):
        total += 0.18
    return total


def _shades_of(player: Player) -> str:
    try:
        pool = all_pool_players()
    except Exception:
        pool = []
    matches = sorted(((_similarity(player, c), c) for c in pool if not (c.name == player.name and _source(c) == "Custom Player")), key=lambda m: m[0])
    labels, seen = [], set()
    for _score, c in matches:
        if c.name in seen:
            continue
        seen.add(c.name)
        labels.append(f"{c.name} ({_source(c)})")
        if len(labels) == 3:
            break
    return ", ".join(labels) if labels else "None"


def _build(form: Dict) -> Optional[Player]:
    player = players_data.custom_player_from_record(_record(form))
    if player is not None:
        player.secondary_positions = sim_engine.default_secondary_positions(player.position)
        player.archetype = players_data.infer_custom_player_archetype(player)
        sim_engine.assign_player_badges(Team("Custom Player", [player]))
    return player


def player_preview(form: Dict) -> Dict:
    player = _build(form)
    text = sim_engine.fantasy_player_preview_text(player)
    if player is not None:
        text += f"\nArchetype: {sim_engine.plan_label(player.archetype)}\nShades of: {_shades_of(player)}"
    pos = str(form.get("position") or "SG").upper()
    return {"text": text, "ok": player is not None, "secondary": ", ".join(sim_engine.default_secondary_positions(pos)) or "-"}


def save_player(runner, form: Dict) -> Dict:
    if runner.active:
        return {"error": "Finish or clear the current sim before creating a player."}
    player = _build(form)
    if player is None:
        return {"error": "Could not create that player. Check the name and ratings."}
    players = players_data.load_custom_fantasy_players()
    index = form.get("index")
    if isinstance(index, int) and 0 <= index < len(players):
        players[index] = player
        verb = "Updated"
    else:
        players.append(player)
        verb = "Saved"
    players_data.save_custom_fantasy_players(players)
    with _lock:
        _pool["players"] = None   # the pool picks the new player up next time Create Team opens
    return {"ok": True, "verb": verb, "name": player.name, "path": sim_engine.CUSTOM_PLAYERS_PATH}
