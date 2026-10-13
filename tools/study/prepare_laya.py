"""Download one pinned public Laya checkpoint as data, validating LFS hashes."""

import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
REPO = "convaiinnovations/laya"
REVISION = "7b928d828b7b0e022f929d9bd2e44165aa270148"
SUBFOLDER = "typed-decisions"
DESTINATION = ROOT / "artifacts/laya-baseline/checkpoint"
MANIFEST = ROOT / "experiments/judge-baseline/laya-checkpoint.json"


def main():
    if MANIFEST.exists():
        raise ValueError("Checkpoint manifest already recorded")
    started = time.perf_counter()
    endpoint = "https://huggingface.co/api/models/" + REPO + "/tree/" + REVISION + "/" + SUBFOLDER + "?recursive=true"
    with urllib.request.urlopen(endpoint, timeout=30) as response:
        entries = json.load(response)
    records = []
    for entry in entries:
        if entry["type"] != "file":
            continue
        relative = Path(entry["path"]).relative_to(SUBFOLDER)
        target = (DESTINATION / relative).resolve()
        if not target.is_relative_to(DESTINATION.resolve()):
            raise ValueError("Unsafe model path")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            temporary = target.with_suffix(target.suffix + ".partial")
            url = "https://huggingface.co/" + REPO + "/resolve/" + REVISION + "/" + entry["path"] + "?download=true"
            request = urllib.request.Request(url, headers={"User-Agent": "Skylla-local-research"})
            with urllib.request.urlopen(request, timeout=30) as response, temporary.open("wb") as stream:
                downloaded = 0
                progress = -1
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    stream.write(chunk)
                    downloaded += len(chunk)
                    step = int(downloaded * 10 / entry["size"]) if entry["size"] else 10
                    if step > progress:
                        print(relative.as_posix(), step * 10, "percent", flush=True)
                        progress = step
            temporary.replace(target)
        digest = hashlib.sha256()
        with target.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        actual = digest.hexdigest()
        if target.stat().st_size != entry["size"]:
            raise ValueError("Checkpoint size mismatch")
        if entry.get("lfs") and actual != entry["lfs"]["oid"]:
            raise ValueError("Checkpoint LFS content mismatch")
        records.append({"path": relative.as_posix(), "bytes": entry["size"], "sha256": actual,
                        "source_blob_oid": entry["oid"], "lfs_sha256": entry.get("lfs", {}).get("oid")})
    result = {"schema_version": 1, "repo_id": REPO, "revision": REVISION, "subfolder": SUBFOLDER,
              "files": records, "download_and_verify_seconds": time.perf_counter() - started,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print("Pinned checkpoint verified; weights remain in ignored local artifacts")


if __name__ == "__main__":
    main()
