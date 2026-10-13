// Usage: python tests/parity_dump.py 200 > /tmp/py.json && node tests/parity.js /tmp/py.json
const fs = require("fs");
const path = require("path");
const PS = require(path.join(__dirname, "..", "web", "model.js"));
const spec = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data", "scenarios.json")));
const py = JSON.parse(fs.readFileSync(process.argv[2]));
let total = 0, outcomeMismatch = 0, maxErr = 0;
for (const sid of Object.keys(py)) {
  const cfg = PS.build(spec, sid);
  py[sid].forEach((row, k) => {
    const sim = new PS.Simulation(cfg, k + 1);
    const r = sim.run();
    total++;
    if (r.outcome !== row.res.outcome || r.winner !== row.res.winner || r.steps !== row.res.steps || sim.events.length !== row.events) {
      outcomeMismatch++;
      if (outcomeMismatch <= 5) console.log("mismatch", sid, k + 1, r, row.res);
    }
    sim.actors.forEach((a, i) => { maxErr = Math.max(maxErr, Math.abs(a.C - row.C[i])); });
  });
}
console.log(JSON.stringify({ runs: total, mismatches: outcomeMismatch, max_capability_diff: maxErr }));
process.exit(outcomeMismatch ? 1 : 0);
