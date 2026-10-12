# Next study and path to a defensible advantage

October 13, 2026. Proposed plan. This document formulates a testable direction;
it does not claim a new algorithm, established novelty, or an existing moat.

## Decision

Time-box the next research iteration to two focused weeks. Investigate whether
Skylla should recognize an inadequate experiment menu and request a missing
distinguishing check, instead of always selecting from the offered candidates.

The longer product direction remains a model/harness-agnostic debugging experiment
tool for developers and agents. The next study narrows the research question,
not the user groups or integration boundary.

An indicative six-to-eight-week horizon can cover a useful prototype and a
stronger pilot if execution infrastructure, account access, and budget are
available. It cannot guarantee a publishable superiority result or a moat.
Planning estimates assume one focused builder; setup and evaluation are the
critical uncertainties. A sustained advantage needs repeated use and continued
maintenance over a longer period.

## Why change the immediate question?

Our [development rehearsal](../experiments/rehearsal/REPORT.md) supplies three
specific problems:

| Observation | Consequence for the next study |
| --- | --- |
| Every tqdm probe used an explicit width; the failure involved omitted width | Selection quality and candidate availability must be separate measurements |
| PySnooper's target fix passed, but non-ASCII file output still failed locally | A narrow passing check does not establish completion of the investigation |
| A neighboring ANSI test failed on both tqdm variants | Evaluators must distinguish pre-existing failures from repair-induced regressions |

Three convenience cases do not establish how often these failures occur in
current agents. First quantify them on a better cohort. Keep the original
observations and candidates unchanged; follow-up menus become new versions.

## Proposed contribution to test

**Can an agent improve verified repair within a fixed budget by deciding when to
expand its debugging experiments, and when the current evidence already suffices?**

A first controller has a small action set:

1. Continue the existing repair policy when additional probing is unnecessary.
2. Execute a feasible distinguishing probe from the current menu.
3. Request a bounded expansion of the menu when available probes are uninformative
   or expected controls are missing.
4. Refresh observations that no longer apply after a state change.
5. Return unresolved when the budget or available evidence is insufficient.

The algorithm is a research proposal. These actions are familiar planning and
diagnosis techniques; their names or combination do not prove novelty. A possible
paper contribution is a precise task, reproducible corpus, and measured benefit
over strong existing workflows on realistic repository bugs.

## Smallest meaningful method

Keep the first policy inspectable and cheap:

- Validate execution preconditions through executable checks, including whether
  the intended input/control actually reached the program.
- Inspect the declared hypothesis/outcome matrix. Flag identical predicted
  outcomes and duplicate experiments; preserve uncertainty when predictions are
  incomplete or qualitative.
- Use a small set of reviewed expansion templates: omitted versus explicit
  options; boundaries; fresh versus retained state; single test versus ordered
  suite; package/configuration origin; relevant encoding settings.
- Ask the same configured generator for at most a bounded number of additions.
  Preserve exact candidate and prediction versions before execution.
- Choose among feasible candidates with a simple cost/discrimination policy.
  Do not require a trained ranker for this study.
- Initially invalidate evidence conservatively after code/environment changes.
  More selective reuse is a separate ablation, with measurable validity checks.

Predicted distinctions are fallible. A menu with varied predictions can still
omit the real mechanism; a boundary template can still miss the trigger. The
controller emits warnings and decisions, not a certificate that every cause is
covered. Measure false expansion and missed-expansion decisions explicitly.

The executed probe record should state the tested condition, verified
preconditions, actual observable result, state identity, and remaining alternatives.
It should not convert an exception, confidence increase, or failed setup into
a definitive causal conclusion.

## New prior-art checks that narrow the proposal

These primary abstracts were checked on October 13; full methods/artifacts still
need inspection before experimental adaptation or novelty claims:

- [PROBE / Debugging the Debuggers](https://arxiv.org/abs/2605.08717), May 2026,
  revised June: organizes failed-run telemetry into diagnosis and bounded recovery
  guidance for subsequent attempts, including software repair. Evidence-backed
  recovery guidance is already adjacent prior art.
- [PACMI](https://arxiv.org/abs/2610.05732), October 5, 2026: proposes dependency
  graphs and cascading memory invalidation. Evidence invalidation alone is not
  an unexplored contribution.
- [Presentation, Not Mechanism](https://arxiv.org/abs/2607.16019), July 2026:
  reports that apparent gains from a detailed revision ledger largely disappear
  under a matched presentation control, with coarse invalidation performing better
  on its current-state queries. This is a different task, but motivates matching
  rendering and testing simple invalidation before adding graph complexity.

Also retain [the focused audit](PRIOR_ART_AUDIT.md): AutoSD, Debug2Fix, ReplayLens,
CAR, REFLECT, and executed-replay credit studies. Check active diagnosis,
cost-aware test generation/selection, incremental regression testing, and adaptive
experiment planning. No absence claim follows from a limited search.

## Work sequence and deliverables

| Stage | Indicative effort | Concrete output | Gate |
| --- | --- | --- | --- |
| Scope and overlap audit | Days 1-3 | Claim matrix: existing capability, proposed difference, evidence needed; freeze the first question | Narrow/reuse the method if prior work already covers it |
| Cohort and failure measurement | Days 3-7 | Screen the proposed 12 historical cases across four repositories, plus four separately scored controlled cases; frozen manifests and exclusions | Reproducible acceptance checks and enough ambiguity to study selection |
| Minimal controller and arm definitions | Days 5-9 | Feasibility checks, bounded expansion templates, cheap selection, state-bound evidence, exact comparison configurations | Core runs locally; generator/provider belongs in an adapter |
| Matched development comparison | Days 9-14, access permitting | Paired traces, outcomes, full costs, failed/abstained cases, and a decision report | Expand only if this exposes useful decision variation or a credible improvement |
| Product pilot | Following 2-4 weeks, conditional | CLI and one structured interface; a second harness adapter; developer task observations | Independent verification and actual workflow usefulness |
| Confirmatory study and paper | Sized after pilot variance/cost measurements | Frozen holdout, powered primary comparison, reproduction package, manuscript | Claims match uncertainty and tested scope |

Dates are planning bounds, not guarantees. If environment preparation consumes
the first week, reduce the development cohort explicitly and record that change.
Do not quietly weaken acceptance checks or extend research indefinitely.

Historical selection should use failure characteristics and execution feasibility,
not whether Skylla succeeds. Include easy direct-fix controls as well as runtime
ambiguity. Controlled cases deliberately test omissions and interacting causes;
they cannot support a natural-prevalence claim. All pilot cases are development
data and are excluded from a later tuned-and-frozen confirmation set.

## Comparisons that can disprove the idea

Within the same harness/model, compare:

| Arm | Purpose |
| --- | --- |
| Native debugging, using documented best practices | Real incumbent performance |
| Scientific-debugging prompt and evidence notebook | Whether instructions and better presentation suffice |
| Fixed-menu cheap selector | Whether ranking offered probes is enough |
| Blind bounded menu expansion | Whether simply generating more candidates is enough |
| Proposed conditional expansion | Whether the expansion decision adds value |

Initial menus and generator configurations are shared for the diagnostic
comparison. Every expansion arm receives the same maximum generation allowance;
the policy controls when to consume it. Include generation and execution in the
same total time/money cap. Native agents keep their normal ability to inspect,
write diagnostic scripts, and regenerate ideas. Do not handicap them to create a win.

Use the same evidence presentation when comparing validity mechanisms. Compare
retain-all, conservative invalidation, and selective revalidation separately;
do not attribute a better notebook format to a better algorithm.

Start with one solver/harness to identify the effect, then replicate in another.
Claude Code and Cursor Debug Mode are important incumbent configurations, as
documented in [HARNESSES.md](HARNESSES.md). Model/harness account access and the
inference budget remain unresolved; no external runs are authorized by this plan.

## Measurement and go/no-go

The primary outcome remains independently verified repair success under a fixed
total budget. Secondary measurements cover time/cost, unnecessary edits, wrong
definitive conclusions, redundant/invalid probes, expansion frequency, and human
reproduction effort. Preserve unsolved runs and timeout censoring.

Candidate availability is evaluated retrospectively through executed branches,
with uncertainty and continuation-policy dependence. It is not information the
live controller receives. In controlled tasks, reviewed mechanisms can supply
additional labels; real tasks may have disputed or incomplete mechanism labels.

Before a confirmatory study, preregister the primary contrast and minimum useful
effect, calculate sample needs from pilot variance and repository clustering, and
account for multiple comparisons. A practical secondary target such as 20% lower
cost is provisional and cannot become the winning criterion after inspecting data.

Decision outcomes:

- If the native or notebook arm matches the controller, prioritize the demonstrated
  useful component and revise the algorithmic claim.
- If blind expansion matches conditional expansion, prefer the simpler expansion
  policy; a sophisticated detector has not earned its overhead.
- If the cheap selector matches a model selector, keep the cheap policy.
- If gains occur only on deliberately incomplete controlled menus, limit the claim
  to that condition and seek natural cases before product expansion.
- If the experiment is underpowered or continuation labels are noisy, report
  inconclusive evidence and fix the measurement before training.

For superiority over all tested alternatives, define that set in advance and
support each required contrast. Average superiority does not imply every-baseline
superiority. The target is a bounded empirical claim, not universal dominance.

## How an open-source advantage could accumulate

| Asset | What makes it valuable over time | Evidence of progress |
| --- | --- | --- |
| Maintained executable probe packs | Applicability checks, reset quality, extraction, and fixes across dependency/environment changes | Valid execution and reuse on unfamiliar repositories |
| Comparative execution corpus | Alternatives at the same state, failures, abstentions, independent continuations, and uncertainty | Predictive value beyond transcripts or synthetic self-ratings |
| Portable integration and record format | Developers and multiple harnesses contribute/use the same artifacts | Repeated use and low adapter maintenance burden |
| Trusted evaluation and community maintenance | Reproducible releases, honest failures, and prompt repair of broken probe packs | External reproduction and sustained voluntary contributions |

These assets are copyable. An open-source advantage depends on continued
execution quality, maintenance, adoption, and useful releases. A file format,
MCP server, paper, or a particular decision model is not by itself an established
moat. Do not collect private histories or enable telemetry by default; opt-in
local exports can contribute permitted, reviewed artifacts later.

Measure sustained reuse only after there is a usable prototype. A small initial
developer cohort can test friction and unmet needs; it cannot establish broad
adoption. The research dataset and product feedback should remain distinguishable.

## Immediate next milestone

Produce a frozen claim matrix and a small set of naturally ambiguous cases, then
run the bounded-expansion comparison. Keep the existing rehearsal as an execution
test. Start with the simplest controller and coarse evidence validity policy.
Train only after measured labels and held-out predictive value justify it.
