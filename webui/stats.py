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
    if kind in ("shots", "defense", "matchups"):
        result["columns"] = ["Team", "Player"] + (["Opponent"] if kind == "matchups" else []) + [label for _, label in ZONES] + ["TOTAL"]
    elif kind == "advanced":
        result["columns"] = ["Team", "Player", "MPG", "PER", "TS%", "eFG%", "3PAr", "FTr", "ORB%", "DRB%", "TRB%", "AST%", "STL%", "BLK%", "TOV%", "USG%", "OWS", "DWS", "WS", "WS/48", "OBPM", "DBPM", "BPM", "VORP", "OFF", "DEF", "IMPACT", "+/-", "DOUBLES/G", "ON/48", "OFF/48", "ON-OFF"]
    else:
        result["columns"] = ["Team", "Player", "GP", "MIN", "PTS", "REB", "ORB", "AST", "STL", "BLK", "TOV", "PF", "FG", "FG%", "3PT", "3PT%", "FT", "FT%", "+/-"]
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
                pair = lambda m, a: f"{st[m]/g:.1f}/{st[a]/g:.1f}"
                result["rows"].append([tn, pn, st["games"], round(st["minutes"]/60/g, 1)] + [round(st[k]/g, 1) for k in ("pts", "reb", "oreb", "ast", "stl", "blk", "tov", "pf")] + [pair("fgm", "fga"), pct("fgm", "fga"), pair("tpm", "tpa"), pct("tpm", "tpa"), pair("ftm", "fta"), pct("ftm", "fta"), round(st["plus_minus"]/g, 1)])
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
    if source not in data or not find(source)[0]:
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
        ranks.append({"key": key, "label": label, "value": round(val, 1), "pct": pct})
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
            out.append({"key": key, "label": label, "value": round(val, 3 if abs(val) < 2 else 1), "pct": pct})
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
            zone_ranks.append({"key": f"{key}_{kind}", "label": lbl, "value": round(val, 1), "pct": pct})
    keys = ("minutes", "pts", "reb", "oreb", "dreb", "ast", "stl", "blk", "tov", "pf", "fgm", "fga", "tpm", "tpa", "ftm", "fta", "plus_minus")
    totals = {k: (round(st[k] / 60, 1) if k == "minutes" else round(st[k], 1) if k == "plus_minus" else int(st[k])) for k in keys}
    per_game = {k: round(st[k] / g / (60 if k == "minutes" else 1), 1) for k in keys}
    diet = st.get("shot_diet") or {}
    zone = lambda k: [int(diet.get(k + "_made", 0)), int(diet.get(k, 0))]
    return {"name": name, "team": team, "source": source, "sources": main, "games": int(st["games"]), "totals": totals, "per_game": per_game, "ranks": ranks, "adv_groups": adv_groups, "zone_ranks": zone_ranks, "zone_avg": zone_avg,
            "pool": len(qualified), "group": group, "position": POSITION_GROUPS.get(_positions(runner, team).get(name), ""), "min_gp": min_gp, "shots": {"rim": [a + b for a, b in zip(zone("rim"), zone("dunk"))], "mid": zone("mid"), "three": zone("three"), "post": zone("post")},
            "three_split": {"corner": zone("corner3"), "above_break": zone("atb3"), "deep": zone("deep3"), "wing": zone("wing3"), "top": zone("top3"),
                            "corner_L": zone("corner3_L"), "corner_R": zone("corner3_R"), "wing_L": zone("wing3_L"), "wing_R": zone("wing3_R")},
            "mid_split": {"base": zone("mid_base"), "elbow": zone("mid_elbow"), "wing": zone("mid_wing"),
                          "base_L": zone("mid_base_L"), "base_R": zone("mid_base_R"), "wing_L": zone("mid_wing_L"), "wing_R": zone("mid_wing_R")},
            "fine": fine_me, "fine_avg": fine_avg}
