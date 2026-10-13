"""Experimental recommendation checks; never execute or replace model actions."""

import argparse
import hashlib
import json
from pathlib import Path

from judge_baseline import OPTIONS, validate


def check(state, action):
    validate(state)
    if state["remaining_seconds"] == 0:
        return {"disposition": "defer", "admissible_action": "defer", "reason": "budget_exhausted"}
    if action is None:
        return {"disposition": "defer", "admissible_action": None, "reason": "model_abstained"}
    if not isinstance(action, str) or action not in OPTIONS:
        return {"disposition": "rejected", "admissible_action": None, "reason": "unknown_action"}
    if action == "repair_setup" and "failed" not in state["evidence"]["preconditions"]:
        return {"disposition": "rejected", "admissible_action": None,
                "reason": "no_explicit_failed_precondition"}
    return {"disposition": "allowed", "admissible_action": action,
            "reason": "passes_minimal_contract_checks"}


def replay(source, output):
    if output.exists():
        raise ValueError("Output exists; preserve earlier artifacts")
    records = json.loads(source.read_text(encoding="utf-8"))
    rows = []
    for index, record in enumerate(records):
        action = (record.get("recommendation") or {}).get("action")
        decision = (check(record["state"], action) if record["status"] in ("completed", "budget_exhausted")
                    else {"disposition": "rejected", "admissible_action": None, "reason": "backend_not_completed"})
        rows.append({"record_index": index, "state_id": record["state"]["state_id"],
                     "raw_action": action, **decision})
    result = {"schema_version": 1,
              "scope": "Post-hoc minimal contract replay; no inference, new cases, action execution or utility evaluation",
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "records": rows,
              "counts": {name: sum(r["disposition"] == name for r in rows)
                         for name in ("allowed", "rejected", "defer")},
              "limitation": "Allowed means only these checks passed. Evidence may be incomplete or stale; deadline and execution costs require harness enforcement."}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    print(json.dumps(result["counts"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    replay(args.source, args.output)
