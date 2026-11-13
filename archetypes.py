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


def _special(sk, group, usage, player):
    off = max(sk[k] for k in _OFFENSE)
    dfn = max(sk[k] for k in _DEFENSE)
    if usage >= 0.88 and off >= 0.90 and dfn >= 0.88:
        return "Two-Way Superstar"
    if group in ("forward", "big") and sk["shoot"] >= 0.72 and sk["intd"] >= 0.85 and sk["finish"] >= 0.65:
        return "Unicorn"
    if usage >= 0.93 and sk["play"] >= 0.92:
        return "Heliocentric Engine"
    if group == "guard" and _pct(player, "playmaking") >= 0.97:
        return "Point God"
    if usage >= 0.82 and min(sk["shoot"], sk["mid"], sk["finish"]) >= 0.70:
        return "Three-Level Scorer"
    if usage >= 0.85 and sk["play"] >= 0.80 and off >= 0.85 and group in ("wing", "forward"):
        return "Do-Everything Forward"
    if group == "big" and sk["intd"] >= 0.90 and sk["reb"] >= 0.85 and usage < 0.70:
        return "Defensive Anchor"
    if group == "big" and sk["play"] >= 0.80 and sk["post"] >= 0.75:
        return "Post Hub"
    if usage >= 0.90 and _pct(player, "ball_handle") >= 0.85 and off >= 0.85:
        return f"Isolation Scorer"
    if group != "big" and sk["shoot"] >= 0.65 and sk["perim"] >= 0.70 and usage <= 0.60:
        return f"3-and-D {_GROUP_WORD[group]}"
    if usage <= 0.25 and sk["shoot"] >= 0.80 and sk["play"] < 0.45:
        return f"Spot-Up {_GROUP_WORD[group]}"
    if usage <= 0.30 and sk["ath"] >= 0.75 and sk["reb"] >= 0.70 and dfn >= 0.65:
        return f"Energy {_GROUP_WORD[group]}"
    vals = sorted(sk.values(), reverse=True)
    if vals[0] < 0.62 and sum(vals) / len(vals) >= 0.45:
        return "Glue Guy"
    if vals[0] < 0.45:
        return f"Depth {_GROUP_WORD[group]}"
    if vals[0] - vals[4] < 0.12 and vals[4] >= 0.70:
        return f"All-Around {_GROUP_WORD[group]}"
    return None


SPECIALS = ["Two-Way Superstar", "Unicorn", "Heliocentric Engine", "Point God", "Three-Level Scorer", "Do-Everything Forward",
            "Defensive Anchor", "Post Hub", "Isolation Scorer", "Glue Guy"]
SPECIALS += [f"{w} {_GROUP_WORD[g]}" for w in ("3-and-D",) for g in ("guard", "wing", "forward")]
SPECIALS += [f"{w} {_GROUP_WORD[g]}" for w in ("Spot-Up", "Energy", "Depth", "All-Around") for g in GROUPS]

ARCHETYPES = sorted(set(SPECIALS) | {f"{ADJECTIVES[s2]} {NOUNS[s1][g]}" for g in GROUPS for s1 in SKILLS for s2 in SKILLS if s1 != s2})


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
