"""Bounded, non-model Windows sandbox project-runner check."""

import json
from pathlib import Path
import shutil
from run_native_feasibility import call_codex
from prepare_matched_pilot import ROOT, sha


def main():
    output = ROOT / "experiments/matched-pilot/sandbox-runtime-check.json"
    if output.exists():
        raise ValueError("Preserve existing check")
    private = ROOT / "artifacts/harness-smoke"
    code = ("import os; os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'; "
            "import pytest; raise SystemExit(pytest.main(['-q','-p','no:cacheprovider','-o','addopts=',"
            "'test/contrib/redshift_test.py::TestS3CopyToTable']))")
    work = ROOT / "artifacts/matched-native/run-002/luigi-4-solver"
    runtime = ROOT / "artifacts/runtime/python39"
    argv = [shutil.which("codex.cmd"), "-c", 'windows.sandbox="elevated"', "sandbox", "-P", ":workspace",
            "-C", str(work), str(runtime / "python.exe"), "-c", code]
    result = call_codex(argv, "", 30, private / "runtime.stdout.txt", private / "runtime.stderr.txt", ROOT)
    record = {"scope": "Non-model project-runner check on already patched solver workspace; no new repair or inference",
              "argv": argv, "runtime_manifest_sha256": sha(runtime / "manifest.json"),
              "implementation_sha256": sha(Path(__file__)), "result": result,
              "stdout": (private / "runtime.stdout.txt").read_text(encoding="utf-8"),
              "stderr": (private / "runtime.stderr.txt").read_text(encoding="utf-8")}
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"returncode": result["returncode"], "timed_out": result["timed_out"], "seconds": result["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
