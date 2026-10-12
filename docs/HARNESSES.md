# Current harnesses and Skylla's comparison target

Reviewed October 13, 2026. This is a documentation audit, not a measured benchmark.
Capabilities do not establish how often a particular model uses them successfully.
Live documentation must be pinned or archived again when the experiment starts.

## What they already do

| Harness/workflow | Documented debugging capabilities | Consequence for Skylla |
| --- | --- | --- |
| Claude Code | Gather context, take action, verify; repository search, edits, shell commands/tests; configurable skills, hooks, MCP, and subagents | A model-driven tool loop is already a capable debugging baseline |
| Cursor Debug Mode | Multiple hypotheses, logging instrumentation, user reproduction, runtime-log analysis, targeted repair, verification and cleanup | Hypotheses plus runtime evidence is direct product overlap |
| Codex CLI | Explore/edit repositories and run local tools; skills/plugins, delegation, review, MCP; noninteractive execution with structured event logs | Executable debugging and auditable command output are existing capabilities |
| OpenHands SDK | Bash/file/browser tools, custom tools/MCP, planning, context compression, persistence and tracing | Extensible, model-agnostic agent infrastructure is already available |
| mini-swe-agent | Simple shell-action loop and linear history with replaceable environment/model | A small baseline can already run arbitrary debugging experiments through the shell |

Sources inspected:

- [Claude Code architecture](https://code.claude.com/docs/en/how-claude-code-works).
- [Claude Code best practices](https://code.claude.com/docs/en/best-practices):
  recommends executable checks, goals, Stop hooks, and independent verification
  workflows. Compare a well-configured workflow rather than intentionally weak prompting.
- [Cursor Debug Mode](https://cursor.com/docs/agent/debug-mode) and
  [December 2025 introduction](https://cursor.com/blog/debug-mode).
- [Official OpenAI documentation: Codex CLI](https://learn.chatgpt.com/docs/codex/cli)
  and [noninteractive mode](https://learn.chatgpt.com/docs/non-interactive-mode).
  JSONL exposes events and usage suitable for instrumentation of comparisons.
- [OpenHands SDK](https://docs.openhands.dev/sdk).
- [mini-swe-agent's official repository](https://github.com/SWE-agent/mini-swe-agent).
  Its simple architecture is relevant; advertised benchmark scores are not
  comparable to our unmeasured pilot and are not used as a target number.

## What we cannot infer from the docs

The documentation reviewed does not establish a standardized, cross-harness
protocol for evaluating multiple alternative probes from the same state and
measuring their downstream benefit. That is a possible contribution, not proof
that those products cannot do it. A developer can already ask a harness to write
predictions, run isolated experiments, and export a notebook.

Do not claim that agents only guess, never inspect runtime state, lack hypotheses,
cannot use a debugger, or cannot verify patches. Actual traces must establish
when they waste probes, lose evidence, misinterpret observations, or over-edit.

Cursor is especially important: its specialized debugging mode deserves a direct
comparison. A generic edit-test baseline alone would miss the closest product
workflow. Its user-assisted reproduction also means human effort must be recorded.

## The product objective

Skylla should improve an existing harness on difficult debugging decisions:
select whether to investigate at all, choose a discriminative feasible probe,
validate the control, preserve evidence through state changes, and hand findings
back to the repair policy. The harness should remain free to use all its normal
tools and to abstain from Skylla when a cheap direct fix is better.

The first target is **the same harness and model with Skylla versus without it**.
Replacing Claude Code with a different model or giving Skylla extra runtime tools
would conflate selection with other changes.

## A fair test of "better"

There are two separate questions:

1. Does adding Skylla help within a harness at the same budget and capabilities?
2. Does that assisted configuration compare favorably with the best configured
   alternatives on the same cohort?

For each named configuration, record exact harness/version, model identifier,
reasoning setting, prompts/rules, extensions, tool access, operating environment,
memory/session reset, token/money/time caps, and human interventions. Preserve
traces and independent evaluator results. Cross-product configurations with
different native models support system-level comparisons, not isolated harness
or selector effects.

Primary target: higher verified success at a fixed total budget. Secondary targets:
lower time/cost, fewer unnecessary edits, fewer invalid/redundant probes, and no
increase in false definitive conclusions. Predefine the primary contrast and
how uncertainty and multiple comparisons are handled.

To claim superiority over every *tested* baseline, require support against each
predeclared baseline, not just their average. Report ties, tradeoffs, and failure
families. "Better than all tools" without a bounded tested set is not a defensible
claim. An API can be harness agnostic even when performance effects are not.

## Experiment arms

| Arm | Changes from the native configuration | What it isolates |
| --- | --- | --- |
| Native | Normal tools and documented recommended debugging practices | Actual incumbent workflow |
| Scientific notebook | Add explicit hypotheses/predictions/evidence instructions | Benefit of prompting and organization |
| Runtime tools | Equal additional runtime access, without Skylla selection | Benefit of new observations/tools |
| Skylla with cheap selection | Same contracts and evidence, deterministic policy | Benefit of structure with low selection cost |
| Skylla with model selection | Swap only selector on the same candidates | Marginal value of model-based selection |

Record voluntary adoption first. If a forced-use arm is needed, label it as a
separate intervention. Count subagent inference, instrumentation, reset time,
reproduction effort, and failures. Do not weaken the native arm by banning its
own debugging scripts or good practices.

## Access observed locally

Python 3.9 is available. Docker's Linux daemon was unavailable during screening.
The Codex command is installed; Claude Code was not found on PATH. These checks
do not establish account authentication, model access, or authorization to spend.
No external model/harness repair run has been launched.

The three historical cases are a local feasibility rehearsal. They do not
establish Skylla's superiority, developer adoption, or harness transfer.
