"""Development-only replay of an issue-derived probe; no models or code repairs."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
COMMIT = "ef6e6a7b86f8479b9a1fecf15ad5b88a2326b31e"
SOURCE = ROOT / "artifacts/sources/xarray-evidence"
CONFIG = ROOT / "experiments/evidence-pilot"
MODES = ("top_level_only", "caught_method", "assert_relation")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=True) + "\n")


def probe(mode):
    import xarray as xr
    origin = Path(xr.__file__).resolve()
    if SOURCE.resolve() not in origin.parents:
        raise RuntimeError("Imported xarray outside pinned source")
    ds = xr.Dataset({"a": 0})
    da = xr.DataArray(1, name="b")
    expected = xr.merge([ds, da])
    record = {"mode": mode, "origin": str(origin), "xarray_version": xr.__version__,
              "top_level_variables": sorted(expected.data_vars),
              "method_exercised": mode != "top_level_only"}
    status = 0
    if mode != "top_level_only":
        try:
            actual = ds.merge(da)
            record["relation_holds"] = actual.identical(expected)
            if mode == "assert_relation" and not record["relation_holds"]:
                status = 1
        except Exception as exc:
            record["method_exception"] = {"type": type(exc).__name__, "message": str(exc)}
            record["relation_holds"] = False
            if mode == "assert_relation":
                status = 1
    print(json.dumps(record, ensure_ascii=True))
    return status


def run(python, name):
    if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
        raise ValueError("Run name must use lowercase letters, digits, hyphen or underscore")
    output = CONFIG / "results" / name
    if output.exists():
        raise ValueError("Run already exists; use a new name")
    actual = subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True).strip()
    if actual != COMMIT:
        raise ValueError("Source revision differs from pin")
    dirty = subprocess.check_output(["git", "-C", str(SOURCE), "status", "--porcelain", "--untracked-files=no"], text=True)
    if dirty:
        raise ValueError("Tracked source has been modified")
    python = Path(python).resolve(strict=True)
    env = dict(os.environ, PYTHONPATH=str(SOURCE), PYTHONIOENCODING="utf-8", PYTHONHASHSEED="0")
    packages = subprocess.check_output([str(python), "-m", "pip", "freeze"], text=True)
    version = subprocess.check_output([str(python), "--version"], text=True).strip()
    records = []
    # Repetitions check apparatus stability; they are not independent bugs.
    for repetition in range(3):
        for mode in MODES:
            argv = [str(python), str(Path(__file__).resolve()), "probe", "--mode", mode]
            started = time.perf_counter()
            try:
                result = subprocess.run(argv, cwd=SOURCE, env=env, capture_output=True,
                                        text=True, encoding="utf-8", timeout=30)
                payload = json.loads(result.stdout)
                infra = result.returncode not in (0, 1) or payload.get("mode") != mode
                records.append({"repetition": repetition, "mode": mode, "argv": argv,
                                "returncode": result.returncode, "observation": payload,
                                "stderr": result.stderr, "infrastructure_failure": infra,
                                "elapsed_seconds": time.perf_counter() - started})
            except (subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
                records.append({"repetition": repetition, "mode": mode, "argv": argv,
                                "infrastructure_failure": True, "error": type(exc).__name__,
                                "elapsed_seconds": time.perf_counter() - started})
    summary = {"schema_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(),
               "instance_id": "pydata__xarray-3677", "source_commit": actual,
               "source_tree": subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "HEAD^{tree}"], text=True).strip(),
               "python": version, "packages": packages.splitlines(),
               "script_sha256": sha(Path(__file__)), "method_sha256": sha(CONFIG / "METHODOLOGY.md"),
               "processes": len(records), "infrastructure_failures": sum(r["infrastructure_failure"] for r in records),
               "probe_elapsed_seconds": sum(r["elapsed_seconds"] for r in records),
               "scope": "One hand-authored development bug; no agent, classifier, reference fix or repair comparison"}
    write_json(output / "observations.json", records)
    summary["observations_sha256"] = sha(output / "observations.json")
    write_json(output / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    return int(summary["infrastructure_failures"] != 0)


def verify(name):
    output = CONFIG / "results" / name
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    for field, path in (("script_sha256", Path(__file__)),
                        ("method_sha256", CONFIG / "METHODOLOGY.md"),
                        ("observations_sha256", output / "observations.json")):
        if summary[field] != sha(path):
            raise ValueError("Hash mismatch: " + field)
    records = json.loads((output / "observations.json").read_text(encoding="utf-8"))
    if len(records) != 9 or summary["processes"] != 9:
        raise ValueError("Incomplete run")
    expected = {(rep, mode) for rep in range(3) for mode in MODES}
    if {(r["repetition"], r["mode"]) for r in records} != expected:
        raise ValueError("Unexpected modes/repetitions")
    if sum(r["infrastructure_failure"] for r in records) != summary["infrastructure_failures"]:
        raise ValueError("Failure count mismatch")
    print("Verified source record and artifact hashes; interpretation is not independently reviewed")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("probe")
    p.add_argument("--mode", choices=MODES, required=True)
    r = commands.add_parser("run")
    r.add_argument("--python", required=True)
    r.add_argument("--name", required=True)
    v = commands.add_parser("verify")
    v.add_argument("--name", required=True)
    args = parser.parse_args()
    if args.command == "probe":
        return probe(args.mode)
    if args.command == "run":
        return run(args.python, args.name)
    return verify(args.name)


if __name__ == "__main__":
    sys.exit(main())
