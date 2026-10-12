"""Screen pinned historical cases locally; never invokes an inference provider."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/pilot"))
from prepare import prepare

BENCHMARK_COMMIT = "11c5f1eea954a42132cfd06bf257766a7963e0fd"
SELECTION = {"cookiecutter": [1, 2, 3, 4], "luigi": [5, 7, 9],
             "tornado": [3, 5, 6, 7], "tqdm": [6]}


def fields(path):
    text = path.read_text(encoding="utf-8")
    return dict(re.findall(r'([a-z_]+)\s*=\s*"([^"]*)"', text))


def build_manifest():
    benchmark = ROOT / "artifacts/sources/BugsInPy"
    actual = subprocess.run(["git", "-C", str(benchmark), "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    if actual != BENCHMARK_COMMIT:
        raise ValueError("Benchmark checkout differs from pinned revision")
    cases = []
    for project, ids in SELECTION.items():
        project_root = benchmark / "projects" / project
        repository = fields(project_root / "project.info")["github_url"]
        for bug in ids:
            directory = project_root / "bugs" / str(bug)
            info = fields(directory / "bug.info")
            commands = directory.joinpath("run_test.sh").read_text(encoding="utf-8").splitlines()
            commands = [line.strip() for line in commands if line.strip()]
            if all("-m unittest" in command for command in commands):
                mode = "unittest"
                targets = [command.split()[-1] for command in commands]
            else:
                mode = "pytest"
                targets = [command.split()[-1] for command in commands]
            cases.append({"id": project + "-" + str(bug), "repository": repository,
                          "buggy_commit": info["buggy_commit_id"],
                          "fixed_commit": info["fixed_commit_id"],
                          "benchmark_python": info["python_version"],
                          "test_file": info["test_file"], "test_mode": mode,
                          "targets": targets, "original_commands": commands,
                          "selection_reason": "Execution/workflow symptoms suggested by test names; selected before source inspection and without viewing reference patches"})
    return {"schema_version": 1, "benchmark_commit": actual,
            "purpose": "Development screening, not a frozen holdout or prevalence sample",
            "test_environment_deviation": "Local Python 3.9; tox matrix replaced with direct pytest where present",
            "cases": cases}


def classify(mode, code, combined):
    """Screening triage, not a universal distinction between environment and code defects."""
    if code == 0:
        if re.search(r"\b\d+ skipped\b|skipped=\d+|Ran 0 tests", combined):
            return "inconclusive"
        return "passed"
    if ("ModuleNotFoundError" in combined or "ImportError" in combined or
            "ERROR at setup" in combined or "ERROR at teardown" in combined or
            "unittest.loader._FailedTest" in combined or (mode == "pytest" and code != 1)):
        return "setup_failure"
    return "failed"


def run_case(case, output, repeats):
    result = {"id": case["id"], "runs": [], "sources": [], "admitted": False}
    for variant in ("buggy", "fixed"):
        try:
            excluded = (("maint/test/appengine/",) if case["id"].startswith("tornado-") else
                        ("docs/",) if case["id"] in ("cookiecutter-1", "cookiecutter-2") else ())
            metadata = prepare(case, variant, exclude_symlink_prefixes=excluded)
            result["sources"].append(metadata)
        except Exception as error:
            result["setup_error"] = {"variant": variant, "type": type(error).__name__, "message": str(error)}
            return result
        source = ROOT / metadata["path"]
        for repeat in range(repeats):
            work_root = ROOT / "workspaces/screening"
            work_root.mkdir(parents=True, exist_ok=True)
            work = Path(tempfile.mkdtemp(prefix=case["id"] + "-", dir=work_root))
            shutil.copytree(source, work, dirs_exist_ok=True)
            # Reference fixtures on both variants, as in the benchmark checkout.
            if variant == "buggy":
                try:
                    fixed = prepare(case, "fixed", exclude_symlink_prefixes=excluded)
                    fixture = ROOT / fixed["path"] / case["test_file"]
                    shutil.copyfile(fixture, work / case["test_file"])
                except Exception as error:
                    result["setup_error"] = {"variant": variant, "type": type(error).__name__, "message": str(error)}
                    return result
            mode = case["test_mode"]
            argv = [sys.executable, "-m", mode, "-q"]
            if mode == "pytest":
                argv.extend(["-p", "no:cacheprovider", "-o", "addopts="])
                if case["id"] == "cookiecutter-3":
                    argv.extend(["-p", "pytest_mock"])
            argv.extend(case["targets"])
            runtime = work / ".runtime"
            runtime.mkdir()
            env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "PATH", "COMSPEC")
                   if key in os.environ}
            env.update({"TEMP": str(runtime), "TMP": str(runtime), "HOME": str(runtime),
                        "USERPROFILE": str(runtime), "PYTHONPATH": str(work),
                        "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
                        "PYTHONIOENCODING": "utf-8", "PYTHONHASHSEED": "0",
                        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})
            start = time.perf_counter()
            try:
                process = subprocess.run(argv, cwd=work, env=env, capture_output=True,
                                         text=True, encoding="utf-8", errors="replace", timeout=30)
                code, stdout, stderr = process.returncode, process.stdout, process.stderr
                combined = stdout + stderr
                status = classify(mode, code, combined)
            except subprocess.TimeoutExpired as error:
                def decode(value):
                    return value.decode("utf-8", "replace") if isinstance(value, bytes) else (value or "")
                code, stdout, stderr, status = None, decode(error.stdout), decode(error.stderr), "timeout"
            raw = output / (case["id"] + "-" + variant + "-" + str(repeat + 1) + ".json")
            payload = {"argv": argv, "cwd": str(work), "stdout": stdout, "stderr": stderr}
            raw.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            result["runs"].append({"variant": variant, "repeat": repeat + 1, "status": status,
                                   "exit_code": code, "seconds": round(time.perf_counter() - start, 6),
                                   "raw_log": raw.relative_to(ROOT).as_posix(),
                                   "raw_log_sha256": hashlib.sha256(raw.read_bytes()).hexdigest()})
            # Repeated setup failures are not useful admission checks.
            if status in ("setup_failure", "timeout"):
                break
    states = {v: [r["status"] for r in result["runs"] if r["variant"] == v]
              for v in ("buggy", "fixed")}
    result["admitted"] = states == {"buggy": ["failed"] * repeats, "fixed": ["passed"] * repeats}
    result["admission_scope"] = "Targeted discriminator only; mechanism ambiguity and regressions still need review"
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-only", action="store_true")
    parser.add_argument("--output", default="experiments/expansion/screening/cases.json")
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--repeats", type=int, default=3, choices=(1, 3))
    parser.add_argument("--workers", type=int, default=2, choices=(1, 2, 3))
    args = parser.parse_args()
    if args.manifest_only:
        manifest = build_manifest()
        path = (ROOT / args.output).resolve()
        if not path.is_relative_to((ROOT / "experiments/expansion").resolve()):
            parser.error("Manifest must be inside experiments/expansion")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(manifest, indent=2) + "\n")
        print("Frozen", len(manifest["cases"]), "screening candidates at", path)
    else:
        manifest_path = ROOT / "experiments/expansion/screening/cases.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["benchmark_commit"] != BENCHMARK_COMMIT:
            parser.error("Frozen manifest differs from pinned benchmark revision")
        output = (ROOT / args.output).resolve()
        if not output.is_relative_to((ROOT / "artifacts/screening").resolve()):
            parser.error("Raw screening output must be inside artifacts/screening")
        output.mkdir(parents=True, exist_ok=False)
        cases = [case for case in manifest["cases"] if not args.case or case["id"] in args.case]
        if not cases or set(args.case) - {case["id"] for case in cases}:
            parser.error("Unknown or empty case selection")
        results = []
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(run_case, case, output, args.repeats): case["id"] for case in cases}
            for future in as_completed(futures):
                case_id = futures[future]
                try:
                    result = future.result()
                except Exception as error:
                    result = {"id": case_id, "admitted": False, "setup_error": str(error)}
                results.append(result)
                print(json.dumps(result), flush=True)
        packages = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True,
                                  text=True, check=True).stdout.splitlines()
        summary = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
                   "packages": packages, "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   "benchmark_commit": BENCHMARK_COMMIT, "repeats": args.repeats,
                   "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                   "environment_policy": "Child home/temp redirected to workspace; unrelated pytest addopts cleared",
                   "cases": sorted(results, key=lambda result: result["id"])}
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
