# AI Policy Simulator

**Research question:** will governments coordinate or compete as they develop transformative AI, and which mechanisms tip the balance?

Governments are agents in a repeated game. Each quarter they choose to cooperate (join a safety bloc, share research, meet a common safety standard) or race (go alone, keep secrets, let safety slip under pressure). Some are secretly deceptive. The run ends when someone crosses the AGI threshold, when a catastrophe happens first, or when time runs out.

**Interactive version:** open `docs/index.html` in a browser, or enable GitHub Pages on the `docs/` folder. It runs the same model as the Python package: the same seed gives the same future in both.

## Quick start

```bash
python simulate.py                                  # status quo, 1000 runs
python simulate.py --all                            # compare every scenario
python simulate.py --scenario classic --single --seed 7    # narrate one run
python simulate.py --sweep verification             # sensitivity sweep
python simulate.py --set export_controls=0.9 --set verification=0.6
python -m pytest tests                              # unit tests
```

No dependencies beyond the standard library (pytest for tests).

## Scenarios (2,000 runs each)

| Scenario | Safe, coordinated | Safe, unilateral | Unsafe arrival | Catastrophe first | Good outcome | Median arrival |
|---|---|---|---|---|---|---|
| Fragmented (Oct 2026) | 28% | 19% | 49% | 4% | 47% | 2032 |
| Incident hotline works | 34% | 18% | 44% | 4% | 52% | 2032 |
| Verifiable compute | 37% | 18% | 40% | 4% | 56% | 2032 |
| Decoupled race | 24% | 26% | 47% | 3% | 49% | 2032 |
| Verified treaty | 76% | 6% | 14% | 4% | 82% | 2032.5 |
| Classic (2021 model) | 19% | 15% | 54% | 12% | 34% | 2033.5 |

What the model currently says, given its assumptions:

- **Verification is the strongest single lever short of a treaty.** Raising it from 0 to 1 moves the good-outcome share from about 47% to 61%, almost all of it through coordinated arrivals. Verification catches deceivers, deters them, and substitutes for trust that low-trust pairs (US-China) do not have.
- **Export controls trade trust for a lead.** Tighter controls widen the leader's margin, which buys time to be careful, but they shrink the bloc. In this calibration the two roughly cancel: Decoupled lands near the status quo, with more unilateral and fewer coordinated arrivals.
- **Binding exit costs matter as much as goodwill.** The treaty scenario works mainly because leaving is expensive and verification is high, not because initial trust is high.
- **Symmetric worlds are the most dangerous.** The Classic setup, with many evenly matched actors, has the highest catastrophe rate because close races erode safety.

These are conditional outputs of a stylized model. Use them to compare levers, not as forecasts.

## Mechanics

Per quarter, in order:

1. **Decisions.** Each actor reconsiders with probability `reconsider`. Its pull toward cooperation is a logistic score of perceived risk, trust in potential partners, research it would gain, the safety tax it would pay to meet the bloc standard, any lead it would give up, and the cost of exiting if already inside. The bloc must accept a newcomer on trust.
2. **Safety.** Honest bloc members converge on `treaty_standard`. Racers erode safety in proportion to how close their nearest rival is.
3. **Growth.** Capability compounds at `g`, minus the safety tax, slowed by export controls for restricted actors, and accelerated past the critical research point (`crp`). Bloc members close part of the gap to the bloc leader (`spillover`).
4. **Deception.** Imposters sit in the bloc, take shared research, skip the safety work and the tax. Spies race and steal research. Each step of deception risks detection at `verification × detect_base`. Exposure zeroes trust in the deceiver, locks it out for `exposure_lockout` quarters, and cuts trust system-wide.
5. **Trust.** Grows between bloc members (faster with verification). Export controls erode restricted actors' trust in controllers.
6. **Hazards.** Warning shots (non-fatal incidents) raise everyone's perceived risk and add `shared_alarm` trust. A catastrophe can end the run; its odds rise with capability, low safety and close races.
7. **Alarm fades** toward `risk_floor` at `risk_decay`. Steps 6 and 7 together are the galvanizing event and enforcement gap of the coordination cycle.
8. **Arrival.** When an actor crosses 100, alignment succeeds with probability based on its true safety, its margin over the nearest rival outside its coalition, and a bonus for arriving inside a genuine coalition.

## 2026 calibration

Actors: United States, China, EU, UK, Japan and Korea, India, Gulf states, Russia. Capability, growth, safety and trust values are stylized starting points meant to reflect the situation in October 2026. All of them live in `data/scenarios.json` and are editable in the web app. The scenarios draw on:

- EU AI Omnibus (in force 27 Jul 2026): general-purpose model obligations stay on schedule; high-risk deadlines slip to Dec 2027 and Aug 2028. [Mondaq](https://www.mondaq.com/eu-digital-omnibus-on-ai-enters-into-force/1825722)
- Jan 2026 US rule allowing conditional sales of H200-class chips to China with caps and a tariff; the Chip Security Act (location verification) still pending. [CASRAI](https://casrai.org/wp/?p=2848)
- June 2026 Commerce export controls on frontier models themselves, later eased for trusted partners. [Mayer Brown](https://www.mayerbrown.com/en/insights/publications/2026/06/commerce-department-extends-export-controls-to-advanced-ai-models-authorizes-release-to-specific-trusted-partners)
- Sept 2026 US-China agreement on a bilateral AI incident channel. [Al Jazeera](https://www.aljazeera.com/news/2026/9/26/china-us-to-open-ai-communication-channel-after-summit-white-house-says)
- First UN Global Dialogue on AI Governance (Jul 2026): no binding outcome; Scientific Panel warns of catastrophic risk. [AI2 Work](https://ai2.work/blog/inside-the-global-dialogue-on-ai-governance-193-nations-one-table)
- 29 countries sign on to the China-led World AI Cooperation Organization (Jul 2026). [Belt and Road Portal](https://ydyl.gansu.gov.cn/enggsydyl/news/topnews/202607/t20260717_38273.html)
- US federal preemption of state AI law unenacted; California SB 53 in effect since Jan 2026. [CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-us-ai-regulation-preemption-compliance-202/)
- US and China hold about 90% of global AI compute. [AI Weekly](https://aiweekly.co/alerts/us-and-china-control-90-of-global-ai-compute-panel-says)
- Evaluations miss dangerous capabilities and most risk management is voluntary. [International AI Safety Report 2026](https://internationalaisafetyreport.org/publication/2026-report-extended-summary-policymakers)

## Layout

```
policysim/      model.py (the model), rng.py, scenarios.py, montecarlo.py
data/           scenarios.json: defaults, actors, trust, scenario presets (shared by Python and web)
web/            model.js (JavaScript port), app.html (interactive page template)
docs/           index.html: built standalone page
scripts/        build_web.py: inlines model.js and scenarios.json into docs/index.html
tests/          test_model.py; parity_dump.py + parity.js check Python and JS agree run for run
simulate.py     command line interface
```

After changing `web/model.js`, `web/app.html` or `data/scenarios.json`, run `python scripts/build_web.py`. After changing either model, run the parity check:

```bash
python tests/parity_dump.py 300 > /tmp/py.json && node tests/parity.js /tmp/py.json
```

## Changes from the 2021 version

- Named actors calibrated to 2026. The original anonymous setup survives as the Classic scenario.
- Explicit safety, catastrophe and alignment. The old model ended only when someone reached 100, so it could not say whether coordination made things safer.
- New mechanics: verification and deterrence, export controls, a pairwise trust network, warning shots and fading alarm, exit costs, the critical research point as recursive acceleration.
- Monte Carlo and sensitivity sweeps (the old `meta_simulator.py` stub, finished).
- Bug fixes: circular imports; `bool("False")` reading as true; global variables inside `create_population`; imposters losing progress instead of gaining it; spies logging every success as a failure; exposed imposters still drawing on the shared pool; a `threshold` method shadowed by an attribute; a broken test.
