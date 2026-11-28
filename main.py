# 5v5 basketball simulator entry point: running this file opens the GUI.

import multiprocessing
import sys

import project_paths  # noqa: F401  (puts engine/, seasons/, desktop/ on the import path)
from gui_app import run_gui_app


def main():
    run_gui_app()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
    sys.exit(0)
