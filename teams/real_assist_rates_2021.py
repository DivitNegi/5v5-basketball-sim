"""Real 2020-21 assists per minute played (Basketball-Reference: assists per game over minutes per game) for every player on the 2021 teams; the engine paces assists toward each rate over the minutes played."""

REAL_ASSIST_RATE_2021 = {
    "2021 Portland Trail Blazers": {
        "Damian Lillard": 0.2095, "CJ McCollum": 0.1382, "Norman Powell": 0.0552, "Robert Covington": 0.0531,
        "Jusuf Nurkic": 0.1429, "Carmelo Anthony": 0.0612, "Anfernee Simons": 0.0809, "Derrick Jones Jr.": 0.0352,
        "Nassir Little": 0.0376,
    },
    "2021 Milwaukee Bucks": {
        "Jrue Holiday": 0.1889, "Khris Middleton": 0.1617, "Giannis Antetokounmpo": 0.1788, "Brook Lopez": 0.0257,
        "Donte DiVincenzo": 0.1127, "Bobby Portis": 0.0529, "Pat Connaughton": 0.0526, "PJ Tucker": 0.0402,
        "Bryn Forbes": 0.0311, "Jeff Teague": 0.1761,
    },
    "2021 Chicago Bulls": {
        "Patrick Williams": 0.0502, "Zach LaVine": 0.1396, "Coby White": 0.1538, "Nikola Vučević": 0.1196,
        "Lauri Markkanen": 0.0349, "Garrett Temple": 0.0806, "Wendell Carter Jr.": 0.0887, "Thaddeus Young": 0.177,
        "Tomáš Satoranský": 0.2089, "Daniel Theis": 0.072, "Otto Porter Jr.": 0.0926, "Denzel Valentine": 0.1018,
    },
    "2021 Cleveland Cavaliers": {
        "Isaac Okoro": 0.0586, "Collin Sexton": 0.1246, "Darius Garland": 0.1843, "Jarrett Allen": 0.0561,
        "Larry Nance Jr.": 0.0994, "Cedi Osman": 0.1133, "Andre Drummond": 0.09, "Kevin Love": 0.1004,
        "Dean Wade": 0.0625, "Damyean Dotson": 0.1015, "Taurean Prince": 0.1013, "Dylan Windler": 0.0667,
    },
    "2021 Boston Celtics": {
        "Jayson Tatum": 0.1201, "Jaylen Brown": 0.0986, "Marcus Smart": 0.1733, "Kemba Walker": 0.1541,
        "Tristan Thompson": 0.0504, "Daniel Theis": 0.0653, "Semi Ojeleye": 0.0412, "Robert Williams": 0.0952,
        "Grant Williams": 0.0552, "Jeff Teague": 0.116, "Payton Pritchard": 0.0938, "Aaron Nesmith": 0.0345,
    },
    "2021 Los Angeles Clippers": {
        "Reggie Jackson": 0.1348, "Paul George": 0.1543, "Kawhi Leonard": 0.1525, "Marcus Morris": 0.0379,
        "Ivica Zubac": 0.0583, "Terance Mann": 0.0847, "Nicolas Batum": 0.0803, "Luke Kennard": 0.0867,
        "Rajon Rondo": 0.2843, "Patrick Beverley": 0.0933,
    },
    "2021 Memphis Grizzlies": {
        "Kyle Anderson": 0.1319, "Dillon Brooks": 0.0772, "Ja Morant": 0.227, "Jonas Valančiūnas": 0.0636,
        "Grayson Allen": 0.0873, "Desmond Bane": 0.0762, "Brandon Clarke": 0.0667, "Xavier Tillman Sr.": 0.0707,
        "Tyus Jones": 0.2114, "De'Anthony Melton": 0.1244, "Justise Winslow": 0.0974, "John Konchar": 0.0821,
    },
    "2021 Atlanta Hawks": {
        "Trae Young": 0.2789, "Bogdan Bogdanovic": 0.1111, "De'Andre Hunter": 0.0644, "John Collins": 0.041,
        "Clint Capela": 0.0266, "Kevin Huerter": 0.1136, "Danilo Gallinari": 0.0625, "Lou Williams": 0.1619,
        "Cam Reddish": 0.0451, "Onyeka Okongwu": 0.0333,
    },
    "2021 Miami Heat": {
        "Duncan Robinson": 0.0573, "Bam Adebayo": 0.1612, "Jimmy Butler": 0.2113, "Kendrick Nunn": 0.0881,
        "Kelly Olynyk": 0.0781, "Trevor Ariza": 0.0643, "Tyler Herro": 0.1122, "Goran Dragić": 0.1648,
        "Gabe Vincent": 0.0992, "Andre Iguodala": 0.108, "Precious Achiuwa": 0.0413, "Max Strus": 0.0462,
    },
    "2021 Charlotte Hornets": {
        "Terry Rozier": 0.1217, "P.J. Washington": 0.082, "Gordon Hayward": 0.1206, "Devonte' Graham": 0.1788,
        "Bismack Biyombo": 0.0588, "LaMelo Ball": 0.2118, "Cody Zeller": 0.0861, "Miles Bridges": 0.0751,
        "Jalen McDaniels": 0.0573, "Cody Martin": 0.1043, "Caleb Martin": 0.0844, "Malik Monk": 0.1005,
    },
    "2021 Utah Jazz": {
        "Mike Conley": 0.2041, "Donovan Mitchell": 0.1557, "Bojan Bogdanovic": 0.0617, "Royce O'Neale": 0.0791,
        "Rudy Gobert": 0.0422, "Jordan Clarkson": 0.0936, "Joe Ingles": 0.1685, "Derrick Favors": 0.0392,
        "Georges Niang": 0.05, "Miye Oni": 0.0521,
    },
    "2021 Sacramento Kings": {
        "Buddy Hield": 0.105, "Richaun Holmes": 0.0582, "Harrison Barnes": 0.0967, "De'Aaron Fox": 0.2051,
        "Marvin Bagley III": 0.0386, "Tyrese Haliburton": 0.1761, "Maurice Harkless": 0.0562, "Delon Wright": 0.1395,
        "Chimezie Metu": 0.0588, "Hassan Whiteside": 0.0395, "Cory Joseph": 0.1163, "Terence Davis": 0.0791,
    },
    "2021 New York Knicks": {
        "RJ Barrett": 0.086, "Julius Randle": 0.1596, "Reggie Bullock": 0.05, "Elfrid Payton": 0.1356,
        "Nerlens Noel": 0.0289, "Mitchell Robinson": 0.0182, "Alec Burks": 0.0859, "Derrick Rose": 0.1567,
        "Taj Gibson": 0.0385, "Immanuel Quickley": 0.1031, "Obi Toppin": 0.0455, "Kevin Knox": 0.0455,
    },
    "2021 Los Angeles Lakers": {
        "Kentavious Caldwell-Pope": 0.0669, "Dennis Schröder": 0.1807, "LeBron James": 0.2335, "Marc Gasol": 0.1099,
        "Anthony Davis": 0.096, "Kyle Kuzma": 0.0662, "Markieff Morris": 0.0609, "Andre Drummond": 0.0565,
        "Wesley Matthews": 0.0462, "Alex Caruso": 0.1333, "Talen Horton-Tucker": 0.1393, "Montrezl Harrell": 0.048,
    },
    "2021 Orlando Magic": {
        "Dwayne Bacon": 0.0506, "Nikola Vučević": 0.1114, "James Ennis III": 0.0625, "Cole Anthony": 0.1513,
        "Evan Fournier": 0.1221, "Aaron Gordon": 0.1429, "Michael Carter-Williams": 0.1628, "Chuma Okeke": 0.0873,
        "Chasson Randle": 0.0882, "Khem Birch": 0.0556, "Mo Bamba": 0.0506, "Terrence Ross": 0.0785,
    },
    "2021 Dallas Mavericks": {
        "Luka Dončić": 0.2507, "Dorian Finney-Smith": 0.0531, "Josh Richardson": 0.0858, "Kristaps Porziņģis": 0.0518,
        "Maxi Kleber": 0.0522, "Tim Hardaway Jr.": 0.0634, "Dwight Powell": 0.0659, "Willie Cauley-Stein": 0.0409,
        "Jalen Brunson": 0.14, "Josh Green": 0.0614, "James Johnson": 0.0977, "Trey Burke": 0.0884,
    },
    "2021 Brooklyn Nets": {
        "James Harden": 0.2978, "Kyrie Irving": 0.1719, "Kevin Durant": 0.1692, "Joe Harris": 0.0613,
        "DeAndre Jordan": 0.0731, "Blake Griffin": 0.1116, "Bruce Brown": 0.0717, "Jeff Green": 0.0593,
        "Landry Shamet": 0.0696,
    },
    "2021 Denver Nuggets": {
        "Nikola Jokić": 0.2399, "Michael Porter Jr.": 0.0351, "Will Barton": 0.1032, "Jamal Murray": 0.1352,
        "Paul Millsap": 0.0865, "Aaron Gordon": 0.0849, "Gary Harris": 0.0556, "Facundo Campazzo": 0.1644,
        "Monte Morris": 0.126, "PJ Dozier": 0.0826, "Austin Rivers": 0.0967, "JaMychal Green": 0.0466,
    },
    "2021 Indiana Pacers": {
        "Domantas Sabonis": 0.1861, "Malcolm Brogdon": 0.171, "Justin Holiday": 0.0561, "Myles Turner": 0.0323,
        "Caris LeVert": 0.1489, "Doug McDermott": 0.0531, "Edmond Sumner": 0.0556, "Oshae Brissett": 0.0364,
        "Jeremy Lamb": 0.0704, "Aaron Holiday": 0.1067, "T.J. McConnell": 0.2538, "Goga Bitadze": 0.064,
    },
    "2021 New Orleans Pelicans": {
        "Eric Bledsoe": 0.1279, "Brandon Ingram": 0.1429, "Zion Williamson": 0.1114, "Steven Adams": 0.0686,
        "Lonzo Ball": 0.1792, "Nickeil Alexander-Walker": 0.1005, "Willy Hernangómez": 0.0611, "Naji Marshall": 0.1279,
        "Josh Hart": 0.0801, "Jaxson Hayes": 0.0373, "JJ Redick": 0.0699, "Kira Lewis Jr.": 0.1377,
    },
    "2021 Detroit Pistons": {
        "Mason Plumlee": 0.1343, "Jerami Grant": 0.0826, "Saddiq Bey": 0.0513, "Delon Wright": 0.1712,
        "Wayne Ellington": 0.0682, "Josh Jackson": 0.0913, "Killian Hayes": 0.2054, "Isaiah Stewart": 0.0421,
        "Sekou Doumbouya": 0.0516, "Saben Lee": 0.2209, "Frank Jackson": 0.0486, "Svi Mykhailiuk": 0.0909,
    },
    "2021 Toronto Raptors": {
        "Pascal Siakam": 0.1257, "Fred VanVleet": 0.1726, "Kyle Lowry": 0.2098, "OG Anunoby": 0.0661,
        "Norman Powell": 0.0592, "Aron Baynes": 0.0486, "Khem Birch": 0.0625, "Chris Boucher": 0.0455,
        "Malachi Flynn": 0.1472, "Stanley Johnson": 0.0909, "DeAndre' Bembry": 0.1099, "Yuta Watanabe": 0.0552,
    },
    "2021 Houston Rockets": {
        "Jae'Sean Tate": 0.0856, "Christian Wood": 0.0526, "John Wall": 0.2143, "P.J. Tucker": 0.0467,
        "Kelly Olynyk": 0.1318, "Kevin Porter Jr.": 0.1963, "Danuel House Jr.": 0.0734, "Victor Oladipo": 0.1493,
        "Sterling Brown": 0.0581, "Eric Gordon": 0.089, "David Nwaba": 0.0442, "KJ Martin": 0.0464,
    },
    "2021 Philadelphia 76ers": {
        "Danny Green": 0.0607, "Tobias Harris": 0.1077, "Ben Simmons": 0.213, "Seth Curry": 0.0941,
        "Joel Embiid": 0.09, "Mike Scott": 0.0479, "Furkan Korkmaz": 0.0777, "Matisse Thybulle": 0.05,
        "Tyrese Maxey": 0.1307, "Dwight Howard": 0.052, "Shake Milton": 0.1336, "Isaiah Joe": 0.0538,
    },
    "2021 San Antonio Spurs": {
        "Dejounte Murray": 0.1693, "Keldon Johnson": 0.0632, "DeMar DeRozan": 0.2047, "Jakob Poeltl": 0.0712,
        "Lonnie Walker IV": 0.0669, "Derrick White": 0.1182, "LaMarcus Aldridge": 0.0656, "Trey Lyles": 0.0385,
        "Devin Vassell": 0.0529, "Drew Eubanks": 0.0571, "Patty Mills": 0.0968, "Rudy Gay": 0.0648,
    },
    "2021 Phoenix Suns": {
        "Chris Paul": 0.2834, "Devin Booker": 0.1268, "Mikal Bridges": 0.0644, "Jae Crowder": 0.0764,
        "Deandre Ayton": 0.0456, "Cameron Payne": 0.2, "Cameron Johnson": 0.0583, "Torrey Craig": 0.0532,
        "Dario Saric": 0.0747, "Frank Kaminsky": 0.1118,
    },
    "2021 Oklahoma City Thunder": {
        "Darius Bazley": 0.0577, "Luguentz Dort": 0.0572, "Théo Maledon": 0.1277, "Shai Gilgeous-Alexander": 0.1751,
        "Isaiah Roby": 0.0769, "Moses Brown": 0.0093, "Al Horford": 0.1219, "Aleksej Pokusevski": 0.0909,
        "Kenrich Williams": 0.1065, "Svi Mykhailiuk": 0.0783, "Hamidou Diallo": 0.1008, "Ty Jerome": 0.1506,
    },
    "2021 Minnesota Timberwolves": {
        "Anthony Edwards": 0.0903, "Ricky Rubio": 0.2452, "Karl-Anthony Towns": 0.1331, "Josh Okogie": 0.0542,
        "Malik Beasley": 0.0732, "Jarred Vanderbilt": 0.0674, "Jaden McDaniels": 0.0458, "D'Angelo Russell": 0.2035,
        "Naz Reid": 0.0521, "Juancho Hernangómez": 0.0405, "Jordan McLaughlin": 0.2065, "Jaylen Nowell": 0.0829,
    },
    "2021 Golden State Warriors": {
        "Andrew Wiggins": 0.0721, "Stephen Curry": 0.1696, "Draymond Green": 0.2825, "Kelly Oubre Jr.": 0.0423,
        "Kevon Looney": 0.1053, "James Wiseman": 0.0327, "Kent Bazemore": 0.0804, "Juan Toscano-Anderson": 0.134,
        "Jordan Poole": 0.0979, "Mychal Mulder": 0.0312, "Eric Paschall": 0.0747, "Damion Lee": 0.0688,
    },
    "2021 Washington Wizards": {
        "Russell Westbrook": 0.3214, "Bradley Beal": 0.1229, "Rui Hachimura": 0.0444, "Alex Len": 0.0506,
        "Deni Avdija": 0.0515, "Garrison Mathews": 0.0247, "Raul Neto": 0.105, "Robin Lopez": 0.0419,
        "Isaac Bonga": 0.0556, "Dāvis Bertāns": 0.035, "Ish Smith": 0.1857, "Daniel Gafford": 0.0282,
    },
}
