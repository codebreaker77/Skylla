import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/study"))
from process_record import execute, readiness


class ProcessRecordTests(unittest.TestCase):
    def test_failed_import_retains_stderr_and_does_not_pass_readiness(self):
        record = execute([sys.executable, "-c", "import skylla_missing_dependency_93851"])
        self.assertNotEqual(record["returncode"], 0)
        self.assertIn("ModuleNotFoundError", record["stderr"])
        self.assertFalse(readiness(record, "case"))

    def test_zero_exit_with_non_json_is_preserved_not_ready(self):
        record = execute([sys.executable, "-c", "print('caught exception')"])
        self.assertEqual(record["returncode"], 0)
        self.assertIn("caught exception", record["stdout"])
        self.assertFalse(readiness(record, "case"))

    def test_timeout_retains_output(self):
        record = execute([sys.executable, "-c", "import time; print('started', flush=True); time.sleep(10)"], timeout=1)
        self.assertTrue(record["timed_out"])
        self.assertIn("started", record["stdout"])
        self.assertFalse(readiness(record, "case"))

    def test_ready_requires_matching_case_and_source_origin(self):
        record = execute([sys.executable, "-c", "print('{\"case\":\"case\",\"ready\":true,\"imported_pinned_source\":true}')"])
        self.assertTrue(readiness(record, "case"))
        self.assertFalse(readiness(record, "another"))
        record["payload"]["imported_pinned_source"] = False
        self.assertFalse(readiness(record, "case"))
