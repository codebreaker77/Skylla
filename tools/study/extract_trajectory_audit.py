"""Extract review candidates as data; never execute recorded shell commands."""

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/trajectory-audit"
RUNTIME = re.compile(r"(?:^|&&|;|\n)\s*(?:env\s+)?(?:[A-Za-z_][A-Za-z0-9_]*=[^\s]+\s+)*(?:python(?:[23](?:\.\d+)?)?|pytest|tox|nosetests|sphinx-build)\b")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract(case, raw_path):
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    messages = raw["messages"]
    tools = {message.get("tool_call_id"): (index, message) for index, message in enumerate(messages) if message.get("role") == "tool"}
    user = next((message.get("content", "") for message in messages if message.get("role") == "user"), "")
    candidates, packet = [], []
    for index, message in enumerate(messages):
        if message.get("role") != "assistant":
            continue
        for position, call in enumerate(message.get("tool_calls") or []):
            function = call.get("function", {})
            if function.get("name") != "bash":
                continue
            arguments = function.get("arguments", {})
            arguments = json.loads(arguments) if isinstance(arguments, str) else arguments
            command = arguments.get("command", "")
            if not RUNTIME.search(command):
                continue
            output_index, tool = tools.get(call.get("id"), (None, {}))
            extra = tool.get("extra", {})
            observation = extra.get("raw_output", tool.get("content", ""))
            event = {"event_id": case["instance_id"] + ":m" + str(index) + ":c" + str(position),
                     "assistant_message_index": index, "call_index": position, "tool_call_id": call.get("id"),
                     "observation_message_index": output_index, "command_sha256": sha(command),
                     "observation_sha256": sha(observation), "return_code": extra.get("returncode"),
                     "observation_characters": len(observation), "selection": "Regex candidate, requires semantic review"}
            candidates.append(event)
            packet.append(dict(event, command=command, observation=observation,
                               agent_context=message.get("content", ""), task_description=user))
    reviewed = candidates[:3]
    return {"instance_id": case["instance_id"], "source_url": case["source_url"],
            "trajectory_format": raw.get("trajectory_format"), "message_count": len(messages),
            "task_description_sha256": sha(user), "all_candidate_count": len(candidates),
            "selected_candidates": reviewed}, packet[:3]


if __name__ == "__main__":
    sample = json.loads((CONFIG / "sample.json").read_text(encoding="utf-8"))
    acquisition = json.loads((CONFIG / "acquisition.json").read_text(encoding="utf-8"))
    by_id = {record["instance_id"]: record for record in acquisition["records"]}
    traces, packets = [], []
    for case in sample["cases"]:
        record = by_id[case["instance_id"]]
        if record["status"] != "downloaded":
            traces.append({"instance_id": case["instance_id"], "status": record["status"], "selected_candidates": []})
            continue
        path = ROOT / record["raw_path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("Changed downloaded artifact")
        trace, packet = extract(case, path)
        traces.append(trace)
        packets.extend(packet)
    output = {"schema_version": 1, "purpose": "Candidate extraction, not automatic evidence-quality labels",
              "sample_sha256": hashlib.sha256((CONFIG / "sample.json").read_bytes()).hexdigest(),
              "extractor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "traces": traces}
    for path, value in ((CONFIG / "events.json", output),
                        (ROOT / "artifacts/trajectory-audit/review-packet.json", packets)):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(value, indent=2) + "\n")
    print("Extracted", len(packets), "early candidates from", len(traces), "selected traces")
