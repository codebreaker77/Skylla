"""Bounded AST container-observation proposals; no reference outcomes or inference."""

import ast
import hashlib
from pathlib import Path

CONSTRUCTORS = {"dict", "list", "set", "deque", "WeakKeyDictionary", "WeakValueDictionary"}


def container_initializer(node):
    if isinstance(node, (ast.Dict, ast.List, ast.Set)):
        return True
    if isinstance(node, ast.Call):
        name = node.func.id if isinstance(node.func, ast.Name) else (
            node.func.attr if isinstance(node.func, ast.Attribute) else None)
        return name in CONSTRUCTORS
    return False


def propose(source, relative_files):
    """Use source-selected files; propose lengths of class and self containers."""
    candidates, seen = [], set()
    for relative in relative_files:
        path = (source / relative).resolve()
        if not path.is_relative_to(source.resolve()):
            raise ValueError("Source file escapes snapshot")
        raw = path.read_bytes()
        tree = ast.parse(raw, filename=relative)
        module = Path(relative).with_suffix("").as_posix().replace("/", ".")
        for cls in tree.body:
            if not isinstance(cls, ast.ClassDef):
                continue
            # Class attributes: direct declarations only. Instance attributes:
            # assignments in direct methods, excluding nested functions/classes.
            declarations = [(node, "class") for node in cls.body]
            for method in cls.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    def statements(nodes):
                        for node in nodes:
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                                continue
                            yield node
                            for field in ("body", "orelse", "finalbody"):
                                yield from statements(getattr(node, field, []))
                            for handler in getattr(node, "handlers", []):
                                yield from statements(handler.body)
                    declarations.extend((node, "instance") for node in statements(method.body))
            for node, scope in declarations:
                if not isinstance(node, (ast.Assign, ast.AnnAssign)) or not container_initializer(node.value):
                    continue
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if scope == "class" and isinstance(target, ast.Name):
                        attribute = target.id
                    elif (scope == "instance" and isinstance(target, ast.Attribute)
                          and isinstance(target.value, ast.Name) and target.value.id == "self"):
                        attribute = target.attr
                    else:
                        continue
                    if attribute.startswith("__"):
                        continue
                    key = (scope, module if scope == "class" else "", cls.name if scope == "class" else "", attribute)
                    if key in seen:
                        continue
                    seen.add(key)
                    candidates.append({"id": "candidate-%03d" % len(candidates), "scope": scope,
                                       "module": module, "declaring_class": cls.name, "attribute": attribute,
                                       "source_file": relative, "source_line": node.lineno,
                                       "source_sha256": hashlib.sha256(raw).hexdigest(),
                                       "extractor": "length", "reason": "Container initializer found in source AST"})
    return candidates
