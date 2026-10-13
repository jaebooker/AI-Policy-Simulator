"""Monte Carlo runs and one-parameter sensitivity sweeps."""

from .model import OUTCOMES, Simulation


def run_many(config, runs=1000, seed=1):
    counts = {o: 0 for o in OUTCOMES}
    years = []
    winners = {}
    coop = 0.0
    exposures = 0
    for k in range(runs):
        r = Simulation(config, seed + k).run()
        counts[r["outcome"]] += 1
        if r["outcome"] in ("safe_coordinated", "safe_unilateral", "unsafe_arrival"):
            years.append(r["year"])
            winners[r["winner"]] = winners.get(r["winner"], 0) + 1
        coop += r["coop_share"]
        exposures += r["exposures"]
    years.sort()
    return {
        "runs": runs,
        "share": {o: counts[o] / runs for o in OUTCOMES},
        "p_good": (counts["safe_coordinated"] + counts["safe_unilateral"]) / runs,
        "median_year": years[len(years) // 2] if years else None,
        "winners": {w: c / runs for w, c in sorted(winners.items(), key=lambda kv: -kv[1])},
        "mean_coop_share": coop / runs,
        "mean_exposures": exposures / runs,
    }


def sweep(build_fn, param, values, runs=400, seed=1):
    """build_fn(params_override) -> config. Returns one summary per value."""
    out = []
    for v in values:
        summary = run_many(build_fn({param: v}), runs=runs, seed=seed)
        summary["value"] = v
        out.append(summary)
    return out
