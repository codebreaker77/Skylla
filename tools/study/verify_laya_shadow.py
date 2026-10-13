"""Verify frozen CUDA shadow execution and its post-run analysis integrity."""

import json
from pathlib import Path

from analyze_laya_shadow import ROOT, RUN, sha
from judge_baseline import canonical
import hashlib


def main():
    protocol = json.loads((RUN / "protocol.json").read_text(encoding="utf-8"))
    summary = json.loads((RUN / "summary.json").read_text(encoding="utf-8"))
    for path, expected in protocol["implementation_sha256"].items():
        if sha(ROOT / path) != expected:
            raise ValueError("Changed frozen implementation: " + path)
    config = ROOT / "experiments/judge-baseline"
    if sha(config / "METHODOLOGY.md") != protocol["method_sha256"] or sha(config / "laya-checkpoint.json") != protocol["checkpoint_sha256"]:
        raise ValueError("Changed frozen method/checkpoint identity")
    for path, expected in protocol["state_files_sha256"].items():
        if sha(config / "states" / path) != expected:
            raise ValueError("Changed state export")
    for key, path in (("protocol_sha256", "protocol.json"), ("decisions_sha256", "decisions.json"), ("warmup_sha256", "warmup.json")):
        if summary[key] != sha(RUN / path):
            raise ValueError("Changed run artifact")
    records = json.loads((RUN / "decisions.json").read_text(encoding="utf-8"))
    identities = {(r["state"]["state_id"], r["order_name"], r["repetition"]) for r in records}
    expected = {(Path(s).stem, order, repetition) for s in protocol["state_files_sha256"]
                for order in protocol["orders"] for repetition in range(protocol["repetitions"])}
    if identities != expected or len(records) != len(expected):
        raise ValueError("Incomplete or duplicate shadow decisions")
    for r in records:
        if r["state_sha256"] != hashlib.sha256(canonical(r["state"]).encode()).hexdigest():
            raise ValueError("State hash mismatch")
        if r["option_order"] != protocol["orders"][r["order_name"]]:
            raise ValueError("Order mismatch")
        if r["status"] == "completed":
            if r["recommendation"]["hardware"]["device"] != "cuda:0" or r["recommendation"]["hardware"]["cpu_inference_fallback"] is not False:
                raise ValueError("Unexpected model device/fallback configuration")
    analysis = json.loads((RUN / "analysis.json").read_text(encoding="utf-8"))
    for path, expected_hash in analysis["source_sha256"].items():
        if sha(RUN / path) != expected_hash:
            raise ValueError("Changed analysis source")
    if analysis["script_sha256"] != sha(ROOT / "tools/study/analyze_laya_shadow.py"):
        raise ValueError("Changed analysis implementation")
    count = sum(r["status"] == "completed" and r["recommendation"]["action"] == "repair_setup"
                and "failed" not in r["state"]["evidence"]["preconditions"] for r in records)
    if count != analysis["declared_setup_contract_violations"]:
        raise ValueError("Contract review count mismatch")
    print("Verified 12 frozen CUDA shadow decisions and descriptive contract analysis; accuracy/generalization unestablished")


if __name__ == "__main__":
    main()
