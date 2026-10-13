# Controlled probe repair: observations and decision

October 13, 2026. **Calibration did not improve recovery over the cheapest
normalization baseline in this controlled study, and it used more target calls.**
This is a negative result for adding this calibration step to these fixtures,
not a general result about debugging agents or all experiment-repair methods.

## Method and run provenance

The [method](METHODOLOGY.md), [protocol](protocol.json), programs, policies, and
apparatus tests were frozen in commit `ad93c26` before the comparative run.
Protocol freeze: 05:23:55 UTC. Execution: 05:24:02 to 05:25:07 UTC. Study wall
time was 65.17 seconds with three workers on Windows/Python 3.9.5.

Four original fault families, seven probe conditions, fault present/absent,
three menu permutations, and five deterministic policies produced 840 episodes.
These comprise 56 controlled cells, not 840 independent bugs. Each policy had
84 fault-present and 84 fault-absent episodes, with eight target calls per episode.
One calibration triplet consumed three calls. Apparatus validation touched the
constructed cases before freezing, so this is development evidence.

All 840 episodes completed; none timed out or failed infrastructure setup.
The run made 4,960 policy target calls and 4,024 additional reference-evaluation
calls. Reference evaluation occurred after policy completion and was not charged
to policy budget. Full records and the exact environment are in
[episodes.jsonl](results/run-001/episodes.jsonl) and
[summary.json](results/run-001/summary.json).

## Primary outcome

A recovered probe must show the specified failure in the current workspace and
satisfy that specification on the separate reference implementation. This is a
diagnostic discriminator, not a generated production repair.

| Policy | Recovered / 84 fault-present episodes | Recovery | Mean target calls over all 168 episodes | Mean calls in fault-present episodes |
| --- | ---: | ---: | ---: | ---: |
| Blind search | 36 / 84 | 42.9% | 7.14 | 6.29 |
| Input-first sweep | 60 / 84 | 71.4% | 5.81 | 5.33 |
| Normalize then sweep | 72 / 84 | 85.7% | 3.62 | 2.67 |
| Always calibrate | 72 / 84 | 85.7% | 6.69 | 5.81 |
| Conditional calibration | 72 / 84 | 85.7% | 6.26 | 4.95 |

Normalization used 608 target calls versus 1,052 for conditional calibration:
42.2% fewer calls with identical recovery in all 84 matched positive episodes.
Do not interpret this as a 42.2% wall-time reduction. Subprocess totals per arm
were approximately 35-36 seconds; startup/other overhead dominates these tiny
targets. Calibration savings need evaluation on realistic execution costs.

## Paired observations

The [post-run analysis](results/run-001/analysis.json) matches on family, condition,
fault state, and menu-order seed. Its public-input check confirms identical menus
and initial probes across arms in every matched cell.

| Conditional calibration compared with | Positive wins / losses / ties | Mean additional calls over 168 matched episodes |
| --- | ---: | ---: |
| Blind search | 36 / 0 / 48 | -0.88 |
| Input-first sweep | 12 / 0 / 72 | +0.45 |
| Normalize then sweep | 0 / 0 / 84 | +2.64 |
| Always calibrate | 0 / 0 / 84 | -0.43 |

Conditional execution avoids 72 calls relative to always calibrating, but adds
444 relative to normalization. The narrower ablation benefit does not establish
that calibration is useful relative to the strongest cheap comparator.

Each normalization/calibration policy recovered all 72 positive episodes in the
six repairable conditions. Every policy failed all 12 positive masked-result
episodes. Input-first sweep additionally failed all 12 source-plus-observer
cases; blind search varied strongly by ordering, recovering 24/28, 4/28, and 8/28
positive episodes across the three seeds. This small order sample is not an
estimate of general randomized-search performance.

## Observation 1: a useful route can still be unnecessarily expensive

For configuration precedence with both wrong source and observer, the conditional
policy's seed-101 trace is:

| Call | Action | Observation |
| --- | --- | --- |
| 1 | Run fallback source, observe status | `ok`; wrong source |
| 2 | Switch to workspace, observe status | `ok`; expected source |
| 3 | Calibration clean replay | `ok` |
| 4 | Overwrite result with a sentinel | Still `ok` |
| 5 | Change unobserved metadata | Still `ok` |
| 6 | Switch observation to result | `disk`, violating environment-precedence specification |

The reference returns `env`, confirming the discriminator. Routing recovered the
probe, but normalization reached the same result in two calls by fixing source
and observer together. The common interface already exposes these canonical
choices, so calibration does not buy information needed for this decision.

## Observation 2: a passing control is local evidence

Both calibration arms returned a sensitive control on all 12 positive masked
cases per arm, yet none recovered the fault. The masking wrapper substitutes the
expected value upstream of the sentinel injection. The collector sees the
sentinel, while remaining blind to the original program result.

This was a deliberately constructed stress case, not an unexpected discovery or
an estimate of its frequency in real agents. It demonstrates the specified
control's limited scope. It does not establish that all controls are ineffective.
No policy treated calibration as a root-cause conclusion or global adequacy proof.

There were zero false completions across the 420 fault-absent episodes. This
follows under explicit fixture specifications and conservative submission rules;
it is not a false-positive estimate for an LLM or naturally ambiguous symptoms.

## Interpretation and next experiment

Keep normalization as the default comparator and a candidate simple workflow.
The result does not justify adding this control triplet as a general default.
It also does not support a breakthrough or agent-repair superiority claim.

The main unresolved assumption is that the useful observer and correct source
are already known and cheap to select. A stronger follow-up should measure how
often real diagnostic probes require discovering a different observation point,
tracing an unintended mock, or restoring missing state. First audit development
trajectories to establish whether these problems occur and incur meaningful cost.

If that audit supports another mechanism experiment, use source-derived candidate
observers and real execution costs, keep normalization and the strongest simple
alternatives, and test controls at the hypothesized effect site as well as the
collector. Require a fresh uninstrumented replay so that instrumentation-induced
behavior does not become a success label. Those changes are proposals for a new
version; v1 method, records, and outcomes remain frozen.

## Limits

- Finite hand-authored menus always contain the useful input/observer for the six
  repairable conditions; automatic generation and discovery were not tested.
- Four programs share one structural search problem. They do not provide four
  independent demonstrations of broad generalization.
- The action space cannot remove the masking wrapper. Failure there exposes this
  limitation, not comparative superiority of any arm.
- Specifications, instrumentation, fixtures, and reference code were authored in
  the same project. No independent reviewer adjudicated the mechanisms.
- The information boundary is a fixed-policy API, not an adversarial sandbox.
- These are study heuristics, not published-system reproductions or the Skylla
  CLI's current pair-count selector. No model, native harness, or repair ran.

## Reproduce and verify

```sh
python tools/study/probe_repair/study.py verify --name run-001
python tools/study/analyze_probe_repair.py
python tools/study/probe_repair/study.py run --name reproduction --workers 3
```

Use a new run name; recorded runs cannot be overwritten. Hash verification
checked the frozen sources, all 840 local raw logs, extracted observations,
unique episode directories, budget accounting, complete case coverage, and
aggregate consistency. All 21 repository tests passed before the freeze,
including five apparatus checks. The analysis is descriptive and was written
after the run under the outcomes specified in the frozen method.
