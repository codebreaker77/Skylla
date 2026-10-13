"""Audit tokenization only; never load weights or execute a model forward."""

import hashlib
import json
import os
from pathlib import Path
from unittest.mock import patch
import socket

os.environ.update(USE_TF="0", USE_FLAX="0", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", DEEPEVAL_TELEMETRY_OPT_OUT="1")
from transformers import PreTrainedTokenizerFast
from laya.agent import Agent
from judge_baseline import evaluate
from check_judge_integration import Stub

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/judge-baseline"


def main():
    path = CONFIG / "token-audit.json"
    if path.exists():
        raise ValueError("Token audit exists")
    checkpoint = ROOT / "artifacts/laya-baseline/checkpoint"
    agent = object.__new__(Agent)
    agent.tok = PreTrainedTokenizerFast.from_pretrained(str(checkpoint / "tokenizer"), local_files_only=True)
    agent.cfg = json.loads((checkpoint / "rl_agent_config.json").read_text(encoding="utf-8"))
    records = []
    with patch.object(socket.socket, "connect", side_effect=AssertionError("Offline token audit")):
        for state_path in sorted((CONFIG / "states").glob("*.json")):
            state = json.loads(state_path.read_text(encoding="utf-8"))
            result = evaluate(state, "deepeval-system-one", "local-integration-stub", Stub("propose_probe"))
            if result["status"] != "completed":
                raise ValueError("Unable to construct exact SDK inputs")
            call = result["recommendation"]["provider_calls"][0]
            mapped = {key: {"type": "choice", "instructions": question["instructions"], "criteria": question["options"]}
                      for key, question in call["questions"].items()}
            ids = list(mapped)
            internal = {key: agent._to_internal(q) for key, q in mapped.items()}
            actual = agent._encode_state(call["state"], ids, internal, max_len=1024, head_max_len=256)
            full = agent._encode_state(call["state"], ids, internal, max_len=32768, head_max_len=32768)
            for key, small, large in zip(ids, actual, full):
                records.append({"state_id": state["state_id"], "question": key,
                                "input_tokens": len(small["ids"]), "untruncated_tokens": len(large["ids"]),
                                "markers": len(small["markers"]), "options": len(mapped[key]["criteria"]),
                                "identical_to_untruncated": small["ids"] == large["ids"]})
    value = {"scope": "Pure tokenization using real SDK serialization and local stub; no neural forward",
             "records": records, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
