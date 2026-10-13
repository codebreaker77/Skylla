"""Pin a public trajectory sample before content inspection, then download as data."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import base64
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/trajectory-audit"
ASSET_REPO = "SWE-bench/20260901_mini-v2.4.2_gemini-3-5-flash"
ASSET_COMMIT = "2f6637a2557da1f7b5f2b583ab7090a077bbeed2"
REGISTRY_COMMIT = "40f164d5b8f1d249bf95a6df8b74b577fd8e519d"
SEED = "skylla-observation-audit-v1"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")


def select():
    manifest = CONFIG / "sample.json"
    if manifest.exists():
        raise ValueError("Sample already frozen; do not replace it")
    tree = json.loads((ROOT / "artifacts/trajectory-audit/discovery/tree.json").read_text(encoding="utf-8"))
    if tree["truncated"]:
        raise ValueError("Incomplete inventory")
    candidates = [item for item in tree["tree"] if item["type"] == "blob"
                  and item["path"].startswith("trajs/") and item["path"].endswith(".traj.json")]
    ordered = sorted(candidates, key=lambda item: hashlib.sha256((SEED + "|" + item["path"]).encode()).hexdigest())
    cases, counts = [], {}
    for item in ordered:
        instance = Path(item["path"]).name.removesuffix(".traj.json")
        group = instance.rsplit("-", 1)[0]
        if counts.get(group, 0) >= 3:
            continue
        counts[group] = counts.get(group, 0) + 1
        cases.append({"instance_id": instance, "repository_group": group, "path": item["path"],
                      "git_blob_sha1": item["sha"], "bytes": item["size"],
                      "source_url": "https://github.com/" + ASSET_REPO + "/blob/" + ASSET_COMMIT + "/" + item["path"]})
        if len(cases) == 15:
            break
    inventory = [{"path": item["path"], "sha": item["sha"], "size": item["size"]}
                 for item in sorted(candidates, key=lambda item: item["path"])]
    payload = {"schema_version": 1, "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
               "purpose": "Public development trajectory audit; not unseen confirmation data",
               "registry_repo": "SWE-bench/experiments", "registry_commit": REGISTRY_COMMIT,
               "submission": "20260901_mini-v2.4.2_gemini-3-5-flash",
               "asset_repo": ASSET_REPO, "asset_commit": ASSET_COMMIT, "asset_tree_sha1": tree["sha"],
               "inventory_trajectories": len(candidates),
               "inventory_sha256": hashlib.sha256(json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
               "selection": "Ascending SHA256(seed|path); first 15 with at most three per repository; no outcome/content filtering",
               "seed": SEED, "repository_counts": counts, "cases": cases,
               "method_sha256": digest(CONFIG / "METHODOLOGY.md"), "acquisition_script_sha256": digest(Path(__file__))}
    write_json(manifest, payload)
    print("Frozen", len(cases), "traces across", len(counts), "repositories before downloading their contents")


def acquire(case):
    target = ROOT / "artifacts/trajectory-audit/raw" / (case["instance_id"] + ".traj.json")
    if not target.exists():
        endpoint = "https://api.github.com/repos/" + ASSET_REPO + "/git/blobs/" + case["git_blob_sha1"]
        request = urllib.request.Request(endpoint, headers={"User-Agent": "Skylla-public-trajectory-audit"})
        with urllib.request.urlopen(request, timeout=45) as response:
            payload = json.load(response)
        if payload.get("encoding") != "base64":
            raise ValueError("Unexpected Git blob encoding")
        data = base64.b64decode(payload["content"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    data = target.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if blob != case["git_blob_sha1"] or len(data) != case["bytes"]:
        raise ValueError("Public artifact changed: " + case["instance_id"])
    parsed = json.loads(data)
    return {"instance_id": case["instance_id"], "raw_path": target.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "top_level_fields": sorted(parsed), "messages": len(parsed.get("messages", [])), "status": "downloaded"}


def download():
    sample = json.loads((CONFIG / "sample.json").read_text(encoding="utf-8"))
    if digest(CONFIG / "METHODOLOGY.md") != sample["method_sha256"] or digest(Path(__file__)) != sample["acquisition_script_sha256"]:
        raise ValueError("Frozen acquisition method changed")
    def safe(case):
        try:
            return acquire(case)
        except Exception as error:
            return {"instance_id": case["instance_id"], "status": "download_failed", "error": type(error).__name__ + ": " + str(error)}
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(safe, sample["cases"]))
    path = CONFIG / "acquisition.json"
    if path.exists():
        raise ValueError("Acquisition record exists; preserve it and use an explicitly versioned retry")
    write_json(path, {"sample_sha256": digest(CONFIG / "sample.json"), "downloaded_at_utc": datetime.now(timezone.utc).isoformat(), "records": records})
    print(json.dumps([{key: value for key, value in record.items() if key not in ("raw_path", "sha256")}
                      for record in records], indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("select", "download"))
    args = parser.parse_args()
    select() if args.operation == "select" else download()
