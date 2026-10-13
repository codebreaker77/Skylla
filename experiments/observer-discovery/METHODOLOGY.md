# Source-proposed container observations: development protocol v1

October 13, 2026. Freeze proposals and implementations before paired execution.
This is an apparatus and observation contrast on exposed historical cases, not
the matched coding-agent repair study. No model, learned policy, candidate patch,
or repaired production code is evaluated here.

## Question and information boundary

Can a bounded AST scan of source supply an observation that distinguishes the
Tornado development versions when the native closed-loop indicator does not?
Does the existing normalized Luigi operation already distinguish its versions?

The author knows the registry observation from earlier work. This is not blind
discovery. The generator itself receives only the two selected buggy source files,
`tornado/ioloop.py` and `tornado/platform/asyncio.py`: never the reference patch,
test fixture, useful field name, or reference outcome. File selection and the
close operation are manually supplied; localization is not evaluated. All
generated candidates, including irrelevant and unavailable fields, are retained.

Parse class container declarations and direct-method `self` assignments whose
initializers are dict/list/set literals or named container constructors, including
weak dictionaries and deques. Propose length observations, deduplicate identical
runtime access paths, and skip dunder attributes. This is a simple syntactic
heuristic, not data-flow/alias analysis, mutation testing, causal inference or a
novel algorithm. Constructors with matching names can be unrelated containers;
runtime failures remain unavailable, never negative bug evidence.

The scenario reads container lengths without retaining entries. Candidate
availability is not the same as useful candidate selection. Every candidate is
observed; there is no learned/adaptive ranking. Do not attribute any result to
Laya or claim that a native agent cannot inspect these same fields.

## Cases and modes

Use previously screened BugsInPy `tornado-6` and `luigi-7`, with original revision
pins from [the screening manifest](../expansion/screening/cases.json). Both are
excluded from confirmation. Earlier buggy/fixed observations and benchmark test
fixtures were already exposed. These are two convenience development bugs.

- Tornado normalization: create and close one or ten independent AsyncIOLoops;
  inspect only the native `is_closed()` result. This deliberately narrow
  baseline is not a native coding-agent baseline.
- Tornado source containers: same inputs, with all generated class/instance
  container lengths before creation, while active, after close, and at the end.
- Luigi adequate-probe control: claim task A with worker X, report UNKNOWN for A
  from worker Y, and observe running tasks before/after. No additional observer
  generator is evaluated on Luigi; this control cannot measure avoided expansion.

Run three repetitions in fixed case/variant/arm/input order, a fresh snapshot and
subprocess for every invocation. Repetitions measure stability, not independent
bugs. If all variants are ready: thirty probe processes (24 Tornado, six Luigi).
Four separate readiness processes precede probes; any failed readiness blocks
that variant and preserves a disposition. Readiness imports the actual project
and exercises constructor/close for Tornado; Luigi readiness only imports relevant
classes. It does not validate every future probe or dependency.

## Reference evaluation

After each ready variant's probes, run evaluator-only benchmark target fixtures
and one neighbor check on buggy and fixed source. Ten evaluator processes total
when all variants are ready. Fixture files are copied from the fixed snapshot
into fresh evaluator workspaces; they never reach proposal generation. The
Tornado neighbor is its asyncio callback check; Luigi's is `test_dep`. These
checks validate this development contrast, not a generated repair or broad
regression freedom. Never interpret every nonzero exit as a target bug: preserve
stdout/stderr and inspect failures against the reported requirement.

## Recording, environment and interpretation

Use the existing study environment (Windows, Python 3.9), with package inventory,
UTF-8 output, disabled pytest plugin autoload, pinned source metadata and content
fingerprints. Record command, working directory, output, status, launch failures,
timeouts and parsing failures. A zero exit or valid JSON alone cannot pass the
readiness gate: matching case, readiness flag and actual source origin are needed.
Timeout/invalid-payload paths retain stdout/stderr. Fresh source copies preserve
the earlier explicit omission of legacy AppEngine symlinks.

Hashes bind method, generator, probe, runner, preparation/fingerprint utilities,
proposals and observations. Source identity checks bind runtime snapshots to
proposal generation. Preserve previous frozen experiments unchanged. No paid
inference is invoked. Source downloads and third-party fixtures stay ignored.

Report generation/source-check time, process time, complete runner time and
evaluator time separately. These are local apparatus costs, not full agent cost.
Fixed run order and startup/cache effects prevent latency superiority claims.

If an additional observation distinguishes versions, report a candidate surface,
not proof of the cause, discovery advantage, or increased repair success. If the
normalized control suffices, retain it. The actual next gate still requires native
agents, equal tools/budgets, generated patches and independently verified repairs:
[matched agent protocol](../trajectory-audit/NEXT_COMPARISON.md).

## Reproduction (PowerShell)

```powershell
python tools/study/observer_study.py freeze
artifacts/venvs/study/Scripts/python.exe tools/study/observer_study.py run --name run-002
python tools/study/observer_study.py verify --name run-001
```

Freeze only in a fresh checkout without existing proposals/protocol. Existing
frozen files must not be replaced. Prepare the study environment using the
[expansion dependencies](../expansion/requirements.txt); generating proposals
uses only standard-library Python. Use a new run name. Verification checks
integrity, not independent interpretation or hidden-test repair success.
