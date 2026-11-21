"""NBA / Olympic teams for 2004 (moved out of players_data.py, which imports everything defined here)."""
from sim_engine import *


def make_pistons_2004() -> Team:
    players = [
        Player("Chauncey Billups", "PG",
               0.42, 0.34, 0.18, 0.06,   0.04, 0.285,
               0.86, 0.86, 0.82, 0.55, 0.88,
               0.24, 0.82, 0.78,
               0.76, 0.38, 0.36, 0.52, 0.800, 0.733,
               0.94, 0.58,
               clutchness=0.90, secondary_positions=("SG",), shot_iq=0.90, stamina=0.8),

        Player("Richard Hamilton", "SG",
               0.26, 0.48, 0.20, 0.06,   0.08, 0.305,
               0.82, 0.90, 0.84, 0.62, 0.86,
               0.25, 0.48, 0.70,
               0.62, 0.35, 0.34, 0.50, 0.733, 0.667,
               0.82, 0.56,
               clutchness=0.84, secondary_positions=("SF",), shot_iq=0.84, stamina=0.79),

        Player("Tayshaun Prince", "SF",
               0.32, 0.34, 0.22, 0.12,   0.18, 0.210,
               0.80, 0.82, 0.84, 0.72, 0.78,
               0.16, 0.46, 0.54,
               0.70, 0.70, 0.47, 0.64, 0.467, 0.667,
               0.90, 0.80,
               clutchness=0.78, secondary_positions=("PF",), shot_iq=0.82, stamina=0.82),

        Player("Rasheed Wallace", "PF",
               0.34, 0.34, 0.14, 0.18,   0.28, 0.265,
               0.82, 0.86, 0.86, 0.82, 0.76,
               0.22, 0.48, 0.50,
               0.61, 0.82, 0.70, 0.84, 0.667, 0.990,
               0.74, 0.88,
               clutchness=0.84, secondary_positions=("C",), shot_iq=0.80, stamina=0.72),

        Player("Ben Wallace", "C",
               0.00, 0.00, 0.34, 0.62,   0.58, 0.120,
               0.05, 0.52, 0.84, 0.86, 0.42,
               0.10, 0.28, 0.30,
               0.85, 0.99, 0.99, 0.99, 0.533, 0.933,
               0.85, 0.99,
               clutchness=0.70, shot_iq=0.70, stamina=0.86),

        Player("Mehmet Okur", "C",
               0.26, 0.34, 0.16, 0.24,   0.18, 0.205,
               0.80, 0.82, 0.82, 0.70, 0.78,
               0.16, 0.36, 0.38,
               0.45, 0.62, 0.66, 0.78, 0.600, 0.800,
               0.45, 0.74,
               secondary_positions=("PF",), shot_iq=0.78, stamina=0.68),

        Player("Corliss Williamson", "SF",
               0.08, 0.34, 0.26, 0.32,   0.28, 0.240,
               0.55, 0.82, 0.86, 0.78, 0.76,
               0.20, 0.34, 0.42,
               0.52, 0.50, 0.56, 0.62, 0.733, 0.800,
               0.58, 0.68,
               secondary_positions=("PF",), shot_iq=0.76, stamina=0.7),

        Player("Lindsey Hunter", "PG",
               0.46, 0.26, 0.20, 0.08,   0.04, 0.145,
               0.78, 0.76, 0.76, 0.55, 0.78,
               0.10, 0.56, 0.62,
               0.84, 0.30, 0.31, 0.42, 0.333, 0.733,
               0.88, 0.42,
               secondary_positions=("SG",), shot_iq=0.76, stamina=0.72),

        Player("Mike James", "PG",
               0.42, 0.28, 0.24, 0.06,   0.08, 0.175,
               0.80, 0.78, 0.80, 0.62, 0.80,
               0.14, 0.58, 0.66,
               0.78, 0.28, 0.32, 0.43, 0.467, 0.667,
               0.80, 0.38,
               secondary_positions=("SG",), shot_iq=0.74, stamina=0.71),

        Player("Elden Campbell", "C",
               0.02, 0.22, 0.28, 0.48,   0.30, 0.105,
               0.08, 0.72, 0.82, 0.78, 0.66,
               0.08, 0.28, 0.26,
               0.42, 0.76, 0.70, 0.78, 0.467, 0.933,
               0.40, 0.82,
               secondary_positions=("PF",), shot_iq=0.72, stamina=0.58),
    ]
    t = Team("2004 Detroit Pistons", players)
    t.init_lineup()
    return t
