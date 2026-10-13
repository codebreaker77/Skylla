"""Verify pinned source/event/annotation lineage; optionally restore public raw data."""

from collections import Counter
import hashlib
import json
from pathlib import Path

from acquire_trajectory_audit import acquire
from extract_trajectory_audit import extract

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/trajectory-audit"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore", action="store_true", help="Download original public blobs into ignored local artifacts")
    args = parser.parse_args()
    sample = json.loads((CONFIG / "sample.json").read_text(encoding="utf-8"))
    acquisition = json.loads((CONFIG / "acquisition.json").read_text(encoding="utf-8"))
    events = json.loads((CONFIG / "events.json").read_text(encoding="utf-8"))
    audit = json.loads((CONFIG / "audit.json").read_text(encoding="utf-8"))
    comparison = json.loads((CONFIG / "next-comparison.json").read_text(encoding="utf-8"))
    require(digest(CONFIG / "NEXT_COMPARISON.md") == comparison["protocol_sha256"], "Frozen comparison design changed")
    require(digest(CONFIG / "audit.json") == comparison["audit_sha256"], "Comparison audit lineage changed")
    require(comparison["confirmation_exclusions"] == [case["instance_id"] for case in sample["cases"]], "Confirmation exclusion list differs")
    require(digest(CONFIG / "METHODOLOGY.md") == sample["method_sha256"], "Frozen method changed")
    require(digest(ROOT / "tools/study/acquire_trajectory_audit.py") == sample["acquisition_script_sha256"], "Frozen acquisition code changed")
    require(digest(CONFIG / "sample.json") == acquisition["sample_sha256"] == events["sample_sha256"], "Sample lineage mismatch")
    require(digest(CONFIG / "events.json") == audit["events_sha256"], "Reviewed events changed")
    require(digest(ROOT / "tools/study/extract_trajectory_audit.py") == events["extractor_sha256"], "Extractor changed")
    require(digest(ROOT / "tools/study/review_trajectory_audit.py") == audit["review_script_sha256"], "Review script changed")
    require(len(sample["cases"]) == 15, "Unexpected sample count")
    counts = Counter(case["repository_group"] for case in sample["cases"])
    require(dict(counts) == sample["repository_counts"] and max(counts.values()) <= 3, "Repository cap mismatch")
    acquired = {record["instance_id"]: record for record in acquisition["records"]}
    extracted = {trace["instance_id"]: trace for trace in events["traces"]}
    require(set(acquired) == set(extracted) == {case["instance_id"] for case in sample["cases"]}, "Missing trace disposition")
    local = 0
    for case in sample["cases"]:
        record = acquired[case["instance_id"]]
        if record["status"] != "downloaded":
            continue
        path = (ROOT / record["raw_path"]).resolve()
        require(path.is_relative_to((ROOT / "artifacts/trajectory-audit/raw").resolve()), "Unexpected raw path")
        if args.restore and not path.exists():
            restored = acquire(case)
            require(restored["sha256"] == record["sha256"], "Restored blob differs")
        if not path.exists():
            continue
        require(digest(path) == record["sha256"], "Changed raw source")
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == case["git_blob_sha1"], "Git blob identity mismatch")
        trace, _ = extract(case, path)
        require(trace == extracted[case["instance_id"]], "Extracted event differs from source")
        local += 1
    all_events = {event["event_id"]: event for trace in events["traces"] for event in trace["selected_candidates"]}
    annotations = audit["annotations"]
    require(len(annotations) == len(all_events) == audit["reviewed_candidates"], "Review count mismatch")
    require({item["event_id"] for item in annotations} == set(all_events), "Incomplete event review")
    for item in annotations:
        require(all(item[key] == value for key, value in all_events[item["event_id"]].items()), "Review identity mismatch")
    included = [item for item in annotations if item["included"]]
    require(len(included) == audit["included_runtime_events"], "Included count mismatch")
    require(dict(Counter(item["visible_outcome"] for item in included)) == audit["outcomes"], "Outcome count mismatch")
    require([item["event_id"] for item in included if item["exception_visible"] and item["return_code"] == 0] == audit["zero_exit_with_visible_exception"], "Zero-exit observation mismatch")
    print("Verified", len(sample["cases"]), "selected traces,", len(annotations), "reviews, and", local,
          "available raw blobs; labels remain single-reviewer judgments")
