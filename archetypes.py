"""Player archetypes worked out from a player's ratings (nobody assigns them by hand).

Each rating is turned into a percentile against every player in the sim (the breakpoints below were measured across all
team files), the percentiles are folded into nine skills, and the archetype is the player's best skill (the noun, which
depends on his position group) plus his second-best skill (the adjective): a guard who is best at playmaking and next best at
shooting is a "Sharpshooting Floor General". A handful of special archetypes (Three-Level Scorer, Unicorn, 3-and-D Wing...)
are checked first for players whose profile is better described as a whole.

`archetype_label(player)` gives the name; `ARCHETYPES` lists every name it can give (well over 100).
This is a label only. The engine's own gameplay archetype (`Player.archetype`, e.g. "three_and_d") is separate.
"""
from bisect import bisect_right

# percentile breakpoints: rating value at the 0, 10, 25, 50, 75, 90, 97 and 100th percentile of every player in the sim
_Q = (0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 0.97, 1.0)
_BREAKS = {
    "three_rating":  (0.00, 0.29, 0.64, 0.79, 0.85, 0.91, 0.93, 1.00),
    "mid_rating":    (0.00, 0.60, 0.72, 0.79, 0.85, 0.90, 0.94, 1.00),
    "rim_rating":    (0.00, 0.76, 0.80, 0.86, 0.90, 0.94, 0.97, 1.00),
    "dunk_rating":   (0.00, 0.42, 0.58, 0.72, 0.82, 0.92, 0.93, 1.00),
    "ft_rating":     (0.00, 0.67, 0.72, 0.77, 0.82, 0.86, 0.90, 1.00),
    "playmaking":    (0.00, 0.26, 0.42, 0.57, 0.70, 0.82, 0.94, 1.00),
    "ball_handle":   (0.00, 0.34, 0.47, 0.59, 0.73, 0.84, 0.92, 1.00),
    "usage":         (0.00, 0.08, 0.11, 0.17, 0.25, 0.31, 0.40, 1.00),
    "perimeter_def": (0.00, 0.54, 0.62, 0.70, 0.79, 0.88, 0.93, 1.00),
    "interior_def":  (0.00, 0.43, 0.52, 0.62, 0.73, 0.84, 0.93, 1.00),
    "steal":         (0.00, 0.33, 0.41, 0.52, 0.65, 0.78, 0.89, 1.00),
    "block":         (0.00, 0.14, 0.37, 0.51, 0.68, 0.83, 0.93, 1.00),
    "oreb":          (0.00, 0.31, 0.37, 0.45, 0.60, 0.78, 0.93, 1.00),
    "dreb":          (0.00, 0.43, 0.50, 0.61, 0.72, 0.87, 0.97, 1.00),
    "speed":         (0.00, 0.60, 0.66, 0.74, 0.80, 0.84, 0.89, 1.00),
    "post_tendency": (0.00, 0.02, 0.03, 0.06, 0.14, 0.29, 0.52, 1.00),
}


def _pct(player, key):
    v = float(getattr(player, key, 0) or 0)
    b = _BREAKS[key]
    i = min(max(bisect_right(b, v) - 1, 0), len(b) - 2)
    lo, hi = b[i], b[i + 1]
    t = 0.0 if hi <= lo else (v - lo) / (hi - lo)
    return max(0.0, min(1.0, _Q[i] + t * (_Q[i + 1] - _Q[i])))


SKILLS = ("shoot", "mid", "finish", "post", "play", "perim", "intd", "reb", "ath")


def skills(player):
    p = lambda k: _pct(player, k)
    return {
        "shoot": p("three_rating"),
        "mid": p("mid_rating"),
        "finish": (p("rim_rating") + p("dunk_rating")) / 2,
        "post": 0.6 * p("post_tendency") + 0.2 * p("rim_rating") + 0.2 * p("mid_rating"),
        "play": (p("playmaking") + p("ball_handle")) / 2,
        "perim": (2 * p("perimeter_def") + p("steal")) / 3,
        "intd": (2 * p("interior_def") + p("block")) / 3,
        "reb": (p("oreb") + 2 * p("dreb")) / 3,
        "ath": (2 * p("speed") + p("dunk_rating")) / 3,
    }


GROUPS = ("guard", "wing", "forward", "big")
_GROUP_OF = {"PG": "guard", "SG": "guard", "SF": "wing", "PF": "forward", "C": "big"}

# best skill -> noun, per position group
NOUNS = {
    "shoot":  {"guard": "Sharpshooter", "wing": "Sniper", "forward": "Stretch Forward", "big": "Stretch Big"},
    "mid":    {"guard": "Pull-Up Shooter", "wing": "Midrange Maestro", "forward": "Face-Up Scorer", "big": "Elbow Shooter"},
    "finish": {"guard": "Slasher", "wing": "Slashing Wing", "forward": "Rim Attacker", "big": "Rim Runner"},
    "post":   {"guard": "Post-Up Guard", "wing": "Post Wing", "forward": "Post Scorer", "big": "Low-Post Anchor"},
    "play":   {"guard": "Floor General", "wing": "Point Wing", "forward": "Point Forward", "big": "Playmaking Big"},
    "perim":  {"guard": "Perimeter Lockdown", "wing": "Wing Stopper", "forward": "Switchable Defender", "big": "Switch Big"},
    "intd":   {"guard": "Help-Side Guard", "wing": "Shot-Blocking Wing", "forward": "Weak-Side Protector", "big": "Rim Protector"},
    "reb":    {"guard": "Rebounding Guard", "wing": "Glass-Crashing Wing", "forward": "Glass Cleaner", "big": "Paint Beast"},
    "ath":    {"guard": "Blur", "wing": "Transition Wing", "forward": "Athletic Forward", "big": "Vertical Threat"},
}
# second-best skill -> adjective
ADJECTIVES = {
    "shoot": "Sharpshooting", "mid": "Shot-Making", "finish": "Slashing", "post": "Post-Up", "play": "Playmaking",
    "perim": "Two-Way", "intd": "Rim-Protecting", "reb": "Glass-Crashing", "ath": "Athletic",
}
_OFFENSE = ("shoot", "mid", "finish", "post", "play")
_DEFENSE = ("perim", "intd")
_GROUP_WORD = {"guard": "Guard", "wing": "Wing", "forward": "Forward", "big": "Big"}


def _ovr(player):
    try:
        import sim_engine
        return float(sim_engine.fantasy_ovr_uncapped(player))
    except Exception:
        return 0.0


def _rules():
    """(name, test) in priority order; the first test that passes names the player. Forward-only ones use group in FWD."""
    FWD = ("wing", "forward")
    W = _GROUP_WORD
    return [
        # the very top: a 100 overall who carries the offense and is elite on defense too (Jordan, peak LeBron)
        ("GOAT", lambda k, g, u, p, o, d, ov: ov >= 99.5 and u >= 0.93 and o >= 0.98 and d >= 0.90),
        # true superstars only: elite at both ends and the man the offense runs through
        ("Two-Way Superstar", lambda k, g, u, p, o, d, ov: ov >= 94 and u >= 0.93 and o >= 0.93 and d >= 0.93),
        ("Unicorn", lambda k, g, u, p, o, d, ov: g in ("forward", "big") and k["shoot"] >= 0.72 and k["intd"] >= 0.85 and k["finish"] >= 0.65),
        ("Heliocentric Engine", lambda k, g, u, p, o, d, ov: u >= 0.95 and k["play"] >= 0.94 and float(getattr(p, "shot_tendency", 0) or 0) >= 0.70
         and sorted((k["shoot"], k["mid"], k["finish"]))[1] >= 0.75),   # and can really score: good at two of threes / midrange / finishing   # runs the offense AND looks for his own shot
        ("Point God", lambda k, g, u, p, o, d, ov: g == "guard" and _pct(p, "playmaking") >= 0.97),
        ("Offensive Juggernaut", lambda k, g, u, p, o, d, ov: ov >= 93 and u >= 0.95 and o >= 0.95 and d < 0.80),
        ("Athletic Freak", lambda k, g, u, p, o, d, ov: k["ath"] >= 0.92 and k["finish"] >= 0.90 and g != "guard"),
        ("Defensive Menace", lambda k, g, u, p, o, d, ov: k["perim"] >= 0.88 and k["intd"] >= 0.82 and u < 0.75),
        # forwards
        ("Do-Everything Forward", lambda k, g, u, p, o, d, ov: g in FWD and u >= 0.85 and k["play"] >= 0.80 and o >= 0.85),
        ("Primary Scoring Forward", lambda k, g, u, p, o, d, ov: g in FWD and u >= 0.90 and sorted((k["shoot"], k["mid"], k["finish"]))[1] >= 0.80),
        ("Stretch Rim Protector", lambda k, g, u, p, o, d, ov: g == "forward" and k["shoot"] >= 0.70 and k["intd"] >= 0.80),
        ("Small-Ball Five", lambda k, g, u, p, o, d, ov: g == "forward" and k["intd"] >= 0.75 and k["reb"] >= 0.75 and k["ath"] >= 0.65 and float(getattr(p, "height", 0) or 0) <= 80),
        ("Two-Way Forward", lambda k, g, u, p, o, d, ov: g in FWD and k["perim"] >= 0.78 and k["intd"] >= 0.72 and max(k["shoot"], k["finish"], k["mid"]) >= 0.72),
        ("Slashing Point Forward", lambda k, g, u, p, o, d, ov: g in FWD and k["play"] >= 0.75 and k["finish"] >= 0.80),
        ("Post Playmaker", lambda k, g, u, p, o, d, ov: g in FWD and k["post"] >= 0.70 and k["play"] >= 0.70),
        ("Bully-Ball Forward", lambda k, g, u, p, o, d, ov: g in FWD and k["post"] >= 0.72 and k["finish"] >= 0.80 and k["reb"] >= 0.60),
        ("Mid-Post Maestro", lambda k, g, u, p, o, d, ov: g in FWD and k["mid"] >= 0.85 and k["post"] >= 0.65),
        ("Mismatch Forward", lambda k, g, u, p, o, d, ov: g in FWD and k["shoot"] >= 0.75 and k["post"] >= 0.62),
        ("Swiss Army Forward", lambda k, g, u, p, o, d, ov: g in FWD and sum(v >= 0.60 for v in k.values()) >= 6),
        ("Floor-Spacing Four", lambda k, g, u, p, o, d, ov: g == "forward" and k["shoot"] >= 0.80 and u <= 0.55),
        ("Connector Forward", lambda k, g, u, p, o, d, ov: g in FWD and k["play"] >= 0.65 and u <= 0.45 and k["perim"] >= 0.60),
        ("Hustle Forward", lambda k, g, u, p, o, d, ov: g in FWD and k["reb"] >= 0.80 and d >= 0.65 and u <= 0.35 and k["shoot"] < 0.60),
        ("Rebounding Machine", lambda k, g, u, p, o, d, ov: g != "big" and k["reb"] >= 0.95),
        # guards
        ("Scoring Point Guard", lambda k, g, u, p, o, d, ov: str(getattr(p, "position", "")) == "PG" and u >= 0.90 and k["play"] >= 0.80 and max(k["shoot"], k["finish"]) >= 0.85),
        ("Defensive Pest", lambda k, g, u, p, o, d, ov: g == "guard" and _pct(p, "steal") >= 0.96 and k["perim"] >= 0.86),
        ("Combo Guard", lambda k, g, u, p, o, d, ov: g == "guard" and k["shoot"] >= 0.84 and k["play"] >= 0.82 and 0.55 <= u < 0.90),
        # bigs
        ("Defensive Anchor", lambda k, g, u, p, o, d, ov: g == "big" and k["intd"] >= 0.90 and k["reb"] >= 0.85 and u < 0.70),
        ("Post Hub", lambda k, g, u, p, o, d, ov: g == "big" and k["play"] >= 0.80 and k["post"] >= 0.75),
        ("Old-School Center", lambda k, g, u, p, o, d, ov: g == "big" and k["post"] >= 0.85 and k["shoot"] < 0.35),
        ("Modern Big", lambda k, g, u, p, o, d, ov: g == "big" and min(k["shoot"], k["play"], k["intd"]) >= 0.60),
        ("Lob Threat", lambda k, g, u, p, o, d, ov: g == "big" and k["finish"] >= 0.90 and k["ath"] >= 0.70 and u <= 0.40),
        # anyone
        ("Three-Level Scorer", lambda k, g, u, p, o, d, ov: u >= 0.82 and min(k["shoot"], k["mid"], k["finish"]) >= 0.70),
        ("Isolation Scorer", lambda k, g, u, p, o, d, ov: u >= 0.90 and _pct(p, "ball_handle") >= 0.85 and o >= 0.85),
        ("3-and-D {W}", lambda k, g, u, p, o, d, ov: g != "big" and k["shoot"] >= 0.65 and k["perim"] >= 0.70 and u <= 0.60),
        ("Spot-Up {W}", lambda k, g, u, p, o, d, ov: u <= 0.25 and k["shoot"] >= 0.80 and k["play"] < 0.45),
        ("Energy {W}", lambda k, g, u, p, o, d, ov: u <= 0.30 and k["ath"] >= 0.75 and k["reb"] >= 0.70 and d >= 0.65),
        ("Glue Guy", lambda k, g, u, p, o, d, ov: max(k.values()) < 0.62 and sum(k.values()) / len(k) >= 0.45),
        ("Depth {W}", lambda k, g, u, p, o, d, ov: max(k.values()) < 0.45),
        ("All-Around {W}", lambda k, g, u, p, o, d, ov: (lambda v: v[0] - v[4] < 0.12 and v[4] >= 0.70)(sorted(k.values(), reverse=True))),
    ]


_RULES = _rules()

# a two-way superstar is named for what he does best on offense (and where he plays)
TWO_WAY = {
    ("play", "guard"): "Two-Way Lead Guard", ("play", "wing"): "Two-Way Point Forward Star", ("play", "forward"): "Two-Way Point Forward Star",
    ("play", "big"): "Two-Way Hub Big",
    ("finish", "guard"): "Two-Way Slashing Star", ("finish", "wing"): "Two-Way Slashing Star", ("finish", "forward"): "Two-Way Freight Train",
    ("finish", "big"): "Two-Way Paint Titan",
    ("mid", "guard"): "Two-Way Shot Creator", ("mid", "wing"): "Two-Way Shot Creator", ("mid", "forward"): "Two-Way Midrange Assassin",
    ("mid", "big"): "Two-Way Midrange Assassin",
    ("shoot", "guard"): "Two-Way Sharpshooting Star", ("shoot", "wing"): "Two-Way Sharpshooting Star", ("shoot", "forward"): "Two-Way Stretch Star",
    ("shoot", "big"): "Two-Way Stretch Star",
    ("post", "guard"): "Two-Way Post Star", ("post", "wing"): "Two-Way Post Star", ("post", "forward"): "Two-Way Post Star",
    ("post", "big"): "Two-Way Paint Titan",
}


def _two_way(sk, group):
    best = max(_OFFENSE, key=lambda k: sk[k])
    if group == "guard" and best == "play" and max(sk["shoot"], sk["mid"], sk["finish"]) >= sk["play"] - 0.02:
        best = max(("shoot", "mid", "finish"), key=lambda k: sk[k])   # a guard who scores as well as he passes is a creator, not a lead guard
    if group in ("wing", "forward") and best != "play" and sk["play"] >= sk[best] - 0.04:
        best = "play"   # a forward who runs the offense nearly as well as he scores is a point forward
    return TWO_WAY[(best, group)]


def _special(sk, group, usage, player):
    off = max(sk[k] for k in _OFFENSE)
    dfn = max(sk[k] for k in _DEFENSE)
    ov = None
    for name, test in _RULES:
        if name in ("GOAT", "Two-Way Superstar", "Offensive Juggernaut"):
            if ov is None:
                ov = _ovr(player)
        if test(sk, group, usage, player, off, dfn, ov if ov is not None else 0.0):
            if name == "Two-Way Superstar":
                return _two_way(sk, group)
            return name.replace("{W}", _GROUP_WORD[group])
    return None


SPECIALS = []
for _name, _t in _RULES:
    SPECIALS += [_name.replace("{W}", _GROUP_WORD[g]) for g in GROUPS] if "{W}" in _name else [_name]
SPECIALS = [x for x in SPECIALS if x not in ("3-and-D Big", "Two-Way Superstar")] + sorted(set(TWO_WAY.values()))

ARCHETYPES = sorted(set(SPECIALS) | {f"{ADJECTIVES[s2]} {NOUNS[s1][g]}" for g in GROUPS for s1 in SKILLS for s2 in SKILLS if s1 != s2})
_COMBOS = {f"{ADJECTIVES[s2]} {NOUNS[s1][g]}" for g in GROUPS for s1 in SKILLS for s2 in SKILLS if s1 != s2}
assert not (_COMBOS & set(TWO_WAY.values())), _COMBOS & set(TWO_WAY.values())   # star names must not collide with everyday ones


def archetype_label(player):
    """The player's archetype name, worked out from his ratings."""
    group = _GROUP_OF.get(str(getattr(player, "position", "") or "").upper(), "wing")
    sk = skills(player)
    usage = _pct(player, "usage")
    special = _special(sk, group, usage, player)
    if special:
        return special
    order = sorted(SKILLS, key=lambda k: sk[k], reverse=True)
    first, second = order[0], order[1]
    return f"{ADJECTIVES[second]} {NOUNS[first][group]}"
