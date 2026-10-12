"""Behavioral checks for budget, state, uncertainty, and duplicate-execution boundaries."""

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from skylla import decide


def request():
    return {"schema_version": 1, "state_id": "snapshot-a", "hypotheses": ["input", "cache"],
            "required_controls": [], "evidence": [],
            "budget": {"remaining_seconds": 10, "remaining_expansions": 1, "expansion_estimated_seconds": 2},
            "candidates": [{"id": "inspect", "state_id": "snapshot-a", "argv": ["python", "inspect.py"],
                            "covers": [], "outcomes": ["same", "different"],
                            "predictions": {"input": "same", "cache": "different"},
                            "estimated_seconds": 1,
                            "preconditions": [{"id": "source_imported", "state_id": "snapshot-a", "status": "passed"}]}]}


class DecisionTests(unittest.TestCase):
    def test_use_existing_distinction_and_blind_expansion_is_separate(self):
        self.assertEqual(decide(request())["action"], "execute")
        self.assertEqual(decide(request(), "blind")["action"], "expand")

    def test_expansion_detects_missing_default_control_despite_contrasts(self):
        data = request()
        data["required_controls"] = ["option_omitted"]
        self.assertEqual(decide(data)["missing_controls"], ["option_omitted"])
        self.assertEqual(decide(data)["action"], "expand")
        self.assertEqual(decide(data, "fixed")["action"], "execute")

    def test_identical_and_unknown_predictions_do_not_create_information(self):
        for predictions in ({"input": "same", "cache": "same"}, {"input": None, "cache": "different"}):
            data = request()
            data["candidates"][0]["predictions"] = predictions
            self.assertEqual(decide(data)["action"], "expand")

    def test_active_stale_evidence_cannot_support_a_new_state(self):
        data = request()
        data["evidence"] = [{"id": "old-observation", "state_id": "snapshot-before", "active": True}]
        for policy in ("fixed", "blind", "conditional"):
            self.assertEqual(decide(data, policy)["action"], "revalidate")
        data["evidence"][0]["active"] = False
        self.assertEqual(decide(data)["action"], "execute")

    def test_preconditions_must_apply_to_current_state(self):
        data = request()
        data["candidates"][0]["preconditions"][0]["state_id"] = "snapshot-before"
        self.assertEqual(decide(data)["action"], "verify_preconditions")

    def test_setup_failure_is_not_a_hypothesis_falsification(self):
        data = request()
        data["candidates"][0]["preconditions"][0]["status"] = "failed"
        decision = decide(data)
        self.assertEqual(decision["invalid_candidates"], ["inspect"])
        self.assertEqual(decision["action"], "expand")
        self.assertNotIn("diagnosis", decision)

    def test_rename_or_reorder_non_tied_candidates_preserves_execution(self):
        data = request()
        weak = copy.deepcopy(data["candidates"][0])
        weak.update(id="weak", argv=["python", "weak.py"], estimated_seconds=5)
        data["candidates"].append(weak)
        self.assertEqual(decide(data)["candidate_id"], "inspect")
        data["candidates"].reverse()
        data["candidates"][1]["id"] = "renamed"
        self.assertEqual(decide(data)["candidate_id"], "renamed")

    def test_duplicate_execution_cannot_inflate_discrimination(self):
        data = request()
        duplicate = copy.deepcopy(data["candidates"][0])
        duplicate["id"] = "copy"
        data["candidates"].append(duplicate)
        self.assertEqual(len(decide(data)["contrast_counts"]), 1)
        duplicate["predictions"]["cache"] = "same"
        decision = decide(data)
        self.assertEqual(decision["action"], "expand")
        self.assertEqual(len(decision["invalid_candidates"]), 2)

    def test_no_generation_budget_preserves_uncertainty(self):
        data = request()
        data["candidates"] = []
        data["budget"]["remaining_expansions"] = 0
        self.assertEqual(decide(data)["action"], "unresolved")

    def test_budget_limits_apply_before_action(self):
        data = request()
        data["budget"]["remaining_seconds"] = 0
        self.assertEqual(decide(data)["action"], "unresolved")
        data["budget"]["remaining_seconds"] = 0.5
        self.assertEqual(decide(data)["action"], "unresolved")

    def test_bad_costs_and_boolean_budgets_are_rejected(self):
        for cost in (float("nan"), float("inf"), -1, True):
            data = request()
            data["candidates"][0]["estimated_seconds"] = cost
            with self.assertRaises(ValueError):
                decide(data)
        data = request()
        data["budget"]["remaining_expansions"] = True
        with self.assertRaises(ValueError):
            decide(data)

    def test_repeated_argv_values_are_valid_but_undeclared_environment_is_not(self):
        data = request()
        data["candidates"][0]["argv"] = ["python", "script.py", "one", "one"]
        self.assertEqual(decide(data)["action"], "execute")
        data["candidates"][0]["env"] = {"CACHE": "empty"}
        with self.assertRaises(ValueError):
            decide(data)

    def test_duplicate_execution_with_inconsistent_control_tags_is_rejected(self):
        data = request()
        duplicate = copy.deepcopy(data["candidates"][0])
        duplicate.update(id="second", covers=["default"])
        data["candidates"].append(duplicate)
        self.assertEqual(len(decide(data)["invalid_candidates"]), 2)

    def test_solver_continuation_is_not_claimed_as_success(self):
        data = request()
        data["solver_ready"] = True
        decision = decide(data)
        self.assertEqual(decision["action"], "return_to_solver")
        self.assertNotIn("success", decision)


if __name__ == "__main__":
    unittest.main()
