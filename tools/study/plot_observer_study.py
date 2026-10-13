"""Descriptive figures for an exposed two-case observer apparatus study."""

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/observer-discovery"
RUN = CONFIG / "results/run-001"
OUT = CONFIG / "figures"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    records = json.loads((RUN / "processes.json").read_text(encoding="utf-8"))
    analysis = json.loads((RUN / "analysis.json").read_text(encoding="utf-8"))
    cid = next(c["candidate"]["id"] for c in analysis["candidates"] if c["different_pairs"] > 0)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.fonttype": "none", "svg.hashsalt": "skylla-observer-v1"})
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5), gridspec_kw={"width_ratios": [1.1, 1]})
    for variant, label, color in (("buggy", "Buggy source", "#b56b36"), ("fixed", "Reference source", "#168575")):
        points = {}
        for record in records:
            if record["kind"] == "probe" and record["case"] == "tornado-6" and record["arm"] == "source_containers" and record["variant"] == variant:
                obs = record["payload"]["observation"]
                points.setdefault(record["cycles"], []).append(obs["after"][cid]["length"] - obs["before"][cid]["length"])
        for values in points.values():
            if len(set(values)) != 1:
                raise ValueError("Repetitions differ; figure must show variation")
        x = sorted(points)
        axes[0].plot(x, [points[k][0] for k in x], "o-", label=label, color=color, linewidth=2)
    axes[0].set(title="Tornado: closed loops can stay registered", xlabel="Loops closed per fresh invocation",
                ylabel="Registry length change after close", xticks=[1, 10], yticks=[0, 1, 5, 10])
    axes[0].legend(frameon=False)
    axes[0].text(0.04, 0.93, "Native is_closed(): true on both versions", transform=axes[0].transAxes,
                 va="top", fontsize=9)
    counts = [sum(c["different_pairs"] > 0 for c in analysis["candidates"]),
              sum(c["comparable_pairs"] > 0 and c["different_pairs"] == 0 for c in analysis["candidates"]),
              sum(c["comparable_pairs"] == 0 for c in analysis["candidates"])]
    bars = axes[1].bar(["Different", "Unchanged", "Unavailable"], counts,
                       color=["#168575", "#587dab", "#8493aa"], width=0.6)
    axes[1].set(title="Eight AST proposals: one distinguishes", ylabel="Proposed fields", ylim=(0, 5), yticks=range(6))
    for bar, count in zip(bars, counts):
        axes[1].text(bar.get_x() + bar.get_width() / 2, count + 0.12, str(count), ha="center")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#e5e9ef", linewidth=0.7)
        ax.set_axisbelow(True)
    fig.suptitle("Source-proposed observations on an exposed development bug", fontsize=14, fontweight="bold")
    fig.text(0.5, 0.02, "Three identical repetitions per input/version. Reference contrast; no agent repair or learned routing evaluated.",
             ha="center", fontsize=9, color="#475569")
    fig.tight_layout(rect=(0, 0.08, 1, 0.93))
    OUT.mkdir(parents=True, exist_ok=True)
    assets = {}
    for extension in ("png", "svg"):
        path = OUT / ("source-observations." + extension)
        fig.savefig(path, dpi=180, facecolor="white", metadata={"Date": None} if extension == "svg" else None)
        if extension == "svg":
            path.write_bytes(("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n").encode("utf-8"))
        assets[path.name] = sha(path)
    plt.close(fig)
    manifest = {"schema_version": 1, "script_sha256": sha(Path(__file__)),
                "source_sha256": {"results/run-001/processes.json": sha(RUN / "processes.json"),
                                  "results/run-001/analysis.json": sha(RUN / "analysis.json")},
                "versions": {"matplotlib": matplotlib.__version__, "numpy": numpy.__version__},
                "assets_sha256": assets}
    with (OUT / "manifest.json").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, indent=2) + "\n")
    print("Rendered descriptive PNG/SVG and bound hashes to source records")


if __name__ == "__main__":
    main()
