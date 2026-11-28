# Puts the project's code folders on the import path, so modules import each other by plain name
# (`import sim_engine`, `import players_data`, `from season_year import ...`) wherever they live.
# main.py, main_web.py and webui/__init__.py import this first. A script or one-off test run from
# the project folder does the same: `import project_paths` before importing any engine module.
# Spawned worker processes (multiprocessing "spawn") inherit sys.path from the parent.

import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
CODE_DIRS = [os.path.join(PROJECT_DIR, name) for name in ("engine", "seasons", "desktop")]

for _path in [PROJECT_DIR] + CODE_DIRS:
    if _path not in sys.path:
        sys.path.insert(1 if sys.path else 0, _path)
