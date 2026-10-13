# Focused prior-art audit

October 13, 2026. Method-level reading supplements [LITERATURE.md](LITERATURE.md).
Published findings are the authors' results, not Skylla replications.

New product overlap: [DeepEval/Jev](DEEPEVAL_JEV_AUDIT.md) already supplies
custom System-1 evaluation/classification and a coding-agent evaluation workflow.
The audit records inspected scope, untested capabilities and comparison changes.

## AutoSD

[Published article](https://link.springer.com/article/10.1007/s10664-024-10594-x),
sections 3 and 4 inspected. Prompts produce hypotheses, predictions, and
executable debugger/edit-and-run commands. Observations enter the next prompt;
the model continues or emits a completion signal before patch generation.
Evaluation generates multiple patch candidates and distinguishes test-plausible
from correct repairs using additional assessment.

Overlap: scientific debugging, predictions before execution, model-interpreted
observations, and explanations. Avoid claiming those as new. The inspected
method does not establish a frozen competing-probe dataset with matched
continuations; its artifacts still need an implementation audit before a strong
novelty statement.

Baseline implication: adapt an AutoSD-style prompt and notebook to the same
runtime tools and budgets; do not present that adaptation as an exact reproduction.

## Debug2Fix

[Full-text v1](https://arxiv.org/html/2602.18571v1), setup, ablations, results,
failure analysis, and limitations inspected. Evaluates 186 Java cases and 400
Python cases. Baselines separate direct debugger tools, a debugger subagent,
and an edit restriction that encourages debugging. Python GPT-5 pass rate goes
from 31.2% to 36.2%, while Sonnet moves from 39.6% to 40.4%. Usage and inference
overhead matter. Build/debug-session failures and wrong repair despite useful
diagnosis appear in its analysis; rigid gating can overcomplicate easy tasks.

Overlap: runtime debugging integrated into agents and packaging that changes
adoption. Selection must be tested with equivalent capabilities and full costs.
Adaptive investigation/abstention is worth testing, but is not established novelty.
An exact reproduction requires released implementation/configuration verification.

## ReplayLens

[PDF v2, October 3, 2026](https://arxiv.org/pdf/2609.34177), section 4.7 and appendix S
inspected after HTML retrieval failed. Uses 24 deterministic tasks from eight
function families, twelve candidate implementations, four recorded patch outcomes,
three fresh public-test calls, and a sealed final submission. The study intervenes
on the initial ledger while holding candidate menu and tool budget fixed. It
explicitly does not establish open-ended repository repair or unrestricted code
generation. Artifact/code availability has not been verified.

Overlap: controlled action menus, altered evidence, sequential test feedback, and
independent hidden outcomes. Skylla's proposed repository-level experiment-value
study differs in task/action scope; fixed menus and hidden tests alone are not novel.

Baseline implication: distinguish harmless renaming/reordering from corrupted
action/outcome attachment. Verify evidence use, not just endpoint scores.

## Product overlap that changes the thesis

[Cursor's official Debug Mode documentation](https://cursor.com/docs/agent/debug-mode)
already describes hypothesis generation, code instrumentation, runtime logs,
targeted fixes, and verification. Skylla's hypothesis loop alone is insufficient
product differentiation.

The working contribution is reproducible comparison of alternative probes,
validated preconditions, state-bound evidence, and measured cost-aware selection
that helps an existing workflow. Each component has precedents. The combined
evaluation question needs a fuller active-diagnosis/test-selection literature
audit and experiments before any novelty or performance claim.

## Claim boundary

### Additional citation leads checked

[Causal Agent Replay](https://arxiv.org/abs/2606.08275), Jaineet Shah, June 6, 2026:
abstract read. Intervenes on an agent step and re-executes continuations to estimate
outcome effects, including interaction attribution. Executed counterfactual
continuations are already a general agent-evaluation technique.

[Credit Without Ground Truth](https://arxiv.org/abs/2608.19760), Haiyue Zhang,
August 2026 (v2 August 25): abstract read. Audits step contribution using executed
replay in ALFWorld, with policy-dependent counterfactual support and unreliable
credit signals. Our continuation labels must retain policy dependence and sampling
uncertainty; they cannot be called a universal oracle.

[REFLECT](https://arxiv.org/abs/2606.09071), Xiaofeng Lin et al., June 8, 2026:
abstract read. Uses diagnosis-specific replay interventions and verified outcome
changes to refine error attribution. Intervention-supported diagnosis is prior art.

These are leads from ReplayLens's references, not independently replicated methods.
Full-method and artifact audits remain necessary. They further narrow Skylla's
possible contribution to a useful software-debugging task/protocol and measured
selection benefit, rather than counterfactual execution in general.

## Current evidence boundary

- Established: runtime evidence and scientific debugging have substantial prior art.
- Proposed: a controlled corpus can expose useful selection failures and tradeoffs.
- Measured here: only the local execution rehearsal, reported separately.
- Unresolved: full overlap audit, reliable continuation labels, generalization,
  and whether a selector beats a well-configured incumbent.
