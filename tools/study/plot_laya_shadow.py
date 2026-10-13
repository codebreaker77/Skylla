"""Descriptive CUDA shadow timing and probabilities; no repair accuracy figure."""

import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/judge-baseline"
RUN = CONFIG / "results/laya-gpu-001"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    analysis = json.loads((RUN / "analysis.json").read_text(encoding="utf-8"))
    records = json.loads((RUN / "decisions.json").read_text(encoding="utf-8"))
    labels = ["Tornado native close", "Xarray caught method", "Xarray top-level only"]
    groups = analysis["groups"]
    plt.rcParams.update({"svg.fonttype": "none", "svg.hashsalt": "skylla-laya-gpu-v1", "font.size": 9})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [0.9, 1.3]})
    for i, group in enumerate(groups):
        values = [r["recommendation"]["inference_seconds"]*1000 for r in records if r["state"]["state_id"] == group["state_id"]]
        axes[0].scatter([i]*len(values), values, color="#587dab", alpha=0.65, s=28)
        axes[0].plot([i-0.2, i+0.2], [group["median_inference_seconds"]*1000]*2, color="#1f3047", linewidth=2)
    axes[0].set(xticks=range(3), xticklabels=["Tornado", "Caught method", "Top-level"], ylabel="Classification-call milliseconds",
                title="GPU warm calls: median 223 ms", ylim=(0, 350))
    axes[0].spines[["top", "right"]].set_visible(False)
    axes[0].grid(axis="y", alpha=0.2)
    options = ["inspect_failure", "repair_setup", "propose_probe", "continue_investigation", "defer", "NONE"]
    data = np.array([[g["original_first_answer"]["probabilities"][o] for o in options] for g in groups])
    axes[1].imshow(data, vmin=0, vmax=1, cmap="Blues", aspect="auto")
    axes[1].set(yticks=range(3), yticklabels=labels, xticks=range(6),
                xticklabels=["Inspect\nfailure", "Repair\nsetup", "Propose\nprobe", "Continue", "Defer", "None"],
                title="First original-order probability vectors")
    for row in range(3):
        for column in range(6):
            axes[1].text(column, row, "%.2f" % data[row,column], ha="center", va="center")
    fig.suptitle("Local Laya on GTX 1050: timing and action probabilities", fontsize=13, fontweight="bold")
    fig.text(0.5, 0.025, "Three exposed states, four calls each. Model load 38.7 s. Two states recommend setup repair without a failed precondition.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.09, 1, 0.92))
    out = CONFIG / "figures"
    out.mkdir(exist_ok=True)
    assets = {}
    for extension in ("png", "svg"):
        path = out / ("laya-gpu-shadow." + extension)
        fig.savefig(path, dpi=180, facecolor="white", metadata={"Date": None} if extension == "svg" else None)
        if extension == "svg":
            path.write_bytes(("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n").encode())
        assets[path.name] = sha(path)
    plt.close(fig)
    with (out / "manifest.json").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"script_sha256": sha(Path(__file__)), "analysis_sha256": sha(RUN / "analysis.json"),
                                "decisions_sha256": sha(RUN / "decisions.json"), "matplotlib": matplotlib.__version__,
                                "assets_sha256": assets}, indent=2) + "\n")
    print("Rendered GPU shadow timing/probability PNG and SVG")


if __name__ == "__main__":
    main()
