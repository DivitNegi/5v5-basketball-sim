# 5v5 Basketball Sim

A text-driven basketball simulation engine with a Tkinter GUI (and a secondary
lightweight web GUI), covering full 5-on-5 games, a 1-on-1 street-ball mode,
season/playoff/fantasy-draft simulation, and a large roster of historical,
current, Olympic, and custom teams.

## Project structure

Originally a single ~43,000-line script; split into modules by concern:

- **`sim_engine.py`** — the core simulation engine: `Player`/`Team` data
  models, shot math, possession resolution, box scores, ratings/badges,
  play-by-play commentary, the full 5-on-5 game loop (`simulate_game`), the
  1-on-1 mode (`simulate_1v1_game`), and the season/playoff/fantasy-draft
  subsystem.
- **`teams/teams_YYYY.py`** — one file per season holding that season's team
  rosters (`make_*_YYYY` factory functions), e.g. `teams/teams_2018.py`.
  `teams/teams_olympic.py` holds the special international teams (1992 Dream Team,
  2008 Redeem Team and the 2024 Olympic field).
- **`players_data.py`** — imports every `teams/teams_YYYY.py`, applies the
  real-stat calibration overrides, and holds the fantasy player pool builder,
  the postseason/season runners and the team-factory registries
  (`gui_team_factories`, `fantasy_team_factories`).
- **`gui_app.py`** — the primary Tkinter desktop GUI.
- **`web_app.py`** — a secondary, browser-based GUI served over local HTTP
  (used as a fallback when Tkinter isn't available).
- **`main.py`** — entry point; running it opens the GUI.

### A note on the split

`players_data.py` imports from `sim_engine.py` (team factories need the
`Player`/`Team` classes and a few lineup-balancing helpers). A handful of
functions in `sim_engine.py`'s season/fantasy-draft/Olympic-tournament code
need to call back into `players_data.py`'s team-factory registries; those
use function-local imports to avoid a circular import at module load time.

A small set of simulation-speed/pause/queue globals (`SLEEP`,
`SIM_FAST_FORWARD`, `SIM_PAUSED`, the GUI queues, etc.) are owned by
`sim_engine.py`. Code in `gui_app.py`/`web_app.py` that needs to read or
change them does so through qualified `sim_engine.<name>` access rather than
a bare `global` statement, since `global` always binds to the module a
function is defined in.

## Running it

```bash
python main.py               # opens the Tkinter desktop GUI
```

Requires Python 3.10+. `Pillow` is optional (used for logo/headshot images
in the GUI; the app falls back to plain drawn placeholders if it's not
installed).
