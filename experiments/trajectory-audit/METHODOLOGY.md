# Public diagnostic-trajectory audit: method v1

October 13, 2026. Development audit, one AI reviewer, no newly launched model
sessions. Select and commit the sample before downloading trajectory content.
This local sampling freeze is not external preregistration or blinded human review.

## Source and sample

The [SWE-bench submission registry](https://github.com/SWE-bench/experiments)
lists public execution and trajectory assets. Pin registry commit
`40f164d5b8f1d249bf95a6df8b74b577fd8e519d`, submission
`20260901_mini-v2.4.2_gemini-3-5-flash`, and asset commit
`2f6637a2557da1f7b5f2b583ab7090a077bbeed2` in
[the public asset repository](https://github.com/SWE-bench/20260901_mini-v2.4.2_gemini-3-5-flash).
These are existing mini-SWE-agent/Gemini traces, not Skylla-authored probes.
Submission model/harness metadata are publisher-reported, not reproduced here.

There are 441 trajectory files in the pinned inventory. Their availability is
not the entire SWE-bench Verified population. Sort files by SHA256 of
`skylla-observation-audit-v1|path`; take the first 15 with at most three from one
repository. Do not filter by reported success, probe count, or interesting errors.
Include missing/nonparseable downloads in acquisition dispositions; no silent
substitutions. Record paths, Git blob IDs, sizes, and sampling/inventory hashes.

This repository-capped convenience sample is for taxonomy and prototype design.
It cannot estimate defect frequency in current agents, compare providers, or
measure Skylla's benefit. Menu caps introduce sampling bias; only one submitted
model/harness run is represented. All inspected instances become development
data and must be excluded from subsequent confirmation tasks.

## Evidence handling

Download trajectories as JSON data. Never execute recorded commands. Preserve
full content only in ignored local artifacts, verify Git blob hashes, and publish
source links/hashes plus original paraphrased annotations. No public asset license
was found in its root inventory; do not relicense or redistribute full transcripts,
reasoning, or third-party code under Skylla's MIT license.

Read the task description and review the first three shell events that plausibly
execute Python, a test runner, or a reproduction script, with adjacent observations
and agent context. Text search is candidate extraction, not semantic labeling.
Reject mere searches, installs, and edit-only scripts with an explicit exclusion
reason. Retain failed setup attempts. If fewer than three candidates exist, retain
the trajectory and record the actual number. Preserve message/call indices and
command/output hashes so the annotation can be checked against its source.

Later diagnostic events may be inspected to clarify a reviewed event, but are
not added to its denominator. Clearly mark such context use. This is an early-event
audit, not exhaustive reconstruction of every action or an execution replay.

## Annotation fields

For each reviewed event record:

- Intent: reproduction, exploratory observation, regression/validation, or unknown.
- Visible outcome: symptom observed, no visible failure, setup blocked, or unknown.
- Observation surface: returned value, exception, test assertion, textual output,
  internal state, or mixed/unknown.
- Evidence support: documented by log, plausible interpretation, or unknown.
- Setup issue: name a visible loader/dependency/command failure without claiming
  that every exception is unrelated to the target bug.
- Missing observation: a specific gap supported by context, or unknown. Generic
  passing output alone does not prove an observation gap.
- Contrast: explicitly recorded buggy/current-state contrast, suggested comparison,
  or not established. No gold replay is available in this audit.
- Next check: an actionable candidate and the evidence it would seek, with cost
  unknown when timing information is unavailable.

Observed failure is not automatically correct causal attribution. Observed pass
is not automatically bug discrimination. Do not call an observer inadequate
merely because a trace eventually failed. Inspecting commands is insufficient to
establish which import, branch, or object actually ran unless the log shows it.

The reviewer is the coding assistant conducting this audit; annotations are not
independent human ground truth. Preserve unknown labels and reviewer uncertainty.
A later second review and executable replay are needed before training a detector
or using these labels as a confirmation outcome.

## Deliverable and next gate

Deliver 15 pinned trace records, early-event annotations, acquisition dispositions,
and a report distinguishing visible setup/observation problems from unestablished
causal or usefulness judgments. Raw counts apply only to these reviewed events.
Do not turn them into a natural-prevalence claim.

Use the audit to freeze a separate development comparison protocol: observer
discovery from code/traces without an evaluator-supplied correct field, strong
cheap baselines, complete generation/execution costs, and final target/regression
verification. Freezing that protocol is not executing it. Live model evaluation
still requires configured access and budget; this audit does not spend either.
