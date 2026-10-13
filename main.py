# 5v5 basketball simulator entry point: running this file opens the GUI.

import multiprocessing
import sys

from gui_app import run_gui_app


def main():
    run_gui_app()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
    sys.exit(0)
