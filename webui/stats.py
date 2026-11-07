"""Browser tables backed by the same totals and advanced formulas as Tkinter."""
from collections import defaultdict
import sim_engine as engine

SOURCES = {
    "Series": ("_series_totals", "_series_team_totals"),
    "Season": ("_season_player_totals", "_season_team_totals"),
    "Playoffs": ("_playoff_player_totals", "_playoff_team_totals"),
}
ZONES = [("three", "3P"), ("mid", "MID"), ("rim", "RIM"),
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

def payload(runner, source="Live", kind="averages", team_filter="All teams", quarter="All"):
    sec = runner.sections or {}
    data = datasets(sec)
    if source not in data:
        source = next(iter(data), "Live")
    players, teams = data.get(source, ({}, {}))
    result = {"sources": list(data), "source": source, "teams": list(players), "columns": [], "rows": []}
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
        result["columns"] = ["Team", "Player", "MPG", "PER", "TS%", "eFG%", "3PAr", "FTr", "ORB%", "DRB%", "TRB%", "AST%", "STL%", "BLK%", "TOV%", "USG%", "OWS", "DWS", "WS", "WS/48", "OBPM", "DBPM", "BPM", "VORP", "OFF", "DEF", "IMPACT", "+/-", "DOUBLES/G"]
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
            elif kind == "advanced":
                tt = defaultdict(float, teams.get(tn, {}))
                other = next((v for k, v in teams.items() if k != tn), {})
                opp = defaultdict(float, {k: tt.get("opp_" + k, v) for k, v in other.items()})
                adv = engine.calc_series_advanced(st, tt, opp)
                result["rows"].append([tn, pn] + [round(x, 3 if i in (4, 5, 17) else 1) for i, x in enumerate(adv)])
            else:
                pct = lambda m, a: round(100*st[m]/st[a], 1) if st[a] else None
                pair = lambda m, a: f"{st[m]/g:.1f}/{st[a]/g:.1f}"
                result["rows"].append([tn, pn, st["games"], round(st["minutes"]/60/g, 1)] + [round(st[k]/g, 1) for k in ("pts", "reb", "oreb", "ast", "stl", "blk", "tov", "pf")] + [pair("fgm", "fga"), pct("fgm", "fga"), pair("tpm", "tpa"), pct("tpm", "tpa"), pair("ftm", "fta"), pct("ftm", "fta"), round(st["plus_minus"]/g, 1)])
    return result
