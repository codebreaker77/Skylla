"""Small, original observational probes for the development rehearsal."""

import argparse
import html
import io
import json
from pathlib import Path
import sys


def attempt(label, function):
    try:
        return {"input": label, "value": function(), "status": "observed"}
    except Exception as error:
        return {"input": label, "status": "exception", "type": type(error).__name__,
                "message": str(error)}


def tqdm_probe(probe):
    from tqdm import tqdm
    format_meter = tqdm.format_meter
    if probe == "width":
        settings = [{"ncols": n, "bar_format": "************{bar}$$$$$$$$$$"}
                    for n in (0, 2, 10, 20, 30, 40)]
    elif probe == "encoding":
        settings = [{"ncols": 40, "prefix": prefix}
                    for prefix in ("plain", "\033[31mplain\033[0m", "\u5168\u89d2")]
    elif probe == "format":
        settings = [{"ncols": 20, "bar_format": value}
                    for value in (None, "{l_bar}{bar}{r_bar}", "{bar}", "{r_bar}")]
    else:
        return [attempt(values, lambda values=values: format_meter(*values, ncols=40))
                for values in ((0, 100, 1), (20, 100, 12), (100, 100, 12), (101, 100, 12))]
    return [attempt(setting, lambda setting=setting: format_meter(20, 100, 12, **setting))
            for setting in settings]


def traced_function(value):
    result = value + "!"
    return result


def trace_to(destination, value="plain"):
    import pysnooper
    original = sys.gettrace()
    try:
        result = pysnooper.snoop(destination)(traced_function)(value)
        return {"return": result, "trace_restored": sys.gettrace() is original}
    finally:
        sys.settrace(original)


def pysnooper_probe(probe):
    path = Path("probe-output.log")
    if probe == "destinations":
        stream = io.StringIO()
        return [attempt("StringIO", lambda: trace_to(stream)),
                attempt("path", lambda: trace_to(str(path))),
                attempt("stderr", lambda: trace_to(None))]
    if probe == "file_state":
        writable = Path("writable-control.txt")
        writable.write_text("writeability verified", encoding="utf-8")
        absent = attempt("absent path", lambda: trace_to(str(path)))
        path.write_text("existing file", encoding="utf-8")
        existing = attempt("existing path", lambda: trace_to(str(path)))
        return [absent, existing]
    if probe == "text":
        return [attempt(value, lambda value=value: trace_to(str(path), value))
                for value in ("plain", "\u4f60\u597d")]
    stream = io.StringIO()
    return [attempt("undecorated", lambda: traced_function("plain")),
            attempt("decorated", lambda: trace_to(stream)),
            {"trace_output_nonempty": bool(stream.getvalue())}]


def youtube_probe(probe):
    from youtube_dl.utils import unescapeHTML
    inputs = {
        "classes": ["&amp;", "&quot;", "&#47;", "&#x2F;", "&unknown;"],
        "composition": ["&amp;", "&quot;", "&amp;&quot;", "a&b&quot;c", "&unknown;&amp;"],
        "boundaries": ["&amp;", "&amp", "&amp;text", "x&y&amp;", "&&amp;"],
        "levels": ["&amp;quot;", "&amp;amp;", "&amp;#47;", "&amp;&quot;"],
    }[probe]
    observations = []
    for value in inputs:
        result = attempt(value, lambda value=value: unescapeHTML(value))
        # Stdlib behavior is a comparator, not the project's specification.
        result["stdlib_comparator"] = html.unescape(value)
        if probe == "levels" and result["status"] == "observed":
            result["second_application"] = attempt(result["value"],
                                                     lambda: unescapeHTML(result["value"]))
        observations.append(result)
    return observations


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--probe", required=True)
    args = parser.parse_args()
    function = {"tqdm-2": tqdm_probe, "pysnooper-3": pysnooper_probe,
                "youtube-dl-3": youtube_probe}[args.case]
    try:
        payload = {"case": args.case, "probe": args.probe,
                   "observations": function(args.probe)}
    except Exception as error:
        payload = {"case": args.case, "probe": args.probe,
                   "setup_failure": type(error).__name__ + ": " + str(error)}
        print(json.dumps(payload))
        raise SystemExit(2)
    print(json.dumps(payload))
