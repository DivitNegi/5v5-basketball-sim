"""
Per-player rating / tendency calibration against real regular-season lines.

players_data.py builds every historical team from hand-entered ratings. This
module holds the corrections found by comparing a simulated season with the
real per-game stats of the same players (points, rebounds, assists, FG%, 3P%,
FT%, steals, blocks, attempts). Everything here is an ordinary rating or
tendency -- no volume caps. OVERRIDES maps

    team name -> player name -> {attribute: value}

and wrap_factories() applies it every time a make_*_YYYY team is built.
"""
import functools

OVERRIDES = {
    # Only attempt ROLES live here (shots per game, keep-the-possession-when-behind-pace, how often a player swings it instead of
    # shooting). Every rating and tendency is in the team files (teams/teams_YYYY.py), so the row you edit by hand is the value used.
    "2018 Boston Celtics": {
        # Kyrie: ~18 shots a night, no extra pace-keeping.
        "Kyrie Irving": {"target_fga_soft_cap": 19.0, "target_fga_per_game": 18.0, "target_fga_precision": 0.9, "keep_pace_shots": False},
    },
    "2018 Houston Rockets": {
        # Harden: 30+ a night on ~23 shots that keep the possession when behind pace.
        "James Harden": {"target_fga_soft_cap": 25.0, "target_fga_per_game": 23.0, "target_fga_precision": 1.0, "keep_pace_shots": True},
    },
    "2020 Houston Rockets": {
        # Harden's 2019-20 scoring title: ~34 points on ~23 shots and 11+ free throws.
        "James Harden": {"target_fga_soft_cap": 25.0, "target_fga_per_game": 23.0, "target_fga_precision": 1.0, "keep_pace_shots": True},
    },
    "2024 Dallas Mavericks": {
        # Luka: ~23 shots a night, with opt-in "keep the possession when behind pace".
        "Luka Dončić": {"target_fga_soft_cap": 25.0, "target_fga_per_game": 22.6, "target_fga_precision": 1.0, "keep_pace_shots": True},
    },
    "2027 Philadelphia 76ers": {
        # no shot targets: shot volume comes from each player's tendencies (tuned to Basketball-Reference 2026-27). LeBron keeps a
        # pass tendency so his 0.99 playmaking does not make him swing away most of his own looks.
        "LeBron James": {"extra_pass_scale": 0.6, "score_first_bias": 0.5},   # keeps more of the possessions he brings up
    },
}


_SHOT_PROFILES = None


def _fold(name: str) -> str:
    import unicodedata
    n = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower()
    for junk in (".", "'", ",", " jr", " sr", " iii", " ii", " iv"):
        n = n.replace(junk, "")
    return " ".join(n.split())


def shot_profiles():
    """Real shooting splits per team-season and player (shot_profiles.json, from Basketball-Reference): where each player's shots came from."""
    global _SHOT_PROFILES
    if _SHOT_PROFILES is None:
        import json, os
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "shot_profiles.json")
        try:
            with open(path, encoding="utf-8") as handle:
                _SHOT_PROFILES = json.load(handle)
        except (OSError, ValueError):
            _SHOT_PROFILES = {}
    return _SHOT_PROFILES


def apply_overrides(team):
    table = OVERRIDES.get(getattr(team, "name", ""))
    if table:
        for player in team.roster:
            for attr, value in table.get(player.name, {}).items():
                setattr(player, attr, value)
    profiles = shot_profiles().get(getattr(team, "name", ""))
    if profiles:
        for player in team.roster:
            prof = profiles.get(_fold(player.name))
            if prof:
                player.shot_profile = prof
    return team


def _wrap(factory):
    @functools.wraps(factory)
    def wrapped(*args, **kwargs):
        return apply_overrides(factory(*args, **kwargs))

    return wrapped


def _is_team_factory(name, fn):
    return (
        name.startswith("make_") and callable(fn) and name[-5:-4] == "_" and name[-4:].isdigit()
        and not getattr(fn, "_real_stat_wrapped", False)
    )


def wrap_factories(namespace):
    """Wrap every make_*_YYYY factory in `namespace`, including the ones stored in
    module-level registries (e.g. PLAYOFF_2016_TEAM_FACTORIES)."""
    for name, fn in list(namespace.items()):
        if _is_team_factory(name, fn):
            wrapped = _wrap(fn)
            wrapped._real_stat_wrapped = True
            namespace[name] = wrapped
    for value in list(namespace.values()):
        if isinstance(value, dict):
            for key, fn in list(value.items()):
                if callable(fn) and _is_team_factory(getattr(fn, "__name__", ""), fn):
                    wrapped = _wrap(fn)
                    wrapped._real_stat_wrapped = True
                    value[key] = wrapped
