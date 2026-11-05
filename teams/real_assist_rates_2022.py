"""Real 2021-22 assists per minute played (Basketball-Reference: assists per game over minutes per game) for every player on the 25 teams built from real data; the engine paces assists toward each rate over the minutes played."""

REAL_ASSIST_RATE_2022 = {
    "2022 Atlanta Hawks": {
        "Trae Young": 0.2779, "Clint Capela": 0.0435, "Kevin Huerter": 0.0912, "John Collins": 0.0584,
        "De'Andre Hunter": 0.0436, "Bogdan Bogdanović": 0.1058, "Danilo Gallinari": 0.0593, "Timothé Luwawu-Cabarrot": 0.0606,
        "Delon Wright": 0.127, "Cam Reddish": 0.047, "Onyeka Okongwu": 0.0531, "Lou Williams": 0.1329,
    },
    "2022 Charlotte Hornets": {
        "Miles Bridges": 0.107, "LaMelo Ball": 0.2353, "Terry Rozier": 0.1335, "Mason Plumlee": 0.126,
        "Gordon Hayward": 0.1129, "P.J. Washington": 0.0846, "Kelly Oubre Jr.": 0.0418, "Cody Martin": 0.0951,
        "Nick Richards": 0.0411, "Jalen McDaniels": 0.0675, "Ish Smith": 0.1884, "Montrezl Harrell": 0.0952,
    },
    "2022 Chicago Bulls": {
        "DeMar DeRozan": 0.1357, "Nikola Vučević": 0.0967, "Zach LaVine": 0.1297, "Javonte Green": 0.0385,
        "Ayo Dosunmu": 0.1204, "Lonzo Ball": 0.1474, "Alex Caruso": 0.1429, "Coby White": 0.1055,
        "Derrick Jones Jr.": 0.0341, "Troy Brown Jr.": 0.0625, "Tony Bradley": 0.05, "Matt Thomas": 0.0435,
    },
    "2022 Cleveland Cavaliers": {
        "Evan Mobley": 0.074, "Darius Garland": 0.2409, "Lauri Markkanen": 0.0422, "Isaac Okoro": 0.0608,
        "Jarrett Allen": 0.0495, "Dean Wade": 0.0521, "Lamar Stevens": 0.0435, "Caris LeVert": 0.1309,
        "Ricky Rubio": 0.2316, "Brandon Goodwin": 0.1799, "Kevin Love": 0.0978, "Cedi Osman": 0.0901,
    },
    "2022 Denver Nuggets": {
        "Aaron Gordon": 0.0789, "Nikola Jokić": 0.2358, "Monte Morris": 0.1472, "Will Barton": 0.1215,
        "Jeff Green": 0.0526, "Austin Rivers": 0.0588, "JaMychal Green": 0.0556, "Davon Reed": 0.0791,
        "Bones Hyland": 0.1474, "Facundo Campazzo": 0.1868, "Bryn Forbes": 0.0575, "Zeke Nnaji": 0.0235,
    },
    "2022 Detroit Pistons": {
        "Saddiq Bey": 0.0848, "Isaiah Stewart": 0.0469, "Cade Cunningham": 0.1718, "Jerami Grant": 0.0752,
        "Killian Hayes": 0.168, "Cory Joseph": 0.1463, "Hamidou Diallo": 0.0594, "Frank Jackson": 0.0455,
        "Trey Lyles": 0.0567, "Josh Jackson": 0.0718, "Rodney McGruder": 0.0608, "Kelly Olynyk": 0.1466,
    },
    "2022 Houston Rockets": {
        "Jae'Sean Tate": 0.1061, "Jalen Green": 0.0815, "Christian Wood": 0.0747, "Kevin Porter Jr.": 0.1981,
        "Eric Gordon": 0.0922, "Garrison Mathews": 0.038, "Daniel Theis": 0.0356, "Alperen Şengün": 0.1256,
        "Armoni Brooks": 0.0714, "David Nwaba": 0.0606, "KJ Martin": 0.0619, "Josh Christopher": 0.1111,
    },
    "2022 Indiana Pacers": {
        "Domantas Sabonis": 0.1441, "Myles Turner": 0.034, "Justin Holiday": 0.0623, "Caris LeVert": 0.1415,
        "Chris Duarte": 0.075, "Malcolm Brogdon": 0.1761, "Tyrese Haliburton": 0.2659, "Buddy Hield": 0.1348,
        "Oshae Brissett": 0.0472, "Torrey Craig": 0.0542, "Duane Washington Jr.": 0.0891, "Lance Stephenson": 0.2097,
    },
    "2022 Los Angeles Clippers": {
        "Ivica Zubac": 0.0656, "Reggie Jackson": 0.1538, "Marcus Morris": 0.0724, "Nicolas Batum": 0.0685,
        "Terance Mann": 0.0909, "Paul George": 0.1643, "Amir Coffey": 0.0793, "Eric Bledsoe": 0.1667,
        "Luke Kennard": 0.0766, "Serge Ibaka": 0.0649, "Isaiah Hartenstein": 0.1341, "Brandon Boston Jr.": 0.0671,
    },
    "2022 Los Angeles Lakers": {
        "Russell Westbrook": 0.207, "LeBron James": 0.1667, "Avery Bradley": 0.0352, "Anthony Davis": 0.0883,
        "Malik Monk": 0.1032, "Stanley Johnson": 0.0746, "Dwight Howard": 0.037, "Talen Horton-Tucker": 0.1071,
        "Austin Reaves": 0.0776, "Kent Bazemore": 0.0643, "Wayne Ellington": 0.0372, "Carmelo Anthony": 0.0385,
    },
    "2022 Miami Heat": {
        "P.J. Tucker": 0.0753, "Duncan Robinson": 0.0618, "Kyle Lowry": 0.2212, "Jimmy Butler": 0.1622,
        "Bam Adebayo": 0.1043, "Gabe Vincent": 0.1325, "Max Strus": 0.0601, "Dewayne Dedmon": 0.044,
        "Caleb Martin": 0.048, "Omer Yurtseven": 0.0714, "Tyler Herro": 0.1227, "Markieff Morris": 0.08,
    },
    "2022 Milwaukee Bucks": {
        "Giannis Antetokounmpo": 0.1763, "Khris Middleton": 0.1667, "Jrue Holiday": 0.2061, "Grayson Allen": 0.0549,
        "Bobby Portis": 0.0426, "Pat Connaughton": 0.05, "George Hill": 0.0948, "Wesley Matthews": 0.0343,
        "Jordan Nwora": 0.0524, "Thanasis Antetokounmpo": 0.0505, "Sandro Mamukelashvili": 0.0505, "Rodney Hood": 0.0537,
    },
    "2022 Minnesota Timberwolves": {
        "Karl-Anthony Towns": 0.1075, "Anthony Edwards": 0.1108, "Jarred Vanderbilt": 0.0512, "D'Angelo Russell": 0.2219,
        "Patrick Beverley": 0.1811, "Jaden McDaniels": 0.0426, "Malik Beasley": 0.06, "Taurean Prince": 0.0585,
        "Naz Reid": 0.057, "Josh Okogie": 0.0476, "Jordan McLaughlin": 0.2, "Jaylen Nowell": 0.1338,
    },
    "2022 New Orleans Pelicans": {
        "Jonas Valančiūnas": 0.0858, "Herbert Jones": 0.0702, "Devonte' Graham": 0.1479, "Brandon Ingram": 0.1647,
        "Josh Hart": 0.1224, "Jaxson Hayes": 0.03, "CJ McCollum": 0.1716, "Nickeil Alexander-Walker": 0.1065,
        "Garrett Temple": 0.0699, "Willy Hernangómez": 0.0774, "Jose Alvarado": 0.1818, "Trey Murphy III": 0.0432,
    },
    "2022 New York Knicks": {
        "Evan Fournier": 0.0712, "Julius Randle": 0.1445, "RJ Barrett": 0.087, "Mitchell Robinson": 0.0195,
        "Alec Burks": 0.1049, "Kemba Walker": 0.1367, "Nerlens Noel": 0.04, "Obi Toppin": 0.0643,
        "Quentin Grimes": 0.0585, "Derrick Rose": 0.1633, "Taj Gibson": 0.033, "Immanuel Quickley": 0.1515,
    },
    "2022 Oklahoma City Thunder": {
        "Shai Gilgeous-Alexander": 0.17, "Josh Giddey": 0.2032, "Darius Bazley": 0.0502, "Luguentz Dort": 0.0521,
        "Jeremiah Robinson-Earl": 0.045, "Aaron Wiggins": 0.0579, "Isaiah Roby": 0.0758, "Tre Mann": 0.0658,
        "Aleksej Pokusevski": 0.104, "Théo Maledon": 0.1236, "Ty Jerome": 0.1377, "Kenrich Williams": 0.1005,
    },
    "2022 Orlando Magic": {
        "Franz Wagner": 0.0945, "Mo Bamba": 0.0467, "Cole Anthony": 0.1798, "Wendell Carter Jr.": 0.0936,
        "Jalen Suggs": 0.1618, "Gary Harris": 0.0634, "Chuma Okeke": 0.068, "R.J. Hampton": 0.1142,
        "Robin Lopez": 0.0882, "Moritz Wagner": 0.0921, "Ignas Brazdeikis": 0.0703, "Terrence Ross": 0.0783,
    },
    "2022 Philadelphia 76ers": {
        "Tyrese Maxey": 0.1218, "Tobias Harris": 0.1006, "Joel Embiid": 0.1243, "Matisse Thybulle": 0.0431,
        "Seth Curry": 0.1149, "Danny Green": 0.0459, "James Harden": 0.2785, "Furkan Korkmaz": 0.09,
        "Andre Drummond": 0.1087, "Georges Niang": 0.057, "Shake Milton": 0.1168, "Isaiah Joe": 0.0541,
    },
    "2022 Phoenix Suns": {
        "Mikal Bridges": 0.0661, "Devin Booker": 0.1391, "Jae Crowder": 0.0676, "Chris Paul": 0.3283,
        "Deandre Ayton": 0.0475, "JaVale McGee": 0.038, "Cameron Johnson": 0.0573, "Landry Shamet": 0.0769,
        "Cameron Payne": 0.2227, "Bismack Biyombo": 0.0426, "Torrey Craig": 0.0577, "Elfrid Payton": 0.1818,
    },
    "2022 Portland Trail Blazers": {
        "Jusuf Nurkić": 0.0993, "Robert Covington": 0.047, "Norman Powell": 0.0631, "CJ McCollum": 0.1278,
        "Anfernee Simons": 0.1322, "Damian Lillard": 0.2005, "CJ Elleby": 0.0743, "Nassir Little": 0.0502,
        "Drew Eubanks": 0.0542, "Larry Nance Jr.": 0.0862, "Trendon Watford": 0.0939, "Ben McLemore": 0.0448,
    },
    "2022 Sacramento Kings": {
        "Harrison Barnes": 0.0716, "De'Aaron Fox": 0.1586, "Tyrese Haliburton": 0.2145, "Richaun Holmes": 0.046,
        "Justin Holiday": 0.0586, "Maurice Harkless": 0.0272, "Chimezie Metu": 0.0469, "Davion Mitchell": 0.1516,
        "Marvin Bagley III": 0.0271, "Damian Jones": 0.0659, "Buddy Hield": 0.0664, "Donte DiVincenzo": 0.1353,
    },
    "2022 San Antonio Spurs": {
        "Keldon Johnson": 0.0658, "Dejounte Murray": 0.2644, "Jakob Poeltl": 0.0966, "Doug McDermott": 0.0542,
        "Derrick White": 0.1848, "Devin Vassell": 0.0696, "Joshua Primo": 0.0829, "Keita Bates-Diop": 0.0432,
        "Tre Jones": 0.2048, "Drew Eubanks": 0.0826, "Lonnie Walker IV": 0.0957, "Bryn Forbes": 0.0592,
    },
    "2022 Toronto Raptors": {
        "Scottie Barnes": 0.0989, "Gary Trent Jr.": 0.0571, "Pascal Siakam": 0.1398, "Fred VanVleet": 0.1768,
        "OG Anunoby": 0.0722, "Precious Achiuwa": 0.0466, "Khem Birch": 0.0556, "Chris Boucher": 0.0142,
        "Svi Mykhailiuk": 0.0625, "Malachi Flynn": 0.1311, "Dalano Banton": 0.1376, "Thaddeus Young": 0.0929,
    },
    "2022 Utah Jazz": {
        "Royce O'Neale": 0.0801, "Mike Conley": 0.1853, "Bojan Bogdanović": 0.055, "Donovan Mitchell": 0.1568,
        "Rudy Gobert": 0.0343, "Joe Ingles": 0.1406, "Hassan Whiteside": 0.0223, "Danuel House Jr.": 0.051,
        "Trent Forrest": 0.1406, "Eric Paschall": 0.0472, "Jordan Clarkson": 0.0923, "Rudy Gay": 0.0529,
    },
    "2022 Washington Wizards": {
        "Kentavious Caldwell-Pope": 0.0629, "Kyle Kuzma": 0.1048, "Daniel Gafford": 0.0448, "Spencer Dinwiddie": 0.1921,
        "Bradley Beal": 0.1833, "Corey Kispert": 0.047, "Raul Neto": 0.1582, "Aaron Holiday": 0.1173,
        "Rui Hachimura": 0.0489, "Deni Avdija": 0.0826, "Montrezl Harrell": 0.0864, "Ish Smith": 0.2364,
    },
}
