"""The Tk Shots tab: shot diet, defense diet and matchup defense, with Tk's filters, rankings and leaderboard minimums."""
import sim_engine as engine
from .stats import datasets

SHOT_RANK_KEYS = {
    "3P": ("three",), "3P OPEN": ("three_open",), "3P CONT": ("three_contested",),
    "MID": ("mid",), "MID OPEN": ("mid_open",), "MID CONT": ("mid_contested",),
    "RIM": ("rim",), "RIM OPEN": ("rim_open",), "RIM CONT": ("rim_contested",),
    "POST": ("post",), "DUNK": ("dunk",), "C&S": ("catch_shoot",), "ISO": ("iso",), "PUTB": ("putback",),
    "OPEN": ("wide_open",), "CONT": ("contested",), "TOTAL": ("three", "mid", "rim", "post", "dunk"),
}
SHOT_COLS = [("3P", "three"), ("3P OPEN", "three_open"), ("3P CONT", "three_contested"), ("MID", "mid"), ("MID OPEN", "mid_open"), ("MID CONT", "mid_contested"),
             ("RIM", "rim"), ("RIM OPEN", "rim_open"), ("RIM CONT", "rim_contested"), ("POST", "post"), ("DUNK", "dunk"), ("C&S", "catch_shoot"),
             ("ISO", "iso"), ("PUTB", "putback"), ("OPEN", "wide_open"), ("CONT", "contested")]
DEF_COLS = [("3P", "three"), ("MID", "mid"), ("RIM", "rim"), ("POST", "post"), ("DUNK", "dunk"), ("C&S", "catch_shoot"), ("ISO", "iso"),
            ("PUTB", "putback"), ("OPEN", "wide_open"), ("CONT", "contested")]
TOTAL_KEYS = ("three", "mid", "rim", "post", "dunk")
MODES = ("Shot Diet", "Defense Diet", "Matchup Defense")


def _pair(d, key):
    return engine.format_diet_pair_compact(d, key)


def _total(d):
    made = sum(d.get(k + "_made", 0) for k in TOTAL_KEYS)
    att = sum(d.get(k, 0) for k in TOTAL_KEYS)
    return f"{made}/{att} {engine.safe_pct(made, att):.0f}%"


def _num(text):
    try:
        return float(str(text).strip())
    except ValueError:
        return None


def payload(runner, q):
    sec = runner.sections or {}
    data = datasets(sec)
    sources = [k for k in data if not k.startswith("Game ")]
    games = ["All Games"] + [k for k in data if k.startswith("Game ")]
    mode = q.get("mode", MODES[0]) if q.get("mode") in MODES else MODES[0]
    game = q.get("game", "All Games")
    if game != "All Games" and game in data:
        key = game
    else:
        game = "All Games"
        want = q.get("source", "Season")
        key = want if want in data else next((k for k in ("Season", "Playoffs", "Series", "Live") if k in data), None)
    out = {"modes": list(MODES), "sources": sources, "source": key, "games": games, "game": game, "teams": [], "defenders": [], "guarded": [], "rankKeys": list(SHOT_RANK_KEYS),
           "mode": mode, "columns": [], "rows": [], "note": ""}
    if key is None:
        return out
    players = data[key][0]
    quarter = q.get("quarter", "All Quarters")
    qkey = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4, "OT": 5}.get(quarter)
    out["teams"] = sorted(players)
    team = q.get("team", "All Teams")
    team = team if team in players else "All Teams"
    picked = {team: players[team]} if team != "All Teams" else players

    def diet_of(stats):
        if qkey is not None and mode == "Shot Diet":
            qd = stats.get("quarter_shot_diet", {}) or {}
            return dict(qd.get(qkey) or qd.get(str(qkey)) or {})
        return stats.get("shot_diet", {}) or {}

    defenders, guarded = [], []
    for tn, pp in picked.items():
        for pn, st in pp.items():
            md = st.get("defended_matchup_diet", {}) or {}
            if md:
                defenders.append(pn)
            for g in md:
                if g not in guarded:
                    guarded.append(g)
    out["defenders"], out["guarded"] = sorted(set(defenders)), sorted(guarded)

    rank = q.get("rank", "Team order")
    rank_active = rank in SHOT_RANK_KEYS and mode != "Matchup Defense"
    rank_stat = q.get("rankStat", "Made")
    as_pct = rank_stat == "Percentage"
    defense = mode == "Defense Diet"

    def value_of(d):
        keys = SHOT_RANK_KEYS[rank]
        att = sum(d.get(k, 0) for k in keys)
        made = sum(d.get(k + "_made", 0) for k in keys)
        if as_pct:
            return 100.0 * made / att if att else 0.0
        return att if rank_stat == "Attempted" else made

    def qualifies(d, team_games):
        if not as_pct:
            return True
        keys = SHOT_RANK_KEYS[rank]
        att = sum(d.get(k, 0) for k in keys)
        made = sum(d.get(k + "_made", 0) for k in keys)
        typed = _num(q.get("minDef" if defense else "minAtt", ""))
        if typed is not None and typed >= 0:
            return att >= typed
        scale = min(1.0, max(1, team_games) / 82)
        if defense:
            need = 200 * scale if rank == "3P" else 500 * scale if rank == "TOTAL" else max(5.0, 100 * scale)
            return att >= need
        if rank == "3P":
            return made >= 82 * scale
        if rank == "TOTAL":
            return made >= 300 * scale
        return att >= max(5.0, 100 * scale)

    rows = out["rows"]
    if mode == "Shot Diet":
        out["columns"] = ["Team", "Player"] + [c for c, _ in SHOT_COLS] + ["SQ", "TOTAL"]
        cells = lambda d: [_pair(d, k) for _, k in SHOT_COLS] + [engine.format_shot_quality_avg(d), _total(d)]
        if rank_active:
            ranked = []
            for tn, pp in picked.items():
                tg = max((s.get("games", 0) for s in pp.values()), default=0)
                for pn, st in pp.items():
                    d = diet_of(st)
                    if qualifies(d, tg):
                        ranked.append((value_of(d), tn, pn, d))
            ranked.sort(key=lambda it: it[0], reverse=True)
            for i, (_v, tn, pn, d) in enumerate(ranked, 1):
                rows.append({"kind": "row", "cells": [tn, f"{i}. {pn}"] + cells(d)})
        else:
            for tn, pp in picked.items():
                tot = {}
                for st in pp.values():
                    for k, v in diet_of(st).items():
                        tot[k] = tot.get(k, 0) + v
                rows.append({"kind": "team", "cells": [tn, "TEAM TOTAL"] + cells(tot)})
                for pn, st in sorted(pp.items(), key=lambda it: it[1].get("minutes", 0), reverse=True):
                    rows.append({"kind": "row", "cells": [tn, pn] + cells(diet_of(st))})
        if not rows:
            out["note"] = "Shot diet will start at 0/0 when a game begins."
    elif mode == "Defense Diet":
        out["columns"] = ["Team", "Player"] + ["OPP " + c for c, _ in DEF_COLS] + ["TOV", "TOTAL"]
        cells = lambda d: [_pair(d, k) for _, k in DEF_COLS] + [d.get("turnover", 0), _total(d)]
        if rank_active:
            ranked = []
            for tn, pp in picked.items():
                tg = max((s.get("games", 0) for s in pp.values()), default=0)
                for pn, st in pp.items():
                    d = st.get("defended_diet", {}) or {}
                    if qualifies(d, tg):
                        ranked.append((value_of(d), tn, pn, d))
            # lower allowed % is better on defense; counts still rank high to low
            ranked.sort(key=lambda it: it[0], reverse=not as_pct)
            for i, (_v, tn, pn, d) in enumerate(ranked, 1):
                rows.append({"kind": "row", "cells": [tn, f"{i}. {pn}"] + cells(d)})
        else:
            for tn, pp in picked.items():
                rows.append({"kind": "team", "cells": [tn, "DEFENDED SHOTS"] + [""] * (len(out["columns"]) - 2)})
                for pn, st in sorted(pp.items(), key=lambda it: it[1].get("minutes", 0), reverse=True):
                    rows.append({"kind": "row", "cells": [tn, pn] + cells(st.get("defended_diet", {}) or {})})
        if not rows:
            out["note"] = "Defense tracking will start at 0/0 when a game begins."
    else:
        out["columns"] = ["Team", "Defender", "Guarded"] + [c for c, _ in DEF_COLS] + ["TOV", "TOTAL"]
        sel_def, sel_guard = q.get("defender", "All Defenders"), q.get("guarded", "All Guarded")
        for tn, pp in picked.items():
            header = False
            for pn, st in sorted(pp.items(), key=lambda it: it[1].get("minutes", 0), reverse=True):
                for gname, d in (st.get("defended_matchup_diet", {}) or {}).items():
                    if sel_def != "All Defenders" and pn != sel_def:
                        continue
                    if sel_guard != "All Guarded" and gname != sel_guard:
                        continue
                    if not header:
                        rows.append({"kind": "team", "cells": [tn, "MATCHUP DEFENSE"] + [""] * (len(out["columns"]) - 2)})
                        header = True
                    d = d or {}
                    rows.append({"kind": "row", "cells": [tn, pn, gname] + [_pair(d, k) for _, k in DEF_COLS] + [d.get("turnover", 0), _total(d)]})
        if not rows:
            out["note"] = "No defender-vs-player shots for this filter yet."
    return out
