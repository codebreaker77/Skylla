import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/study"))
from receiver_filter import filter_candidates


class ReceiverFilterTests(unittest.TestCase):
    def test_shared_state_and_aliased_access_survive_unrelated_owner_filter(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "sample.py").write_text("class Receiver:\n def init(self):\n  self.shared = {}\n", encoding="utf-8")
            candidates = [{"id": name, "scope": scope, "module": "sample", "declaring_class": "Other",
                           "attribute": attribute, "source_file": "sample.py"}
                          for name, scope, attribute in (("registry", "class", "registry"),
                                                         ("alias", "instance", "shared"),
                                                         ("irrelevant", "instance", "missing"))]
            kept, decisions = filter_candidates(source, candidates, [{"module": "sample", "class": "Receiver"}])
            self.assertEqual([c["id"] for c in kept], ["registry", "alias"])
            self.assertFalse(decisions[-1]["keep"])
