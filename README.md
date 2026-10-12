# Skylla

An open-source debugging experiment tool for developers and AI coding agents.

Skylla's proposed job is to help answer: **What should I run next to understand
this failure, and what did the result actually establish?**

Start from a failing command, compare plausible explanations, run a distinguishing
experiment, and keep the evidence attached to the exact code and environment that
produced it. Developers and agents should share the same workflow and artifacts.
The core will work without a required model provider or agent harness.

## Status

Research and design, started October 13, 2026. A local development rehearsal has
recorded 48 executions across three historical bugs, with pinned sources and
reproducible probe scripts. There is no installable developer CLI, published
paper, or measured agent-repair improvement yet.

The initial literature review points toward studying experiment selection under a
fixed debugging budget. We will test that direction before investing in a broad
platform or training a selector.

## Read the design

- [Next study and advantage plan](docs/NEXT_STUDY.md): the proposed expansion
  decision, bounded research schedule, fair comparisons, and assets to build.
- [Literature review](docs/LITERATURE.md): recent papers, evidence boundaries,
  adjacent systems, and remaining novelty questions.
- [Product direction](docs/DIRECTION.md): alternatives considered, recommended
  first workflow, model/harness independence, and proposed contracts.
- [Pilot protocol](docs/PILOT.md): reproducibility, baselines, measurements,
  execution costs, and decision gates.
- [Paper plan](docs/PAPER.md): research questions, required evidence, and artifacts.
- [Harness comparison](docs/HARNESSES.md): Claude Code, Cursor Debug Mode, Codex,
  OpenHands, and mini-swe-agent; documented capabilities and fair comparison arms.
- [Focused prior-art audit](docs/PRIOR_ART_AUDIT.md): overlap and unresolved checks.
- [Executed rehearsal](experiments/rehearsal/README.md): commands, artifacts,
  measured findings, and limitations.

## Principles

- Useful to an ordinary developer and to an existing coding agent.
- Local evidence collection and deterministic selection need no remote inference.
- Model choice, experiment generation, selection, and execution are separate.
- Predictions precede results; observations stay separate from interpretation.
- Correctness comes from independent checks, not a model's confidence.
- Unresolved investigations and negative research findings are legitimate outcomes.

Repository: [codebreaker77/Skylla](https://github.com/codebreaker77/Skylla).

## License

Skylla's original files are available under the [MIT license](LICENSE).
Third-party datasets, code, and papers retain their own licenses.
