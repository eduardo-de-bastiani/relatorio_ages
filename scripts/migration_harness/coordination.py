"""Cooperative ownership checks and task locks; never a security sandbox."""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
from fnmatch import fnmatchcase
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile

from .common import REPO, git, protected_findings, read_json, require_work_branch, sha256, write_json


def changed_paths(repo: Path, base: str) -> list[str]:
    git(repo, "rev-parse", "--verify", base + "^{commit}")
    tracked = subprocess.check_output(["git", "-C", str(repo), "diff", "--name-only", "-z", base])
    untracked = subprocess.check_output(["git", "-C", str(repo), "ls-files", "--others", "--exclude-standard", "-z"])
    return sorted(set(p.decode() for p in (tracked + untracked).split(b"\0") if p))


def scope_check(role: str, base: str, *, unit: str | None = None, repo: Path = REPO) -> dict:
    config = read_json(repo / "harness.json")
    patterns = list(config["roles"][role]["write"])
    if role == "converter" and not unit:
        raise ValueError("Converter scope requires an assigned unit")
    if role == "converter" and unit:
        manifest = read_json(repo / config["manifest"])
        selected = next((u for u in manifest["units"] if u["id"] == unit), None)
        if selected is None:
            raise ValueError("Unknown unit: " + unit)
        destination = selected["destination"]
        patterns.append(destination if isinstance(destination, str) else destination["path"])
        patterns.append(f"migration/ledgers/{unit}.json")
    changed = changed_paths(repo, base)
    baseline = read_json(repo / "docs/BASELINE.json")
    forbidden = []
    for path in changed:
        allowed = any(fnmatchcase(path, pattern) for pattern in patterns)
        if path in baseline["protected_files"]:
            allowed = False
        if path == config["manifest"] and role != "extractor":
            allowed = False
        if config["phase"] == "harness" and path.startswith(config["destination_root"] + "/"):
            allowed = False
        if not allowed:
            forbidden.append(path)
    return {"status": "fail" if forbidden else "pass", "role": role, "unit": unit,
            "base": git(repo, "rev-parse", base), "changed_paths": changed,
            "forbidden_paths": forbidden, "cooperative_only": True}


@contextmanager
def resource_locks(resources: list[str], *, repo: Path = REPO):
    common = Path(git(repo, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = repo / common
    identity = hashlib.sha256(str(common.resolve()).encode()).hexdigest()
    # A trusted child command may invoke the CLI while run-task owns the same
    # lock. The parent retains the actual flock throughout the child lifetime.
    inherited = set()
    try:
        lease = json.loads(os.environ.get("AGES_HARNESS_LOCK_LEASE", "{}"))
        if lease.get("identity") == identity and lease.get("pid") == os.getppid():
            inherited = set(lease.get("resources", []))
    except (ValueError, TypeError):
        pass
    directory = Path(tempfile.gettempdir()) / ("ages-harness-locks-" + identity)
    directory.mkdir(mode=0o700, exist_ok=True)
    handles = []
    try:
        for resource in sorted(set(resources)):
            if resource in inherited:
                continue
            path = directory / hashlib.sha256(resource.encode()).hexdigest()
            stream = path.open("a+")
            handles.append(stream)
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise ValueError("Resource already owned: " + resource) from error
        yield {"identity": identity, "pid": os.getpid(), "resources": sorted(set(resources) | inherited)}
    finally:
        for stream in reversed(handles):
            fcntl.flock(stream, fcntl.LOCK_UN)
            stream.close()


def run_task(role: str, command: list[str], *, unit: str | None = None, repo: Path = REPO) -> dict:
    initial_branch = require_work_branch(repo)
    config = read_json(repo / "harness.json")
    if not command:
        raise ValueError("Provide a trusted command after --")
    if role in {"converter", "latex-maintainer"} and config["phase"] == "harness":
        raise ValueError("Content conversion and global LaTeX edits are not authorized in harness phase")
    if role == "converter":
        if not unit:
            raise ValueError("Converter requires an assigned unit")
        scope_check(role, "HEAD", unit=unit, repo=repo)
    if protected_findings(repo):
        raise ValueError("Protected source integrity failed")
    # Existing changes would make post-task attribution ambiguous.
    if git(repo, "status", "--porcelain"):
        raise ValueError("run-task requires a clean dedicated branch/worktree")
    base = git(repo, "rev-parse", "HEAD")
    resources = [r.replace("{unit}", unit or "UNASSIGNED") for r in config["roles"][role]["locks"]]
    with resource_locks(resources, repo=repo) as lease:
        env = os.environ.copy()
        env["AGES_HARNESS_LOCK_LEASE"] = json.dumps(lease)
        result = subprocess.run(command, cwd=repo, env=env, check=False)
        current_branch = require_work_branch(repo)
        if current_branch != initial_branch:
            raise ValueError("Task changed its assigned branch")
        scope = scope_check(role, base, unit=unit, repo=repo)
        findings = protected_findings(repo)
        return {"status": "pass" if result.returncode == 0 and scope["status"] == "pass" and not findings else "fail",
                "command": command, "returncode": result.returncode, "scope": scope,
                "protected_findings": findings, "rollback": "Inspect diff; do not auto-reset"}


def checkpoint(unit: str, *, repo: Path = REPO) -> dict:
    require_work_branch(repo)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", unit):
        raise ValueError("Invalid unit identifier")
    config = read_json(repo / "harness.json")
    manifest = read_json(repo / config["manifest"])
    if unit not in {u["id"] for u in manifest["units"]}:
        raise ValueError("Unknown unit: " + unit)
    reports = {str(p.relative_to(repo)): sha256(p) for p in sorted((repo / "build").rglob("report.json"))}
    dossier = {"schema_version": 1, "unit": unit, "status": "pending_human_approval",
               "commit": git(repo, "rev-parse", "HEAD"), "dirty": bool(git(repo, "status", "--porcelain")),
               "source_sha256": sha256(repo / config["source"]), "reports": reports,
               "approval": None, "pilot_authorized": False,
               "notice": "A generated dossier never constitutes user authorization"}
    write_json(repo / "build/checkpoints" / (unit + ".json"), dossier, repo=repo)
    return dossier
