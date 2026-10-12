# Three-case development rehearsal

This directory contains original probe contracts, pinned historical source
manifests, and measured observations. It is development data, not a held-out
evaluation or evidence that Skylla improves agent repair.

The initial source is [BugsInPy](https://github.com/soarsmu/BugsInPy/tree/11c5f1eea954a42132cfd06bf257766a7963e0fd).
Use [cases.json](cases.json) for exact commits and screening exclusions,
[probes.json](probes.json) for frozen development predictions, and
[the execution report](REPORT.md) for findings and limitations.

## Reproduce locally

Use Python 3.9 for the recorded environment. Commands from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r experiments/rehearsal/requirements.txt
python tools/pilot/prepare.py --variant buggy
python tools/pilot/prepare.py --variant fixed
.venv\Scripts\python.exe tools/pilot/run.py --output experiments/rehearsal/results/local-rerun
.venv\Scripts\python.exe tools/pilot/run.py --regressions-only --output experiments/rehearsal/results/local-regressions
python tools/pilot/verify.py
```

Output directories must be new. Source archives, workspaces, and raw logs are
ignored by Git; manifests, hashes, extracted observations, and summaries are
tracked. Raw logs can be regenerated with these commands. Different platforms
may expose additional failures; do not silently substitute their results for
the recorded Windows run.

Each run uses a new source copy and process, no solution-bearing Git history,
an explicit environment, disabled unrelated pytest plugins, and a 30-second cap.
The upstream fixed regression-test file is installed on both code variants to
validate the historical failure. This file is an evaluator fixture and must not
be exposed as a hidden acceptance oracle to future solver arms.

Cached sources are development coordination artifacts. They are not a secure
sandbox. Full model comparisons need evaluator separation and OS/container-level
access boundaries; separate folders on this unrestricted machine are insufficient.

## Licenses and scope

Original Skylla scripts, contracts, and reports use the root MIT license.
Fetched snapshots retain their own licenses: PySnooper's MIT license,
youtube-dl's public-domain dedication, and tqdm's file-specific MIT/MPL notices.
Read the upstream license files before redistributing snapshots. No third-party
source or test fixture is vendored here. BugsInPy metadata provenance is recorded;
do not infer a blanket license for its entire database from downstream projects.

The runner invokes no model, accesses no harness account, and produces no agent
repair-success label. Three-case setup/probe results are not the 12-bug pilot's
continuation experiment.
