"""Deterministic policies see only the common public menu and execution receipts.

No imports of fixtures, reference implementations, labels, family, or fault state.
These bounded heuristics are not reproductions of published systems.
"""

import itertools

ARMS = ("blind_search", "input_sweep", "normalize_then_sweep",
        "always_calibrate", "conditional_calibrate")


def run_policy(arm, public, execute, calibrate):
    if arm not in ARMS:
        raise ValueError("Unknown arm")
    current = dict(public["initial_probe"])
    seen, decisions = set(), []

    def key(probe):
        return tuple(probe[field] for field in ("input", "observer", "source"))

    def run(probe, reason):
        seen.add(key(probe))
        decisions.append({"action": "execute", "probe": dict(probe), "reason": reason})
        return execute(probe)

    def found(receipt):
        return receipt is not None and receipt["source_matches"] and receipt["symptom"]

    def finish(status, probe=None):
        return {"status": status, "selected_probe": probe, "decisions": decisions}

    first = run(current, "shared_initial_probe")
    if first is None:
        return finish("budget_exhausted")
    if arm not in ("always_calibrate", "conditional_calibrate") and found(first):
        return finish("candidate_discriminator", current)

    if arm in ("always_calibrate", "conditional_calibrate"):
        # Both arms repair provenance first. This checks a public execution fact,
        # not an evaluator label about why the probe was constructed.
        if not first["source_matches"]:
            current["source"] = "workspace"
            first = run(current, "repair_source_from_receipt")
            if first is None:
                return finish("budget_exhausted")
        if arm == "conditional_calibrate" and found(first):
            return finish("candidate_discriminator", current)
        decisions.append({"action": "calibrate", "probe": dict(current),
                          "reason": "always_control" if arm == "always_calibrate" else "null_observation"})
        control = calibrate(current)
        if control is None:
            return finish("budget_exhausted")
        if found(first):
            return finish("candidate_discriminator", current)
        if not control["sensitive"]:
            current["observer"] = control["perturbed_field"]
            receipt = run(current, "repair_observer_from_control")
            if receipt is None:
                return finish("budget_exhausted")
            if found(receipt):
                return finish("candidate_discriminator", current)
        # The control supports only its tested collector and input. No global
        # adequacy claim or hypothesis rejection is made before this input sweep.
        candidates = [dict(current, input=value) for value in public["input_order"]]
    elif arm == "normalize_then_sweep":
        inputs = [current["input"]] + public["input_order"]
        candidates = [{"input": value, "source": "workspace", "observer": "result"} for value in inputs]
    elif arm == "input_sweep":
        candidates = []
        for source, observer in ((current["source"], current["observer"]),
                                 ("workspace", current["observer"]), ("workspace", "result")):
            candidates.extend({"input": value, "source": source, "observer": observer}
                              for value in public["input_order"])
    else:
        candidates = public["blind_order"]

    for probe in candidates:
        if key(probe) in seen:
            continue
        receipt = run(probe, "shared_menu_search")
        if receipt is None:
            return finish("budget_exhausted")
        if found(receipt):
            return finish("candidate_discriminator", probe)
    return finish("menu_exhausted")


def full_menu(input_ids):
    return [{"input": value, "observer": observer, "source": source}
            for value, observer, source in itertools.product(input_ids, ("result", "status"),
                                                            ("workspace", "fallback"))]
