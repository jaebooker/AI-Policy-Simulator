"""Command line entry point.

Examples:
    python simulate.py                              # status quo, 1000 runs
    python simulate.py --scenario treaty --runs 2000
    python simulate.py --scenario classic --single --seed 7   # narrate one run
    python simulate.py --sweep verification         # sensitivity sweep
    python simulate.py --all                        # compare every scenario
    python simulate.py --set export_controls=0.9 --set verification=0.6
"""

import argparse
import json

from policysim import OUTCOMES, Simulation, build, run_many, scenario_ids, sweep

LABELS = {
    "safe_coordinated": "Safe arrival, coordinated",
    "safe_unilateral": "Safe arrival, unilateral",
    "unsafe_arrival": "Unsafe arrival",
    "catastrophe": "Catastrophe before AGI",
    "timeout": "No AGI in window",
}


def parse_sets(items):
    out = {}
    for item in items or []:
        k, v = item.split("=", 1)
        out[k] = float(v)
    return out


def print_summary(name, s):
    print("\n== " + name + " (" + str(s["runs"]) + " runs)")
    for o in OUTCOMES:
        bar = "#" * int(round(s["share"][o] * 40))
        print("  {:<28} {:>5.1%}  {}".format(LABELS[o], s["share"][o], bar))
    print("  P(good outcome)              {:>5.1%}".format(s["p_good"]))
    print("  Median arrival year          {}".format(s["median_year"]))
    print("  Avg share of actor-quarters cooperating {:.0%}".format(s["mean_coop_share"]))
    print("  Avg deceivers exposed per run {:.2f}".format(s["mean_exposures"]))
    print("  Who gets there first: " + ", ".join("{} {:.0%}".format(w, v) for w, v in s["winners"].items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenario", default="status_quo", choices=scenario_ids())
    ap.add_argument("--runs", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--set", action="append", help="override a parameter, e.g. verification=0.6")
    ap.add_argument("--single", action="store_true", help="narrate one run")
    ap.add_argument("--sweep", help="parameter to sweep from 0 to 1")
    ap.add_argument("--all", action="store_true", help="compare all scenarios")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = ap.parse_args()
    overrides = parse_sets(args.set)

    if args.single:
        sim = Simulation(build(args.scenario, params=overrides), args.seed)
        res = sim.run()
        if args.json:
            print(json.dumps({"result": res, "events": sim.events, "history": sim.history}))
            return
        hidden = [a["short"] + ":" + a["hidden"] for a in sim.actors if a["hidden"] != "honest"]
        for e in sim.events:
            print("  {:.2f}  {:<12} {}".format(e["year"], e["kind"], e["text"]))
        print("\nOutcome: {} ({}), {:.2f}".format(LABELS[res["outcome"]], res["winner"], res["year"]))
        if hidden:
            print("Still-hidden deceivers at the end: " + ", ".join(hidden))
        return

    if args.sweep:
        vals = [round(k / 10, 2) for k in range(11)]
        out = sweep(lambda o: build(args.scenario, params=dict(overrides, **o)), args.sweep, vals,
                    runs=args.runs, seed=args.seed)
        if args.json:
            print(json.dumps(out))
            return
        print("Sweep of {} in scenario {} ({} runs per point)".format(args.sweep, args.scenario, args.runs))
        print("  value  P(good)  coordinated  catastrophe")
        for o in out:
            print("  {:>5}  {:>6.1%}  {:>11.1%}  {:>10.1%}".format(o["value"], o["p_good"],
                  o["share"]["safe_coordinated"], o["share"]["catastrophe"]))
        return

    targets = scenario_ids() if args.all else [args.scenario]
    results = {s: run_many(build(s, params=overrides), runs=args.runs, seed=args.seed) for s in targets}
    if args.json:
        print(json.dumps(results))
        return
    for s, r in results.items():
        print_summary(s, r)


if __name__ == "__main__":
    main()
