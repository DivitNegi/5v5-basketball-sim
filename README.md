# 5v5 Basketball Sim

A possession-by-possession NBA basketball simulator with live play-by-play, shot charts and a deep stats layer, played
through a browser UI (with the original Tkinter desktop app kept as a backup).

- **Games:** single games, Game 7s, a 1-on-1 street mode, NBA or FIBA rules, with live speed control and "sim to" jumps.
- **Seasons:** full 82-game seasons on the real NBA schedule for 2016, 2018 and 2021-2027, with hot/cold form, the play-in,
  playoffs, replays of any season or playoff game, and awards (MVP, DPOY, Rookie of the Year, Most Improved, All-NBA,
  All-Defensive, All-Rookie) with live award races.
- **Other modes:** playoff series, custom 16-team playoffs, custom 82-game seasons, fantasy drafts (2027 players or
  all-time) and an Olympic tournament.
- **Teams:** 341 teams from 1962 to 2027, plus the 1992 Dream Team, the 2008 Redeem Team and the 2024 Olympic field.
- **Stats:** box scores, advanced stats, shot charts and zones, defended shots, matchups, on/off, play types, finishes,
  clutch, shot-making vs expected, assist networks, splits and game logs.
- **Tools:** a live ratings editor, team/player builder, lineups, coaching and draft & trades.

## Running it

```bash
python main_web.py                # browser UI at http://127.0.0.1:8790 (opens a tab)
python main_web.py --no-browser   # same, without opening a tab
python main.py                    # Tkinter desktop app (backup)
```

Requires Python 3.10+ and nothing else. `Pillow` is optional (logos and headshots in the desktop app).

Restarting the web server locks in ratings-editor edits: the editor's Reset and revert arrows only cover edits made since
the server started.

## Project structure

```
main_web.py            browser UI entry point (python main_web.py)
main.py                Tkinter desktop app entry point (backup)
project_paths.py       puts engine/, seasons/ and desktop/ on the import path
engine/                the simulator
seasons/               82-game season runners
teams/                 one roster file per season
webui/                 the browser UI (Python API + static front end)
desktop/               the Tkinter desktop app
data/                  JSON data files the engine reads
nba_logo_cache/, nba_headshot_cache/   downloaded images (git-ignored)
```

- **`engine/sim_engine.py`**: the whole engine. `Player`/`Team` models, possessions, play types and team playbooks, shot
  choice and make chance, fouls, passing and assists, rebounds, badges, minutes and rotations, play-by-play, seasons,
  awards, playoffs, fantasy drafts and the analytics counters. `simulate_game` is the 5-on-5 game loop,
  `simulate_1v1_game` the 1-on-1 mode and `simulate_silent_season_game` a quiet seeded game.
- **`engine/players_data.py`**: imports every team file, applies real-stat calibration (`engine/real_stat_calibration.py`)
  and holds the team-factory registries (`gui_team_factories()`), divisions and postseason runners.
- **`engine/broadcast.py`**, **`engine/archetypes.py`**, **`engine/media_ids.py`**: commentary, player archetypes,
  headshot/logo ids.
- **`teams/teams_YYYY.py`**: one file per season, each team a `make_<team>_<year>` factory of `Player(...)` ratings and
  tendencies. `teams/teams_olympic.py` holds the international teams.
- **`seasons/season_year.py`** / **`seasons/season_2018.py`**: 82-game seasons (`SEASON_YEARS`, `run_year_season`).
  They use multiprocessing, so a script that calls them needs an `if __name__ == "__main__":` guard.
- **`webui/`**: the browser UI. `server.py` (HTTP API), `runner.py` (runs every mode), `stats.py` (stats tables and
  player pages), `live.py` (live game), `ratings_editor.py`, `builder.py`, `shots.py`, `badges.py`, `hub.py`, and
  `static/` (`index.html`, `js/app.js`, `css/app.css`).
- **`desktop/gui_app.py`**: the Tkinter desktop app.
- **`data/`**: `real_minutes.json` (real minutes per team-season), `shot_profiles.json` (real shot-distance splits),
  `mip_data.json` (Most Improved candidates), `schedule_2027.json`, `headshot_ids_extra.json`. Created players and
  saved roster swaps go to `data/custom_players.json` and `data/custom_roster_swaps.json` (git-ignored).

Modules import each other by plain name (`import sim_engine`, `from season_year import ...`) because
`project_paths.py` adds the code folders to `sys.path`; `main.py`, `main_web.py` and `webui/__init__.py` import it first.
`players_data.py` imports `sim_engine.py`; the few engine functions that need the team registries import
`players_data` inside the function to avoid a circular import. Simulation speed/pause globals (`SLEEP`,
`SIM_FAST_FORWARD`, `SIM_PAUSED`, ...) live in `sim_engine.py` and are changed through `sim_engine.<name>`.

## Testing a change

Run from the project folder. Import `project_paths` first, and redirect stdout because the engine prints a lot:

```python
import contextlib, io
import project_paths   # engine/, seasons/, desktop/ on the import path
with contextlib.redirect_stdout(io.StringIO()):
    import sim_engine as se, players_data as pd

se.SEASON_STAR_MINUTES_CAP = 34          # regular-season minutes rules, as in a real season
f = pd.gui_team_factories()
a, b = se.simulate_silent_season_game(f["2024 Boston Celtics"], f["2024 Dallas Mavericks"], seed=1)
```

The same seed always plays out the same game. Check per-player numbers over at least a full season per team
(`season_year.run_year_season(year)`, about 10 minutes): a few dozen games per player is too noisy.
