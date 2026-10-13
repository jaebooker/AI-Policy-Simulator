"""Dump seeded runs from the Python model for tests/parity.js to compare against."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from policysim import Simulation, build, scenario_ids  # noqa: E402

SEEDS = int(sys.argv[1]) if len(sys.argv) > 1 else 200
out = {}
for sid in scenario_ids():
    cfg = build(sid)
    rows = []
    for seed in range(1, SEEDS + 1):
        sim = Simulation(cfg, seed)
        res = sim.run()
        rows.append({"res": res, "C": [a["C"] for a in sim.actors], "events": len(sim.events)})
    out[sid] = rows
print(json.dumps(out))
