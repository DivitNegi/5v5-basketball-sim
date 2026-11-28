# 5v5 basketball simulator, browser UI: run this file and the app opens in your browser.
# The Tkinter app (main.py) is still the full-featured backup.

import multiprocessing
import sys

import project_paths  # noqa: F401  (puts engine/, seasons/, desktop/ on the import path)
from webui.server import run


def main():
    run(open_browser="--no-browser" not in sys.argv)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
