# Repair pilot: six cases screened, native feasibility recorded

Six development cases are selected before inspecting their target outcomes:
Luigi 17 and 4, Tornado 10 and 1, tqdm 7 and 4. Earlier examined cases and
screening exclusions are excluded. These are new case IDs for this research,
not a model-unseen or confirmatory benchmark.

The [cohort](v1/cohort.json) records the eligible inventory, exposure exclusions,
selection seed and source metadata hashes. The [draft configuration](v1/run-config.draft.json)
proposes four arms and deterministic order, but has unresolved budgets and
implementation gates. No comparative repair episode has run. Candidate selection
was committed at 24e12bb before target screening.

## Screening outcomes

All six cases were screened on local Windows/Python 3.9, with separate import
origin checks and target invocations on both pinned versions: 24 processes.
This differs from the original benchmark runtimes. A single assistant reviewed
the raw outputs; these exploratory labels have no independent second review.

| Case | Disposition | Recorded evidence |
| --- | --- | --- |
| Luigi 4 | Behavioral contrast | Buggy `len(None)` failure; reference target executes one passing test |
| Tornado 10 | Behavioral contrast | Buggy template/rendered-message failure; reference target executes one passing test |
| Luigi 17 | Dependency role unresolved | Buggy local scheduler imports unavailable sqlalchemy; reference passes. Missing dependency may itself be the defect |
| Tornado 1 | Runtime incompatibility | Both variants fail setup at asyncio `add_reader` on this Windows policy |
| tqdm 7 | Runtime incompatibility | Both variants fail setup on removed `sys.setcheckinterval` |
| tqdm 4 | Runtime incompatibility | Same removed-runtime-API fixture failure |

No case was quietly replaced. These outcomes are readiness results, not six
repair attempts. [All screening records](screening/run-001/summary.json) and
[manual review](screening/review-001.json) preserve the dispositions.

A separately launched Codex CLI 0.162.1 instance, gpt-5.6-terra at medium
reasoning, returned `SKYLLA_TERRA_READY` successfully through existing ChatGPT
authentication. The minimal request used 13,992 input tokens (7,936 cached) and
11 output tokens according to CLI events. Access is verified; this was not a
repair, a tool-use test or an inference-cost comparison. Hidden harness context
is therefore material to the eventual total token budget.
The [official Terra model page](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
lists medium reasoning support; the actual local access check establishes this
account's successful invocation, rather than assuming access from documentation.

## Native-agent feasibility

The first two bounded agent episodes were blocked by child sandbox configuration:
shell reads failed, no patch was applied, and Tornado hit its 120-second cap.
Preserve [run-001](native-feasibility/run-001/summary.json) as apparatus failures,
not valid native performance observations. Its implementation is preserved at
015121d. A corrected explicit Windows workspace sandbox launcher was committed
at 07a7aae before [run-002](native-feasibility/run-002/summary.json).

| Corrected native episode | Agent wall time | Clean target | Selected class | Completion under cap |
| --- | ---: | --- | --- | --- |
| Luigi 4 | 60.6 s | 1 passed | 8 passed | Yes |
| Tornado 10 | 120.1 s including timeout cleanup | 1 passed | 24 passed | No: session timed out |

Both final production patches pass the selected checks after transfer into clean
evaluator copies. Luigi adds an explicit non-None guard to the optional COPY
column list. Tornado tolerates an absent UI namespace during template rendering.
No diagnostic mocks/instrumentation enter these final production changes.
The encompassing classes include the target, so these are 32 distinct selected
tests, not 34 independent regressions or complete repository suites.

Count only Luigi as an in-cap completed candidate under the frozen rule. Do not
erase the Tornado timeout because its final patch passes after termination.
This readiness-selected, manually described development subset cannot estimate
native accuracy or improvement over another arm. No Skylla or Laya treatment ran.

The completed corrected Luigi episode reports 196,788 input tokens, 159,232
cached input tokens and 1,531 output tokens. The earlier blocked Luigi episode
reports 107,244 input and 967 output tokens. Both Tornado timeouts lack final
usage summaries; their token usage is unknown, not zero. The four episode calls
total about 327.9 seconds, excluding source acquisition, evaluator work,
interpreter preparation and orchestration. Existing ChatGPT access was used;
no hard token cap or dollar-cost estimate is established.

The child sandbox cannot start the original virtual-environment launcher's
user-profile base interpreter. An ignored local copy of that already installed
interpreter now passes version/package imports and a 30-second-bounded sandbox
project check: five original Luigi class tests in about 2.3 seconds. This was
a non-model check on an already patched solver workspace. The evaluator's eight
tests use a later fixture file, explaining the different count. A preceding
unbounded direct check stalled and was terminated; it remains a disclosed setup
failure. The [runtime record](sandbox-runtime-check.json) preserves the bounded
result. The [v3 launcher amendment](NATIVE_FEASIBILITY_V3.md) prepares future
episodes with this interpreter; no v3 agent run has executed.

## Implication and next gate

Native investigation can already generate repairs for these straightforward
failures. Skylla needs a measurable benefit on harder evidence problems under
matched caps; patch generation or a fast classifier alone does not provide one.
The harness/evaluator path is now substantially exercised, including configuration
failures and timeout accounting. Source/trace localization, executable observation
adapters, Laya candidate ranking and a final matched configuration still need
implementation and validation before the four-arm comparison.

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
python tools/study/verify_matched_pilot.py
artifacts/venvs/study/Scripts/python.exe tools/study/screen_matched_pilot.py --name run-001
```

Use a new screening run name to preserve earlier records. The screen runs
evaluator-only target tests, not the draft coding-agent schedule. See the
[methodology](METHODOLOGY.md) for readiness, information boundaries and pending gates.
The recorded run-001 command will refuse to overwrite existing artifacts.
