import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/study"))
from action_admissibility import check
from prepare_matched_pilot import select, COUNT, CAP


class MatchedPilotTests(unittest.TestCase):
    def state(self, preconditions=None, budget=10):
        return {"schema_version": 1, "state_id": "current", "issue": "Reported behavior fails",
                "remaining_seconds": budget,
                "evidence": {"preconditions": preconditions or ["passed"],
                             "observations": [], "requirement_exercised": None}}

    def test_setup_requires_explicit_failure_without_replacing_prediction(self):
        for preconditions in ([], ["passed"], ["unknown"]):
            state = self.state()
            state["evidence"]["preconditions"] = preconditions
            before = copy.deepcopy(state)
            result = check(state, "repair_setup")
            self.assertEqual(result["disposition"], "rejected")
            self.assertIsNone(result["admissible_action"])
            self.assertEqual(state, before)
        self.assertEqual(check(self.state(["failed"]), "repair_setup")["disposition"], "allowed")

    def test_exhausted_budget_abstention_and_unknown_are_not_executed(self):
        self.assertEqual(check(self.state(budget=0), "inspect_failure")["admissible_action"], "defer")
        self.assertIsNone(check(self.state(), None)["admissible_action"])
        self.assertEqual(check(self.state(), "invented")["disposition"], "rejected")

    def test_sampling_ignores_input_order_excludes_exposure_and_caps_repository(self):
        rows = [{"id": "case-" + str(n), "project": str(n % 5)} for n in range(30)]
        excluded = ["case-0", "case-1"]
        selected = select(rows, excluded)
        self.assertEqual(selected, select(list(reversed(rows)), excluded))
        self.assertEqual(len(selected), COUNT)
        self.assertFalse(set(excluded) & {r["id"] for r in selected})
        for project in {r["project"] for r in selected}:
            self.assertLessEqual(sum(r["project"] == project for r in selected), CAP)


if __name__ == "__main__":
    unittest.main()
