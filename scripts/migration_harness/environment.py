"""Inventory the real toolchain, and pin the cached resources used by builds."""
from __future__ import annotations

import importlib.metadata
from pathlib import Path
import platform
import shutil
import subprocess

from .common import sha256

REQUIRED = {"tectonic": "--version", "biber": "--version", "git": "--version",
            "pdfinfo": "-v", "pdftotext": "-v", "pdftoppm": "-v", "pdffonts": "-v"}
OPTIONAL = {"pandoc": "--version", "pdflatex": "--version", "xelatex": "--version",
            "lualatex": "--version", "bibtex": "--version", "latexmk": "--version",
            "libreoffice": "--version", "agy": "--version"}


def command_version(name: str, flag: str) -> dict:
    executable = shutil.which(name)
    if not executable:
        return {"available": False, "version": None}
    try:
        result = subprocess.run([executable, flag], capture_output=True, text=True,
                                timeout=15)
        lines = (result.stdout + result.stderr).strip().splitlines()
        return {"available": result.returncode == 0, "version": lines[0] if lines else None,
                "returncode": result.returncode}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"available": False, "version": None, "error": str(error)}


def tectonic_cache() -> Path:
    # Read the actual existing default cache; builds copy it to their own profile.
    return Path.home() / ".cache" / "tectonic"


def cache_resources() -> dict[str, str]:
    cache = tectonic_cache()
    if not cache.is_dir():
        return {}
    # Pin every seed resource, including cached formats, fonts and bundle indices.
    return {str(path.relative_to(cache)): sha256(path)
            for path in sorted(cache.rglob("*")) if path.is_file()}


def inspect_environment(*, include_resources: bool = True) -> dict:
    commands = {name: command_version(name, flag)
                for name, flag in {**REQUIRED, **OPTIONAL}.items()}
    libraries = {}
    for name in ("pypdf", "lxml", "Pillow", "odfpy"):
        try:
            libraries[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            libraries[name] = None
    findings = [{"severity": "error", "code": "TOOL_MISSING", "path": name,
                 "message": "Required command is unavailable"}
                for name in REQUIRED if not commands[name]["available"]]
    if not tectonic_cache().is_dir():
        findings.append({"severity": "error", "code": "CACHE_MISSING",
                         "message": "Offline Tectonic cache is unavailable"})
    return {"schema_version": 1, "python": platform.python_version(),
            "commands": commands, "python_libraries": libraries,
            "cache_resources": cache_resources() if include_resources else {},
            "status": "fail" if findings else "pass", "findings": findings}


def check_lock(actual: dict, expected: dict) -> list[dict]:
    findings = []
    for name in REQUIRED:
        current = actual["commands"].get(name, {}).get("version")
        locked = expected["commands"].get(name, {}).get("version")
        if current != locked:
            findings.append({"severity": "error", "code": "TOOLCHAIN_DRIFT",
                             "path": name, "expected": locked, "actual": current})
    if actual["python"] != expected["python"]:
        findings.append({"severity": "error", "code": "PYTHON_DRIFT",
                         "expected": expected["python"], "actual": actual["python"]})
    if actual["cache_resources"] != expected["cache_resources"]:
        changed = sorted(name for name in set(actual["cache_resources"]) |
                         set(expected["cache_resources"])
                         if actual["cache_resources"].get(name) !=
                         expected["cache_resources"].get(name))
        findings.append({"severity": "error", "code": "CACHE_DRIFT",
                         "message": "Cached build seed differs from lock", "paths": changed})
    return findings
