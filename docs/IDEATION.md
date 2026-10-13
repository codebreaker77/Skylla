# Research ideation: repair the investigation

October 13, 2026. A research proposal supported by design counterexamples, not a
breakthrough claim. This memo extends the [study plan](NEXT_STUDY.md) and narrows
the prior suggestion to discover missing causes. No external model runs were made.

Follow-up: the [controlled mechanism study](../experiments/probe-repair/REPORT.md)
has now run. Simple normalization matched both calibration policies on recovery
and used fewer target calls. Its deliberately masked observer also passed the
narrow control while hiding the fault. This limits the case for calibration;
automatic observer discovery and real agent-repair benefit remain untested.

## The proposed question

**Can a debugging tool distinguish an inadequate experiment from an inadequate
explanation, and spend its next action repairing the right one?**

An experiment includes setup, intervention, observation, and interpretation.
Changing its input is only one possible repair. A useful controller might instead
change the reset procedure, remove an unintended mock, observe retained state,
or revise a causal explanation. The value must come from making these choices
well enough to improve verified repairs at a fixed total budget.

Current Skylla checks caller-declared preconditions and missing control tags. It
does not establish them through executable evidence or construct experiment
repairs. The proposal is therefore a new research branch, not an existing feature.

## What survived the first ideation round

| Candidate | Pressure test | Decision |
| --- | --- | --- |
| Hypothesis notebook plus runtime tools | AutoSD and current harnesses already overlap | Keep as baseline/product infrastructure |
| Expand candidates when progress stalls | ConcoLixir already uses failure/plateau-triggered discovery | Insufficient standalone novelty |
| Reach omitted paths using source traces | ConcoLLMic and concolic testing already do path exploration | Reuse/compare, rather than rename |
| Infer metamorphic relations and shrink failures | AI4MT and DDMT already address these mechanisms | Optional backend; generated relations need validation |
| Score probes using code mutations | Mutation testing and EvoOtter directly overlap | Strong baseline, not a new core claim |
| Flag evidence that would also pass on buggy code | BSG-VA already studies replay feedback | Strong evidence-quality baseline |
| Store an evidence dependency graph | PACMI and other provenance/invalidation work overlap | Defer beyond coarse validity |
| Choose between generation, execution, and repair by budget | Active diagnosis and planning have substantial precedent | Necessary evaluation dimension; no novelty by itself |
| Repair setup/intervention/observation before revising explanations | Technically overlaps testing and diagnosis, but fits our concrete failure modes | Lead empirical research question |
| Make decisions invariant to duplicated hypothesis wording | Current scorer fails a constructed example; standard weighted inference addresses related issues | Required robustness check, not a breakthrough |

These are dispositions from this search, not claims that the literature is
exhausted. The leading proposal still needs direct comparison with active
diagnosis, test-harness synthesis, mutation-guided test repair, and sensor planning.

## Three reproducible challenges to the current direction

Run `python tools/study/check_ideation.py`. The tracked
[design checks](../experiments/ideation/design-checks.json) contain these results.
They are not the four controlled fault tasks planned for the evaluation.

### 1. A null observation does not identify what went wrong

For a deliberately simplified deterministic model, let `H` mean a real contrast
exists, `R` that the intervention reaches it, and `O` that the observer transmits
it. The visible contrast is `Y = H * R * O`.

Of the eight Boolean worlds, seven yield `Y = 0`. Both `H = 0` and `H = 1` are
compatible with that observation. Therefore no function of `Y` alone can always
tell an absent contrast from a failed intervention or an insensitive observer.
This is an elementary identifiability example, not a new theorem. Real systems
also have noise, confounding, and interactions, which this model omits.

Verified checks of reach and observation can remove some ambiguity. The truth
table does not implement those checks or grant access to latent `R` and `O`.
The actual engineering challenge is to obtain informative checks cheaply without
assuming the correct cause or seeing a reference fix.

### 2. Our Tornado data contains an observation bottleneck

Post-hoc projection of the existing tornado-6 batch gives:

| Probe | Native loops closed, buggy/fixed | Registry delta, buggy/fixed |
| --- | --- | --- |
| Single close | true / true | 1 / 0 |
| Repeated close | true / true | 10 / 0 |
| Garbage collection | true / true | 10 / 0 |
| Native close | true / true | 10 / 1 |

The native-closure field differs in zero of four pairs; the registry field differs
in all four. This illustrates why varying inputs while retaining an inadequate
observer can fail to expose a distinction. The existing full probe already
records both fields. We selected this projection after seeing results; no system
has automatically discovered the missing observation, and no fresh executions
or diagnostic-success labels are implied. The residual fixed native-close entry
also prevents a blanket claim that every registry effect is eliminated.

The earlier tqdm case supplies a different failure: all candidates explicitly
supplied width, missing the default path. A method that handles only observation
repair or only input expansion cannot cover both development examples.

### 3. Hypothesis count is not a stable information measure

For hypotheses A/B/C, probe-a isolates A and costs 1; probe-c isolates C and costs
1.25. Both split two pairs, so today's controller selects probe-a. Add an alias
of C with identical predictions and no new causal explanation: probe-a splits
three pairs; probe-c splits four, so the decision flips to probe-c.

This is a reproduced limitation in `contrast_count`, not a repair-performance
result. The schema cannot express alias semantics. Deduplicating every identical
prediction vector is not a complete solution: distinct real hypotheses can be
indistinguishable under a limited menu. A later design must represent known
aliases or justify a weighting scheme, and test invariance when a hypothesis is
split into synonyms with conserved weight. Calibrated probabilities are not
available merely because the model supplies numbers.

## Proposed mechanism: check and repair the experiment

Treat a proposed experiment as `(setup, intervention, observer, prediction)`.
Attach candidate evidence checks to a specific claim, rather than a universal
"valid experiment" flag. The same probe can support one claim while remaining
uninformative about another.

1. Reproduce the reported failure and record the actual code/environment state.
2. Have the configured generator propose an experiment and the change it expects
   to cause. Extract measurable checks from code, traces, and that contract.
3. Check whether the intended condition actually occurred: which import was
   loaded, whether the branch executed, whether a cache entry was removed, or
   whether an update reached the intended object.
4. Where feasible, assess the observer with a narrowly scoped positive control
   in a disposable copy. For a retained-entry claim, create a known retained
   entry and check whether the chosen observation responds. Include an unchanged
   replay and a suitable placebo to expose incidental failures.
5. If a relevant check fails, propose a bounded repair to setup, intervention,
   or observation. Record and rerun it. If checks support the intended experiment
   but observations conflict with predictions, consider revising predictions or
   expanding explanations. Unknown checks preserve uncertainty.
6. Resume repair or stop based on remaining budget; verify the final production
   patch independently of diagnostic instrumentation and controls.

The checks in step 4 are calibration interventions, not reference repairs and not
evidence that the injected fault caused the original failure. A passing control
only supports sensitivity to that intervention in that context. A failed control
can also reflect a bad control design. Arbitrary crashing mutants are inadequate:
they can make any exit-code observer appear sensitive. Instrumentation may change
timing or state; test and report such effects rather than silently trusting it.

For the first implementation, use replay, cheap trace checks, and a small reviewed
control library. The generator must infer applicability from task evidence;
evaluation labels and human-supplied missing-control tags are unavailable to it.
Keep full probabilistic planning as a later option, conditional on useful data.

## Why this might add value, and why it might fail

Our inference is that expansion sometimes wastes budget because the problem is
how an experiment is executed or observed. A controller that repairs that problem
could make ordinary probes useful without generating many new hypotheses.
Its research contribution would be demonstrated action selection and downstream
benefit, not the invention of controls, instrumentation, or mutation analysis.

This can fail for several concrete reasons: ordinary agents already repair these
mistakes; simple reminders suffice; calibration costs exceed the saved work;
controls are as hard to generate as the original experiment; inferred contracts
encode the same misconception as the probe; or observed distinctions do not help
produce a correct patch. The study must retain those negative outcomes.

## Next falsification experiment

First inspect naturally occurring diagnostic probes from development trajectories
and label failures with independent review. Do not infer prevalence from our
hand-authored probes. If experiment inadequacy is rare or inexpensive to recover
from, narrow or abandon the controller proposal before building much machinery.

For mechanism development, build the four planned controlled fault families:
omitted option, retained state, execution order, and configuration/import origin.
Cross two factors: adequate/inadequate probe and present/absent causal explanation
in the initial hypothesis set. Include adequate probes with legitimate negative
results, easy direct fixes, and controls whose sensitivity checks cannot be made.
Labels remain evaluator-only. Code, issue, and submitted probe remain visible to
all arms. These deliberately constructed cases cannot establish natural frequency.

Use staged comparisons to avoid paying for a large experiment prematurely:

- Mechanism stage: same generator and repair budget, comparing a generic probe
  review reminder, blind regeneration, coverage-guided repair, mutation-guided
  repair, and the proposed choice among setup/intervention/observer repairs.
  Compare always-running controls with conditionally requested controls to test
  whether routing itself earns its overhead. All arms get equivalent tools.
- End-to-end stage, only if the mechanism helps: native agent, strongest cheap
  baseline, and full Skylla under matched model/harness and total time/money.
  Measure independently verified target and regression success on a new split,
  plus incorrect rejection of hypotheses, unnecessary expansion, false adequacy
  declarations, setup failures, and complete generation/execution overhead.

A positive diagnostic score alone cannot establish a repair claim. Report
per-family behavior and repository-clustered uncertainty. Choose the minimum
useful effect and confirmation sample size using pilot costs/variance before
inspecting confirmation outcomes; do not select an arbitrary success threshold
after results arrive. Match message formatting and attention across feedback arms.

Stop conditions: if a reminder matches the proposed method, ship the simpler
workflow; if coverage or mutation guidance explains the gain, reuse it and revise
the contribution; if only constructed tasks improve, restrict the claim to them;
if no repair benefit survives full costs, retire the efficiency claim.

## Prior-art check from this round

Reading depth is explicit below. These sources were inspected, not reproduced.

- [ConcoLixir](https://arxiv.org/html/2606.26545v1), abstract and design excerpts:
  proposes inputs at solver failures and coverage plateaus, then validates by
  execution. Conditional generation after stalled exploration is prior art.
- [ConcoLLMic](https://abhikrc.com/pdf/SP26.pdf), introduction/method overview and
  [author repository](https://github.com/ConcoLLMic/ConcoLLMic): source
  instrumentation, path summarization, and solving support alternative-path
  generation. Trace-guided missing-branch exploration is a strong comparator.
- [Agolic](https://arxiv.org/html/2608.06397v1), introduction and planning excerpts:
  configures later bounded symbolic runs using earlier evidence, including
  different input surfaces and execution modes. Reconfiguring experiments from
  feedback is not new in itself.
- [EvoOtter](https://arxiv.org/html/2607.02854v1), sections I and III overview:
  uses rule-based mutants to select/evolve reproduction tests with successive
  halving and batched generation. It explicitly operates without the future fix.
  Mutation-based probe feedback must be compared against this family of methods.
- [BSG-VA](https://arxiv.org/html/2607.28871v1), method and discussion:
  replays agent tests on buggy, candidate, and gold states; its live feedback uses
  buggy-state replay. It reports evidence-quality gains with no detectable repair
  success change. Measurement starts after the first production edit, so earlier
  diagnostic probes are outside that measured population. That boundary suggests
  a study scope, not proof of an untouched research area. Code is available on
  request according to the paper, rather than a verified public implementation.
- [DDMT](https://arxiv.org/html/2607.00929v1), abstract/method description, and
  [AI4MT](https://doi.org/10.1016/j.infsof.2026.108150), abstract: metamorphic
  testing supports oracle-limited debugging and generated follow-up tests.
  Generated relations still require justification; a changed output is not
  automatically incorrect.
- [Formal RIP analysis](https://arxiv.org/abs/2410.21904), abstract, and
  [ripr](https://github.com/EffortlessMetrics/ripr), README: reach, infection,
  propagation, and observation have extensive testing precedent. The latter
  offers static advisory oracle-gap analysis and focused repair guidance for
  developers/agents. Its documented runtime limits do not establish Skylla's
  superiority.
- [Efficient Test Selection in Active Diagnosis](https://arxiv.org/abs/1207.1418),
  abstract: test choice using approximate information gain predates coding
  agents. Budgeted information gathering needs a defensible observation model.

## Decision

Pursue experiment repair as the next falsifiable research candidate. Retain
missing-cause discovery as one possible action after checking the experiment.
Do not label the current idea a breakthrough. The next evidence must show that
the proposed distinction can be automated and improves real debugging beyond
the closest simpler alternatives.
