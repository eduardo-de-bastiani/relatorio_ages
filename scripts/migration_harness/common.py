"""Paths, serialization, and integrity checks shared by the harness."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True,
                            capture_output=True, check=True)
    return result.stdout.strip()


def safe_relative(repo: Path, name: str, *, must_exist: bool = False) -> Path:
    path = Path(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Expected a repository-relative path: {name}")
    resolved = (repo / path).resolve(strict=must_exist)
    if not resolved.is_relative_to(repo.resolve()):
        raise ValueError(f"Path escapes repository: {name}")
    return resolved


def require_work_branch(repo: Path = REPO) -> str:
    branch = git(repo, "symbolic-ref", "--short", "HEAD")
    if branch in {"main", "master"}:
        raise ValueError("Writes must run on a task branch, never main/master")
    return branch


def write_json(path: Path, data: dict, *, repo: Path = REPO) -> None:
    path = path.resolve()
    if path.is_relative_to(repo.resolve()):
        require_work_branch(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=path.parent, encoding="utf-8",
                                         delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def protected_findings(repo: Path = REPO) -> list[dict]:
    baseline = read_json(repo / "docs/BASELINE.json")
    findings = []
    for name, expected in baseline["protected_files"].items():
        try:
            path = safe_relative(repo, name, must_exist=True)
            actual = sha256(path)
        except (OSError, ValueError) as error:
            findings.append({"severity": "error", "code": "PROTECTED_FILE_MISSING",
                             "path": name, "message": str(error)})
            continue
        if actual != expected:
            findings.append({"severity": "error", "code": "PROTECTED_FILE_CHANGED",
                             "path": name, "expected": expected, "actual": actual})
    return findings


def print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
