from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/study"))
from observer_candidates import propose


class ObserverCandidateTests(unittest.TestCase):
    def test_source_is_parsed_without_execution_and_nested_helpers_are_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.py").write_text("""raise RuntimeError('must not execute')
class Owner:
    registry = {}
    scalar = 1
    def initialize(self):
        self.handlers = dict()
        def unrelated():
            self.hidden = []
        if True:
            self.queue = deque()
""", encoding="utf-8")
            candidates = propose(root, ["sample.py"])
            self.assertEqual({c["attribute"] for c in candidates}, {"registry", "handlers", "queue"})

    def test_paths_cannot_escape_source_and_repeated_accesses_are_deduplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.py").write_text("""class Owner:
    def one(self):
        self.values = []
    def two(self):
        self.values = list()
""", encoding="utf-8")
            self.assertEqual(len(propose(root, ["sample.py"])), 1)
            with self.assertRaises(ValueError):
                propose(root, ["../outside.py"])
