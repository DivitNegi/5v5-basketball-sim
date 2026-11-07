"""Runs simulations for the browser UI on a background thread and turns the engine's output into events."""
import builtins
import json
import queue
import sys
import threading
import time
import traceback
from typing import Dict, Optional

import sim_engine
import players_data
from season_2018 import run_2018_season, factories_2018
from season_year import run_year_season, factories_for_year
from gui_app import GuiOutputProxy, FANTASY_SEASON_MODES   # same play-by-play filter and scoreboard parsing as the Tk app

from .hub import EventHub
from .live import live_snapshot, team_identity

# Modes the browser UI can run today. The rest of the Tk modes are added as their screens are built.
SEASON_MODES = {"2021 season (82 games)": 2021, "2022 season (82 games)": 2022, "2023 season (82 games)": 2023, "2026 season (82 games)": 2026}
SEASON_LIKE = tuple(SEASON_MODES) + ("2027 season (82 games)", "2018 season (82 games)")
SUPPORTED_MODES = ("Game", "Playoff series") + SEASON_LIKE + ("2027 play-in & playoffs",)
ALL_MODES = (
    "Game", "1-on-1", "Playoff series", "Custom 16-team playoffs", "Full 2027 playoffs", "2027 season (82 games)",
    "2018 season (82 games)", "2021 season (82 games)", "2022 season (82 games)", "2023 season (82 games)", "2026 season (82 games)",
    "Full 2018 playoffs", "Custom season (82 games)", "Fantasy draft: 2027 players (season + playoffs)",
    "Fantasy draft: all-time (season + playoffs)", "Fantasy draft playoffs", "Olympic tournament",
)
JUMP_TARGETS = {"game": None, "end1": "end1", "half": "half", "end3": "end3", "last5": "last5", "last2": "last2"}


class WebOutputProxy(GuiOutputProxy):
    """The Tk app's output proxy, minus its 1 ms pause per write while a "sim to" jump is fast-forwarding."""
    def write(self, text):
        if not text:
            return
        if sim_engine.SIM_FAST_FORWARD and not getattr(sim_engine, "SIM_STICKY_FAST", None):
            self.full_output.append(text)
            self.buffer += text
            while "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                clean = line.strip()
                self._maybe_scoreboard(clean)
                self._maybe_series_record(clean)
                if self._should_show_in_play_log(clean):
                    self.output_queue.put(line + "\n")
            return
        super().write(text)


class _Sink:
    """Stands in for the Tk app's queues: whatever the output proxy puts goes straight to a callback."""
    def __init__(self, callback):
        self.put = callback


class SimRunner:
    def __init__(self, hub: EventHub):
        self.hub = hub
        self.lock = threading.Lock()
        self.active = False
        self.mode = None
        self.status = "Ready"
        self.speed = 1.0
        self.factories = players_data.gui_team_factories()
        self.score = None              # latest parsed scoreboard line
        self.series = None             # latest series record
        self.flow = []                 # (period, clock, margin) points for the game-flow chart
        self.last_live = None          # last live snapshot (kept after the game ends for the final box score)
        self.sections: Dict = {}
        self.season = {"progress": None, "races": None, "standings": None, "ready": False}
        self.post = {"standings": None, "factories": None, "year": None}
        self.bracket = {}
        self._live_signature = None
        self._engine_queue = queue.Queue()
        threading.Thread(target=self._pump_engine_messages, daemon=True).start()
        threading.Thread(target=self._tick_live, daemon=True).start()

    # ---------------------------------------------------------------- state
    def season_state(self) -> Dict:
        sec = self.sections or {}
        return {**self.season, "hasSections": bool(sec), "keys": sorted(k for k in sec if k.startswith("_"))}

    def meta(self) -> Dict:
        return {
            "teams": [team_identity(name) for name in self.factories],
            "modes": [{"name": m, "ready": m in SUPPORTED_MODES} for m in ALL_MODES],
            "rules": ["NBA", "FIBA"],
        }

    def state(self) -> Dict:
        return {
            "active": self.active, "mode": self.mode, "status": self.status, "speed": self.speed,
            "paused": bool(sim_engine.SIM_PAUSED), "score": self.score, "series": self.series,
            "flow": self.flow, "live": self.last_live, "sectionsReady": bool(self.sections), "season": self.season_state(),
        }

    def set_status(self, text: str):
        self.status = text
        self.hub.publish({"type": "status", "text": text, "active": self.active, "paused": bool(sim_engine.SIM_PAUSED), "speed": self.speed})

    # --------------------------------------------------------------- control
    def start(self, mode: str, team_a: str, team_b: str, rules: str = "NBA") -> Optional[str]:
        if mode == "Next":
            mode = "2027 play-in & playoffs"
            if not self.season.get("ready"):
                return "Finish a season first."
        if mode not in SUPPORTED_MODES:
            return f"{mode} is not in the browser UI yet. Use the Tk app for it for now."
        needs_teams = mode in ("Game", "Playoff series")
        if needs_teams and (team_a not in self.factories or team_b not in self.factories):
            return "Pick two teams from the list."
        if needs_teams and team_a == team_b:
            return "Pick two different teams."
        with self.lock:
            if self.active:
                return "A simulation is already running."
            self.active = True
        self.mode = mode
        keep = mode == "2027 play-in & playoffs"
        self.score, self.series, self.flow, self.last_live = None, None, [], None
        if not keep:
            self.sections = {}
            self.season = {"progress": None, "races": None, "standings": None, "ready": False}
        self._live_signature = None
        self.hub.clear_backlog()
        self.hub.publish({"type": "reset", "mode": mode, "teams": [team_identity(team_a), team_identity(team_b)] if needs_teams else [None, None]})
        threading.Thread(target=self._run, args=(mode, team_a, team_b, rules), daemon=True).start()
        return None

    def control(self, action: str, value=None) -> Optional[str]:
        if action == "speed":
            self.speed = max(0.5, min(20.0, round(float(value), 2)))
            sim_engine.SIM_SLEEP_SCALE = 1.0 / self.speed
            self.set_status(self.status)
            return None
        if not self.active:
            return "Start a simulation first."
        if action == "pause":
            sim_engine.SIM_PAUSED = not sim_engine.SIM_PAUSED
            self.set_status("Paused" if sim_engine.SIM_PAUSED else "Running")
        elif action == "jump":
            if value not in JUMP_TARGETS:
                return "Unknown jump."
            sim_engine.SIM_FAST_FORWARD = True
            sim_engine.SIM_JUMP_TARGET = JUMP_TARGETS[value]
            self.set_status({"game": "Simming to the end of the game", "end1": "Simming to the end of the 1st", "half": "Simming to halftime",
                             "end3": "Simming to the end of the 3rd", "last5": "Simming to the final 5 minutes",
                             "last2": "Simming to the final 2 minutes"}[value])
        elif action == "simPlayoffs":
            sim_engine.SIM_STICKY_FAST = "playoffs"
            sim_engine.SIM_FAST_FORWARD = True
            sim_engine.SIM_JUMP_TARGET = None
            self.set_status("Simming all the playoffs")
        elif action == "simSeries":
            sim_engine.SIM_STICKY_FAST = "series"
            sim_engine.SIM_FAST_FORWARD = True
            sim_engine.SIM_JUMP_TARGET = None
            self.set_status("Simming the rest of the series")
        else:
            return "Unknown action."
        return None

    # ------------------------------------------------------------------ run
    def _on_pbp(self, text: str):
        line = text.rstrip("\n")
        self.hub.publish({"type": "pbp", "text": line}, keep=True)

    def _on_section(self, sections):
        if isinstance(sections, dict):
            merged = dict(self.sections or {})
            merged.update(sections)
            self.sections = merged
            self.hub.publish({"type": "sections", "keys": sorted(k for k in merged if k.startswith("_"))})

    def _on_season_message(self, message: Dict) -> bool:
        if message.get("season_progress"):
            self.season["progress"] = {"completed": message.get("completed", 0), "total": message.get("total", 1230)}
            self.hub.publish({"type": "season", "season": self.season_state()})
        elif "season_races" in message:
            self.season["races"] = message["season_races"]
            self.season["progress"] = {"completed": message.get("completed", 0), "total": message.get("total", 1230)}
            self.hub.publish({"type": "season", "season": self.season_state()})
        elif "season_standings" in message:
            self.season["standings"] = message["season_standings"]
            self.hub.publish({"type": "season", "season": self.season_state()})
        elif message.get("postseason_ready"):
            self.season["ready"] = True
            self.hub.publish({"type": "season", "season": self.season_state()})
        else:
            return False
        return True

    def _on_score(self, message: Dict):
        if self._on_season_message(message):
            return
        if "period" in message and "clock" in message and "score_a" in message:
            self.score = message
            if self.status.startswith("Simming") and not sim_engine.SIM_FAST_FORWARD and not sim_engine.SIM_STICKY_FAST:
                self.set_status("Paused" if sim_engine.SIM_PAUSED else "Running")   # the jump target was reached
            try:
                self.flow.append([message["period"], message["clock"], int(message["score_a"]) - int(message["score_b"])])
                del self.flow[:-3000]
            except (TypeError, ValueError):
                pass
            self.hub.publish({"type": "score", **message})
            self._push_live(force=True)
        elif "series_status" in message or "game_result" in message:
            self.series = {**(self.series or {}), **message}
            self.hub.publish({"type": "series", **message}, keep=True)

    def _run(self, mode: str, team_a_name: str, team_b_name: str, rules: str):
        original_stdout, original_input = sys.stdout, builtins.input
        original_engine_queue = sim_engine.GUI_SCOREBOARD_QUEUE
        original_ruleset = sim_engine.CURRENT_RULESET
        proxy = WebOutputProxy(_Sink(self._on_pbp), _Sink(self._on_score), original_stdout)
        sys.stdout = proxy
        builtins.input = lambda prompt="": ""
        sim_engine.GUI_SCOREBOARD_QUEUE = self._engine_queue
        sim_engine.SIM_FAST_FORWARD = False
        sim_engine.SIM_JUMP_TARGET = None
        sim_engine.SIM_STICKY_FAST = None
        sim_engine.SIM_PAUSED = False
        sim_engine.SIM_SLEEP_SCALE = 1.0 / self.speed
        sim_engine.set_ruleset(rules if rules in ("NBA", "FIBA") else "NBA")
        if mode not in ("2018 season (82 games)", "2027 play-in & playoffs"):
            players_data.POSTSEASON_PLAY_IN = True
        self.set_status("Running")
        error = None
        try:
            if mode == "Game":
                team_a = self.factories[team_a_name]()
                team_b = self.factories[team_b_name]()
                sim_engine.apply_star_clutchness(team_a, team_b)
                sim_engine.assign_player_badges(team_a)
                sim_engine.assign_player_badges(team_b)
                sim_engine.simulate_game(team_a, team_b)
            elif mode == "Playoff series":
                sim_engine.run_best_of_7_series(self.factories[team_a_name], self.factories[team_b_name])
            elif mode in SEASON_LIKE:
                sim_engine.GUI_SERIES_UPDATE_QUEUE = None
                self.set_status("Season running")
                sink_sections = _Sink(self._on_section)
                if mode in SEASON_MODES:
                    year = SEASON_MODES[mode]
                    result = run_year_season(year, sink_sections, _Sink(self._on_score))
                    self.post = {"standings": (result or {}).get("_season_standings"), "factories": factories_for_year(year), "year": year}
                elif mode == "2027 season (82 games)":
                    result = players_data.run_2027_season(sink_sections, _Sink(self._on_score))
                    self.post = {"standings": (result or {}).get("_season_standings"), "factories": None, "year": 2027}
                else:
                    result = run_2018_season(sink_sections, _Sink(self._on_score))
                    self.post = {"standings": (result or {}).get("_season_standings"), "factories": None, "year": 2018}
                self._on_section(result or {})
                self._on_score({"postseason_ready": True})
            elif mode == "2027 play-in & playoffs":
                sim_engine.GUI_SERIES_UPDATE_QUEUE = _Sink(self._on_section)
                players_data.run_2027_postseason(self.post.get("standings"), self.post.get("factories"))
        except Exception:
            error = traceback.format_exc()
        finally:
            self._push_live(force=True)
            try:
                merged = dict(self.sections or {})
                merged.update(sim_engine.split_gui_series_sections("".join(proxy.full_output)))
                self.sections = merged
            except Exception:
                self.sections = {}
            sys.stdout, builtins.input = original_stdout, original_input
            sim_engine.GUI_SCOREBOARD_QUEUE = original_engine_queue
            sim_engine.SIM_FAST_FORWARD = False
            sim_engine.SIM_JUMP_TARGET = None
            sim_engine.SIM_STICKY_FAST = None
            sim_engine.SIM_PAUSED = False
            sim_engine.set_ruleset(original_ruleset)
            with self.lock:
                self.active = False
            if error:
                print(error, file=original_stdout)
                self.hub.publish({"type": "pbp", "text": "[Simulation stopped with an error: see the console]"}, keep=True)
            self.set_status("Final" if not error else "Stopped (error)")
            self.hub.publish({"type": "finished", "sections": sorted(self.sections)})

    # --------------------------------------------------------- live updates
    def _push_live(self, force: bool = False):   # force: called on an event (score, substitution), not by the timer
        try:
            snap = live_snapshot()
        except Exception:
            return
        if snap is None:
            return
        signature = json.dumps(snap, sort_keys=True, default=str)
        if signature == self._live_signature:
            return
        self._live_signature = signature
        self.last_live = snap
        self.hub.publish({"type": "live", "data": snap})

    def _tick_live(self):
        while True:
            time.sleep(0.25)
            if self.active and not sim_engine.SIM_STICKY_FAST:
                self._push_live()

    def _pump_engine_messages(self):
        while True:
            message = self._engine_queue.get()
            if not isinstance(message, dict):
                continue
            if message.get("lineup_changed"):
                self._push_live(force=True)      # a substitution: the on-court box switches right away
            elif "bracket_state" in message:
                self.bracket = message["bracket_state"]
                self.hub.publish({"type": "bracket"})
            elif "series_status" in message or "game_result" in message or message.get("reset_series_score"):
                self._on_score(message)
