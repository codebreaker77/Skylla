# Issue-derived evidence replay: development pilot v1

October 13, 2026. Written before execution of the probes below. This is apparatus
development on one previously audited case, not confirmation or a model comparison.

## Selection and question

Use `pydata__xarray-3677`, already included in the public trajectory audit. Select
it deliberately because it has a small issue-level reproduction and demonstrates
caught exceptions at zero exit. This convenience selection cannot estimate
failure frequency, native-agent shortcomings or observer-discovery effectiveness.
The native agent already read the exception in the audited trace.

Question: on the original buggy source, how do shell status and explicit
issue-derived evidence differ across three checks?

The benchmark metadata endpoint identifies repository `pydata/xarray`, base
revision `ef6e6a7b86f8479b9a1fecf15ad5b88a2326b31e`, version 0.12. Metadata was
retrieved from the public SWE-bench Verified rows API. Gold patch/test fields were
not used to author probes or written into the experiment artifacts. The case's
public issue and earlier audited trajectory are known: this is not blinded.

- [Benchmark dataset](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified)
- [Pinned source](https://github.com/pydata/xarray/tree/ef6e6a7b86f8479b9a1fecf15ad5b88a2326b31e)
- [Earlier audit](../trajectory-audit/REPORT.md)

## Three hand-authored modes

All modes construct `Dataset({'a': 0})` and a named scalar `DataArray(1, name='b')`.
All first run the top-level merge. The issue requires the dataset method to
support the same named input.

| Mode | Check | Recorded evidence |
| --- | --- | --- |
| top_level_only | Only run the working top-level API | Variables; method explicitly not exercised |
| caught_method | Run method and catch its exception | Exception type/message; process can exit zero |
| assert_relation | Require method to succeed and equal the top-level result | Explicit relation; nonzero exit on failure |

This is an assertion authored from the issue, not a discovered observer. No
universal rule converts every exception into a reported symptom. An unexercised
method leaves the issue unresolved, even if the top-level call succeeds.

## Execution and information boundary

Run each mode in a fresh process three times in fixed order. Nine invocations
test apparatus stability on one bug, not nine independent cases. Use isolated
Python 3.10 with NumPy 1.23.5 and pandas 1.5.3. These are compatibility choices,
not the original benchmark container. Record all dependency versions, actual
import origin, source revision/tree, script/method hashes, exit status, structured
observations, stderr and full subprocess elapsed time. Set UTF-8 output and a
fixed Python hash seed. Reject a changed tracked source or unexpected import.
Apply a 30-second timeout; preserve infrastructure failures. No source edits,
reference fix, model calls, classifier thresholds or production repairs occur.

Preparation/download time is excluded from probe latency and must not be claimed
as a complete workflow cost. The source checkout, environment and third-party
transcripts remain ignored. Only original probe code and observations are tracked.

## Interpretation gates

Do not call `top_level_only` a verified bug absence. Do not call zero-exit
`caught_method` a successful requirement check. An assertion failure can confirm
this specific reported requirement is unmet; it does not establish the root cause.
If this contrast is reproduced, it supports explicit evidence handling already
available to native agents. It cannot establish superiority over normalization,
usefulness of Laya, unseen generalization, or a breakthrough.

Next: executable cases where observer/input discovery might add value, including
adequate-probe controls. The matched agent protocol remains
[NEXT_COMPARISON.md](../trajectory-audit/NEXT_COMPARISON.md).

## Reproduction (PowerShell)

```powershell
git init artifacts/sources/xarray-evidence
git -C artifacts/sources/xarray-evidence fetch --depth 1 https://github.com/pydata/xarray.git ef6e6a7b86f8479b9a1fecf15ad5b88a2326b31e
git -C artifacts/sources/xarray-evidence checkout --detach FETCH_HEAD
py -3.10 -m venv artifacts/venvs/evidence-pilot
artifacts/venvs/evidence-pilot/Scripts/python.exe -m pip install -r experiments/evidence-pilot/requirements.txt
python tools/study/evidence_pilot.py run --python artifacts/venvs/evidence-pilot/Scripts/python.exe --name run-002
python tools/study/evidence_pilot.py verify --name run-001
```

Use a new run name; existing records are never overwritten. Verification checks
artifact integrity, not independent interpretation or replay equivalence.
