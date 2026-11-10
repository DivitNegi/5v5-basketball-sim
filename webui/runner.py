"""Runs simulations for the browser UI on a background thread and turns the engine's output into events."""
import builtins
import copy
import json
import queue
import sys
import threading
import time
import traceback
from typing import Dict, Optional

import sim_engine
import players_data
from season_2018 import run_2018_season, run_2018_playoffs, factories_2018
from season_year import run_year_season, factories_for_year
from gui_app import GuiOutputProxy, FANTASY_SEASON_MODES   # same play-by-play filter and scoreboard parsing as the Tk app

from .hub import EventHub
from .live import live_snapshot, team_identity

# Modes the browser UI can run today. The rest of the Tk modes are added as their screens are built.
SEASON_MODES = {"2021 season (82 games)": 2021, "2022 season (82 games)": 2022, "2023 season (82 games)": 2023, "2026 season (82 games)": 2026}
SEASON_LIKE = tuple(SEASON_MODES) + ("2027 season (82 games)", "2018 season (82 games)")
SUPPORTED_MODES = (
    "Game", "Game 7", "1-on-1", "Playoff series", "Custom 16-team playoffs",
    "Full 2027 playoffs", "Full 2018 playoffs", "Custom season (82 games)",
    "Fantasy draft: 2027 players (season + playoffs)",
    "Fantasy draft: all-time (season + playoffs)", "Fantasy draft playoffs",
    "Olympic tournament",
) + SEASON_LIKE + ("2027 play-in & playoffs", "Replay season game")
ALL_MODES = (
    "Game", "Game 7", "1-on-1", "Playoff series", "Custom 16-team playoffs", "Full 2027 playoffs", "2027 season (82 games)",
    "2018 season (82 games)", "2021 season (82 games)", "2022 season (82 games)", "2023 season (82 games)", "2026 season (82 games)",
    "Full 2018 playoffs", "Custom season (82 games)", "Fantasy draft: 2027 players (season + playoffs)",
    "Fantasy draft: all-time (season + playoffs)", "Fantasy draft playoffs", "Olympic tournament",
)
JUMP_TARGETS = {"game": None, "end1": "end1", "half": "half", "end3": "end3", "last5": "last5", "last2": "last2"}


def rating_summary(p) -> Dict:
    """A player's ratings on the 0-100 scale the Tk draft board shows, for the draft pool, the roster panels and the trade lists."""
    def g(k):
        return round(float(getattr(p, k, 0) or 0) * 100)
    return {
        "name": p.name, "pos": p.position, "ovr": sim_engine.fantasy_ovr(p), "ht": getattr(p, "height", 0), "arch": getattr(p, "archetype", ""),
        "badges": list(getattr(p, "badges", ()) or ()), "team": getattr(p, "source_team", ""),
        "r": {"3PT": g("three_rating"), "MID": g("mid_rating"), "RIM": g("rim_rating"), "DUNK": g("dunk_rating"), "FT": g("ft_rating"),
              "PLAY": g("playmaking"), "HANDLE": g("ball_handle"), "PERIM D": g("perimeter_def"), "INT D": g("interior_def"),
              "STL": g("steal"), "BLK": g("block"), "OREB": g("oreb"), "DREB": g("dreb"), "USAGE": g("usage")},
    }


FF_LINE_PAUSE = 0.0015   # seconds per play-by-play line while a "sim to" jump is running


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
                    # a tiny pause per play, so the page receives and draws every play and score instead of one lump at the end:
                    # a little slower than Sim Series, and it follows the speed buttons (higher speed = shorter pause)
                    # (the engine turns time.sleep into a no-op while fast-forwarding, so use the real one; and a Windows sleep is ~15 ms
                    #  at best, so the small per-line pauses are added up and slept in one go)
                    # paced by the clock, not by counting sleeps: a Windows sleep can run long or short depending on the timer resolution,
                    # so each line is given a time slot and the sleep only covers what is still owed (an overshoot is simply caught up)
                    now = time.perf_counter()
                    slot = FF_LINE_PAUSE * max(0.05, min(2.0, float(getattr(sim_engine, "SIM_SLEEP_SCALE", 1.0) or 1.0)))
                    due = max(getattr(self, "_pace_due", now), now - 0.05) + slot
                    self._pace_due = due
                    if due - now > 0.010:
                        sim_engine._REAL_SLEEP(due - now)
            return
        if sim_engine.SIM_STICKY_FAST == "series":   # Sim All Playoffs stays fully quiet, as before
            self._write_quick(text)
            return
        super().write(text)

    def _write_quick(self, text):
        """Sim Series: no play-by-play, but the scoreboard still ticks along (at most ~16 times a second)."""
        self.full_output.append(text)
        self.buffer += text
        pending = None
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            clean = line.strip()
            self._maybe_series_record(clean)
            m = self.scoreboard_pattern.match(clean)
            if m:
                pending = m.groups()
        now = time.perf_counter()
        if pending is not None and now - getattr(self, "_last_quick_score", 0.0) >= 0.06:
            period, clock, team_a, score_a, team_b, score_b = pending
            self._last_quick_score = now
            self.scoreboard_queue.put({"period": period, "clock": clock, "team_a": team_a, "score_a": score_a, "team_b": team_b, "score_b": score_b})
        if now - self._last_yield > 0.12:   # hand the interpreter to the web thread now and then, like the Tk proxy does
            sim_engine._REAL_SLEEP(0.03)
            self._last_yield = time.perf_counter()


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
        self.options: Dict = {}
        self.draft_prompt: Dict = {}
        self.trade_prompt: Dict = {}
        self.shots: list = []          # this game's shot events, so a page opened mid-game can rebuild its shot map
        self._shot_count = 0
        self._pending_shot = None
        self._draft_choice = None
        self._draft_event = threading.Event()
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
    def start(self, mode: str, team_a: str, team_b: str, rules: str = "NBA", options: Optional[Dict] = None) -> Optional[str]:
        if mode == "Next":
            mode = "2027 play-in & playoffs"
            if not self.season.get("ready"):
                return "Finish a season first."
        if mode not in SUPPORTED_MODES:
            return f"{mode} is not in the browser UI yet. Use the Tk app for it for now."
        options = dict(options or {})
        needs_teams = mode in ("Game", "Game 7", "Playoff series")
        if needs_teams and (team_a not in self.factories or team_b not in self.factories):
            return "Pick two teams from the list."
        if needs_teams and team_a == team_b:
            return "Pick two different teams."
        selected = [n for n in options.get("teams", []) if n in self.factories]
        if mode == "Custom 16-team playoffs" and len(selected) != 16:
            return "Choose exactly 16 teams for the custom playoffs."
        if mode == "Custom season (82 games)" and len(selected) != 30:
            return "Choose exactly 30 teams for the custom season."
        if mode == "1-on-1" and not all(options.get(k) for k in ("teamA", "playerA", "teamB", "playerB")):
            return "Choose both players for 1-on-1."
        if mode == "Replay season game" and not sim_engine.season_replay_available(options.get("order")):
            return "That season game is not available for replay."
        with self.lock:
            if self.active:
                return "A simulation is already running."
            self.active = True
        self.mode = mode
        self.options = options
        keep = mode in ("2027 play-in & playoffs", "Replay season game")   # a replay must leave the finished season as it was
        self.score, self.series, self.flow, self.last_live = None, None, [], None
        self.shots, self._shot_count, self._pending_shot = [], 0, None
        if not keep:
            self.sections = {}
            self.season = {"progress": None, "races": None, "standings": None, "ready": False}
            self.bracket = {}
            self.post = {"standings": None, "factories": None, "year": None}
        self._live_signature = None
        self.hub.clear_backlog()
        self.hub.publish({"type": "reset", "mode": mode, "teams": [team_identity(team_a), team_identity(team_b)] if needs_teams else [None, None]})
        threading.Thread(target=self._run, args=(mode, team_a, team_b, rules), daemon=True).start()
        return None

    # ------------------------------------------------------------ trade offers
    def _show_trade_prompt(self, kind: str, info: Dict):
        """The engine paused the season for an AI trade offer (or the deadline) and is waiting: ask the user in the browser."""
        prompt = {"kind": kind, **dict(info)}
        if kind == "offer":
            mine = {p.name: p for p in sim_engine.fantasy_trade_roster(sim_engine.FANTASY_TRADE_STATE["user_team"])}
            prompt["send"] = [sim_engine.fantasy_trade_describe(mine[n]) for n in info.get("user_gives", []) if n in mine]
            prompt["receive"] = list(info.get("detail", []))
        self.trade_prompt = prompt
        sim_engine.SIM_PAUSED = True
        self.set_status("Trade offer: the season is paused until you answer." if kind == "offer" else "Trade deadline: the season is paused for your last trades.")
        self.hub.publish({"type": "trade_prompt", "data": prompt})

    def _clear_trade_prompt(self, resume: bool):
        self.trade_prompt = {}
        sim_engine.FANTASY_TRADE_STATE["offer"] = None
        if resume:
            sim_engine.SIM_PAUSED = False
            self.set_status("Running")
        self.hub.publish({"type": "trade_prompt", "data": {}})

    def trade_respond(self, action: str) -> Dict:
        prompt = self.trade_prompt
        if not prompt:
            return {"ok": False, "error": "There is no trade waiting for an answer."}
        if prompt["kind"] == "deadline":
            if action == "resume":
                self._clear_trade_prompt(True)
                return {"ok": True}
            return {"ok": False, "error": "Resume the season when you are done trading."}
        if action == "reject":
            self._clear_trade_prompt(True)
            return {"ok": True}
        if action == "negotiate":
            preset = {"team": prompt["ai_team"], "give": prompt["user_gives"], "get": prompt["ai_gives"]}
            self._clear_trade_prompt(False)           # the season stays paused: press Resume when the negotiating is done
            self.set_status("Paused: negotiating a trade. Press Resume when you are done.")
            return {"ok": True, "preset": preset}
        if action == "accept":
            check = sim_engine.evaluate_fantasy_trade(prompt["ai_team"], prompt["user_gives"], prompt["ai_gives"], allow_counter=False)
            if check["decision"] != "accept":
                self._clear_trade_prompt(True)
                return {"ok": False, "error": "That offer is no longer available (the rosters have changed). The season resumed."}
            outcome = sim_engine.fantasy_trade_submit(prompt["ai_team"], prompt["user_gives"], prompt["ai_gives"])
            if not outcome.get("ok"):
                return {"ok": False, "error": outcome.get("error") or "The trade could not be completed."}
            self._clear_trade_prompt(True)
            return {"ok": True}
        return {"ok": False, "error": "Unknown trade action."}

    def draft_state(self) -> Dict:
        state = dict(getattr(sim_engine, "FANTASY_DRAFT_STATE", {}) or {})
        rosters = state.pop("rosters", None) or {}
        mine = [rating_summary(pl) for pl in list(rosters.get(state.get("user_team"), []))]
        return {"active": bool(self.draft_prompt), "prompt": self.draft_prompt, "state": state, "roster": mine}

    def draft_choose(self, value) -> Optional[str]:
        if not self.draft_prompt:
            return "The fantasy draft is not waiting for a choice."
        self._draft_choice = value
        self._draft_event.set()
        return None

    def _wait_draft_choice(self, prompt: Dict):
        self.draft_prompt = prompt
        self._draft_choice = None
        self._draft_event.clear()
        self.hub.publish({"type": "draft", "data": self.draft_state()})
        while self.active and not self._draft_event.wait(0.2):
            pass
        value = self._draft_choice
        self.draft_prompt = {}
        self.hub.publish({"type": "draft", "data": self.draft_state()})
        return value

    def _web_fantasy_picker(self, pools, taken_names):
        players = sim_engine.fantasy_available_players(pools, taken_names)
        players.sort(key=sim_engine.fantasy_ovr, reverse=True)
        by_key = {}
        rows = []
        for index, player in enumerate(players):
            key = f"{index}:{getattr(player, 'fantasy_base_name', player.name)}"
            by_key[key] = player
            rows.append({**rating_summary(player), "key": key})
        value = self._wait_draft_choice({"kind": "player", "title": "You are on the clock", "players": rows})
        if value == "__auto__":
            return sim_engine.FANTASY_DRAFT_AUTO
        return by_key.get(str(value))

    def _web_option_picker(self, title, message, options):
        value = self._wait_draft_choice({"kind": "option", "title": title, "message": message, "options": list(options)})
        return value if value in options else (options[0] if options else None)

    def _web_position_picker(self, player):
        choices = ["PG", "SG", "SF", "PF", "C"]
        value = self._wait_draft_choice({"kind": "option", "title": f"Position for {player.name}", "options": choices})
        return value if value in choices else player.position

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
    def _flush_shot(self, made: bool):
        """Publish the shot that was waiting for its result (a make, or a miss at the rebound) as one {"type": "shot"} event."""
        ev = getattr(self, "_pending_shot", None)
        self._pending_shot = None
        if not ev:
            return
        ev = {"type": "shot", **ev, "made": bool(made), "n": self._shot_count}
        self._shot_count += 1
        self.shots.append(ev)
        del self.shots[:-3000]
        self.hub.publish(ev)

    def _track_shot(self, kind: str, info: Dict):
        if getattr(sim_engine, "SILENT_SIM_DEPTH", 0) > 0 or self.mode in SEASON_LIKE:
            return   # a quiet season game is not a live game: no shot map for it
        if kind == "attempt":
            self._flush_shot(False)   # the previous attempt never got a make or a rebound (e.g. a blocked shot): it missed
            player, team = info.get("player"), info.get("team")
            if player is None or team is None:
                self._pending_shot = None
                return
            ctx = sim_engine.SIM_CONTEXT
            self._pending_shot = {"team": team.name, "player": player.name, "zone": str(info.get("shot_type") or "mid"), "period": ctx.get("period"), "clock": ctx.get("period_time")}
        elif kind == "make":
            self._flush_shot(True)
        elif kind == "miss":
            self._flush_shot(False)

    def _on_shot_hook(self, kind: str, **info):
        self._track_shot(kind, info)
        # "make" arrives just before the made shot's result line, so that next line is the make. "miss" arrives when the rebound is
        # about to be resolved, i.e. just after the miss line, so the page marks the last line it received. (An attempt alone says
        # nothing: drives record it before their build-up lines, blocks after the block line.)
        if kind == "make":
            self._shot_state = "make"
        elif kind == "miss":
            self.hub.publish({"type": "shotmark", "result": "miss"}, keep=True)

    def _on_pbp(self, text: str):
        line = text.rstrip("\n")
        event = {"type": "pbp", "text": line}
        state = getattr(self, "_shot_state", None)
        if state and line.strip():
            event["shot"] = state
            self._shot_state = None
        self.hub.publish(event, keep=True)

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
        if "trade_offer" in message:
            self._show_trade_prompt("offer", message["trade_offer"])
            return
        if "trade_deadline" in message:
            self._show_trade_prompt("deadline", message["trade_deadline"])
            return
        if self._on_season_message(message):
            return
        if "period" in message and "clock" in message and "score_a" in message:
            if str(message.get("period", "")).lower() == "1st" and str(message.get("clock")) in ("12:00", "10:00") and str(message.get("score_a")) == "0" and str(message.get("score_b")) == "0" and self.shots:
                self.shots, self._shot_count, self._pending_shot = [], 0, None   # the next game of a series starts a fresh shot map
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
        original_series_queue = sim_engine.GUI_SERIES_UPDATE_QUEUE
        original_fantasy_picker = sim_engine.GUI_FANTASY_PICKER
        original_position_picker = sim_engine.GUI_POSITION_PICKER
        original_option_picker = sim_engine.GUI_OPTION_PICKER
        original_ruleset = sim_engine.CURRENT_RULESET
        proxy = WebOutputProxy(_Sink(self._on_pbp), _Sink(self._on_score), original_stdout)
        sys.stdout = proxy
        builtins.input = lambda prompt="": ""
        sim_engine.GUI_SCOREBOARD_QUEUE = self._engine_queue
        self._shot_state = None
        sim_engine.SHOT_RESULT_HOOK = self._on_shot_hook
        sim_engine.GUI_SERIES_UPDATE_QUEUE = _Sink(self._on_section)
        sim_engine.GUI_FANTASY_PICKER = self._web_fantasy_picker
        sim_engine.GUI_POSITION_PICKER = self._web_position_picker
        sim_engine.GUI_OPTION_PICKER = self._web_option_picker
        sim_engine.SIM_FAST_FORWARD = False
        sim_engine.SIM_JUMP_TARGET = None
        sim_engine.SIM_STICKY_FAST = None
        sim_engine.SIM_PAUSED = False
        sim_engine.SIM_SLEEP_SCALE = 1.0 / self.speed
        sim_engine.set_ruleset(rules if rules in ("NBA", "FIBA") else "NBA")
        if mode not in ("2018 season (82 games)", "2027 play-in & playoffs", "Game"):   # "Game" is a regular-season game
            players_data.POSTSEASON_PLAY_IN = True
        self.set_status("Running")
        error = None
        try:
            if mode in ("Game", "Game 7"):
                # "Game 7" is the playoff-intensity single game; "Game" is a regular-season game: paced star minutes, but a close
                # fourth quarter keeps the starters in (the same rules the season games use)
                previous_cap = sim_engine.SEASON_STAR_MINUTES_CAP
                if mode == "Game":
                    sim_engine.SEASON_STAR_MINUTES_CAP = 34   # set before the teams are built, as in the season
                try:
                    team_a = self.factories[team_a_name]()
                    team_b = self.factories[team_b_name]()
                    sim_engine.apply_star_clutchness(team_a, team_b)
                    sim_engine.assign_player_badges(team_a)
                    sim_engine.assign_player_badges(team_b)
                    sim_engine.simulate_game(team_a, team_b)
                finally:
                    sim_engine.SEASON_STAR_MINUTES_CAP = previous_cap
            elif mode == "Replay season game":
                previous_cap = sim_engine.SEASON_STAR_MINUTES_CAP
                sim_engine.SEASON_STAR_MINUTES_CAP = 34
                try:
                    team_a, team_b = sim_engine.build_season_replay_teams(self.options.get("order"))
                    sim_engine.simulate_game(team_a, team_b)
                finally:
                    sim_engine.SEASON_STAR_MINUTES_CAP = previous_cap
            elif mode == "1-on-1":
                def resolve(team_name, player_name):
                    if team_name not in self.factories:
                        return None
                    return next((copy.deepcopy(p) for p in self.factories[team_name]().roster if p.name == player_name), None)
                player_a = resolve(self.options.get("teamA"), self.options.get("playerA"))
                player_b = resolve(self.options.get("teamB"), self.options.get("playerB"))
                if player_a is None or player_b is None:
                    raise ValueError("Could not find one of the selected 1-on-1 players.")
                sim_engine.assign_player_badges(sim_engine.Team("temp", [player_a]))
                sim_engine.assign_player_badges(sim_engine.Team("temp", [player_b]))
                sim_engine.simulate_1v1_game(player_a, player_b,
                                             int(self.options.get("target", 11)), int(self.options.get("winBy", 2)))
            elif mode == "Playoff series":
                sim_engine.run_best_of_7_series(self.factories[team_a_name], self.factories[team_b_name])
            elif mode == "Custom 16-team playoffs":
                sim_engine.run_custom_16_team_playoffs(self.options.get("teams", []), self.factories)
            elif mode == "Full 2027 playoffs":
                players_data.run_2027_playoffs()
            elif mode == "Full 2018 playoffs":
                run_2018_playoffs()
            elif mode == "Olympic tournament":
                sim_engine.set_ruleset("FIBA")
                sim_engine.run_olympic_tournament(self.factories)
            elif mode == "Fantasy draft playoffs":
                sim_engine.run_fantasy_draft_playoffs()
            elif mode in FANTASY_SEASON_MODES:
                year_prefix = "2027 " if "2027" in mode else None
                names, factories, user_team = sim_engine.run_fantasy_season_draft(year_prefix)
                if names and factories:
                    self.set_status("Fantasy season running")
                    result = sim_engine.run_quiet_82_game_season(names, factories, _Sink(self._on_section), _Sink(self._on_score))
                    self.post = {"standings": (result or {}).get("_season_standings"), "factories": dict(factories), "year": 2027 if year_prefix else None}
                    self._on_section(result or {})
                    self._on_score({"postseason_ready": True})
            elif mode == "Custom season (82 games)":
                selected = self.options.get("teams", [])
                result = sim_engine.run_quiet_82_game_season(selected, self.factories, _Sink(self._on_section), _Sink(self._on_score))
                self.post = {"standings": (result or {}).get("_season_standings"),
                             "factories": {n: self.factories[n] for n in selected}, "year": None}
                self._on_section(result or {})
                self._on_score({"postseason_ready": True})
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
            self._flush_shot(False)   # a last attempt that never got a rebound (the buzzer) was a miss
            self._push_live(force=True)
            try:
                if mode != "Replay season game":   # the replayed game's own tables must not replace the season's
                    merged = dict(self.sections or {})
                    merged.update(sim_engine.split_gui_series_sections("".join(proxy.full_output)))
                    self.sections = merged
            except Exception:
                self.sections = {}
            sys.stdout, builtins.input = original_stdout, original_input
            sim_engine.SHOT_RESULT_HOOK = None
            sim_engine.GUI_SCOREBOARD_QUEUE = original_engine_queue
            sim_engine.GUI_SERIES_UPDATE_QUEUE = original_series_queue
            sim_engine.GUI_FANTASY_PICKER = original_fantasy_picker
            sim_engine.GUI_POSITION_PICKER = original_position_picker
            sim_engine.GUI_OPTION_PICKER = original_option_picker
            sim_engine.SIM_FAST_FORWARD = False
            sim_engine.SIM_JUMP_TARGET = None
            sim_engine.SIM_STICKY_FAST = None
            sim_engine.SIM_PAUSED = False
            sim_engine.set_ruleset(original_ruleset)
            with self.lock:
                self.active = False
            self.draft_prompt = {}
            if error:
                print(error, file=original_stdout)
                self.hub.publish({"type": "pbp", "text": "[Simulation stopped with an error: see the console]"}, keep=True)
            self.set_status("Final" if not error else "Stopped (error)")
            self.hub.publish({"type": "finished", "sections": sorted(self.sections)})

    # --------------------------------------------------------- live updates
    def _push_live(self, force: bool = False):   # force: called on an event (score, substitution), not by the timer
        if self.mode in SEASON_LIKE:
            return   # a regular season is simulated quietly: its games (and the All-Star game) are not a live game to show
        if force and sim_engine.SIM_FAST_FORWARD:
            return   # a jump is running: the 0.25 s timer refreshes the live view, so ~200 forced full snapshots a game would only clog the stream
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
