"""Ratings editor: read a player's ratings straight from his team file and write edits back into that file.

The team files are plain Python: each player is a `Player('Name', 'POS', <22 numbers>, keyword=value, ...)` call inside a
`make_<team>_<year>()` function. Reading uses the file's own literals (not the built Player, which the engine adjusts at load time),
and writing replaces only the argument text that changed, so the rest of the file (comments, layout, other players) is untouched.
After a save the team module is reloaded and every reference to its old factory functions is swapped for the new ones, so the
app uses the new ratings straight away, and a restart reads them from the file.
"""
import ast
import importlib
import inspect
import sys
import types

import archetypes
import sim_engine

# the 24 positional fields of Player, in order (see sim_engine.Player)
POSITIONAL = [
    "name", "position",
    "three_tendency", "mid_tendency", "drive_tendency", "post_tendency", "dunk_tendency", "shot_tendency",
    "three_rating", "mid_rating", "rim_rating", "dunk_rating", "ft_rating",
    "usage", "playmaking", "ball_handle",
    "steal", "block", "oreb", "dreb", "foul_draw", "foul_rate",
    "perimeter_def", "interior_def",
]
KEYWORDS = ["clutchness", "secondary_positions", "badges", "rookie", "height", "speed", "stamina", "shot_iq", "iso_tendency", "archetype", "go_to_shot"]
TENDENCIES = ("three_tendency", "mid_tendency", "drive_tendency", "post_tendency", "dunk_tendency", "shot_tendency", "iso_tendency")
EDITABLE = [k for k in POSITIONAL[1:] + KEYWORDS if k not in TENDENCIES and k not in ("archetype", "usage")]   # the archetype is worked out from the ratings   # tendencies are not shown and cannot be changed here
POSITIONS = ("PG", "SG", "SF", "PF", "C")

# how the editor lays the fields out (label, field, kind)
GROUPS = [
    ("Shooting & finishing", [("3-pt", "three_rating", "unit"), ("Midrange", "mid_rating", "unit"), ("Rim", "rim_rating", "unit"),
                              ("Dunk", "dunk_rating", "unit"), ("Free throw", "ft_rating", "unit"), ("Shot IQ", "shot_iq", "unit")]),
    ("Playmaking", [("Playmaking", "playmaking", "unit"), ("Ball handle", "ball_handle", "unit")]),
    ("Defense & rebounding", [("Perimeter D", "perimeter_def", "unit"), ("Interior D", "interior_def", "unit"), ("Steal", "steal", "unit"),
                              ("Block", "block", "unit"), ("Off. rebound", "oreb", "unit"), ("Def. rebound", "dreb", "unit")]),
    ("Other", [("Draws fouls", "foul_draw", "unit"), ("Foul rate", "foul_rate", "unit"), ("Clutch", "clutchness", "unit"),
               ("Speed", "speed", "unit"), ("Stamina", "stamina", "unit"), ("Height (inches)", "height", "int"),
               ("Position", "position", "pos"), ("Other positions", "secondary_positions", "positions"),
               ("Rookie", "rookie", "bool")]),
]


def _factory(runner, team):
    fn = runner.factories.get(team)
    if fn is None or not isinstance(fn, types.FunctionType):
        raise ValueError("That team is not in the team files.")
    return inspect.unwrap(fn)   # the factories are wrapped by real_stat_calibration; the Player entries live in the original


def _locate(fn, name):
    """(path, source text, ast.Call node of this player's Player(...) entry) inside the team's factory function."""
    path = inspect.getsourcefile(fn)
    with open(path, encoding="utf-8", newline="") as fh:   # newline="": keep the file's own line endings
        text = fh.read()
    tree = ast.parse(text)
    func = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == fn.__name__), None)
    if func is None:
        raise ValueError(f"Could not find {fn.__name__} in {path}.")
    for node in ast.walk(func):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "Player" and node.args:
            first = node.args[0]
            if isinstance(first, ast.Constant) and first.value == name:
                return path, text, node
    raise ValueError(f"{name} is not written as a Player(...) entry in {fn.__name__}, so he has to be edited by hand.")


def _literal(node):
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def _values(call):
    vals = {}
    for i, arg in enumerate(call.args[: len(POSITIONAL)]):
        vals[POSITIONAL[i]] = _literal(arg)
    for kw in call.keywords:
        if kw.arg:
            vals[kw.arg] = _literal(kw.value)
    return vals


def _build(values):
    kwargs = {k: v for k, v in values.items() if k in POSITIONAL or k in KEYWORDS}
    p = sim_engine.Player(**kwargs)
    return p


def _played(team, values):
    """The player as the engine plays him: file values plus every fallback (speed, shot IQ, height, stamina, star clutch)."""
    p = _build(values)
    try:
        sim_engine.apply_star_clutchness(types.SimpleNamespace(name=team, roster=[p]))
    except Exception:
        pass
    return p


def _overall(team, values):
    return round(sim_engine.fantasy_ovr(_played(team, values)))


# ratings the engine fills in when a file leaves them out (or, for clutch, leaves it at the 0.50 default)
FALLBACK_KEYS = ("speed", "shot_iq", "clutchness", "height", "stamina")


def _with_fallbacks(team, values):
    """(values with the engine's fallback numbers filled in, the keys that came from a fallback)"""
    p = _played(team, values)
    out, filled = dict(values), []
    for k in FALLBACK_KEYS:
        eff = getattr(p, k, None)
        if eff is None:
            continue
        eff = int(round(eff)) if k == "height" else round(float(eff), 2)
        if values.get(k) is None or (values.get(k) != eff and k == "clutchness"):
            out[k] = eff
            filled.append(k)
    return out, filled, archetypes.archetype_label(p)


def read(runner, team, name):
    fn = _factory(runner, team)
    path, _text, call = _locate(fn, name)
    vals = _values(call)
    rel = path.replace("\\", "/").split("/5v5_sim/")[-1]
    try:
        orig = original(runner, team, name)   # values from before the editor changed him (None if it has not), for the revert buttons
    except Exception:
        orig = None
    shown, filled, arch = _with_fallbacks(team, vals)
    if orig is not None:
        orig = _with_fallbacks(team, orig)[0]
    return {"team": team, "name": name, "file": rel, "function": fn.__name__, "values": shown, "original": orig, "overall": _overall(team, vals),
            "fallbacks": filled, "archetype": arch,
            "groups": [{"title": t, "fields": [{"label": l, "key": k, "kind": kind} for l, k, kind in fs]} for t, fs in GROUPS]}


def _clean(changes):
    out = {}
    for key, value in (changes or {}).items():
        if key not in EDITABLE:
            continue
        if key == "position":
            value = str(value).upper()
            if value not in POSITIONS:
                raise ValueError("Position must be PG, SG, SF, PF or C.")
        elif key == "secondary_positions":
            value = tuple(p for p in (str(x).upper() for x in (value or [])) if p in POSITIONS)
        elif key == "badges":
            value = tuple(str(x) for x in (value or []))
        elif key in ("archetype", "go_to_shot"):
            value = str(value or "")
        elif key == "rookie":
            value = bool(value)
        elif key == "height":
            value = int(round(float(value)))
            if not 60 <= value <= 96:
                raise ValueError("Height must be between 60 and 96 inches.")
        else:
            value = round(float(value), 3)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{key} must be between 0 and 1.")
        out[key] = value
    return out


def preview(runner, team, name, changes):
    fn = _factory(runner, team)
    _path, _text, call = _locate(fn, name)
    vals = _values(call)
    vals.update(_clean(changes))
    return {"overall": _overall(team, vals), "archetype": archetypes.archetype_label(_played(team, vals))}


def _source(value):
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".") if value not in (0.0, 1.0) else f"{value:.2f}"
    if isinstance(value, tuple):
        return "(" + ", ".join(repr(v) for v in value) + ("," if len(value) == 1 else "") + ")"
    return repr(value)


def _source_like(value, old_src):
    """Write a number the way the file already writes it there (0.860 stays three places, 0.86 two), so only the digits change."""
    if isinstance(value, float) and isinstance(old_src, str) and "." in old_src and old_src.replace(".", "", 1).isdigit():
        places = len(old_src.split(".")[1])
        out = f"{value:.{places}f}"
        return out if abs(float(out) - value) < 1e-9 else f"{value:.3f}"
    return _source(value)


def _offsets(text):
    """ast gives (line, UTF-8 byte column); turn that into an index into the text (names like Dončić make bytes and characters differ)."""
    lines = text.splitlines(keepends=True)
    starts, pos = [0], 0
    for line in lines:
        pos += len(line)
        starts.append(pos)
    return lambda lineno, col: starts[lineno - 1] + len(lines[lineno - 1].encode("utf-8")[:col].decode("utf-8", errors="ignore"))


def save(runner, team, name, changes):
    fn = _factory(runner, team)
    path, text, call = _locate(fn, name)
    vals = _values(call)
    changes = {k: v for k, v in _clean(changes).items() if vals.get(k) != v}
    if not changes:
        return {"saved": False, "message": "Nothing changed.", **read(runner, team, name)}
    snaps, key = _snaps(), _snap_key(fn, name)
    if key not in snaps:   # first editor change to this player: remember what he was, so Reset can bring it back
        snaps[key] = vals
        _write_snaps(snaps)
    off = _offsets(text)
    edits = []   # (start, end, replacement)
    kw_nodes = {kw.arg: kw for kw in call.keywords if kw.arg}
    to_append = []
    for key, value in changes.items():
        if key in POSITIONAL or key in kw_nodes:
            node = call.args[POSITIONAL.index(key)] if key in POSITIONAL else kw_nodes[key].value
            a, b = off(node.lineno, node.col_offset), off(node.end_lineno, node.end_col_offset)
            edits.append((a, b, _source_like(value, text[a:b])))
        else:
            to_append.append(f"{key}={_source(value)}")
    if to_append:   # new keyword arguments go just before the closing parenthesis
        last = (call.keywords[-1].value if call.keywords else call.args[-1])
        at = off(last.end_lineno, last.end_col_offset)
        edits.append((at, at, ", " + ", ".join(to_append)))
    for start, end, rep in sorted(edits, key=lambda e: e[0], reverse=True):
        text = text[:start] + rep + text[end:]
    compile(text, path, "exec")   # never write a file that would not load
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    _reload(fn)
    if hasattr(runner, "factories"):
        _refresh_factories(runner)
    return {"saved": True, "changed": sorted(changes), "message": f"Saved to {read(runner, team, name)['file']}.", **read(runner, team, name)}


def _reload(old_fn):
    """Reload the edited team module and point every reference to its old factory functions at the new ones (also the
    real_stat_calibration wrappers, which hold the old function inside them, and factory registries kept in dicts)."""
    global _SWAP
    mod = sys.modules[old_fn.__module__]
    old = {k: v for k, v in vars(mod).items() if isinstance(v, types.FunctionType) and v.__module__ == mod.__name__}
    new_mod = importlib.reload(mod)
    _SWAP = {id(f): getattr(new_mod, k) for k, f in old.items() if hasattr(new_mod, k)}
    for m in list(sys.modules.values()):
        d = getattr(m, "__dict__", None)
        if not isinstance(d, dict) or m is new_mod:
            continue
        for k, v in list(d.items()):
            nv = _replacement(v)
            if nv is not None:
                d[k] = nv
            elif isinstance(v, dict) and k.isupper():
                for kk, vv in list(v.items()):
                    nvv = _replacement(vv)
                    if nvv is not None:
                        v[kk] = nvv


_SWAP = {}


def _replacement(v):
    if not isinstance(v, types.FunctionType):
        return None
    if id(v) in _SWAP:
        return _SWAP[id(v)]
    inner = getattr(v, "__wrapped__", None)
    if inner is not None and id(inner) in _SWAP:
        import real_stat_calibration as rsc
        w = rsc._wrap(_SWAP[id(inner)])
        w._real_stat_wrapped = True
        return w
    return None


def _refresh_factories(runner):
    for team, fn in list(runner.factories.items()):
        nv = _replacement(fn)
        if nv is not None:
            runner.factories[team] = nv
    try:   # cached rankings and positions were built from the old ratings
        from . import server, stats
        server._STRENGTH_CACHE.clear()
        server._ALL_ROSTER_CACHE.clear()
        stats._POS_CACHE.clear()
    except Exception:
        pass


# "Original" = a player's values from just before the editor first changed him. Edits made by hand (VS Code etc.) are never
# undone: a player the editor has not touched has no snapshot, so there is nothing to reset. Kept in a small JSON file next to this one.
import json as _json
import os as _os
_SNAP_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "ratings_originals.json")


def _snaps():
    try:
        with open(_SNAP_PATH, encoding="utf-8") as fh:
            return _json.load(fh)
    except Exception:
        return {}


def _write_snaps(d):
    with open(_SNAP_PATH, "w", encoding="utf-8") as fh:
        _json.dump(d, fh, indent=1, ensure_ascii=False, sort_keys=True)


def _snap_key(fn, name):
    rel = inspect.getsourcefile(fn).replace("\\", "/").split("/5v5_sim/")[-1]
    return f"{rel}::{fn.__name__}::{name}"


def original(runner, team, name):
    """This player's values from before the editor first changed him (None if the editor has not changed him)."""
    snap = _snaps().get(_snap_key(_factory(runner, team), name))
    if snap is None:
        return None
    return {k: (tuple(v) if isinstance(v, list) and k in ("secondary_positions", "badges") else v) for k, v in snap.items()}


def _remove_keywords(runner, team, name, keys):
    """Take keyword arguments the editor added (e.g. speed=) back out of the player's entry."""
    fn = _factory(runner, team)
    path, text, call = _locate(fn, name)
    off = _offsets(text)
    items = list(call.args) + list(call.keywords)
    cuts = []
    for i, kw in enumerate(call.keywords):
        if kw.arg in keys:
            prev = items[len(call.args) + i - 1]
            pv = prev.value if isinstance(prev, ast.keyword) else prev
            cuts.append((off(pv.end_lineno, pv.end_col_offset), off(kw.value.end_lineno, kw.value.end_col_offset)))
    if not cuts:
        return
    for a, b in sorted(cuts, reverse=True):
        text = text[:a] + text[b:]
    compile(text, path, "exec")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    _reload(fn)
    if hasattr(runner, "factories"):
        _refresh_factories(runner)


def reset(runner, team, name):
    """Put this one player back to how he was before the editor first changed him. Hand edits to the file are left alone."""
    old = original(runner, team, name)
    if old is None:
        return {"saved": False, "message": f"{name} has not been changed in the ratings editor, so there is nothing to reset.", **read(runner, team, name)}
    now = _values(_locate(_factory(runner, team), name)[2])
    changes = {k: v for k, v in old.items() if k in EDITABLE and now.get(k) != v}
    added = [k for k in now if k in EDITABLE and k not in old]   # ratings the editor wrote in that the entry did not have before
    if changes:
        save(runner, team, name, changes)
    if added:
        _remove_keywords(runner, team, name, added)
    snaps = _snaps()
    snaps.pop(_snap_key(_factory(runner, team), name), None)   # back to where he started: no longer counts as edited
    _write_snaps(snaps)
    n = len(changes) + len(added)
    msg = f"{name} reset to his ratings from before the editor changed him ({n} value{'s' if n != 1 else ''})." if n else f"{name} already has his original ratings."
    return {"saved": bool(n), "message": msg, **read(runner, team, name)}