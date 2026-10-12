# Product direction

October 13, 2026. Proposed design, subject to the pilot. Confirmed requirements:
Skylla is open source, serves developers and AI agents, remains model and harness
agnostic, and supports a research publication grounded in our findings.

## The useful moment

A test fails and several mechanisms could explain it. Repeating the test gives
the same symptom; editing immediately risks treating that symptom. Skylla helps
turn the uncertainty into a small executable check, then preserves what happened.

For example, an integration test fails only in a suite. Plausible causes include
a leaked environment variable, shared cache contents, or order-dependent fixtures.
A fresh-process run, a cache reset with verified preconditions, and a controlled
test-order change distinguish different possibilities. A result is evidence under
those controls, not automatic proof of a root cause.

## Alternatives considered

| Direction | Practical value | Main weakness | Decision |
| --- | --- | --- | --- |
| Conversational debugger | Easy questions about runtime state | Strong existing systems; tool access alone is insufficient differentiation | Reuse debugger capabilities |
| Evidence notebook | Reproducible handoffs and fewer lost observations | Can become documentation overhead; weak standalone research contribution | Build only enough to support experiments |
| Experiment selector | Potentially saves expensive or redundant investigations | Benefit may depend on candidates, solver, and failure family | Primary research hypothesis |
| Maintained probe packs | Concrete reusable checks for common mechanisms | Maintenance and applicability verification are substantial | Start with a few tested packs |
| Autonomous repair agent | Complete workflow ownership | Large scope and competes with existing harnesses | Keep repair in the user's existing workflow |

The initial product combines a small evidence record, executable probe contracts,
and interchangeable selection policies. A trained selector is optional and must
outperform cheap alternatives before becoming a product dependency.

## First workflow

1. Start from an existing failing command; capture state and reproduce the failure.
2. Obtain a few candidate probes from reviewed templates, the developer, or an agent.
3. Show the command, its controls, what outcomes distinguish, and expected duration.
4. Let the developer choose or let a configured policy select; allow abstention.
5. Execute from a resettable state and preserve raw output and parsed observations.
6. Update evidence relations and export an investigation for the existing repair flow.

A developer should not need to write a probability table or name every possible
cause. Richer hypothesis records are available to agents and research workflows.
The first-use screen must be useful before asking for extensive annotation.

The example workflow is a design target; none of these commands exists yet:

```text
skylla start -- pytest tests/test_example.py
skylla next <session>
skylla run <session> <probe>
skylla export <session>
```

## Architecture boundary

The proposed core is a versioned data contract plus state tracking, probe
validation, execution coordination, and evidence export. It does not own the
agent's planner or repair loop.

Separate interfaces:

- Generator: supplies hypotheses and candidates; may be templates, human, or model.
- Selector: ranks feasible candidates and may abstain; accepts a frozen snapshot.
- Executor: runs a contract and returns observations with an environment fingerprint.
- Evaluator: verifies research/repair outcomes independently; hidden checks are
  outside the selector's and solver's accessible workspace.
- Adapter: maps the shared operations to CLI, library, or structured tool calls.

A selector request contains serialized evidence and candidates, not a
provider-specific conversation object. Provider authentication and model-specific
formats belong in adapters. Model/version and usage belong in provenance.

No model is required to record or execute a user-supplied probe. The initial
deterministic policy is useful without API keys. Model-assisted generation and
selection are explicit choices. Supporting several providers is not enough:
verify swapping them without changing the core or session format.

Expose the same operations through a developer CLI and a structured interface.
An MCP adapter is one possible transport, not the core protocol. Start with one
minimal adapter and later demonstrate the same core in a second harness; avoid
building several integrations before the workflow earns value.

## Minimum records

| Record | Required content |
| --- | --- |
| State | Code snapshot, dirty-file hashes, environment/dependency identity, fixture hashes, failing command and reproduction output |
| Hypothesis | Mechanism, linked evidence, falsifiable predictions, unresolved alternatives; multiple causes allowed |
| Probe | Preconditions, exact command/script, controls/interventions, predictions, extractor, timeout, estimated cost, reset method |
| Observation | Probe/state IDs, raw output references, exit status, timing, extracted facts, result category |
| Interpretation | Author/model, source observations, supported/contradicted/unresolved relations; versioned separately |
| Outcome | Independent acceptance/regression result, repair provenance, total cost, termination reason |

Freeze predictions before running a probe. Later edits create new versions.
Timeout, setup failure, inconclusive, and unexpected output are explicit categories.
Do not force one of the original hypotheses to win. Duplicate observations are
not independent confirmation. Evidence from a changed state must be revalidated.

## First implementation scope

Use deterministic local Python test failures as an execution feasibility wedge,
not a restriction on the long-term protocol. Candidate probe families are fresh
process/state reset, configuration/import inspection, and controlled input checks.
Add another language only after the core records and execution assumptions survive
real use. Defer nondeterministic distributed execution, trained sequential policies,
hosted dashboards, and automatic patching.

For reversible local probes, use isolated copies and explicit restoration. A Git
worktree does not reset caches, databases, environment variables, or dependencies;
the reset contract must cover those resources too. Record instrumentation so a
probe that changes behavior is interpretable.

## Adoption and research can diverge

Developers may value reproducible handoffs even if a learned selector fails.
That can justify a narrower tool but cannot support a paper claiming improved
selection. Conversely, benchmark gains do not establish that developers will
repeatedly use the workflow. Run a separate usability study later.

There is no demonstrated moat. Tested probe packs, quality execution artifacts,
and trustworthy evaluation can build useful project assets. An open dataset and
API are copyable; a model choice alone does not create defensible differentiation.
