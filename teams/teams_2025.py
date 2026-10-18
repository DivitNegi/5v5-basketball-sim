"""NBA / Olympic teams for 2025 (moved out of players_data.py, which imports everything defined here)."""
from sim_engine import *


def _players_data():
    """players_data wraps every factory with its calibration overrides; go through it so those apply."""
    import players_data
    return players_data


def make_pacers_2025() -> Team:
    players = [
        Player("Tyrese Haliburton", "PG",
               0.46, 0.22, 0.24, 0.08, 0.08, 0.310,
               0.85, 0.80, 0.89, 0.62, 0.86,
               0.30, 0.96, 0.92,
               0.62, 0.55, 0.34, 0.48, 0.733, 0.600,
               0.76, 0.59,
               clutchness=0.99, stamina=0.87),

        Player("Andrew Nembhard", "SG",
               0.36, 0.30, 0.26, 0.08, 0.12, 0.35,
               0.84, 0.84, 0.84, 0.72, 0.82,
               0.18, 0.76, 0.76,
               0.42, 0.35, 0.32, 0.46, 0.600, 0.667,
               0.88, 0.68,
               clutchness=0.78, stamina=0.83),

        Player("Aaron Nesmith", "SF",
               0.50, 0.20, 0.20, 0.10, 0.28, 0.25,
               0.97, 0.78, 0.82, 0.80, 0.78,
               0.12, 0.38, 0.44,
               0.35, 0.54, 0.42, 0.52, 0.600, 0.933,
               0.75, 0.71, stamina=0.8),

        Player('Pascal Siakam', 'PF',
               0.15, 0.25, 0.24, 0.23, 0.44, 0.45,
               0.82, 0.86, 0.88, 0.75, 0.78,
               0.18, 0.50, 0.76,
               0.46, 0.50, 0.47, 0.69, 0.833, 0.600,
               0.82, 0.78,
               clutchness=0.82, height=80, speed=0.64,
               shot_iq=0.70, archetype='big', stamina=0.85),

        Player("Myles Turner", "C",
               0.36, 0.24, 0.18, 0.22, 0.46, 0.260,
               0.84, 0.80, 0.88, 0.90, 0.78,
               0.18, 0.40, 0.42,
               0.44, 0.90, 0.49, 0.72, 0.733, 0.867,
               0.73, 0.90, stamina=0.72),

        Player("Bennedict Mathurin", "SG",
               0.34, 0.28, 0.30, 0.08, 0.30, 0.245,
               0.82, 0.82, 0.86, 0.82, 0.82,
               0.20, 0.42, 0.56,
               0.39, 0.41, 0.43, 0.65, 0.933, 0.733,
               0.68, 0.41, stamina=0.79),

        Player("T.J. McConnell", "PG",
               0.14, 0.36, 0.34, 0.16, 0.04, 0.210,
               0.62, 0.98, 0.90, 0.50, 0.80,
               0.26, 0.85, 0.84,
               0.85, 0.46, 0.35, 0.53, 0.600, 0.667,
               0.81, 0.48, stamina=0.85),

        Player("Obi Toppin", "PF",
               0.34, 0.22, 0.28, 0.16, 0.70, 0.220,
               0.82, 0.76, 0.88, 0.90, 0.74,
               0.16, 0.42, 0.46,
               0.43, 0.32, 0.41, 0.83, 0.600, 0.733,
               0.48, 0.66, stamina=0.81),

        Player("Ben Sheppard", "SG",
               0.58, 0.18, 0.16, 0.08, 0.12, 0.120,
               0.80, 0.76, 0.78, 0.68, 0.78,
               0.08, 0.36, 0.40,
               0.41, 0.35, 0.41, 0.55, 0.333, 0.600,
               0.79, 0.54, stamina=0.76),

        Player("Thomas Bryant", "C",
               0.18, 0.22, 0.28, 0.32, 0.45, 0.120,
               0.76, 0.76, 0.86, 0.84, 0.72,
               0.10, 0.28, 0.28,
               0.38, 0.70, 0.65, 0.78, 0.533, 0.933,
               0.38, 0.61, stamina=0.66),
    ]
    t = Team("2025 Indiana Pacers", players)
    t.init_lineup()
    return t


def make_knicks_2025() -> Team:
    return _players_data().make_knicks_2026()
