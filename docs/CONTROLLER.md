# Local controller contract

The v0.0.1 CLI accepts JSON and returns one inspectable decision. It runs without
a model, provider credentials, or a particular agent harness. It does not yet
generate experiments, execute commands, or repair repositories.

```sh
python -m pip install .
skylla experiments/expansion/examples/missing-control.json --policy conditional
skylla experiments/expansion/examples/missing-control.json --policy fixed
skylla experiments/expansion/examples/missing-control.json --policy blind
python -m unittest discover -s tests -v
```

Use `skylla -` for stdin. Invalid input produces a JSON error on stderr and exit
code 2. Python callers can use `from skylla import decide`. The example is
synthetic contract input, not a benchmark task; its `probe.py` is illustrative.

## Input and responsibility

The [example request](../experiments/expansion/examples/missing-control.json)
shows the complete minimal shape. Supply schema version 1, current `state_id`,
hypothesis IDs, budget, and candidate contracts. A candidate includes argument
vector, estimated cost, outcome labels, hypothesis predictions, covered control
tags, and explicit state-bound precondition records. Missing predictions or
`null` mean unknown. Evidence has an ID, state identity, and optional `active` flag.

The caller must check the preconditions and construct state identities that bind
code, dependencies, interpreter, relevant configuration, and execution context.
The controller validates declarations and state equality; it cannot establish
that an asserted check really passed. Required control tags are supplied by the
caller, so an undeclared missing cause can still be missed. No shell string is
executed. Version 1 assumes a common execution environment; candidate `env` or
`cwd` overrides are rejected. Encode experimental input changes in `argv`.

Budgets contain remaining seconds, remaining expansion calls, and estimated
expansion cost. Costs are estimates. An integrating executor must measure actual
costs, enforce deadlines, debit the budget, and submit updated requests.

## Decisions

| Action | Meaning |
| --- | --- |
| `execute` | A verified, current-state candidate is selected |
| `expand` | Request at most one generator call, within the declared allowance |
| `verify_preconditions` | No ready candidate exists, but some need checks |
| `revalidate` | Active evidence belongs to another state |
| `return_to_solver` | The caller requested repair continuation |
| `unresolved` | Budget or declared menu cannot support the next action |

All three policies share validation, feasibility, duplicate handling, and stale
evidence checks. `fixed` never expands. `blind` requests expansion whenever its
allowance permits, after those checks. `conditional` expands for absent required
controls, no feasible verified candidate, or no predicted distinction. Unknown
preconditions take priority when there is no ready candidate. Expansion produces
a request, not a new candidate; the caller invokes its configured generator and
debits the allowance. A caller that repeatedly submits unchanged budgets can
repeatedly receive expansion requests.

For execution, the score counts hypothesis pairs assigned different known
outcome labels, divided by estimated seconds. It is a heuristic, not information
gain, calibrated causal confidence, or expected repair value. Exact duplicate
argument vectors count once. Conflicting predictions or control tags for the same
execution invalidate that group. Cost and an argument-vector hash break ties.
The score can change its selected execution when one explanation is duplicated
under another hypothesis ID. The current schema does not encode hypothesis
aliases; see the [reproduced counterexample](IDEATION.md). Candidate deduplication
does not solve this separate hypothesis-representation limitation.
Setup failures do not falsify hypotheses. Returning to the solver does not assert
repair success.

## Current evidence and missing integration

Sixteen unit tests check decision boundaries and historical test-output triage.
An installed CLI smoke check exercises file/stdin transport and invalid-input
handling. The [runtime development batch](../experiments/expansion/REPORT.md)
executes frozen probes independently of this controller. It does not evaluate
the three policies, a live expansion generator, or agent repair.

The next integration needs a budgeted executor, recorded generation requests,
typed extraction from probe observations, state identities covering environment,
and a common adapter used by every comparison arm. The first runtime batch uses
a source-file fingerprint and records dependencies separately; it is not yet the
complete code/environment binding required by this contract.
