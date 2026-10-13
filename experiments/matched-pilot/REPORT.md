# Next repair pilot: selection frozen, screening pending

Six development cases are selected before inspecting their target outcomes:
Luigi 17 and 4, Tornado 10 and 1, tqdm 7 and 4. Earlier examined cases and
screening exclusions are excluded. These are new case IDs for this research,
not a model-unseen or confirmatory benchmark.

The [cohort](v1/cohort.json) records the eligible inventory, exposure exclusions,
selection seed and source metadata hashes. The [draft configuration](v1/run-config.draft.json)
proposes four arms and deterministic order, but has unresolved budgets and
implementation gates. No comparative repair episode has run.

A separately launched Codex CLI 0.162.1 instance, gpt-5.6-terra at medium
reasoning, returned `SKYLLA_TERRA_READY` successfully through existing ChatGPT
authentication. The minimal request used 13,992 input tokens (7,936 cached) and
11 output tokens according to CLI events. Access is verified; this was not a
repair, a tool-use test or an inference-cost comparison. Hidden harness context
is therefore material to the eventual total token budget.

The user also offered Gemini through Pi/OpenCode. Both harnesses are installed;
the checked provider-name inventories and process environment did not expose
a configured Google API credential. This is not a claim that no credential
exists elsewhere. No key value was printed or saved.

The minimal [action contract replay](admissibility-replay.json) rejects eight
of the twelve earlier Laya recommendations, all unsupported setup repairs on
two exposed states. Four recommendations pass this narrow contract. Passing
does not mean correct or useful. There was no additional model inference,
replacement prediction, executed action or repaired code.

## Reproduction

```powershell
python tools/study/prepare_matched_pilot.py verify
artifacts/venvs/study/Scripts/python.exe tools/study/screen_matched_pilot.py --name run-001
```

Use a new screening run name to preserve earlier records. The screen runs
evaluator-only target tests, not the draft coding-agent schedule. See the
[methodology](METHODOLOGY.md) for readiness, information boundaries and pending gates.
