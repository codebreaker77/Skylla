# Controlled study figures

Descriptive figures generated from `results/run-001/summary.json`. The study uses
four related constructed fault families and three menu permutations. Episodes
are not independent natural bugs, and recovered probes are not agent repairs.

| Figure | PNG preview | Editable vector |
| --- | --- | --- |
| Recovery and mean target-call cost | [PNG](recovery-and-cost.png) | [SVG](recovery-and-cost.svg) |
| Recovery by initial probe condition | [PNG](recovery-by-condition.png) | [SVG](recovery-by-condition.svg) |
| Study workflow and calibration blind spot | [PNG](workflow-and-control-blind-spot.png) | [SVG](workflow-and-control-blind-spot.svg) |

Recovery uses 84 fault-present episodes per policy. Cost uses all 168 episodes
per policy and includes calibration calls, with an eight-call budget. Offline
reference replay is excluded. Each heatmap cell contains 12 fault-present
episodes. These constructed cases and permutations do not provide independent
natural-bug samples, so the figures have no inferential uncertainty bars.

Regenerate from the repository root:

```sh
python -m pip install -r experiments/probe-repair/figures/requirements.txt
python tools/study/plot_probe_repair.py
```

Generation checks the episode-source hash and records source, script, PNG, and
SVG hashes in [manifest.json](manifest.json), along with library versions.
SVG text remains selectable. PNGs use 180 DPI. Exact bytes may differ across
plotting environments; the manifest identifies the committed artifacts.
Regenerating figures does not rerun experiments or change the frozen method.
