"""The badges each player plays with: his file badges plus everything the engine assigns from his ratings, at the level he has it."""
import sim_engine


def team_badges(runner, team_name):
    """{player name: [badge strings]} for one team, built the way a game builds it."""
    factory = (getattr(runner, "factories", None) or {}).get(team_name)
    if not factory:
        return {}
    try:
        team = factory()
        sim_engine.apply_star_clutchness(team)
        sim_engine.assign_player_badges(team)
    except Exception:
        return {}
    return {p.name: list(getattr(p, "badges", ()) or ()) for p in team.roster}


def player_badges(runner, team_name, name):
    return team_badges(runner, team_name).get(name, [])
