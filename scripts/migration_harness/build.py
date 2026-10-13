"""Compile in an isolated copy; never write auxiliary files into sources."""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from .common import REPO, git, read_json, require_work_branch, sha256, write_json, protected_findings
from .environment import check_lock, inspect_environment, tectonic_cache
from .latex import audit_latex

PROFILE_ROOTS = {"template": "Template_AGES___Guvidaletti",
                 "fixture": "harness/fixtures/latex",
                 "document": "relatorio_AGES_eduardo"}
GENERATED = {".aux", ".bbl", ".bcf", ".blg", ".log", ".toc", ".lof", ".lot",
             ".out", ".xdv", ".synctex", ".fls", ".fdb_latexmk"}


def audit_log(log: str, *, returncode: int = 0, biber_log: str = "", compiler_output: str = "") -> dict:
    findings = []
    if returncode:
        findings.append({"severity": "error", "code": "COMPILE_FAILED",
                         "message": f"Compiler exit code: {returncode}"})
    rules = [
        ("TEX_ERROR", r"^!\s|^error:", "error"),
        ("UNDEFINED_REFERENCE", r"Reference .* undefined|undefined references", "error"),
        ("UNDEFINED_CITATION", r"Citation .* undefined|undefined citations", "error"),
        ("MISSING_GLYPH", r"Missing character:|could not represent character", "error"),
        ("FONT_UNAVAILABLE", r"not loadable:|Font shape .*undefined", "error"),
        ("EMPTY_BIBLIOGRAPHY", r"Empty bibliography", "error"),
        ("RERUN_REQUIRED", r"Please \(re\)run Biber|Please rerun LaTeX|Rerun to get", "error"),
        ("DUPLICATE_LABEL", r"multiply defined|already defined", "error"),
        ("OVERFULL", r"Overfull \\[hv]box", "error"),
        ("UNDERFULL", r"Underfull \\[hv]box", "warning"),
        ("PACKAGE_WARNING", r"(?:Package|Class|LaTeX).* Warning:", "warning"),
    ]
    for number, line in enumerate(log.splitlines(), 1):
        for code, pattern, severity in rules:
            if re.search(pattern, line, flags=re.I):
                findings.append({"severity": severity, "code": code,
                                 "line": number, "message": line.strip()})
                break
    for number, line in enumerate(biber_log.splitlines(), 1):
        if re.search(r"\b(?:ERROR|WARN)\b|not found", line):
            findings.append({"severity": "error", "code": "BIBER_DIAGNOSTIC",
                             "line": number, "message": line.strip()})
    # PDF-backend diagnostics are outside the final TeX log. Do not mix
    # transient first-pass reference warnings into final reference checking.
    for number, line in enumerate(compiler_output.splitlines(), 1):
        if re.search(r"Object .*already defined|duplicate destination|destination .*same identifier|xdvipdfmx.*warning|^error:", line, re.I):
            findings.append({"severity": "error", "code": "PDF_BACKEND_DIAGNOSTIC",
                             "line": number, "message": line.strip()})
    return {"status": "fail" if findings else "pass", "findings": findings,
            "warning_policy": "unreviewed warnings block acceptance"}


def _copy_sources(source: Path, destination: Path) -> None:
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        if path.is_symlink():
            raise ValueError(f"Source symlinks must be reviewed: {path}")
        relative = path.relative_to(source)
        if any(part in {".git", "build", "__pycache__"} for part in relative.parts):
            continue
        if path.suffix in GENERATED or path.name.endswith(".run.xml"):
            continue
        if path.name == "main.pdf":
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def compile_profile(profile: str, *, repo: Path = REPO, check_toolchain: bool = True,
                    timeout: int = 180) -> dict:
    branch = require_work_branch(repo)
    output = repo / "build" / profile
    output.mkdir(parents=True, exist_ok=True)
    # Invalidate every artifact before even preflight: a failed attempt must
    # never leave an old PASS/PDF mistaken for its own result.
    for name in ("main.pdf", "main.log", "main.blg", "main.bbl", "main.toc",
                 "main.lof", "main.lot", "main.bcf", "main.aux", "main.out", "main.run.xml", "report.json", "compiler.txt"):
        (output / name).unlink(missing_ok=True)

    def preflight_report(status, findings):
        report = {"schema_version": 1, "status": status, "profile": profile,
                  "findings": findings, "pdf": None, "pdf_sha256": None,
                  "commit": git(repo, "rev-parse", "HEAD"), "branch": branch,
                  "memorial_migrated": False, "is_document_profile": profile == "document"}
        write_json(output / "report.json", report, repo=repo)
        return report

    protected = protected_findings(repo)
    if protected:
        return preflight_report("fail", protected)
    source = repo / PROFILE_ROOTS[profile]
    if not (source / "main.tex").is_file():
        return preflight_report("unconverted", [{"severity": "error", "code": "DOCUMENT_NOT_CREATED",
                                                  "message": "No memorial has been migrated"}])
    if profile == "document" and git(repo, "status", "--porcelain"):
        return preflight_report("fail", [{"severity": "error", "code": "UNCOMMITTED_DOCUMENT",
                                           "message": "Freeze the document/ledger in a task commit before a production build"}])
    actual = inspect_environment()
    findings = actual["findings"]
    if check_toolchain:
        findings += check_lock(actual, read_json(repo / "docs/TOOLCHAIN.lock.json"))
    if findings:
        return preflight_report("fail", findings)
    structure = audit_latex(source, source / "main.tex")
    if structure["status"] != "pass":
        return preflight_report("fail", structure["findings"])
    fingerprints = {str(p.relative_to(source)): sha256(p) for p in sorted(source.rglob("*"))
                    if p.is_file() and p.suffix not in GENERATED and p.name != "main.pdf"}
    with tempfile.TemporaryDirectory(prefix="ages-compile-") as temporary:
        isolated = Path(temporary)
        work = isolated / "source"
        work.mkdir()
        _copy_sources(source, work)
        cache = isolated / "cache"
        shutil.copytree(tectonic_cache(), cache / "tectonic")
        env = os.environ.copy()
        env.update({"XDG_CACHE_HOME": str(cache), "TECTONIC_CACHE_DIR": str(cache / "tectonic"),
                    "TMPDIR": str(isolated), "SOURCE_DATE_EPOCH": str(read_json(repo / "docs/BASELINE.json")["source_date_epoch"]),
                    "FORCE_SOURCE_DATE": "1", "TZ": "UTC"})
        command = ["tectonic", "--only-cached", "--untrusted", "--keep-intermediates",
                   "--keep-logs", "main.tex"]
        try:
            result = subprocess.run(command, cwd=work, env=env, text=True,
                                    capture_output=True, timeout=timeout)
            chatter = result.stdout + result.stderr
            returncode = result.returncode
        except subprocess.TimeoutExpired as error:
            chatter = "Compilation timed out"
            returncode = 124
        log = (work / "main.log").read_text(errors="replace") if (work / "main.log").exists() else ""
        blg = (work / "main.blg").read_text(errors="replace") if (work / "main.blg").exists() else ""
        diagnostics = audit_log(log, returncode=returncode, biber_log=blg, compiler_output=chatter)
        # XeTeX final log and Biber final log are authoritative after all passes.
        if not log:
            diagnostics = audit_log(chatter, returncode=returncode, biber_log=blg)
        uses_biblatex = any("\\usepackage" in p.read_text(errors="replace") and
                            "biblatex" in p.read_text(errors="replace") for p in work.rglob("*.tex"))
        if uses_biblatex and not (work / "main.bbl").exists():
            diagnostics["findings"].append({"severity": "error", "code": "BIBLIOGRAPHY_NOT_PROCESSED",
                                             "message": "No Biber output from clean build"})
            diagnostics["status"] = "fail"
        for name in ("main.pdf", "main.log", "main.blg", "main.bbl", "main.toc", "main.lof", "main.lot", "main.bcf", "main.aux", "main.out", "main.run.xml"):
            path = work / name
            if path.exists():
                shutil.copyfile(path, output / name)
        (output / "compiler.txt").write_text(chatter, encoding="utf-8")
    report = {**diagnostics, "schema_version": 1, "profile": profile,
              "commit": git(repo, "rev-parse", "HEAD"), "branch": branch,
              "dirty": bool(git(repo, "status", "--porcelain")),
              "memorial_migrated": False, "is_document_profile": profile == "document", "returncode": returncode,
              "command": command, "source_files": fingerprints,
              "source_date_epoch": read_json(repo / "docs/BASELINE.json")["source_date_epoch"],
              "toolchain_lock_sha256": sha256(repo / "docs/TOOLCHAIN.lock.json"),
              "pdf": str((output / "main.pdf").relative_to(repo)) if (output / "main.pdf").exists() else None,
              "pdf_sha256": sha256(output / "main.pdf") if (output / "main.pdf").exists() else None,
              "visual_review": "pending_human_review"}
    report["artifacts"] = {p.name: sha256(p) for p in sorted(output.iterdir()) if p.is_file()}
    after = protected_findings(repo)
    report["findings"].extend(after)
    if after or report["pdf"] is None:
        report["status"] = "fail"
    write_json(output / "report.json", report, repo=repo)
    return report
