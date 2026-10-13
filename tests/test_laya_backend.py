from contextlib import nullcontext
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/study"))
from laya_backend import strict_cuda_forward


class LayaGpuGuardTests(unittest.TestCase):
    def test_non_cuda_device_is_rejected_before_forward(self):
        agent = SimpleNamespace(device=SimpleNamespace(type="cpu"), model=Mock())
        with self.assertRaises(RuntimeError):
            strict_cuda_forward(None, agent, {})
        agent.model.assert_not_called()

    def test_cuda_oom_propagates_without_cpu_retry(self):
        device = SimpleNamespace(type="cuda")
        model = Mock(side_effect=RuntimeError("CUDA out of memory"))
        agent = SimpleNamespace(device=device, model=model)
        tensors = {key: Mock() for key in ("input_ids", "attention_mask", "marker_pos", "marker_mask", "qtype")}
        torch = SimpleNamespace(autocast=lambda *args, **kwargs: nullcontext(), float16="float16")
        with self.assertRaisesRegex(RuntimeError, "CUDA out of memory"):
            strict_cuda_forward(torch, agent, tensors)
        self.assertEqual(model.call_count, 1)
        for tensor in tensors.values():
            tensor.to.assert_called_once_with(device)
        self.assertEqual(agent.device.type, "cuda")
