# Literature review: choosing debugging experiments

Reviewed October 13, 2026. This is an exploratory review, not a systematic survey
or a claim of novelty. Published findings belong to the cited authors; Skylla has
not reproduced them.

## Search and reading scope

Searched for scientific debugging, interactive debugger agents, experiment
selection, information gain, runtime diagnosis, and recent repair benchmarks.
Prioritized 2025-2026 work and retained older systems that constrain novelty.
Sources are arXiv, proceedings, publisher pages, and official project repositories.

Representative queries:

- `LLM scientific debugging experiment hypothesis selection 2025 2026 paper`
- `debugging agent active diagnosis information gain experiments paper 2025 2026`
- `"Debug2Fix" arxiv`
- `site:arxiv.org debugging agent 2026 benchmark runtime hypothesis`
- `site:arxiv.org debugging "counterfactual" experiments agent 2025 2026`
- `site:arxiv.org debugging "value of information" agents`

Selected full-text sections support initial design choices, not a complete methods
audit. Abstract-only entries need deeper reading before becoming experimental
baselines. An arXiv record does not establish absence of subsequent publication.

## Recent papers

### Debug2Fix — February 20, 2026

[Debug2Fix: Supercharging Coding Agents with Interactive Debugging Capabilities](https://arxiv.org/abs/2602.18571),
Spandan Garg and Yufan Huang. Preprint record. Architecture, evaluation, results,
and ablations inspected in [v1](https://arxiv.org/html/2602.18571v1).

Uses a debugger subagent for repository repair in Java and Python. Its Java
evaluation raises GPT-5 pass rate from 60.2% to 73.1%: 12.9 percentage points,
about 21.4% relative. Tool adoption and Python gains vary by model. Direct debugger
exposure and debugging-before-editing restrictions are ablated.

Skylla implication: compare equivalent runtime access and count all overhead.
Experiment selection must earn value beyond tool packaging or extra inference.

### DDBench — August 14, 2026

[Evaluating Agentic Code Repair Capabilities in Distributed Systems](https://arxiv.org/abs/2608.14863),
Yibo Yan et al. Preprint record. Dataset, context channel, evaluation, and oracle
construction inspected in [v1](https://arxiv.org/html/2608.14863v1).

Introduces 60 historical bugs across 13 distributed systems. Compares symptom-only
and context-augmented conditions; reports an aggregate 18.1 percentage-point
pass-rate lift and cases where faithful context misleads. Supports tool-produced
context bundles.

Skylla implication: attractive external validation target later. Acquiring context
through live probes has costs that supplying curated context does not measure.
Distributed execution is a costly first scope.

### ReplayLens — September 28, 2026

[ReplayLens: Auditing Agents' Use of Outcomes](https://arxiv.org/abs/2609.34177),
Dong Xu et al. Preprint record. Abstract inspected;
[full text](https://arxiv.org/html/2609.34177v1) accessed, detailed audit pending.

Audits action/outcome attachment, record position, and naming in logged experience.
Includes sequential experiment planning and a debugging case with hidden tests.

Skylla implication: test evidence ordering and attachment independently. Its
debugging case needs a closer overlap audit before defining our contribution.

### Precise Debugging Benchmark — April 19, 2026

[Precise Debugging Benchmark: Is Your Model Debugging or Regenerating?](https://arxiv.org/abs/2604.17338),
Wang Bill Zhu et al. Preprint record. Abstract and official summary read.

Constructs atomic and multi-bug programs; measures edit precision and bug recall.
Reports test-pass rates above 76% alongside precision below 45% for cited models.

Skylla implication: passing tests misses unnecessary edits. Evaluate patch scope,
but do not treat historical patches as the only valid minimal solution.

### AgentRx — February 2, 2026

[AgentRx: Diagnosing AI Agent Failures from Execution Trajectories](https://arxiv.org/abs/2602.02475),
Shraddha Barke et al. Preprint record. Abstract read.

Uses synthesized constraints, stepwise checks, and an evidence-backed judge to
diagnose failed trajectories; releases 115 annotated failed runs.

Skylla implication: evidence-backed diagnosis is adjacent prior art. Our initial
target is prospective program debugging, rather than retrospective agent failure
localization.

### VeriTrace — August 3, 2026

[VeriTrace: Human-Like Temporal Exploration Completes Agentic Action Space](https://arxiv.org/abs/2608.02878),
Yu-Tung Liu and Cunxi Yu. Preprint record. Abstract read.

Expands hardware debugging actions through signal selection, time-window selection,
and waveform inspection. Reports 100% Pass@1 on VerilogEval-V2.

Skylla implication: selection cannot compensate for an inadequate candidate set.
Separate useful-probe availability from selection quality. Hardware results do not
establish general software debugging performance.

### Hypothesis generation and updating — May 7, 2026

[Hypothesis generation and updating in large language models](https://arxiv.org/abs/2605.05851),
Hua-Dong Xiong. Preprint record. Abstract read.

Studies inference in a number game; finds differences between evaluating and
generating hypotheses and limits in extrapolation.

Skylla implication: generation and selection are different capabilities. This is
conceptual motivation, not debugging evidence. Test absent true explanations.

### POPPER — ICML 2025

[Automated Hypothesis Validation with Agentic Sequential Falsifications](https://proceedings.mlr.press/v267/huang25n.html),
Kexin Huang et al. Published proceedings paper. Abstract and metadata read.

Designs and executes falsification experiments with sequential testing for Type-I
error control.

Skylla implication: agentic falsification is prior art. Its statistical guarantees
cannot be transferred to model-written debugging predictions without satisfying
the underlying assumptions.

### Scientific mutation testing — March 11, 2025

[Mutation Testing via Iterative Large Language Model-Driven Scientific Debugging](https://arxiv.org/abs/2503.08182),
Philipp Straubinger et al. [ICSTW 2025 publication](https://doi.org/10.1109/ICSTW64639.2025.10962485).
Abstract and publisher-indexed method excerpts read.

Uses hypotheses and experiments to generate tests distinguishing programs from
mutants; compares direct prompting, iterative prompting, and Pynguin.

Skylla implication: useful controlled validation of probe contracts. Mutant
killing does not substitute for real-bug repair outcomes.

### DSDBench — EMNLP, November 2025

[Why Stop at One Error? Benchmarking LLMs as Data Science Code Debuggers for Multi-Hop and Multi-Bug Errors](https://aclanthology.org/2025.emnlp-main.878/),
Zhiyu Yang et al. Published proceedings paper. Abstract and metadata read.

Provides 1,117 annotated samples with synthesized multi-hop and multi-bug
data-science debugging tasks.

Skylla implication: support interacting causes. Keep snippet-based and
repository-based scores separate.

### SWE-bench-Live — May 29, 2025

[SWE-bench Goes Live!](https://arxiv.org/abs/2505.23419), Linghao Zhang et al.
Preprint record. Abstract read.

Describes a live-updatable issue-resolution benchmark with an initial release of
1,319 tasks across 93 repositories and task-specific Docker images.

Skylla implication: possible recent-bug substrate. Freeze task snapshots and
audit leakage; recency alone does not prove absence of memorization.

## Foundational overlap

### AutoSD — December 18, 2024; EMSE volume 2025

[Explainable automated debugging via large language model-driven scientific debugging](https://link.springer.com/article/10.1007/s10664-024-10594-x),
Sungmin Kang, Bei Chen, Shin Yoo, and Jian-Guang Lou. Published journal article.
Workflow, conclusion, human-study summary, and artifact availability inspected.

Generates hypotheses, interacts with buggy programs through a debugger, reaches
conclusions, and produces patches and explanations. Includes a 20-participant
human study. [Artifacts](https://doi.org/10.6084/m9.figshare.27861528.v3).

Skylla implication: the scientific debugging loop is prior art. Compare against
a scientific-debugging prompt and notebook before claiming algorithmic benefit.

### ChatDBG — March 25, 2024

[ChatDBG: An AI-Powered Debugging Assistant](https://arxiv.org/abs/2403.16354),
Kyla Levin et al. Preprint record. Abstract read.

Enables natural-language interaction with debuggers, allowing runtime inspection
and control before returning findings to a developer.

Skylla implication: conversational debugger assistance already serves developers.
We need value in experiment comparison, reproducibility, or verified outcomes.

## Adjacent lead and execution substrate

[Value of Information: A Framework for Human-Agent Communication](https://arxiv.org/abs/2601.06407),
Yijiang River Dong et al., January 10, 2026. Preprint record; abstract read.
Balances clarification benefit against user effort. Adjacent motivation for
cost-aware decisions, not evidence of transfer to executable debugging probes.

[BugsInPy](https://github.com/soarsmu/BugsInPy) offers real Python bugs, buggy/fixed
checkouts, test commands, and Docker setup. Official README inspected. Individual
project licenses and old dependencies need case-level checks. No environment has
been built and no bug instance has been selected.

## Synthesis and remaining novelty audit

Runtime information, hypothesis testing, evidence logs, and debugger interfaces
have clear precedents. They are components to use, not new contributions to claim.

Our proposed gap is comparing multiple feasible probes from the same state using
downstream repair outcomes and full evidence-acquisition costs. This is an
inference from the inspected sources, not proof that nobody has done it.

Before a novelty claim, audit full methods/artifacts of Debug2Fix, AutoSD,
ReplayLens, POPPER, and ChatDBG. Search backward/forward citations and active
diagnosis, delta debugging, cost-aware test selection, and repair planning.
Specifically look for executed alternatives with matched repair continuations.
If an existing method or dataset covers this, reuse it and narrow our claim.
