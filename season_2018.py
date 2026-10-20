"""
2017-18 NBA regular season (82 games, real NBA schedule structure) and a "Full 2018 playoffs" bracket.

Mirrors run_2027_season / run_2027_playoffs in players_data.py for the 30 `make_*_2018` teams; the
playoffs after the season reuse run_2027_postseason with this season's factories. There is no play-in for
2018 (it started in 2020-21): seeds 1-8 in each conference go straight to the bracket, and the All-NBA and
All-Defensive teams are picked by position (two guards, two forwards, one center), as they were then.
"""
import random
from typing import Dict

import players_data as pd
import sim_engine
from sim_engine import (
    SeasonGameLog, add_player_to_series_totals, add_team_to_series_totals, build_season_sections,
    season_entry_from_factory, simulate_silent_season_game,
)

SEASON_2018_DIVISIONS = pd.SEASON_2027_DIVISIONS  # same five-team divisions; the team keys are year-agnostic

PLAYOFF_2018_CONFERENCES = {
    conference: [f"make_{key}_2018" for divisions in [SEASON_2018_DIVISIONS[conference]] for keys in divisions.values() for key in keys]
    for conference in ("East", "West")
}


def factories_2018() -> Dict[str, object]:
    """{team name: factory} for every 2018 team."""
    out = {}
    for divisions in SEASON_2018_DIVISIONS.values():
        for keys in divisions.values():
            for key in keys:
                factory = getattr(pd, f"make_{key}_2018")
                out[factory().name] = factory
    return out


def _run_2018_season_game(task):
    """Worker entry point: simulate one silent season game and return the finished teams."""
    home_key, away_key = task[0], task[1]
    order = task[2] if len(task) > 2 else None
    sim_engine.SEASON_STAR_MINUTES_CAP = 34
    team_a, team_b = simulate_silent_season_game(
        getattr(pd, f"make_{home_key}_2018"), getattr(pd, f"make_{away_key}_2018")
    )
    return home_key, away_key, team_a, team_b, order


def run_2018_season(section_queue=None, progress_queue=None) -> Dict:
    pd.POSTSEASON_YEAR_LABEL = "2018"
    pd.POSTSEASON_SEASON_LABEL = "2017-18"
    pd.POSTSEASON_PLAY_IN = False   # the play-in tournament did not exist in 2017-18
    games, conf_of = pd.build_2027_season_schedule()
    games = [(home, away, order) for order, (home, away) in enumerate(games)]
    entries = []
    for key, conference in conf_of.items():
        factory = getattr(pd, f"make_{key}_2018")
        entry = season_entry_from_factory(factory().name, factory)
        entry["conference"] = conference
        entries.append(entry)
    entry_by_name = {entry["name"]: entry for entry in entries}
    player_totals, team_totals = {}, {}
    game_log = SeasonGameLog()
    total_games = len(games)
    print("\n=== 2018 SEASON (82 games per team, NBA schedule) ===")
    print(f"Quiet-simming {total_games} games. No play-by-play during the regular season.")
    if progress_queue is not None:
        progress_queue.put({"season_progress": True, "completed": 0, "total": total_games})

    def snap():
        sim_engine.season_pause_snapshot(section_queue, entries, player_totals, team_totals, game_log, None, total_games,
                                         positional=True)   # the 2018 All-NBA / All-Defensive teams are picked by position

    live_tick = sim_engine.make_season_live_updater(snap)

    def parallel_results():
        import multiprocessing
        import os
        import time as _time
        workers = max(1, min(12, (os.cpu_count() or 4) - 2))
        pool = multiprocessing.get_context("spawn").Pool(processes=workers)
        try:
            batch = workers * 6
            for start in range(0, len(games), batch):
                sim_engine.hold_season_while_paused(snap)
                for result in pool.imap_unordered(_run_2018_season_game, games[start:start + batch], chunksize=2):
                    yield result
        finally:
            pool.terminate()
            pool.join()

    def sequential_results():
        import time as _time
        for home_key, away_key, order in games:
            sim_engine.hold_season_while_paused(snap)
            yield _run_2018_season_game((home_key, away_key, order))

    try:
        import os as _os
        use_parallel = (_os.cpu_count() or 1) >= 4
    except Exception:
        use_parallel = False
    results = parallel_results() if use_parallel else sequential_results()
    for done, (home_key, away_key, team_a, team_b, order) in enumerate(results, start=1):
        sim_engine.hold_season_while_paused(snap)
        add_player_to_series_totals(player_totals, team_a)
        add_player_to_series_totals(player_totals, team_b)
        add_team_to_series_totals(team_totals, team_a)
        add_team_to_series_totals(team_totals, team_b)
        game_log.add(team_a, team_b, order)
        a, b = entry_by_name[team_a.name], entry_by_name[team_b.name]
        a["pf"] += team_a.score
        a["pa"] += team_b.score
        b["pf"] += team_b.score
        b["pa"] += team_a.score
        if team_a.score > team_b.score:
            a["wins"] += 1
            b["losses"] += 1
            team_totals[team_a.name]["wins"] += 1
        else:
            b["wins"] += 1
            a["losses"] += 1
            team_totals[team_b.name]["wins"] += 1
        if progress_queue is not None:
            progress_queue.put({"season_progress": True, "completed": done, "total": total_games})
            if done % 6 == 0 or done == total_games:
                progress_queue.put({
                    "season_standings": [
                        {
                            "conference": e["conference"], "team": e["name"], "wins": e["wins"], "losses": e["losses"],
                            "pf": e["pf"] / max(1, e["wins"] + e["losses"]), "pa": e["pa"] / max(1, e["wins"] + e["losses"]),
                            "diff": (e["pf"] - e["pa"]) / max(1, e["wins"] + e["losses"]), "strength": e["strength"],
                        }
                        for e in entries
                    ],
                    "completed": done, "total": total_games,
                })
            progress_queue.put(sim_engine.live_season_races_payload(entries, player_totals, team_totals, done, total_games))
        live_tick()
        sim_engine.season_game_pace()
        if done % 300 == 0:
            print(f"Season sim progress: {done}/{total_games} games.")

    sim_engine.SEASON_STAR_MINUTES_CAP = None
    sim_engine.SEASON_POSITIONAL_AWARDS = True
    try:
        sections = build_season_sections(entries, player_totals, team_totals, game_log=game_log.rows,
                                         game_extras=game_log.extras, game_meta=game_log.games)
    finally:
        sim_engine.SEASON_POSITIONAL_AWARDS = False
    if section_queue is not None:
        section_queue.put(sections)

    print("\n2018 SEASON FINAL STANDINGS")
    for conference in ("East", "West"):
        print(f"\n{conference}ern Conference" if conference == "East" else "\nWestern Conference")
        ranked = sorted(
            (e for e in entries if e["conference"] == conference),
            key=lambda e: (-e["wins"], -(e["pf"] - e["pa"])),
        )
        for seed, e in enumerate(ranked, start=1):
            games_played = e["wins"] + e["losses"]
            diff = (e["pf"] - e["pa"]) / max(1, games_played)
            mark = "*" if seed <= 8 else " "
            print(f" {seed:>2}{mark} {e['name']:<32}{e['wins']:>3}-{e['losses']:<3}  {diff:+5.1f}")
    print("\n* = top 8, playoff team. Standings, averages, advanced stats, shot diet and awards are in the tabs.")
    return sections


def playoff_2018_field():
    """{conference: [(team_name, seed, strength, factory_name), ...]} for the 8 strongest per conference."""
    field = {}
    for conference, factory_names in PLAYOFF_2018_CONFERENCES.items():
        rated = []
        for factory_name in factory_names:
            team = getattr(pd, factory_name)()
            rated.append((team.name, pd.team_strength_2027(team), factory_name))
        rated.sort(key=lambda item: -item[1])
        field[conference] = [(name, seed, strength, factory_name)
                             for seed, (name, strength, factory_name) in enumerate(rated[:8], start=1)]
    return field


def run_2018_playoffs():
    pd.POSTSEASON_YEAR_LABEL = "2018"
    pd.POSTSEASON_SEASON_LABEL = "2017-18"
    pd.POSTSEASON_PLAY_IN = False   # the play-in tournament did not exist in 2017-18
    field = playoff_2018_field()
    factories = {name: getattr(pd, factory) for rows in field.values() for name, _s, _st, factory in rows}
    pd.run_2027_playoffs(field, factories)
