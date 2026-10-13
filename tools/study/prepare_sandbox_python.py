"""Copy the existing host interpreter to a sandbox-readable local runtime."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    base = Path(sys.base_prefix)
    target = ROOT / "artifacts/runtime/python39"
    if sys.version_info[:2] != (3, 9) or sys.platform != "win32":
        raise RuntimeError("Use the existing Windows Python 3.9 interpreter")
    if target.exists():
        raise ValueError("Runtime exists; do not overwrite it")
    target.mkdir(parents=True)
    for name in ("python.exe", "pythonw.exe", "python39.dll", "python3.dll", "vcruntime140.dll", "vcruntime140_1.dll"):
        if (base / name).exists():
            shutil.copy2(base / name, target / name)
    shutil.copytree(base / "DLLs", target / "DLLs", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(base / "Lib", target / "Lib", ignore=shutil.ignore_patterns("site-packages", "__pycache__"))
    # Explicit isolated paths: same study packages, no user site or model runtime.
    paths = ["Lib", "DLLs", str(ROOT / "artifacts/venvs/study/Lib/site-packages"), ".", "import site"]
    (target / "python39._pth").write_text("\n".join(paths) + "\n", encoding="utf-8")
    # Isolated _pth normally omits the working directory. Restore it explicitly
    # for source-bound native project tests while keeping user site disabled.
    (target / "Lib/sitecustomize.py").write_text(
        "import os, sys\nsys.path.insert(0, os.getcwd())\n"
        "os.environ.setdefault('PYTEST_DISABLE_PLUGIN_AUTOLOAD', '1')\n", encoding="utf-8")
    version = subprocess.run([str(target / "python.exe"), "-c", "import sys,pytest,mock; print(sys.version); print(pytest.__version__)"],
                             capture_output=True, text=True, check=True).stdout.strip()
    files = {p.relative_to(target).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(target.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
    result = {"scope": "Copied existing host interpreter; no model inference or new Python download",
              "source_base": str(base), "runtime": target.relative_to(ROOT).as_posix(),
              "version_check": version, "files_sha256": files,
              "note": "Study site-packages remain external and separately inventoried; this is a Windows/Python 3.9 runtime deviation."}
    (target / "manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"runtime": result["runtime"], "files": len(files), "version_check": version}))


if __name__ == "__main__":
    main()
