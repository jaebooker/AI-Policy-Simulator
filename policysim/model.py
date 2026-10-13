"""Core model for the AI Policy Simulator.

Each actor is a government (or bloc) developing advanced AI. Every quarter it
decides whether to cooperate (join the safety bloc, share research, accept a
common safety standard) or race (go alone, keep secrets, cut safety under
pressure). Some actors are secretly deceptive:

* imposter: appears to cooperate and receives shared research, but keeps its
  own safety low and skips the safety tax.
* spy: races openly but steals research from the bloc.

Verification controls how quickly deception is caught. Getting caught destroys
trust in the deceiver and dents trust across the whole system.

The run ends when an actor crosses the AGI threshold, when a catastrophe
happens first, or when time runs out. Arrival is judged safe or unsafe from the
winner's true safety level, its lead over the runner-up (time to be careful),
and whether it arrived inside a genuine coalition.

The JavaScript port in web/model.js mirrors this file line for line and uses
the same random number generator, so a given seed produces the same run in both.
"""

import math

from .rng import Mulberry32

OUTCOMES = [
    "safe_coordinated",
    "safe_unilateral",
    "unsafe_arrival",
    "catastrophe",
    "timeout",
]


def clamp01(x):
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


class Simulation:
    def __init__(self, config, seed=1):
        self.p = dict(config["params"])
        self.rng = Mulberry32(seed)
        self.t = 0
        self.events = []
        self.history = []
        self.outcome = None
        self.winner = None
        self.arrival_year = None

        p = self.p
        rnd = self.rng.next
        self.actors = []
        for spec in config["actors"]:
            jit_c = 1.0 + p["jitter"] * (rnd() * 2.0 - 1.0)
            jit_g = 1.0 + p["jitter"] * 0.5 * (rnd() * 2.0 - 1.0)
            r = rnd()
            hidden = "honest"
            if r < p["deception_rate"] * (1.0 - p["deterrence"] * p["verification"]):
                hidden = "imposter" if rnd() < 0.5 else "spy"
            self.actors.append({
                "name": spec["name"],
                "short": spec["short"],
                "C": spec["C"] * jit_c,
                "g": spec["g"] * jit_g,
                "s_base": spec["s"],
                "s": spec["s"],
                "restricted": bool(spec["restricted"]),
                "coop": bool(spec["coop"]),
                "hidden": hidden,
                "risk": p["risk_init"],
                "locked_until": -1,
                "exposed": False,
            })
        self.trust = [list(row) for row in config["trust"]]
        self.snapshot()

    # ------------------------------------------------------------------ helpers
    def year(self):
        return self.p["start_year"] + self.t / self.p["steps_per_year"]

    def log(self, kind, text):
        self.events.append({"t": self.t, "year": round(self.year(), 2), "kind": kind, "text": text})

    def bloc(self):
        return [i for i, a in enumerate(self.actors) if a["coop"]]

    def partners(self, i):
        """Actors i would cooperate with: trusted, not locked out, and in the bloc if one exists."""
        a = self.actors
        bloc = [j for j in self.bloc() if j != i]
        pool = bloc if len(bloc) > 0 else [j for j in range(len(a)) if j != i]
        out = []
        for j in pool:
            if self.eff_trust(i, j) >= self.p["min_trust"] and a[j]["locked_until"] < self.t:
                out.append(j)
        return out

    def eff_trust(self, i, j):
        """Trust plus what verification can substitute for: you need less faith in what you can check."""
        t = self.trust[i][j]
        return t + self.p["verify_substitute"] * self.p["verification"] * (1.0 - t)

    def race_pressure(self, i):
        a = self.actors
        best = 0.0
        for j in range(len(a)):
            if j != i:
                v = math.exp(-abs(a[i]["C"] - a[j]["C"]) / 10.0)
                if v > best:
                    best = v
        return best

    def max_c_except(self, i, members):
        m = 0.0
        for j in members:
            if j != i and self.actors[j]["C"] > m:
                m = self.actors[j]["C"]
        return m

    def snapshot(self):
        self.history.append({
            "t": self.t,
            "year": self.year(),
            "C": [a["C"] for a in self.actors],
            "s": [a["s"] for a in self.actors],
            "coop": [a["coop"] for a in self.actors],
            "risk": sum(a["risk"] for a in self.actors) / len(self.actors),
            "trust": self.mean_trust(),
        })

    def mean_trust(self):
        n = len(self.actors)
        tot = 0.0
        for i in range(n):
            for j in range(n):
                if i != j:
                    tot += self.trust[i][j]
        return tot / (n * (n - 1))

    # --------------------------------------------------------------------- step
    def step(self):
        p = self.p
        a = self.actors
        n = len(a)
        rnd = self.rng.next

        # 1. decisions
        for i in range(n):
            reconsider = rnd()
            draw = rnd()
            if reconsider >= p["reconsider"] or a[i]["locked_until"] >= self.t:
                if a[i]["locked_until"] >= self.t:
                    a[i]["coop"] = False
                continue
            parts = self.partners(i)
            if len(parts) == 0:
                choose = False
            else:
                avg_trust = sum(self.eff_trust(i, j) for j in parts) / len(parts)
                pool_gain = min(1.0, max(0.0, self.max_c_except(i, parts) - a[i]["C"]) / max(a[i]["C"], 1.0))
                lead = (a[i]["C"] - self.max_c_except(i, range(n))) / 100.0
                tax_burden = p["safety_tax"] * max(0.0, p["treaty_standard"] - a[i]["s_base"])
                if a[i]["hidden"] == "imposter":
                    tax_burden = 0.0
                score = (p["w_bias"] + p["w_risk"] * a[i]["risk"] + p["w_trust"] * avg_trust
                         + p["w_pool"] * pool_gain - p["w_tax"] * tax_burden
                         - p["w_lead"] * max(0.0, lead) * (a[i]["C"] / 100.0))
                if a[i]["hidden"] == "spy":
                    score -= 1.0
                if a[i]["coop"]:
                    score += p["exit_cost"]
                choose = draw < sigmoid(score)
            if choose and not a[i]["coop"]:
                members = [j for j in self.bloc() if j != i]
                if len(members) > 0:
                    acceptance = sum(self.eff_trust(j, i) for j in members) / len(members)
                else:
                    acceptance = 1.0
                if acceptance >= p["min_trust"]:
                    a[i]["coop"] = True
                    self.log("join", a[i]["short"] + " joins the safety bloc")
            elif (not choose) and a[i]["coop"]:
                a[i]["coop"] = False
                self.log("defect", a[i]["short"] + " leaves the bloc to race")

        bloc = self.bloc()
        bloc_real = len(bloc) >= 2

        # 2. safety levels (true values)
        for i in range(n):
            honest_coop = a[i]["coop"] and bloc_real and a[i]["hidden"] != "imposter"
            if honest_coop:
                target = max(p["treaty_standard"], a[i]["s"])
                a[i]["s"] += p["convergence"] * (target - a[i]["s"])
            else:
                a[i]["s"] -= p["race_erosion"] * self.race_pressure(i) * a[i]["s"]
                a[i]["s"] += 0.02 * (a[i]["s_base"] - a[i]["s"])
            a[i]["s"] = max(0.05, min(1.0, a[i]["s"]))

        # 3. capability growth, spying, detection
        dC = [0.0] * n
        exposed = []
        for i in range(n):
            ai = a[i]
            comp = 1.0 - 0.5 * p["export_controls"] if ai["restricted"] else 1.0
            pays_tax = not (ai["hidden"] == "imposter" and ai["coop"])
            tax = p["safety_tax"] * ai["s"] if pays_tax else 0.0
            crp_mult = 1.0
            if ai["C"] >= p["crp"]:
                crp_mult = 1.0 + p["recursive_boost"] * (ai["C"] - p["crp"]) / (p["agi_threshold"] - p["crp"])
            dC[i] = ai["C"] * ai["g"] * comp * (1.0 - tax) * crp_mult
            if ai["coop"] and bloc_real:
                dC[i] += p["spillover"] * max(0.0, self.max_c_except(i, bloc) - ai["C"])
            deceiving = False
            if ai["hidden"] == "spy" and not ai["coop"] and len(bloc) > 0:
                deceiving = True
                if rnd() < p["spy_success"]:
                    dC[i] += p["spy_gain"] * max(0.0, self.max_c_except(i, bloc) - ai["C"])
            if ai["hidden"] == "imposter" and ai["coop"] and bloc_real:
                deceiving = True
            if deceiving:
                if rnd() < p["verification"] * p["detect_base"] + 0.01:
                    exposed.append(i)
        for i in range(n):
            a[i]["C"] += dC[i]

        for k in exposed:
            kind = a[k]["hidden"]
            a[k]["hidden"] = "honest"
            a[k]["exposed"] = True
            a[k]["coop"] = False
            a[k]["locked_until"] = self.t + p["exposure_lockout"]
            for i in range(n):
                for j in range(n):
                    if i != j:
                        self.trust[i][j] *= (1.0 - p["exposure_trust_hit"])
            for i in range(n):
                if i != k:
                    self.trust[i][k] = 0.0
            self.log("exposed", a[k]["short"] + " caught acting as " + kind + "; trust collapses")

        # 4. trust dynamics
        verify_factor = 0.3 + 0.7 * p["verification"]
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if a[i]["coop"] and a[j]["coop"]:
                    self.trust[i][j] += p["trust_growth"] * verify_factor * (1.0 - self.trust[i][j])
                if a[i]["restricted"] and not a[j]["restricted"]:
                    self.trust[i][j] -= p["export_trust_cost"] * p["export_controls"]
                self.trust[i][j] = clamp01(self.trust[i][j])

        # 5. hazards: catastrophe and galvanizing warning shots
        for i in range(n):
            x = a[i]["C"] / p["agi_threshold"]
            if x > 1.0:
                x = 1.0
            x2 = x * x
            cat_p = p["catastrophe_rate"] * x2 * x2 * (1.0 - a[i]["s"]) * (1.0 + self.race_pressure(i))
            warn_p = p["warning_rate"] * x2 * (1.0 - a[i]["s"])
            r_cat = rnd()
            r_warn = rnd()
            if r_cat < cat_p and self.outcome is None:
                self.outcome = "catastrophe"
                self.winner = i
                self.log("catastrophe", "Catastrophe originating from " + a[i]["short"] + " AI program")
            elif r_warn < warn_p:
                for j in range(n):
                    a[j]["risk"] += p["warning_shock"] * (1.0 - a[j]["risk"])
                for u in range(n):
                    for v in range(n):
                        if u != v:
                            self.trust[u][v] = clamp01(self.trust[u][v] + p["shared_alarm"])
                self.log("warning", "Warning shot: serious incident traced to " + a[i]["short"])

        # 6. alarm fades (the enforcement gap)
        for i in range(n):
            a[i]["risk"] += p["risk_decay"] * (p["risk_floor"] - a[i]["risk"])

        self.t += 1

        # 7. arrival
        if self.outcome is None:
            order = sorted(range(n), key=lambda q: -a[q]["C"])
            w = order[0]
            if a[w]["C"] >= p["agi_threshold"]:
                coalition = a[w]["coop"] and len(self.bloc()) >= 2 and a[w]["hidden"] == "honest"
                # Margin = breathing room to be careful. Inside a genuine coalition the
                # race that matters is against the strongest actor outside it.
                second = 0.0
                for q in order[1:]:
                    if not (coalition and a[q]["coop"] and a[q]["hidden"] == "honest"):
                        second = a[q]["C"]
                        break
                margin = (a[w]["C"] - second) / a[w]["C"]
                p_safe = a[w]["s"] * (0.55 + 0.45 * min(1.0, margin / 0.25))
                if coalition:
                    p_safe += 0.15
                p_safe = clamp01(p_safe)
                self.winner = w
                self.arrival_year = self.year()
                if rnd() < p_safe:
                    self.outcome = "safe_coordinated" if coalition else "safe_unilateral"
                    self.log("arrival", a[w]["short"] + " reaches AGI safely" + (" inside the coalition" if coalition else " alone"))
                else:
                    self.outcome = "unsafe_arrival"
                    self.log("arrival", a[w]["short"] + " reaches AGI, but alignment fails")
                self.p_safe = p_safe
        if self.outcome is None and self.t >= p["max_steps"]:
            self.outcome = "timeout"
            self.log("timeout", "No AGI within the simulated window")
        self.snapshot()

    def run(self):
        while self.outcome is None:
            self.step()
        return self.result()

    def result(self):
        coop_steps = 0
        total = 0
        for h in self.history[1:]:
            for c in h["coop"]:
                total += 1
                if c:
                    coop_steps += 1
        return {
            "outcome": self.outcome,
            "winner": self.actors[self.winner]["short"] if self.winner is not None else None,
            "year": round(self.year(), 2),
            "steps": self.t,
            "coop_share": coop_steps / total if total else 0.0,
            "exposures": sum(1 for e in self.events if e["kind"] == "exposed"),
            "warnings": sum(1 for e in self.events if e["kind"] == "warning"),
        }
