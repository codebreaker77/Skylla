"""Optional DeepEval System-1 shadow baseline; commands never execute repairs."""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import sys
import time

OPTIONS = {
    "inspect_failure": "Inspect an observed exception or failed requirement before changing production code.",
    "repair_setup": "Repair an explicitly failed execution precondition before interpreting a probe.",
    "propose_probe": "Propose a new behavioral check when the supplied evidence does not exercise the reported requirement.",
    "continue_investigation": "Continue ordinary source inspection or repair investigation when no explicit execution obstacle needs handling.",
    "defer": "Return unresolved when the remaining execution budget is zero or evidence cannot support a next action."
}


class BackendFailure(Exception):
    def __init__(self, error_type, evidence):
        super().__init__(error_type)
        self.error_type = error_type
        self.evidence = evidence


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def validate(state):
    if not isinstance(state, dict) or set(state) != {"schema_version", "state_id", "issue", "evidence", "remaining_seconds"}:
        raise ValueError("Expected only solver-visible state fields")
    if type(state["schema_version"]) is not int or state["schema_version"] != 1:
        raise ValueError("Unsupported schema")
    for key in ("state_id", "issue"):
        if not isinstance(state[key], str) or not state[key]:
            raise ValueError("Missing " + key)
    seconds = state["remaining_seconds"]
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds < 0:
        raise ValueError("Invalid remaining_seconds")
    evidence = state["evidence"]
    fields = {"preconditions", "observations", "requirement_exercised"}
    if not isinstance(evidence, dict) or set(evidence) != fields:
        raise ValueError("Expected explicit evidence fields")
    if not isinstance(evidence["preconditions"], list) or any(v not in ("passed", "failed", "unknown") for v in evidence["preconditions"]):
        raise ValueError("Invalid preconditions")
    if not isinstance(evidence["observations"], list):
        raise ValueError("Observations must be a list")
    if evidence["requirement_exercised"] not in (True, False, None) or type(evidence["requirement_exercised"]) not in (bool, type(None)):
        raise ValueError("Requirement exercise must be boolean or unknown")
    canonical(state)  # Reject non-finite/non-JSON nested values, not semantic leaks.


def rules(state):
    if state["remaining_seconds"] == 0:
        return "defer"
    evidence = state["evidence"]
    if "failed" in evidence["preconditions"]:
        return "repair_setup"
    if "unknown" in evidence["preconditions"]:
        return "continue_investigation"
    if any(isinstance(o, dict) and "method_exception" in o for o in evidence["observations"]):
        return "inspect_failure"
    if evidence["requirement_exercised"] is False:
        return "propose_probe"
    return "continue_investigation"


def deepeval_judge(state, model, system_one_model=None, option_order=None):
    os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "1"
    from deepeval.classifiers import Classifier, Label
    from deepeval.test_case import LLMTestCase
    from deepeval.models import DeepEvalBaseSystemOneModel

    class RecordingModel(DeepEvalBaseSystemOneModel):
        def __init__(self, inner):
            self.inner, self.calls = inner, []

        def load_model(self):
            return self.inner

        def get_model_name(self):
            return self.inner.get_model_name()

        def decide(self, state, questions):
            call = {"state": state, "questions": {k: v.model_dump(mode="json") for k, v in questions.items()},
                    "answers": None, "reported_cost_usd": None}
            self.calls.append(call)
            started = time.perf_counter()
            try:
                answers, cost = self.inner.decide(state, questions)
                call.update(answers=answers.model_dump(mode="json"), reported_cost_usd=cost)
                return answers, cost
            except Exception as exc:
                call["error_type"] = type(exc).__name__
                raise
            finally:
                call["elapsed_seconds"] = time.perf_counter() - started

        async def a_decide(self, state, questions):
            raise RuntimeError("Synchronous shadow adapter only")

    if system_one_model is None:
        from laya_backend import create_model
        system_one_model = create_model(model)
    recorder = RecordingModel(system_one_model)
    # No expected labels, patches or evaluator outcomes are passed to the judge.
    case = LLMTestCase(input=canonical({"issue": state["issue"], "state_id": state["state_id"],
                                       "remaining_seconds": state["remaining_seconds"],
                                       "instruction": "Recommend one next debugging action; a successful shell exit does not establish a correct repair."}),
                       actual_output=canonical(state["evidence"]))
    order = list(OPTIONS) if option_order is None else option_order
    judge = Classifier(name="skylla_next_evidence_action", labels=[Label(name=k, description=OPTIONS[k]) for k in order],
                       eval_mode="system_one", system_one_model=recorder,
                       include_reason=True, allow_none=True, async_mode=False)
    started = time.perf_counter()
    try:
        label = judge.classify(case, _show_indicator=False)
    except Exception as exc:
        raise BackendFailure(type(exc).__name__, recorder.calls) from None
    elapsed = time.perf_counter() - started
    if judge.error:
        raise ValueError("Judge returned an invalid classification")
    if label is not None and label not in OPTIONS:
        raise ValueError("Unknown action label")
    return {"action": label, "reason": judge.reason, "inference_seconds": elapsed,
            "reported_cost_usd": judge.evaluation_cost,
            "input_tokens": judge.input_tokens, "output_tokens": judge.output_tokens,
            "provider_calls": recorder.calls,
            "local_model_load_seconds": getattr(system_one_model, "load_seconds", None),
            "local_model_raw": getattr(system_one_model, "last_raw", None),
            "hardware": getattr(system_one_model, "hardware", None),
            "provider_state": {"input": case.input, "actual_output": case.actual_output}}


def evaluate(state, backend, model=None, system_one_model=None, option_order=None):
    validate(state)
    order = list(OPTIONS) if option_order is None else option_order
    if not isinstance(order, list) or len(order) != len(OPTIONS) or set(order) != set(OPTIONS):
        raise ValueError("Option order must be an exact permutation")
    started = time.perf_counter()
    record = {"schema_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "mode": "shadow", "backend": backend, "model": model, "state": state,
              "state_sha256": hashlib.sha256(canonical(state).encode()).hexdigest(), "options": OPTIONS,
              "option_order": order, "option_order_sha256": hashlib.sha256(canonical(order).encode()).hexdigest(),
              "options_sha256": hashlib.sha256(canonical(OPTIONS).encode()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "recommendation": None, "status": None, "package_versions": {},
              "wall_seconds": None, "calls_attempted": 0}
    if state["remaining_seconds"] == 0:
        record.update(status="budget_exhausted", recommendation={"action": "defer"})
    elif backend == "rules":
        record.update(status="completed", recommendation={"action": rules(state), "reported_cost_usd": 0})
    elif backend in ("deepeval-laya", "deepeval-system-one"):
        if system_one_model is None and (not model or not Path(model).is_dir()):
            record.update(status="blocked_model_configuration")
        else:
            try:
                packages = [("deepeval", "4.2.8")]
                if system_one_model is None:
                    packages += [("laya", "0.3.20"), ("transformers", "4.51.3")]
                for package, expected in packages:
                    version = importlib.metadata.version(package)
                    record["package_versions"][package] = version
                    if version != expected:
                        raise ValueError("Pinned optional package version mismatch")
                record["calls_attempted"] = 1
                record["recommendation"] = deepeval_judge(state, model, system_one_model, order)
                record["status"] = "completed"
            except importlib.metadata.PackageNotFoundError:
                record["status"] = "blocked_dependencies"
            except BackendFailure as exc:
                record.update(status="backend_failure", error_type=exc.error_type, provider_calls=exc.evidence)
            except Exception as exc:
                # Do not publish provider exception messages: they can contain
                # credentials or request URLs. Keep a type and preserve no fallback.
                record.update(status="backend_failure", error_type=type(exc).__name__)
    else:
        raise ValueError("Unsupported backend")
    record["wall_seconds"] = time.perf_counter() - started
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state")
    parser.add_argument("--backend", choices=("rules", "deepeval-laya"), required=True)
    parser.add_argument("--model")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        parser.error("Output exists; use a new path before attempting inference")
    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    result = evaluate(state, args.backend, args.model)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    print(json.dumps({"status": result["status"], "backend": args.backend,
                      "action": (result["recommendation"] or {}).get("action")}))
    sys.exit(0 if result["status"] in ("completed", "budget_exhausted") else 2)
