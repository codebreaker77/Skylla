"""Execute frozen development probes; observations are not usefulness labels."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/expansion"
sys.path.insert(0, str(ROOT / "tools/pilot"))
from prepare import prepare
from run import fingerprint


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(CONFIG.resolve()):
        parser.error("Output must be inside experiments/expansion")
    output.mkdir(parents=True, exist_ok=False)
    contracts_path = CONFIG / "runtime/probes.json"
    contracts = json.loads(contracts_path.read_text(encoding="utf-8"))
    cases = json.loads((CONFIG / "screening/cases.json").read_text(encoding="utf-8"))["cases"]
    records = []
    with (output / "observations.jsonl").open("w", encoding="utf-8") as stream:
        for case in cases:
            if case["id"] not in contracts["cases"]:
                continue
            for variant in ("buggy", "fixed"):
                excluded = ("maint/test/appengine/",) if case["id"].startswith("tornado-") else ()
                source = prepare(case, variant, exclude_symlink_prefixes=excluded)
                for probe in contracts["cases"][case["id"]]["probes"]:
                    work_root = ROOT / "workspaces/runtime-probes"
                    work_root.mkdir(parents=True, exist_ok=True)
                    work = Path(tempfile.mkdtemp(prefix=case["id"] + "-", dir=work_root))
                    shutil.copytree(ROOT / source["path"], work, dirs_exist_ok=True)
                    shutil.copyfile(ROOT / "tools/study/probe_runtime.py", work / "probe_runtime.py")
                    state = fingerprint(work)
                    runtime = work / ".runtime"
                    runtime.mkdir()
                    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "PATH", "COMSPEC") if key in os.environ}
                    env.update({"HOME": str(runtime), "USERPROFILE": str(runtime), "TEMP": str(runtime),
                                "TMP": str(runtime), "PYTHONPATH": str(work), "PYTHONNOUSERSITE": "1",
                                "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8", "PYTHONHASHSEED": "0"})
                    argv = [sys.executable, "probe_runtime.py", "--case", case["id"], "--probe", probe["id"]]
                    start = time.perf_counter()
                    try:
                        process = subprocess.run(argv, cwd=work, env=env, capture_output=True, text=True,
                                                 encoding="utf-8", errors="replace", timeout=30)
                        stdout, stderr, code = process.stdout, process.stderr, process.returncode
                        try:
                            observed = json.loads(stdout.splitlines()[-1])
                            status = "observed" if code == 0 and "setup_failure" not in observed else "setup_failure"
                        except (ValueError, IndexError):
                            observed, status = None, "unexpected"
                    except subprocess.TimeoutExpired as error:
                        def decode(value):
                            return value.decode("utf-8", "replace") if isinstance(value, bytes) else (value or "")
                        stdout, stderr, code, observed, status = decode(error.stdout), decode(error.stderr), None, None, "timeout"
                    seconds = time.perf_counter() - start
                    log_root = ROOT / "artifacts/runtime-probes" / output.name
                    log_root.mkdir(parents=True, exist_ok=True)
                    log = log_root / (case["id"] + "-" + variant + "-" + probe["id"] + ".json")
                    log.write_text(json.dumps({"argv": argv, "cwd": str(work), "stdout": stdout, "stderr": stderr}, indent=2) + "\n", encoding="utf-8")
                    record = {"case": case["id"], "variant": variant, "probe": probe["id"],
                              "commit": source["commit"], "archive_sha256": source["archive_sha256"],
                              "state_id": state, "status": status, "exit_code": code,
                              "seconds": round(seconds, 6), "result": observed,
                              "raw_log": log.relative_to(ROOT).as_posix(),
                              "raw_log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}
                    records.append(record)
                    stream.write(json.dumps(record) + "\n")
                    stream.flush()
                    print(case["id"], variant, probe["id"], status, flush=True)
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True).stdout.splitlines()
    summary = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
               "packages": freeze, "runs": len(records),
               "purpose": "Development observations; no model, ranking, or repair comparison",
               "contract_sha256": hashlib.sha256(contracts_path.read_bytes()).hexdigest(),
               "implementation_sha256": hashlib.sha256((ROOT / "tools/study/probe_runtime.py").read_bytes()).hexdigest(),
               "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "total_execution_seconds": round(sum(record["seconds"] for record in records), 6)}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
