# DeepEval / local Laya shadow baseline: apparatus protocol v1

October 13, 2026. This is an executable adapter and integration exercise, not a
Jev accuracy study or a matched coding-agent repair experiment.

Use pinned DeepEval 4.2.8, Laya 0.3.20, Transformers 4.51.3 and CUDA PyTorch 2.6.0
in a separate Python 3.10+
environment. The controller and prior study environment retain their existing
dependencies. The optional adapter uses the documented custom `Classifier`
in `system_one` mode, with five explicit debugging action descriptions and
no-label behavior. This is an application of existing DeepEval primitives.
[Official classifier documentation](https://deepeval.com/docs/classifiers-custom).

## Information and execution boundary

Each input contains a version, state ID, issue, remaining time and explicit
preconditions/observations/requirement-exercise status. Both rules and the optional
judge receive this solver-visible state. No evaluator outcomes, expected labels,
reference patches or future observations are supplied by the input builder.
Top-level unknown fields are rejected. This validation cannot detect semantic
leaks hidden inside arbitrary issue text or observations; independently review
future study exports. Development examples use exposed cases and manually
paraphrased issues/requirement-exercise annotations, not a blinded dataset.

The judge receives the issue/state/budget as its test-case input and the evidence
as its actual output. Save this mapping and the canonical shared state/options
hashes. SDK prompt/state rendering differs from the rules representation; do not
claim byte-identical provider prompts. The actions describe possible next steps,
not causal labels or verified completion. Rules recognize explicit setup failure,
a recorded method exception or an unexercised requirement; ambiguous cases return
to ordinary investigation. Shell status is not treated as repair success.

Everything runs in shadow mode: recommendations do not execute probes, edit code
or change repairs. Zero remaining time blocks inference. Positive remaining time
is supplied context, not a hard deadline enforced by this adapter; the eventual
outer harness must enforce elapsed-time/money limits, source validity and actions.
SDK retries and token accounting need provider-side verification before a live
budgeted study. `calls_attempted` counts adapter invocation attempts, not proven
billable HTTP requests. A backend failure is retained without a rules fallback.

The user selected local Laya only, with no Jev API, and explicitly required GPU
inference. The live CLI takes a local checkpoint path; it has no hosted Jev backend.
The checkpoint is `convaiinnovations/laya`, `typed-decisions` subfolder at revision
`7b928d828b7b0e022f929d9bd2e44165aa270148`. Content hashes and LFS hashes are
verified by the downloader. Keep weights ignored and preserve downloaded files:
the SDK gets separate tokenizer/config copies and a hard link to read-only weights.
No API key is needed. No hosted inference is performed.

This machine has an NVIDIA GTX 1050 with 3 GB VRAM. Require CUDA and use fp16
weights/autocast; no compiled/TileLang fast path is used. The pinned SDK normally
falls back to CPU on CUDA OOM. The bridge overrides its private `_infer` method
with a strict CUDA pass, and rejects a non-CUDA loaded model before prediction.
OOM is a failure, not a CPU retry. CPU tokenization, serialization and loading
are separate from neural inference. Record device, dtype, load and inference time.
This private method integration requires revalidation before an SDK upgrade.

Use max_len 1024 and head_max_len 256 with an explicit typed checkpoint. Preserve
raw token usage and probabilities. Oversized option definitions fail; remaining
state text can be truncated by the SDK. Full stored state is not proof that every
token reached the model, so inspect lengths before interpreting results.

## Local validation

Standard-library tests cover exhausted budget, missing local checkpoint, prohibited
top-level evaluator fields, non-finite budgets and exception handling. A separate
optional integration test injects a local `DeepEvalBaseSystemOneModel` stub into
the real pinned classifier, testing state/options mapping, abstention and usage
reporting without a hosted model. Its predetermined label is a test fixture, not
a Jev prediction, accuracy result or training label.

Record package inventory and wall time for the integration exercise. Unknown
provider costs/token usage remain unknown, not zero. A stub's explicitly returned
zero cost represents that local test only. An instrumented System-1 wrapper records
the exact SDK state/questions and typed probability answers, including failures
and reported costs. Provider-internal HTTP retries remain unobserved. These
vectors enable a later calibration evaluation with independently reviewed labels;
this integration test itself supplies no calibration evidence.

## Reproduction

```powershell
py -3.10 -m venv artifacts/venvs/judge-baseline
artifacts/venvs/judge-baseline/Scripts/python.exe -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu118
artifacts/venvs/judge-baseline/Scripts/python.exe -m pip install -r experiments/judge-baseline/requirements.txt
python tools/study/build_judge_states.py
python tools/study/judge_baseline.py experiments/judge-baseline/states/xarray-top-level.json --backend rules --output artifacts/judge-baseline/rules-reproduction.json
artifacts/venvs/judge-baseline/Scripts/python.exe tools/study/check_judge_integration.py
```

Existing exports/results are never overwritten. The outer coding model/harness
remains unconfigured. Selecting Laya supplies the System-1 judge, not a patch-
generating coding model. These shadow decisions do not satisfy the matched agent
repair prerequisites or demonstrate repair gains.
