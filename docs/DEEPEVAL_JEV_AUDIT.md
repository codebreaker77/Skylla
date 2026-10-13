# DeepEval / Jev competitive audit

October 13, 2026. User-supplied lead. Official product documentation and the
JevEval implementation were inspected; no SDK, hosted inference, end-to-end
workflow or performance benchmark was executed. This narrows the research thesis.

## Verified scope and overlap

[The JevEval announcement](https://deepeval.com/blog/introducing-jev-as-a-judge)
describes user-authored bounded questions, typed probabilistic answers, fixed
score aggregation, per-question breakdowns and constructed explanations. These
features overlap directly with any proposal to package a System-1 judge with
inspectable questions and deterministic evaluation arithmetic. They are already
product capabilities, not a new Skylla contribution.

[JevEval documentation](https://deepeval.com/docs/metrics-jev-eval) additionally
supports trajectory judgments over span trees and custom System-1 model objects.
Its trajectory representation omits prompts, costs and token counts. This is a
representation choice, not evidence that the platform cannot account for costs
elsewhere. Backend flexibility and trace evaluation cannot distinguish Skylla by
themselves. A score derived from model probabilities still needs task-specific
accuracy/calibration evaluation; fixed arithmetic cannot prove its semantic input
judgments are correct. The implementation inspected was the unpinned current
[JevEval module](https://github.com/confident-ai/deepeval/blob/main/deepeval/metrics/jev_eval/jev_eval.py),
not a reproducible pinned artifact audit.

[Custom classifier documentation](https://deepeval.com/docs/classifiers-custom)
supports application-defined labels/descriptions, System-1 inference, optional
no-label behavior, and a standalone classification API. Merely asking a model
to choose setup repair, deeper investigation or deferral is therefore an adapter
design, not a moat or novel decision primitive.

[DeepEval 4.0](https://deepeval.com/blog/introducing-deepeval-4) describes codebase-
informed dataset generation, CLI tests, locally accessible traces/results,
coding-agent skills and agent-framework integrations. It can participate in an
iterative improvement workflow. Do not characterize DeepEval as an offline-only
scorer or claim open-source/local/harness integration is unique to Skylla.

## Consequence for our direction

The competitive risk is high for a generic fast-judge wrapper, trace dashboard,
custom metric package, or thin System-1 routing layer. Laya versus Jev is a backend
choice and can be evaluated independently of Skylla's research question. Published
speed/pricing claims from these announcements are not our deployment measurements.

The candidate research distinction remains executable experiment improvement:
generate an input or observation, validate its execution conditions, run it, and
measure whether the new evidence improves independently verified repository
repairs under an equal total budget. The inspected JevEval metric/classifier
documents decision making over supplied state; these pages do not demonstrate
that complete experiment-discovery/repair method. This is a limited scope finding,
not proof of absence across DeepEval or of novelty versus other work. Dataset
generation and the coding-agent workflow are adjacent capabilities requiring
closer comparison. Existing scientific debugging, active diagnosis, mutation-
guided generation and LAVOIR remain relevant prior art too.

Current evidence is limited: our AST heuristic proposes a previously known
Tornado registry among eight fields, and a Luigi normalized probe already
suffices. Neither measures generated repairs, learned selection, blind discovery,
cross-harness gains or superiority over JevEval. A successful semantic judgment
of a trace cannot by itself establish unobserved program behavior; equally, a
Skylla trace with extra fields is not automatically a better experiment.

## Required comparison amendment before future agent runs

Keep the existing frozen development protocols and historical observations intact.
Before a new matched-agent run, freeze an explicit DeepEval/Jev-assisted baseline
configuration in its run manifest. This is a proposed additional baseline, not
an amendment to already executed experiments or a completed integration.

Compare the same coding model, starting state, native tools and total budget:

1. Native agent.
2. Native agent with cheap normalization.
3. Native agent with DeepEval/Jev evidence judgments and the same native ability
   to inspect source and create probes. Specify the questions and how results
   enter the loop; this adaptation is not an exact reproduction of a published
   repair system.
4. Native agent with bounded Skylla experiment proposals/execution.

Retain the existing attention and blind-generation controls before attributing a
mechanism. Give every arm equivalent source/trace access and observation rendering;
do not remove a native capability to manufacture a gain. Where classifier choices
are compared, keep candidate/state inputs identical and separate backend quality
from the benefit of obtaining new evidence. Count generation, all judge inference,
execution, invalid proposals, retries, resets and final verification.

Primary outcome remains independently verified production repair and regression
checks with diagnostic instrumentation removed. A judge score, confidence gain,
trace correctness label, or discovered field is a secondary measurement. Jev's
hosted calls need configured access/budget before execution. If the cheaper or
DeepEval-assisted baseline matches Skylla, narrow or drop the improvement claim;
do not infer equivalence from an underpowered pilot.

## Product and paper decision

Build reusable runtime evidence tooling that can integrate with existing evaluation
frameworks; do not spend this iteration recreating their generic metric/classifier
features. Retain replaceable backends, including no-model operation. The possible
paper must explain a precise experiment-improvement mechanism or release a useful
evaluation contribution, then establish its effect on held-out repairs. No
defensible moat or breakthrough has been established by the current experiments.
