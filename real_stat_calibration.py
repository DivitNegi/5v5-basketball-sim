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
    "2018 Boston Celtics": {
        # Kyrie's ratings are in teams/teams_2018.py; this keeps only his attempt role (~18 shots a night, no extra pace-keeping).
        "Kyrie Irving": {"target_fga_soft_cap": 19.0, "target_fga_per_game": 18.0, "target_fga_precision": 0.9, "keep_pace_shots": False},
    },
    "2018 Houston Rockets": {
        # Harden's ratings are calibrated in teams/teams_2018.py; this keeps only his attempt role:
        # 30+ a night on ~23 shots that keep the possession when behind pace.
        "James Harden": {"target_fga_soft_cap": 25.0, "target_fga_per_game": 23.0, "target_fga_precision": 1.0, "keep_pace_shots": True},
    },
    "2020 Houston Rockets": {
        # Harden's 2019-20 scoring title: ~34 points on ~23 shots and 11+ free throws. His hand-entered row had him
        # at a 0.30 usage / 0.64 foul draw / 0.40 shot IQ, which left him at ~19 points.
        "James Harden": {"usage": 0.45, "shot_tendency": 0.95, "foul_draw": 0.95, "shot_iq": 0.62, "three_rating": 0.91,
                         "target_fga_soft_cap": 25.0, "target_fga_per_game": 23.0, "target_fga_precision": 1.0, "keep_pace_shots": True},
    },
    "2024 Dallas Mavericks": {
        # Volume (usage / shot_tendency / three_tendency) is left to the hand-entered row; he takes ~23 shots a night.
        "Luka Doncic": {"block": 0.67, "dreb": 0.96, "dunk_rating": 0.93, "ft_rating": 0.784, "mid_rating": 0.99, "oreb": 0.617, "playmaking": 0.80, "foul_draw": 0.80, "rim_rating": 0.99, "steal": 0.77, "three_rating": 0.84,
                        # ~23 shots a night: an explicit attempt role plus opt-in "keep the possession when behind pace".
                        "target_fga_soft_cap": 25.0, "target_fga_per_game": 22.6, "target_fga_precision": 1.0, "keep_pace_shots": True},
    },
}


def apply_overrides(team):
    table = OVERRIDES.get(getattr(team, "name", ""))
    if table:
        for player in team.roster:
            for attr, value in table.get(player.name, {}).items():
                setattr(player, attr, value)
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
