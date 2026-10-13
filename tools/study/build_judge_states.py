"""Export three exposed development states, excluding evaluator/reference outputs."""

import hashlib
import json
from pathlib import Path

from judge_baseline import evaluate, canonical

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/judge-baseline"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")


def main():
    if (CONFIG / "states").exists() or (CONFIG / "offline-records.json").exists():
        raise ValueError("Development states already exported")
    xarray_path = ROOT / "experiments/evidence-pilot/results/run-002/observations.json"
    xarray = json.loads(xarray_path.read_text(encoding="utf-8"))
    tornado_path = ROOT / "experiments/observer-discovery/results/run-001/processes.json"
    tornado = json.loads(tornado_path.read_text(encoding="utf-8"))
    records, provenance = [], []
    for name, mode in (("xarray-top-level", "top_level_only"), ("xarray-caught-method", "caught_method")):
        raw = next(r for r in xarray if r["mode"] == mode and r["repetition"] == 0)
        observation = {k: v for k, v in raw["observation"].items() if k != "origin"}
        state = {"schema_version": 1, "state_id": name,
                 "issue": "Dataset.merge should accept a named DataArray, as the top-level merge function does.",
                 "remaining_seconds": 30, "evidence": {"preconditions": ["passed"],
                 "observations": [observation], "requirement_exercised": observation["method_exercised"]}}
        write(CONFIG / "states" / (name + ".json"), state)
        records.append(evaluate(state, "rules"))
        provenance.append({"state_id": name, "source": str(xarray_path.relative_to(ROOT)).replace("\\", "/"),
                           "source_sha256": hashlib.sha256(xarray_path.read_bytes()).hexdigest(),
                           "selection": {"mode": mode, "repetition": 0}})
    raw = next(r for r in tornado if r["case"] == "tornado-6" and r["variant"] == "buggy"
               and r["kind"] == "probe" and r["arm"] == "normalize" and r["cycles"] == 10 and r["repetition"] == 0)
    state = {"schema_version": 1, "state_id": "tornado-native-close",
             "issue": "Repeated creation and closure of IOLoops leaks resources.", "remaining_seconds": 30,
             "evidence": {"preconditions": ["passed"], "observations": [raw["payload"]["observation"]],
                          "requirement_exercised": None}}
    write(CONFIG / "states/tornado-native-close.json", state)
    records.append(evaluate(state, "rules"))
    provenance.append({"state_id": state["state_id"], "source": str(tornado_path.relative_to(ROOT)).replace("\\", "/"),
                       "source_sha256": hashlib.sha256(tornado_path.read_bytes()).hexdigest(),
                       "selection": {"case": "tornado-6", "variant": "buggy", "kind": "probe",
                                     "arm": "normalize", "cycles": 10, "repetition": 0}})
    write(CONFIG / "offline-records.json", {"scope": "Three exposed development examples; rules outputs only",
                                          "provenance": provenance, "records": records,
                                          "state_hashes": {r["state"]["state_id"]: r["state_sha256"] for r in records},
                                          "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    print("Exported three solver-visible development states and offline rules records")


if __name__ == "__main__":
    main()
