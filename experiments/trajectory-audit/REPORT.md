# Public trajectory audit: what the logs establish

October 13, 2026. Fifteen genuine public coding-agent traces were sampled before
content inspection. **This audit does not yet establish a missing-observer
advantage for Skylla.** It identifies simpler evidence-handling and setup issues
that a later comparison must control for, and existing agent behavior we must beat.

## Source and scope

Sampling and acquisition were frozen in commit `b3fbe1a` before downloading
trajectory content. The [sample](sample.json) pins an official public artifact
repository, Git commit, blob IDs, and an outcome-independent hash ordering.
Fifteen traces span seven repositories, capped at three per repository, from a
single mini-SWE-agent/Gemini submission. All downloads matched their Git blobs.
[Method](METHODOLOGY.md), [acquisition](acquisition.json), and
[extracted event identities](events.json) preserve this provenance.

The source inventory contains 441 released trajectory files, not every benchmark
instance. This is a development convenience sample, not a representative sample
of today's agents. It includes bug reports and enhancement/refactoring requests;
do not describe all fifteen as independently verified bugs. No target command was
executed, no repair was evaluated, and no inference account was used.

The coding assistant reviewed the task and first three runtime-like shell
candidates per trace. Seven candidates were excluded as edit-only, version-only,
or docstring-only events. This leaves 38 runtime events. This is an early-event
audit, not exhaustive annotation of every step. A later UTF-8 recovery was read
as explicitly marked context and excluded from these counts.

## Descriptive observations

| Reviewed runtime outcome | Events |
| --- | ---: |
| No visible failure | 20 |
| Reported symptom observed | 6 |
| Setup or probe precondition blocked | 8 |
| Interpretation unresolved | 4 |
| Total | 38 |

These are single-assistant judgments, not independent human labels or replayed
causal evidence. A passing result need not test the issue. An exception need not
be a setup failure. One numeric symptom interpretation is explicitly marked
plausible. All event-level reasoning and proposed checks are in [audit.json](audit.json).

### Process success can coexist with a visible exception

Three reviewed events have zero exit status while printing an exception: two
Xarray exploratory/reproduction scripts and one Astropy exploration. The scripts
catch and display errors. The Xarray method reproduction visibly reaches project
code and exposes its reported exception despite zero exit status.

The agent reads the output and continues investigating. This demonstrates why
an exit-code-only adapter loses evidence; it does not demonstrate that the agent
ignored that evidence or that Skylla would improve its repair.

### Generic setup triage can misclassify the bug itself

In `pytest-dev__pytest-6197`, the targeted collection reproduction exits with
pytest code two because an unintended package initializer is collected and its
assertion runs. That collection failure is the reported regression, not merely
an environment obstacle. Our older screening heuristic treats non-one pytest
failures as setup problems; it is not suitable as a universal diagnostic classifier.
The older frozen records and their stated limitations remain unchanged.

A new adapter must preserve raw runner status and classify its meaning in task
context, or abstain. It must not relabel all collection errors as benign setup.

### Some probe obstacles already have cheap recovery

Three reviewed test attempts request a missing pytest executable. Other events
hit file/output encoding problems, missing angular units, and an incompatible
celestial-frame construction. Those failures can block an intended check before
its relevant operation runs. Their observed details differ; a single generic
exception category would obscure that distinction.

In the accent-normalization trace, changing the printed representation still
fails under ASCII. Later context shows the agent explicitly setting UTF-8 output
and exposing the intended comparison. The script uses copied function logic,
so this is not a replay of the actual project function. It is evidence of native
agent recovery, not a Skylla intervention or verified project diagnosis.

### Native agents already add meaningful observations

The Sphinx traces inspect AST defaults and class-signature annotations. The
Astropy sliced-coordinate trace changes its input path to avoid a frame-resolution
failure, then adds dimensional, slice-index, and axis-correlation observations.
The SymPy traces compare ordered gamma factors and alternative solver paths.

These are useful examples of behaviors that must remain available to the native
baseline. They do not prove that every observation was necessary, that its causal
interpretation was correct, or that it yielded a correct final patch.

## Case map

| Selected trace | Early-window observation | Candidate next evidence |
| --- | --- | --- |
| scikit-learn-14496 | Existing tests pass; fractional-input reproduction raises target type error | Effective neighbor count across input boundaries |
| django-15128 | Existing suites pass; alias reproduction absent from reviewed events | Alias-map changes during query combination |
| django-11276 | Runner unavailable, then fixture decoding blocks suite | Compatible encoding and wrapper equivalence |
| pytest-7982 | Existing path tests pass; edit is not a behavioral check | Actual collected nodes under symlink traversal |
| django-14787 | Partial-wrapper metadata inspected; test runner recovered | Metadata through project decorator path |
| xarray-3677 | Target method error is printed despite successful process status | Same-input top-level/method assertions |
| scikit-learn-15100 | Display encoding blocks copied-function comparison | Encoding-safe actual project execution |
| astropy-13398 | Units/frame/time assumptions affect exploratory transforms | Explicit transform preconditions and target time |
| sphinx-7757 | AST defaults inspected directly | Rendered positional-only signature |
| sphinx-7590 | Existing tests pass; editing helper errors are excluded | Literal-suffix parser and rendering outputs |
| sympy-18211 | Equation path fails; direct solver returns a condition set | Matching domains and dispatch evidence |
| sympy-23824 | Ordered-factor reproduction fails while existing tests pass | Same ordered assertions after repair |
| sphinx-10449 | Agent already observes return-annotation metadata | Final rendered class documentation |
| pytest-6197 | Collection error is the reported regression | Collected node identities before/after repair |
| astropy-13579 | Revised probe exposes numerical discrepancy and internal mapping | Explicit slice-equivalence relation |

Full instance IDs, source links, and exact message/command/output hashes are in
the sample and audit records. The table is a proposed evidence map, not a list
of confirmed missing observers or successful Skylla probes.

## Decision

Confirmed missing internal observers: **none established by this limited audit**.
That does not show they are absent. It means these logs and this review do not
justify a frequency estimate or automatically labeled training set for the idea.

Before a complicated discovery policy, keep a strong baseline that handles
provenance, output encoding, task-specific runner conventions, caught exceptions,
and the distinction between script edits and behavioral checks. A future observer
discovery method must improve beyond both that baseline and native agent behavior.
The [next comparison protocol](NEXT_COMPARISON.md) makes these comparison arms and
go/no-go conditions explicit. It has not been executed.

## Reproduction and limitations

```sh
python tools/study/verify_trajectory_audit.py
python tools/study/verify_trajectory_audit.py --restore
```

`--restore` downloads the pinned public blobs into ignored local artifacts when
missing. No recorded command is executed. Full third-party transcripts and code
are not redistributed in this repository. Sources retain their own rights; our
annotations are original paraphrases. Public schema details are documented by
[mini-SWE-agent](https://mini-swe-agent.com/latest/usage/output_files/).

Verification checks source hashes, extraction, complete annotation coverage, and
count consistency; it does not validate reviewer interpretation. No independent
second review, replayed code-state contrast, hidden-test evaluation, causal labels,
or counterfactual costs are available here. Failures outside the early window and
unreleased trajectories are not covered.
