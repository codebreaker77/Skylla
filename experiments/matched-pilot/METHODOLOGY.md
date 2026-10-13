# Matched repair pilot: preparation and readiness screening

October 13, 2026. The existing [comparison protocol](../trajectory-audit/NEXT_COMPARISON.md)
continues to govern information boundaries, repair verification and later controls.
This pilot is development work, not confirmatory evidence or a novelty claim.

## Selection before outcomes

Freeze a metadata-only inventory at the existing BugsInPy revision. Eligibility
is limited to cookiecutter, Luigi, Tornado, tqdm and PySnooper, based on prior
local apparatus experience with small Python libraries. This limits external
validity and does not imply all excluded projects require heavy resources.
Exclude all cases and screening exclusions in the historical rehearsal,
expansion screening and public trajectory audit. Sort IDs by SHA256(seed|id),
take six with at most two per repository. Keep setup failures; do not silently
replace cases after observing their outcomes.

The selected IDs have not been examined in this research before this selection.
Other bugs in the same repositories were studied. Historical benchmark cases
may exist in model training data; neither model-unseen status nor independence
from researcher repository knowledge is established. All six become development
data once screening begins and remain excluded from later confirmation.

## Evaluator-only local screening

Use the existing isolated study environment on Windows/Python 3.9. Preserve the
benchmark Python versions in the cohort, and disclose the runtime deviation.
Export pinned buggy and reference snapshots without Git history; omit only
legacy Tornado AppEngine symlinks under the previous export policy. Preserve
archive hashes and export metadata. Do not inspect reference patches.

For each case, copy the benchmark fixture file from the fixed snapshot into
fresh evaluator-only workspaces for both versions. Confirm the project imports
from each workspace, then run its single benchmark target command once per
version, with a 30-second process timeout. Preserve stdout, stderr, status,
timeout, source metadata and import origins. Three independent case workers
may overlap acquisition and evaluation; these timings are not a speed comparison.

An exit pattern of buggy=1/reference=0 is only a review candidate. Manually
inspect assertion meaning, test counts, skipped tests and setup issues before
admission. Import failures, absent dependencies and incompatible platforms are
explicit dispositions. Neighbor regression checks and reset verification are
still necessary before repair episodes. No coding agent sees these evaluator
workspaces, fixtures, reference source or outcomes.

## Coding backend and proposed comparison

The user authorized a separate Codex instance with Terra at medium reasoning,
or a Gemini backend through an available harness. A minimal separate Codex CLI
invocation returned the requested marker using gpt-5.6-terra, medium, existing
ChatGPT authentication. This validates access only, not patch generation, tool
execution or repair performance. Pi and OpenCode are installed; a Google API
credential was not found in the checked environment/provider inventories.
Credential contents are never recorded. Laya stays local and CUDA-only.

The draft four-arm schedule is native, cheap normalization, structural
observations, and structural observations plus Laya. The primary feasibility
contrast is structural observations against normalization, with native as the
incumbent reference. Include attention and blind-generation controls from the
governing protocol before attributing an effect to discovery/routing.

The existing Laya action classifier is not a candidate ranker. Candidate ranking,
source/trace localization, common tool logging and deadline enforcement must be
implemented and frozen before those arms run. All arms retain native read,
edit, debugger and probe-writing capabilities. Count discovery and Laya costs
inside the same total budget. No manually selected useful observer enters an arm.
Freeze a runnable configuration with explicit caps before a comparative episode;
the draft with null budgets is not permission to launch an unbounded batch.

## Minimal recommendation checks

A separate post-hoc contract replay checks existing GPU predictions. Reject
setup repair without an explicit failed precondition, preserve abstention and
unknown actions, and defer on a declared exhausted budget. Rejected model
predictions are retained, not replaced by a higher-scoring allowed action.
This intentionally narrow check does not establish action usefulness, evidence
freshness or execution validity. It runs no inference and executes no action.
It must not be reported as a corrected accuracy or new GPU experiment.
