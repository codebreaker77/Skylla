# Research paper plan

October 13, 2026. Planning document. No manuscript results or publication claims
exist yet. The target venue will follow the contribution and evidence rather
than determine which result we report.

## Working question

When does selecting a debugging experiment improve verified repair outcomes
under a fixed budget, and can a lightweight policy capture that value across
models and harnesses?

Working title: **Choosing the Next Debugging Experiment: A Controlled Study of
Probe Utility in Repository Repair**. This title is provisional and does not
claim an improvement before measurement.

## Possible contributions

| Contribution | Evidence required |
| --- | --- |
| Reproducible competing-probe corpus | Frozen states, independently executed alternatives, reliable resets, raw outcomes, permitted artifacts |
| Measurement of probe utility | Matched repair continuations, no-added-observation controls, cost accounting, policy-specific uncertainty |
| Selection comparison | Fixed candidate sets, fair baselines, leakage controls, held-out evaluation |
| Transfer analysis | Multiple model families/harnesses with matched protocols and separately reported effects |
| Practical developer utility | Separate user study; benchmark success cannot establish adoption |

The scientific-debugging loop, use of debuggers, evidence logs, and generic value
prediction are established prior work. A corpus is not automatically a novel
contribution: finish the overlap audit and show what it enables beyond available
artifacts. No "first," state-of-the-art, or moat claim is supported now.

## Research questions

1. Do feasible probes from one state differ in downstream repair benefit after
   acquisition cost is included?
2. Which cheap or model-based policies select useful probes, and when do they fail?
3. Are gains due to selection, candidate generation, runtime access, evidence
   organization, additional inference, or enforced tool use?
4. How do effects change across repositories, failure families, solvers, and harnesses?
5. Can the workflow abstain and preserve uncertainty when candidates or hypotheses
   are inadequate?

Question 1 is the initial feasibility focus. A small pilot cannot answer all five.
Narrow the paper to what the eventual study can actually support.

## Required controls

Keep candidate generation fixed in selection-only runs. Compare equivalent
runtime access and an evidence-notebook prompt in end-to-end runs. Use independent
hidden acceptance/regression checks. Keep all bug variants in the same split,
hide solution history, and account for preparation, retries, probes, and inference.

Precommit the primary comparison, exclusions, budget, stopping conditions,
sample-size rationale, and analysis before the confirmatory study. Do not select
the strongest-looking metric or model after inspecting the held-out results.
Disclose contamination limits and provider nondeterminism.

## Artifact package

- Dataset manifests with task provenance, commits, environment identity, licenses,
  inclusion/exclusion reasons, and split assignment.
- Versioned candidate contracts and predictions recorded before execution.
- Raw probe outputs, extracted observations, state fingerprints, and reset checks.
- Continuation configurations, seeds, trajectories, patches, costs, and evaluator results.
- Baseline implementations, exact prompts, model versions, usage records, and analysis scripts.
- Reproduction instructions and machine-readable tables behind every reported figure.

Release original code under the repository license. Third-party repositories and
datasets retain their licenses; distribute permitted manifests/build recipes when
redistributing source or environment images is not permitted. Publish an artifact
availability statement describing anything that cannot be released.

## Manuscript structure

Problem and motivation; related work and overlap; task/formalization; corpus and
probe protocol; policies and baselines; experimental design; results; failure
analysis and ablations; threats to validity; artifact availability; implications.

Keep findings, explanations of findings, and future proposals distinguishable.
Report negative and inconclusive comparisons, including cases where probes waste
budget or misleading observations worsen repair.

## Next milestone

Complete the prior-art audit and three-case rehearsal in [PILOT.md](PILOT.md), then
publish a feasibility report with actual manifests and measured costs. Only then
freeze a larger study, consider learning a selector, and begin a results manuscript.
