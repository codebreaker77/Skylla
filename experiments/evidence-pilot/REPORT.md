# Real-bug evidence replay: Xarray 3677

October 13, 2026. Development apparatus result, not a repair/classifier benchmark.

## Result

On the original benchmark source, the issue-derived method call consistently
raises `AttributeError` for a named scalar DataArray. The top-level API works.
Catching the method exception produces a successful shell status while preserving
the failed requirement in the structured observation.

| Probe mode | Fresh processes | Exit status | Requirement evidence |
| --- | ---: | --- | --- |
| Top-level API only | 3 | 0 in all | Method not exercised; reported issue unresolved |
| Method with caught exception | 3 | 0 in all | `AttributeError`; method requirement unmet |
| Explicit issue-derived relation check | 3 | 1 in all | Same exception; requirement check fails |

The exception reports that the DataArray has no `items` attribute. Import origins
pointed to the pinned local checkout in all nine successful apparatus executions.
No production source was changed. Total subprocess time was **20.031 seconds**,
including startup/imports; the first call took 8.274 seconds. Preparation and
downloads are excluded. These timings compare no policies and show no speedup.

## All attempts and setup correction

Two runs are preserved: eighteen attempted processes in total, on one bug.

- [run-001 summary](results/run-001/summary.json): all nine invocations were
  infrastructure failures. The orchestrator started the study before the separate
  dependency installation completed. The package inventory was empty. No probe
  payload was produced; this runner recorded JSON decoding failures and did not
  retain the underlying stderr on that failure path. These attempts provide no
  bug evidence and are not counted as successful reproductions.
- [run-002 summary](results/run-002/summary.json): after installation completed,
  all nine invocations produced observations; zero infrastructure failures.
  [Detailed observations](results/run-002/observations.json) preserve statuses,
  payloads, import origins, stderr and elapsed time.

Runs were not overwritten or silently excluded. Before broader screening, improve
the runner's failure-path logging and readiness checks in a versioned iteration.

## Meaning for Skylla

Shell status alone is insufficient for this case. A successful call to a sibling
API also does not check the reported requirement. Explicit evidence handling
retains the distinction between unexercised behavior and an observed method
failure. This supports the cheap normalization/evidence baseline.

The native agent already read the caught exception in the public trace. We have
not established that it missed evidence, that new internal observations were
needed, or that Skylla improves its final repair. The three probes were manually
authored from an exposed issue, with one fixed input and no fault-absent/reference
comparison. There is no automatic observer discovery, Laya inference, learned
policy, repair generation or independent second review in this run.

## Method and next gate

[Methodology and reproduction](METHODOLOGY.md) specifies the original source
revision, environment, probes and interpretation limits before execution.
Python 3.10.11, NumPy 1.23.5 and pandas 1.5.3 reproduced the reported symptom in a
local Windows environment, not the original benchmark container. Script,
methodology and observation hashes are recorded in both summaries.

```powershell
python tools/study/evidence_pilot.py verify --name run-001
python tools/study/evidence_pilot.py verify --name run-002
```

The [active research plan](../../docs/RESEARCH_ITERATION.md) keeps this as an
evidence-handling control. The next substantive question is whether input or
observation discovery helps beyond this cheap baseline and native investigation.
The optional classifier starts in shadow mode only after reliable decision states
exist; these nine repetitions do not constitute training data or a breakthrough.
