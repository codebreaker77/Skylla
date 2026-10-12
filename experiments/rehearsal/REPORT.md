# First local rehearsal: measured findings

October 13, 2026. Development feasibility only. No model-based selector,
downstream repair comparison, or harness-superiority result is reported.

## What ran

Three historical BugsInPy cases from three repositories were exported at pinned
buggy/fixed commits. Each targeted upstream regression fixture was run three
times on each variant in a fresh source copy and process. Four observational
probe contracts per case were frozen before target fixed snapshots were fetched
and before these probes ran. Each probe ran once per code variant.

This produced 18 targeted test executions and 24 probe executions (42 runs).
A separate follow-up ran ten selected neighboring regression tests per variant
across the cohort, in six more processes. Total: 48 recorded executions.

Recorded environment: Python 3.9.5 on Windows, with
[pinned packages](requirements.txt). This differs from benchmark interpreter
versions; it is a local portability rehearsal rather than an exact environment
reproduction. The unavailable Docker daemon led us to this scope.

| Case | Buggy targeted test | Fixed targeted test | Changed probe outputs, out of four |
| --- | --- | --- | --- |
| tqdm-2 | Failed 3/3 | Passed 3/3 | 0 |
| pysnooper-3 | Failed 3/3 | Passed 3/3 | 3 |
| youtube-dl-3 | Failed 3/3 | Passed 3/3 | 2 |

"Changed" means unequal extracted observation payloads between code variants.
It is a descriptive comparison, not a label of diagnostic usefulness, causal
identification, or benefit to a repair agent. Probe output equality does not
mean a probe never helps; both variants can expose a relevant invariant.

## Observations and interpretation

### tqdm: every candidate missed the failing control

The targeted test observes `format_meter(0, 1000, 13)` returning `None` on the buggy
snapshot. The frozen probes all exercise explicit numeric widths. Their outputs
are identical between buggy and fixed code. After inspecting the outputs and
buggy implementation, omitted/default width is a useful follow-up condition:
that return path differs from the explicit-width path.

This is a candidate-coverage failure in this menu. No selector can select an
unoffered probe. Do not retrofit a default-width candidate into this frozen run
and claim a selection improvement. A revised menu must be a new development
version, with later held-out tasks used for confirmatory evaluation.

### PySnooper: a destination-specific error, then another failure

In-memory and stderr tracing work. File-path tracing raises `NameError` for
`output_path` on the buggy snapshot, regardless of file existence or ASCII versus
non-ASCII content. On the fixed snapshot, ASCII file output works. Non-ASCII
output still raises `UnicodeEncodeError` in this Windows environment.

The probes distinguish destination behavior and help reject a simple missing-file
explanation under verified writeability. The additional encoding failure shows
why a passing targeted test must not become a claim that every related behavior
is correct. It may reflect a separate bug or an environment-specific limitation;
we did not adjudicate or repair it.

The visible NameError already gives a strong clue, so this is an easy control
case, not convincing evidence that a sophisticated selector is needed.

### youtube-dl: composition matters

Isolated named/numeric entities decode correctly in the inspected inputs.
Strings such as `a&b&quot;c` and `x&y&amp;` remain incorrectly unescaped on the buggy
snapshot and decode on the fixed snapshot. The composition and boundary probes
change; isolated-class and decoding-level probes do not.

These observations support investigating recognition boundaries, rather than a
blanket entity lookup failure. The standard-library decoder is only a comparator;
its handling of missing semicolons is not automatically this project's contract.

## Neighboring regression checks

PySnooper's four selected neighboring tests and youtube-dl's three pass on both
variants. tqdm's interval and numeric formatting checks pass, but its ANSI test
fails on both variants: observed length 140 versus expected 136, with an extra
reset sequence. This is a common failure under the recorded environment, not
evidence that the target fix caused a regression. Its cause remains unadjudicated.

There are 18 passing and two failing individual neighboring checks across both
variants. The paired failure means we cannot describe the fixed cohort as passing
every selected regression. The targeted pass/fail discriminator still reproduces.

## Costs and provenance

[Initial summary](results/run-001/summary.json) records 28.542137 seconds of summed
subprocess execution; [regression summary](results/regressions-001/summary.json)
records 6.811902 seconds. These exclude download, installation, workspace copying,
human/model research, and verification overhead. They are not full study costs.
No paid inference or external harness run was launched.

Tracked observations:

- [Initial records](results/run-001/observations.jsonl).
- [Neighboring regression records](results/regressions-001/observations.jsonl).

Source archive hashes, code commits, starting-state fingerprints, probe contract
and implementation hashes, run statuses, durations, and raw-log hashes are stored.
Raw logs and source/workspace copies stay in ignored local artifacts. The verifier
checked all 48 records against all 48 local raw logs, including unique workspaces
and equality between extracted JSON and raw output.

## Limits and next decisions

- These cases were chosen for local execution feasibility, not sampled to represent
  developer workloads. Some symptoms are easy to diagnose directly.
- Reference-patch exposure during early screening was recorded in
  [cases.json](cases.json). The cohort is development data, never a frozen holdout.
- Predictions are manually authored qualitative relations, not calibrated
  probabilities. No inter-reviewer agreement has been measured.
- A changed observation is not downstream benefit. Matched repair continuations
  remain pending authorized account access and a defined inference budget.
- Folder/process isolation verifies local reset mechanics, not adversarial solver
  isolation. Hidden evaluators must be inaccessible in real harness comparisons.
- Initial run-001 predates the addition of a runner hash to summary output. Its
  raw-log and observation hashes are present; later runs record the runner hash too.

The next cohort should contain stronger runtime ambiguity plus easy controls,
include an explicit useful-candidate availability assessment, and preserve
invalid/abstention cases. Compare native harnesses with and without Skylla as
defined in [HARNESSES.md](../../docs/HARNESSES.md). This rehearsal establishes that
the execution pipeline can capture discriminating and non-discriminating results;
it does not establish that a learned selector or broad platform is warranted.
