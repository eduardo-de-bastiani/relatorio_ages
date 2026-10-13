"""Generate page images and evidence for a human visual audit."""
from __future__ import annotations

from pathlib import Path
import subprocess

from .common import REPO, git, safe_relative, sha256, write_json, require_work_branch


def prepare_visual(pdf: str, *, repo: Path = REPO, dpi: int = 100) -> dict:
    require_work_branch(repo)
    source = safe_relative(repo, pdf, must_exist=True)
    if source.suffix.lower() != ".pdf" or not 50 <= dpi <= 200:
        raise ValueError("Expected a PDF and DPI between 50 and 200")
    digest = sha256(source)
    output = repo / "build/visual" / digest[:16]
    output.mkdir(parents=True, exist_ok=True)
    evidence = {}
    commands = [["pdfinfo", "-box", str(source)], ["pdffonts", str(source)],
                ["pdftotext", "-layout", str(source), str(output / "text.txt")],
                ["pdftoppm", "-png", "-r", str(dpi), str(source), str(output / "page")]]
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True, timeout=180)
        evidence[command[0]] = {"command": command, "returncode": result.returncode,
                                "stdout": result.stdout, "stderr": result.stderr}
        if result.returncode:
            raise ValueError(f"{command[0]} failed: {result.stderr}")
    links = []
    try:
        from pypdf import PdfReader
        reader = PdfReader(source)
        for number, page in enumerate(reader.pages, 1):
            for annotation in page.get("/Annots", []):
                obj = annotation.get_object()
                action = obj.get("/A", {})
                if action.get("/URI"):
                    links.append({"page": number, "uri": str(action["/URI"]), "rect": list(obj.get("/Rect", []))})
    except ImportError:
        evidence["pdf_links"] = {"status": "pending", "reason": "pypdf unavailable"}
    pages = [{"path": str(p.relative_to(repo)), "sha256": sha256(p)} for p in sorted(output.glob("page-*.png"))]
    report = {"schema_version": 1, "status": "pending_human_review", "pdf": pdf,
              "commit": git(repo, "rev-parse", "HEAD"),
              "branch": git(repo, "symbolic-ref", "--short", "HEAD"),
              "pdf_sha256": digest, "pages": pages, "links": links, "tools": evidence,
              "checklist": ["Inspect every rendered page", "Margins and text clipping", "Sprint title continuity",
                            "Caption above and source below", "Reflection border/page continuation",
                            "Tables, blank pages, lists, citations and references"],
              "notice": "Rendering and extracted text are evidence, not visual approval"}
    write_json(output / "report.json", report, repo=repo)
    return report
