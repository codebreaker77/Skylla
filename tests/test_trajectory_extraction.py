"""Guard the data-only extraction boundary and real trace-format edge cases."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/study"))
from extract_trajectory_audit import extract, RUNTIME


class TrajectoryExtractionTests(unittest.TestCase):
    def test_environment_prefix_is_execution_but_search_is_not(self):
        self.assertTrue(RUNTIME.search("PYTHONIOENCODING=utf-8 python reproduce.py"))
        self.assertTrue(RUNTIME.search("cd /testbed && python3 -m pytest reproduce_issue"))
        self.assertFalse(RUNTIME.search("grep -n python source.py"))

    def test_link_by_call_id_and_preserve_zero_exit_exception_as_data(self):
        messages = [
            {"role": "user", "content": "A reported exception"},
            {"role": "assistant", "content": "Run reproduction", "tool_calls": [
                {"id": "first", "function": {"name": "bash", "arguments": json.dumps({"command": "python reproduce.py"})}},
                {"id": "second", "function": {"name": "bash", "arguments": json.dumps({"command": "python other.py"})}}]},
            {"role": "tool", "tool_call_id": "second", "extra": {"returncode": 1, "raw_output": "Other error"}},
            {"role": "tool", "tool_call_id": "first", "extra": {"returncode": 0, "raw_output": "Traceback: caught target exception"}},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.json"
            path.write_text(json.dumps({"messages": messages}), encoding="utf-8")
            result, packet = extract({"instance_id": "case", "source_url": "https://example.invalid/source"}, path)
        self.assertEqual(result["selected_candidates"][0]["observation_message_index"], 3)
        self.assertEqual(packet[0]["return_code"], 0)
        self.assertIn("exception", packet[0]["observation"])
        self.assertNotIn("passed", packet[0])


if __name__ == "__main__":
    unittest.main()
