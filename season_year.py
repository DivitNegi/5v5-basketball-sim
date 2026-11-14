"""
A full regular season (82 games, NBA schedule structure) for any year that has all 30 `make_*_<year>` teams, followed by the
shared play-in and playoffs (players_data.run_2027_postseason with this season's factories). Mirrors season_2018.py and
run_2027_season in players_data.py.

Per year: the labels, whether the season had a play-in tournament (from 2020-21), and whether the All-NBA / All-Defensive
teams were picked by position (two guards, two forwards, one center, up to 2022-23) or not (from 2023-24).
"""
import random
from typing import Dict

import players_data as pd
import sim_engine
from sim_engine import (
    SeasonGameLog, add_player_to_series_totals, add_team_to_series_totals, build_season_sections,
    season_entry_from_factory, simulate_silent_season_game,
)

SEASON_YEARS = {
    2016: {"label": "2016", "season_label": "2015-16", "play_in": False, "positional": True},   # before the play-in: seeds 1-8 go straight to the playoffs
    2021: {"label": "2021", "season_label": "2020-21", "play_in": True, "positional": True},
    2022: {"label": "2022", "season_label": "2021-22", "play_in": True, "positional": True},
    2023: {"label": "2023", "season_label": "2022-23", "play_in": True, "positional": True},
    2026: {"label": "2026", "season_label": "2025-26", "play_in": True, "positional": False},
}


def factories_for_year(year: int) -> Dict[str, object]:
    """{team name: factory} for every team of that year."""
    out = {}
    for divisions in pd.SEASON_2027_DIVISIONS.values():
        for keys in divisions.values():
            for key in keys:
                factory = getattr(pd, f"make_{key}_{year}")
                out[factory().name] = factory
    return out


def _run_year_season_game(task):
    """Worker entry point: simulate one silent season game and return the finished teams."""
    home_key, away_key, order, seed, year = task
    sim_engine.SEASON_STAR_MINUTES_CAP = 34
    team_a, team_b = simulate_silent_season_game(
        getattr(pd, f"make_{home_key}_{year}"), getattr(pd, f"make_{away_key}_{year}"), seed
    )
    return home_key, away_key, team_a, team_b, order


def run_year_season(year: int, section_queue=None, progress_queue=None) -> Dict:
    info = SEASON_YEARS[year]
    pd.POSTSEASON_YEAR_LABEL = info["label"]
    pd.POSTSEASON_SEASON_LABEL = info["season_label"]
    pd.POSTSEASON_PLAY_IN = info["play_in"]
    games, conf_of = pd.build_2027_season_schedule()
    games = [(home, away, order, random.getrandbits(32), year) for order, (home, away) in enumerate(games)]
    entries = []
    name_of_key = {}
    sim_engine.season_replay_reset()
    for key, conference in conf_of.items():
        factory = getattr(pd, f"make_{key}_{year}")
        entry = season_entry_from_factory(factory().name, factory)
        entry["conference"] = conference
        entries.append(entry)
        name_of_key[key] = entry["name"]
        sim_engine.season_replay_register_maker(entry["name"], factory)
    for home_key, away_key, order, seed, _year in games:
        sim_engine.season_replay_register_game(order, name_of_key[home_key], name_of_key[away_key], seed)
    entry_by_name = {entry["name"]: entry for entry in entries}
    fixtures = [(order + 1, name_of_key[home_key], name_of_key[away_key]) for home_key, away_key, order, _seed, _y in games]   # the whole schedule, so the schedule tab can list upcoming games
    player_totals, team_totals = {}, {}
    game_log = SeasonGameLog()
    total_games = len(games)
    print(f"\n=== {info['label']} SEASON (82 games per team, NBA schedule) ===")
    print(f"Quiet-simming {total_games} games. No play-by-play during the regular season.")
    if progress_queue is not None:
        progress_queue.put({"season_progress": True, "completed": 0, "total": total_games})

    def snap():
        sim_engine.season_pause_snapshot(section_queue, entries, player_totals, team_totals, game_log, None, total_games,
                                         positional=info["positional"], fixtures=fixtures)

    live_tick = sim_engine.make_season_live_updater(snap)

    def parallel_results():
        import multiprocessing
        import os
        workers = max(1, min(12, (os.cpu_count() or 4) - 2))
        pool = multiprocessing.get_context("spawn").Pool(processes=workers)
        try:
            batch = workers * 6
            for start in range(0, len(games), batch):
                sim_engine.hold_season_while_paused(snap)
                for result in pool.imap_unordered(_run_year_season_game, games[start:start + batch], chunksize=2):
                    yield result
        finally:
            pool.terminate()
            pool.join()

    def sequential_results():
        for task in games:
            sim_engine.hold_season_while_paused(snap)
            yield _run_year_season_game(task)

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
    sim_engine.SEASON_POSITIONAL_AWARDS = info["positional"]
    try:
        sections = build_season_sections(entries, player_totals, team_totals, game_log=game_log.rows,
                                         game_extras=game_log.extras, game_meta=game_log.games, fixtures=fixtures)
    finally:
        sim_engine.SEASON_POSITIONAL_AWARDS = False
    if section_queue is not None:
        section_queue.put(sections)

    print(f"\n{info['label']} SEASON FINAL STANDINGS")
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
    print("\n* = top 8 (10 with the play-in): Standings, averages, advanced stats, shot diet and awards are in the tabs.")
    return sections
