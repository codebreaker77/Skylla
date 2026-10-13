import copy
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/study"))
from judge_baseline import evaluate, validate


def state():
    return {"schema_version": 1, "state_id": "development-state", "issue": "The reported method should work.",
            "evidence": {"preconditions": ["passed"], "observations": [], "requirement_exercised": False},
            "remaining_seconds": 30}


class JudgeBaselineTests(unittest.TestCase):
    def test_zero_budget_blocks_backend_import_or_call(self):
        request = state()
        request["remaining_seconds"] = 0
        with patch("judge_baseline.deepeval_judge", side_effect=AssertionError("must not call")):
            result = evaluate(request, "deepeval-laya", "missing-checkpoint")
        self.assertEqual(result["status"], "budget_exhausted")
        self.assertEqual(result["calls_attempted"], 0)

    def test_missing_local_checkpoint_has_no_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            result = evaluate(state(), "deepeval-laya", "missing-checkpoint")
        self.assertEqual(result["status"], "blocked_model_configuration")
        self.assertIsNone(result["recommendation"])

    def test_reference_fields_and_nonfinite_budgets_are_rejected(self):
        request = state()
        request["expected_label"] = "propose_probe"
        with self.assertRaises(ValueError):
            validate(request)
        request = state()
        request["remaining_seconds"] = float("nan")
        with self.assertRaises(ValueError):
            validate(request)

    def test_rules_preserve_state_and_exception_is_inspected_not_success(self):
        request = state()
        request["evidence"]["observations"] = [{"method_exception": {"type": "AttributeError"}}]
        before = copy.deepcopy(request)
        result = evaluate(request, "rules")
        self.assertEqual(result["recommendation"]["action"], "inspect_failure")
        self.assertEqual(request, before)
