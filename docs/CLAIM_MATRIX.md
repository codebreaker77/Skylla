# Claims and evidence boundaries

October 13, 2026. Skylla's current contribution is an inspectable prototype and
development artifacts. A defensible advantage remains a hypothesis.

The [DeepEval/Jev audit](DEEPEVAL_JEV_AUDIT.md) establishes direct product overlap
with generic System-1 judgments, custom classifiers, trace evaluation and coding-
agent iteration. None of these is a Skylla novelty claim. A DeepEval/Jev-assisted
baseline must be configured before future matched repair comparisons.

The [latest ideation memo](IDEATION.md) adds closer prior art and proposes checking
and repairing experiments before expanding explanations. It also reproduces a
hypothesis-alias sensitivity in the current pair-count heuristic. Neither finding
establishes novelty or measured repair benefit.

A [controlled follow-up](../experiments/probe-repair/REPORT.md) now compares five
deterministic probe-repair heuristics. Calibration adds no recovery over simple
normalization on its supplied menus and costs more target calls. This is evidence
against that added step for the tested fixtures, not a repair-agent result.

A [public trajectory audit](../experiments/trajectory-audit/REPORT.md) now reviews
early runtime events from 15 genuine agent traces. It documents setup obstacles,
zero-exit exceptions, and native observation/repair behavior. Missing internal
observers and causal usefulness remain unestablished without independent review
or replay; these labels cannot justify a discovery-performance claim.

| Proposed claim | Present evidence | Evidence still required |
| --- | --- | --- |
| Provider-independent local decisions | Python/JSON core, no inference dependency, CLI smoke check | Multiple real harness integrations |
| Recognizes some inadequate menus | Explicit control tags and qualitative predictions; unit tests | False/missed expansion on independently labeled unseen tasks |
| Preserves validity after changes | Rejects mismatched declared state IDs | Full environment binding and real edit/configuration interventions |
| More efficient debugging | None; pair-count/cost is a heuristic | Matched-budget executed policies, generation overhead, useful evidence |
| Better verified agent repair | None | Same model/harness, strong native baseline, independent target/regression checks |
| Novel algorithm | Not established | Full prior-art/artifact audit and a precise technical distinction |
| Sustainable advantage | Initial reproducible scripts and development observations | Maintained packs, cross-harness adoption, repeated trustworthy execution data |

## Prior art narrows the paper

AutoSD already studies scientific debugging; Debug2Fix already uses debugger
subagents; Cursor Debug Mode already combines hypotheses, instrumentation, and
runtime observations. See the [harness comparison](HARNESSES.md) and
[prior-art audit](PRIOR_ART_AUDIT.md). Skylla cannot claim that ordinary harnesses
lack debugging tool loops or that recording hypotheses is new.

Follow-up inspection went beyond abstracts for these three papers, but did not
reproduce their code or exhaustively audit their artifacts:

- [PROBE, full v2](https://arxiv.org/html/2605.08717v2), sections 3.4 and 4.1:
  telemetry-guided recovery includes a guidance gate and a bounded additional
  repair attempt. The software-repair setup uses mini-swe-agent, separate subject
  and feedback models, and initially failed cases. Feedback adds overhead, so
  Skylla must count generation/feedback costs. Live menu expansion is a narrower
  research question, not evidence of superiority over recovery guidance.
- [PACMI, full v1](https://arxiv.org/html/2610.05732v1), sections 5.1–5.5:
  the reported benchmark supplies dependency topology. Propagation correctness
  under that topology does not by itself establish a causal repair benefit in
  repositories. Invalidation is prior art; compare coarse invalidation before
  spending effort on learned dependency graphs.
- [Presentation, Not Mechanism, full v1](https://arxiv.org/html/2607.16019v1),
  section 4.1 and rendering-control appendix: detailed-ledger results depend
  heavily on presentation controls. Match observation rendering and prompts
  across arms, and include a coarse-state baseline. These findings do not
  directly predict Skylla's repair performance.

[Using Hypotheses](https://arxiv.org/abs/2005.13652) supports studying how
developers formulate explanations; it does not establish that this controller
helps. [Fixed-Horizon Active Hypothesis Testing](https://arxiv.org/abs/1911.06912)
studies adaptive experiments under mathematical assumptions. Skylla's fallible
qualitative predictions do not satisfy a known probabilistic observation model,
so no theoretical optimality guarantee transfers.

The possible paper is a task and evaluation contribution: distinguish candidate
availability from selection, measure when expansion helps under realistic total
budgets, and release comparable artifacts. If conditional expansion cannot beat
blind expansion or the native workflow, report that outcome and revise the
product direction. A named combination of familiar components is insufficient
to claim novelty or a moat.
