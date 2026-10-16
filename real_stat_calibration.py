"""
Per-player rating / tendency calibration against real regular-season lines.

players_data.py builds every historical team from hand-entered ratings. This
module holds the corrections found by comparing a simulated season with the
real per-game stats of the same players (points, rebounds, assists, FG%, 3P%,
FT%, steals, blocks, attempts). Everything here is an ordinary rating or
tendency -- no volume caps. OVERRIDES maps

    team name -> player name -> {attribute: value}

and wrap_factories() applies it every time a make_*_YYYY team is built.
"""
import functools

OVERRIDES = {
    "1986 Boston Celtics": {
        "Kevin McHale": {"block": 0.865, "dreb": 0.509, "dunk_rating": 0.94, "mid_rating": 0.99, "oreb": 0.538, "playmaking": 0.5, "rim_rating": 0.99, "shot_tendency": 0.337, "usage": 0.219},
        "Larry Bird": {"block": 0.643, "dreb": 0.602, "dunk_rating": 0.844, "ft_rating": 0.881, "mid_rating": 0.99, "oreb": 0.422, "playmaking": 0.747, "rim_rating": 0.99, "shot_tendency": 0.53, "steal": 0.78, "three_rating": 0.99, "usage": 0.374},
    },
    "1987 Boston Celtics": {
        "Larry Bird": {"block": 0.61, "dreb": 0.95, "dunk_rating": 0.853, "ft_rating": 0.906, "mid_rating": 0.987, "oreb": 0.71, "playmaking": 0.69, "rim_rating": 0.986, "shot_tendency": 0.576, "steal": 0.752, "three_rating": 0.99, "usage": 0.436},
    },
    "1987 Los Angeles Lakers": {
        "Kareem Abdul-Jabbar": {"block": 0.8, "dreb": 0.81, "dunk_rating": 0.964, "ft_rating": 0.706, "mid_rating": 0.896, "oreb": 0.8, "playmaking": 0.63, "rim_rating": 0.935, "shot_tendency": 0.222, "steal": 0.524, "usage": 0.164},
        "Magic Johnson": {"block": 0.453, "dreb": 0.814, "dunk_rating": 0.738, "ft_rating": 0.828, "mid_rating": 0.805, "oreb": 0.408, "playmaking": 0.99, "rim_rating": 0.832, "shot_tendency": 0.46, "steal": 0.77, "usage": 0.52},
    },
    "1994 Houston Rockets": {
        "Hakeem Olajuwon": {"block": 0.929, "dreb": 0.851, "dunk_rating": 0.909, "ft_rating": 0.718, "mid_rating": 0.875, "oreb": 0.796, "playmaking": 0.708, "rim_rating": 0.897, "shot_tendency": 0.42, "steal": 0.836, "usage": 0.24},
    },
    "1996 Chicago Bulls": {
        "Dennis Rodman": {"block": 0.471, "dreb": 0.99, "oreb": 0.99, "playmaking": 0.55, "shot_tendency": 0.3, "steal": 0.48, "usage": 0.019},
        "Michael Jordan": {"block": 0.6, "dreb": 0.66, "dunk_rating": 0.977, "ft_rating": 0.817, "mid_rating": 0.972, "oreb": 0.67, "playmaking": 0.616, "rim_rating": 0.963, "shot_tendency": 0.496, "steal": 0.99, "three_rating": 0.85, "three_tendency": 0.107, "usage": 0.33},
        "Scottie Pippen": {"block": 0.6, "dreb": 0.7, "dunk_rating": 0.761, "mid_rating": 0.779, "oreb": 0.53, "playmaking": 0.828, "rim_rating": 0.854, "shot_tendency": 0.405, "steal": 0.8, "usage": 0.32},
    },
    "1997 Utah Jazz": {
        "Karl Malone": {"block": 0.551, "dreb": 0.43, "dunk_rating": 0.96, "ft_rating": 0.73, "mid_rating": 0.99, "oreb": 0.39, "playmaking": 0.6, "rim_rating": 0.99, "shot_tendency": 0.3, "steal": 0.61, "usage": 0.216},
    },
    "1999 San Antonio Spurs": {
        "David Robinson": {"dreb": 0.35, "dunk_rating": 0.93, "mid_rating": 0.98, "oreb": 0.301, "rim_rating": 0.99, "shot_tendency": 0.179, "usage": 0.126},
        "Tim Duncan": {"block": 0.847, "dreb": 0.43, "dunk_rating": 0.822, "ft_rating": 0.711, "mid_rating": 0.938, "oreb": 0.39, "playmaking": 0.558, "rim_rating": 0.977, "shot_tendency": 0.267, "steal": 0.391, "usage": 0.208},
    },
    "2001 Los Angeles Lakers": {
        "Kobe Bryant": {"block": 0.46, "dreb": 0.61, "dunk_rating": 0.917, "ft_rating": 0.81, "mid_rating": 0.937, "oreb": 0.49, "playmaking": 0.552, "rim_rating": 0.944, "shot_tendency": 0.92, "steal": 0.79, "three_rating": 0.78, "three_tendency": 0.328, "usage": 0.388},
        "Shaquille O'Neal": {"block": 0.84, "dreb": 0.886, "dunk_rating": 0.967, "ft_rating": 0.507, "mid_rating": 0.67, "oreb": 0.886, "playmaking": 0.5, "rim_rating": 0.941, "shot_tendency": 0.576, "steal": 0.48, "usage": 0.48},
    },
    "2001 Philadelphia 76ers": {
        "Allen Iverson": {"block": 0.4, "dreb": 0.611, "dunk_rating": 0.92, "ft_rating": 0.808, "mid_rating": 0.99, "oreb": 0.466, "playmaking": 0.612, "rim_rating": 0.99, "shot_tendency": 0.819, "steal": 0.99, "three_rating": 0.95, "usage": 0.348},
    },
    "2003 San Antonio Spurs": {
        "Tim Duncan": {"block": 0.888, "dreb": 0.99, "dunk_rating": 0.873, "ft_rating": 0.676, "mid_rating": 0.827, "oreb": 0.99, "playmaking": 0.79, "rim_rating": 0.855, "shot_tendency": 0.209, "steal": 0.58, "usage": 0.325},
    },
    "2005 Phoenix Suns": {
        "Amar'e Stoudemire": {"block": 0.812, "dreb": 0.69, "dunk_rating": 0.969, "ft_rating": 0.748, "mid_rating": 0.851, "oreb": 0.635, "playmaking": 0.51, "rim_rating": 0.977, "shot_tendency": 0.285, "steal": 0.6, "usage": 0.223},
    },
    "2006 Miami Heat": {
        "Dwyane Wade": {"block": 0.65, "dreb": 0.632, "dunk_rating": 0.844, "ft_rating": 0.778, "mid_rating": 0.754, "oreb": 0.611, "playmaking": 0.782, "rim_rating": 0.854, "shot_tendency": 0.612, "steal": 0.84, "three_rating": 0.658, "usage": 0.479},
    },
    "2008 Boston Celtics": {
        "Kevin Garnett": {"block": 0.681, "dreb": 0.79, "dunk_rating": 0.87, "ft_rating": 0.785, "mid_rating": 0.889, "oreb": 0.78, "playmaking": 0.755, "rim_rating": 0.883, "shot_tendency": 0.296, "steal": 0.743, "usage": 0.201},
        "Paul Pierce": {"dreb": 0.566, "dunk_rating": 0.754, "mid_rating": 0.884, "oreb": 0.401, "playmaking": 0.678, "rim_rating": 0.81, "shot_tendency": 0.319, "steal": 0.563, "three_rating": 0.949, "usage": 0.205},
        "Rajon Rondo": {"dreb": 0.583, "oreb": 0.497, "playmaking": 0.81, "shot_tendency": 0.197, "steal": 0.83, "usage": 0.492},
    },
    "2008 Los Angeles Lakers": {
        "Kobe Bryant": {"block": 0.46, "dreb": 0.61, "dunk_rating": 0.807, "ft_rating": 0.828, "mid_rating": 0.863, "oreb": 0.48, "playmaking": 0.634, "rim_rating": 0.81, "shot_tendency": 0.647, "steal": 0.78, "three_rating": 0.988, "usage": 0.349},
    },
    "2009 Cleveland Cavaliers": {
        "LeBron James": {"block": 0.7, "dreb": 0.774, "dunk_rating": 0.84, "ft_rating": 0.787, "mid_rating": 0.73, "oreb": 0.483, "playmaking": 0.787, "rim_rating": 0.84, "shot_tendency": 0.818, "steal": 0.73, "three_rating": 0.748, "usage": 0.418},
    },
    "2009 Orlando Magic": {
        "Dwight Howard": {"block": 0.917, "dreb": 0.99, "dunk_rating": 0.921, "ft_rating": 0.587, "mid_rating": 0.32, "oreb": 0.99, "playmaking": 0.51, "rim_rating": 0.885, "shot_tendency": 0.431, "steal": 0.657, "usage": 0.301},
    },
    "2011 Chicago Bulls": {
        "Derrick Rose": {"block": 0.52, "dreb": 0.593, "dunk_rating": 0.801, "ft_rating": 0.857, "mid_rating": 0.769, "oreb": 0.529, "playmaking": 0.823, "rim_rating": 0.778, "shot_tendency": 0.95, "steal": 0.721, "three_rating": 0.774, "usage": 0.67},
    },
    "2011 Dallas Mavericks": {
        "Dirk Nowitzki": {"block": 0.543, "dreb": 0.71, "dunk_rating": 0.691, "ft_rating": 0.89, "mid_rating": 0.968, "oreb": 0.64, "playmaking": 0.563, "rim_rating": 0.962, "shot_tendency": 0.194, "steal": 0.51, "three_rating": 0.902, "usage": 0.177},
        "Jason Kidd": {"dreb": 0.65, "oreb": 0.389, "playmaking": 0.99, "shot_tendency": 0.104, "usage": 0.067},
        "Tyson Chandler": {"dreb": 0.803, "oreb": 0.783, "shot_tendency": 0.172, "usage": 0.104},
    },
    "2012 Oklahoma City Thunder": {
        "Kevin Durant": {"block": 0.7, "dreb": 0.94, "dunk_rating": 0.834, "ft_rating": 0.843, "mid_rating": 0.915, "oreb": 0.388, "playmaking": 0.65, "rim_rating": 0.848, "shot_tendency": 0.429, "steal": 0.68, "three_rating": 0.912, "usage": 0.29},
    },
    "2013 Memphis Grizzlies": {
        "Marc Gasol": {"dreb": 0.74, "oreb": 0.65, "playmaking": 0.87, "shot_tendency": 0.184, "usage": 0.128},
        "Zach Randolph": {"dreb": 0.99, "oreb": 0.956, "playmaking": 0.57, "shot_tendency": 0.231, "usage": 0.157},
    },
    "2013 Miami Heat": {
        "LeBron James": {"block": 0.64, "dreb": 0.84, "dunk_rating": 0.975, "ft_rating": 0.731, "mid_rating": 0.879, "oreb": 0.487, "playmaking": 0.791, "rim_rating": 0.961, "shot_tendency": 0.693, "steal": 0.73, "three_rating": 0.99, "usage": 0.294},
    },
    "2013 New York Knicks": {
        "Carmelo Anthony": {"block": 0.543, "dreb": 0.69, "dunk_rating": 0.85, "ft_rating": 0.827, "mid_rating": 0.962, "oreb": 0.66, "playmaking": 0.563, "rim_rating": 0.938, "shot_tendency": 0.427, "steal": 0.57, "three_rating": 0.99, "usage": 0.27},
    },
    "2014 Los Angeles Clippers": {
        "Blake Griffin": {"block": 0.604, "dreb": 0.817, "dunk_rating": 0.909, "ft_rating": 0.712, "mid_rating": 0.759, "oreb": 0.709, "playmaking": 0.708, "rim_rating": 0.795, "shot_tendency": 0.381, "steal": 0.663, "usage": 0.181},
    },
    "2014 San Antonio Spurs": {
        "Tim Duncan": {"block": 0.8, "dreb": 0.81, "dunk_rating": 0.771, "mid_rating": 0.766, "oreb": 0.79, "playmaking": 0.7, "rim_rating": 0.83, "shot_tendency": 0.28, "usage": 0.18},
    },
    "2016 Cleveland Cavaliers": {
        "Kevin Love": {"block": 0.672, "dreb": 0.794, "dunk_rating": 0.66, "ft_rating": 0.821, "mid_rating": 0.725, "oreb": 0.614, "playmaking": 0.7, "rim_rating": 0.742, "shot_tendency": 0.544, "steal": 0.446, "three_rating": 0.767, "three_tendency": 0.267, "usage": 0.299},
        "Tristan Thompson": {"block": 0.81, "dreb": 0.835, "dunk_rating": 0.819, "mid_rating": 0.7, "oreb": 0.93, "playmaking": 0.45, "rim_rating": 0.86, "shot_tendency": 0.264, "steal": 0.531, "usage": 0.143},
    },
    "2016 Dallas Mavericks": {
        "Dirk Nowitzki": {"block": 0.658, "dreb": 0.71, "dunk_rating": 0.874, "ft_rating": 0.867, "mid_rating": 0.76, "oreb": 0.64, "playmaking": 0.594, "rim_rating": 0.712, "shot_tendency": 0.381, "steal": 0.51, "three_rating": 0.857, "three_tendency": 0.197, "usage": 0.139},
    },
    "2016 Golden State Warriors": {
        "Andrew Bogut": {"block": 0.95, "dreb": 0.76, "dunk_rating": 0.784, "mid_rating": 0.636, "oreb": 0.64, "playmaking": 0.73, "rim_rating": 0.806, "shot_tendency": 0.129, "steal": 0.71, "usage": 0.064},
        "Draymond Green": {"block": 0.756, "dreb": 0.647, "dunk_rating": 0.726, "mid_rating": 0.769, "oreb": 0.357, "playmaking": 0.99, "rim_rating": 0.873, "shot_tendency": 0.188, "steal": 0.77, "three_rating": 0.813, "three_tendency": 0.223, "usage": 0.25},
        "Harrison Barnes": {"dreb": 0.466, "oreb": 0.437, "shot_tendency": 0.161, "usage": 0.097},
        "Klay Thompson": {"block": 0.585, "dreb": 0.449, "dunk_rating": 0.834, "ft_rating": 0.916, "mid_rating": 0.827, "oreb": 0.309, "playmaking": 0.31, "rim_rating": 0.867, "shot_tendency": 0.319, "steal": 0.63, "three_rating": 0.99, "three_tendency": 0.55, "usage": 0.233},
        "Stephen Curry": {"shot_iq": 0.97},
    },
    "2016 Houston Rockets": {
        "Dwight Howard": {"block": 0.893, "dreb": 0.855, "dunk_rating": 0.962, "ft_rating": 0.502, "mid_rating": 0.579, "oreb": 0.864, "playmaking": 0.555, "rim_rating": 0.951, "shot_tendency": 0.218, "usage": 0.152},
        "James Harden": {"block": 0.518, "dreb": 0.65, "dunk_rating": 0.725, "ft_rating": 0.852, "mid_rating": 0.879, "oreb": 0.378, "playmaking": 0.806, "rim_rating": 0.862, "shot_tendency": 0.597, "steal": 0.6, "three_rating": 0.988, "three_tendency": 0.471, "usage": 0.38},
        "Trevor Ariza": {"block": 0.399, "dreb": 0.55, "dunk_rating": 0.744, "mid_rating": 0.694, "oreb": 0.38, "playmaking": 0.577, "rim_rating": 0.669, "shot_tendency": 0.251, "steal": 0.86, "three_rating": 0.823, "three_tendency": 0.446, "usage": 0.185},
    },
    "2016 Indiana Pacers": {
        "Paul George": {"block": 0.42, "dreb": 0.692, "dunk_rating": 0.818, "ft_rating": 0.869, "mid_rating": 0.794, "oreb": 0.365, "playmaking": 0.55, "rim_rating": 0.73, "shot_tendency": 0.325, "steal": 0.979, "three_rating": 0.888, "three_tendency": 0.291, "usage": 0.215},
    },
    "2016 Los Angeles Clippers": {
        "Blake Griffin": {"block": 0.645, "dreb": 0.717, "dunk_rating": 0.852, "ft_rating": 0.744, "mid_rating": 0.787, "oreb": 0.669, "playmaking": 0.861, "rim_rating": 0.811, "shot_tendency": 0.516, "steal": 0.618, "usage": 0.352},
    },
    "2016 Memphis Grizzlies": {
        "Zach Randolph": {"block": 0.52, "dreb": 0.913, "dunk_rating": 0.905, "mid_rating": 0.832, "oreb": 0.913, "playmaking": 0.637, "rim_rating": 0.808, "shot_tendency": 0.261, "steal": 0.57, "usage": 0.172},
    },
    "2016 Miami Heat": {
        "Hassan Whiteside": {"block": 0.99, "dreb": 0.857, "dunk_rating": 0.92, "ft_rating": 0.636, "mid_rating": 0.756, "oreb": 0.822, "playmaking": 0.437, "rim_rating": 0.87, "shot_tendency": 0.311, "steal": 0.655, "usage": 0.217},
    },
    "2016 Oklahoma City Thunder": {
        "Kevin Durant": {"block": 0.726, "dreb": 0.77, "dunk_rating": 0.785, "ft_rating": 0.92, "mid_rating": 0.847, "oreb": 0.48, "playmaking": 0.793, "rim_rating": 0.79, "shot_tendency": 0.595, "steal": 0.427, "three_rating": 0.877, "three_tendency": 0.359, "usage": 0.372},
        "Russell Westbrook": {"block": 0.414, "dreb": 0.86, "dunk_rating": 0.895, "ft_rating": 0.797, "mid_rating": 0.756, "oreb": 0.67, "playmaking": 0.99, "rim_rating": 0.83, "shot_tendency": 0.755, "steal": 0.82, "three_rating": 0.763, "three_tendency": 0.447, "usage": 0.49},
        "Serge Ibaka": {"block": 0.912, "dreb": 0.565, "dunk_rating": 0.913, "mid_rating": 0.821, "oreb": 0.478, "playmaking": 0.184, "rim_rating": 0.826, "shot_tendency": 0.156, "steal": 0.485, "three_rating": 0.857, "three_tendency": 0.062, "usage": 0.1},
        "Steven Adams": {"block": 0.81, "dreb": 0.69, "dunk_rating": 0.966, "ft_rating": 0.582, "mid_rating": 0.15, "oreb": 0.77, "playmaking": 0.484, "rim_rating": 0.99, "shot_tendency": 0.15, "steal": 0.56, "usage": 0.106},
    },
    "2016 San Antonio Spurs": {
        "Kawhi Leonard": {"block": 0.64, "dreb": 0.716, "dunk_rating": 0.871, "ft_rating": 0.846, "mid_rating": 0.876, "oreb": 0.437, "playmaking": 0.55, "rim_rating": 0.852, "shot_tendency": 0.332, "steal": 0.78, "three_rating": 0.99, "three_tendency": 0.221, "usage": 0.218},
        "LaMarcus Aldridge": {"block": 0.82, "dreb": 0.77, "dunk_rating": 0.894, "ft_rating": 0.839, "mid_rating": 0.855, "oreb": 0.69, "playmaking": 0.512, "rim_rating": 0.808, "shot_tendency": 0.245, "steal": 0.45, "usage": 0.175},
        "Tim Duncan": {"block": 0.896, "dreb": 0.769, "dunk_rating": 0.896, "ft_rating": 0.735, "mid_rating": 0.8, "oreb": 0.727, "playmaking": 0.708, "rim_rating": 0.795, "shot_tendency": 0.206, "steal": 0.77, "usage": 0.142},
        "Tony Parker": {"dreb": 0.615, "oreb": 0.397, "playmaking": 0.809, "shot_tendency": 0.403, "usage": 0.275},
    },
    "2017 Golden State Warriors": {
        "Draymond Green": {"block": 0.785, "dreb": 0.698, "dunk_rating": 0.774, "ft_rating": 0.741, "mid_rating": 0.824, "oreb": 0.388, "playmaking": 0.99, "rim_rating": 0.99, "shot_tendency": 0.261, "steal": 0.907, "three_rating": 0.742, "three_tendency": 0.5, "usage": 0.229},
        "Kevin Durant": {"block": 0.839, "dreb": 0.712, "dunk_rating": 0.808, "ft_rating": 0.875, "mid_rating": 0.888, "oreb": 0.379, "playmaking": 0.8, "rim_rating": 0.835, "shot_tendency": 0.525, "steal": 0.5, "three_rating": 0.792, "three_tendency": 0.372, "usage": 0.325},
        "Klay Thompson": {"block": 0.567, "dreb": 0.444, "dunk_rating": 0.845, "ft_rating": 0.901, "mid_rating": 0.844, "oreb": 0.306, "playmaking": 0.478, "rim_rating": 0.85, "shot_tendency": 0.449, "steal": 0.63, "three_rating": 0.912, "three_tendency": 0.6, "usage": 0.273},
        "Stephen Curry": {"block": 0.468, "dreb": 0.571, "dunk_rating": 0.658, "ft_rating": 0.889, "mid_rating": 0.98, "oreb": 0.344, "playmaking": 0.743, "rim_rating": 0.896, "shot_tendency": 0.617, "steal": 0.61, "three_rating": 0.957, "three_tendency": 0.667, "usage": 0.318},
    },
    "2018 Boston Celtics": {
        "Kyrie Irving": {"block": 0.476, "dreb": 0.581, "dunk_rating": 0.305, "ft_rating": 0.854, "mid_rating": 0.886, "oreb": 0.491, "playmaking": 0.676, "rim_rating": 0.898, "shot_tendency": 0.473, "steal": 0.65, "three_rating": 0.99, "three_tendency": 0.381, "usage": 0.302},
    },
    "2018 Cleveland Cavaliers": {
        "LeBron James": {"block": 0.7, "dreb": 0.84, "dunk_rating": 0.948, "ft_rating": 0.723, "mid_rating": 0.874, "oreb": 0.492, "playmaking": 0.891, "rim_rating": 0.924, "shot_tendency": 0.709, "steal": 0.48, "three_rating": 0.802, "three_tendency": 0.437, "usage": 0.507},
    },
    "2018 Houston Rockets": {
        "James Harden": {"block": 0.69, "dreb": 0.718, "dunk_rating": 0.694, "ft_rating": 0.879, "mid_rating": 0.721, "oreb": 0.365, "playmaking": 0.914, "rim_rating": 0.83, "shot_tendency": 0.99, "steal": 0.87, "three_rating": 0.967, "three_tendency": 0.55, "usage": 0.445,
                         # 30+ a night: an explicit attempt role (~23 shots) that keeps possessions when behind pace
                         "target_fga_soft_cap": 25.0, "target_fga_per_game": 23.0, "target_fga_precision": 1.0, "keep_pace_shots": True},
    },
    "2020 Houston Rockets": {
        # Harden's 2019-20 scoring title: ~34 points on ~23 shots and 11+ free throws. His hand-entered row had him
        # at a 0.30 usage / 0.64 foul draw / 0.40 shot IQ, which left him at ~19 points.
        "James Harden": {"usage": 0.45, "shot_tendency": 0.95, "foul_draw": 0.95, "shot_iq": 0.62, "three_rating": 0.91,
                         "target_fga_soft_cap": 25.0, "target_fga_per_game": 23.0, "target_fga_precision": 1.0, "keep_pace_shots": True},
    },
    "2018 Milwaukee Bucks": {
        "Giannis Antetokounmpo": {"block": 0.705, "dreb": 0.805, "dunk_rating": 0.933, "ft_rating": 0.593, "mid_rating": 0.701, "oreb": 0.728, "playmaking": 0.711, "rim_rating": 0.904, "shot_tendency": 0.497, "steal": 0.601, "three_rating": 0.49, "three_tendency": 0.237, "usage": 0.302},
    },
    "2018 New Orleans Pelicans": {
        "Anthony Davis": {"block": 0.874, "dreb": 0.99, "dunk_rating": 0.896, "ft_rating": 0.828, "mid_rating": 0.83, "oreb": 0.895, "playmaking": 0.486, "rim_rating": 0.873, "shot_tendency": 0.438, "steal": 0.649, "three_rating": 0.748, "three_tendency": 0.207, "usage": 0.229},
    },
    "2018 Utah Jazz": {
        "Donovan Mitchell": {"block": 0.392, "dreb": 0.582, "dunk_rating": 0.89, "ft_rating": 0.805, "mid_rating": 0.903, "oreb": 0.34, "playmaking": 0.51, "rim_rating": 0.96, "shot_tendency": 0.287, "steal": 0.7, "three_rating": 0.904, "three_tendency": 0.348, "usage": 0.22},
    },
    "2019 Golden State Warriors": {
        "Kevin Durant": {"block": 0.713, "dreb": 0.574, "dunk_rating": 0.803, "ft_rating": 0.877, "mid_rating": 0.882, "oreb": 0.314, "playmaking": 0.85, "rim_rating": 0.79, "shot_tendency": 0.502, "steal": 0.316, "three_rating": 0.77, "three_tendency": 0.405, "usage": 0.366},
    },
    "2019 Toronto Raptors": {
        "Kawhi Leonard": {"block": 0.433, "dreb": 0.74, "dunk_rating": 0.873, "ft_rating": 0.853, "mid_rating": 0.97, "oreb": 0.461, "playmaking": 0.5, "rim_rating": 0.949, "shot_tendency": 0.332, "steal": 0.81, "three_rating": 0.99, "three_tendency": 0.233, "usage": 0.264},
    },
    "2022 Boston Celtics": {
        "Jayson Tatum": {"block": 0.6, "dreb": 0.942, "dunk_rating": 0.84, "ft_rating": 0.851, "mid_rating": 0.891, "oreb": 0.359, "playmaking": 0.592, "rim_rating": 0.948, "shot_tendency": 0.382, "steal": 0.51, "three_rating": 0.99, "three_tendency": 0.314, "usage": 0.234},
    },
    "2022 Dallas Mavericks": {
        "Luka Doncic": {"block": 0.67, "dreb": 0.96, "dunk_rating": 0.771, "ft_rating": 0.721, "mid_rating": 0.937, "oreb": 0.7, "playmaking": 0.892, "rim_rating": 0.96, "shot_tendency": 0.867, "steal": 0.759, "three_rating": 0.829, "three_tendency": 0.664, "usage": 0.576},
    },
    "2022 Golden State Warriors": {
        "Draymond Green": {"block": 0.711, "dreb": 0.833, "dunk_rating": 0.716, "mid_rating": 0.743, "oreb": 0.462, "playmaking": 0.99, "rim_rating": 0.874, "shot_tendency": 0.154, "steal": 0.67, "usage": 0.096},
        "Stephen Curry": {"block": 0.648, "dreb": 0.68, "dunk_rating": 0.564, "ft_rating": 0.9, "mid_rating": 0.842, "oreb": 0.47, "playmaking": 0.672, "rim_rating": 0.848, "shot_tendency": 0.538, "steal": 0.61, "three_rating": 0.927, "three_tendency": 0.822, "usage": 0.354},
    },
    "2024 Boston Celtics": {
        "Jayson Tatum": {"block": 0.545, "dreb": 0.791, "dunk_rating": 0.789, "ft_rating": 0.821, "mid_rating": 0.848, "oreb": 0.301, "playmaking": 0.718, "rim_rating": 0.818, "shot_tendency": 0.443, "steal": 0.51, "three_rating": 0.846, "three_tendency": 0.238, "usage": 0.332},
    },
    "2024 Dallas Mavericks": {
        # Volume (usage / shot_tendency / three_tendency) is left to the hand-entered row; he takes ~23 shots a night.
        "Luka Doncic": {"block": 0.67, "dreb": 0.96, "dunk_rating": 0.93, "ft_rating": 0.784, "mid_rating": 0.99, "oreb": 0.617, "playmaking": 0.80, "foul_draw": 0.80, "rim_rating": 0.99, "steal": 0.77, "three_rating": 0.84,
                        # ~23 shots a night: an explicit attempt role plus opt-in "keep the possession when behind pace".
                        "target_fga_soft_cap": 25.0, "target_fga_per_game": 22.6, "target_fga_precision": 1.0, "keep_pace_shots": True},
    },
    "2024 Denver Nuggets": {
        "Nikola Jokic": {"block": 0.73, "dreb": 0.99, "dunk_rating": 0.675, "ft_rating": 0.782, "mid_rating": 0.904, "oreb": 0.875, "playmaking": 0.949, "rim_rating": 0.939, "shot_tendency": 0.573, "steal": 0.68, "three_rating": 0.757, "three_tendency": 0.212, "usage": 0.376},
    },
    "2024 Los Angeles Clippers": {
        "Kawhi Leonard": {"block": 0.708, "dreb": 0.635, "dunk_rating": 0.895, "ft_rating": 0.869, "mid_rating": 0.949, "oreb": 0.44, "playmaking": 0.551, "rim_rating": 0.98, "shot_tendency": 0.31, "steal": 0.76, "three_rating": 0.989, "three_tendency": 0.12, "usage": 0.221},
    },
    "2024 Minnesota Timberwolves": {
        "Anthony Edwards": {"block": 0.486, "dreb": 0.707, "dunk_rating": 0.931, "ft_rating": 0.853, "mid_rating": 0.915, "oreb": 0.301, "playmaking": 0.554, "rim_rating": 0.968, "shot_tendency": 0.455, "steal": 0.74, "three_rating": 0.976, "three_tendency": 0.409, "usage": 0.189},
    },
    "2024 Oklahoma City Thunder": {
        "Shai G-Alexander": {"block": 0.749, "dreb": 0.714, "dunk_rating": 0.895, "ft_rating": 0.858, "mid_rating": 0.98, "oreb": 0.402, "playmaking": 0.722, "rim_rating": 0.976, "shot_tendency": 0.459, "steal": 0.864, "three_rating": 0.873, "three_tendency": 0.204, "usage": 0.359},
    },
}


def apply_overrides(team):
    table = OVERRIDES.get(getattr(team, "name", ""))
    if table:
        for player in team.roster:
            for attr, value in table.get(player.name, {}).items():
                setattr(player, attr, value)
    return team


def _wrap(factory):
    @functools.wraps(factory)
    def wrapped(*args, **kwargs):
        return apply_overrides(factory(*args, **kwargs))

    return wrapped


def _is_team_factory(name, fn):
    return (
        name.startswith("make_") and callable(fn) and name[-5:-4] == "_" and name[-4:].isdigit()
        and not getattr(fn, "_real_stat_wrapped", False)
    )


def wrap_factories(namespace):
    """Wrap every make_*_YYYY factory in `namespace`, including the ones stored in
    module-level registries (e.g. PLAYOFF_2016_TEAM_FACTORIES)."""
    for name, fn in list(namespace.items()):
        if _is_team_factory(name, fn):
            wrapped = _wrap(fn)
            wrapped._real_stat_wrapped = True
            namespace[name] = wrapped
    for value in list(namespace.values()):
        if isinstance(value, dict):
            for key, fn in list(value.items()):
                if callable(fn) and _is_team_factory(getattr(fn, "__name__", ""), fn):
                    wrapped = _wrap(fn)
                    wrapped._real_stat_wrapped = True
                    value[key] = wrapped
