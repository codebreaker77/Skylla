"""Two bounded native Codex episodes; not a matched Skylla comparison."""

import argparse
from datetime import datetime, timezone
import difflib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from prepare_matched_pilot import ROOT, sha, read
from screen_matched_pilot import metadata, write
from process_record import execute

CASES = {
    "bugsinpy:luigi-4": {
        "issue": "S3CopyToTable crashes when columns=None: building the COPY statement calls len(None). The optional column list should be omittable; explicit column lists must continue to work. Repair the production implementation.",
        "regression_target": "test/contrib/redshift_test.py::TestS3CopyToTable"},
    "bugsinpy:tornado-10": {
        "issue": "Rendering a template from a WebSocketHandler fails. A handler rendering a template with message='hello' should produce '<b>hello</b>', but the request fails with TypeError: 'NoneType' object is not iterable and the client receives no rendered message. Repair template rendering while preserving ordinary WebSocket behavior.",
        "regression_target": "tornado.test.websocket_test.WebSocketTest"}}


def environment(work):
    runtime = work / ".runtime"
    runtime.mkdir(exist_ok=True)
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "PATH", "COMSPEC") if key in os.environ}
    env.update(TEMP=str(runtime), TMP=str(runtime), USERPROFILE=str(runtime), PYTHONPATH=str(work),
               PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
               PYTHONHASHSEED="0", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    return env


def evaluator(case, source, work, target):
    shutil.copytree(source, work)
    fixed = ROOT / "artifacts/sources" / (case["id"] + "-fixed")
    fixture = Path(case["test_file"])
    shutil.copyfile(fixed / fixture, work / fixture)
    argv = [sys.executable, "-m", case["mode"], "-q"]
    if case["mode"] == "pytest":
        argv += ["-p", "no:cacheprovider", "-o", "addopts="]
    return work, argv + [target]


def call_codex(argv, prompt, timeout, stdout_path, stderr_path, cwd):
    started = time.perf_counter()
    process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               cwd=cwd, text=True, encoding="utf-8", errors="replace")
    timed_out = False
    try:
        stdout, stderr = process.communicate(prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        # This PID belongs to our live Popen child. Stop its owned tool descendants too.
        if process.poll() is None:
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
        stdout, stderr = process.communicate(timeout=15)
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    events = []
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    usage = [e["usage"] for e in events if e.get("type") == "turn.completed" and "usage" in e]
    commands = [e["item"] for e in events if e.get("type") == "item.completed" and
                e.get("item", {}).get("type") == "command_execution"]
    return {"returncode": process.returncode, "timed_out": timed_out,
            "elapsed_seconds": time.perf_counter() - started, "usage": usage,
            "completed_command_calls": len(commands), "stdout_sha256": sha(stdout_path),
            "stderr_sha256": sha(stderr_path), "event_count": len(events)}


def main(name):
    if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
        raise ValueError("Unsafe run name")
    executable = shutil.which("codex.cmd")
    if executable is None:
        raise RuntimeError("Codex Windows CLI unavailable")
    model_interpreter = ROOT / "artifacts/runtime/python39/python.exe"
    if not model_interpreter.exists():
        raise RuntimeError("Prepare and check the sandbox-readable project interpreter first")
    rows = read(ROOT / "experiments/matched-pilot/v1/cohort.json")["selected"]
    selected = [row for row in rows if row["id"] in CASES]
    output = ROOT / "experiments/matched-pilot/native-feasibility" / name
    private = ROOT / "artifacts/matched-native" / name
    output.mkdir(parents=True, exist_ok=False)
    private.mkdir(parents=True, exist_ok=False)
    version = subprocess.run([executable, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    protocol = {"schema_version": 1, "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
                "scope": "Two native-only development feasibility episodes; no Skylla or Laya treatment",
                "model": "gpt-5.6-terra", "reasoning_effort": "medium", "cli_version": version,
                "auth": "Existing ChatGPT login; no supplied API key", "wall_cap_seconds_per_episode": 120,
                "token_cap": None, "token_note": "CLI usage measured after completion; no hard token quota or dollar estimate established",
                "method_sha256": sha(ROOT / "experiments/matched-pilot/NATIVE_FEASIBILITY_V3.md"),
                "launcher_revision": 3, "permission_profile": ":workspace", "windows_sandbox": "elevated",
                "solver_interpreter": str(model_interpreter),
                "solver_runtime_manifest_sha256": sha(model_interpreter.parent / "manifest.json"),
                "script_sha256": sha(Path(__file__)), "cases": CASES,
                "runtime_python": sys.version, "host": sys.platform,
                "cohort_sha256": sha(ROOT / "experiments/matched-pilot/v1/cohort.json")}
    write(output / "protocol.json", protocol)
    results = []
    for row in selected:
        case = metadata(row)
        source = ROOT / "artifacts/sources" / (case["id"] + "-buggy")
        work = private / (case["id"] + "-solver")
        shutil.copytree(source, work)
        package = work / row["project"]
        original = {p.relative_to(work).as_posix(): p.read_bytes() for p in package.rglob("*.py")
                    if not {"test", "tests"} & set(p.relative_to(package).parts)}
        prompt = (CASES[row["id"]]["issue"] + "\nUse only files inside this workspace. Do not read parent directories, "
                  "reference snapshots, benchmark metadata, credentials or network sources. You can inspect source, "
                  "edit production code and run native tests or your own probes. Do not modify evaluator tests. "
                  "Use the sandbox-readable Python interpreter at " + str(model_interpreter) + ". You have 120 seconds. "
                  "Leave the smallest production repair in this workspace, and report what you tested. No commit or push.")
        argv = [executable, "-a", "never", "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
                "-C", str(work), "-s", "workspace-write", "-m", "gpt-5.6-terra", "-c", 'model_reasoning_effort="medium"',
                "-c", 'windows.sandbox="elevated"', "-c", 'default_permissions=":workspace"',
                "-c", 'web_search="disabled"', "--json", "-"]
        write(output / (case["id"] + "-request.json"), {"prompt": prompt, "argv": argv,
                                                       "source_metadata": read(source / ".skylla-source.json"),
                                                       "production_before_sha256": {p: __import__("hashlib").sha256(b).hexdigest() for p, b in original.items()}})
        inference = call_codex(argv, prompt, 120, private / (case["id"] + ".stdout.jsonl"),
                               private / (case["id"] + ".stderr.txt"), work)
        changed = {p: (work / p).read_bytes() for p, before in original.items()
                   if (work / p).exists() and (work / p).read_bytes() != before}
        deleted = [p for p in original if not (work / p).exists()]
        patch = "".join("".join(difflib.unified_diff(original[p].decode("utf-8").splitlines(True),
                                                   after.decode("utf-8").splitlines(True), fromfile="a/" + p, tofile="b/" + p))
                        for p, after in sorted(changed.items()))
        patch_path = private / (case["id"] + ".patch")
        patch_path.write_text(patch, encoding="utf-8")
        result = {"case_id": row["id"], "inference": inference, "changed_production_files": sorted(changed),
                  "deleted_production_files": deleted, "patch_sha256": sha(patch_path), "evaluation": [],
                  "status": "not_verified"}
        # Evaluate final candidate only on clean buggy copies with independent fixed fixtures.
        for kind, target in (("target", case["target"]), ("regression_class", CASES[row["id"]]["regression_target"])):
            evaluation_work, command = evaluator(case, source, private / (case["id"] + "-eval-" + kind), target)
            for relative, after in changed.items():
                (evaluation_work / relative).write_bytes(after)
            record = execute(command, cwd=evaluation_work, env=environment(evaluation_work), timeout=30)
            path = output / (case["id"] + "-" + kind + ".json")
            write(path, record)
            result["evaluation"].append({"kind": kind, "returncode": record["returncode"],
                                          "timed_out": record["timed_out"], "record_sha256": sha(path)})
        if not deleted and changed and not inference["timed_out"] and inference["returncode"] == 0 and all(
                e["returncode"] == 0 and not e["timed_out"] for e in result["evaluation"]):
            result["status"] = "candidate_passes_selected_checks_pending_review"
        write(output / (case["id"] + "-summary.json"), result)
        results.append(result)
        print(json.dumps({"case": row["id"], "status": result["status"],
                          "seconds": inference["elapsed_seconds"], "changed": sorted(changed)}), flush=True)
    write(output / "summary.json", {"scope": protocol["scope"], "protocol_sha256": sha(output / "protocol.json"),
                                    "cases": results, "note": "Inspect test counts and failures before claiming verified repairs; no comparative effect measured."})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="run-001")
    main(parser.parse_args().name)
