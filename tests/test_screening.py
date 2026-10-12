"""Regression checks for real setup failures discovered during cohort screening."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/study"))
from screen import classify


class ScreeningTests(unittest.TestCase):
    def test_missing_fixture_and_legacy_setup_error_are_not_code_failures(self):
        self.assertEqual(classify("pytest", 1, "ERROR at setup of test_click\nfixture 'mocker' not found"), "setup_failure")
        self.assertEqual(classify("pytest", 1, "ERROR at setup of test_imap\nAttributeError: sys.setcheckinterval"), "setup_failure")
        self.assertEqual(classify("pytest", 1, "FAILED test_status\nAssertionError: expected running"), "failed")

    def test_skipped_and_empty_tests_do_not_verify_a_fix(self):
        self.assertEqual(classify("unittest", 0, "Ran 1 test\nOK (skipped=1)"), "inconclusive")
        self.assertEqual(classify("pytest", 0, "1 skipped in 0.1s"), "inconclusive")
        self.assertEqual(classify("unittest", 0, "Ran 0 tests\nOK"), "inconclusive")


if __name__ == "__main__":
    unittest.main()
