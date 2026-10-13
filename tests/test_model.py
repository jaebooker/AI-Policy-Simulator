import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policysim import OUTCOMES, Simulation, build, run_many, scenario_ids  # noqa: E402
from policysim.rng import Mulberry32  # noqa: E402


def test_rng_known_values():
    r = Mulberry32(1)
    vals = [r.next() for _ in range(3)]
    # Reference values from the JavaScript implementation.
    assert [round(v, 10) for v in vals] == [0.6270739406, 0.0027357212, 0.52744704]


def test_every_scenario_builds_and_terminates():
    for sid in scenario_ids():
        cfg = build(sid)
        res = Simulation(cfg, 3).run()
        assert res["outcome"] in OUTCOMES
        assert res["steps"] <= cfg["params"]["max_steps"]


def test_same_seed_same_run():
    a = Simulation(build("status_quo"), 42).run()
    b = Simulation(build("status_quo"), 42).run()
    assert a == b


def test_trust_and_safety_stay_bounded():
    sim = Simulation(build("decoupled"), 5)
    sim.run()
    for row in sim.trust:
        assert all(0.0 <= v <= 1.0 for v in row)
    assert all(0.05 <= a["s"] <= 1.0 for a in sim.actors)


def test_shares_sum_to_one():
    s = run_many(build("status_quo"), runs=50)
    assert abs(sum(s["share"].values()) - 1.0) < 1e-9


def test_treaty_beats_status_quo():
    sq = run_many(build("status_quo"), runs=300)
    tr = run_many(build("treaty"), runs=300)
    assert tr["p_good"] > sq["p_good"] + 0.1


def test_verification_raises_coordination():
    lo = run_many(build("status_quo", params={"verification": 0.0}), runs=300)
    hi = run_many(build("status_quo", params={"verification": 1.0}), runs=300)
    assert hi["share"]["safe_coordinated"] > lo["share"]["safe_coordinated"]
    assert hi["mean_coop_share"] > lo["mean_coop_share"]


def test_actor_override_applies():
    cfg = build("status_quo", actor_overrides={"US": {"C": 99}})
    assert cfg["actors"][0]["C"] == 99
