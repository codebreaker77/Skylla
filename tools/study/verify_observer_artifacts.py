"""Verify frozen replay, post-run analysis and plotted artifact integrity."""

import json
from pathlib import Path
import xml.etree.ElementTree as ET

from observer_study import CONFIG, ROOT, sha, verify


def main():
    verify("run-001")
    run = CONFIG / "results/run-001"
    analysis = json.loads((run / "analysis.json").read_text(encoding="utf-8"))
    for key, path in (("processes_sha256", run / "processes.json"),
                      ("summary_sha256", run / "summary.json"),
                      ("script_sha256", ROOT / "tools/study/analyze_observer_study.py")):
        if analysis[key] != sha(path):
            raise ValueError("Analysis hash mismatch: " + key)
    records = json.loads((run / "processes.json").read_text(encoding="utf-8"))
    identities = [(r["case"], r["variant"], r["kind"], r.get("arm"), r.get("cycles"),
                   r.get("repetition"), r.get("target")) for r in records]
    if len(set(identities)) != len(identities):
        raise ValueError("Duplicate execution identities")
    for contrast in analysis["contrasts"]:
        pairs = [p for p in analysis["pairs"] if p["case"] == contrast["case"] and p["arm"] == contrast["arm"]]
        if (contrast["pairs"] != len(pairs) or contrast["comparable_pairs"] != sum(p["comparable"] for p in pairs)
                or contrast["different_pairs"] != sum(p["different"] is True for p in pairs)):
            raise ValueError("Contrast counts disagree")
    proposals = json.loads((CONFIG / "proposals.json").read_text(encoding="utf-8"))["candidates"]
    if [c["candidate"] for c in analysis["candidates"]] != proposals:
        raise ValueError("Analysis changed candidate set")
    figures = CONFIG / "figures"
    manifest = json.loads((figures / "manifest.json").read_text(encoding="utf-8"))
    if manifest["script_sha256"] != sha(ROOT / "tools/study/plot_observer_study.py"):
        raise ValueError("Changed figure script")
    for relative, digest in manifest["source_sha256"].items():
        if sha(CONFIG / relative) != digest:
            raise ValueError("Changed figure source")
    for relative, digest in manifest["assets_sha256"].items():
        if sha(figures / relative) != digest:
            raise ValueError("Changed figure asset")
        if relative.endswith(".svg"):
            ET.parse(figures / relative)
    print("Verified analysis counts, unique process identities and PNG/SVG hashes; no independent semantic review")


if __name__ == "__main__":
    main()
