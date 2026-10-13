"""Evaluator-only readiness screening, not a coding-agent repair experiment."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from prepare_matched_pilot import ROOT, PIN, sha, read, verify
from process_record import execute
from screen import fields
sys.path.insert(0, str(ROOT / "tools/pilot"))
from prepare import prepare


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=True) + "\n")


def metadata(row):
    project = ROOT / "artifacts/sources/BugsInPy/projects" / row["project"]
    directory = project / "bugs" / str(row["bug"])
    if sha(directory / "bug.info") != row["benchmark_metadata_sha256"]:
        raise ValueError("Case metadata drift")
    info = fields(directory / "bug.info")
    commands = [line.strip() for line in (directory / "run_test.sh").read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(commands) != 1:
        raise ValueError("This screen requires one benchmark target invocation")
    words = commands[0].split()
    if "unittest" in words:
        mode = "unittest"
    elif "pytest" in words:
        mode = "pytest"
    else:
        raise ValueError("Unsupported runner; preserve disposition")
    return {"id": row["id"].split(":", 1)[1], "repository": fields(project / "project.info")["github_url"],
            "buggy_commit": info["buggy_commit_id"], "fixed_commit": info["fixed_commit_id"],
            "test_file": info["test_file"], "mode": mode, "target": words[-1]}


def run_case(row, output):
    result = {"case_id": row["id"], "status": "pending_review", "runs": [], "sources": []}
    try:
        case = metadata(row)
        prefixes = ("maint/test/appengine/",) if row["project"] == "tornado" else ()
        sources = {variant: prepare(case, variant, exclude_symlink_prefixes=prefixes) for variant in ("buggy", "fixed")}
        result["sources"] = list(sources.values())
        for variant in ("buggy", "fixed"):
            parent = ROOT / "workspaces/matched-screen"
            parent.mkdir(parents=True, exist_ok=True)
            work = Path(tempfile.mkdtemp(prefix=case["id"] + "-" + variant + "-", dir=parent))
            shutil.copytree(ROOT / sources[variant]["path"], work, dirs_exist_ok=True)
            fixture = Path(case["test_file"])
            if fixture.is_absolute() or ".." in fixture.parts:
                raise ValueError("Fixture path escapes source")
            destination = work / fixture
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / sources["fixed"]["path"] / fixture, destination)
            runtime = work / ".runtime"
            runtime.mkdir()
            env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "PATH", "COMSPEC") if key in os.environ}
            env.update(TEMP=str(runtime), TMP=str(runtime), USERPROFILE=str(runtime),
                       PYTHONPATH=str(work), PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
                       PYTHONIOENCODING="utf-8", PYTHONHASHSEED="0", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
            # Separate import origin check; passing tests alone cannot certify source identity.
            module = row["project"]
            import_code = ("import importlib,json,pathlib; m=importlib.import_module(" + repr(module) + "); "
                           "p=pathlib.Path(m.__file__).resolve(); print(json.dumps({'origin':str(p),'local':p.is_relative_to(pathlib.Path.cwd())}))")
            origin = execute([sys.executable, "-c", import_code], cwd=work, env=env, timeout=30)
            origin_ok = (origin["returncode"] == 0 and isinstance(origin["payload"], dict) and origin["payload"].get("local") is True)
            write(output / (case["id"] + "-" + variant + "-origin.json"), origin)
            if not origin_ok:
                result["runs"].append({"variant": variant, "status": "blocked_import_origin"})
                continue
            argv = [sys.executable, "-m", case["mode"], "-q"]
            if case["mode"] == "pytest":
                argv.extend(["-p", "no:cacheprovider", "-o", "addopts="])
            argv.append(case["target"])
            record = execute(argv, cwd=work, env=env, timeout=30)
            log = output / (case["id"] + "-" + variant + "-target.json")
            write(log, record)
            result["runs"].append({"variant": variant, "returncode": record["returncode"],
                                   "timed_out": record["timed_out"], "launch_error": record["launch_error"],
                                   "elapsed_seconds": record["elapsed_seconds"],
                                   "log": log.relative_to(ROOT).as_posix(), "log_sha256": sha(log),
                                   "status": "awaiting_failure_and_test_count_review"})
        if len(result["runs"]) == 2:
            pair = result["runs"]
            result["exit_pattern_candidate"] = [r.get("returncode") for r in pair] == [1, 0]
            result["note"] = "Exit pattern is triage only: inspect target assertions, executed/skipped counts, setup failures and regression checks before admission."
    except Exception as exc:
        result.update(status="setup_failure", error_type=type(exc).__name__)
    write(output / (row["id"].split(":", 1)[1] + "-summary.json"), result)
    print(json.dumps({"case": row["id"], "status": result["status"],
                      "exit_pattern_candidate": result.get("exit_pattern_candidate")}), flush=True)
    return result


def main(name):
    if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
        raise ValueError("Unsafe name")
    cohort_dir = ROOT / "experiments/matched-pilot/v1"
    verify(cohort_dir)
    output = ROOT / "experiments/matched-pilot/screening" / name
    output.mkdir(parents=True, exist_ok=False)
    cohort = read(cohort_dir / "cohort.json")
    protocol = {"schema_version": 1, "scope": "Evaluator-only local screening; no agent, Laya inference or repair gain",
                "cohort_sha256": sha(cohort_dir / "cohort.json"), "benchmark_commit": PIN,
                "method_sha256": sha(ROOT / "experiments/matched-pilot/METHODOLOGY.md"),
                "implementation_sha256": {p: sha(ROOT / p) for p in ("tools/study/screen_matched_pilot.py", "tools/study/process_record.py", "tools/pilot/prepare.py")},
                "python": sys.version, "platform": sys.platform, "repetitions": 1,
                "per_process_timeout_seconds": 30, "case_workers": 3,
                "deviations": "Windows Python 3.9 local environment; differs from original benchmark runtimes. Fixed-version fixture files in evaluator workspaces only."}
    write(output / "protocol.json", protocol)
    inventory = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True).stdout.splitlines()
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda row: run_case(row, output), cohort["selected"]))
    write(output / "summary.json", {"scope": protocol["scope"], "cases": results,
                                    "package_inventory": inventory, "protocol_sha256": sha(output / "protocol.json"),
                                    "admitted_cases": None, "status": "screen_completed_pending_review"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="run-001")
    main(parser.parse_args().name)
