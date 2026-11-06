# 2022-23 teams: real stat, rating, reason

The 26 teams in `teams/teams_2023.py` built from real data (any hand-built teams are unchanged). Source: Basketball-Reference 2022-23 per-game, advanced and shooting tables. Ratings were derived from the real numbers, then calibrated by simulating full 82-game seasons until each player's per-minute line matched the real one. Ratings of 0.95 or more, and 0.30 or less, are flagged with their reason.

## 2023 Atlanta Hawks

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Dejounte Murray | SG | 32.6 | 20.5 pts, 5.2 reb, 6.1 ast; 3P 34.4% on 5.2; rim 69.7%; mid 46.8%; FT 83.2%; USG 24%, AST% 24 | 0.80 / 0.89 / 0.88 / 0.70 / 0.83 | 0.35 / 0.79 |  |
| Trae Young | PG | 31.0 | 26.2 pts, 3.0 reb, 10.2 ast; 3P 33.5% on 6.3; rim 54.6%; mid 47.5%; FT 88.6%; USG 33%, AST% 42 | 0.92 / 0.92 / 0.92 / 0.49 / 0.88 | 0.47 / 0.95 | playmaking 0.95 (AST% 42, league-best passer) |
| De'Andre Hunter | SF | 27.5 | 15.4 pts, 4.3 reb, 1.4 ast; 3P 35.0% on 4.3; rim 65.1%; mid 51.0%; FT 82.6%; USG 20%, AST% 6 | 0.79 / 0.95 / 0.90 / 0.93 / 0.82 | 0.21 / 0.33 | mid 0.95 (mid FG 51.0%) |
| John Collins | PF | 25.6 | 13.1 pts, 6.5 reb, 1.2 ast; 3P 29.2% on 3.4; rim 79.5%; mid 48.7%; FT 80.3%; USG 17%, AST% 5 | 0.77 / 0.85 / 0.92 / 0.93 / 0.82 | 0.14 / 0.48 |  |
| Clint Capela | C | 21.9 | 12.0 pts, 11.1 reb, 0.9 ast; 3P 0.0% on 0.0; rim 72.5%; mid 25.0%; FT 60.3%; USG 16%, AST% 5 | 0.23 / 0.60 / 0.95 / 0.93 / 0.61 | 0.28 / 0.46 | rim 0.95 (72.5% at the rim); oreb 0.97 (ORB% 16.1); dreb 0.97 (DRB% 29.4); 3PT 0.23 (rarely shoots threes) |
| Saddiq Bey | SF | 20.4 | 13.8 pts, 4.7 reb, 1.5 ast; 3P 36.1% on 5.4; rim 64.3%; mid 27.7%; FT 86.1%; USG 20%, AST% 8 | 0.85 / 0.77 / 0.89 / 0.77 / 0.85 | 0.20 / 0.39 |  |
| Bogdan Bogdanović | SG | 23.3 | 14.0 pts, 3.0 reb, 2.8 ast; 3P 40.6% on 6.7; rim 64.2%; mid 42.2%; FT 83.1%; USG 20%, AST% 13 | 0.95 / 0.85 / 0.90 / 0.59 / 0.77 | 0.19 / 0.56 |  |
| Onyeka Okongwu | C | 18.2 | 9.9 pts, 7.2 reb, 1.0 ast; 3P 30.8% on 0.2; rim 76.4%; mid 46.8%; FT 78.1%; USG 15%, AST% 6 | 0.33 / 0.85 / 0.94 / 0.93 / 0.77 | 0.06 / 0.49 |  |
| AJ Griffin | SF | 14.6 | 8.9 pts, 2.1 reb, 1.0 ast; 3P 39.0% on 3.6; rim 63.0%; mid 47.8%; FT 89.4%; USG 18%, AST% 7 | 0.90 / 0.85 / 0.90 / 0.81 / 0.79 | 0.11 / 0.39 |  |
| Jalen Johnson | SF | 10.3 | 5.6 pts, 4.0 reb, 1.2 ast; 3P 28.8% on 1.5; rim 72.2%; mid 39.2%; FT 62.8%; USG 16%, AST% 10 | 0.59 / 0.85 / 0.90 / 0.93 / 0.67 | 0.23 / 0.55 |  |
| Aaron Holiday | PG | 9.0 | 3.9 pts, 1.2 reb, 1.4 ast; 3P 40.9% on 1.4; rim 61.2%; mid 39.1%; FT 84.4%; USG 13%, AST% 13 | 0.85 / 0.83 / 0.83 / 0.40 / 0.76 | 0.10 / 0.61 |  |
| Garrison Mathews | SG | 5.6 | 4.8 pts, 1.3 reb, 0.5 ast; 3P 35.0% on 3.3; rim 66.7%; mid 50.0%; FT 90.6%; USG 15%, AST% 5 | 0.92 / 0.60 / 0.83 / 0.47 / 0.79 | 0.19 / 0.10 |  |

## 2023 Boston Celtics

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Jayson Tatum | SF | 33.0 | 30.1 pts, 8.8 reb, 4.6 ast; 3P 35.0% on 9.3; rim 73.8%; mid 37.7%; FT 85.4%; USG 33%, AST% 21 | 0.92 / 0.85 / 0.92 / 0.90 / 0.84 | 0.30 / 0.66 | dreb 0.97 (DRB% 22.5) |
| Jaylen Brown | SF | 31.8 | 26.6 pts, 6.9 reb, 3.5 ast; 3P 33.5% on 7.3; rim 74.1%; mid 47.7%; FT 76.5%; USG 31%, AST% 16 | 0.86 / 0.92 / 0.95 / 0.93 / 0.75 | 0.29 / 0.56 | rim 0.95 (74.1% at the rim) |
| Marcus Smart | PG | 27.5 | 11.5 pts, 3.2 reb, 6.3 ast; 3P 33.6% on 5.6; rim 75.0%; mid 38.3%; FT 74.6%; USG 18%, AST% 26 | 0.81 / 0.79 / 0.85 / 0.53 / 0.74 | 0.34 / 0.94 |  |
| Al Horford | C | 25.7 | 9.8 pts, 6.2 reb, 3.0 ast; 3P 44.6% on 5.2; rim 67.2%; mid 25.0%; FT 71.4%; USG 12%, AST% 13 | 0.95 / 0.60 / 0.80 / 0.60 / 0.72 | 0.07 / 0.66 | 3PT 0.95 (44.6% from three on 5.2 attempts, elite volume) |
| Derrick White | SG | 23.3 | 12.4 pts, 3.5 reb, 3.9 ast; 3P 38.1% on 4.8; rim 72.0%; mid 47.4%; FT 87.5%; USG 18%, AST% 19 | 0.85 / 0.80 / 0.83 / 0.74 / 0.87 | 0.27 / 0.72 |  |
| Robert Williams | C | 18.3 | 8.0 pts, 8.4 reb, 1.4 ast; 3P 0.0% on 0.0; rim 87.9%; mid 33.3%; FT 61.0%; USG 12%, AST% 8 | 0.23 / 0.60 / 0.90 / 0.93 / 0.68 | 0.10 / 0.54 | oreb 0.97 (ORB% 14.0); dreb 0.97 (DRB% 24.5); 3PT 0.23 (rarely shoots threes) |
| Grant Williams | PF | 20.8 | 8.1 pts, 4.6 reb, 1.7 ast; 3P 39.5% on 3.7; rim 73.8%; mid 36.0%; FT 77.0%; USG 13%, AST% 8 | 0.88 / 0.55 / 0.79 / 0.59 / 0.75 | 0.05 / 0.54 |  |
| Mike Muscala | C | 11.3 | 6.1 pts, 3.2 reb, 0.8 ast; 3P 39.1% on 3.3; rim 63.0%; mid 50.0%; FT 76.9%; USG 15%, AST% 7 | 0.86 / 0.80 / 0.90 / 0.58 / 0.74 | 0.05 / 0.31 |  |
| Sam Hauser | SF | 11.2 | 6.4 pts, 2.5 reb, 0.9 ast; 3P 41.8% on 4.2; rim 83.9%; mid 36.8%; FT 70.6%; USG 15%, AST% 8 | 0.92 / 0.60 / 0.84 / 0.47 / 0.72 | 0.04 / 0.16 |  |
| Payton Pritchard | PG | 8.8 | 5.6 pts, 1.8 reb, 1.3 ast; 3P 36.4% on 3.2; rim 61.5%; mid 38.1%; FT 75.0%; USG 20%, AST% 14 | 0.92 / 0.79 / 0.85 / 0.41 / 0.72 | 0.15 / 0.53 |  |
| Malcolm Brogdon | PG | 20.9 | 14.9 pts, 4.2 reb, 3.7 ast; 3P 44.4% on 4.4; rim 61.3%; mid 49.5%; FT 87.0%; USG 23%, AST% 22 | 0.92 / 0.81 / 0.85 / 0.52 / 0.88 | 0.27 / 0.66 |  |
| Luke Kornet | C | 7.4 | 3.8 pts, 2.8 reb, 0.8 ast; 3P 23.1% on 0.2; rim 77.3%; mid 28.6%; FT 82.1%; USG 12%, AST% 9 | 0.35 / 0.60 / 0.90 / 0.90 / 0.75 | 0.10 / 0.56 |  |

## 2023 Brooklyn Nets

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Spencer Dinwiddie | SG | 30.4 | 17.3 pts, 3.5 reb, 6.5 ast; 3P 36.9% on 6.2; rim 64.6%; mid 42.3%; FT 81.2%; USG 22%, AST% 28 | 0.92 / 0.76 / 0.82 / 0.53 / 0.82 | 0.22 / 0.66 |  |
| Mikal Bridges | SG | 29.2 | 20.1 pts, 4.4 reb, 3.3 ast; 3P 38.2% on 5.3; rim 69.3%; mid 44.2%; FT 89.5%; USG 23%, AST% 14 | 0.92 / 0.92 / 0.92 / 0.85 / 0.89 | 0.14 / 0.43 |  |
| Cameron Johnson | PF | 25.5 | 15.5 pts, 4.4 reb, 1.9 ast; 3P 40.4% on 6.1; rim 69.1%; mid 44.3%; FT 84.2%; USG 21%, AST% 10 | 0.95 / 0.85 / 0.90 / 0.85 / 0.84 | 0.12 / 0.57 | 3PT 0.95 (40.4% from three on 6.1 attempts, elite volume) |
| Nic Claxton | C | 24.5 | 12.6 pts, 9.2 reb, 1.9 ast; 3P 0.0% on 0.0; rim 80.5%; mid 46.2%; FT 54.1%; USG 15%, AST% 9 | 0.20 / 0.60 / 0.95 / 0.95 / 0.56 | 0.11 / 0.56 | rim 0.95 (80.5% at the rim); dunk 0.95 (191 dunks); block 0.95 (BLK% 7.1); interior D 0.95 (DBPM +2.2); 3PT 0.20 (rarely shoots threes) |
| Dorian Finney-Smith | PF | 22.2 | 8.3 pts, 4.8 reb, 1.5 ast; 3P 33.7% on 5.1; rim 64.2%; mid 20.0%; FT 76.3%; USG 13%, AST% 7 | 0.86 / 0.54 / 0.81 / 0.73 / 0.74 | 0.10 / 0.50 |  |
| Ben Simmons | PG | 20.8 | 6.9 pts, 6.3 reb, 6.1 ast; 3P 0.0% on 0.0; rim 71.3%; mid 43.6%; FT 43.9%; USG 14%, AST% 31 | 0.22 / 0.50 / 0.72 / 0.73 / 0.45 | 0.22 / 0.95 | playmaking 0.95 (AST% 31, league-best passer); perimeter D 0.95 (DBPM +2.6, 2.4% steals); 3PT 0.22 (rarely shoots threes) |
| Royce O'Neale | SF | 26.5 | 8.8 pts, 5.0 reb, 3.7 ast; 3P 38.9% on 5.5; rim 48.9%; mid 16.7%; FT 72.5%; USG 14%, AST% 15 | 0.91 / 0.38 / 0.72 / 0.37 / 0.72 | 0.09 / 0.67 |  |
| Joe Harris | SF | 15.1 | 7.6 pts, 2.2 reb, 1.4 ast; 3P 42.6% on 4.5; rim 71.4%; mid 39.4%; FT 64.3%; USG 14%, AST% 9 | 0.92 / 0.60 / 0.85 / 0.40 / 0.70 | 0.04 / 0.33 |  |
| Edmond Sumner | SG | 9.1 | 7.1 pts, 1.4 reb, 1.3 ast; 3P 35.6% on 1.6; rim 62.4%; mid 48.0%; FT 91.7%; USG 22%, AST% 13 | 0.85 / 0.85 / 0.90 / 0.64 / 0.92 | 0.18 / 0.44 |  |
| Seth Curry | SG | 14.4 | 9.2 pts, 1.6 reb, 1.6 ast; 3P 40.5% on 3.8; rim 61.5%; mid 52.2%; FT 92.7%; USG 19%, AST% 12 | 0.92 / 0.92 / 0.90 / 0.47 / 0.80 | 0.12 / 0.47 |  |
| Cam Thomas | SG | 11.4 | 10.6 pts, 1.6 reb, 1.4 ast; 3P 38.3% on 2.3; rim 68.4%; mid 38.6%; FT 86.8%; USG 28%, AST% 13 | 0.92 / 0.92 / 0.90 / 0.61 / 0.87 | 0.15 / 0.31 |  |
| Yuta Watanabe | SF | 10.9 | 5.6 pts, 2.4 reb, 0.8 ast; 3P 44.4% on 2.3; rim 76.9%; mid 38.5%; FT 72.3%; USG 13%, AST% 7 | 0.92 / 0.76 / 0.86 / 0.68 / 0.72 | 0.05 / 0.32 |  |

## 2023 Charlotte Hornets

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Terry Rozier | SG | 30.4 | 21.1 pts, 4.1 reb, 5.1 ast; 3P 32.7% on 8.0; rim 62.2%; mid 44.5%; FT 80.9%; USG 27%, AST% 23 | 0.77 / 0.76 / 0.82 / 0.40 / 0.80 | 0.38 / 0.75 |  |
| LaMelo Ball | PG | 30.2 | 23.3 pts, 6.5 reb, 8.4 ast; 3P 37.6% on 10.6; rim 59.8%; mid 42.5%; FT 83.6%; USG 30%, AST% 39 | 0.91 / 0.84 / 0.88 / 0.25 / 0.84 | 0.36 / 0.90 |  |
| P.J. Washington | PF | 27.3 | 15.7 pts, 4.9 reb, 2.4 ast; 3P 34.8% on 5.9; rim 69.1%; mid 37.0%; FT 73.0%; USG 21%, AST% 11 | 0.79 / 0.82 / 0.88 / 0.81 / 0.74 | 0.26 / 0.60 |  |
| Gordon Hayward | SF | 26.2 | 14.7 pts, 4.3 reb, 4.1 ast; 3P 32.5% on 3.2; rim 76.3%; mid 45.5%; FT 81.1%; USG 20%, AST% 19 | 0.75 / 0.90 / 0.87 / 0.76 / 0.79 | 0.31 / 0.79 |  |
| Kelly Oubre Jr. | SF | 27.0 | 20.3 pts, 5.2 reb, 1.1 ast; 3P 31.9% on 7.1; rim 66.0%; mid 45.7%; FT 76.0%; USG 26%, AST% 6 | 0.82 / 0.85 / 0.92 / 0.92 / 0.76 | 0.30 / 0.10 |  |
| Svi Mykhailiuk | SF | 16.9 | 6.9 pts, 1.7 reb, 1.7 ast; 3P 42.4% on 3.1; rim 66.7%; mid 40.0%; FT 66.7%; USG 19%, AST% 16 | 0.85 / 0.74 / 0.83 / 0.60 / 0.70 | 0.07 / 0.60 |  |
| Mark Williams | C | 13.8 | 9.0 pts, 7.1 reb, 0.4 ast; 3P 30.0% on 0.0; rim 75.1%; mid 46.7%; FT 69.1%; USG 17%, AST% 3 | 0.28 / 0.67 / 0.86 / 0.90 / 0.71 | 0.16 / 0.10 | 3PT 0.28 (rarely shoots threes) |
| Dennis Smith Jr. | PG | 20.1 | 8.8 pts, 3.1 reb, 4.8 ast; 3P 21.6% on 2.1; rim 66.4%; mid 31.0%; FT 73.6%; USG 18%, AST% 26 | 0.50 / 0.81 / 0.92 / 0.79 / 0.73 | 0.34 / 0.95 |  |
| Théo Maledon | PG | 13.9 | 6.7 pts, 2.8 reb, 3.5 ast; 3P 29.5% on 2.2; rim 58.2%; mid 48.8%; FT 85.1%; USG 17%, AST% 24 | 0.62 / 0.85 / 0.90 / 0.46 / 0.78 | 0.33 / 0.86 |  |
| Bryce McGowens | SG | 11.8 | 5.3 pts, 2.0 reb, 1.2 ast; 3P 32.5% on 1.7; rim 57.6%; mid 17.6%; FT 75.0%; USG 15%, AST% 9 | 0.85 / 0.78 / 0.90 / 0.67 / 0.73 | 0.06 / 0.46 |  |
| Nick Richards | C | 13.3 | 8.2 pts, 6.4 reb, 0.6 ast; 3P 100.0% on 0.0; rim 74.1%; mid 44.2%; FT 74.9%; USG 16%, AST% 4 | 0.31 / 0.58 / 0.89 / 0.88 / 0.76 | 0.29 / 0.10 |  |
| JT Thor | PF | 9.1 | 3.8 pts, 2.2 reb, 0.5 ast; 3P 31.7% on 1.8; rim 56.5%; mid 36.7%; FT 70.2%; USG 13%, AST% 5 | 0.51 / 0.78 / 0.90 / 0.69 / 0.71 | 0.08 / 0.10 |  |

## 2023 Chicago Bulls

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| DeMar DeRozan | SF | 33.8 | 24.5 pts, 4.7 reb, 5.1 ast; 3P 32.4% on 1.9; rim 73.5%; mid 47.7%; FT 87.2%; USG 28%, AST% 22 | 0.66 / 0.92 / 0.92 / 0.93 / 0.86 | 0.26 / 0.68 |  |
| Zach LaVine | SG | 33.4 | 24.8 pts, 4.4 reb, 4.2 ast; 3P 37.5% on 7.1; rim 69.3%; mid 43.2%; FT 84.8%; USG 28%, AST% 19 | 0.92 / 0.92 / 0.92 / 0.93 / 0.86 | 0.26 / 0.55 |  |
| Nikola Vučević | C | 30.6 | 17.6 pts, 11.0 reb, 3.2 ast; 3P 34.9% on 4.2; rim 70.4%; mid 46.0%; FT 83.5%; USG 22%, AST% 15 | 0.90 / 0.92 / 0.92 / 0.93 / 0.83 | 0.14 / 0.69 |  |
| Patrick Beverley | SG | 23.6 | 6.2 pts, 3.7 reb, 2.9 ast; 3P 33.5% on 3.6; rim 63.6%; mid 58.3%; FT 72.3%; USG 11%, AST% 13 | 0.83 / 0.46 / 0.77 / 0.33 / 0.72 | 0.03 / 0.66 |  |
| Patrick Williams | PF | 24.5 | 10.2 pts, 4.0 reb, 1.2 ast; 3P 41.5% on 3.4; rim 64.0%; mid 42.3%; FT 85.7%; USG 16%, AST% 6 | 0.92 / 0.91 / 0.92 / 0.83 / 0.80 | 0.10 / 0.49 |  |
| Ayo Dosunmu | SG | 22.2 | 8.6 pts, 2.8 reb, 2.6 ast; 3P 31.2% on 2.4; rim 67.9%; mid 42.9%; FT 80.5%; USG 15%, AST% 13 | 0.66 / 0.85 / 0.92 / 0.86 / 0.76 | 0.23 / 0.66 |  |
| Alex Caruso | PG | 19.3 | 5.6 pts, 2.9 reb, 2.9 ast; 3P 36.4% on 2.3; rim 69.9%; mid 40.0%; FT 80.8%; USG 11%, AST% 15 | 0.84 / 0.79 / 0.82 / 0.53 / 0.76 | 0.03 / 0.71 | perimeter D 0.95 (DBPM +3.3, 3.0% steals) |
| Coby White | SG | 19.2 | 9.7 pts, 2.8 reb, 2.8 ast; 3P 37.2% on 4.6; rim 67.2%; mid 44.6%; FT 87.1%; USG 18%, AST% 16 | 0.92 / 0.85 / 0.90 / 0.65 / 0.79 | 0.15 / 0.65 |  |
| Javonte Green | SF | 10.8 | 5.2 pts, 2.7 reb, 0.7 ast; 3P 37.1% on 1.1; rim 75.0%; mid 0.0%; FT 66.7%; USG 14%, AST% 6 | 0.85 / 0.60 / 0.90 / 0.93 / 0.70 | 0.04 / 0.20 |  |
| Derrick Jones Jr. | PF | 9.8 | 5.0 pts, 2.4 reb, 0.5 ast; 3P 33.8% on 1.3; rim 62.7%; mid 50.0%; FT 73.8%; USG 14%, AST% 5 | 0.60 / 0.60 / 0.90 / 0.93 / 0.74 | 0.12 / 0.28 |  |
| Andre Drummond | C | 8.7 | 6.0 pts, 6.7 reb, 0.5 ast; 3P 0.0% on 0.0; rim 66.0%; mid 0.0%; FT 53.6%; USG 21%, AST% 6 | 0.20 / 0.60 / 0.92 / 0.93 / 0.55 | 0.17 / 0.17 | steal 0.95 (STL% 2.6); oreb 0.97 (ORB% 18.7); dreb 0.97 (DRB% 40.2); 3PT 0.20 (rarely shoots threes) |
| Terry Taylor | PF | 4.1 | 2.9 pts, 1.5 reb, 0.3 ast; 3P 26.3% on 0.6; rim 76.5%; mid 25.1%; FT 54.5%; USG 14%, AST% 5 | 0.47 / 0.60 / 0.85 / 0.58 / 0.70 | 0.11 / 0.10 |  |

## 2023 Cleveland Cavaliers

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Donovan Mitchell | SG | 33.1 | 28.3 pts, 4.2 reb, 4.4 ast; 3P 38.6% on 9.3; rim 70.0%; mid 45.5%; FT 86.7%; USG 32%, AST% 21 | 0.92 / 0.92 / 0.92 / 0.93 / 0.88 | 0.24 / 0.56 |  |
| Darius Garland | PG | 32.8 | 21.6 pts, 2.7 reb, 7.8 ast; 3P 41.0% on 6.0; rim 61.5%; mid 44.8%; FT 86.3%; USG 27%, AST% 34 | 0.95 / 0.83 / 0.83 / 0.48 / 0.86 | 0.31 / 0.83 | 3PT 0.95 (41.0% from three on 6.0 attempts, elite volume) |
| Evan Mobley | PF | 31.5 | 16.2 pts, 9.0 reb, 2.8 ast; 3P 21.6% on 1.3; rim 81.7%; mid 38.3%; FT 67.4%; USG 20%, AST% 12 | 0.34 / 0.71 / 0.89 / 0.93 / 0.67 | 0.17 / 0.64 |  |
| Jarrett Allen | C | 29.3 | 14.3 pts, 9.8 reb, 1.7 ast; 3P 10.0% on 0.1; rim 76.5%; mid 45.4%; FT 73.3%; USG 16%, AST% 8 | 0.30 / 0.74 / 0.89 / 0.93 / 0.74 | 0.23 / 0.52 | 3PT 0.30 (rarely shoots threes) |
| Isaac Okoro | SF | 17.3 | 6.4 pts, 2.5 reb, 1.1 ast; 3P 36.3% on 2.3; rim 68.7%; mid 66.7%; FT 75.7%; USG 12%, AST% 7 | 0.86 / 0.60 / 0.90 / 0.93 / 0.74 | 0.04 / 0.39 |  |
| Caris LeVert | SG | 26.6 | 12.1 pts, 3.8 reb, 3.9 ast; 3P 39.2% on 4.4; rim 63.8%; mid 29.3%; FT 72.2%; USG 19%, AST% 18 | 0.92 / 0.67 / 0.81 / 0.69 / 0.77 | 0.20 / 0.68 |  |
| Lamar Stevens | SF | 13.7 | 5.3 pts, 3.4 reb, 0.5 ast; 3P 31.6% on 1.5; rim 65.3%; mid 40.8%; FT 70.2%; USG 14%, AST% 4 | 0.64 / 0.85 / 0.90 / 0.80 / 0.71 | 0.06 / 0.10 |  |
| Dean Wade | PF | 15.8 | 4.7 pts, 3.5 reb, 0.8 ast; 3P 35.4% on 2.9; rim 75.9%; mid 20.1%; FT 65.2%; USG 10%, AST% 5 | 0.82 / 0.60 / 0.82 / 0.58 / 0.71 | 0.02 / 0.48 |  |
| Ricky Rubio | PG | 12.8 | 5.2 pts, 2.1 reb, 3.5 ast; 3P 25.6% on 2.5; rim 40.7%; mid 48.0%; FT 80.0%; USG 18%, AST% 27 | 0.72 / 0.66 / 0.73 / 0.28 / 0.80 | 0.26 / 0.72 |  |
| Robin Lopez | C | 4.8 | 3.0 pts, 1.4 reb, 0.5 ast; 3P 50.0% on 0.1; rim 82.6%; mid 74.9%; FT 77.8%; USG 16%, AST% 9 | 0.33 / 0.60 / 0.89 / 0.53 / 0.73 | 0.14 / 0.10 |  |
| Cedi Osman | SF | 15.6 | 8.7 pts, 2.3 reb, 1.5 ast; 3P 37.2% on 4.1; rim 73.2%; mid 33.6%; FT 69.4%; USG 18%, AST% 11 | 0.84 / 0.60 / 0.90 / 0.64 / 0.71 | 0.09 / 0.56 |  |
| Raul Neto | PG | 6.7 | 3.3 pts, 1.0 reb, 1.6 ast; 3P 28.6% on 0.9; rim 71.1%; mid 77.1%; FT 91.2%; USG 13%, AST% 21 | 0.61 / 0.85 / 0.85 / 0.40 / 0.78 | 0.22 / 0.73 |  |

## 2023 Dallas Mavericks

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Kyrie Irving | SG | 36.0 | 27.1 pts, 5.1 reb, 5.5 ast; 3P 37.9% on 8.3; rim 72.4%; mid 52.7%; FT 90.5%; USG 29%, AST% 25 | 0.89 / 0.95 / 0.92 / 0.59 / 0.90 | 0.36 / 0.73 | mid 0.95 (mid FG 52.7%) |
| Luka Dončić | PG | 33.6 | 32.4 pts, 8.6 reb, 8.0 ast; 3P 34.2% on 8.2; rim 74.5%; mid 46.2%; FT 74.2%; USG 38%, AST% 42 | 0.72 / 0.92 / 0.95 / 0.71 / 0.73 | 0.59 / 0.93 | rim 0.95 (74.5% at the rim) |
| Dwight Powell | C | 14.7 | 6.7 pts, 4.2 reb, 0.9 ast; 3P 0.0% on 0.1; rim 79.1%; mid 24.4%; FT 66.7%; USG 13%, AST% 7 | 0.27 / 0.60 / 0.92 / 0.93 / 0.64 | 0.06 / 0.51 | foul draw 0.95 (FTA per FGA 0.63); 3PT 0.27 (rarely shoots threes) |
| Reggie Bullock | SF | 26.6 | 7.2 pts, 3.6 reb, 1.4 ast; 3P 38.0% on 5.1; rim 75.0%; mid 33.3%; FT 70.3%; USG 10%, AST% 6 | 0.86 / 0.60 / 0.85 / 0.43 / 0.71 | 0.03 / 0.47 |  |
| Tim Hardaway Jr. | SF | 26.6 | 14.4 pts, 3.5 reb, 1.8 ast; 3P 38.5% on 7.7; rim 54.3%; mid 38.9%; FT 77.0%; USG 21%, AST% 9 | 0.91 / 0.74 / 0.74 / 0.54 / 0.76 | 0.29 / 0.54 |  |
| Christian Wood | C | 21.7 | 16.6 pts, 7.3 reb, 1.8 ast; 3P 37.6% on 4.2; rim 69.7%; mid 38.5%; FT 77.2%; USG 26%, AST% 12 | 0.85 / 0.81 / 0.86 / 0.90 / 0.78 | 0.31 / 0.62 |  |
| Josh Green | SG | 21.5 | 9.1 pts, 3.0 reb, 1.7 ast; 3P 40.2% on 2.8; rim 78.0%; mid 46.4%; FT 72.3%; USG 15%, AST% 10 | 0.90 / 0.85 / 0.90 / 0.93 / 0.72 | 0.09 / 0.53 |  |
| Maxi Kleber | PF | 20.9 | 5.9 pts, 3.6 reb, 1.4 ast; 3P 34.8% on 3.0; rim 72.5%; mid 55.6%; FT 71.1%; USG 10%, AST% 8 | 0.81 / 0.49 / 0.73 / 0.65 / 0.72 | 0.03 / 0.52 |  |
| Justin Holiday | SF | 12.0 | 4.5 pts, 1.2 reb, 0.9 ast; 3P 32.2% on 3.1; rim 70.0%; mid 29.7%; FT 62.5%; USG 14%, AST% 8 | 0.81 / 0.64 / 0.77 / 0.59 / 0.71 | 0.09 / 0.52 |  |
| Jaden Hardy | SG | 10.5 | 8.8 pts, 1.8 reb, 1.4 ast; 3P 40.4% on 3.3; rim 54.8%; mid 31.6%; FT 82.3%; USG 26%, AST% 15 | 0.92 / 0.77 / 0.78 / 0.59 / 0.82 | 0.32 / 0.58 |  |
| Frank Ntilikina | SG | 8.8 | 2.9 pts, 1.3 reb, 1.2 ast; 3P 25.4% on 1.4; rim 57.9%; mid 60.0%; FT 66.7%; USG 13%, AST% 13 | 0.58 / 0.76 / 0.82 / 0.40 / 0.70 | 0.11 / 0.56 |  |
| Dāvis Bertāns | PF | 7.1 | 4.6 pts, 1.2 reb, 0.5 ast; 3P 39.0% on 3.1; rim 76.9%; mid 100.0%; FT 86.7%; USG 16%, AST% 6 | 0.92 / 0.60 / 0.89 / 0.57 / 0.74 | 0.04 / 0.10 |  |

## 2023 Detroit Pistons

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Bojan Bogdanović | PF | 27.7 | 21.6 pts, 3.8 reb, 2.6 ast; 3P 41.1% on 6.0; rim 68.5%; mid 49.7%; FT 88.4%; USG 26%, AST% 14 | 0.95 / 0.92 / 0.90 / 0.86 / 0.89 | 0.20 / 0.64 | 3PT 0.95 (41.1% from three on 6.0 attempts, elite volume) |
| Jaden Ivey | SG | 26.6 | 16.3 pts, 3.9 reb, 5.2 ast; 3P 34.3% on 4.7; rim 58.4%; mid 42.6%; FT 74.7%; USG 25%, AST% 26 | 0.85 / 0.76 / 0.82 / 0.53 / 0.75 | 0.29 / 0.68 |  |
| Isaiah Stewart | C | 23.6 | 11.3 pts, 8.1 reb, 1.4 ast; 3P 32.7% on 4.1; rim 57.1%; mid 72.8%; FT 73.8%; USG 17%, AST% 7 | 0.82 / 0.60 / 0.90 / 0.90 / 0.73 | 0.17 / 0.52 |  |
| James Wiseman | C | 20.3 | 10.0 pts, 5.9 reb, 0.7 ast; 3P 20.0% on 0.4; rim 74.2%; mid 29.1%; FT 70.1%; USG 21%, AST% 6 | 0.20 / 0.85 / 0.90 / 0.93 / 0.70 | 0.14 / 0.48 | 3PT 0.20 (rarely shoots threes) |
| Killian Hayes | PG | 23.6 | 10.3 pts, 2.9 reb, 6.2 ast; 3P 28.0% on 3.8; rim 58.6%; mid 40.6%; FT 82.1%; USG 20%, AST% 32 | 0.76 / 0.70 / 0.72 / 0.51 / 0.80 | 0.25 / 0.85 |  |
| Marvin Bagley III | C | 18.6 | 12.0 pts, 6.4 reb, 0.9 ast; 3P 28.8% on 1.6; rim 77.9%; mid 43.4%; FT 75.0%; USG 20%, AST% 6 | 0.34 / 0.85 / 0.90 / 0.93 / 0.75 | 0.15 / 0.49 |  |
| Jalen Duren | C | 19.9 | 9.1 pts, 8.9 reb, 1.1 ast; 3P 0.0% on 0.0; rim 74.7%; mid 44.6%; FT 61.1%; USG 14%, AST% 7 | 0.23 / 0.57 / 0.88 / 0.91 / 0.63 | 0.26 / 0.51 | dreb 0.96 (DRB% 25.1); 3PT 0.23 (rarely shoots threes) |
| Isaiah Livers | PF | 18.1 | 6.7 pts, 2.7 reb, 0.8 ast; 3P 36.5% on 3.9; rim 84.2%; mid 43.9%; FT 82.1%; USG 12%, AST% 5 | 0.83 / 0.85 / 0.90 / 0.70 / 0.75 | 0.05 / 0.47 |  |
| Alec Burks | SG | 17.0 | 12.8 pts, 3.1 reb, 2.2 ast; 3P 41.4% on 4.7; rim 65.0%; mid 43.2%; FT 81.4%; USG 23%, AST% 16 | 0.92 / 0.80 / 0.85 / 0.41 / 0.80 | 0.19 / 0.46 |  |
| Eugene Omoruyi | SF | 16.9 | 7.0 pts, 2.8 reb, 0.7 ast; 3P 28.1% on 2.2; rim 70.7%; mid 16.7%; FT 68.0%; USG 19%, AST% 6 | 0.81 / 0.60 / 0.90 / 0.78 / 0.67 | 0.05 / 0.10 |  |
| Cory Joseph | PG | 14.8 | 6.9 pts, 1.7 reb, 3.5 ast; 3P 38.9% on 2.9; rim 64.5%; mid 40.0%; FT 79.2%; USG 15%, AST% 25 | 0.91 / 0.81 / 0.83 / 0.40 / 0.75 | 0.20 / 0.69 |  |
| Hamidou Diallo | SF | 12.9 | 9.3 pts, 3.4 reb, 1.0 ast; 3P 23.8% on 0.4; rim 76.5%; mid 43.9%; FT 58.8%; USG 22%, AST% 9 | 0.57 / 0.85 / 0.92 / 0.93 / 0.56 | 0.17 / 0.22 |  |

## 2023 Golden State Warriors

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Stephen Curry | PG | 30.5 | 29.4 pts, 6.1 reb, 6.3 ast; 3P 42.7% on 11.4; rim 76.0%; mid 47.8%; FT 91.5%; USG 31%, AST% 30 | 0.95 / 0.92 / 0.90 / 0.58 / 0.89 | 0.32 / 0.74 | 3PT 0.95 (42.7% from three on 11.4 attempts, elite volume) |
| Klay Thompson | SF | 28.6 | 21.9 pts, 4.2 reb, 2.4 ast; 3P 41.2% on 10.6; rim 69.4%; mid 39.3%; FT 87.9%; USG 26%, AST% 11 | 0.95 / 0.82 / 0.83 / 0.60 / 0.88 | 0.27 / 0.43 | 3PT 0.95 (41.2% from three on 10.6 attempts, elite volume) |
| Andrew Wiggins | SF | 27.7 | 17.1 pts, 5.0 reb, 2.3 ast; 3P 39.6% on 6.1; rim 71.1%; mid 40.2%; FT 61.1%; USG 22%, AST% 10 | 0.91 / 0.85 / 0.90 / 0.91 / 0.59 | 0.21 / 0.53 |  |
| Draymond Green | PF | 26.9 | 8.5 pts, 7.2 reb, 6.8 ast; 3P 30.5% on 1.8; rim 70.9%; mid 40.1%; FT 71.3%; USG 13%, AST% 28 | 0.57 / 0.85 / 0.90 / 0.90 / 0.72 | 0.09 / 0.95 | playmaking 0.95 (AST% 28, league-best passer) |
| Kevon Looney | C | 18.8 | 7.0 pts, 9.2 reb, 2.5 ast; 3P 0.0% on 0.0; rim 73.4%; mid 41.4%; FT 60.6%; USG 11%, AST% 14 | 0.23 / 0.62 / 0.83 / 0.80 / 0.64 | 0.10 / 0.67 | oreb 0.97 (ORB% 15.7); dreb 0.97 (DRB% 26.8); 3PT 0.23 (rarely shoots threes) |
| Jordan Poole | PG | 25.3 | 20.4 pts, 2.8 reb, 4.5 ast; 3P 33.6% on 7.8; rim 69.6%; mid 38.8%; FT 87.0%; USG 29%, AST% 22 | 0.82 / 0.84 / 0.88 / 0.68 / 0.87 | 0.35 / 0.68 |  |
| Donte DiVincenzo | SG | 21.3 | 9.4 pts, 4.5 reb, 3.5 ast; 3P 39.7% on 5.3; rim 56.7%; mid 29.2%; FT 81.7%; USG 15%, AST% 17 | 0.84 / 0.60 / 0.82 / 0.57 / 0.77 | 0.17 / 0.74 |  |
| Jonathan Kuminga | PF | 15.7 | 9.9 pts, 3.4 reb, 1.9 ast; 3P 37.0% on 2.2; rim 67.3%; mid 44.7%; FT 65.2%; USG 20%, AST% 13 | 0.70 / 0.85 / 0.92 / 0.93 / 0.67 | 0.21 / 0.65 |  |
| Anthony Lamb | SF | 14.2 | 6.7 pts, 3.5 reb, 1.5 ast; 3P 36.7% on 3.2; rim 80.9%; mid 33.7%; FT 76.7%; USG 14%, AST% 10 | 0.85 / 0.60 / 0.85 / 0.64 / 0.74 | 0.08 / 0.59 |  |
| Ty Jerome | SG | 13.1 | 6.9 pts, 1.8 reb, 3.0 ast; 3P 38.9% on 2.0; rim 73.9%; mid 49.1%; FT 92.7%; USG 15%, AST% 22 | 0.85 / 0.85 / 0.84 / 0.40 / 0.79 | 0.26 / 0.76 |  |
| JaMychal Green | PF | 9.4 | 6.4 pts, 3.6 reb, 0.9 ast; 3P 37.8% on 1.9; rim 70.1%; mid 36.4%; FT 77.6%; USG 18%, AST% 9 | 0.86 / 0.60 / 0.90 / 0.93 / 0.75 | 0.12 / 0.55 |  |
| Moses Moody | SG | 8.5 | 4.8 pts, 1.6 reb, 0.8 ast; 3P 36.3% on 2.1; rim 72.5%; mid 63.9%; FT 69.8%; USG 15%, AST% 8 | 0.86 / 0.60 / 0.85 / 0.70 / 0.71 | 0.07 / 0.37 |  |

## 2023 Houston Rockets

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Kevin Porter Jr. | PG | 35.0 | 19.2 pts, 5.3 reb, 5.7 ast; 3P 36.6% on 6.5; rim 71.1%; mid 46.8%; FT 78.4%; USG 24%, AST% 26 | 0.92 / 0.87 / 0.88 / 0.80 / 0.78 | 0.25 / 0.72 |  |
| Jalen Green | SG | 34.8 | 22.1 pts, 3.8 reb, 3.7 ast; 3P 33.8% on 7.3; rim 59.1%; mid 41.2%; FT 78.6%; USG 28%, AST% 17 | 0.90 / 0.84 / 0.88 / 0.78 / 0.79 | 0.24 / 0.47 |  |
| Jabari Smith Jr. | PF | 30.6 | 12.8 pts, 7.2 reb, 1.3 ast; 3P 30.7% on 4.9; rim 72.5%; mid 40.2%; FT 78.6%; USG 18%, AST% 6 | 0.77 / 0.81 / 0.85 / 0.79 / 0.81 | 0.21 / 0.49 |  |
| Alperen Şengün | C | 28.0 | 14.8 pts, 9.0 reb, 3.9 ast; 3P 33.3% on 0.8; rim 67.7%; mid 43.7%; FT 71.5%; USG 21%, AST% 21 | 0.39 / 0.78 / 0.88 / 0.88 / 0.70 | 0.19 / 0.84 | oreb 0.97 (ORB% 12.1); dreb 0.97 (DRB% 22.3) |
| KJ Martin | SF | 26.8 | 12.7 pts, 5.5 reb, 1.5 ast; 3P 31.5% on 2.6; rim 80.7%; mid 50.0%; FT 68.0%; USG 16%, AST% 8 | 0.78 / 0.60 / 0.95 / 0.93 / 0.69 | 0.16 / 0.44 | rim 0.95 (80.7% at the rim) |
| Jae'Sean Tate | SF | 19.4 | 9.1 pts, 3.8 reb, 2.7 ast; 3P 28.3% on 1.5; rim 61.4%; mid 30.8%; FT 72.5%; USG 19%, AST% 18 | 0.59 / 0.85 / 0.90 / 0.76 / 0.73 | 0.30 / 0.66 |  |
| Tari Eason | PF | 19.0 | 9.3 pts, 6.1 reb, 1.1 ast; 3P 34.3% on 2.1; rim 61.9%; mid 17.3%; FT 75.2%; USG 19%, AST% 7 | 0.86 / 0.54 / 0.83 / 0.84 / 0.73 | 0.14 / 0.52 |  |
| Daishen Nix | PG | 13.0 | 4.0 pts, 1.7 reb, 2.3 ast; 3P 28.6% on 2.5; rim 48.9%; mid 32.8%; FT 66.7%; USG 15%, AST% 19 | 0.75 / 0.60 / 0.78 / 0.47 / 0.70 | 0.27 / 0.71 |  |
| TyTy Washington Jr. | PG | 10.9 | 4.7 pts, 1.5 reb, 1.5 ast; 3P 23.8% on 2.6; rim 44.4%; mid 48.6%; FT 55.6%; USG 17%, AST% 15 | 0.72 / 0.85 / 0.90 / 0.62 / 0.69 | 0.21 / 0.62 |  |
| Usman Garuba | C | 9.8 | 3.0 pts, 4.1 reb, 0.9 ast; 3P 40.7% on 0.8; rim 62.5%; mid 0.0%; FT 61.7%; USG 10%, AST% 9 | 0.46 / 0.60 / 0.90 / 0.73 / 0.68 | 0.03 / 0.55 |  |
| Josh Christopher | SG | 9.2 | 5.8 pts, 1.1 reb, 1.1 ast; 3P 23.6% on 1.4; rim 68.5%; mid 43.1%; FT 75.0%; USG 22%, AST% 14 | 0.55 / 0.85 / 0.90 / 0.93 / 0.73 | 0.25 / 0.48 |  |
| Frank Kaminsky | C | 3.5 | 2.5 pts, 1.5 reb, 0.9 ast; 3P 39.4% on 0.9; rim 84.6%; mid 50.0%; FT 87.5%; USG 14%, AST% 18 | 0.35 / 0.85 / 0.90 / 0.63 / 0.74 | 0.26 / 0.77 |  |

## 2023 Indiana Pacers

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Tyrese Haliburton | PG | 30.0 | 20.7 pts, 3.7 reb, 10.4 ast; 3P 40.0% on 7.2; rim 73.3%; mid 45.3%; FT 87.1%; USG 24%, AST% 48 | 0.91 / 0.83 / 0.83 / 0.67 / 0.87 | 0.24 / 0.95 | playmaking 0.95 (AST% 48, league-best passer) |
| Myles Turner | C | 25.4 | 18.0 pts, 7.5 reb, 1.4 ast; 3P 37.3% on 4.0; rim 77.8%; mid 52.0%; FT 78.3%; USG 22%, AST% 8 | 0.86 / 0.85 / 0.92 / 0.93 / 0.79 | 0.17 / 0.52 | block 0.95 (BLK% 6.6) |
| Buddy Hield | SF | 27.2 | 16.8 pts, 5.0 reb, 2.8 ast; 3P 42.5% on 8.5; rim 68.8%; mid 41.7%; FT 82.2%; USG 21%, AST% 13 | 0.95 / 0.85 / 0.92 / 0.66 / 0.82 | 0.18 / 0.57 | 3PT 0.95 (42.5% from three on 8.5 attempts, elite volume) |
| Andrew Nembhard | SG | 23.4 | 9.5 pts, 2.7 reb, 4.5 ast; 3P 35.0% on 3.5; rim 71.6%; mid 39.9%; FT 79.0%; USG 16%, AST% 22 | 0.80 / 0.84 / 0.79 / 0.49 / 0.75 | 0.25 / 0.81 |  |
| Aaron Nesmith | SF | 20.5 | 10.1 pts, 3.7 reb, 1.3 ast; 3P 36.6% on 4.3; rim 63.9%; mid 44.9%; FT 83.8%; USG 17%, AST% 7 | 0.85 / 0.76 / 0.76 / 0.64 / 0.79 | 0.19 / 0.45 |  |
| Jordan Nwora | SF | 20.1 | 8.7 pts, 3.7 reb, 1.4 ast; 3P 40.8% on 3.4; rim 57.4%; mid 30.2%; FT 79.1%; USG 19%, AST% 10 | 0.92 / 0.70 / 0.76 / 0.66 / 0.74 | 0.13 / 0.53 |  |
| Jalen Smith | C | 14.2 | 9.4 pts, 5.8 reb, 1.0 ast; 3P 28.3% on 2.8; rim 76.1%; mid 29.6%; FT 75.9%; USG 21%, AST% 8 | 0.73 / 0.85 / 0.92 / 0.93 / 0.77 | 0.14 / 0.52 | block 0.95 (BLK% 4.0) |
| Chris Duarte | SF | 14.9 | 7.9 pts, 2.5 reb, 1.4 ast; 3P 31.6% on 3.8; rim 54.1%; mid 27.4%; FT 84.7%; USG 19%, AST% 10 | 0.79 / 0.71 / 0.73 / 0.51 / 0.78 | 0.18 / 0.49 |  |
| Bennedict Mathurin | SG | 24.4 | 16.7 pts, 4.1 reb, 1.5 ast; 3P 32.3% on 4.0; rim 62.5%; mid 35.4%; FT 82.8%; USG 25%, AST% 8 | 0.89 / 0.85 / 0.92 / 0.77 / 0.84 | 0.19 / 0.19 |  |
| Isaiah Jackson | C | 12.0 | 7.2 pts, 4.5 reb, 0.8 ast; 3P 14.3% on 0.2; rim 68.4%; mid 45.4%; FT 65.1%; USG 17%, AST% 7 | 0.26 / 0.69 / 0.90 / 0.90 / 0.65 | 0.26 / 0.51 | block 0.95 (BLK% 7.7); 3PT 0.26 (rarely shoots threes) |
| T.J. McConnell | PG | 15.7 | 8.7 pts, 3.1 reb, 5.3 ast; 3P 44.1% on 0.8; rim 64.2%; mid 48.6%; FT 85.3%; USG 19%, AST% 38 | 0.75 / 0.85 / 0.92 / 0.51 / 0.78 | 0.26 / 0.95 | playmaking 0.95 (AST% 38, league-best passer) |
| Oshae Brissett | PF | 12.2 | 6.1 pts, 3.4 reb, 0.7 ast; 3P 31.0% on 2.4; rim 55.8%; mid 18.3%; FT 71.7%; USG 16%, AST% 5 | 0.58 / 0.60 / 0.87 / 0.67 / 0.71 | 0.23 / 0.12 |  |

## 2023 Los Angeles Clippers

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Paul George | SF | 29.3 | 23.8 pts, 6.1 reb, 5.1 ast; 3P 37.1% on 7.6; rim 69.9%; mid 41.6%; FT 87.1%; USG 30%, AST% 24 | 0.92 / 0.87 / 0.88 / 0.83 / 0.87 | 0.32 / 0.78 |  |
| Kawhi Leonard | SF | 28.4 | 23.8 pts, 6.5 reb, 3.9 ast; 3P 41.6% on 4.8; rim 72.4%; mid 50.2%; FT 87.1%; USG 27%, AST% 20 | 0.92 / 0.93 / 0.87 / 0.85 / 0.85 | 0.30 / 0.71 |  |
| Russell Westbrook | PG | 24.7 | 15.9 pts, 5.8 reb, 7.5 ast; 3P 31.1% on 3.9; rim 63.2%; mid 37.5%; FT 65.6%; USG 28%, AST% 39 | 0.78 / 0.84 / 0.88 / 0.47 / 0.65 | 0.41 / 0.95 | playmaking 0.95 (AST% 39, league-best passer) |
| Ivica Zubac | C | 23.0 | 10.8 pts, 9.9 reb, 1.0 ast; 3P 0.0% on 0.0; rim 70.2%; mid 46.2%; FT 69.7%; USG 15%, AST% 5 | 0.28 / 0.54 / 0.83 / 0.89 / 0.69 | 0.31 / 0.47 | oreb 0.97 (ORB% 12.3); dreb 0.97 (DRB% 26.5); 3PT 0.28 (rarely shoots threes) |
| Marcus Morris | PF | 22.5 | 11.2 pts, 3.9 reb, 1.8 ast; 3P 36.4% on 4.7; rim 71.1%; mid 43.0%; FT 78.2%; USG 18%, AST% 9 | 0.81 / 0.89 / 0.87 / 0.59 / 0.78 | 0.17 / 0.55 |  |
| Eric Gordon | SG | 19.2 | 12.4 pts, 1.9 reb, 2.7 ast; 3P 37.1% on 5.2; rim 71.0%; mid 35.5%; FT 82.1%; USG 18%, AST% 13 | 0.88 / 0.60 / 0.87 / 0.43 / 0.79 | 0.22 / 0.63 |  |
| Terance Mann | SG | 17.4 | 8.8 pts, 3.5 reb, 2.3 ast; 3P 38.9% on 2.4; rim 76.9%; mid 41.5%; FT 78.0%; USG 15%, AST% 14 | 0.84 / 0.85 / 0.92 / 0.93 / 0.76 | 0.16 / 0.66 |  |
| Nicolas Batum | PF | 16.3 | 6.1 pts, 3.8 reb, 1.6 ast; 3P 39.1% on 4.1; rim 69.4%; mid 23.2%; FT 70.8%; USG 12%, AST% 9 | 0.84 / 0.60 / 0.84 / 0.58 / 0.72 | 0.02 / 0.57 |  |
| Mason Plumlee | C | 14.4 | 10.8 pts, 8.9 reb, 3.1 ast; 3P 30.0% on 0.0; rim 76.6%; mid 52.3%; FT 63.6%; USG 15%, AST% 17 | 0.25 / 0.59 / 0.92 / 0.91 / 0.65 | 0.31 / 0.76 | oreb 0.97 (ORB% 11.8); dreb 0.97 (DRB% 25.1); foul draw 0.96 (FTA per FGA 0.66); 3PT 0.25 (rarely shoots threes) |
| Norman Powell | SG | 20.4 | 17.0 pts, 2.9 reb, 1.8 ast; 3P 39.7% on 4.8; rim 68.4%; mid 40.0%; FT 81.2%; USG 26%, AST% 11 | 0.92 / 0.85 / 0.92 / 0.83 / 0.81 | 0.23 / 0.38 |  |
| Bones Hyland | PG | 13.4 | 11.8 pts, 2.5 reb, 3.1 ast; 3P 37.1% on 5.6; rim 61.8%; mid 37.3%; FT 84.3%; USG 28%, AST% 23 | 0.85 / 0.57 / 0.72 / 0.32 / 0.86 | 0.30 / 0.66 |  |
| Robert Covington | PF | 11.0 | 6.0 pts, 3.4 reb, 1.2 ast; 3P 39.7% on 2.8; rim 70.2%; mid 19.9%; FT 75.0%; USG 16%, AST% 10 | 0.85 / 0.59 / 0.84 / 0.59 / 0.73 | 0.14 / 0.59 |  |

## 2023 Memphis Grizzlies

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Ja Morant | PG | 27.6 | 26.2 pts, 5.9 reb, 8.1 ast; 3P 30.7% on 4.9; rim 65.2%; mid 46.4%; FT 74.8%; USG 35%, AST% 41 | 0.76 / 0.89 / 0.89 / 0.85 / 0.73 | 0.56 / 0.91 |  |
| Desmond Bane | SG | 27.3 | 21.5 pts, 5.0 reb, 4.4 ast; 3P 40.8% on 7.0; rim 64.2%; mid 48.4%; FT 88.3%; USG 26%, AST% 21 | 0.95 / 0.81 / 0.86 / 0.55 / 0.88 | 0.31 / 0.71 |  |
| Dillon Brooks | SF | 25.8 | 14.3 pts, 3.3 reb, 2.6 ast; 3P 32.6% on 6.0; rim 63.5%; mid 39.4%; FT 77.9%; USG 22%, AST% 12 | 0.81 / 0.76 / 0.77 / 0.57 / 0.77 | 0.31 / 0.62 |  |
| Jaren Jackson Jr. | C | 23.7 | 18.6 pts, 6.7 reb, 1.0 ast; 3P 35.5% on 4.5; rim 70.4%; mid 35.7%; FT 78.8%; USG 25%, AST% 5 | 0.82 / 0.60 / 0.92 / 0.93 / 0.78 | 0.28 / 0.47 | block 0.95 (BLK% 9.6); interior D 0.95 (DBPM +2.0) |
| Steven Adams | C | 22.2 | 8.6 pts, 11.6 reb, 2.3 ast; 3P 0.0% on 0.0; rim 64.5%; mid 40.0%; FT 36.4%; USG 15%, AST% 11 | 0.20 / 0.54 / 0.92 / 0.88 / 0.37 | 0.20 / 0.61 | oreb 0.97 (ORB% 20.1); dreb 0.97 (DRB% 25.3); 3PT 0.20 (rarely shoots threes) |
| Xavier Tillman Sr. | C | 14.3 | 7.0 pts, 5.0 reb, 1.6 ast; 3P 26.7% on 0.2; rim 75.3%; mid 42.1%; FT 55.1%; USG 14%, AST% 11 | 0.20 / 0.85 / 0.92 / 0.93 / 0.63 | 0.06 / 0.60 | steal 0.95 (STL% 2.3); 3PT 0.20 (rarely shoots threes) |
| Tyus Jones | PG | 19.3 | 10.3 pts, 2.6 reb, 5.2 ast; 3P 37.1% on 4.1; rim 60.0%; mid 46.7%; FT 80.0%; USG 18%, AST% 29 | 0.84 / 0.89 / 0.86 / 0.48 / 0.77 | 0.28 / 0.84 |  |
| Santi Aldama | PF | 16.8 | 9.0 pts, 4.8 reb, 1.3 ast; 3P 35.3% on 3.5; rim 70.7%; mid 32.0%; FT 75.0%; USG 16%, AST% 8 | 0.77 / 0.57 / 0.87 / 0.81 / 0.74 | 0.12 / 0.52 |  |
| John Konchar | SF | 15.8 | 5.1 pts, 4.3 reb, 1.4 ast; 3P 33.9% on 2.5; rim 70.2%; mid 28.5%; FT 77.8%; USG 10%, AST% 8 | 0.84 / 0.54 / 0.79 / 0.51 / 0.74 | 0.02 / 0.39 |  |
| Luke Kennard | SG | 19.6 | 9.3 pts, 2.7 reb, 1.5 ast; 3P 49.4% on 4.6; rim 54.5%; mid 45.7%; FT 94.9%; USG 14%, AST% 9 | 0.92 / 0.85 / 0.90 / 0.49 / 0.80 | 0.05 / 0.37 |  |
| Brandon Clarke | PF | 14.5 | 10.0 pts, 5.5 reb, 1.3 ast; 3P 16.7% on 0.1; rim 79.2%; mid 47.5%; FT 72.3%; USG 18%, AST% 10 | 0.38 / 0.85 / 0.92 / 0.93 / 0.70 | 0.12 / 0.57 |  |
| David Roddy | PF | 13.1 | 6.7 pts, 2.7 reb, 0.8 ast; 3P 30.7% on 3.0; rim 71.1%; mid 41.3%; FT 63.1%; USG 17%, AST% 6 | 0.78 / 0.60 / 0.90 / 0.82 / 0.68 | 0.09 / 0.40 |  |

## 2023 Milwaukee Bucks

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Jrue Holiday | PG | 30.1 | 19.3 pts, 5.1 reb, 7.4 ast; 3P 38.4% on 6.1; rim 72.7%; mid 45.6%; FT 85.9%; USG 25%, AST% 34 | 0.81 / 0.87 / 0.87 / 0.54 / 0.86 | 0.43 / 0.95 | playmaking 0.95 (AST% 34, league-best passer) |
| Giannis Antetokounmpo | PF | 29.4 | 31.1 pts, 11.8 reb, 5.7 ast; 3P 27.5% on 2.7; rim 79.1%; mid 35.4%; FT 64.5%; USG 39%, AST% 33 | 0.58 / 0.84 / 0.88 / 0.89 / 0.64 | 0.60 / 0.92 | oreb 0.96 (ORB% 7.3); dreb 0.97 (DRB% 30.0) |
| Brook Lopez | C | 27.4 | 15.9 pts, 6.7 reb, 1.3 ast; 3P 37.4% on 4.7; rim 77.1%; mid 45.8%; FT 78.4%; USG 19%, AST% 6 | 0.81 / 0.84 / 0.94 / 0.93 / 0.81 | 0.15 / 0.49 | block 0.95 (BLK% 6.7) |
| Grayson Allen | SG | 24.0 | 10.4 pts, 3.2 reb, 2.3 ast; 3P 39.9% on 5.1; rim 67.0%; mid 36.6%; FT 90.5%; USG 15%, AST% 11 | 0.88 / 0.77 / 0.74 / 0.55 / 0.87 | 0.15 / 0.60 |  |
| Khris Middleton | SF | 20.5 | 15.1 pts, 4.2 reb, 4.9 ast; 3P 31.5% on 4.9; rim 64.4%; mid 45.3%; FT 90.2%; USG 27%, AST% 31 | 0.73 / 0.83 / 0.86 / 0.55 / 0.90 | 0.46 / 0.88 |  |
| Pat Connaughton | SF | 19.8 | 7.6 pts, 4.6 reb, 1.3 ast; 3P 33.9% on 5.3; rim 67.2%; mid 59.7%; FT 65.9%; USG 14%, AST% 7 | 0.79 / 0.60 / 0.85 / 0.58 / 0.70 | 0.10 / 0.48 |  |
| Jevon Carter | PG | 18.3 | 8.0 pts, 2.5 reb, 2.4 ast; 3P 42.1% on 4.2; rim 53.8%; mid 43.5%; FT 81.6%; USG 15%, AST% 14 | 0.92 / 0.81 / 0.74 / 0.39 / 0.75 | 0.14 / 0.67 |  |
| Bobby Portis | PF | 22.4 | 14.1 pts, 9.6 reb, 1.5 ast; 3P 37.0% on 3.7; rim 64.3%; mid 47.7%; FT 76.8%; USG 22%, AST% 9 | 0.81 / 0.92 / 0.92 / 0.83 / 0.77 | 0.14 / 0.55 | oreb 0.97 (ORB% 9.2); dreb 0.97 (DRB% 28.6) |
| MarJon Beauchamp | SF | 9.5 | 5.1 pts, 2.2 reb, 0.7 ast; 3P 33.1% on 2.7; rim 66.7%; mid 33.3%; FT 73.0%; USG 18%, AST% 7 | 0.78 / 0.70 / 0.76 / 0.63 / 0.72 | 0.12 / 0.34 |  |
| Joe Ingles | SF | 18.8 | 6.9 pts, 2.8 reb, 3.3 ast; 3P 40.9% on 4.4; rim 65.0%; mid 42.9%; FT 85.7%; USG 13%, AST% 18 | 0.84 / 0.60 / 0.83 / 0.43 / 0.75 | 0.12 / 0.78 |  |
| Wesley Matthews | SF | 11.7 | 3.4 pts, 2.2 reb, 0.7 ast; 3P 31.5% on 2.4; rim 70.6%; mid 39.7%; FT 85.7%; USG 10%, AST% 5 | 0.64 / 0.83 / 0.83 / 0.40 / 0.75 | 0.05 / 0.10 |  |
| Goran Dragić | PG | 8.1 | 6.3 pts, 1.4 reb, 2.6 ast; 3P 35.9% on 2.5; rim 61.3%; mid 41.2%; FT 68.9%; USG 21%, AST% 24 | 0.78 / 0.79 / 0.83 / 0.40 / 0.71 | 0.38 / 0.91 |  |

## 2023 Minnesota Timberwolves

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Anthony Edwards | SG | 31.7 | 24.6 pts, 5.8 reb, 4.4 ast; 3P 36.9% on 7.3; rim 67.4%; mid 36.4%; FT 75.6%; USG 30%, AST% 19 | 0.92 / 0.84 / 0.88 / 0.76 / 0.75 | 0.23 / 0.48 |  |
| Karl-Anthony Towns | PF | 28.2 | 20.8 pts, 8.2 reb, 4.8 ast; 3P 36.6% on 5.7; rim 79.1%; mid 45.3%; FT 87.4%; USG 26%, AST% 22 | 0.75 / 0.78 / 0.84 / 0.78 / 0.87 | 0.18 / 0.86 |  |
| Mike Conley | PG | 26.4 | 11.9 pts, 2.7 reb, 6.7 ast; 3P 38.5% on 5.2; rim 60.8%; mid 50.0%; FT 83.4%; USG 16%, AST% 29 | 0.89 / 0.81 / 0.79 / 0.38 / 0.84 | 0.20 / 0.95 | playmaking 0.95 (AST% 29, league-best passer) |
| Rudy Gobert | C | 25.6 | 13.4 pts, 11.6 reb, 1.2 ast; 3P 0.0% on 0.0; rim 74.8%; mid 28.2%; FT 64.4%; USG 16%, AST% 6 | 0.25 / 0.54 / 0.85 / 0.91 / 0.63 | 0.32 / 0.48 | foul draw 0.95 (FTA per FGA 0.63); 3PT 0.25 (rarely shoots threes) |
| Jaden McDaniels | SF | 25.5 | 12.1 pts, 3.9 reb, 1.9 ast; 3P 39.8% on 3.4; rim 75.2%; mid 42.5%; FT 73.6%; USG 16%, AST% 8 | 0.90 / 0.84 / 0.91 / 0.88 / 0.74 | 0.09 / 0.45 |  |
| Kyle Anderson | PF | 23.2 | 9.4 pts, 5.4 reb, 4.9 ast; 3P 41.0% on 1.5; rim 64.8%; mid 38.7%; FT 73.5%; USG 14%, AST% 23 | 0.61 / 0.82 / 0.90 / 0.67 / 0.72 | 0.18 / 0.88 |  |
| Austin Rivers | SG | 14.2 | 4.9 pts, 1.6 reb, 1.4 ast; 3P 35.0% on 2.4; rim 78.6%; mid 25.0%; FT 76.9%; USG 10%, AST% 9 | 0.87 / 0.60 / 0.85 / 0.51 / 0.74 | 0.02 / 0.41 |  |
| Naz Reid | C | 13.2 | 11.5 pts, 4.9 reb, 1.1 ast; 3P 34.6% on 3.2; rim 81.2%; mid 39.8%; FT 67.7%; USG 25%, AST% 10 | 0.85 / 0.60 / 0.92 / 0.93 / 0.68 | 0.15 / 0.57 |  |
| Taurean Prince | PF | 16.7 | 9.1 pts, 2.5 reb, 1.6 ast; 3P 38.1% on 3.6; rim 67.1%; mid 47.2%; FT 84.4%; USG 17%, AST% 10 | 0.86 / 0.85 / 0.90 / 0.76 / 0.78 | 0.12 / 0.57 |  |
| Jaylen Nowell | SG | 14.0 | 10.8 pts, 2.7 reb, 2.0 ast; 3P 28.9% on 3.6; rim 66.2%; mid 50.5%; FT 77.8%; USG 25%, AST% 16 | 0.78 / 0.85 / 0.92 / 0.75 / 0.79 | 0.19 / 0.49 |  |
| Jordan McLaughlin | PG | 10.8 | 3.7 pts, 1.4 reb, 3.4 ast; 3P 30.8% on 1.8; rim 70.8%; mid 50.2%; FT 83.3%; USG 12%, AST% 27 | 0.64 / 0.82 / 0.84 / 0.40 / 0.74 | 0.21 / 0.93 |  |
| Nickeil Alexander-Walker | SG | 10.5 | 6.2 pts, 1.8 reb, 1.8 ast; 3P 38.4% on 2.7; rim 63.4%; mid 50.0%; FT 66.7%; USG 18%, AST% 17 | 0.83 / 0.77 / 0.82 / 0.47 / 0.70 | 0.17 / 0.63 |  |

## 2023 New Orleans Pelicans

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| CJ McCollum | PG | 29.7 | 20.9 pts, 4.3 reb, 5.7 ast; 3P 38.9% on 7.2; rim 62.1%; mid 42.8%; FT 76.9%; USG 26%, AST% 25 | 0.88 / 0.79 / 0.82 / 0.43 / 0.77 | 0.32 / 0.73 |  |
| Brandon Ingram | SF | 28.7 | 24.7 pts, 5.5 reb, 5.8 ast; 3P 39.0% on 3.6; rim 73.5%; mid 45.9%; FT 88.2%; USG 31%, AST% 28 | 0.92 / 0.92 / 0.90 / 0.92 / 0.88 | 0.34 / 0.77 |  |
| Zion Williamson | PF | 27.4 | 26.0 pts, 7.0 reb, 4.6 ast; 3P 36.8% on 0.7; rim 72.1%; mid 37.1%; FT 71.4%; USG 30%, AST% 24 | 0.53 / 0.85 / 0.95 / 0.93 / 0.70 | 0.37 / 0.92 | rim 0.95 (72.1% at the rim) |
| Herbert Jones | PF | 23.8 | 9.8 pts, 4.1 reb, 2.5 ast; 3P 33.5% on 2.5; rim 66.0%; mid 28.6%; FT 76.4%; USG 14%, AST% 11 | 0.79 / 0.85 / 0.92 / 0.91 / 0.79 | 0.18 / 0.61 |  |
| Jonas Valančiūnas | C | 19.0 | 14.1 pts, 10.1 reb, 1.8 ast; 3P 34.9% on 1.4; rim 72.5%; mid 41.1%; FT 82.6%; USG 23%, AST% 11 | 0.50 / 0.85 / 0.95 / 0.93 / 0.81 | 0.30 / 0.61 | rim 0.95 (72.5% at the rim); oreb 0.97 (ORB% 13.0); dreb 0.97 (DRB% 33.3) |
| Trey Murphy III | SF | 25.2 | 14.5 pts, 3.5 reb, 1.4 ast; 3P 40.6% on 6.3; rim 75.8%; mid 27.0%; FT 90.5%; USG 17%, AST% 6 | 0.89 / 0.60 / 0.92 / 0.90 / 0.91 | 0.09 / 0.34 |  |
| Naji Marshall | SF | 17.4 | 9.1 pts, 3.6 reb, 2.5 ast; 3P 30.3% on 2.8; rim 66.2%; mid 51.9%; FT 78.9%; USG 18%, AST% 14 | 0.73 / 0.84 / 0.89 / 0.83 / 0.80 | 0.30 / 0.68 |  |
| Josh Richardson | SG | 17.3 | 10.1 pts, 2.7 reb, 2.7 ast; 3P 36.5% on 4.5; rim 66.0%; mid 47.0%; FT 85.2%; USG 18%, AST% 16 | 0.83 / 0.92 / 0.89 / 0.61 / 0.79 | 0.23 / 0.63 |  |
| Jose Alvarado | PG | 15.7 | 9.0 pts, 2.4 reb, 3.0 ast; 3P 33.6% on 4.0; rim 67.0%; mid 31.3%; FT 81.3%; USG 20%, AST% 20 | 0.82 / 0.82 / 0.86 / 0.45 / 0.77 | 0.22 / 0.65 |  |
| Dyson Daniels | PG | 12.2 | 3.8 pts, 3.2 reb, 2.3 ast; 3P 31.4% on 1.5; rim 63.5%; mid 24.8%; FT 65.0%; USG 12%, AST% 16 | 0.65 / 0.70 / 0.84 / 0.55 / 0.70 | 0.10 / 0.74 |  |
| Larry Nance Jr. | C | 15.4 | 6.8 pts, 5.4 reb, 1.8 ast; 3P 33.3% on 0.6; rim 76.9%; mid 37.0%; FT 69.6%; USG 12%, AST% 12 | 0.33 / 0.85 / 0.90 / 0.93 / 0.71 | 0.03 / 0.62 |  |
| Jaxson Hayes | C | 8.2 | 5.0 pts, 2.8 reb, 0.7 ast; 3P 10.3% on 0.6; rim 76.6%; mid 65.8%; FT 69.9%; USG 16%, AST% 8 | 0.21 / 0.60 / 0.90 / 0.91 / 0.71 | 0.19 / 0.28 | 3PT 0.21 (rarely shoots threes) |

## 2023 New York Knicks

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Julius Randle | PF | 30.8 | 25.1 pts, 9.9 reb, 4.1 ast; 3P 34.3% on 8.3; rim 67.9%; mid 43.1%; FT 75.7%; USG 30%, AST% 18 | 0.85 / 0.91 / 0.92 / 0.89 / 0.77 | 0.30 / 0.74 | dreb 0.97 (DRB% 25.2) |
| Jalen Brunson | PG | 30.3 | 24.0 pts, 3.6 reb, 6.2 ast; 3P 41.6% on 4.7; rim 61.2%; mid 48.4%; FT 82.9%; USG 27%, AST% 29 | 0.92 / 0.90 / 0.90 / 0.49 / 0.80 | 0.30 / 0.74 |  |
| RJ Barrett | SG | 29.1 | 19.6 pts, 5.0 reb, 2.8 ast; 3P 31.0% on 5.3; rim 64.2%; mid 28.9%; FT 74.0%; USG 26%, AST% 12 | 0.77 / 0.73 / 0.86 / 0.74 / 0.74 | 0.32 / 0.58 |  |
| Mitchell Robinson | C | 21.6 | 7.4 pts, 9.4 reb, 0.9 ast; 3P 30.0% on 0.0; rim 70.0%; mid 50.0%; FT 48.4%; USG 10%, AST% 4 | 0.20 / 0.54 / 0.86 / 0.90 / 0.58 | 0.09 / 0.46 | oreb 0.97 (ORB% 18.4); dreb 0.97 (DRB% 20.0); 3PT 0.20 (rarely shoots threes) |
| Quentin Grimes | SG | 24.7 | 11.3 pts, 3.2 reb, 2.1 ast; 3P 38.6% on 5.7; rim 74.5%; mid 28.1%; FT 79.6%; USG 14%, AST% 10 | 0.87 / 0.57 / 0.88 / 0.79 / 0.76 | 0.14 / 0.57 |  |
| Immanuel Quickley | SG | 23.6 | 14.9 pts, 4.1 reb, 3.4 ast; 3P 37.0% on 5.6; rim 68.1%; mid 43.3%; FT 81.9%; USG 21%, AST% 17 | 0.89 / 0.92 / 0.90 / 0.64 / 0.84 | 0.28 / 0.64 |  |
| Evan Fournier | SG | 11.9 | 6.1 pts, 1.8 reb, 1.3 ast; 3P 30.7% on 4.2; rim 50.0%; mid 32.0%; FT 85.7%; USG 18%, AST% 11 | 0.82 / 0.78 / 0.77 / 0.38 / 0.75 | 0.10 / 0.41 |  |
| Jericho Sims | C | 10.6 | 3.4 pts, 4.7 reb, 0.5 ast; 3P 0.0% on 0.0; rim 83.1%; mid 50.0%; FT 75.0%; USG 7%, AST% 4 | 0.31 / 0.73 / 0.90 / 0.89 / 0.72 | 0.03 / 0.10 | oreb 0.95 (ORB% 13.3) |
| Isaiah Hartenstein | C | 14.4 | 5.0 pts, 6.5 reb, 1.2 ast; 3P 21.6% on 0.5; rim 62.3%; mid 36.6%; FT 67.6%; USG 11%, AST% 8 | 0.24 / 0.77 / 0.89 / 0.83 / 0.70 | 0.02 / 0.54 | oreb 0.95 (ORB% 14.1); 3PT 0.24 (rarely shoots threes) |
| Obi Toppin | PF | 10.7 | 7.4 pts, 2.8 reb, 1.0 ast; 3P 34.4% on 3.7; rim 73.6%; mid 27.1%; FT 80.9%; USG 20%, AST% 9 | 0.84 / 0.58 / 0.87 / 0.89 / 0.75 | 0.17 / 0.56 |  |
| Josh Hart | SF | 24.8 | 9.8 pts, 7.8 reb, 3.8 ast; 3P 37.2% on 2.2; rim 73.6%; mid 25.6%; FT 75.0%; USG 13%, AST% 16 | 0.80 / 0.85 / 0.92 / 0.69 / 0.74 | 0.10 / 0.73 | dreb 0.97 (DRB% 21.0) |
| Miles McBride | PG | 7.5 | 3.5 pts, 0.8 reb, 1.1 ast; 3P 29.9% on 2.1; rim 63.6%; mid 35.5%; FT 66.7%; USG 15%, AST% 12 | 0.83 / 0.73 / 0.83 / 0.51 / 0.70 | 0.09 / 0.56 |  |

## 2023 Oklahoma City Thunder

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Shai Gilgeous-Alexander | PG | 34.5 | 31.4 pts, 4.9 reb, 5.5 ast; 3P 34.5% on 2.5; rim 67.8%; mid 48.5%; FT 90.5%; USG 33%, AST% 26 | 0.83 / 0.91 / 0.91 / 0.83 / 0.90 | 0.31 / 0.66 |  |
| Josh Giddey | PF | 28.9 | 16.6 pts, 7.8 reb, 6.2 ast; 3P 32.5% on 3.1; rim 64.6%; mid 42.6%; FT 73.1%; USG 25%, AST% 30 | 0.79 / 0.79 / 0.84 / 0.62 / 0.73 | 0.32 / 0.95 | playmaking 0.95 (AST% 30, league-best passer) |
| Luguentz Dort | SF | 28.4 | 13.7 pts, 4.6 reb, 2.1 ast; 3P 33.0% on 5.5; rim 52.1%; mid 40.8%; FT 77.2%; USG 20%, AST% 9 | 0.85 / 0.77 / 0.72 / 0.70 / 0.77 | 0.27 / 0.56 |  |
| Jalen Williams | SG | 28.0 | 14.1 pts, 4.5 reb, 3.3 ast; 3P 35.6% on 2.7; rim 72.6%; mid 41.0%; FT 81.2%; USG 18%, AST% 15 | 0.88 / 0.84 / 0.94 / 0.92 / 0.81 | 0.28 / 0.66 |  |
| Aleksej Pokusevski | PF | 16.9 | 8.1 pts, 4.7 reb, 1.9 ast; 3P 36.5% on 3.1; rim 64.5%; mid 31.6%; FT 62.9%; USG 18%, AST% 12 | 0.78 / 0.57 / 0.76 / 0.70 / 0.65 | 0.27 / 0.64 |  |
| Jaylin Williams | C | 14.9 | 5.9 pts, 4.9 reb, 1.6 ast; 3P 40.7% on 2.3; rim 66.7%; mid 46.3%; FT 70.4%; USG 14%, AST% 11 | 0.57 / 0.73 / 0.83 / 0.62 / 0.71 | 0.23 / 0.60 |  |
| Jeremiah Robinson-Earl | PF | 15.1 | 6.8 pts, 4.2 reb, 1.0 ast; 3P 33.3% on 2.6; rim 61.2%; mid 35.7%; FT 83.3%; USG 15%, AST% 7 | 0.53 / 0.73 / 0.81 / 0.73 / 0.76 | 0.14 / 0.21 |  |
| Kenrich Williams | PF | 19.3 | 8.0 pts, 4.9 reb, 2.0 ast; 3P 37.3% on 2.5; rim 71.8%; mid 47.2%; FT 43.6%; USG 14%, AST% 12 | 0.82 / 0.83 / 0.90 / 0.83 / 0.63 | 0.06 / 0.62 |  |
| Aaron Wiggins | SG | 14.7 | 6.8 pts, 3.0 reb, 1.1 ast; 3P 39.3% on 1.7; rim 70.5%; mid 32.9%; FT 83.1%; USG 14%, AST% 8 | 0.92 / 0.60 / 0.90 / 0.79 / 0.77 | 0.09 / 0.42 |  |
| Isaiah Joe | SG | 15.4 | 9.5 pts, 2.4 reb, 1.2 ast; 3P 40.9% on 5.4; rim 70.6%; mid 50.8%; FT 82.0%; USG 18%, AST% 9 | 0.95 / 0.85 / 0.88 / 0.58 / 0.78 | 0.12 / 0.42 | 3PT 0.95 (40.9% from three on 5.4 attempts, elite volume) |
| Tre Mann | PG | 13.9 | 7.7 pts, 2.3 reb, 1.8 ast; 3P 31.5% on 3.8; rim 66.7%; mid 45.5%; FT 76.4%; USG 21%, AST% 14 | 0.82 / 0.76 / 0.77 / 0.49 / 0.74 | 0.20 / 0.58 |  |
| Dario Šarić | C | 10.0 | 6.4 pts, 3.6 reb, 1.3 ast; 3P 39.1% on 2.0; rim 73.1%; mid 24.2%; FT 82.9%; USG 19%, AST% 13 | 0.56 / 0.85 / 0.90 / 0.54 / 0.82 | 0.31 / 0.65 |  |

## 2023 Orlando Magic

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Paolo Banchero | PF | 30.5 | 20.0 pts, 6.9 reb, 3.7 ast; 3P 29.8% on 4.0; rim 65.8%; mid 38.1%; FT 73.8%; USG 28%, AST% 17 | 0.76 / 0.84 / 0.88 / 0.70 / 0.75 | 0.32 / 0.73 |  |
| Franz Wagner | SF | 29.1 | 18.6 pts, 4.1 reb, 3.5 ast; 3P 36.1% on 4.5; rim 72.8%; mid 42.6%; FT 84.2%; USG 24%, AST% 17 | 0.92 / 0.84 / 0.93 / 0.76 / 0.85 | 0.26 / 0.57 |  |
| Markelle Fultz | PG | 25.6 | 14.0 pts, 4.0 reb, 5.7 ast; 3P 31.0% on 1.5; rim 68.5%; mid 44.2%; FT 78.3%; USG 21%, AST% 30 | 0.64 / 0.91 / 0.92 / 0.79 / 0.80 | 0.28 / 0.82 |  |
| Wendell Carter Jr. | C | 25.6 | 15.2 pts, 8.7 reb, 2.3 ast; 3P 35.6% on 3.9; rim 85.0%; mid 41.0%; FT 73.8%; USG 20%, AST% 12 | 0.84 / 0.84 / 0.90 / 0.92 / 0.76 | 0.17 / 0.63 |  |
| Gary Harris | SG | 20.3 | 8.3 pts, 2.0 reb, 1.2 ast; 3P 43.1% on 4.5; rim 61.4%; mid 29.6%; FT 90.0%; USG 13%, AST% 7 | 0.92 / 0.75 / 0.72 / 0.42 / 0.77 | 0.05 / 0.27 |  |
| Bol Bol | PF | 16.9 | 9.1 pts, 5.8 reb, 1.0 ast; 3P 26.5% on 1.6; rim 87.1%; mid 40.5%; FT 75.9%; USG 18%, AST% 7 | 0.41 / 0.85 / 0.92 / 0.93 / 0.75 | 0.13 / 0.51 |  |
| Jalen Suggs | SG | 19.0 | 9.9 pts, 3.0 reb, 2.9 ast; 3P 32.7% on 3.8; rim 58.8%; mid 38.3%; FT 72.3%; USG 20%, AST% 18 | 0.80 / 0.78 / 0.82 / 0.54 / 0.70 | 0.25 / 0.63 |  |
| Moritz Wagner | C | 14.9 | 10.5 pts, 4.5 reb, 1.5 ast; 3P 31.3% on 2.9; rim 73.3%; mid 37.4%; FT 84.1%; USG 21%, AST% 12 | 0.77 / 0.60 / 0.90 / 0.93 / 0.84 | 0.22 / 0.62 |  |
| Chuma Okeke | SF | 14.6 | 4.7 pts, 3.6 reb, 1.4 ast; 3P 30.2% on 3.2; rim 70.0%; mid 22.3%; FT 76.2%; USG 12%, AST% 9 | 0.83 / 0.67 / 0.72 / 0.54 / 0.73 | 0.03 / 0.41 |  |
| Cole Anthony | PG | 21.5 | 13.0 pts, 4.8 reb, 3.9 ast; 3P 36.4% on 3.4; rim 63.2%; mid 47.9%; FT 89.4%; USG 22%, AST% 23 | 0.85 / 0.91 / 0.88 / 0.64 / 0.90 | 0.24 / 0.68 |  |
| Caleb Houstan | SF | 11.4 | 3.8 pts, 2.0 reb, 0.6 ast; 3P 33.8% on 2.7; rim 48.3%; mid 30.2%; FT 83.3%; USG 11%, AST% 5 | 0.86 / 0.60 / 0.79 / 0.40 / 0.74 | 0.02 / 0.10 |  |
| Goga Bitadze | C | 10.6 | 4.4 pts, 3.6 reb, 1.0 ast; 3P 23.1% on 0.7; rim 75.8%; mid 0.0%; FT 54.8%; USG 15%, AST% 12 | 0.23 / 0.60 / 0.90 / 0.93 / 0.66 | 0.11 / 0.63 | 3PT 0.23 (rarely shoots threes) |

## 2023 Philadelphia 76ers

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| James Harden | PG | 34.2 | 21.0 pts, 6.1 reb, 10.7 ast; 3P 38.5% on 7.2; rim 61.8%; mid 46.4%; FT 86.7%; USG 25%, AST% 43 | 0.92 / 0.76 / 0.82 / 0.29 / 0.88 | 0.35 / 0.95 | playmaking 0.95 (AST% 43, league-best passer) |
| Joel Embiid | C | 31.6 | 33.1 pts, 10.1 reb, 4.2 ast; 3P 33.0% on 3.0; rim 80.7%; mid 50.5%; FT 85.7%; USG 37%, AST% 23 | 0.85 / 0.95 / 0.95 / 0.93 / 0.86 | 0.31 / 0.78 | mid 0.95 (mid FG 50.5%); rim 0.95 (80.7% at the rim) |
| Tobias Harris | SF | 29.6 | 14.7 pts, 5.7 reb, 2.5 ast; 3P 38.9% on 4.4; rim 70.9%; mid 46.0%; FT 87.6%; USG 18%, AST% 11 | 0.82 / 0.85 / 0.92 / 0.87 / 0.87 | 0.21 / 0.61 |  |
| P.J. Tucker | PF | 21.3 | 3.5 pts, 4.0 reb, 0.8 ast; 3P 39.3% on 1.9; rim 48.7%; mid 58.3%; FT 82.6%; USG 6%, AST% 4 | 0.85 / 0.55 / 0.78 / 0.38 / 0.74 | 0.01 / 0.45 |  |
| De'Anthony Melton | SG | 23.9 | 10.1 pts, 4.1 reb, 2.6 ast; 3P 39.0% on 5.2; rim 62.2%; mid 39.0%; FT 79.3%; USG 16%, AST% 13 | 0.86 / 0.65 / 0.74 / 0.42 / 0.76 | 0.19 / 0.65 |  |
| Tyrese Maxey | SG | 30.4 | 20.3 pts, 3.0 reb, 3.5 ast; 3P 43.4% on 6.2; rim 62.6%; mid 44.2%; FT 84.5%; USG 24%, AST% 17 | 0.95 / 0.83 / 0.89 / 0.69 / 0.85 | 0.27 / 0.59 | 3PT 0.95 (43.4% from three on 6.2 attempts, elite volume) |
| Shake Milton | SG | 16.1 | 8.4 pts, 2.5 reb, 3.2 ast; 3P 37.8% on 1.9; rim 68.5%; mid 42.5%; FT 85.3%; USG 18%, AST% 22 | 0.84 / 0.82 / 0.86 / 0.52 / 0.85 | 0.30 / 0.72 |  |
| Jalen McDaniels | SF | 13.0 | 9.4 pts, 4.3 reb, 1.6 ast; 3P 33.2% on 2.9; rim 64.9%; mid 39.7%; FT 84.1%; USG 17%, AST% 10 | 0.79 / 0.80 / 0.85 / 0.79 / 0.83 | 0.24 / 0.57 |  |
| Danuel House Jr. | SF | 10.1 | 4.8 pts, 1.7 reb, 0.8 ast; 3P 33.6% on 2.0; rim 72.7%; mid 53.5%; FT 75.0%; USG 14%, AST% 8 | 0.85 / 0.85 / 0.90 / 0.93 / 0.73 | 0.05 / 0.26 |  |
| Montrezl Harrell | C | 7.9 | 5.6 pts, 2.8 reb, 0.6 ast; 3P 0.0% on 0.1; rim 71.0%; mid 9.9%; FT 69.3%; USG 19%, AST% 7 | 0.28 / 0.60 / 0.90 / 0.93 / 0.62 | 0.23 / 0.15 | 3PT 0.28 (rarely shoots threes) |
| Georges Niang | PF | 14.9 | 8.2 pts, 2.3 reb, 1.0 ast; 3P 40.1% on 4.9; rim 68.1%; mid 35.7%; FT 86.7%; USG 17%, AST% 7 | 0.92 / 0.60 / 0.85 / 0.41 / 0.77 | 0.08 / 0.52 |  |
| Paul Reed | C | 7.0 | 4.2 pts, 3.8 reb, 0.4 ast; 3P 16.7% on 0.1; rim 70.6%; mid 38.9%; FT 74.5%; USG 16%, AST% 5 | 0.31 / 0.85 / 0.90 / 0.86 / 0.73 | 0.22 / 0.28 | steal 0.95 (STL% 3.0); block 0.95 (BLK% 6.3) |

## 2023 Phoenix Suns

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Devin Booker | SG | 33.3 | 27.8 pts, 4.6 reb, 5.5 ast; 3P 35.1% on 6.0; rim 71.7%; mid 51.8%; FT 85.5%; USG 32%, AST% 27 | 0.89 / 0.95 / 0.92 / 0.93 / 0.85 | 0.37 / 0.71 | mid 0.95 (mid FG 51.8%) |
| Kevin Durant | PF | 32.0 | 29.1 pts, 6.7 reb, 5.0 ast; 3P 40.4% on 4.9; rim 82.1%; mid 57.2%; FT 91.9%; USG 31%, AST% 24 | 0.88 / 0.95 / 0.90 / 0.93 / 0.92 | 0.41 / 0.92 | mid 0.95 (mid FG 57.2%) |
| Chris Paul | PG | 30.0 | 13.9 pts, 4.3 reb, 8.9 ast; 3P 37.5% on 4.4; rim 58.8%; mid 48.5%; FT 83.1%; USG 19%, AST% 39 | 0.78 / 0.83 / 0.78 / 0.42 / 0.85 | 0.36 / 0.95 | playmaking 0.95 (AST% 39, league-best passer) |
| Deandre Ayton | C | 28.1 | 18.0 pts, 10.0 reb, 1.7 ast; 3P 29.2% on 0.4; rim 80.6%; mid 45.8%; FT 76.0%; USG 23%, AST% 9 | 0.26 / 0.88 / 0.94 / 0.92 / 0.76 | 0.32 / 0.56 | dreb 0.97 (DRB% 27.5); 3PT 0.26 (rarely shoots threes) |
| Torrey Craig | PF | 21.4 | 7.4 pts, 5.4 reb, 1.5 ast; 3P 39.5% on 3.2; rim 69.9%; mid 28.9%; FT 71.1%; USG 13%, AST% 8 | 0.84 / 0.72 / 0.87 / 0.64 / 0.72 | 0.07 / 0.53 |  |
| Josh Okogie | SG | 15.0 | 7.3 pts, 3.5 reb, 1.5 ast; 3P 33.5% on 2.7; rim 56.0%; mid 32.5%; FT 72.4%; USG 18%, AST% 10 | 0.78 / 0.65 / 0.72 / 0.64 / 0.74 | 0.22 / 0.50 |  |
| Cameron Payne | PG | 16.5 | 10.3 pts, 2.3 reb, 4.5 ast; 3P 36.8% on 3.9; rim 60.7%; mid 42.8%; FT 76.6%; USG 25%, AST% 33 | 0.80 / 0.76 / 0.82 / 0.25 / 0.78 | 0.40 / 0.83 |  |
| Bismack Biyombo | C | 10.5 | 4.3 pts, 4.3 reb, 0.9 ast; 3P 30.0% on 0.0; rim 81.4%; mid 42.1%; FT 35.7%; USG 14%, AST% 9 | 0.20 / 0.61 / 0.90 / 0.86 / 0.55 | 0.20 / 0.55 | block 0.95 (BLK% 9.0); 3PT 0.20 (rarely shoots threes) |
| Damion Lee | SG | 16.7 | 8.2 pts, 3.0 reb, 1.3 ast; 3P 44.5% on 3.3; rim 60.0%; mid 37.6%; FT 90.4%; USG 16%, AST% 9 | 0.92 / 0.84 / 0.83 / 0.45 / 0.82 | 0.12 / 0.49 |  |
| Jock Landale | C | 10.4 | 6.6 pts, 4.0 reb, 1.0 ast; 3P 25.0% on 1.2; rim 74.0%; mid 38.5%; FT 75.2%; USG 19%, AST% 10 | 0.31 / 0.85 / 0.90 / 0.93 / 0.78 | 0.29 / 0.58 |  |
| Terrence Ross | SG | 14.6 | 8.3 pts, 2.4 reb, 1.5 ast; 3P 36.8% on 4.1; rim 70.6%; mid 48.4%; FT 79.4%; USG 17%, AST% 10 | 0.82 / 0.92 / 0.90 / 0.59 / 0.74 | 0.26 / 0.56 |  |
| Ish Wainright | SF | 11.5 | 4.2 pts, 2.4 reb, 0.9 ast; 3P 32.9% on 2.9; rim 52.9%; mid 34.6%; FT 83.9%; USG 12%, AST% 7 | 0.76 / 0.60 / 0.80 / 0.50 / 0.75 | 0.06 / 0.48 |  |

## 2023 Portland Trail Blazers

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Damian Lillard | PG | 30.4 | 32.2 pts, 4.8 reb, 7.3 ast; 3P 37.1% on 11.3; rim 67.3%; mid 50.8%; FT 91.4%; USG 34%, AST% 35 | 0.92 / 0.85 / 0.92 / 0.77 / 0.90 | 0.36 / 0.77 |  |
| Jerami Grant | PF | 29.7 | 20.5 pts, 4.5 reb, 2.4 ast; 3P 40.1% on 5.7; rim 68.0%; mid 38.9%; FT 81.3%; USG 23%, AST% 10 | 0.94 / 0.84 / 0.89 / 0.90 / 0.81 | 0.29 / 0.59 |  |
| Anfernee Simons | SG | 29.0 | 21.1 pts, 2.6 reb, 4.1 ast; 3P 37.7% on 9.1; rim 64.7%; mid 48.4%; FT 89.4%; USG 25%, AST% 19 | 0.92 / 0.92 / 0.92 / 0.83 / 0.89 | 0.30 / 0.66 |  |
| Matisse Thybulle | SG | 21.4 | 4.1 pts, 2.0 reb, 0.7 ast; 3P 36.5% on 2.1; rim 64.2%; mid 33.3%; FT 67.9%; USG 11%, AST% 6 | 0.92 / 0.30 / 0.72 / 0.46 / 0.71 | 0.01 / 0.10 | perimeter D 0.95 (DBPM +2.2, 3.4% steals) |
| Jusuf Nurkić | C | 20.5 | 13.3 pts, 9.1 reb, 2.9 ast; 3P 36.1% on 2.3; rim 64.5%; mid 53.0%; FT 66.1%; USG 22%, AST% 16 | 0.53 / 0.60 / 0.92 / 0.88 / 0.66 | 0.40 / 0.74 |  |
| Cam Reddish | SF | 21.3 | 9.7 pts, 2.3 reb, 1.4 ast; 3P 31.3% on 3.6; rim 67.5%; mid 36.4%; FT 85.3%; USG 17%, AST% 8 | 0.76 / 0.85 / 0.90 / 0.82 / 0.78 | 0.13 / 0.33 |  |
| Justise Winslow | PF | 20.5 | 6.8 pts, 5.0 reb, 3.4 ast; 3P 31.1% on 1.6; rim 55.1%; mid 26.0%; FT 71.4%; USG 14%, AST% 17 | 0.53 / 0.69 / 0.77 / 0.53 / 0.72 | 0.30 / 0.76 |  |
| Drew Eubanks | C | 14.3 | 6.6 pts, 5.4 reb, 1.3 ast; 3P 38.9% on 0.2; rim 75.6%; mid 47.7%; FT 66.4%; USG 12%, AST% 9 | 0.27 / 0.85 / 0.92 / 0.93 / 0.69 | 0.03 / 0.56 | block 0.95 (BLK% 5.7); 3PT 0.27 (rarely shoots threes) |
| Shaedon Sharpe | SG | 16.0 | 9.9 pts, 3.0 reb, 1.2 ast; 3P 36.0% on 3.5; rim 70.8%; mid 40.4%; FT 71.4%; USG 19%, AST% 8 | 0.90 / 0.85 / 0.92 / 0.93 / 0.72 | 0.11 / 0.16 |  |
| Trendon Watford | PF | 13.2 | 7.4 pts, 3.9 reb, 2.1 ast; 3P 39.1% on 1.0; rim 67.6%; mid 46.7%; FT 72.0%; USG 16%, AST% 16 | 0.63 / 0.85 / 0.90 / 0.86 / 0.69 | 0.26 / 0.73 |  |
| Kevin Knox | SF | 11.4 | 6.6 pts, 2.8 reb, 0.5 ast; 3P 34.9% on 3.0; rim 69.2%; mid 47.1%; FT 76.7%; USG 18%, AST% 5 | 0.85 / 0.85 / 0.90 / 0.83 / 0.74 | 0.09 / 0.10 |  |
| Nassir Little | SF | 12.3 | 6.6 pts, 2.6 reb, 0.9 ast; 3P 36.7% on 2.9; rim 69.6%; mid 45.7%; FT 71.7%; USG 16%, AST% 7 | 0.86 / 0.83 / 0.87 / 0.68 / 0.72 | 0.09 / 0.32 |  |

## 2023 San Antonio Spurs

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Keldon Johnson | SF | 28.8 | 22.0 pts, 5.1 reb, 2.9 ast; 3P 32.9% on 6.5; rim 65.7%; mid 33.3%; FT 74.9%; USG 28%, AST% 14 | 0.81 / 0.85 / 0.92 / 0.82 / 0.75 | 0.31 / 0.61 |  |
| Tre Jones | PG | 24.9 | 12.9 pts, 3.6 reb, 6.6 ast; 3P 28.5% on 2.3; rim 67.3%; mid 44.8%; FT 86.0%; USG 19%, AST% 32 | 0.60 / 0.88 / 0.86 / 0.46 / 0.86 | 0.36 / 0.95 | playmaking 0.95 (AST% 32, league-best passer) |
| Jeremy Sochan | PF | 21.4 | 11.0 pts, 5.3 reb, 2.5 ast; 3P 24.6% on 2.4; rim 66.5%; mid 42.1%; FT 69.8%; USG 20%, AST% 14 | 0.67 / 0.75 / 0.89 / 0.88 / 0.70 | 0.23 / 0.67 |  |
| Devin Vassell | SG | 26.9 | 18.5 pts, 3.9 reb, 3.6 ast; 3P 38.7% on 7.0; rim 64.3%; mid 44.7%; FT 78.0%; USG 24%, AST% 17 | 0.92 / 0.90 / 0.90 / 0.77 / 0.78 | 0.29 / 0.64 |  |
| Keita Bates-Diop | PF | 16.9 | 9.7 pts, 3.7 reb, 1.5 ast; 3P 39.4% on 2.1; rim 69.6%; mid 33.5%; FT 79.3%; USG 17%, AST% 10 | 0.92 / 0.60 / 0.92 / 0.73 / 0.82 | 0.15 / 0.58 |  |
| Malaki Branham | SG | 18.8 | 10.2 pts, 2.7 reb, 1.9 ast; 3P 30.2% on 3.9; rim 63.7%; mid 48.9%; FT 82.9%; USG 19%, AST% 11 | 0.72 / 0.85 / 0.90 / 0.89 / 0.77 | 0.23 / 0.56 |  |
| Romeo Langford | SG | 14.8 | 6.9 pts, 2.6 reb, 1.2 ast; 3P 26.2% on 1.4; rim 68.0%; mid 46.9%; FT 69.6%; USG 15%, AST% 8 | 0.59 / 0.85 / 0.90 / 0.93 / 0.71 | 0.12 / 0.46 |  |
| Devonte' Graham | PG | 21.8 | 7.4 pts, 1.7 reb, 2.7 ast; 3P 35.2% on 4.6; rim 60.0%; mid 43.3%; FT 74.8%; USG 17%, AST% 19 | 0.83 / 0.80 / 0.82 / 0.40 / 0.74 | 0.14 / 0.65 |  |
| Sandro Mamukelashvili | C | 18.5 | 6.1 pts, 4.3 reb, 1.4 ast; 3P 30.3% on 2.3; rim 61.0%; mid 16.5%; FT 68.4%; USG 18%, AST% 13 | 0.49 / 0.56 / 0.81 / 0.59 / 0.71 | 0.11 / 0.65 |  |
| Zach Collins | C | 18.1 | 11.6 pts, 6.3 reb, 2.9 ast; 3P 37.4% on 2.3; rim 67.9%; mid 39.8%; FT 76.1%; USG 21%, AST% 18 | 0.78 / 0.82 / 0.91 / 0.78 / 0.75 | 0.23 / 0.77 |  |
| Doug McDermott | SF | 15.7 | 10.2 pts, 2.2 reb, 1.4 ast; 3P 41.3% on 4.7; rim 70.7%; mid 33.4%; FT 75.7%; USG 19%, AST% 10 | 0.92 / 0.82 / 0.88 / 0.69 / 0.74 | 0.13 / 0.56 |  |
| Blake Wesley | SG | 13.4 | 5.0 pts, 2.2 reb, 2.6 ast; 3P 38.5% on 1.4; rim 51.7%; mid 20.7%; FT 59.1%; USG 18%, AST% 19 | 0.85 / 0.36 / 0.72 / 0.52 / 0.62 | 0.30 / 0.68 |  |

## 2023 Toronto Raptors

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Pascal Siakam | PF | 32.7 | 24.2 pts, 7.8 reb, 5.8 ast; 3P 32.4% on 4.0; rim 75.0%; mid 42.5%; FT 77.4%; USG 27%, AST% 25 | 0.77 / 0.87 / 0.93 / 0.78 / 0.78 | 0.36 / 0.81 |  |
| Fred VanVleet | PG | 32.1 | 19.3 pts, 4.0 reb, 7.2 ast; 3P 34.2% on 8.8; rim 58.6%; mid 42.8%; FT 89.8%; USG 23%, AST% 28 | 0.82 / 0.76 / 0.82 / 0.26 / 0.90 | 0.30 / 0.76 |  |
| OG Anunoby | SF | 30.9 | 16.8 pts, 4.9 reb, 2.0 ast; 3P 38.7% on 5.5; rim 69.5%; mid 41.0%; FT 83.8%; USG 20%, AST% 8 | 0.84 / 0.83 / 0.88 / 0.89 / 0.83 | 0.17 / 0.39 |  |
| Scottie Barnes | SF | 30.0 | 15.3 pts, 6.6 reb, 4.8 ast; 3P 28.1% on 2.9; rim 68.5%; mid 32.6%; FT 77.2%; USG 20%, AST% 20 | 0.76 / 0.75 / 0.88 / 0.88 / 0.76 | 0.32 / 0.77 |  |
| Jakob Poeltl | C | 21.8 | 12.5 pts, 9.1 reb, 2.7 ast; 3P 0.0% on 0.0; rim 75.7%; mid 46.4%; FT 59.2%; USG 18%, AST% 15 | 0.22 / 0.84 / 0.94 / 0.86 / 0.60 | 0.12 / 0.71 | 3PT 0.22 (rarely shoots threes) |
| Gary Trent Jr. | SG | 27.0 | 17.4 pts, 2.7 reb, 1.6 ast; 3P 36.9% on 6.8; rim 70.4%; mid 40.4%; FT 83.9%; USG 22%, AST% 7 | 0.92 / 0.92 / 0.90 / 0.77 / 0.86 | 0.17 / 0.19 |  |
| Christian Koloko | C | 9.0 | 3.1 pts, 2.9 reb, 0.5 ast; 3P 8.3% on 0.2; rim 60.0%; mid 36.2%; FT 62.7%; USG 10%, AST% 5 | 0.24 / 0.66 / 0.87 / 0.81 / 0.68 | 0.16 / 0.10 | block 0.95 (BLK% 6.9); 3PT 0.24 (rarely shoots threes) |
| Precious Achiuwa | C | 15.3 | 9.2 pts, 5.9 reb, 0.9 ast; 3P 26.9% on 2.0; rim 73.4%; mid 27.3%; FT 70.2%; USG 19%, AST% 6 | 0.36 / 0.85 / 0.92 / 0.93 / 0.71 | 0.17 / 0.10 |  |
| Thaddeus Young | PF | 9.8 | 4.4 pts, 3.1 reb, 1.4 ast; 3P 17.6% on 0.6; rim 80.6%; mid 36.4%; FT 69.2%; USG 14%, AST% 13 | 0.44 / 0.85 / 0.90 / 0.93 / 0.71 | 0.07 / 0.65 | steal 0.95 (STL% 3.4) |
| Will Barton | SG | 8.5 | 6.8 pts, 2.5 reb, 2.0 ast; 3P 36.7% on 3.2; rim 59.1%; mid 34.4%; FT 78.7%; USG 19%, AST% 15 | 0.85 / 0.64 / 0.72 / 0.47 / 0.74 | 0.32 / 0.66 |  |
| Chris Boucher | PF | 14.6 | 9.4 pts, 5.6 reb, 0.4 ast; 3P 32.8% on 2.5; rim 65.1%; mid 48.4%; FT 76.2%; USG 18%, AST% 3 | 0.83 / 0.85 / 0.92 / 0.93 / 0.78 | 0.14 / 0.10 |  |
| Malachi Flynn | PG | 8.3 | 4.6 pts, 1.5 reb, 1.3 ast; 3P 35.3% on 2.5; rim 51.7%; mid 33.4%; FT 75.8%; USG 17%, AST% 14 | 0.80 / 0.73 / 0.74 / 0.37 / 0.73 | 0.13 / 0.58 |  |

## 2023 Utah Jazz

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Lauri Markkanen | PF | 34.2 | 25.6 pts, 8.7 reb, 1.9 ast; 3P 39.1% on 7.7; rim 71.7%; mid 49.5%; FT 87.5%; USG 27%, AST% 9 | 0.86 / 0.84 / 0.91 / 0.92 / 0.87 | 0.29 / 0.55 |  |
| Jordan Clarkson | SG | 32.0 | 20.8 pts, 4.1 reb, 4.4 ast; 3P 33.8% on 7.5; rim 68.8%; mid 45.6%; FT 81.6%; USG 28%, AST% 21 | 0.85 / 0.85 / 0.90 / 0.79 / 0.81 | 0.30 / 0.61 |  |
| Kelly Olynyk | C | 27.0 | 12.5 pts, 6.2 reb, 3.7 ast; 3P 39.4% on 3.5; rim 70.2%; mid 36.2%; FT 85.3%; USG 18%, AST% 18 | 0.92 / 0.82 / 0.85 / 0.73 / 0.85 | 0.12 / 0.77 |  |
| Walker Kessler | C | 20.3 | 9.2 pts, 8.4 reb, 0.9 ast; 3P 33.3% on 0.0; rim 81.3%; mid 41.6%; FT 51.6%; USG 13%, AST% 6 | 0.20 / 0.59 / 0.93 / 0.92 / 0.51 | 0.18 / 0.48 | block 0.95 (BLK% 8.6); interior D 0.95 (DBPM +1.5); 3PT 0.20 (rarely shoots threes) |
| Ochai Agbaji | SG | 17.5 | 7.9 pts, 2.0 reb, 1.1 ast; 3P 35.5% on 3.9; rim 62.1%; mid 42.1%; FT 81.2%; USG 16%, AST% 8 | 0.85 / 0.60 / 0.88 / 0.71 / 0.76 | 0.12 / 0.34 |  |
| Collin Sexton | PG | 21.3 | 14.3 pts, 2.2 reb, 2.9 ast; 3P 39.3% on 2.5; rim 60.8%; mid 53.3%; FT 81.9%; USG 23%, AST% 18 | 0.92 / 0.85 / 0.90 / 0.66 / 0.81 | 0.33 / 0.66 |  |
| Talen Horton-Tucker | SG | 17.2 | 10.7 pts, 3.2 reb, 3.8 ast; 3P 28.6% on 3.1; rim 62.7%; mid 33.8%; FT 75.0%; USG 26%, AST% 27 | 0.72 / 0.76 / 0.82 / 0.59 / 0.75 | 0.34 / 0.72 |  |
| Kris Dunn | PG | 23.6 | 13.2 pts, 4.5 reb, 5.6 ast; 3P 47.2% on 1.6; rim 76.7%; mid 41.6%; FT 77.4%; USG 20%, AST% 32 | 0.85 / 0.85 / 0.90 / 0.70 / 0.79 | 0.33 / 0.90 |  |
| Juan Toscano-Anderson | SF | 11.9 | 3.0 pts, 2.3 reb, 1.3 ast; 3P 18.6% on 0.8; rim 66.7%; mid 42.8%; FT 79.2%; USG 11%, AST% 12 | 0.52 / 0.85 / 0.90 / 0.76 / 0.74 | 0.05 / 0.63 |  |
| Simone Fontecchio | SF | 11.3 | 6.3 pts, 1.7 reb, 0.8 ast; 3P 33.0% on 3.7; rim 54.5%; mid 46.1%; FT 79.5%; USG 20%, AST% 8 | 0.88 / 0.80 / 0.78 / 0.62 / 0.75 | 0.12 / 0.32 |  |
| Damian Jones | C | 12.5 | 3.5 pts, 3.0 reb, 0.4 ast; 3P 58.8% on 0.4; rim 70.6%; mid 50.0%; FT 75.9%; USG 11%, AST% 4 | 0.29 / 0.60 / 0.90 / 0.84 / 0.73 | 0.02 / 0.10 | 3PT 0.29 (rarely shoots threes) |
| Rudy Gay | PF | 11.2 | 5.2 pts, 2.9 reb, 1.0 ast; 3P 25.4% on 2.3; rim 66.7%; mid 44.1%; FT 85.7%; USG 18%, AST% 9 | 0.64 / 0.83 / 0.87 / 0.72 / 0.77 | 0.26 / 0.57 |  |

## 2023 Washington Wizards

| Player | Pos | MPG | Real | Ratings (3PT / mid / rim / dunk / FT) | Usage / playmaking | Flags |
|---|---|---|---|---|---|---|
| Kyle Kuzma | PF | 32.9 | 21.2 pts, 7.3 reb, 3.7 ast; 3P 33.3% on 7.5; rim 72.2%; mid 35.1%; FT 73.0%; USG 28%, AST% 16 | 0.79 / 0.85 / 0.92 / 0.88 / 0.71 | 0.28 / 0.70 |  |
| Bradley Beal | SG | 31.1 | 23.2 pts, 3.9 reb, 5.4 ast; 3P 36.5% on 4.4; rim 78.6%; mid 47.5%; FT 84.2%; USG 29%, AST% 27 | 0.92 / 0.92 / 0.92 / 0.92 / 0.84 | 0.26 / 0.68 |  |
| Kristaps Porziņģis | C | 30.0 | 23.2 pts, 8.4 reb, 2.7 ast; 3P 38.5% on 5.5; rim 74.0%; mid 46.2%; FT 85.1%; USG 27%, AST% 13 | 0.88 / 0.85 / 0.86 / 0.89 / 0.85 | 0.24 / 0.65 |  |
| Monte Morris | PG | 23.8 | 10.3 pts, 3.4 reb, 5.3 ast; 3P 38.2% on 3.3; rim 75.4%; mid 47.9%; FT 83.1%; USG 16%, AST% 26 | 0.83 / 0.85 / 0.90 / 0.70 / 0.84 | 0.28 / 0.91 |  |
| Corey Kispert | SF | 25.0 | 11.1 pts, 2.8 reb, 1.2 ast; 3P 42.4% on 5.2; rim 76.2%; mid 36.2%; FT 85.2%; USG 14%, AST% 6 | 0.95 / 0.60 / 0.90 / 0.84 / 0.79 | 0.08 / 0.34 | 3PT 0.95 (42.4% from three on 5.2 attempts, elite volume) |
| Daniel Gafford | C | 16.5 | 9.0 pts, 5.6 reb, 1.1 ast; 3P 30.0% on 0.0; rim 84.6%; mid 56.3%; FT 67.9%; USG 15%, AST% 8 | 0.27 / 0.60 / 0.92 / 0.93 / 0.70 | 0.18 / 0.52 | block 0.95 (BLK% 5.2); 3PT 0.27 (rarely shoots threes) |
| Deni Avdija | SF | 23.0 | 9.2 pts, 6.4 reb, 2.8 ast; 3P 29.7% on 3.1; rim 72.0%; mid 19.3%; FT 73.9%; USG 17%, AST% 14 | 0.73 / 0.55 / 0.85 / 0.75 / 0.73 | 0.23 / 0.68 |  |
| Delon Wright | PG | 20.6 | 7.4 pts, 3.6 reb, 3.9 ast; 3P 34.5% on 2.4; rim 84.2%; mid 53.5%; FT 86.7%; USG 13%, AST% 21 | 0.78 / 0.85 / 0.90 / 0.83 / 0.83 | 0.21 / 0.82 |  |
| Jordan Goodwin | PG | 13.7 | 6.6 pts, 3.3 reb, 2.7 ast; 3P 32.2% on 1.9; rim 71.2%; mid 42.3%; FT 76.8%; USG 17%, AST% 21 | 0.67 / 0.85 / 0.90 / 0.77 / 0.74 | 0.25 / 0.70 |  |
| Anthony Gill | PF | 7.0 | 3.3 pts, 1.7 reb, 0.6 ast; 3P 13.8% on 0.5; rim 78.0%; mid 37.3%; FT 73.1%; USG 12%, AST% 7 | 0.30 / 0.72 / 0.90 / 0.56 / 0.72 | 0.09 / 0.10 | 3PT 0.30 (rarely shoots threes) |
| Kendrick Nunn | SG | 10.1 | 7.1 pts, 1.5 reb, 1.3 ast; 3P 35.4% on 3.2; rim 66.7%; mid 47.2%; FT 85.4%; USG 24%, AST% 14 | 0.86 / 0.85 / 0.90 / 0.65 / 0.77 | 0.17 / 0.51 |  |
| Taj Gibson | C | 6.3 | 3.4 pts, 1.9 reb, 0.7 ast; 3P 33.3% on 0.5; rim 80.6%; mid 43.3%; FT 71.4%; USG 15%, AST% 10 | 0.29 / 0.73 / 0.90 / 0.64 / 0.72 | 0.12 / 0.29 | 3PT 0.29 (rarely shoots threes) |

