"""Stable entry point for deterministic migration checks."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import subprocess

from .common import REPO, git, print_json, protected_findings, read_json, safe_relative, sha256, write_json
from .environment import check_lock, inspect_environment
from .odf import extract_manifest, verify_manifest
from .latex import audit_latex
from .preservation import audit_conversion
from .coordination import checkpoint, resource_locks, run_task, scope_check
from .build import compile_profile
from .visual import prepare_visual


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Read-only preservation checks and isolated build harness; no converter")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("verify-source")
    inventory = commands.add_parser("inventory", help="Reextract the complete ODF manifest deterministically")
    inventory.add_argument("--check", action="store_true", help="Compare without writing the tracked manifest")
    commands.add_parser("doctor")
    latex = commands.add_parser("audit-latex")
    latex.add_argument("--root", required=True)
    latex.add_argument("--entry", default="main.tex")
    validate = commands.add_parser("validate")
    validate.add_argument("--ledger")
    validate.add_argument("--unit")
    build = commands.add_parser("build")
    build.add_argument("--profile", choices=["fixture", "template", "document"], default="document")
    visual = commands.add_parser("visual")
    visual.add_argument("--pdf", required=True)
    visual.add_argument("--dpi", type=int, default=100)
    for name in ("scope-check", "run-task"):
        scoped = commands.add_parser(name)
        scoped.add_argument("--role", choices=list(read_json(REPO / "harness.json")["roles"]), required=True)
        scoped.add_argument("--unit")
        if name == "scope-check":
            scoped.add_argument("--base", default="HEAD")
            scoped.add_argument("--end", help="Audit a sealed commit interval; exclude unrelated working-tree changes")
        else:
            scoped.add_argument("task_command", nargs=argparse.REMAINDER)
    point = commands.add_parser("checkpoint", help="Create a pending dossier, never an approval")
    point.add_argument("--unit", required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    config = read_json(REPO / "harness.json")
    execution = {"commit": git(REPO, "rev-parse", "HEAD"),
                 "branch": git(REPO, "rev-parse", "--abbrev-ref", "HEAD"),
                 "dirty": bool(git(REPO, "status", "--porcelain")),
                 "arguments": list(argv if argv is not None else sys.argv[1:]),
                 "manifest_sha256": sha256(REPO / config["manifest"]) if (REPO / config["manifest"]).is_file() else None,
                 "toolchain_lock_sha256": sha256(REPO / config["toolchain_lock"]) if (REPO / config["toolchain_lock"]).is_file() else None}
    try:
        if args.command == "verify-source":
            findings = protected_findings(REPO)
            report = {"status": "fail" if findings else "pass", "findings": findings,
                      "protected_files": len(read_json(REPO / "docs/BASELINE.json")["protected_files"])}
        elif args.command == "inventory":
            with resource_locks(["manifest"], repo=REPO):
                findings = protected_findings(REPO)
                if findings:
                    report = {"status": "fail", "findings": findings}
                else:
                    source = safe_relative(REPO, config["source"], must_exist=True)
                    path = safe_relative(REPO, config["manifest"])
                    if args.check:
                        differences = verify_manifest(read_json(path), source)
                        report = {"status": "fail" if differences else "pass", "findings": differences}
                    else:
                        manifest = extract_manifest(source, destination_root=config["destination_root"])
                        if path.exists():
                            overlay = read_json(path).get("migration_overlay")
                            if overlay is not None:
                                manifest["migration_overlay"] = overlay
                                if verify_manifest(manifest, source):
                                    raise ValueError("Existing migration overlay is inconsistent with the source; do not discard it")
                        write_json(path, manifest)
                        report = {"status": "pass", "manifest": config["manifest"],
                                  "records": len(manifest["records"]), "units": len(manifest["units"])}
        elif args.command == "doctor":
            report = inspect_environment()
            report["findings"] += check_lock(report, read_json(REPO / config["toolchain_lock"]))
            report["status"] = "fail" if report["findings"] else "pass"
            # The lock itself records the resource list; avoid repeating megabytes on stdout.
            report["cache_resource_count"] = len(report.pop("cache_resources"))
        elif args.command == "audit-latex":
            root = safe_relative(REPO, args.root, must_exist=True)
            report = audit_latex(root, safe_relative(root, args.entry, must_exist=True))
        elif args.command == "validate":
            manifest = read_json(REPO / config["manifest"])
            if args.unit is not None and args.unit not in {u["id"] for u in manifest["units"]}:
                raise ValueError("Unknown unit ID")
            differences = verify_manifest(manifest, REPO / config["source"])
            differences += protected_findings(REPO)
            if differences:
                report = {"status": "fail", "findings": differences}
            else:
                ledger = read_json(safe_relative(REPO, args.ledger, must_exist=True)) if args.ledger else {"schema_version": 1, "units": {}}
                report = audit_conversion(manifest, ledger, REPO, unit_id=args.unit)
                report["source_integrity"] = "pass"
                report["execution"] = execution
                write_json(REPO / "build/validation" / ((args.unit or "all") + "/report.json"), report)
        elif args.command == "build":
            with resource_locks(["build:" + args.profile, "latex-config", "integration"], repo=REPO):
                report = compile_profile(args.profile)
        elif args.command == "visual":
            with resource_locks(["visual"], repo=REPO):
                report = prepare_visual(args.pdf, dpi=args.dpi)
        elif args.command == "scope-check":
            report = scope_check(args.role, args.base, unit=args.unit, end=args.end)
        elif args.command == "run-task":
            command = args.task_command
            if command and command[0] == "--":
                command = command[1:]
            report = run_task(args.role, command, unit=args.unit)
        else:
            report = checkpoint(args.unit)
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        report = {"status": "fail", "findings": [{"severity": "error", "code": "HARNESS_ERROR", "message": str(error)}]}
    report["execution"] = execution
    print_json(report)
    return 0 if report["status"] == "pass" else 3 if report["status"] in {"unconverted", "partial", "pending_human_review", "pending_human_approval"} else 1


if __name__ == "__main__":
    sys.exit(main())
