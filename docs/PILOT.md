# Pilot protocol

October 13, 2026. Proposed feasibility study, not a preregistered confirmatory
experiment. No bugs, probes, model runs, or outcomes have been collected yet.

## Question and estimand

Does selecting a distinguishing executable probe improve independently verified
repair outcomes enough to justify its acquisition cost?

For the first comparison, hold debugging state, candidate generation, solver,
and solver budget fixed. Estimate the marginal effect of receiving a particular
probe observation relative to a matched continuation with no added observation.
This value belongs to a specific continuation policy, model, and budget; it is
not an intrinsic or universal value of the probe.

## Stage 0: audit and three-case rehearsal

Finish the closest-prior-work overlap audit in [LITERATURE.md](LITERATURE.md).
Screen candidates from a frozen SWE-bench-Live snapshot and BugsInPy. Prefer
cases that need runtime investigation, execute deterministically without external
services, and have reliable independent acceptance checks. Do not choose cases
because Skylla already succeeds on them.

Take three cases across different repositories to exercise setup, resetting,
observation extraction, and evaluator isolation. Create four candidate probes
per case. Record every rejected case and why it failed screening. Historical
fixed versions may validate the evaluator but stay out of the agent workspace.

Use two reviewers for probe applicability, prediction specificity, and diagnosis
adjudication when available. If only one reviewer is available, report that limit;
do not claim inter-reviewer reliability. Disputed mechanisms can remain unresolved.

Deliverables: exact task IDs/commits, environment manifests, accepted/excluded cases,
probe contracts, raw runs, reset checks, and a list of failures in the protocol.
Concrete case selection follows execution checks; no IDs are being invented now.

## Stage 1: provisional cohort

Expand to 12 historical bugs across four repositories, four probes per initial
state, and three continuation seeds. Add four controlled fault tasks for missing
hypotheses, interacting causes, misleading observations, and invalid probes.
Keep controlled-task and historical-bug scores separate.

The small cohort discovers feasibility and variance. Four repository clusters
are insufficient for confident broad generalization or a powered effectiveness
claim. Use the pilot to plan a larger held-out study, not to advertise a win.

## Admission and state reset

Require the original failure in three clean repeats and the accepted fixed
reference to pass evaluator checks in clean repeats. Define stability rules before
screening. Record excluded flaky/setup cases and their resource consumption.

A reset manifest covers code, interpreter, packages, fixtures, caches, environment,
processes, writable external resources, and random seeds. Each probe starts from
a fresh isolated state. Verify expected state before and after execution.
Do not run alternative probes sequentially in a contaminated environment.

Independent evaluators run outside the solver workspace. Remove solution-bearing
Git history, future observations, reference patches, and hidden evaluator contents
from generator, selector, and repair inputs. Newly authored cases reduce some
memorization risks but do not prove evaluation cleanliness.

## Candidate contract and freezing

Each candidate specifies preconditions, exact command or script, the inspected or
changed variable, controls, prediction per relevant explanation, extractor,
timeout, reset, and estimated cost. Include setup-failed, timeout, inconclusive,
and unexpected outcomes. Freeze contracts and predictions before viewing results.

Have candidates authored from the buggy state and visible symptom without access
to the reference repair. Candidate-generation cost is shared fairly across
selection-only comparisons and included in end-to-end comparisons. Use a fixed
authoring procedure so outcomes do not decide which candidates enter the menu.

## Branches and labels

For each historical case, execute all four candidate probes. Restore the same
starting state for repair and deliver only the assigned observation, including
failed-probe observations. Pair each with a no-added-observation branch. This
isolates information benefit; it does not measure persistent intervention effects.

Use the same solver configuration and ten-minute continuation cap in all five
branches, with three matched seeds. Pairing reduces some variance; identical seeds
do not guarantee identical trajectories or deterministic provider behavior.

Record independently verified success, elapsed time, tokens, monetary usage when
available, probe cost, and unnecessary edits. Use outcome vectors rather than
prematurely collapsing money, time, and success into an arbitrary score. Uncertain
differences yield ties, not invented ranking labels.

Distinguishing reviewed controlled mechanisms is a secondary label. A historical
patch is evidence of repair, not proof of a unique complete root cause. Model
self-rated confidence and entropy reduction are not ground truth.

## Selection-only baselines

| Policy | Purpose |
| --- | --- |
| Cheapest feasible probe | Establish whether cheap execution alone captures the benefit |
| Seeded random feasible probe | Measure advantage beyond chance on the same menu |
| Deterministic discrimination heuristic | Prefer feasible probes with different predicted outcomes across explanations, then break ties by cost |
| Explicit information-gain policy | Controlled tasks only unless priors/likelihoods can be justified; disclose assumptions |
| Reasoning-model selector | Test whether ordinary reasoning already solves selection |
| Optional fast-model selector | Test cost/quality tradeoffs using identical inputs |

All policies use the same visible information and feasibility rules. Estimated
costs come from development measurements or pre-execution estimates; future test
execution costs cannot leak into live decisions. A retrospective best branch is
descriptive hindsight, not an achievable oracle or unbiased optimum: choosing
the largest noisy observed score overestimates performance.

## End-to-end comparisons after feasibility

Compare an ordinary repair agent, the same agent with a scientific-debugging
prompt and evidence notebook, equivalent runtime tooling without Skylla selection,
and the full Skylla workflow. Hold capabilities and total budgets comparable.
Measure voluntary tool use separately from any forced-use intervention.

Use a provisional 20-minute total cap per run, including candidate generation,
selection, probes, and repair. Record total inference usage and enforce a separately
specified monetary cap when costs are known. Final caps are frozen after rehearsal.
Do not launch paid runs until budget and credential use are authorized.

First isolate the effect with one solver/harness. Later validate across at least
two model families and two harnesses; model/harness independence in the interface
does not demonstrate that performance gains transfer.

## Measurements and failure accounting

Primary confirmatory candidate: verified success under a fixed total budget.
Select the final primary comparison before confirmatory runs. Report success
differences and uncertainty, with task and repository dependence respected.

Secondary measurements: time/cost to success, invalid/redundant probes, false
definitive diagnoses, regression failures, and patch scope. Unsolved tasks remain
in denominators. Treat time-to-success as censored at the cap; avoid a mean over
successful cases alone. Record setup exclusions and preparation costs separately.

For controlled faults, precision can use known injected edits. For natural bugs,
report patch extent and reviewer-adjudicated unnecessary edits rather than exact
match to the reference patch. Do not equate patch minimality with correctness.

## Robustness and splits

Keep all states, forks, variants, and seeds of one bug together. Split by repository
for a later trained selector; include an unseen failure-family evaluation.
Pilot cases are development data and cannot become a repeatedly tuned frozen test.

Test candidate order, consistent ID renaming, duplicate evidence, evidence record
ordering, true-hypothesis omission, and stale-state evidence. Test wrong evidence
attachment as a distinct corruption condition rather than treating it as harmless
renaming. Separate candidate availability from selection success.

With enough repositories in the larger study, use uncertainty estimates that
respect repository clustering. Predefine the analysis and multiple-comparison
treatment. Report pilot estimates descriptively and acknowledge low power.

## Resource model

The historical cohort requires 12 x 4 = 48 probe runs and 12 x 5 x 3 = 180 repair
continuations. At a ten-minute continuation cap, this is up to 30 serial
execution-hours. Probes, resets, preparation, evaluator runs, retries, controlled
tasks, and later end-to-end comparisons add costs. Parallelism reduces elapsed
time, not total work. These are planning quantities, not measured consumption.

Dollar cost is not estimated without the chosen models, token volumes, cache
behavior, hosting, and current rates. Measure the three-case rehearsal first;
set a capped budget before expansion. No model training is needed for this pilot.

## Decision gates

1. Continue only if resets, observation extraction, and independent checks are
   reliable enough to compare branches. Document failures instead of silently
   relabeling them as useless probes.
2. If branches show no meaningful outcome variation, audit candidate quality,
   task difficulty, and solver strength before collecting a large ranker dataset.
3. If cheap selection matches model selection, keep the cheap selector.
4. If the notebook/prompt matches the full workflow, narrow the tool to the
   demonstrated useful component and revise the algorithmic research claim.
5. Plan the confirmatory sample from pilot variance, clustering, and a predefined
   minimum useful effect. Insufficient power remains inconclusive.

Publication does not require a positive result. Product expansion requires
evidence of utility and a separate assessment of developer adoption.
