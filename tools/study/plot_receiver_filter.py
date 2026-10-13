"""Render descriptive field-access counts from the recorded receiver replay."""

import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/receiver-filter"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summary_path = CONFIG / "results/run-001/summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    plt.rcParams.update({"svg.fonttype": "none", "svg.hashsalt": "skylla-receiver-v1"})
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    arms = ["unfiltered", "receiver_filtered"]
    available = [summary["field_accesses"][a]["total"] - summary["field_accesses"][a]["unavailable"] for a in arms]
    unavailable = [summary["field_accesses"][a]["unavailable"] for a in arms]
    ax.bar([0, 1], available, width=0.5, color="#168575", label="Available")
    ax.bar([0, 1], unavailable, bottom=available, width=0.5, color="#8493aa", label="Unavailable")
    for x, arm in enumerate(arms):
        ax.text(x, summary["field_accesses"][arm]["total"] + 20,
                str(summary["field_accesses"][arm]["total"]), ha="center")
    ax.set(xticks=[0, 1], xticklabels=["Unfiltered proposals", "Receiver filter"], ylabel="Recorded field accesses",
           ylim=(0, 1250), title="Same distinguishing observation; fewer unavailable accesses")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    fig.text(0.5, 0.03, "One exposed Tornado bug. Each arm: 12 processes, 6 distinguishing pairs. No repair comparison.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    out = CONFIG / "figures"
    out.mkdir(exist_ok=True)
    assets = {}
    for extension in ("png", "svg"):
        path = out / ("receiver-filter." + extension)
        fig.savefig(path, dpi=180, facecolor="white", metadata={"Date": None} if extension == "svg" else None)
        if extension == "svg":
            path.write_bytes(("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n").encode())
        assets[path.name] = sha(path)
    plt.close(fig)
    with (out / "manifest.json").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"source_sha256": sha(summary_path), "script_sha256": sha(Path(__file__)),
                                "matplotlib": matplotlib.__version__, "assets_sha256": assets}, indent=2) + "\n")
    print("Rendered receiver-filter PNG/SVG with source hashes")


if __name__ == "__main__":
    main()
