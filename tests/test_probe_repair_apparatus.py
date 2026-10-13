"""Check controlled-fault apparatus before freezing comparative runs."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/study/probe_repair"))
from episode import load_program, run_episode
from fixtures import FAMILIES
from policies import ARMS


class ApparatusTests(unittest.TestCase):
    def test_reference_matches_spec_and_each_fault_has_one_trigger(self):
        buggy, reference = load_program("buggy.py"), load_program("reference.py")
        for family, inputs in FAMILIES.items():
            differences = []
            for data, expected in inputs:
                self.assertEqual(getattr(reference, family)(data), expected)
                differences.append(getattr(buggy, family)(data) != expected)
            self.assertEqual(differences, [True, False, False, False])

    def test_canary_is_not_a_fault_observation_and_budget_is_enforced(self):
        record = run_episode("omitted_option", "wrong_observer", True, 101,
                             "conditional_calibrate", budget=4)
        self.assertEqual(record["invocations"], 4)
        self.assertEqual(record["decision"]["status"], "budget_exhausted")
        self.assertFalse(record["verified_discriminator"])
        self.assertEqual(len(record["evaluation"]), 1)

    def test_masked_result_can_pass_control_without_exposing_fault(self):
        record = run_episode("retained_state", "masked_result", True, 101,
                             "conditional_calibrate")
        self.assertTrue(record["controls"][0]["sensitive"])
        self.assertFalse(record["verified_discriminator"])
        self.assertEqual(record["decision"]["status"], "menu_exhausted")

    def test_fault_free_control_never_becomes_completion(self):
        for arm in ARMS:
            record = run_episode("configuration", "adequate", False, 101, arm)
            self.assertFalse(record["false_completion"])
            self.assertNotEqual(record["decision"]["status"], "candidate_discriminator")
            self.assertLessEqual(record["invocations"], 8)

    def test_provenance_repair_uses_workspace_and_reset_is_repeatable(self):
        first = run_episode("execution_order", "wrong_source", True, 101, "conditional_calibrate")
        second = run_episode("execution_order", "wrong_source", True, 101, "conditional_calibrate")
        self.assertFalse(first["trace"][0]["receipt"]["source_matches"])
        self.assertTrue(first["trace"][1]["receipt"]["source_matches"])
        self.assertEqual(first["trace"][0]["audit"]["loaded_file"], "experiments/probe-repair/programs/fallback.py")
        self.assertEqual(first["trace"][1]["audit"]["loaded_file"], "experiments/probe-repair/programs/buggy.py")
        self.assertEqual(first["decision"], second["decision"])
        self.assertEqual([item["receipt"] for item in first["trace"]],
                         [item["receipt"] for item in second["trace"]])


if __name__ == "__main__":
    unittest.main()
