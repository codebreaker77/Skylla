"""Read proposed container lengths around known development operations."""

import argparse
import importlib
import json
from pathlib import Path


def imported(module):
    return Path(module.__file__).resolve().is_relative_to(Path.cwd().resolve())


def snapshot(wrapper, candidates):
    results = {}
    for item in candidates:
        try:
            if item["scope"] == "class":
                module = importlib.import_module(item["module"])
                if not imported(module):
                    raise RuntimeError("Candidate module outside workspace")
                owner = getattr(module, item["declaring_class"])
            else:
                owner = wrapper
            value = getattr(owner, item["attribute"])
            results[item["id"]] = {"status": "observed", "length": len(value)}
        except Exception as exc:
            results[item["id"]] = {"status": "unavailable", "error_type": type(exc).__name__}
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("tornado-6", "luigi-7"), required=True)
    parser.add_argument("--readiness", action="store_true")
    parser.add_argument("--candidates")
    parser.add_argument("--arm", choices=("normalize", "source_containers"), default="normalize")
    parser.add_argument("--cycles", type=int, default=1)
    args = parser.parse_args()
    if args.case == "luigi-7":
        import luigi
        from luigi.scheduler import Scheduler, UNKNOWN, RUNNING
        if not imported(luigi):
            raise RuntimeError("Luigi import outside pinned workspace")
        if args.readiness:
            print(json.dumps({"case": args.case, "ready": True, "imported_pinned_source": True}))
            return
        scheduler = Scheduler()
        scheduler.add_task(worker="X", task_id="A")
        claimed = scheduler.get_work(worker="X")["task_id"]
        before = sorted(scheduler.task_list(RUNNING, "").keys())
        scheduler.add_task(worker="Y", task_id="A", status=UNKNOWN)
        after = sorted(scheduler.task_list(RUNNING, "").keys())
        print(json.dumps({"case": args.case, "imported_pinned_source": True,
                          "observation": {"claimed": claimed, "running_before": before, "running_after": after}}))
        return
    import tornado
    from tornado.platform.asyncio import AsyncIOLoop
    if not imported(tornado):
        raise RuntimeError("Tornado import outside pinned workspace")
    if args.readiness:
        loop = AsyncIOLoop()
        loop.close()
        print(json.dumps({"case": args.case, "ready": True, "imported_pinned_source": True}))
        return
    if args.cycles <= 0:
        raise ValueError("Cycles must be positive")
    candidates = json.loads(Path(args.candidates).read_text(encoding="utf-8"))["candidates"] if args.arm == "source_containers" else []
    before = snapshot(None, [c for c in candidates if c["scope"] == "class"])
    observations = []
    for _ in range(args.cycles):
        wrapper = AsyncIOLoop()
        native = wrapper.asyncio_loop
        active = snapshot(wrapper, candidates)
        wrapper.close()
        closed = snapshot(wrapper, candidates)
        observations.append({"native_closed": native.is_closed(), "active": active, "closed": closed})
        del wrapper, native
    after = snapshot(None, [c for c in candidates if c["scope"] == "class"])
    print(json.dumps({"case": args.case, "imported_pinned_source": True,
                      "observation": {"cycles": args.cycles, "before": before,
                                      "events": observations, "after": after}}))


if __name__ == "__main__":
    main()
