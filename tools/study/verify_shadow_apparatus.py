"""Integrity checks for recorded local-stub integration and token-only audit."""

import hashlib
import json
from pathlib import Path

from judge_baseline import canonical

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/judge-baseline"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    integration = json.loads((CONFIG / "integration-v2.json").read_text(encoding="utf-8"))
    for record in integration["records"]:
        if record["script_sha256"] != sha(ROOT / "tools/study/judge_baseline.py"):
            raise ValueError("Integration adapter changed")
        if record["state_sha256"] != hashlib.sha256(canonical(record["state"]).encode()).hexdigest():
            raise ValueError("Recorded state hash mismatch")
    token_audit = json.loads((CONFIG / "token-audit.json").read_text(encoding="utf-8"))
    if token_audit["script_sha256"] != sha(ROOT / "tools/study/check_laya_tokens.py"):
        raise ValueError("Token audit implementation changed")
    if len(token_audit["records"]) != 3 or not all(r["markers"] == r["options"] for r in token_audit["records"]):
        raise ValueError("Token audit incomplete")
    provenance = json.loads((CONFIG / "offline-records.json").read_text(encoding="utf-8"))
    for source in provenance["provenance"]:
        if sha(ROOT / source["source"]) != source["source_sha256"]:
            raise ValueError("Changed example source")
    for record in provenance["records"]:
        state = json.loads((CONFIG / "states" / (record["state"]["state_id"] + ".json")).read_text(encoding="utf-8"))
        if state != record["state"]:
            raise ValueError("Example differs from original development export")
    print("Verified current local integration, token audit and development-state provenance; no model accuracy claims")


if __name__ == "__main__":
    main()
