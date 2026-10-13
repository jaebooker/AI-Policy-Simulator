/* AI Policy Simulator model, JavaScript port of policysim/model.py.
 * Mirrors the Python implementation step for step and uses the same Mulberry32
 * generator, so the same seed and config produce the same run in both.
 * Works in the browser (window.PolicySim) and in Node (module.exports). */
(function (root) {
  "use strict";

  var OUTCOMES = ["safe_coordinated", "safe_unilateral", "unsafe_arrival", "catastrophe", "timeout"];

  function Mulberry32(seed) {
    var a = seed >>> 0;
    this.next = function () {
      a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function clamp01(x) { return x < 0 ? 0 : (x > 1 ? 1 : x); }
  function sigmoid(x) { return 1 / (1 + Math.exp(-x)); }
  function copy(o) { return JSON.parse(JSON.stringify(o)); }

  function Simulation(config, seed) {
    if (seed === undefined) seed = 1;
    var p = this.p = Object.assign({}, config.params);
    this.rng = new Mulberry32(seed);
    this.t = 0;
    this.events = [];
    this.history = [];
    this.outcome = null;
    this.winner = null;
    this.arrivalYear = null;
    this.pSafe = null;
    var rnd = this.rng.next;
    this.actors = [];
    for (var k = 0; k < config.actors.length; k++) {
      var spec = config.actors[k];
      var jitC = 1 + p.jitter * (rnd() * 2 - 1);
      var jitG = 1 + p.jitter * 0.5 * (rnd() * 2 - 1);
      var r = rnd();
      var hidden = "honest";
      if (r < p.deception_rate * (1 - p.deterrence * p.verification)) {
        hidden = rnd() < 0.5 ? "imposter" : "spy";
      }
      this.actors.push({
        name: spec.name, short: spec.short,
        C: spec.C * jitC, g: spec.g * jitG,
        s_base: spec.s, s: spec.s,
        restricted: !!spec.restricted, coop: !!spec.coop,
        hidden: hidden, hiddenAtStart: hidden,
        risk: p.risk_init, locked_until: -1, exposed: false
      });
    }
    this.trust = config.trust.map(function (row) { return row.slice(); });
    this.snapshot();
  }

  var S = Simulation.prototype;

  S.year = function () { return this.p.start_year + this.t / this.p.steps_per_year; };
  S.log = function (kind, text, who) {
    this.events.push({ t: this.t, year: Math.round(this.year() * 100) / 100, kind: kind, text: text, who: who });
  };
  S.bloc = function () {
    var out = [];
    for (var i = 0; i < this.actors.length; i++) if (this.actors[i].coop) out.push(i);
    return out;
  };
  S.effTrust = function (i, j) {
    var t = this.trust[i][j];
    return t + this.p.verify_substitute * this.p.verification * (1 - t);
  };
  S.partners = function (i) {
    var a = this.actors, n = a.length, pool = [], out = [], j;
    var bloc = this.bloc().filter(function (q) { return q !== i; });
    if (bloc.length > 0) pool = bloc; else for (j = 0; j < n; j++) if (j !== i) pool.push(j);
    for (var k = 0; k < pool.length; k++) {
      j = pool[k];
      if (this.effTrust(i, j) >= this.p.min_trust && a[j].locked_until < this.t) out.push(j);
    }
    return out;
  };
  S.racePressure = function (i) {
    var a = this.actors, best = 0;
    for (var j = 0; j < a.length; j++) {
      if (j !== i) {
        var v = Math.exp(-Math.abs(a[i].C - a[j].C) / 10);
        if (v > best) best = v;
      }
    }
    return best;
  };
  S.maxCExcept = function (i, members) {
    var m = 0;
    for (var k = 0; k < members.length; k++) {
      var j = members[k];
      if (j !== i && this.actors[j].C > m) m = this.actors[j].C;
    }
    return m;
  };
  S.meanTrust = function () {
    var n = this.actors.length, tot = 0;
    for (var i = 0; i < n; i++) for (var j = 0; j < n; j++) if (i !== j) tot += this.trust[i][j];
    return tot / (n * (n - 1));
  };
  S.snapshot = function () {
    var a = this.actors, risk = 0;
    for (var i = 0; i < a.length; i++) risk += a[i].risk;
    this.history.push({
      t: this.t, year: this.year(),
      C: a.map(function (x) { return x.C; }),
      s: a.map(function (x) { return x.s; }),
      coop: a.map(function (x) { return x.coop; }),
      risk: risk / a.length,
      trust: this.meanTrust(),
      T: this.trust.map(function (row) { return row.slice(); })
    });
  };

  S.step = function () {
    var p = this.p, a = this.actors, n = a.length, rnd = this.rng.next;
    var i, j, k, u, v, all = [];
    for (i = 0; i < n; i++) all.push(i);

    // 1. decisions
    for (i = 0; i < n; i++) {
      var reconsider = rnd();
      var draw = rnd();
      if (reconsider >= p.reconsider || a[i].locked_until >= this.t) {
        if (a[i].locked_until >= this.t) a[i].coop = false;
        continue;
      }
      var parts = this.partners(i), choose;
      if (parts.length === 0) {
        choose = false;
      } else {
        var sumT = 0;
        for (k = 0; k < parts.length; k++) sumT += this.effTrust(i, parts[k]);
        var avgTrust = sumT / parts.length;
        var poolGain = Math.min(1, Math.max(0, this.maxCExcept(i, parts) - a[i].C) / Math.max(a[i].C, 1));
        var lead = (a[i].C - this.maxCExcept(i, all)) / 100;
        var taxBurden = p.safety_tax * Math.max(0, p.treaty_standard - a[i].s_base);
        if (a[i].hidden === "imposter") taxBurden = 0;
        var score = p.w_bias + p.w_risk * a[i].risk + p.w_trust * avgTrust
          + p.w_pool * poolGain - p.w_tax * taxBurden
          - p.w_lead * Math.max(0, lead) * (a[i].C / 100);
        if (a[i].hidden === "spy") score -= 1;
        if (a[i].coop) score += p.exit_cost;
        choose = draw < sigmoid(score);
      }
      if (choose && !a[i].coop) {
        var members = this.bloc().filter(function (q) { return q !== i; });
        var acceptance = 1;
        if (members.length > 0) {
          var sumA = 0;
          for (k = 0; k < members.length; k++) sumA += this.effTrust(members[k], i);
          acceptance = sumA / members.length;
        }
        if (acceptance >= p.min_trust) {
          a[i].coop = true;
          this.log("join", a[i].short + " joins the safety bloc", i);
        }
      } else if (!choose && a[i].coop) {
        a[i].coop = false;
        this.log("defect", a[i].short + " leaves the bloc to race", i);
      }
    }

    var bloc = this.bloc();
    var blocReal = bloc.length >= 2;

    // 2. safety levels (true values)
    for (i = 0; i < n; i++) {
      var honestCoop = a[i].coop && blocReal && a[i].hidden !== "imposter";
      if (honestCoop) {
        var target = Math.max(p.treaty_standard, a[i].s);
        a[i].s += p.convergence * (target - a[i].s);
      } else {
        a[i].s -= p.race_erosion * this.racePressure(i) * a[i].s;
        a[i].s += 0.02 * (a[i].s_base - a[i].s);
      }
      a[i].s = Math.max(0.05, Math.min(1, a[i].s));
    }

    // 3. capability growth, spying, detection
    var dC = [], exposed = [];
    for (i = 0; i < n; i++) {
      var ai = a[i];
      var comp = ai.restricted ? 1 - 0.5 * p.export_controls : 1;
      var paysTax = !(ai.hidden === "imposter" && ai.coop);
      var tax = paysTax ? p.safety_tax * ai.s : 0;
      var crpMult = 1;
      if (ai.C >= p.crp) crpMult = 1 + p.recursive_boost * (ai.C - p.crp) / (p.agi_threshold - p.crp);
      dC[i] = ai.C * ai.g * comp * (1 - tax) * crpMult;
      if (ai.coop && blocReal) dC[i] += p.spillover * Math.max(0, this.maxCExcept(i, bloc) - ai.C);
      var deceiving = false;
      if (ai.hidden === "spy" && !ai.coop && bloc.length > 0) {
        deceiving = true;
        if (rnd() < p.spy_success) {
          var gain = p.spy_gain * Math.max(0, this.maxCExcept(i, bloc) - ai.C);
          dC[i] += gain;
        }
      }
      if (ai.hidden === "imposter" && ai.coop && blocReal) deceiving = true;
      if (deceiving) {
        if (rnd() < p.verification * p.detect_base + 0.01) exposed.push(i);
      }
    }
    for (i = 0; i < n; i++) a[i].C += dC[i];

    for (var e = 0; e < exposed.length; e++) {
      k = exposed[e];
      var kind = a[k].hidden;
      a[k].hidden = "honest";
      a[k].exposed = true;
      a[k].coop = false;
      a[k].locked_until = this.t + p.exposure_lockout;
      for (i = 0; i < n; i++) for (j = 0; j < n; j++) if (i !== j) this.trust[i][j] *= (1 - p.exposure_trust_hit);
      for (i = 0; i < n; i++) if (i !== k) this.trust[i][k] = 0;
      this.log("exposed", a[k].short + " caught acting as " + kind + "; trust collapses", k);
    }

    // 4. trust dynamics
    var verifyFactor = 0.3 + 0.7 * p.verification;
    for (i = 0; i < n; i++) {
      for (j = 0; j < n; j++) {
        if (i === j) continue;
        if (a[i].coop && a[j].coop) this.trust[i][j] += p.trust_growth * verifyFactor * (1 - this.trust[i][j]);
        if (a[i].restricted && !a[j].restricted) this.trust[i][j] -= p.export_trust_cost * p.export_controls;
        this.trust[i][j] = clamp01(this.trust[i][j]);
      }
    }

    // 5. hazards: catastrophe and galvanizing warning shots
    for (i = 0; i < n; i++) {
      var x = a[i].C / p.agi_threshold;
      if (x > 1) x = 1;
      var x2 = x * x;
      var catP = p.catastrophe_rate * x2 * x2 * (1 - a[i].s) * (1 + this.racePressure(i));
      var warnP = p.warning_rate * x2 * (1 - a[i].s);
      var rCat = rnd();
      var rWarn = rnd();
      if (rCat < catP && this.outcome === null) {
        this.outcome = "catastrophe";
        this.winner = i;
        this.log("catastrophe", "Catastrophe originating from " + a[i].short + " AI program", i);
      } else if (rWarn < warnP) {
        for (j = 0; j < n; j++) a[j].risk += p.warning_shock * (1 - a[j].risk);
        for (u = 0; u < n; u++) for (v = 0; v < n; v++) if (u !== v) this.trust[u][v] = clamp01(this.trust[u][v] + p.shared_alarm);
        this.log("warning", "Warning shot: serious incident traced to " + a[i].short, i);
      }
    }

    // 6. alarm fades (the enforcement gap)
    for (i = 0; i < n; i++) a[i].risk += p.risk_decay * (p.risk_floor - a[i].risk);

    this.t += 1;

    // 7. arrival
    if (this.outcome === null) {
      var order = all.slice().sort(function (q1, q2) { return a[q2].C - a[q1].C; });
      var w = order[0];
      if (a[w].C >= p.agi_threshold) {
        var coalition = a[w].coop && this.bloc().length >= 2 && a[w].hidden === "honest";
        var second = 0;
        for (k = 1; k < order.length; k++) {
          var q = order[k];
          if (!(coalition && a[q].coop && a[q].hidden === "honest")) { second = a[q].C; break; }
        }
        var margin = (a[w].C - second) / a[w].C;
        var pSafe = a[w].s * (0.55 + 0.45 * Math.min(1, margin / 0.25));
        if (coalition) pSafe += 0.15;
        pSafe = clamp01(pSafe);
        this.winner = w;
        this.arrivalYear = this.year();
        if (rnd() < pSafe) {
          this.outcome = coalition ? "safe_coordinated" : "safe_unilateral";
          this.log("arrival", a[w].short + " reaches AGI safely" + (coalition ? " inside the coalition" : " alone"), w);
        } else {
          this.outcome = "unsafe_arrival";
          this.log("arrival", a[w].short + " reaches AGI, but alignment fails", w);
        }
        this.pSafe = pSafe;
      }
    }
    if (this.outcome === null && this.t >= p.max_steps) {
      this.outcome = "timeout";
      this.log("timeout", "No AGI within the simulated window", null);
    }
    this.snapshot();
  };

  S.run = function () {
    while (this.outcome === null) this.step();
    return this.result();
  };

  S.result = function () {
    var coopSteps = 0, total = 0;
    for (var h = 1; h < this.history.length; h++) {
      var c = this.history[h].coop;
      for (var i = 0; i < c.length; i++) { total += 1; if (c[i]) coopSteps += 1; }
    }
    var ex = 0, wa = 0;
    for (var e = 0; e < this.events.length; e++) {
      if (this.events[e].kind === "exposed") ex++;
      if (this.events[e].kind === "warning") wa++;
    }
    return {
      outcome: this.outcome,
      winner: this.winner !== null ? this.actors[this.winner].short : null,
      year: Math.round(this.year() * 100) / 100,
      steps: this.t,
      coop_share: total ? coopSteps / total : 0,
      exposures: ex,
      warnings: wa
    };
  };

  // ---------------------------------------------------------------- scenarios
  function build(spec, scenarioId, params, actorOverrides) {
    var scen = spec.scenarios.filter(function (s) { return s.id === scenarioId; })[0];
    var p = Object.assign({}, spec.defaults, scen.params || {}, params || {});
    var actors, trust, n, i, j, idx = {};
    if (scen.world === "generic") {
      var g = spec.generic;
      n = g.count;
      actors = [];
      for (i = 0; i < n; i++) {
        actors.push({ name: "Government " + (i + 1), short: "G" + (i + 1), C: g.C, g: g.g, s: g.s,
          restricted: false, coop: i < Math.round(n * g.coop_fraction) });
      }
      trust = [];
      for (i = 0; i < n; i++) { trust.push([]); for (j = 0; j < n; j++) trust[i].push(i === j ? 0 : g.trust_default); }
    } else {
      var world = spec[scen.world];
      actors = copy(world.actors);
      n = actors.length;
      actors.forEach(function (x, q) { idx[x.short] = q; });
      trust = [];
      for (i = 0; i < n; i++) { trust.push([]); for (j = 0; j < n; j++) trust[i].push(i === j ? 0 : world.trust_default); }
      world.trust_pairs.concat(scen.trust_overrides || []).forEach(function (tp) {
        trust[idx[tp[0]]][idx[tp[1]]] = tp[2];
        trust[idx[tp[1]]][idx[tp[0]]] = tp[2];
      });
    }
    idx = {};
    actors.forEach(function (x, q) { idx[x.short] = q; });
    [scen.actor_overrides || {}, actorOverrides || {}].forEach(function (ov) {
      Object.keys(ov).forEach(function (short) { if (short in idx) Object.assign(actors[idx[short]], ov[short]); });
    });
    return { params: p, actors: actors, trust: trust };
  }

  function runMany(config, runs, seed) {
    runs = runs || 1000; seed = seed || 1;
    var counts = {}, years = [], winners = {}, coop = 0, exposures = 0;
    OUTCOMES.forEach(function (o) { counts[o] = 0; });
    for (var k = 0; k < runs; k++) {
      var r = new Simulation(config, seed + k).run();
      counts[r.outcome] += 1;
      if (r.outcome === "safe_coordinated" || r.outcome === "safe_unilateral" || r.outcome === "unsafe_arrival") {
        years.push(r.year);
        winners[r.winner] = (winners[r.winner] || 0) + 1;
      }
      coop += r.coop_share;
      exposures += r.exposures;
    }
    years.sort(function (x, y) { return x - y; });
    var share = {};
    OUTCOMES.forEach(function (o) { share[o] = counts[o] / runs; });
    var w = {};
    Object.keys(winners).sort(function (x, y) { return winners[y] - winners[x]; }).forEach(function (key) { w[key] = winners[key] / runs; });
    return {
      runs: runs, share: share,
      p_good: (counts.safe_coordinated + counts.safe_unilateral) / runs,
      median_year: years.length ? years[Math.floor(years.length / 2)] : null,
      years: years,
      winners: w,
      mean_coop_share: coop / runs,
      mean_exposures: exposures / runs
    };
  }

  var api = { OUTCOMES: OUTCOMES, Mulberry32: Mulberry32, Simulation: Simulation, build: build, runMany: runMany };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.PolicySim = api;
})(typeof window !== "undefined" ? window : this);
