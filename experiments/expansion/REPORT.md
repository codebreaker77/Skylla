# Expansion study: development milestone

October 13, 2026. This is a local implementation and feasibility report. There
are no model runs, comparative repair results, or new-algorithm claims here.

## What is implemented

Skylla 0.0.1 provides a dependency-free Python decision function and JSON CLI.
It separates a fixed menu, blind expansion, and conditional expansion, with
shared feasibility and coarse state checks. Sixteen tests pass. See the
[contract](../../docs/CONTROLLER.md) and [claim matrix](../../docs/CLAIM_MATRIX.md).

## Historical-case screen

The [12-case manifest](screening/cases.json) pins BugsInPy metadata revision
`11c5f1eea954a42132cfd06bf257766a7963e0fd` and buggy/fixed source commits.
Candidates were selected from test names before source inspection, without
reading reference patches. This is a convenience development pool, not a
prevalence estimate or an unseen evaluation split. Reference regression fixtures
were copied to buggy snapshots as required for the benchmark target checks.

The frozen manifest's CRLF bytes were normalized to LF for portable Git hash
verification; JSON field values stayed identical. Its pre-normalization SHA256
was `87053546ca8b35b57d210ec7cd6838246a5d78d00b2b1434a44b73ccae0dde7c`.
The aggregate records the current LF manifest hash.

The [screening record](screening/results.json) preserves 22 case-level attempts
and 96 actual test subprocesses. Each mechanically admitted case has three
buggy failures and three fixed passes in its latest attempt.

| Latest disposition | Cases |
| --- | --- |
| Target difference reproduced (10) | cookiecutter-1, -2, -3, -4; luigi-5, -7, -9; tornado-5, -6, -7 |
| No target discrimination | tornado-3: both variants pass locally |
| Compatibility/setup obstacle | tqdm-6: obsolete `sys.setcheckinterval` in test setup on Python 3.9 |

Admission verifies a target-test difference only. It does not establish mechanism
ambiguity or regression completeness. In particular, cookiecutter-4 fails early
on a missing exception attribute in the buggy API; retain it as a possible easy
control, rather than assume it is a difficult runtime diagnosis.

Setup attempts matter: missing `mock`, `python-slugify`, and the `mocker` pytest
plugin required explicit dependency installation; inherited `--cov` options
required clearing pytest addopts. Post-hoc triage corrects missing fixtures,
loader errors, and skipped tests. Original statuses and corrected statuses remain
side by side. This heuristic is not a universal setup-versus-code classifier.
Early attempts did not record complete dependency inventories or runner hashes;
later summaries do. The aggregate keeps missing metadata explicit.

The environment uses Windows/Python 3.9.5, rather than the original Python
3.6–3.8 environments. Direct pytest replaces tox where present. Archive exports
omit only explicitly allowed legacy documentation/App Engine symlinks under
`docs/` (cookiecutter) and `maint/test/appengine/` (Tornado); omitted links and
policy are recorded in source metadata. Package and target test code are not
edited for compatibility. These deviations limit benchmark comparability.

## Frozen runtime observations

The [probe contracts](runtime/probes.json) were frozen before this batch, after
screening symptoms, buggy source, and reference test fixtures were visible.
Authoring did not inspect full target fixes. This remains development data.

Each probe ran once per buggy/fixed variant, with a fresh snapshot and subprocess,
30-second timeout, and actual imported-source path verification. There are
24 observations across 12 probe pairs. All imported the pinned source and
completed successfully. [Results](runtime/results/run-001/observations.jsonl)
and [environment/hash summary](runtime/results/run-001/summary.json) are tracked;
local raw stdout/stderr logs remain under ignored `artifacts/`.

| Case | Experimental variation | Unequal buggy/fixed observation payloads |
| --- | --- | --- |
| luigi-7 | Worker ownership, task identity, status, update order | 4/4 |
| tornado-5 | Normal, backward, boundary, and overrun clock schedules | 2/4; backward and boundary differ |
| tornado-6 | Wrapper close, repeated close, garbage collection, native close | 4/4 |

Ten of 12 payload pairs differ. This is descriptive equality checking, not a
causal label, useful-probe rate, controller ranking result, or repair gain.
The batch used 7.649276 seconds of subprocess time, excluding preparation and
dependency installation. No performance claim rests on this small timing sample.
State IDs fingerprint source files; dependency/interpreter records are separate,
so complete environment-aware invalidation is still pending.

## Reproduce and verify

Historical dependencies should be installed in a separate disposable environment,
not in the dependency-free controller environment. The exact latest screening
environment is [requirements.txt](requirements.txt); the runtime summary retains
its earlier inventory, before the final Cookiecutter dependency retry.

```sh
python -m venv artifacts/venvs/study
artifacts/venvs/study/Scripts/python.exe -m pip install -r experiments/expansion/requirements.txt
artifacts/venvs/study/Scripts/python.exe tools/study/screen.py --output artifacts/screening/reproduction --workers 3 --repeats 3
artifacts/venvs/study/Scripts/python.exe tools/study/summarize_screening.py
artifacts/venvs/study/Scripts/python.exe tools/study/run_runtime_probes.py --output experiments/expansion/runtime/results/reproduction
python tools/study/verify.py
python tools/pilot/verify.py
```

The screening manifest is already committed; regenerating it requires the pinned
BugsInPy checkout under `artifacts/sources/BugsInPy`. Export downloads require
network access. Original raw logs are local and not shipped; verification reports
how many are available and checks every available hash. The scripts' subprocess
isolation is for reproducibility, not a security sandbox for untrusted code.

## Next evidence gate

The four controlled fault tasks proposed in the study plan have not been built.
Nor has this batch run adaptive expansion or integrated an agent. Next: create
and freeze a separate controlled fault set, complete the shared budgeted adapter,
then compare native harness, notebook, fixed-menu, blind-expansion, and conditional
expansion arms at matched model/access/budgets. Development cases must stay out
of confirmation data. External model evaluation still needs configured access
and a run budget. A publishable claim depends on those results, including costs,
false expansion, missed expansion, and independent repair verification.

The [original 48-record rehearsal](../rehearsal/README.md) is preserved separately;
these 96 screening and 24 runtime processes do not revise its findings.
