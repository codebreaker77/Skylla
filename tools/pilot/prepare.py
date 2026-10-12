"""Download pinned source snapshots for the development rehearsal, without Git history."""

import argparse
import concurrent.futures
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import urllib.request


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "experiments/rehearsal/cases.json"


def prepare(case, variant, exclude_symlink_prefixes=()):
    commit = case[variant + "_commit"]
    target = ROOT / "artifacts/sources" / (case["id"] + "-" + variant)
    marker = target / ".skylla-source.json"
    if marker.exists():
        recorded = json.loads(marker.read_text(encoding="utf-8"))
        if recorded["commit"] != commit:
            raise ValueError("Cached source commit does not match manifest")
        if recorded.get("excluded_archive_prefixes", []) != list(exclude_symlink_prefixes):
            raise ValueError("Cached source export policy differs from requested policy")
        return recorded
    if target.exists():
        raise ValueError("Incomplete snapshot exists: " + str(target))
    repo = case["repository"].removeprefix("https://github.com/")
    url = "https://codeload.github.com/" + repo + "/tar.gz/" + commit
    request = urllib.request.Request(url, headers={"User-Agent": "Skylla-rehearsal"})
    with urllib.request.urlopen(request, timeout=90) as response:
        archive = response.read()
    records = []
    omitted = []
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
        for member in bundle.getmembers():
            parts = PurePosixPath(member.name).parts[1:]
            if not parts or member.isdir():
                continue
            if (member.issym() or member.islnk()) and any(
                    "/".join(parts).startswith(prefix) for prefix in exclude_symlink_prefixes):
                omitted.append("/".join(parts))
                continue
            if not member.isfile() or any(p in ("..", ".") or ":" in p for p in parts):
                raise ValueError("Unsupported archive entry: " + member.name)
            relative = Path(*parts)
            destination = target / relative
            if not destination.resolve().is_relative_to(target.resolve()):
                raise ValueError("Archive path escapes target")
            data = bundle.extractfile(member).read()
            records.append((destination, data))
    for destination, data in records:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    result = {
        "id": case["id"], "variant": variant, "commit": commit,
        "archive_url": url, "archive_sha256": hashlib.sha256(archive).hexdigest(),
        "files": len(records), "path": str(target.relative_to(ROOT)),
    }
    if exclude_symlink_prefixes:
        result.update(excluded_archive_prefixes=list(exclude_symlink_prefixes), omitted_links=omitted)
    marker.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("buggy", "fixed"), default="buggy")
    args = parser.parse_args()
    if args.variant == "fixed" and not (ROOT / "experiments/rehearsal/probes.json").exists():
        parser.error("Freeze development probe contracts before fetching reference fixes")
    cases = json.loads(MANIFEST.read_text(encoding="utf-8"))["cases"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(prepare, case, args.variant) for case in cases]
        for future in futures:
            print(json.dumps(future.result()))
