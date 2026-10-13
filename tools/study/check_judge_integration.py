"""Exercise real pinned DeepEval using a local stub; not a Jev model evaluation."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from unittest.mock import patch

os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "1"
from deepeval.models import DeepEvalBaseSystemOneModel
from deepeval.models.system_one.schema import ChoiceAnswer, SystemOneAnswers
from judge_baseline import evaluate, OPTIONS, canonical

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/judge-baseline"


class Stub(DeepEvalBaseSystemOneModel):
    def __init__(self, selected, fail=False):
        self.selected, self.fail, self.calls = selected, fail, 0

    def load_model(self):
        return None

    def get_model_name(self):
        return "local-integration-stub"

    def decide(self, state, questions):
        self.calls += 1
        if self.fail:
            raise RuntimeError("api_key=do-not-record")
        options = questions["label"].options
        if set(options) != set(OPTIONS) | {"NONE"}:
            raise AssertionError("Unexpected option mapping")
        if "expected_labels" in canonical(state) or "expected_output" in canonical(state):
            raise AssertionError("Evaluator fields reached judge")
        probabilities = {key: float(key == self.selected) for key in options}
        return SystemOneAnswers(choices={"label": ChoiceAnswer(choice=self.selected, probabilities=probabilities, confidence=1.0)}), 0.0

    async def a_decide(self, state, questions):
        return self.decide(state, questions)


def main(name):
    if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
        raise ValueError("Unsafe run name")
    path = CONFIG / (name + ".json")
    if path.exists():
        raise ValueError("Integration artifact already exists")
    state = json.loads((CONFIG / "states/xarray-top-level.json").read_text(encoding="utf-8"))
    records = []
    with patch.object(socket.socket, "connect", side_effect=AssertionError("Outbound connections disabled for local test")):
        for selected, fail in (("propose_probe", False), ("NONE", False), ("propose_probe", True)):
            stub = Stub(selected, fail)
            record = evaluate(state, "deepeval-system-one", "local-integration-stub", stub)
            if fail:
                assert record["status"] == "backend_failure", record
                assert record["recommendation"] is None
                assert "do-not-record" not in canonical(record)
            else:
                assert record["status"] == "completed", record
                assert record["recommendation"]["action"] == (None if selected == "NONE" else selected)
                assert stub.calls == 1
                assert len(record["recommendation"]["provider_calls"]) == 1
            records.append(record)
    result = {"schema_version": 1, "scope": "Real DeepEval 4.2.8 with local stub only; no hosted inference",
              "outbound_socket_connections": "disabled during checks", "checks": 3, "records": records,
              "python": sys.version,
              "package_inventory": subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True).splitlines()}
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print("Passed 3 real-library local integration checks: action mapping, abstention, sanitized failure")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="integration-v2")
    main(parser.parse_args().name)
