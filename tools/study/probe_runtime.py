"""Original observational probes for three historical runtime cases."""

import argparse
import gc
import json
from pathlib import Path


def clock(probe):
    import tornado
    from tornado.ioloop import PeriodicCallback
    duration_sets = {"normal": [0, 0, 0, 0], "backward": [-1, -2, -3, 0],
                     "boundary": [0, -0.01, 0, 0.01], "overrun": [0, 15, 25, 0]}
    durations = duration_sets[probe]
    timer = PeriodicCallback(lambda: None, 10000)
    timer._next_timeout = 1000.0
    now, times = 1000.0, []
    for duration in durations:
        timer._update_next(now)
        times.append(timer._next_timeout)
        now = timer._next_timeout + duration
    return tornado, {"durations": durations, "next_times": times,
                     "strictly_increasing": all(left < right for left, right in zip(times, times[1:]))}


def cleanup(probe):
    import asyncio
    import tornado
    from tornado.ioloop import IOLoop
    from tornado.platform.asyncio import AsyncIOLoop
    start = len(IOLoop._ioloop_for_asyncio)
    closed = []
    count = 1 if probe == "single_close" else 10
    for _ in range(count):
        if probe == "asyncio_close":
            native = asyncio.new_event_loop()
            asyncio.set_event_loop(native)
            wrapper = IOLoop.current()
            native.close()
            closed.append(native.is_closed())
        else:
            wrapper = AsyncIOLoop()
            native = wrapper.asyncio_loop
            wrapper.close()
            closed.append(native.is_closed())
        del wrapper, native
    before_gc = len(IOLoop._ioloop_for_asyncio) - start
    if probe == "gc":
        gc.collect()
    return tornado, {"cycles": count, "all_native_loops_closed": all(closed),
                     "mapping_delta_before_gc": before_gc,
                     "mapping_delta_after": len(IOLoop._ioloop_for_asyncio) - start}


def scheduler(probe):
    import luigi
    from luigi.scheduler import Scheduler, UNKNOWN, PENDING, DONE, RUNNING
    cases = {"owners": [("X", UNKNOWN, "A", False), ("Y", UNKNOWN, "A", False)],
             "identity": [("Y", UNKNOWN, "A", False), ("Y", UNKNOWN, "B", False)],
             "statuses": [("Y", value, "A", False) for value in (UNKNOWN, PENDING, DONE)],
             "sequence": [("Y", UNKNOWN, "A", True), ("Y", UNKNOWN, "A", False)]}[probe]
    observations = []
    for actor, status, task, before_claim in cases:
        instance = Scheduler()
        instance.add_task(worker="X", task_id="A")
        if before_claim:
            instance.add_task(worker=actor, task_id=task, status=status)
        claim = instance.get_work(worker="X")
        before = sorted(instance.task_list(RUNNING, "").keys())
        if not before_claim:
            instance.add_task(worker=actor, task_id=task, status=status)
        observations.append({"actor": actor, "reported_status": status, "updated_task": task,
                             "update_before_claim": before_claim, "claimed_task": claim["task_id"],
                             "running_before_update": before,
                             "running_after_update": sorted(instance.task_list(RUNNING, "").keys())})
    return luigi, {"updates": observations}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--probe", required=True)
    args = parser.parse_args()
    try:
        function = {"tornado-5": clock, "tornado-6": cleanup, "luigi-7": scheduler}[args.case]
        module, observation = function(args.probe)
        imported_local = Path(module.__file__).resolve().is_relative_to(Path.cwd().resolve())
        if not imported_local:
            raise RuntimeError("Imported module is not from the pinned workspace")
        print(json.dumps({"case": args.case, "probe": args.probe,
                          "preconditions": {"imported_pinned_source": imported_local},
                          "observation": observation}))
    except Exception as error:
        print(json.dumps({"case": args.case, "probe": args.probe,
                          "setup_failure": type(error).__name__ + ": " + str(error)}))
        raise SystemExit(2)
