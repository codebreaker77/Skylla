# Local System-1 shadow apparatus

October 13, 2026. The user selected local Laya only, without a Jev API, and
required GPU inference. No hosted Jev request was made. Actual Laya GPU predictions
are pending CUDA setup; this report describes completed apparatus validation.

## Available implementation

The optional adapter applies DeepEval's existing System-1 classifier interface
to five debugging actions plus its no-label option. A shared input contract
contains issue, state identity, remaining time and explicit runtime evidence.
The rules backend runs without optional dependencies. The local Laya bridge
maps the same SDK questions into Choice requests, recording exact provider state,
questions, typed probability answers, costs where exposed and failures.

This is an integration of existing primitives, not a novel judge. It recommends
actions in shadow mode and neither executes probes nor repairs production code.
The dependency-free Skylla controller is unchanged.

## Completed validation

- Real DeepEval 4.2.8 integration with a local stub passed three checks: a chosen
  action maps correctly, no-label output is retained, and a failure preserves no
  recommendation or sensitive exception text. Outbound socket connections were
  disabled during these checks. These are predetermined test outputs, not model
  predictions or accuracy measurements.
- Three development inputs were exported from the exposed Xarray/Tornado replay
  records. Only buggy runtime evidence enters the shadow examples; reference test
  outputs and patches are not exported. Issues and requirement-exercise flags
  are manually authored development context, not independent ground truth.
- Pure tokenizer checks using the actual SDK representation retain all six
  markers and identical full sequences at the selected limits. Tokens: Tornado
  native-close 456, Xarray caught-method 367, Xarray top-level 329. No weights or
  neural forward were used for these checks. Reversed action order will also be
  tested in the GPU run; this audit checks original order only.
- The pinned typed-decisions checkpoint was downloaded and all file hashes
  recorded; the large weight file matches its published LFS SHA-256. Weights and
  environment files remain ignored.
- Standard-library tests now include exhausted budgets, missing local model,
  prohibited top-level evaluator fields, non-finite budgets and strict CUDA-only
  behavior. A CUDA OOM is not retried on CPU.

The initial `integration.json` and `offline-records.json` are earlier development
records, preserved before the adapter's final instrumentation. Their adapter hash
identifies that earlier unarchived implementation; they do not certify the current
code. Use `integration-v2.json` for current-code integration verification. Original
state/probe provenance is checked separately. No historical artifact was overwritten.

## GPU configuration and pending measurement

Use PyTorch 2.6.0 CUDA 11.8, Laya 0.3.20 and Transformers 4.51.3 with checkpoint
revision `7b928d828b7b0e022f929d9bd2e44165aa270148`, typed-decisions only. Require the
GTX 1050's CUDA device, fp16 weights/autocast, max_len 1024 and head_max_len 256.
The bridge disables the pinned SDK's CPU retry path through its private inference
method; this integration must be revalidated before upgrading the SDK. CPU data
preparation/serialization is distinct from neural inference.

The upcoming run freezes three states, original/reversed action order, two
repetitions and one separately recorded warmup: twelve scored shadow decisions
plus warmup. It measures inference execution and ordering/repeat stability, not
repair success or calibrated action correctness. File hashes/configuration are
written before model loading. If loading or prediction fails, retain the attempt
and use a new run name; do not silently fall back to another model/device.

CUDA installation is the outstanding prerequisite. The ordinary full-file wheel
transfer stalled; a resumable byte-range download is in progress and must match
PyTorch's published SHA-256 before installation. No GPU inference has run yet.

## Reproduction

See [methodology](METHODOLOGY.md) for dependencies and the information boundary.

```powershell
python tools/study/verify_shadow_apparatus.py
python tools/study/prepare_laya.py
artifacts/venvs/judge-baseline/Scripts/python.exe tools/study/run_laya_shadow.py --name laya-gpu-002
```

Run `prepare_laya.py` only when its recorded manifest is absent; use a new run
name for predictions. The current checkpoint manifest records original download
hashes; the bridge keeps SDK-normalized config copies in a separate local folder.
No large weights or third-party source are committed. The coding model/harness
for the eventual matched repair comparison remains unconfigured. Laya supplies
the small decision layer; it cannot generate the production patches by itself.
