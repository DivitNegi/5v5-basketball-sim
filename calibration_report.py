"""
Calibration report: simulate regular-season games and compare the league's
shooting, pace, rebounding and shot-type efficiency with real NBA benchmarks.

    python calibration_report.py            # 2027 teams, 4 games each (120 teams-games x 2)
    python calibration_report.py 8          # 8 games per team
    python calibration_report.py 4 2016     # use another year's teams

Prints one row per metric: simulated value, real benchmark range, and a flag.
"""
import collections
import random
import sys

import players_data as pd
import sim_engine as se

# (label, real_low, real_high, fmt)
BENCHMARKS = {
    "PPG per team": (112.0, 117.0, "{:.1f}"),
    "FGA per team": (87.0, 92.0, "{:.1f}"),
    "FG%": (46.0, 48.5, "{:.1f}"),
    "3P%": (35.5, 37.5, "{:.1f}"),
    "3PA share of FGA": (38.0, 43.0, "{:.1f}"),
    "eFG%": (53.5, 55.5, "{:.1f}"),
    "TS%": (57.0, 59.0, "{:.1f}"),
    "FT%": (77.0, 79.5, "{:.1f}"),
    "FTA per FGA": (0.22, 0.27, "{:.2f}"),
    "Pace (poss / 48)": (97.0, 101.0, "{:.1f}"),
    "ORB%": (24.0, 28.0, "{:.1f}"),
    "Assists per team": (24.0, 28.0, "{:.1f}"),
    "Turnovers per team": (12.0, 15.0, "{:.1f}"),
    "Layup FG%": (58.0, 62.0, "{:.1f}"),
    "Open layup FG%": (70.0, 76.0, "{:.1f}"),
    "Contested layup FG%": (50.0, 56.0, "{:.1f}"),
    "Dunk FG%": (88.0, 93.0, "{:.1f}"),
    "Mid-range FG%": (40.0, 43.0, "{:.1f}"),
    "Mid-range share of FGA": (14.0, 22.0, "{:.1f}"),
    "Three FG% (open)": (37.0, 41.0, "{:.1f}"),
    "Three FG% (contested)": (29.0, 33.0, "{:.1f}"),
    "Post-up FG%": (43.0, 48.0, "{:.1f}"),
    "Fastbreak FG%": (62.0, 68.0, "{:.1f}"),
}


def flag(value, low, high):
    if value < low:
        return "LOW"
    if value > high:
        return "HIGH"
    return "ok"


def main():
    games_per_team = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    year = sys.argv[2] if len(sys.argv) > 2 else "2027"
    se.SEASON_STAR_MINUTES_CAP = 34  # regular-season mode
    factories = [
        fn for name, fn in sorted(vars(pd).items())
        if name.startswith("make_") and name.endswith(f"_{year}") and callable(fn)
    ]
    if len(factories) < 4:
        print(f"Not enough {year} teams found.")
        return
    random.seed(20271)

    totals = collections.Counter()
    diet = collections.Counter()
    team_totals = {}
    games = 0
    for i, factory in enumerate(factories):
        for g in range(games_per_team):
            opp = factories[(i + 5 + g * 3) % len(factories)]
            a, b = se.simulate_silent_season_game(factory, opp)
            games += 1
            se.add_team_to_series_totals(team_totals, a)
            se.add_team_to_series_totals(team_totals, b)
            for t in (a, b):
                totals["pts"] += t.score
                for p in t.roster:
                    for k in ("fga", "fgm", "tpa", "tpm", "fta", "ftm", "ast", "tov"):
                        totals[k] += getattr(p, k)
                    for k, v in (p.shot_diet or {}).items():
                        if isinstance(v, (int, float)):
                            diet[k] += v
    team_games = games * 2

    def pct(m, a):
        return 100.0 * m / a if a else 0.0

    oreb = sum(t["oreb"] for t in team_totals.values())
    opp_dreb = sum(t.get("opp_dreb", 0) for t in team_totals.values())
    poss = sum(t["fga"] - t["oreb"] + t["tov"] + 0.44 * t["fta"] for t in team_totals.values())
    opp_poss = sum(t.get("opp_fga", 0) - t.get("opp_oreb", 0) + t.get("opp_tov", 0) + 0.44 * t.get("opp_fta", 0) for t in team_totals.values())

    def att(kind):  # attempts / makes for a shot type from the diet counters
        return diet[kind], diet[kind + "_made"]

    fga = totals["fga"]
    r_att, r_made = att("rim")
    d_att, d_made = att("dunk")
    m_att, m_made = att("mid")
    p_att, p_made = att("post")
    results = {
        "PPG per team": totals["pts"] / team_games,
        "FGA per team": fga / team_games,
        "FG%": pct(totals["fgm"], fga),
        "3P%": pct(totals["tpm"], totals["tpa"]),
        "3PA share of FGA": pct(totals["tpa"], fga),
        "eFG%": pct(totals["fgm"] + 0.5 * totals["tpm"], fga),
        "TS%": pct(totals["pts"], 2 * (fga + 0.44 * totals["fta"])),
        "FT%": pct(totals["ftm"], totals["fta"]),
        "FTA per FGA": totals["fta"] / max(1, fga),
        "Pace (poss / 48)": ((poss + opp_poss) / 2) / team_games,
        "ORB%": pct(oreb, oreb + opp_dreb),
        "Assists per team": totals["ast"] / team_games,
        "Turnovers per team": totals["tov"] / team_games,
        "Layup FG%": pct(r_made, r_att),
        "Open layup FG%": pct(diet["rim_open_made"], diet["rim_open"]),
        "Contested layup FG%": pct(diet["rim_contested_made"], diet["rim_contested"]),
        "Dunk FG%": pct(d_made, d_att),
        "Mid-range FG%": pct(m_made, m_att),
        "Mid-range share of FGA": pct(m_att, fga),
        "Three FG% (open)": pct(diet["three_open_made"], diet["three_open"]),
        "Three FG% (contested)": pct(diet["three_contested_made"], diet["three_contested"]),
        "Post-up FG%": pct(p_made, p_att),
        "Fastbreak FG%": pct(diet["fastbreak_made"], diet["fastbreak"]),
    }

    print(f"\nCalibration report | {len(factories)} {year} teams, {games} games ({team_games} team-games)\n")
    print(f"{'metric':<28}{'sim':>9}{'real range':>18}   flag")
    print("-" * 64)
    off = 0
    for label, (low, high, fmt) in BENCHMARKS.items():
        value = results[label]
        f = flag(value, low, high)
        off += f != "ok"
        rng = f"{fmt.format(low)} - {fmt.format(high)}"
        print(f"{label:<28}{fmt.format(value):>9}{rng:>18}   {f}")
    print("-" * 64)
    print(f"{len(BENCHMARKS) - off} of {len(BENCHMARKS)} metrics inside the real-world range.")
    print("(Real ranges are approximate recent-league averages; single-season noise is +/- a point or two.)")


if __name__ == "__main__":
    main()
