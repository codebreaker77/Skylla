# Next research iteration: evidence quality before learned routing

October 13, 2026. Active development plan; no breakthrough or repair advantage
has been demonstrated. The frozen [agent comparison](../experiments/trajectory-audit/NEXT_COMPARISON.md)
remains the governing evaluation design. This memo adds development tasks and
classifier-specific checks, without changing its confirmation exclusions.

## Hypothesis

Within a matched total budget, improving an uninformative debugging experiment
can yield more independently verified production repairs than native debugging
or cheap normalization. Learned routing is a separate hypothesis: it must improve
that trade-off beyond rules, after counting inference and mistaken decisions.

Neither declining uncertainty nor a confident classifier response measures repair
utility. A useful probe can also return no discrepancy. Labels must distinguish
execution/setup validity, reported symptom, relation to the requirement, and
remaining uncertainty rather than flattening those into pass/fail.

## Prior work checked and consequences

[LAVOIR v1, sections 3-5](https://arxiv.org/html/2609.30706v1) uses predefined
information slots, schema-defined decisions, simulated answers and a learned
value head. It chooses whether to ask, choose or defer. Its training target uses
known correct decisions rather than confidence increases alone. Asking for
missing evidence and amortized value-of-information selection are already prior
art. Our candidate distinction is executable input/observation discovery and
downstream repository repair, rather than slot-based conversational clarification.
That is a scope distinction, not proof of novelty. Its code has not been reproduced.

[Fast Models, Slow Evidence v1, sections 8-9](https://arxiv.org/html/2610.02267v1)
reports sensitivity to option order and warns that gate accuracy and excluded
pre-screening costs can distort deployment conclusions. Its model-routing labels
also have single-run noise, and domain fine-tuning was not evaluated. We will
measure ordering/wording robustness, include every inference cost, and avoid
treating one chosen continuation as a universal correct action. We have inspected
the relevant methods/discussion, not reproduced its artifact suite.

The [existing prior-art audit](PRIOR_ART_AUDIT.md) covers neighboring repair and
test-generation work. Reviewing these two System-1 papers does not complete the
novelty search. In particular, investigate strong source/coverage/mutation-guided
diagnostic generation before attributing benefit to our proposed mechanism.

## Development case queue

These are deliberately selected, previously exposed cases. They cannot become
confirmation data or be used to estimate prevalence.

| Case | Development role | Current evidence | Next gate |
| --- | --- | --- | --- |
| Xarray 3677 | Evidence-handling/normalization control | [Replay completed](../experiments/evidence-pilot/REPORT.md): nine valid processes; caught method failure exits zero | Retain as control; improve failure-path logging before broader screening |
| Tornado 6 (BugsInPy) | Candidate observation-surface case | Prior runtime probes distinguish registry behavior while a native closure field does not | Provide issue/source to generator without useful observer; determine whether native tools already resolve it |
| Luigi 7 (BugsInPy) | Adequate-probe control | Earlier identity/status/order probes all distinguish versions | Ensure proposed method avoids unnecessary expansion |

Every queued case and attempted setup gets a disposition. Do not quietly replace
cases after seeing policy outcomes. BugsInPy cases retain the revisions and
environment qualifications in the [expansion study](../experiments/expansion/REPORT.md).
All historical study cases, constructed fixtures, audited tasks and newly used
development tasks are excluded from later confirmation, not just the fifteen
audit IDs. Build a confirmation inventory before examining its outcomes.

## Work packages and acceptance gates

1. **Executable evidence apparatus.** Reproduce the reported symptom from pinned
   actual source, preserve raw status and typed observations, verify import origin,
   and log failed setup. First implementation:
   [evidence pilot methodology](../experiments/evidence-pilot/METHODOLOGY.md).
   This does not evaluate an agent or classifier.
2. **Candidate discovery.** Generate input/observation proposals from the issue,
   current source and trace. Save proposals before executing them. Do not include
   reference fixes, evaluator labels, or the known useful observer in generator
   inputs. Keep native source inspection, debugger and probe-writing available.
3. **Matched pilot.** Start with native, cheap normalization and discovery arms.
   Freeze model/harness versions, prompts, source states, equal budgets and
   independently checked target/regression evaluators first. Add reminder and
   blind-generation controls before claiming a routing/discovery mechanism.
4. **Classifier shadow evaluation.** Evaluate the optional backend below at actual
   decision points. Its predictions cannot execute tools or affect repairs in
   shadow mode. Measure errors and costs before enabling control.
5. **Confirmation and paper.** Freeze the method and primary contrast; size a study
   from pilot variance/cost with repository clustering. Report all unsolved cases
   and setup failures. Replicate with another configured model/harness before
   claiming broad performance independence.

The immediate gate is a useful development contrast beyond normalization. If
normalization matches discovery, retain normalization. If blind generation matches
adaptive choice, do not claim an advantage for routing. No successful pilot
guarantees novelty or a publishable superiority result.

## Optional System-1 backend contract (design, not implemented)

The core keeps deterministic source/state, budget and execution checks. A
replaceable backend receives only solver-visible state: issue, relevant source
references, raw output/status, checked preconditions and available actions. Return
an action ID, per-option scores/probabilities where supported, backend/checkpoint
identity, input hash and inference timing. Store the exact question/options and
input, not just a prediction. Model output is a recommendation, never a validity
certificate. Enforce preconditions and budgets after any recommendation.

Start with a small question: which evidence-handling action should be considered?
Options can include repair setup, inspect caught failure, improve the requirement
check, continue investigation, and defer. Descriptions must permit ambiguity;
exceptions alone do not reveal whether they represent setup or the reported bug.
These are experimental options, not a hand-labeled training set.

Compare rules-only, one explicit pretrained Laya checkpoint, and the configured
larger model on identical visible decision states. Laya remains an optional
Python 3.10+ worker/service; the dependency-free Python 3.9 controller remains
usable. Pin SDK and model revision before execution. Record hardware, load time,
warm inference, serialization, input preparation and memory. Avoid per-call model
loads. Do not assume documented GPU latency applies to this workstation.
[Official Laya card](https://huggingface.co/convaiinnovations/laya).

Test equivalent option permutations, neutral option IDs, instruction paraphrases,
long/noisy outputs and source-state changes. Preserve full evidence and measure
what any truncation omits. Evaluate abstention and held-out error rates; choose
thresholds on development data only. A supplied confidence score is not assumed
calibrated for debugging. Permutation voting has an inference cost too.

Replay comparative continuations where feasible to estimate action usefulness.
Review labels independently; until then treat them as exploratory. The existing
38-event single-review audit and 840 constructed episodes are not sufficient
ground truth for training a trustworthy repair selector. Fine-tuning follows
reliable data and evaluation; it is not a prerequisite for evaluating a pretrained
model and is not part of the immediate apparatus work.

## Current execution constraints

Python 3.10.11 is available alongside the controller's Python 3.9.5. Docker CLI
is installed, but its Linux engine was unavailable during this iteration. Local
compatible environments can support apparatus development; they do not reproduce
benchmark container results automatically. No inference backend or paid-run budget
is configured. These constraints do not block local replay, protocol writing or
artifact verification; they remain prerequisites for the matched agent comparison.
