"""Read a decision request from JSON; no commands or remote models are executed."""

import argparse
import json
from pathlib import Path
import sys
from .decision import POLICIES, decide


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", help="JSON request path, or - for stdin")
    parser.add_argument("--policy", choices=POLICIES, default="conditional")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.request == "-" else Path(args.request).read_text(encoding="utf-8")
        print(json.dumps(decide(json.loads(raw), args.policy), indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
