"""Real regular-season records (wins, losses) of the teams in the sim, used by the custom season's "strongest teams" button.

The year in a team's name is the season's ending year (2018 = 2017-18). The 2027 teams are projections and have no record.
Lockout / short seasons (1999: 50 games, 2012: 66, 2020 and 2021) are compared by win percentage, scaled to 82 games."""
from typing import Dict, Optional, Tuple

REAL_RECORDS: Dict[str, Tuple[int, int]] = {
    "1962 Boston Celtics": (60, 20), "1967 Philadelphia 76ers": (68, 13), "1971 Milwaukee Bucks": (66, 16),
    "1972 Los Angeles Lakers": (69, 13), "1973 New York Knicks": (57, 25), "1977 Portland Trail Blazers": (49, 33),
    "1979 Seattle SuperSonics": (52, 30), "1980 Los Angeles Lakers": (60, 22), "1983 Philadelphia 76ers": (65, 17),
    "1984 Boston Celtics": (62, 20), "1986 Boston Celtics": (67, 15), "1987 Boston Celtics": (59, 23),
    "1987 Los Angeles Lakers": (65, 17), "1989 Detroit Pistons": (63, 19), "1991 Chicago Bulls": (61, 21),
    "1994 Houston Rockets": (58, 24), "1995 Houston Rockets": (47, 35), "1996 Chicago Bulls": (72, 10),
    "1997 Utah Jazz": (64, 18), "1998 Chicago Bulls": (62, 20), "1999 San Antonio Spurs": (37, 13),
    "2001 Los Angeles Lakers": (56, 26), "2001 Philadelphia 76ers": (56, 26), "2003 San Antonio Spurs": (60, 22),
    "2004 Detroit Pistons": (54, 28), "2005 Phoenix Suns": (62, 20), "2006 Miami Heat": (52, 30),
    "2007 Golden State Warriors": (42, 40), "2007 San Antonio Spurs": (58, 24), "2008 Boston Celtics": (66, 16),
    "2008 Los Angeles Lakers": (57, 25), "2009 Cleveland Cavaliers": (66, 16), "2009 Orlando Magic": (59, 23),
    "2011 Chicago Bulls": (62, 20), "2011 Dallas Mavericks": (57, 25), "2012 Boston Celtics": (39, 27),
    "2012 Oklahoma City Thunder": (47, 19), "2013 Indiana Pacers": (49, 32), "2013 Memphis Grizzlies": (56, 26),
    "2013 Miami Heat": (66, 16), "2013 New York Knicks": (54, 28), "2014 Los Angeles Clippers": (57, 25),
    "2014 San Antonio Spurs": (62, 20), "2015 Atlanta Hawks": (60, 22), "2015 Los Angeles Clippers": (56, 26),
    "2016 Cleveland Cavaliers": (57, 25), "2016 Golden State Warriors": (73, 9), "2016 Oklahoma City Thunder": (55, 27),
    "2017 Cleveland Cavaliers": (51, 31), "2017 Golden State Warriors": (67, 15), "2017 Washington Wizards": (49, 33),
    "2018 Atlanta Hawks": (24, 58), "2018 Boston Celtics": (55, 27), "2018 Brooklyn Nets": (28, 54),
    "2018 Charlotte Hornets": (36, 46), "2018 Chicago Bulls": (27, 55), "2018 Cleveland Cavaliers": (50, 32),
    "2018 Dallas Mavericks": (24, 58), "2018 Denver Nuggets": (46, 36), "2018 Detroit Pistons": (39, 43),
    "2018 Golden State Warriors": (58, 24), "2018 Houston Rockets": (65, 17), "2018 Indiana Pacers": (48, 34),
    "2018 Los Angeles Clippers": (42, 40), "2018 Los Angeles Lakers": (35, 47), "2018 Memphis Grizzlies": (22, 60),
    "2018 Miami Heat": (44, 38), "2018 Milwaukee Bucks": (44, 38), "2018 Minnesota Timberwolves": (47, 35),
    "2018 New Orleans Pelicans": (48, 34), "2018 New York Knicks": (29, 53), "2018 Oklahoma City Thunder": (48, 34),
    "2018 Orlando Magic": (25, 57), "2018 Philadelphia 76ers": (52, 30), "2018 Phoenix Suns": (21, 61),
    "2018 Portland Trail Blazers": (49, 33), "2018 Sacramento Kings": (27, 55), "2018 San Antonio Spurs": (47, 35),
    "2018 Toronto Raptors": (59, 23), "2018 Utah Jazz": (48, 34), "2018 Washington Wizards": (43, 39),
    "2019 Brooklyn Nets": (42, 40), "2019 Golden State Warriors": (57, 25), "2019 Philadelphia 76ers": (51, 31),
    "2019 Toronto Raptors": (58, 24), "2020 Boston Celtics": (48, 24), "2020 Houston Rockets": (44, 28),
    "2020 Los Angeles Lakers": (52, 19), "2020 Miami Heat": (44, 29), "2021 Atlanta Hawks": (41, 31),
    "2021 Brooklyn Nets": (48, 24), "2021 Los Angeles Clippers": (47, 25), "2021 Milwaukee Bucks": (46, 26),
    "2021 Phoenix Suns": (51, 21), "2021 Portland Trail Blazers": (42, 30), "2021 Utah Jazz": (52, 20),
    "2022 Boston Celtics": (51, 31), "2022 Brooklyn Nets": (44, 38), "2022 Dallas Mavericks": (52, 30),
    "2022 Golden State Warriors": (53, 29), "2022 Memphis Grizzlies": (56, 26), "2023 Denver Nuggets": (53, 29),
    "2023 Los Angeles Lakers": (43, 39), "2023 Miami Heat": (44, 38), "2023 Sacramento Kings": (48, 34),
    "2024 Boston Celtics": (64, 18), "2024 Dallas Mavericks": (50, 32), "2024 Denver Nuggets": (57, 25),
    "2024 Los Angeles Clippers": (51, 31), "2024 Minnesota Timberwolves": (56, 26), "2024 New Orleans Pelicans": (49, 33),
    "2024 Oklahoma City Thunder": (57, 25), "2024 Orlando Magic": (47, 35), "2025 Indiana Pacers": (50, 32),
    "2026 Detroit Pistons": (60, 22), "2026 Boston Celtics": (56, 26), "2026 New York Knicks": (53, 29),
    "2026 Cleveland Cavaliers": (52, 30), "2026 Toronto Raptors": (46, 36), "2026 Atlanta Hawks": (46, 36),
    "2026 Philadelphia 76ers": (45, 37), "2026 Orlando Magic": (45, 37), "2026 Charlotte Hornets": (44, 38),
    "2026 Miami Heat": (43, 39), "2026 Milwaukee Bucks": (32, 50), "2026 Chicago Bulls": (31, 51),
    "2026 Brooklyn Nets": (20, 62), "2026 Indiana Pacers": (19, 63), "2026 Washington Wizards": (17, 65),
    "2026 Oklahoma City Thunder": (64, 18), "2026 San Antonio Spurs": (62, 20), "2026 Denver Nuggets": (54, 28),
    "2026 Los Angeles Lakers": (53, 29), "2026 Houston Rockets": (52, 30), "2026 Minnesota Timberwolves": (49, 33),
    "2026 Phoenix Suns": (45, 37), "2026 Portland Trail Blazers": (42, 40), "2026 Los Angeles Clippers": (42, 40),
    "2026 Golden State Warriors": (37, 45), "2026 New Orleans Pelicans": (26, 56), "2026 Dallas Mavericks": (26, 56),
    "2026 Memphis Grizzlies": (25, 57), "2026 Sacramento Kings": (22, 60), "2026 Utah Jazz": (22, 60),
}


def real_wins_per_82(team_name: str) -> Optional[float]:
    """Real win percentage scaled to an 82-game season, or None when the team has no real record."""
    record = REAL_RECORDS.get(team_name)
    if not record:
        return None
    wins, losses = record
    return 82.0 * wins / (wins + losses)
