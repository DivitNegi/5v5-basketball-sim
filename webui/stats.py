"""Browser tables backed by the same totals and advanced formulas as Tkinter."""
from collections import defaultdict
import sim_engine as engine

SOURCES = {
    "Series": ("_series_totals", "_series_team_totals"),
    "Season": ("_season_player_totals", "_season_team_totals"),
    "Playoffs": ("_playoff_player_totals", "_playoff_team_totals"),
}
ZONES = [("three", "3P"), ("corner3", "CORNER 3"), ("wing3", "WING 3"), ("top3", "TOP 3"), ("deep3", "DEEP 3"), ("mid", "MID"), ("mid_base", "BASELINE"), ("mid_elbow", "ELBOW"), ("mid_wing", "WING MID"), ("rim", "RIM"),
         ("post", "POST"), ("dunk", "DUNK"), ("catch_shoot", "C&S"),
         ("iso", "ISO"), ("putback", "PUTBACK"), ("wide_open", "OPEN"), ("contested", "CONTESTED")]

def datasets(sections):
    result = {}
    for label, (pk, tk) in SOURCES.items():
        if sections.get(pk):
            result[label] = (sections[pk], sections.get(tk, {}))
    for game in sections.get("_game_logs", []) or []:
        ps, ts = {}, {}
        for team in game.get("teams", []):
            ps[team["name"]] = {p["name"]: dict(p, games=1) for p in team.get("players", [])}
            ts[team["name"]] = team.get("totals", {})
        result[f"Game {game.get('game_num')}"] = (ps, ts)
    ps, ts = {}, {}
    for team in (engine.SIM_CONTEXT.get("teamA"), engine.SIM_CONTEXT.get("teamB")):
        if team is None:
            continue
        ps[team.name] = {}
        for p in team.roster:
            row = {k: getattr(p, k, 0) for k in ("minutes", "pts", "reb", "ast", "stl", "tov", "pf", "fgm", "fga", "tpm", "tpa", "ftm", "fta", "plus_minus", "assist_pts_created")}
            row.update(games=1, oreb=getattr(p, "oreb_stat", 0), dreb=getattr(p, "dreb_stat", 0), blk=getattr(p, "blk_stat", 0))
            for key in ("shot_diet", "quarter_shot_diet", "defended_diet", "defended_matchup_diet"):
                row[key] = getattr(p, key, {}) or {}
            row["analytics"] = getattr(p, "analytics", {}) or {}
            ps[team.name][p.name] = row
        ts[team.name] = dict(engine.accumulate_team_totals(team), games=1)
    if ps:
        result["Live"] = (ps, ts)
    return result

def on_off(st, tt, other, team_minutes):
    """Team net points per 48 minutes with him on the floor, with him off it, and the difference.

    On-court is his plus-minus over his minutes. Off-court is what the rest of the team's net margin was in the minutes he sat
    (the team's whole season margin minus his on-court margin, over the team minutes he missed)."""
    mins = (st.get("minutes", 0) or 0) / 60.0
    pm = st.get("plus_minus", 0) or 0
    on = 48.0 * pm / mins if mins > 0 else None
    opp_pts = tt.get("opp_pts")
    if opp_pts is None:
        opp_pts = (other or {}).get("pts", 0)
    net_total = (tt.get("pts", 0) or 0) - (opp_pts or 0)
    off_min = team_minutes - mins
    off = 48.0 * (net_total - pm) / off_min if off_min >= 5 else None
    return on, off, (on - off if on is not None and off is not None else None)


# ---- analytics tables, built from the "analytics" counts the engine keeps for every player (see analytics_shot in sim_engine)
PLAY_LABELS = [("iso", "Isolation"), ("pnr", "Pick & roll"), ("dribble", "Off the dribble"), ("post", "Post-up"), ("spot_up", "Spot-up"), ("off_screen", "Off screen"),
               ("cut", "Cut"), ("transition", "Transition"), ("putback", "Putback"), ("other", "Late clock & set plays")]   # what has no play tag: late-clock shots, inbounds, after-timeout sets
PLAY_SHORT = ["ISO", "P&R", "DRIBBLE", "POST", "SPOT", "SCREEN", "CUT", "TRANS", "PUTB", "LATE/SET"]   # column labels, same order as PLAY_LABELS


FINISH_LABELS = [("pullup_three", "Off-the-dribble 3"), ("pullup_mid", "Off-the-dribble midrange"), ("cs_three", "Catch & shoot 3"), ("cs_mid", "Catch & shoot midrange"),
                 ("drive_layup", "Driving layup"), ("drive_floater", "Driving floater"), ("drive_dunk", "Driving dunk"),
                 ("pass_layup", "Layup off a pass"), ("pass_dunk", "Dunk off a pass"),
                 ("post_up", "Post-up / hook"), ("post_fade", "Post fadeaway"), ("putback", "Putback"),
                 # games saved under the first, six-row version (not split by shot); shown only when a player has some
                 ("pullup", "Off the dribble (older games)"), ("catch_shoot", "Catch & shoot (older games)"), ("drive", "Drive (older games)"),
                 ("off_pass", "Finish off a pass (older games)"), ("post", "Post move (older games)")]


PLAY_ALIASES = {"drive": "dribble", "pullup": "dribble"}   # games saved before the merge filed these two separately


def _merged(d, key):
    out = {}
    for k, v in (((d or {}).get("analytics") or {}).get(key) or {}).items():
        k = PLAY_ALIASES.get(k, k) if key == "pt" else k
        o = out.setdefault(k, {})
        for f, n in v.items():
            o[f] = o.get(f, 0) + n
    return out


def play_type_breakdown(mine, pool, key="pt", labels=None):
    """His field goals by play type (or, with key "fin", by how the shot finished) next to the league's points per shot and share on the
    same play (pool = every player's stats in this source)."""
    labels = labels or PLAY_LABELS
    league = {}
    for st in pool:
        for k, v in _merged(st, key).items():
            lg = league.setdefault(k, [0, 0])
            lg[0] += v.get("fga", 0)
            lg[1] += v.get("pts", 0)
    lt = sum(x[0] for x in league.values())
    pt = _merged(mine, key)
    total = sum(v.get("fga", 0) for v in pt.values())
    rows = []
    for k, label in labels:
        v = pt.get(k) or {}
        fga, fgm, pts = v.get("fga", 0), v.get("fgm", 0), v.get("pts", 0)
        lf, lp = league.get(k, [0, 0])
        rows.append({"key": k, "label": label, "fga": fga, "fgm": fgm, "pts": pts,
                     "fgp": round(100 * fgm / fga, 1) if fga else None, "pps": round(pts / fga, 2) if fga else None,
                     "freq": round(100 * fga / total, 1) if total else None, "league_pps": round(lp / lf, 2) if lf else None,
                     "league_freq": round(100 * lf / lt, 1) if lt else None})
    return {"rows": rows, "total": total}


ANALYTICS = {
    "onoff": "Team offense and defense per 100 possessions with him on the floor and on the bench. Possessions are the team's, split by his share of the minutes.",
    "playtypes": "Click a player to see his full play-type breakdown: how often he runs each play, how well, and how that compares with the league.",
    "clutch": "Last five minutes of the 4th quarter or overtime with the score within five. Season totals, not per game: clutch samples are small.",
    "xfg": "Every shot carries the make chance the engine rolled. Expected points add those up; the gap to the points he really scored is shot-making above or below expected.",
    "assists": "Who his assists went to: one row per passer and teammate.",
}


def _poss(t, prefix=""):
    t = t or {}
    return (t.get(prefix + "fga", 0) or 0) + 0.44 * (t.get(prefix + "fta", 0) or 0) - (t.get(prefix + "oreb", 0) or 0) + (t.get(prefix + "tov", 0) or 0)


def analytics_table(kind, players, teams, team_filter, result):
    r1 = lambda v: None if v is None else round(v, 1)
    pct = lambda m, a: round(100 * m / a, 1) if a else None
    result["note"] = ANALYTICS[kind]
    cols = {
        "onoff": ["GP", "MIN", "ON ORtg", "ON DRtg", "ON NET", "OFF ORtg", "OFF DRtg", "OFF NET", "NET SWING", "+/-"],
        "playtypes": [],   # just the players: every number is in his pop-up's Play types tab
        "clutch": ["GP", "MIN", "PTS", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "FT", "FTA", "FT%", "TS%", "AST", "TOV", "+/-"],
        "xfg": ["Shots", "xPTS", "PTS", "PTS vs exp", "per 100 shots", "xeFG%", "eFG%"],
        "assists": ["To", "AST", "Share%"],
    }[kind]
    result["columns"] = ["Team", "Player"] + cols
    # whole-number totals (not per-game averages): shown without a decimal
    result["open_tab"] = "playtypes" if kind == "playtypes" else None   # clicking a player opens his pop-up on this tab
    result["counts"] = {"onoff": [], "playtypes": [], "xfg": ["Shots", "PTS"], "assists": ["AST"],
                        "clutch": ["PTS", "FG", "FGA", "3P", "3PA", "FT", "FTA", "AST", "TOV", "+/-"]}[kind]
    shots = lambda st: sum(v.get("fga", 0) for v in ((st.get("analytics") or {}).get("pt") or {}).values())
    for tn, pp in players.items():
        if team_filter not in ("All teams", tn):
            continue
        if kind == "playtypes":
            pp = dict(sorted(pp.items(), key=lambda kv: -shots(kv[1])))
        tt = teams.get(tn, {}) or {}
        other = next((v for k, v in teams.items() if k != tn), {}) or {}
        team_min = sum((x.get("minutes", 0) or 0) for x in pp.values()) / 60.0
        team_pts = tt.get("pts", 0) or 0
        opp_pts = tt.get("opp_pts", other.get("pts", 0)) or 0
        poss_f = _poss(tt)
        poss_a = _poss(tt, "opp_") if tt.get("opp_fga") else _poss(other)
        for pn, st in pp.items():
            a = st.get("analytics") or {}
            gp = st.get("games", 0) or 0
            add = lambda row: (result["rows"].append([tn, pn] + row), result["gp"].append(gp))
            if kind == "onoff":
                mins = (st.get("minutes", 0) or 0) / 60.0
                if not a or mins <= 0 or team_min <= 0:
                    continue
                share = min(1.0, 5 * mins / team_min)
                on_f, on_a = a.get("on_pf", 0), a.get("on_pa", 0)
                rt = lambda pts, poss: 100 * pts / poss if poss > 1 else None
                on_o, on_d = rt(on_f, poss_f * share), rt(on_a, poss_a * share)
                off_o, off_d = (rt(team_pts - on_f, poss_f * (1 - share)), rt(opp_pts - on_a, poss_a * (1 - share))) if share < 0.97 else (None, None)
                on_n = on_o - on_d if on_o is not None and on_d is not None else None
                off_n = off_o - off_d if off_o is not None and off_d is not None else None
                add([gp, r1(mins / max(1, gp)), r1(on_o), r1(on_d), r1(on_n), r1(off_o), r1(off_d), r1(off_n),
                     r1(on_n - off_n) if on_n is not None and off_n is not None else None, r1((st.get("plus_minus", 0) or 0) / max(1, gp))])
            elif kind == "playtypes":   # one row per player who took a shot; the detail is in his pop-up
                if sum(v.get("fga", 0) for v in (a.get("pt") or {}).values()):
                    add([])
            elif kind == "clutch":
                c = a.get("clutch") or {}
                if not c.get("sec") and not c.get("fga") and not c.get("fta"):
                    continue
                g = lambda k: c.get(k, 0) or 0
                ts_d = 2 * (g("fga") + 0.44 * g("fta"))
                add([gp, r1(g("sec") / 60), g("pts"), g("fgm"), g("fga"), pct(g("fgm"), g("fga")), g("tpm"), g("tpa"), pct(g("tpm"), g("tpa")),
                     g("ftm"), g("fta"), pct(g("ftm"), g("fta")), round(100 * g("pts") / ts_d, 1) if ts_d else None, g("ast"), g("tov"), g("pm")])
            elif kind == "xfg":
                x = a.get("xp") or {}
                n, exp, pts = x.get("n", 0), x.get("exp", 0.0), x.get("pts", 0)
                if n:
                    add([n, r1(exp), pts, r1(pts - exp), r1(100 * (pts - exp) / n), round(50 * exp / n, 1), round(50 * pts / n, 1)])
            elif kind == "assists":
                to = a.get("ast_to") or {}
                total = sum(to.values())
                for mate, cnt in sorted(to.items(), key=lambda kv: -kv[1]):
                    add([mate, cnt, pct(cnt, total)])
    return result


def payload(runner, source="Live", kind="averages", team_filter="All teams", quarter="All"):
    sec = runner.sections or {}
    data = datasets(sec)
    if source not in data:
        source = next(iter(data), "Live")
    players, teams = data.get(source, ({}, {}))
    result = {"sources": list(data), "source": source, "teams": list(players), "columns": [], "rows": [], "gp": []}
    if kind == "reports":
        result["reports"] = {k: v for k, v in sec.items() if isinstance(v, str) and v.strip()}
        return result
    if kind == "awards":
        result["columns"] = ["Award", "Player", "Stat line"]
        rows = list(sec.get("_season_awards") or [])
        pool = [(tn, pn, st) for tn, pp in players.items() for pn, st in pp.items() if st.get("games", 0)]
        if not rows and pool:
            winner = [(t, n, s) for t, n, s in pool if t == sec.get("_winner_name")]
            if winner:
                t, n, s = max(winner, key=lambda x: engine.series_player_score(x[2]))
                g = max(1, s.get("games", 1))
                rows.append(["Series MVP", n, f"{t} · {s.get('pts', 0)/g:.1f} PTS · {s.get('reb', 0)/g:.1f} REB · {s.get('ast', 0)/g:.1f} AST"])
            for title, keys, unit in [("Scoring Leader", ("pts",), "PPG"), ("Playmaking Leader", ("ast",), "APG"), ("Defensive Playmaker", ("stl", "blk"), "STL + BLK/G")]:
                score = lambda x: sum(x[2].get(k, 0) for k in keys) / max(1, x[2].get("games", 1))
                t, n, s = max(pool, key=score)
                rows.append([title, n, f"{t} · {score((t,n,s)):.1f} {unit}"])
        result["rows"] = rows
        return result
    if kind in ANALYTICS:
        return analytics_table(kind, players, teams, team_filter, result)
    if kind in ("shots", "defense", "matchups"):
        result["columns"] = ["Team", "Player"] + (["Opponent"] if kind == "matchups" else []) + [label for _, label in ZONES] + ["TOTAL"]
    elif kind == "advanced":
        result["columns"] = ["Team", "Player", "MPG", "PER", "TS%", "eFG%", "3PAr", "FTr", "ORB%", "DRB%", "TRB%", "AST%", "STL%", "BLK%", "TOV%", "USG%", "OWS", "DWS", "WS", "WS/48", "OBPM", "DBPM", "BPM", "VORP", "OFF", "DEF", "IMPACT", "+/-", "DOUBLES/G", "ON/48", "OFF/48", "ON-OFF"]
    else:
        result["columns"] = ["Team", "Player", "GP", "MIN", "PTS", "REB", "ORB", "AST", "STL", "BLK", "TOV", "PF", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "eFG%", "FT", "FTA", "FT%", "+/-"]
    for tn, pp in players.items():
        if team_filter not in ("All teams", tn):
            continue
        for pn, stats in pp.items():
            st = defaultdict(float, stats)
            g = max(1, st["games"])
            if kind in ("shots", "defense", "matchups"):
                diet = stats.get("defended_diet" if kind != "shots" else "shot_diet", {}) or {}
                if quarter != "All" and kind == "shots":
                    qd = stats.get("quarter_shot_diet", {}) or {}
                    diet = qd.get(quarter, qd.get(int(quarter), {}))
                diets = (stats.get("defended_matchup_diet", {}) or {}).items() if kind == "matchups" else [(None, diet)]
                for opponent, d in diets:
                    def pair(keys):
                        a = sum(d.get(k, 0) for k in keys)
                        m = sum(d.get(k + "_made", 0) for k in keys)
                        return f"{m}/{a} · {100*m/a:.0f}%" if a else "0/0 · —"
                    result["rows"].append([tn, pn] + ([opponent] if kind == "matchups" else []) + [pair([k]) for k, _ in ZONES] + [pair(["three", "mid", "rim", "post", "dunk"])])
                    result["gp"].append(st["games"])
            elif kind == "advanced":
                tt = defaultdict(float, teams.get(tn, {}))
                other = next((v for k, v in teams.items() if k != tn), {})
                opp = defaultdict(float, {k: tt.get("opp_" + k, v) for k, v in other.items()})
                adv = engine.calc_series_advanced(st, tt, opp)
                team_min = sum((x.get("minutes", 0) or 0) for x in players.get(tn, {}).values()) / 60.0
                oo = on_off(st, tt, other, team_min)
                result["rows"].append([tn, pn] + [round(x, 3 if i in (4, 5, 17) else 1) for i, x in enumerate(adv)] + [None if v is None else round(v, 1) for v in oo])
                result["gp"].append(st["games"])
            else:
                pct = lambda m, a: round(100*st[m]/st[a], 1) if st[a] else None
                st["twm"], st["twa"] = st["fgm"] - st["tpm"], st["fga"] - st["tpa"]
                per = lambda k: round(st[k]/g, 1)
                efg = round(100 * (st["fgm"] + 0.5 * st["tpm"]) / st["fga"], 1) if st["fga"] else None
                # shooting laid out like Basketball-Reference: makes, attempts and % each in their own column, twos split out, then eFG%
                result["rows"].append([tn, pn, st["games"], round(st["minutes"]/60/g, 1)] + [per(k) for k in ("pts", "reb", "oreb", "ast", "stl", "blk", "tov", "pf")]
                                      + [per("fgm"), per("fga"), pct("fgm", "fga"), per("tpm"), per("tpa"), pct("tpm", "tpa"), per("twm"), per("twa"), pct("twm", "twa"), efg,
                                         per("ftm"), per("fta"), pct("ftm", "fta"), round(st["plus_minus"]/g, 1)])
                result["gp"].append(st["games"])
    return result


# ---- player pop-up: season totals, per game, and where he ranks against the rest of the league
PCT_METRICS = [   # (key, label, value(per-game stats dict -> number or None), needs)
    ("pts", "Points"), ("ast", "Assists"), ("reb", "Total Rebounds"), ("oreb", "Off. Rebounds"), ("dreb", "Def. Rebounds"),
    ("stl", "Steals"), ("blk", "Blocks"), ("fga", "FG Attempts"), ("fgp", "FG %"), ("tpp", "3-pt FG %"), ("efg", "Effective FG %"), ("ts", "True Shooting %"),
]


def _metrics(st):
    g = max(1, st.get("games", 0) or 1)
    fga, fgm, tpa, tpm, fta, pts = (st.get(k, 0) or 0 for k in ("fga", "fgm", "tpa", "tpm", "fta", "pts"))
    out = {"pts": pts / g, "ast": (st.get("ast", 0) or 0) / g, "reb": (st.get("reb", 0) or 0) / g, "oreb": (st.get("oreb", 0) or 0) / g,
           "dreb": (st.get("dreb", 0) or 0) / g, "stl": (st.get("stl", 0) or 0) / g, "blk": (st.get("blk", 0) or 0) / g, "fga": fga / g}
    out["fgp"] = 100 * fgm / fga if fga else None
    out["tpp"] = 100 * tpm / tpa if tpa else None
    out["efg"] = 100 * (fgm + 0.5 * tpm) / fga if fga else None
    out["ts"] = 100 * pts / (2 * (fga + 0.44 * fta)) if (fga + fta) else None
    return out


_POS_CACHE = {}   # team name -> {player name: position}, built from the team factories


def _positions(runner, team_name):
    if team_name not in _POS_CACHE:
        pos = {}
        try:
            for p in runner.factories[team_name]().roster:
                pos[p.name] = p.position
        except Exception:
            pass
        _POS_CACHE[team_name] = pos
    return _POS_CACHE[team_name]


POSITION_GROUPS = {"PG": "guards", "SG": "guards", "G": "guards", "SF": "forwards", "PF": "forwards", "F": "forwards", "C": "centers"}


DEF_ZONES = [("Rim", ("rim", "dunk")), ("Post", ("post", "post_fade")), ("Midrange", ("mid",)), ("Three", ("three",))]


def _def_zone(diet, keys):
    return sum(int(diet.get(k + "_made", 0) or 0) for k in keys), sum(int(diet.get(k, 0) or 0) for k in keys)


def _def_points(diet):
    made3 = int(diet.get("three_made", 0) or 0)
    made2 = sum(int(diet.get(k + "_made", 0) or 0) for k in ("rim", "dunk", "post", "post_fade", "mid"))
    return 2 * made2 + 3 * made3


def _defense_block(mine, pool, games):
    """Shots he defended (the man he guarded, or the help defender who contested): FG% allowed by zone against the league,
    forced turnovers, and the players he guarded most."""
    dd = mine.get("defended_diet") or {}
    zones, tot_m, tot_a = [], 0, 0
    for label, keys in DEF_ZONES:
        m, a = _def_zone(dd, keys)
        lm = la = 0
        for _, _, s in pool:
            x, y = _def_zone(s.get("defended_diet") or {}, keys)
            lm += x; la += y
        tot_m += m; tot_a += a
        zones.append({"zone": label, "made": m, "att": a, "pct": round(100 * m / a, 1) if a else None,
                      "league": round(100 * lm / la, 1) if la else None, "per_game": round(a / games, 1)})
    lm = la = 0
    for _, _, s in pool:
        d2 = s.get("defended_diet") or {}
        for _, keys in DEF_ZONES:
            x, y = _def_zone(d2, keys); lm += x; la += y
    # where his overall FG% allowed ranks among regular defenders (lower is better; 1 = best)
    rates = []
    for _, _, s in pool:
        d2 = s.get("defended_diet") or {}
        mm = sum(_def_zone(d2, k)[0] for _, k in DEF_ZONES); aa = sum(_def_zone(d2, k)[1] for _, k in DEF_ZONES)
        if aa >= 3 * max(1, s.get("games", 1)):
            rates.append(mm / aa)
    mine_rate = tot_m / tot_a if tot_a else None
    rank = (1 + sum(1 for r in rates if r < mine_rate - 1e-9)) if mine_rate is not None and tot_a >= 3 * games else None
    matchups = []
    for opp, d in (mine.get("defended_matchup_diet") or {}).items():
        m = sum(_def_zone(d, k)[0] for _, k in DEF_ZONES); a = sum(_def_zone(d, k)[1] for _, k in DEF_ZONES)
        if a:
            matchups.append({"name": opp, "made": m, "att": a, "pct": round(100 * m / a, 1), "pts": _def_points(d),
                             "tov": int(d.get("turnover", 0) or 0)})
    matchups.sort(key=lambda r: -r["att"])
    return {"made": tot_m, "att": tot_a, "pct": round(100 * mine_rate, 1) if mine_rate is not None else None,
            "league": round(100 * lm / la, 1) if la else None, "per_game": round(tot_a / games, 1),
            "pts_allowed": round(_def_points(dd) / games, 1), "forced_tov": int(dd.get("turnover", 0) or 0),
            "forced_tov_pg": round((dd.get("turnover", 0) or 0) / games, 1), "rank": rank, "of": len(rates),
            "zones": zones, "matchups": matchups[:10]}


def player_detail(runner, source, team, name, group="all"):
    sec = runner.sections or {}
    data = datasets(sec)

    def find(src):   # (team, stats) for this player in one source, his own team first
        pp = data.get(src, ({}, {}))[0]
        if team and name in (pp.get(team) or {}):
            return team, pp[team][name]
        hits = [(tn, st) for tn, roster in pp.items() for pn, st in roster.items() if pn == name]
        return max(hits, key=lambda x: x[1].get("games", 0) or 0) if hits else (None, None)

    main = [src for src in ("Season", "Playoffs", "Series", "Live") if src in data and find(src)[0]]
    # A team was named (he was clicked in that team's box score or table): only offer the sources that really hold THAT team's stats for him,
    # so 2018 Tatum never turns into the 82-game 2024 Tatum just because the bigger sample wins the by-name search. When no source has that
    # exact team (or no team was named), keep the by-name lookup.
    exact = [src for src in main if team and name in (data[src][0].get(team) or {})]
    if exact:
        main = exact
    if source not in data or source not in main:
        source = main[0] if main else next(iter(data), "Live")
    team, _found = find(source)
    if team is None:
        return {"error": "No stats for that player yet."}
    players, teams_tot = data.get(source, ({}, {}))
    mine = players[team][name]
    pool = [(tn, pn, defaultdict(float, st)) for tn, pp in players.items() for pn, st in pp.items() if (st.get("games", 0) or 0) > 0]
    max_gp = max((s["games"] for _, _, s in pool), default=1)
    min_gp = max(1, round(0.2 * max_gp)) if max_gp > 1 else 1
    qualified = [(tn, pn, s) for tn, pn, s in pool if s["games"] >= min_gp]
    if group in ("guards", "forwards", "centers"):   # rank him only against his own position group
        qualified = [(tn, pn, s) for tn, pn, s in qualified if POSITION_GROUPS.get(_positions(runner, tn).get(pn)) == group]
    st = defaultdict(float, mine)
    g = max(1, st["games"])
    metrics = _metrics(st)
    ranks = []
    for key, label in PCT_METRICS:
        val = metrics.get(key)
        if val is None:
            ranks.append({"key": key, "label": label, "value": None, "pct": None})
            continue
        pop = []
        for _, _, s in qualified:
            if key in ("fgp", "efg") and s["fga"] / s["games"] < 3:
                continue   # a shooting % needs real volume
            if key == "tpp" and s["tpa"] / s["games"] < 1:
                continue
            v = _metrics(s).get(key)
            if v is not None:
                pop.append(v)
        below = sum(1 for v in pop if v < val - 1e-9)
        equal = sum(1 for v in pop if abs(v - val) <= 1e-9)
        pct = round(100 * (below + 0.5 * equal) / len(pop)) if pop else None
        rank = 1 + sum(1 for v in pop if v > val + 1e-9)   # his real place (1 = best), so only one player is ever the leader
        ranks.append({"key": key, "label": label, "value": round(val, 1), "pct": pct, "rank": rank, "of": len(pop) if pop else None})
    # advanced radar: the same formulas as the Advanced table, ranked against the same qualified players
    ADV_NAMES = ["MPG", "PER", "TS%", "eFG%", "3PAr", "FTr", "ORB%", "DRB%", "TRB%", "AST%", "STL%", "BLK%", "TOV%", "USG%", "OWS", "DWS", "WS", "WS/48", "OBPM", "DBPM", "BPM", "VORP", "OFF", "DEF", "IMPACT", "+/-", "DOUBLES/G"]
    def adv_row(tn, stats):
        try:
            tt = defaultdict(float, teams_tot.get(tn, {}))
            other = next((v for k, v in teams_tot.items() if k != tn), {})
            opp = defaultdict(float, {k: tt.get("opp_" + k, v) for k, v in other.items()})
            vals = engine.calc_series_advanced(defaultdict(float, stats), tt, opp)
            row = {n: v for n, v in zip(ADV_NAMES, vals)}
            team_min = sum((x.get("minutes", 0) or 0) for x in players.get(tn, {}).values()) / 60.0
            row["ON/48"], row["OFF/48"], row["ON-OFF"] = on_off(stats, tt, other, team_min)
            return row
        except Exception:
            return None
    my_adv = adv_row(team, mine)
    adv_pool = [r for r in (adv_row(tn, s) for tn, _, s in qualified) if r]
    # the advanced stats, grouped by what they describe; each group is its own radar
    ADV_GROUPS = [
        ("Overall impact", "How much he helps his team win: PER, win shares, box plus-minus, VORP and the overall impact rating.",
         [("PER", "PER", False), ("WS", "Win Shares", False), ("WS/48", "Win Shares / 48", False), ("BPM", "Box +/-", False), ("VORP", "VORP", False), ("IMPACT", "Impact", False), ("ON-OFF", "On/off (net per 48)", False)]),
        ("Scoring & efficiency", "How he scores and how efficiently: shooting efficiency, how often he shoots threes and gets to the line, his usage and his offensive value.",
         [("TS%", "True Shooting %", False), ("eFG%", "Effective FG %", False), ("FTr", "Free Throw Rate", False), ("3PAr", "3-pt Attempt Rate", False), ("USG%", "Usage %", False),
          ("OWS", "Off. Win Shares", False), ("OBPM", "Off. Box +/-", False), ("OFF", "Offense rating", False)]),
        ("Defense, rebounding & playmaking", "What he does without scoring: defensive value, rebounding, steals, blocks, passing and ball security (turnover % is flipped so higher is better).",
         [("DWS", "Def. Win Shares", False), ("DBPM", "Def. Box +/-", False), ("DEF", "Defense rating", False), ("ORB%", "Off. Rebound %", False), ("DRB%", "Def. Rebound %", False),
          ("TRB%", "Rebound %", False), ("STL%", "Steal %", False), ("BLK%", "Block %", False), ("AST%", "Assist %", False), ("TOV%", "Ball security (TOV%)", True)]),
    ]
    def rank_adv(picks):
        out = []
        for key, label, lower in picks:
            val = my_adv.get(key) if my_adv else None
            if val is None or not adv_pool:
                out.append({"key": key, "label": label, "value": None, "pct": None}); continue
            pop = [r[key] for r in adv_pool if r.get(key) is not None]
            below = sum(1 for v in pop if v < val - 1e-9)
            equal = sum(1 for v in pop if abs(v - val) <= 1e-9)
            pct = round(100 * (below + 0.5 * equal) / len(pop)) if pop else None
            if pct is not None and lower:
                pct = 100 - pct
            rank = 1 + sum(1 for v in pop if (v < val - 1e-9 if lower else v > val + 1e-9))
            out.append({"key": key, "label": label, "value": round(val, 3 if abs(val) < 2 else 1), "pct": pct, "rank": rank, "of": len(pop) if pop else None})
        return out
    adv_groups = [{"title": t, "desc": d, "ranks": rank_adv(pk)} for t, d, pk in ADV_GROUPS]
    # shot-zone radar: for each zone, how well he shoots it (FG%) and how much he shoots it (attempts a game), against players who use that zone
    def zone_of(stats):
        diet = stats.get("shot_diet") or {}
        z = lambda k: (int(diet.get(k + "_made", 0)), int(diet.get(k, 0)))
        rim, dunk = z("rim"), z("dunk")
        return {"rim": (rim[0] + dunk[0], rim[1] + dunk[1]), "mid": z("mid"), "three": z("three"), "post": z("post")}
    my_zone, pool_zone = zone_of(mine), [(zone_of(s), max(1, s.get("games", 1) or 1)) for _, _, s in qualified]
    # the twelve-zone map: restricted area, paint, elbow, mid wings, baseline, corner / wing / top threes (left and right sides share a value)
    FINE = [("ra", ("rim", "dunk")), ("paint", ("post",)), ("elbow", ("mid_elbow",)), ("mid_wing", ("mid_wing",)), ("baseline", ("mid_base",)),
            ("corner3", ("corner3",)), ("wing3", ("wing3",)), ("top3", ("top3",))]
    def fine_of(stats):
        diet = stats.get("shot_diet") or {}
        return {k: (sum(int(diet.get(x + "_made", 0)) for x in keys), sum(int(diet.get(x, 0)) for x in keys)) for k, keys in FINE}
    fine_me = {k: list(v) for k, v in fine_of(mine).items()}
    pool_fine = [fine_of(s) for _, _, s in qualified]
    fine_avg = {}
    for k, _ in FINE:
        mm, aa = sum(f[k][0] for f in pool_fine), sum(f[k][1] for f in pool_fine)
        fine_avg[k] = {"pct": round(100 * mm / aa, 2) if aa else None, "att": aa}
    zone_avg = {}
    for zk in ("rim", "mid", "three", "post"):
        mm, aa = sum(zz[zk][0] for zz, _ in pool_zone), sum(zz[zk][1] for zz, _ in pool_zone)
        zone_avg[zk] = {"pct": round(100 * mm / aa, 2) if aa else None, "made": mm, "att": aa}
    zone_ranks = []
    for key, label, floor in (("rim", "Rim", 0.5), ("mid", "Midrange", 0.4), ("three", "3-pt", 0.5), ("post", "Post", 0.2)):
        made, att = my_zone[key]
        for kind in ("fgp", "att"):
            lbl = f"{label} FG%" if kind == "fgp" else f"{label} shots / game"
            val = (100 * made / att if att else None) if kind == "fgp" else att / g
            if val is None or (kind == "fgp" and att / g < floor):
                zone_ranks.append({"key": f"{key}_{kind}", "label": lbl, "value": None if val is None else round(val, 1), "pct": 0 if val is not None else None}); continue
            pop = []
            for zz, gg in pool_zone:
                m2, a2 = zz[key]
                if kind == "fgp":
                    if a2 / gg >= floor:
                        pop.append(100 * m2 / a2)
                else:
                    pop.append(a2 / gg)
            below = sum(1 for v in pop if v < val - 1e-9)
            equal = sum(1 for v in pop if abs(v - val) <= 1e-9)
            pct = round(100 * (below + 0.5 * equal) / len(pop)) if pop else None
            rank = 1 + sum(1 for v in pop if v > val + 1e-9)
            zone_ranks.append({"key": f"{key}_{kind}", "label": lbl, "value": round(val, 1), "pct": pct, "rank": rank, "of": len(pop) if pop else None})
    keys = ("minutes", "pts", "reb", "oreb", "dreb", "ast", "stl", "blk", "tov", "pf", "fgm", "fga", "tpm", "tpa", "ftm", "fta", "plus_minus")
    totals = {k: (round(st[k] / 60, 1) if k == "minutes" else round(st[k], 1) if k == "plus_minus" else int(st[k])) for k in keys}
    per_game = {k: round(st[k] / g / (60 if k == "minutes" else 1), 1) for k in keys}
    diet = st.get("shot_diet") or {}
    zone = lambda k: [int(diet.get(k + "_made", 0)), int(diet.get(k, 0))]
    defense = _defense_block(mine, pool, g)
    return {"defense": defense, "name": name, "team": team, "source": source, "sources": main, "games": int(st["games"]), "totals": totals, "per_game": per_game, "ranks": ranks, "adv_groups": adv_groups, "zone_ranks": zone_ranks, "zone_avg": zone_avg,
            "pool": len(qualified), "group": group, "position": POSITION_GROUPS.get(_positions(runner, team).get(name), ""), "min_gp": min_gp, "shots": {"rim": [a + b for a, b in zip(zone("rim"), zone("dunk"))], "mid": zone("mid"), "three": zone("three"), "post": zone("post")},
            "three_split": {"corner": zone("corner3"), "above_break": zone("atb3"), "deep": zone("deep3"), "wing": zone("wing3"), "top": zone("top3"), "heave": zone("heave3"), "heatcheck": zone("heatcheck3"), "logo": zone("logo3"),
                            "corner_L": zone("corner3_L"), "corner_R": zone("corner3_R"), "wing_L": zone("wing3_L"), "wing_R": zone("wing3_R")},
            "mid_split": {"base": zone("mid_base"), "elbow": zone("mid_elbow"), "wing": zone("mid_wing"),
                          "base_L": zone("mid_base_L"), "base_R": zone("mid_base_R"), "wing_L": zone("mid_wing_L"), "wing_R": zone("mid_wing_R")},
            "dist_split": {"rim_float": zone("rim_float"), "mid_long": zone("mid_long")},
            "fine": fine_me, "fine_avg": fine_avg,
            "play_types": play_type_breakdown(mine, [s for _, _, s in pool]),
            "finish_types": play_type_breakdown(mine, [s for _, _, s in pool], "fin", FINISH_LABELS)}



# ---- team pop-up: the team's whole shot chart and zone numbers (all its players' shots added up) and advanced team radars,
# each ranked against every other team in the same set of games (season / playoffs / series / this game)
TEAM_ADV_GROUPS = [   # (title, description, [(key, label, lower_is_better)])
    ("Overall", "How good the team is overall: net rating, point margin, win rate, pace, and its offense and defense ratings.",
     [("net", "Net rating", False), ("diff", "Point margin", False), ("winp", "Win %", False), ("pace", "Pace", False), ("ortg", "Off. rating", False), ("drtg", "Def. rating", True)]),
    ("Offense", "How the team scores: efficiency, shot profile, ball movement, ball security and offensive rebounding.",
     [("ortg", "Off. rating", False), ("efg", "Effective FG %", False), ("ts", "True Shooting %", False), ("tpar", "3-pt Attempt Rate", False),
      ("ftr", "Free Throw Rate", False), ("astr", "Assisted FG %", False), ("tovp", "Turnover %", True), ("orbp", "Off. Rebound %", False)]),
    ("Defense", "How the team defends: points allowed per possession, opponent shooting, turnovers forced, rebounding, steals and blocks.",
     [("drtg", "Def. rating", True), ("opp_efg", "Opp. effective FG %", True), ("opp_tpp", "Opp. 3-pt %", True), ("forced", "Opp. turnover %", False),
      ("drbp", "Def. Rebound %", False), ("stl", "Steals / game", False), ("blk", "Blocks / game", False), ("opp_ftr", "Opp. FT rate", True)]),
]


def _team_metrics(t):
    t = defaultdict(float, t or {})
    g = max(1, t["games"] or 1)
    poss = t["fga"] + 0.44 * t["fta"] - t["oreb"] + t["tov"]
    opp_poss = t["opp_fga"] + 0.44 * t["opp_fta"] - t["opp_oreb"] + t["opp_tov"]

    def div(a, b, k=100.0):
        return k * a / b if b else None
    m = {
        "ortg": div(t["pts"], poss), "drtg": div(t["opp_pts"], opp_poss) if t["opp_fga"] else None,
        "diff": (t["pts"] - t["opp_pts"]) / g if t["opp_pts"] else None,
        "winp": div(t["wins"], g) if "wins" in t else None,
        "pace": (0.5 * (poss + opp_poss) / g) if opp_poss else poss / g,
        "efg": div(t["fgm"] + 0.5 * t["tpm"], t["fga"]), "ts": div(t["pts"], 2 * (t["fga"] + 0.44 * t["fta"])),
        "tpar": div(t["tpa"], t["fga"]), "ftr": div(t["fta"], t["fga"]), "astr": div(t["ast"], t["fgm"]),
        "tovp": div(t["tov"], t["fga"] + 0.44 * t["fta"] + t["tov"]),
        "orbp": div(t["oreb"], t["oreb"] + t["opp_dreb"]) if t["opp_dreb"] else None,
        "drbp": div(t["dreb"], t["dreb"] + t["opp_oreb"]) if (t["dreb"] + t["opp_oreb"]) else None,
        "opp_efg": div(t["opp_fgm"] + 0.5 * t["opp_tpm"], t["opp_fga"]), "opp_tpp": div(t["opp_tpm"], t["opp_tpa"]),
        "forced": div(t["opp_tov"], t["opp_fga"] + 0.44 * t["opp_fta"] + t["opp_tov"]) if t["opp_fga"] else None,
        "stl": t["stl"] / g, "blk": t["blk"] / g, "opp_ftr": div(t["opp_fta"], t["opp_fga"]),
    }
    m["net"] = m["ortg"] - m["drtg"] if m["ortg"] is not None and m["drtg"] is not None else None
    return m


def team_detail(runner, team):
    sec = runner.sections or {}
    data = datasets(sec)
    source = next((s for s in ("Season", "Playoffs", "Series", "Live") if team in (data.get(s, ({}, {}))[0])), None)
    if source is None:
        return None
    players, teams_tot = data[source]

    def merged(roster):   # every player's shot diet added up
        out = defaultdict(int)
        for st in (roster or {}).values():
            for k, v in (st.get("shot_diet") or {}).items():
                if isinstance(v, (int, float)):
                    out[k] += int(v)
        return out
    diets = {tn: merged(pp) for tn, pp in players.items()}
    games = {tn: max(1, int((teams_tot.get(tn) or {}).get("games", 0) or max((s.get("games", 0) or 0 for s in pp.values()), default=1))) for tn, pp in players.items()}
    diet, g = diets[team], games[team]

    def zone(d, k):
        return [int(d.get(k + "_made", 0)), int(d.get(k, 0))]

    def zones_of(d):
        return {"rim": [a + b for a, b in zip(zone(d, "rim"), zone(d, "dunk"))], "mid": zone(d, "mid"), "three": zone(d, "three"), "post": zone(d, "post")}
    FINE = [("ra", ("rim", "dunk")), ("paint", ("post",)), ("elbow", ("mid_elbow",)), ("mid_wing", ("mid_wing",)), ("baseline", ("mid_base",)),
            ("corner3", ("corner3",)), ("wing3", ("wing3",)), ("top3", ("top3",))]

    def fine_of(d):
        return {k: [sum(int(d.get(x + "_made", 0)) for x in ks), sum(int(d.get(x, 0)) for x in ks)] for k, ks in FINE}
    all_z = {tn: zones_of(d) for tn, d in diets.items()}
    all_f = {tn: fine_of(d) for tn, d in diets.items()}
    zone_avg = {}
    for zk in ("rim", "mid", "three", "post"):
        mm, aa = sum(z[zk][0] for z in all_z.values()), sum(z[zk][1] for z in all_z.values())
        zone_avg[zk] = {"pct": round(100 * mm / aa, 2) if aa else None, "made": mm, "att": aa}
    fine_avg = {}
    for k, _ in FINE:
        mm, aa = sum(f[k][0] for f in all_f.values()), sum(f[k][1] for f in all_f.values())
        fine_avg[k] = {"pct": round(100 * mm / aa, 2) if aa else None, "att": aa}

    def rank_of(val, pop, lower):
        """rank 1 = best; the spoke always runs from worst (0) to best (100), so for lower-is-better stats a low number is a long spoke"""
        better = sum(1 for v in pop if (v < val - 1e-9 if lower else v > val + 1e-9))
        below = sum(1 for v in pop if v < val - 1e-9)
        equal = sum(1 for v in pop if abs(v - val) <= 1e-9)
        above = len(pop) - below - equal
        return 1 + better, (round(100 * ((above if lower else below) + 0.5 * equal) / len(pop)) if pop else None)

    zone_ranks = []
    for key, label in (("rim", "Rim"), ("mid", "Midrange"), ("three", "3-pt"), ("post", "Post")):
        for kind in ("fgp", "att"):
            def val_of(tn):
                m, a = all_z[tn][key]
                return (100 * m / a if a else None) if kind == "fgp" else a / games[tn]
            val = val_of(team)
            lbl = f"{label} FG%" if kind == "fgp" else f"{label} shots / game"
            pop = [v for v in (val_of(tn) for tn in all_z) if v is not None]
            if val is None:
                zone_ranks.append({"key": f"{key}_{kind}", "label": lbl, "value": None, "pct": None})
                continue
            rk, pct = rank_of(val, pop, False)
            zone_ranks.append({"key": f"{key}_{kind}", "label": lbl, "value": round(val, 1), "pct": pct, "rank": rk, "of": len(pop)})

    mets = {tn: _team_metrics(dict(teams_tot.get(tn) or {}, games=games[tn])) for tn in players}
    adv_groups = []
    for title, desc, picks in TEAM_ADV_GROUPS:
        ranks = []
        for key, label, lower in picks:
            val = mets[team].get(key)
            pop = [m[key] for m in mets.values() if m.get(key) is not None]
            if val is None or not pop:
                ranks.append({"key": key, "label": label, "value": None, "pct": None})
                continue
            rk, pct = rank_of(val, pop, lower)
            ranks.append({"key": key, "label": label, "value": round(val, 1), "pct": pct, "rank": rk, "of": len(pop)})
        adv_groups.append({"title": title, "desc": desc, "ranks": ranks})
    return {"source": source, "games": g, "pool": len(players), "shots": zones_of(diet), "zone_avg": zone_avg, "zone_ranks": zone_ranks,
            "three_split": {"corner": zone(diet, "corner3"), "above_break": zone(diet, "atb3"), "deep": zone(diet, "deep3"), "wing": zone(diet, "wing3"), "top": zone(diet, "top3"), "heave": zone(diet, "heave3"), "heatcheck": zone(diet, "heatcheck3"), "logo": zone(diet, "logo3"),
                            "corner_L": zone(diet, "corner3_L"), "corner_R": zone(diet, "corner3_R"), "wing_L": zone(diet, "wing3_L"), "wing_R": zone(diet, "wing3_R")},
            "mid_split": {"base": zone(diet, "mid_base"), "elbow": zone(diet, "mid_elbow"), "wing": zone(diet, "mid_wing"),
                          "base_L": zone(diet, "mid_base_L"), "base_R": zone(diet, "mid_base_R"), "wing_L": zone(diet, "mid_wing_L"), "wing_R": zone(diet, "mid_wing_R")},
            "dist_split": {"rim_float": zone(diet, "rim_float"), "mid_long": zone(diet, "mid_long")},
            "fine": fine_of(diet), "fine_avg": fine_avg, "adv_groups": adv_groups}


# ---- the player pop-up's Offense / Defense tabs: passing links and matchups split by region (paint, post, mid, three)
REGIONS = (("paint", ("rim", "dunk")), ("post", ("post", "post_fade")), ("mid", ("mid",)), ("three", ("three",)))


def _regions_of(diet):
    diet = diet or {}
    out = {}
    for r, keys in REGIONS:
        out[r] = [sum(int(diet.get(k + "_made", 0) or 0) for k in keys), sum(int(diet.get(k, 0) or 0) for k in keys)]
    out["all"] = [sum(v[0] for v in out.values()), sum(v[1] for v in out.values())]
    return out


def player_links(runner, source, team, name):
    sec = runner.sections or {}
    data = datasets(sec)
    if source not in data:
        source = next(iter(data), "Live")
    players = data.get(source, ({}, {}))[0]
    if team not in players or name not in players[team]:
        hits = [tn for tn, pp in players.items() if name in pp]
        if not hits:
            return {"error": "No stats for that player yet."}
        team = hits[0]
    mine = players[team][name]
    a = mine.get("analytics") or {}
    games = max(1, mine.get("games", 1) or 1)
    mates = [pn for pn in players[team] if pn != name]
    # passing: by region where recorded (games played after region tracking began); the overall counts also cover older games
    ast_to = {m: {"all": int(c)} for m, c in (a.get("ast_to") or {}).items()}
    for m, regs in (a.get("ast_to_r") or {}).items():
        ast_to.setdefault(m, {"all": 0}).update({r: int(v) for r, v in regs.items()})
    ast_by = {}
    for m in mates:   # overall from each teammate's own assist log
        c = ((players[team][m].get("analytics") or {}).get("ast_to") or {}).get(name)
        if c:
            ast_by[m] = {"all": int(c)}
    for m, regs in (a.get("ast_by_r") or {}).items():
        ast_by.setdefault(m, {"all": sum(regs.values())}).update({r: int(v) for r, v in regs.items()})
    # his own shots by region and how many of his makes came off a pass
    shots = _regions_of(mine.get("shot_diet"))
    assisted_made = {r: sum(int(v.get(r, 0) or 0) for v in (a.get("ast_by_r") or {}).values()) for r, _ in REGIONS}
    # league on the same rows: every player in these games
    lg = {r: [0, 0, 0] for r, _ in REGIONS}   # made, attempts, assisted makes
    for tn, pp in players.items():
        for pn, stx in pp.items():
            rr = _regions_of(stx.get("shot_diet"))
            ab = (stx.get("analytics") or {}).get("ast_by_r") or {}
            for r, _ in REGIONS:
                lg[r][0] += rr[r][0]; lg[r][1] += rr[r][1]
                lg[r][2] += sum(int(v.get(r, 0) or 0) for v in ab.values())
    lg_att = sum(v[1] for v in lg.values())
    lg_tracked = any(v[2] for v in lg.values())
    region_rows = []
    for r, _ in REGIONS:
        m, att = shots[r]
        pts = m * (3 if r == "three" else 2)
        region_rows.append({"region": r, "made": m, "att": att, "pct": round(100 * m / att, 1) if att else None, "per_game": round(att / games, 1),
                            "share": round(100 * att / shots["all"][1], 1) if shots["all"][1] else None, "pts_per_shot": round(pts / att, 2) if att else None,
                            "assisted": assisted_made[r], "assisted_pct": round(100 * assisted_made[r] / m, 1) if m and (a.get("ast_by_r")) else None,
                            "lg_pct": round(100 * lg[r][0] / lg[r][1], 1) if lg[r][1] else None,
                            "lg_share": round(100 * lg[r][1] / lg_att, 1) if lg_att else None,
                            "lg_pts_per_shot": round(lg[r][0] * (3 if r == "three" else 2) / lg[r][1], 2) if lg[r][1] else None,
                            "lg_assisted_pct": round(100 * lg[r][2] / lg[r][0], 1) if lg[r][0] and lg_tracked else None})
    # who guarded him: every opponent's matchup log entry for him
    guarded_by = {}
    for tn, pp in players.items():
        if tn == team:
            continue
        for pn, st in pp.items():
            d = (st.get("defended_matchup_diet") or {}).get(name)
            if d:
                regs = _regions_of(d)
                if regs["all"][1]:
                    guarded_by[pn] = dict(regs, team=tn)
    # who he guarded
    guarded = {}
    for opp, d in (mine.get("defended_matchup_diet") or {}).items():
        regs = _regions_of(d)
        if regs["all"][1]:
            guarded[opp] = regs
    # the same matchups grouped by position: which positions guarded him, and which positions he guarded
    def pos_of(team_name, player_name):
        st_ = (players.get(team_name) or {}).get(player_name) or {}
        return (st_.get("position") or _positions(runner, team_name).get(player_name) or "?").upper()[:2]
    owner = {}   # opponent name -> his team (first team that has him, other than ours)
    for tn, pp in players.items():
        if tn != team:
            for pn in pp:
                owner.setdefault(pn, tn)

    def by_position(entries, team_of):
        out = {}
        for nm, regs in entries.items():
            pos = pos_of(team_of(nm), nm)
            slot = out.setdefault(pos, {r: [0, 0] for r in ("all", "paint", "post", "mid", "three")})
            for r in slot:
                slot[r][0] += regs[r][0]; slot[r][1] += regs[r][1]
        order = {"PG": 0, "SG": 1, "SF": 2, "PF": 3, "C": 4}
        return dict(sorted(out.items(), key=lambda kv: order.get(kv[0], 9)))

    # league on the same rows: every matchup in these games, by the defender's position and by the shooter's position
    lg_def_pos, lg_shooter_pos = {}, {}
    owner_any = {}
    for tn, pp in players.items():
        for pn in pp:
            owner_any.setdefault(pn, tn)
    for tn, pp in players.items():
        for pn, stx in pp.items():
            dpos = pos_of(tn, pn)
            for opp, d in (stx.get("defended_matchup_diet") or {}).items():
                regs = _regions_of(d)
                spos = pos_of(owner_any.get(opp, ""), opp)
                for bucket, key in ((lg_def_pos, dpos), (lg_shooter_pos, spos)):
                    slot = bucket.setdefault(key, {r: [0, 0] for r in ("all", "paint", "post", "mid", "three")})
                    for r in slot:
                        slot[r][0] += regs[r][0]; slot[r][1] += regs[r][1]
    guarded_by_pos = by_position(guarded_by, lambda nm: guarded_by[nm].get("team", owner.get(nm, "")))
    guarded_pos = by_position(guarded, lambda nm: owner.get(nm, ""))
    return {"name": name, "team": team, "source": source, "games": games, "mates": mates, "regions_tracked": bool(a.get("ast_to_r") or a.get("ast_by_r")),
            "ast_to": ast_to, "ast_by": ast_by, "shot_regions": region_rows, "guarded_by": guarded_by, "guarded": guarded,
            "guarded_by_pos": guarded_by_pos, "guarded_pos": guarded_pos, "lg_def_pos": lg_def_pos, "lg_shooter_pos": lg_shooter_pos,
            "extras": player_extras(players, team, name)}


# ---- the extra analytics on the Offense / Defense tabs (games played since this tracking began; older games simply have none)
def _sum_maps(players, key2):
    out = {}
    for tn, pp in players.items():
        for pn, st in pp.items():
            merge_counts(out, ((st.get("analytics") or {}).get(key2) or {}))
    return out


def merge_counts(dst, src):
    for k, v in (src or {}).items():
        if isinstance(v, dict):
            merge_counts(dst.setdefault(k, {}), v)
        elif isinstance(v, (int, float)):
            dst[k] = dst.get(k, 0) + v


def player_extras(players, team, name):
    mine = players[team][name]
    a = mine.get("analytics") or {}
    games = max(1, mine.get("games", 1) or 1)
    lg_sq, lg_xp, lg_help = _sum_maps(players, "sq_r"), _sum_maps(players, "xp_r"), _sum_maps(players, "help_def")
    # matchup possessions: shots defended + turnovers forced by the players he guarded
    def poss_line(dd):
        made3 = int(dd.get("three_made", 0) or 0)
        made2 = sum(int(dd.get(k + "_made", 0) or 0) for k in ("rim", "dunk", "post", "post_fade", "mid"))
        att = sum(int(dd.get(k, 0) or 0) for k in ("rim", "dunk", "post", "post_fade", "mid", "three"))
        tov = int(dd.get("turnover", 0) or 0)
        return 2 * made2 + 3 * made3, att + tov, tov
    pts, poss, tov = poss_line(mine.get("defended_diet") or {})
    lp = lpo = 0
    for tn, pp in players.items():
        for pn, st in pp.items():
            x, y, _ = poss_line(st.get("defended_diet") or {})
            lp += x; lpo += y
    tot_pts = mine.get("pts", 0) or 0
    return {
        "sq_r": a.get("sq_r") or {}, "lg_sq_r": lg_sq,
        "xp_r": a.get("xp_r") or {}, "lg_xp_r": lg_xp,
        "creation": {"pts": tot_pts, "ast": mine.get("ast", 0) or 0, "ast_pts": a.get("ast_pts", 0) or 0, "games": games},
        "clutch": a.get("clutch") or {}, "overall": {k: mine.get(k, 0) or 0 for k in ("minutes", "pts", "fgm", "fga", "tpm", "tpa", "ftm", "fta", "ast", "tov", "plus_minus")},
        "tov_kind": a.get("tov_kind") or {}, "stolen_by": a.get("stolen_by") or {}, "blocked_by": a.get("blocked_by") or {},
        "fd_r": a.get("fd_r") or {}, "and1_r": a.get("and1_r") or {}, "fouled_by": a.get("fouled_by") or {},
        "help_def": a.get("help_def") or {}, "lg_help_def": lg_help,
        "stl_on": a.get("stl_on") or {}, "blk_on": a.get("blk_on") or {}, "blk_r": a.get("blk_r") or {}, "fouls_on": a.get("fouls_on") or {},
        "matchup_poss": {"pts": pts, "poss": poss, "tov": tov, "ppp": round(pts / poss, 2) if poss else None, "lg_ppp": round(lp / lpo, 2) if lpo else None},
    }



# ---- the player pop-up's Splits tab: game splits, opponents, streaks, milestones, the season trend, quarters, shot clock, rebounding
MONTHS = ((6, "Oct"), (21, "Nov"), (36, "Dec"), (51, "Jan"), (63, "Feb"), (78, "Mar"), (999, "Apr"))


def player_splits(runner, source, team, name):
    sec = runner.sections or {}
    data = datasets(sec)
    if source not in data:
        source = next(iter(data), "Live")
    players = data.get(source, ({}, {}))[0]
    if team not in players or name not in players[team]:
        hits = [tn for tn, pp in players.items() if name in pp]
        team = hits[0] if hits else team
    st = (players.get(team) or {}).get(name) or {}
    a = st.get("analytics") or {}
    rows = sec.get("_season_game_log") or []
    fields = sec.get("_season_game_log_fields") or ()
    idx = {f: i for i, f in enumerate(fields)}
    games = []
    if rows and "player" in idx:
        for r in rows:
            if r[idx["player"]] == name and (not team or r[idx["team"]] == team) and (r[idx["min"]] or 0) > 0:
                res = str(r[idx["result"]])
                games.append({"game": r[idx["game"]], "opp": r[idx["opp"]], "home": bool(r[idx["home"]]), "win": res.startswith("W"),
                              **{k: r[idx[k]] for k in ("min", "pts", "reb", "ast", "stl", "blk", "tov", "fgm", "fga", "tpm", "tpa", "ftm", "fta", "pm") if k in idx}})
    games.sort(key=lambda g: g["game"])

    def line(gs):
        n = len(gs)
        if not n:
            return None
        s = lambda k: sum(g.get(k, 0) or 0 for g in gs)
        return {"gp": n, "min": round(s("min") / n, 1), "pts": round(s("pts") / n, 1), "reb": round(s("reb") / n, 1), "ast": round(s("ast") / n, 1),
                "stl": round(s("stl") / n, 1), "blk": round(s("blk") / n, 1), "tov": round(s("tov") / n, 1),
                "fg": round(100 * s("fgm") / s("fga"), 1) if s("fga") else None, "tp": round(100 * s("tpm") / s("tpa"), 1) if s("tpa") else None,
                "ft": round(100 * s("ftm") / s("fta"), 1) if s("fta") else None, "pm": round(s("pm") / n, 1)}

    def month_of(n):
        return next(m for cut, m in MONTHS if n <= cut)
    splits = [[lab, l] for lab, l in (("Home", line([g for g in games if g["home"]])), ("Away", line([g for g in games if not g["home"]])),
                                       ("Wins", line([g for g in games if g["win"]])), ("Losses", line([g for g in games if not g["win"]]))) if l]
    months = []
    for _, m in MONTHS:
        l = line([g for g in games if month_of(g["game"]) == m])
        if l:
            months.append([m, l])
    opps = {}
    for g in games:
        opps.setdefault(g["opp"], []).append(g)
    opp_rows = sorted(([o, line(gs)] for o, gs in opps.items()), key=lambda r: -r[1]["gp"])

    def longest(cond):
        best = cur = 0
        for g in games:
            cur = cur + 1 if cond(g) else 0
            best = max(best, cur)
        return best

    def dd(g):
        return sum(1 for k in ("pts", "reb", "ast", "stl", "blk") if (g.get(k) or 0) >= 10)
    streaks = [["20+ points", longest(lambda g: g["pts"] >= 20)], ["30+ points", longest(lambda g: g["pts"] >= 30)],
               ["Double-doubles", longest(lambda g: dd(g) >= 2)], ["3+ threes", longest(lambda g: (g.get("tpm") or 0) >= 3)],
               ["50%+ shooting (8+ shots)", longest(lambda g: (g.get("fga") or 0) >= 8 and g["fgm"] / g["fga"] >= 0.5)],
               ["Team wins", longest(lambda g: g["win"])]]
    milestones = [["30-point games", sum(1 for g in games if g["pts"] >= 30)], ["40-point games", sum(1 for g in games if g["pts"] >= 40)],
                  ["50-point games", sum(1 for g in games if g["pts"] >= 50)], ["Double-doubles", sum(1 for g in games if dd(g) >= 2)],
                  ["Triple-doubles", sum(1 for g in games if dd(g) >= 3)], ["10-assist games", sum(1 for g in games if g["ast"] >= 10)],
                  ["15-rebound games", sum(1 for g in games if g["reb"] >= 15)], ["5+ three games", sum(1 for g in games if (g.get("tpm") or 0) >= 5)]]
    trend = [{"game": g["game"], "pts": g["pts"], "reb": g["reb"], "ast": g["ast"], "min": round(g["min"], 1), "fgm": g["fgm"], "fga": g["fga"]} for g in games]
    q = st.get("quarter_stats") or {}
    quarters = []
    for k in ("1", "2", "3", "4", "5"):
        x = q.get(k) or q.get(int(k)) or {}
        n = x.get("games", 0) or 0
        if n:
            quarters.append(["OT" if k == "5" else "Q" + k, {"gp": n, "min": round((x.get("minutes", 0) or 0) / 60 / n, 1), "pts": round((x.get("pts", 0) or 0) / n, 1),
                             "fg": round(100 * x.get("fgm", 0) / x["fga"], 1) if x.get("fga") else None, "fga": round((x.get("fga", 0) or 0) / n, 1),
                             "reb": round((x.get("reb", 0) or 0) / n, 1), "ast": round((x.get("ast", 0) or 0) / n, 1)}])
    order = {"early": 0, "middle": 1, "late": 2, "transition / other": 3}
    clock = sorted(([k, v] for k, v in (a.get("clock") or {}).items()), key=lambda kv: order.get(kv[0], 9))
    reb = {"contested": a.get("reb_contested", 0) or 0, "uncontested": a.get("reb_uncontested", 0) or 0, "over": a.get("reb_over") or {}}
    return {"name": name, "team": team, "has_log": bool(games), "splits": splits, "months": months, "opponents": opp_rows, "streaks": streaks,
            "milestones": milestones, "trend": trend, "quarters": quarters, "clock": clock, "rebounding": reb}


def player_names(runner, source):
    data = datasets(runner.sections or {})
    if source not in data:
        source = next(iter(data), "Live")
    players = data.get(source, ({}, {}))[0]
    return {"names": sorted(({"name": pn, "team": tn} for tn, pp in players.items() for pn in pp), key=lambda r: r["name"])}
