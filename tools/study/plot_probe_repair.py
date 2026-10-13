"""Render descriptive figures from the recorded controlled study; no new experiments."""

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "experiments/probe-repair"
RUN = STUDY / "results/run-001"
OUT = STUDY / "figures"
ARMS = ["blind_search", "input_sweep", "normalize_then_sweep", "always_calibrate", "conditional_calibrate"]
LABELS = ["Blind search", "Input-first sweep", "Normalize then sweep", "Always calibrate", "Conditional calibration"]
COLORS = ["#8493aa", "#587dab", "#168575", "#d99045", "#b56b36"]
INK = "#1f3047"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(fig, name):
    for extension in ("png", "svg"):
        metadata = {"Date": None} if extension == "svg" else None
        fig.savefig(OUT / (name + "." + extension), dpi=180, facecolor="white", metadata=metadata)
    plt.close(fig)


def clean(axis):
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.spines["bottom"].set_color("#d8dfe8")
    axis.tick_params(axis="both", length=0)
    axis.set_axisbelow(True)
    axis.grid(axis="x", color="#e9edf2", linewidth=0.8)


def comparison(summary):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4), gridspec_kw={"wspace": 0.36})
    y = np.arange(len(ARMS))
    rows = [summary["arms"][arm] for arm in ARMS]
    recovery = [100 * row["verified_discriminators"] / row["positive_episodes"] for row in rows]
    axes[0].barh(y, recovery, color=COLORS, height=0.58)
    axes[0].set_yticks(y, LABELS)
    axes[0].invert_yaxis()
    axes[0].set_xlim(0, 112)
    axes[0].set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    axes[0].set_title("Verified probe recovery", loc="left", fontweight="bold", pad=18)
    axes[0].set_xlabel("Fault-present episodes (84 per policy)", labelpad=12)
    for index, (value, row) in enumerate(zip(recovery, rows)):
        axes[0].text(value + 1.7, index, str(row["verified_discriminators"]) + "/84", va="center", fontsize=10)
    regular = [(row["target_invocations"] - row["calibration_invocations"]) / row["completed_episodes"] for row in rows]
    controls = [row["calibration_invocations"] / row["completed_episodes"] for row in rows]
    axes[1].barh(y, regular, color=COLORS, height=0.58, label="Ordinary probes")
    control_y = [index for index, value in enumerate(controls) if value > 0]
    axes[1].barh(control_y, [controls[index] for index in control_y], left=[regular[index] for index in control_y], color="#ecd7bc", height=0.58, label="Calibration calls", hatch="//", edgecolor="#b27d43")
    axes[1].set_yticks(y, LABELS)
    axes[1].invert_yaxis()
    axes[1].set_xlim(0, 8.4)
    axes[1].set_xticks([0, 2, 4, 6, 8])
    axes[1].set_title("Mean target invocations", loc="left", fontweight="bold", pad=18)
    axes[1].set_xlabel("All episodes (168 per policy)\nEight-call budget; evaluator replays excluded", labelpad=12, fontsize=9)
    for index, row in enumerate(rows):
        value = row["mean_invocations_completed"]
        axes[1].text(value + 0.12, index, f"{value:.2f}", va="center", fontsize=10)
    axes[1].legend(loc="lower left", bbox_to_anchor=(0, -0.35), ncol=2, frameon=False, fontsize=9)
    for axis in axes:
        clean(axis)
    fig.suptitle("Same recovery, additional calibration cost", x=0.04, y=0.98, ha="left", fontsize=19, fontweight="bold")
    fig.text(0.04, 0.02, "Controlled development study • 4 related fault families • 3 menu orderings • No agent repairs or independent-bug inference", fontsize=9, color="#5a697e")
    fig.subplots_adjust(left=0.17, right=0.96, top=0.79, bottom=0.27)
    save(fig, "recovery-and-cost")


def conditions(summary):
    keys = ["adequate", "wrong_input", "wrong_observer", "wrong_source", "input_and_observer", "source_and_observer", "masked_result"]
    labels = ["Adequate", "Wrong\ninput", "Wrong\nobserver", "Wrong\nsource", "Input +\nobserver", "Source +\nobserver", "Masked\nresult"]
    values = np.array([[summary["positive_results_by_condition"][arm][key]["verified"] for key in keys] for arm in ARMS])
    fig, axis = plt.subplots(figsize=(11.8, 5.7))
    axis.imshow(values, cmap="YlGnBu", vmin=0, vmax=12, aspect="auto")
    axis.set_xticks(range(len(keys)), labels)
    axis.set_yticks(range(len(ARMS)), LABELS)
    axis.tick_params(length=0, pad=10)
    for row in range(len(ARMS)):
        for col in range(len(keys)):
            value = values[row, col]
            axis.text(col, row, f"{value}/12", ha="center", va="center", color="white" if value >= 8 else INK, fontweight="bold", fontsize=12)
    axis.set_xticks(np.arange(-0.5, len(keys), 1), minor=True)
    axis.set_yticks(np.arange(-0.5, len(ARMS), 1), minor=True)
    axis.grid(which="minor", color="white", linewidth=2)
    axis.tick_params(which="minor", bottom=False, left=False)
    for spine in axis.spines.values():
        spine.set_visible(False)
    fig.suptitle("Probe recovery by initial condition", x=0.04, y=0.97, ha="left", fontsize=19, fontweight="bold")
    fig.text(0.04, 0.88, "Verified fault-present recovery: 4 families × 3 orderings = 12 episodes in each cell", color="#5a697e", fontsize=10)
    fig.text(0.04, 0.045, "Every policy misses the masked-result cases: no supplied action removes the masking wrapper.\nCounts describe constructed fixtures; related families and permutations are not independent bug samples.", fontsize=9, color="#5a697e", linespacing=1.6)
    fig.subplots_adjust(left=0.23, right=0.97, top=0.82, bottom=0.21)
    save(fig, "recovery-by-condition")


def workflow():
    fig, axis = plt.subplots(figsize=(12.8, 6.5))
    axis.set_xlim(0, 13)
    axis.set_ylim(0, 7)
    axis.axis("off")

    def box(x, y, width, title, body, color="#edf3f9"):
        axis.add_patch(FancyBboxPatch((x, y), width, 1.35, boxstyle="round,pad=0.06,rounding_size=0.1", facecolor=color, edgecolor="#c8d3df"))
        axis.text(x + width / 2, y + 0.98, title, ha="center", va="center", fontsize=11, fontweight="bold")
        axis.text(x + width / 2, y + 0.45, body, ha="center", va="center", fontsize=9, linespacing=1.5)

    def arrow(x1, x2, y):
        axis.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="-|>", mutation_scale=15, linewidth=1.4, color="#687b91"))

    axis.text(0.2, 6.55, "How the experiment works", fontsize=19, fontweight="bold")
    boxes = [(0.2, "Controlled cases", "4 fault families\n7 probe conditions\nFault present / absent"),
             (3.45, "Same public menu", "4 inputs × 2 observers\n× 2 source choices\n3 shared orderings"),
             (6.7, "Five policies", "8 target-call budget\nControl triplet costs 3\n840 total episodes"),
             (9.95, "Offline evaluation", "Reference replay after\npolicy completion\nVerified discriminator")]
    for x, title, body in boxes:
        box(x, 4.35, 2.8, title, body)
    for x in (3.0, 6.25, 9.5):
        arrow(x, x + 0.4, 5.02)
    axis.text(0.2, 3.6, "Why the calibration trap passes", fontsize=15, fontweight="bold")
    for x, title, body, color in [
        (0.2, "Real program", "Fault affects\nits returned value", "#edf3f9"),
        (3.45, "Masking wrapper", "Substitutes the\nexpected value", "#fff0df"),
        (6.7, "Positive control", "Overwrites result\nwith a known sentinel", "#fff0df"),
        (9.95, "Collector", "Sees the sentinel\nControl passes", "#e6f3ee")]:
        box(x, 1.8, 2.8, title, body, color)
    for x in (3.0, 6.25, 9.5):
        arrow(x, x + 0.4, 2.47)
    axis.text(0.2, 1.15, "The control verifies sensitivity at the collector; it does not establish that the original fault reaches that collector.", fontsize=10, color="#875322")
    axis.text(0.2, 0.35, "Schematic of the frozen v1 study • Supplied menus and explicit specifications • No model-driven discovery or production repair", fontsize=9, color="#5a697e")
    fig.subplots_adjust(left=0.02, right=0.99, bottom=0.02, top=0.99)
    save(fig, "workflow-and-control-blind-spot")


if __name__ == "__main__":
    summary_path = RUN / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if digest(RUN / "episodes.jsonl") != summary["episodes_sha256"]:
        raise ValueError("Episode source hash changed")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
                         "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                         "svg.fonttype": "none", "svg.hashsalt": "skylla-probe-repair-v1"})
    OUT.mkdir(parents=True, exist_ok=True)
    comparison(summary)
    conditions(summary)
    workflow()
    manifest = {"purpose": "Descriptive figures from run-001; no new target executions",
                "source_summary_sha256": digest(summary_path), "source_episodes_sha256": summary["episodes_sha256"],
                "plot_script_sha256": digest(Path(__file__)), "matplotlib": matplotlib.__version__, "numpy": np.__version__,
                "figures": {path.name: digest(path) for path in sorted(OUT.iterdir()) if path.suffix in (".png", ".svg")}}
    with (OUT / "manifest.json").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, indent=2) + "\n")
    print("Rendered three figures as PNG and SVG in", OUT)
