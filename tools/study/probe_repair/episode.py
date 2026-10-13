"""One isolated controlled episode; evaluate reference behavior after policy completion."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys
import time

from fixtures import CONDITIONS, FAMILIES, initial_probe
from policies import full_menu, run_policy

ROOT = Path(__file__).resolve().parents[3]
PROGRAMS = ROOT / "experiments/probe-repair/programs"


def load_program(filename):
    path = PROGRAMS / filename
    spec = importlib.util.spec_from_file_location("controlled_subject", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_episode(family, condition, fault_present, seed, arm, budget=8):
    if family not in FAMILIES or condition not in CONDITIONS:
        raise ValueError("Unknown case")
    rng = random.Random(seed)
    # Opaque identifiers and menu order vary together, identically across arms.
    input_ids = ["input-" + str(value) for value in rng.sample(range(100, 999), 4)]
    inputs = dict(zip(input_ids, FAMILIES[family]))
    input_order = list(input_ids)
    rng.shuffle(input_order)
    blind_order = full_menu(input_ids)
    rng.shuffle(blind_order)
    public = {"initial_probe": initial_probe(condition, input_ids),
              "input_order": input_order, "blind_order": blind_order,
              "budget": budget, "expected_source": "workspace",
              "available_observers": ["result", "status"]}
    logs, controls = [], []
    spent = 0

    def target(probe, reference=False, perturbation=None):
        data, expected = inputs[probe["input"]]
        use_buggy = fault_present and probe["source"] == "workspace" and not reference
        filename = "fallback.py" if probe["source"] == "fallback" else ("buggy.py" if use_buggy else "reference.py")
        module = load_program(filename)
        started = time.perf_counter()
        result = getattr(module, family)(copy.deepcopy(data))
        payload = {"status": "ok", "result": expected if condition == "masked_result" else result}
        if perturbation == "positive":
            payload["result"] = {"skylla_positive_control": "nonce-" + str(seed)}
        elif perturbation == "placebo":
            payload["unobserved_metadata"] = "nonce-" + str(seed)
        observation = copy.deepcopy(payload[probe["observer"]])
        # Expected outputs encode the public task specification, not gold-patch
        # behavior. The evaluator independently runs the reference implementation.
        symptom = probe["observer"] == "result" and observation != expected
        loaded = Path(module.__file__).resolve()
        if loaded.parent != PROGRAMS.resolve():
            raise ValueError("Unexpected source import")
        receipt = {"observation": observation, "symptom": symptom,
                   "source_matches": loaded.name != "fallback.py"}
        audit = {"loaded_file": loaded.relative_to(ROOT).as_posix(),
                 "source_sha256": hashlib.sha256(loaded.read_bytes()).hexdigest(),
                 "target_seconds": time.perf_counter() - started}
        return receipt, audit

    def charged(probe, kind, perturbation=None):
        nonlocal spent
        if spent >= budget:
            return None
        spent += 1
        receipt, audit = target(probe, perturbation=perturbation)
        logs.append({"invocation": spent, "kind": kind, "probe": dict(probe),
                     "receipt": receipt, "audit": audit})
        return receipt

    def execute(probe):
        return charged(probe, "probe")

    def calibrate(probe):
        if budget - spent < 3:
            return None
        clean = charged(probe, "calibration_clean")
        positive = charged(probe, "calibration_positive", "positive")
        placebo = charged(probe, "calibration_placebo", "placebo")
        control = {"sensitive": clean["observation"] != positive["observation"]
                   and clean["observation"] == placebo["observation"],
                   "perturbed_field": "result", "probe": dict(probe),
                   "scope": "Collector sensitivity to result-field overwrite at this input and source"}
        controls.append(control)
        return copy.deepcopy(control)

    started = time.perf_counter()
    decision = run_policy(arm, copy.deepcopy(public), execute, calibrate)
    policy_seconds = time.perf_counter() - started
    # Reference outcomes are computed only after the policy has returned.
    evaluations = []
    for entry in logs:
        if entry["kind"] != "probe":
            continue
        reference, audit = target(entry["probe"], reference=True)
        valid = entry["receipt"]["source_matches"] and entry["receipt"]["symptom"] and not reference["symptom"]
        evaluations.append({"invocation": entry["invocation"], "probe": entry["probe"],
                            "reference": reference, "reference_audit": audit,
                            "verified_discriminator": valid})
    selected = decision["selected_probe"]
    verified = any(item["verified_discriminator"] and item["probe"] == selected for item in evaluations)
    return {"family": family, "condition": condition, "fault_present": fault_present,
            "seed": seed, "arm": arm, "budget": budget, "public_input": public,
            "decision": decision, "invocations": spent, "controls": controls,
            "trace": logs, "evaluation": evaluations,
            "verified_discriminator": verified,
            "false_completion": decision["status"] == "candidate_discriminator" and not verified,
            "policy_wall_seconds": policy_seconds,
            "reference_invocations": len(evaluations),
            "reset": "Fresh interpreter per episode; newly loaded module and fresh local target state per invocation"}


if __name__ == "__main__":
    request = json.loads(sys.stdin.read())
    print(json.dumps(run_episode(**request), separators=(",", ":")))
