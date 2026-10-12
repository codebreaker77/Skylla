"""Decide from declared experiment contracts; never infer a root cause or run commands."""

from collections import defaultdict
import hashlib
import itertools
import json
import math

POLICIES = ("fixed", "blind", "conditional")


def positive_number(value, name, allow_zero=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name + " must be finite numeric data")
    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError(name + " must be " + ("nonnegative" if allow_zero else "positive"))
    return value


def strings(value, name, nonempty=False, unique=True):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError(name + " must be a " + ("nonempty " if nonempty else "") + "list")
    if any(not isinstance(item, str) or not item for item in value):
        raise ValueError(name + " must contain nonempty strings")
    if unique and len(set(value)) != len(value):
        raise ValueError(name + " must contain unique values")
    return value


def execution_key(candidate):
    return hashlib.sha256(json.dumps(candidate["argv"], separators=(",", ":"),
                                     ensure_ascii=True).encode()).hexdigest()


def validate(request):
    if not isinstance(request, dict) or type(request.get("schema_version")) is not int or request.get("schema_version") != 1:
        raise ValueError("Expected schema_version 1 object")
    state = request.get("state_id")
    if not isinstance(state, str) or not state:
        raise ValueError("state_id must be a nonempty string")
    hypotheses = strings(request.get("hypotheses"), "hypotheses", nonempty=True)
    strings(request.get("required_controls", []), "required_controls")
    budget = request.get("budget")
    if not isinstance(budget, dict):
        raise ValueError("budget must be an object")
    positive_number(budget.get("remaining_seconds"), "remaining_seconds", allow_zero=True)
    positive_number(budget.get("expansion_estimated_seconds"), "expansion_estimated_seconds")
    calls = budget.get("remaining_expansions")
    if isinstance(calls, bool) or not isinstance(calls, int) or calls < 0:
        raise ValueError("remaining_expansions must be a nonnegative integer")
    if "solver_ready" in request and not isinstance(request["solver_ready"], bool):
        raise ValueError("solver_ready must be boolean")
    evidence = request.get("evidence", [])
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a list")
    for record in evidence:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
            raise ValueError("Evidence requires an id")
        if not isinstance(record.get("state_id"), str) or not record["state_id"]:
            raise ValueError("Evidence requires a state_id")
        if "active" in record and not isinstance(record["active"], bool):
            raise ValueError("Evidence active must be boolean")
    ids = [record["id"] for record in evidence]
    if len(ids) != len(set(ids)):
        raise ValueError("Evidence ids must be unique")
    candidates = request.get("candidates", [])
    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list")
    ids = []
    for candidate in candidates:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("id"), str) or not candidate["id"]:
            raise ValueError("Candidate requires an id")
        ids.append(candidate["id"])
        if set(candidate) - {"id", "state_id", "argv", "covers", "outcomes", "predictions", "estimated_seconds", "preconditions", "metadata"}:
            raise ValueError("Unsupported candidate fields; put non-execution annotations in metadata")
        if not isinstance(candidate.get("state_id"), str) or not candidate["state_id"]:
            raise ValueError("Candidate requires a state_id")
        strings(candidate.get("argv"), "argv", nonempty=True, unique=False)
        strings(candidate.get("covers", []), "covers")
        outcomes = strings(candidate.get("outcomes"), "outcomes", nonempty=True)
        predictions = candidate.get("predictions")
        if not isinstance(predictions, dict) or set(predictions) - set(hypotheses):
            raise ValueError("Predictions must reference declared hypotheses")
        if any(value is not None and value not in outcomes for value in predictions.values()):
            raise ValueError("Predictions must use candidate outcome labels or null")
        positive_number(candidate.get("estimated_seconds"), "estimated_seconds")
        checks = candidate.get("preconditions")
        if not isinstance(checks, list) or not checks:
            raise ValueError("Candidates require explicit precondition records")
        for check in checks:
            if not isinstance(check, dict) or check.get("status") not in ("passed", "failed", "unknown"):
                raise ValueError("Precondition status must be passed, failed, or unknown")
            if not isinstance(check.get("id"), str) or not check["id"] or not isinstance(check.get("state_id"), str) or not check["state_id"]:
                raise ValueError("Preconditions require id and state_id")
        if len({check["id"] for check in checks}) != len(checks):
            raise ValueError("Precondition ids must be unique within a candidate")
    if len(ids) != len(set(ids)):
        raise ValueError("Candidate ids must be unique")


def contrast_count(candidate, hypotheses):
    predictions = candidate["predictions"]
    return sum(1 for left, right in itertools.combinations(hypotheses, 2)
               if predictions.get(left) is not None and predictions.get(right) is not None
               and predictions[left] != predictions[right])


def decide(request, policy="conditional"):
    validate(request)
    if policy not in POLICIES:
        raise ValueError("Unknown policy")
    state, budget = request["state_id"], request["budget"]
    result = {"schema_version": 1, "policy": policy, "state_id": state,
              "reasons": [], "warnings": [], "invalid_candidates": [], "duplicate_candidates": [],
              "claim": "Decision from declared contracts; not calibrated utility or a root-cause conclusion"}

    def finish(action, reasons, **fields):
        return dict(result, action=action, reasons=reasons, **fields)

    stale = [record["id"] for record in request.get("evidence", [])
             if record.get("active", True) and record["state_id"] != state]
    if budget["remaining_seconds"] == 0:
        return finish("unresolved", ["budget_exhausted"], stale_evidence=stale)
    if stale:
        return finish("revalidate", ["active_evidence_from_other_state"], evidence_ids=stale)
    if request.get("solver_ready", False):
        return finish("return_to_solver", ["caller_requested_repair_continuation"])
    ready, unknown = [], []
    for candidate in request.get("candidates", []):
        if candidate["state_id"] != state or any(check["status"] == "failed" for check in candidate["preconditions"]):
            result["invalid_candidates"].append(candidate["id"])
        elif candidate["estimated_seconds"] > budget["remaining_seconds"]:
            result["invalid_candidates"].append(candidate["id"])
            result["warnings"].append("candidate_exceeds_remaining_budget:" + candidate["id"])
        elif any(check["status"] != "passed" or check["state_id"] != state for check in candidate["preconditions"]):
            unknown.append(candidate)
        else:
            ready.append(candidate)
    groups = defaultdict(list)
    for candidate in ready:
        groups[execution_key(candidate)].append(candidate)
    unique = []
    for key, group in groups.items():
        reference = group[0]["predictions"]
        if any(candidate["predictions"] != reference or
               set(candidate.get("covers", [])) != set(group[0].get("covers", [])) for candidate in group):
            result["invalid_candidates"].extend(candidate["id"] for candidate in group)
            result["warnings"].append("conflicting_declarations_for_same_execution:" + key)
            continue
        candidate = min(group, key=lambda item: (item["estimated_seconds"], item["id"]))
        unique.append(candidate)
        result["duplicate_candidates"].extend(item["id"] for item in group if item is not candidate)
    ready = unique
    covered = set().union(*(set(candidate.get("covers", [])) for candidate in ready)) if ready else set()
    missing = sorted(set(request.get("required_controls", [])) - covered)
    scores = {candidate["id"]: contrast_count(candidate, request["hypotheses"]) for candidate in ready}
    reasons = (["missing_required_controls"] if missing else [])
    if not ready:
        reasons.append("no_verified_feasible_candidate")
    elif not any(scores.values()):
        reasons.append("no_predicted_distinction")
    expansion_available = budget["remaining_expansions"] > 0 and budget["expansion_estimated_seconds"] <= budget["remaining_seconds"]
    # All arms enforce feasibility and state checks; only menu expansion differs.
    if not ready and unknown:
        return finish("verify_preconditions", ["unverified_candidate_preconditions"],
                      candidate_ids=sorted(candidate["id"] for candidate in unknown))
    if expansion_available and (policy == "blind" or (policy == "conditional" and reasons)):
        return finish("expand", reasons or ["blind_expansion_policy"], missing_controls=missing,
                      generation_limit=1, contrast_counts=scores)
    if policy == "conditional" and reasons:
        return finish("unresolved", reasons + ["expansion_budget_unavailable"],
                      missing_controls=missing, contrast_counts=scores)
    if not ready:
        return finish("unresolved", reasons)
    chosen = min(ready, key=lambda candidate: (-scores[candidate["id"]] / candidate["estimated_seconds"],
                                              candidate["estimated_seconds"], execution_key(candidate)))
    if missing:
        result["warnings"].append("required_controls_not_covered")
    return finish("execute", ["declared_contrast_per_estimated_second"], candidate_id=chosen["id"],
                  contrast_counts=scores, missing_controls=missing)
