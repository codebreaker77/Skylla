"""Development receiver filter: use actual MRO, retain shared class containers."""

import ast
import json
from pathlib import Path


def filter_candidates(source, candidates, mro):
    owners = {(c["module"], c["class"]) for c in mro}
    # Recover repeated self access paths whose first declaration was deduplicated
    # under a different class by the original generator.
    assigned = set()
    for relative in {c["source_file"] for c in candidates}:
        path = (source / relative).resolve()
        if not path.is_relative_to(source.resolve()):
            raise ValueError("Source path escapes snapshot")
        module = Path(relative).with_suffix("").as_posix().replace("/", ".")
        tree = ast.parse(path.read_bytes())
        for cls in tree.body:
            if not isinstance(cls, ast.ClassDef) or (module, cls.name) not in owners:
                continue
            for method in cls.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for node in ast.walk(method):
                        if isinstance(node, (ast.Assign, ast.AnnAssign)):
                            for target in node.targets if isinstance(node, ast.Assign) else [node.target]:
                                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                    assigned.add(target.attr)
    decisions, kept = [], []
    for candidate in candidates:
        if candidate["scope"] == "class":
            reason = "shared_class_container_retained"
        elif (candidate["module"], candidate["declaring_class"]) in owners:
            reason = "declaring_class_in_receiver_mro"
        elif candidate["attribute"] in assigned:
            reason = "same_access_assigned_in_receiver_source"
        else:
            reason = "unrelated_instance_declaration"
        keep = reason != "unrelated_instance_declaration"
        decisions.append({"candidate_id": candidate["id"], "keep": keep, "reason": reason})
        if keep:
            kept.append(candidate)
    return kept, decisions


if __name__ == "__main__":
    import argparse
    import importlib
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--class-name", required=True)
    args = parser.parse_args()
    source = Path(args.source).resolve()
    sys.path.insert(0, str(source))
    module = importlib.import_module(args.module)
    if not Path(module.__file__).resolve().is_relative_to(source):
        raise RuntimeError("Receiver imported outside pinned source")
    cls = getattr(module, args.class_name)
    print(json.dumps({"case": "tornado-6", "ready": True, "imported_pinned_source": True,
                      "mro": [{"module": c.__module__, "class": c.__name__} for c in cls.__mro__]}))
