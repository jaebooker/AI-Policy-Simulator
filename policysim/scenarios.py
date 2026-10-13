"""Load scenario presets from data/scenarios.json and turn them into run configs."""

import copy
import json
import os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "scenarios.json")


def load(path=DATA):
    with open(path) as f:
        return json.load(f)


def scenario_ids(spec=None):
    spec = spec or load()
    return [s["id"] for s in spec["scenarios"]]


def build(scenario_id="status_quo", params=None, actor_overrides=None, spec=None):
    """Return {"params", "actors", "trust"} for a scenario, with optional overrides.

    params: dict of global parameter overrides.
    actor_overrides: {short_name: {field: value}} applied after the scenario's own overrides.
    """
    spec = spec or load()
    scen = next(s for s in spec["scenarios"] if s["id"] == scenario_id)
    p = dict(spec["defaults"])
    p.update(scen.get("params", {}))
    if params:
        p.update(params)

    if scen["world"] == "generic":
        g = spec["generic"]
        n = g["count"]
        actors = []
        for i in range(n):
            actors.append({
                "name": "Government " + str(i + 1),
                "short": "G" + str(i + 1),
                "C": g["C"], "g": g["g"], "s": g["s"],
                "restricted": False,
                "coop": i < int(round(n * g["coop_fraction"])),
            })
        trust = [[0.0 if i == j else g["trust_default"] for j in range(n)] for i in range(n)]
    else:
        world = spec[scen["world"]]
        actors = copy.deepcopy(world["actors"])
        idx = {a["short"]: k for k, a in enumerate(actors)}
        n = len(actors)
        trust = [[0.0 if i == j else world["trust_default"] for j in range(n)] for i in range(n)]
        for x, y, v in world["trust_pairs"] + scen.get("trust_overrides", []):
            trust[idx[x]][idx[y]] = v
            trust[idx[y]][idx[x]] = v

    idx = {a["short"]: k for k, a in enumerate(actors)}
    for overrides in (scen.get("actor_overrides", {}), actor_overrides or {}):
        for short, fields in overrides.items():
            actors[idx[short]].update(fields)
    return {"params": p, "actors": actors, "trust": trust}
