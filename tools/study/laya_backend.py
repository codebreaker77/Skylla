"""Local pinned Laya bridge to DeepEval's existing typed decision interface."""

import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import time


def strict_cuda_forward(torch, agent, batch):
    if agent.device.type != "cuda":
        raise RuntimeError("CUDA-only inference")
    with torch.autocast("cuda", dtype=torch.float16):
        return agent.model(batch["input_ids"].to(agent.device), batch["attention_mask"].to(agent.device),
                           batch["marker_pos"].to(agent.device), batch["marker_mask"].to(agent.device),
                           batch["qtype"].to(agent.device))


def create_model(checkpoint):
    os.environ.update(USE_TF="0", USE_FLAX="0", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
                      DEEPEVAL_TELEMETRY_OPT_OUT="1")
    import torch
    import laya
    from deepeval.models import DeepEvalBaseSystemOneModel
    from deepeval.models.system_one.schema import ChoiceAnswer, SystemOneAnswers

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required; CPU inference is disabled")

    checkpoint = Path(checkpoint).resolve(strict=True)
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((root / "experiments/judge-baseline/laya-checkpoint.json").read_text(encoding="utf-8"))
    start = time.perf_counter()
    for item in manifest["files"]:
        path = (checkpoint / item["path"]).resolve()
        if not path.is_relative_to(checkpoint):
            raise ValueError("Model manifest path escapes checkpoint")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != item["sha256"]:
            raise ValueError("Model checkpoint hash mismatch")
    # Laya normalizes tokenizer configuration during loading. Preserve downloaded
    # content and give its loader a separate config copy; hard-link read-only weights.
    runtime = root / "artifacts/laya-baseline/runtime-checkpoint"
    for item in manifest["files"]:
        target = runtime / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and item["path"] == "model.safetensors":
            if not os.path.samefile(target, checkpoint / item["path"]):
                raise ValueError("Unexpected runtime weight file")
        elif item["path"] == "model.safetensors":
            os.link(checkpoint / item["path"], target)
        else:
            shutil.copyfile(checkpoint / item["path"], target)
    agent = laya.load(str(runtime), device="cuda:0", fast=False)
    if agent.device.type != "cuda":
        raise RuntimeError("Laya could not load on CUDA; CPU inference is disabled")
    agent.model.half().eval()

    @torch.inference_mode()
    def gpu_infer(batch):
        # The pinned SDK retries GPU OOM on CPU by default. Replace that private
        # inference method with a strict CUDA pass rather than letting it retry.
        return strict_cuda_forward(torch, agent, batch)

    agent._infer = gpu_infer

    class LayaModel(DeepEvalBaseSystemOneModel):
        def __init__(self):
            self.last_raw = None
            self.load_seconds = time.perf_counter() - start
            self.manifest = manifest
            self.hardware = {"device": str(agent.device), "name": torch.cuda.get_device_name(0),
                             "capability": list(torch.cuda.get_device_capability(0)), "dtype": "float16",
                             "cpu_inference_fallback": False}

        def load_model(self):
            return agent

        def get_model_name(self):
            return "laya@" + manifest["revision"] + ":" + manifest["subfolder"]

        def decide(self, state, questions):
            mapped = {}
            for key, question in questions.items():
                if not hasattr(question, "options"):
                    raise ValueError("This baseline supports Choice questions only")
                instructions = question.instructions
                mapped[key] = {"type": "choice", "instructions": instructions if isinstance(instructions, str) else json.dumps(instructions),
                               "criteria": question.options}
            self.last_raw = agent.predict(state, mapped, max_len=1024, head_max_len=256)
            answers = {}
            for key, answer in self.last_raw["answers"].items():
                probabilities = answer["probabilities"]
                # Published runtime rounds probabilities; preserve its values,
                # without manufacturing calibration or changing its selected ID.
                if set(probabilities) != set(mapped[key]["criteria"]):
                    raise ValueError("Laya option mapping mismatch")
                if any(not math.isfinite(p) or p < 0 or p > 1 for p in probabilities.values()):
                    raise ValueError("Invalid Laya probabilities")
                if abs(sum(probabilities.values()) - 1) > 0.001:
                    raise ValueError("Laya probability mass mismatch")
                answers[key] = ChoiceAnswer(choice=answer["choice"], probabilities=probabilities,
                                            confidence=answer["confidence"])
            return SystemOneAnswers(choices=answers), None  # Local compute is measured in time, not billed tokens.

        async def a_decide(self, state, questions):
            return self.decide(state, questions)

    return LayaModel()
