"""Test real pilot flow between synthetic neighbors, in an isolated copy.

The generated PDF is a test artifact, not the pilot review deliverable and
not another converted Sprint. Original source text is independently checked.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    destination = Path(__file__).resolve().parents[1]
    repo = destination.parent
    unit = destination / "conteudo/migracao/ages-i-sprint-0.tex"
    original_hash = sha(unit)
    manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text())
    entry = next(u for u in manifest["units"] if u["id"] == "ages-i-sprint-0")
    records = {r["id"]: r for r in manifest["records"]}
    tex = unit.read_text()
    decoded = {}
    title = re.search(r"\\subsection\*\{(2\.3\.1 Sprint 0\\originalspace\{\})\}", tex)
    assert title, "Original heading serialization changed"
    decoded[entry["heading_id"]] = title.group(1).replace(r"\originalspace{}", " ")
    for match in re.finditer(r"^% (text-p-\d+)\n([^\n]+)", tex, re.M):
        value = match.group(2)
        wrapper = re.match(r"\\(?:indent|noindent)\s+", value)
        assert wrapper, "Unexpected paragraph wrapper"
        value = value[wrapper.end():]
        value = (value.replace(r"\originaltab{}", "\t")
                      .replace(r"\originalleadingspace{}", " ")
                      .replace(r"\originalspace{}", " "))
        decoded[match.group(1)] = value
    assert set(decoded) == set(entry["source_record_ids"])
    for record_id in entry["source_record_ids"]:
        assert decoded[record_id] == records[record_id]["text"], record_id
    output = repo / "build/pilot-continuity-test"
    output.mkdir(parents=True, exist_ok=True)
    before = "Synthetic context before the pilot."
    after = "Synthetic context after the pilot."
    with tempfile.TemporaryDirectory(prefix="ages-pilot-continuity-") as work:
        work = Path(work)
        source = work / "source"
        shutil.copytree(destination, source, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(Path.home() / ".cache/tectonic", work / "cache/tectonic")
        (source / "main.tex").write_text(r"""\documentclass[a4paper,12pt,oneside,chapter=TITLE,english,brazil]{abntex2}
\input{util/style.tex}\input{util/macros.tex}
\begin{document}\textual\pagestyle{simple}
\setcounter{chapter}{1}\chapter{PROJETO AGES I – EASY CHOOSE}
\setcounter{section}{2}\section{Atividades desempenhadas pelo aluno no projeto}
\noindent Synthetic context before the pilot.\par
\input{conteudo/migracao/ages-i-sprint-0.tex}
\subsection*{Synthetic continuation heading}
\noindent Synthetic context after the pilot.\par
\end{document}
""", encoding="utf-8")
        environment = os.environ | {
            "XDG_CACHE_HOME": str(work / "cache"),
            "TECTONIC_CACHE_DIR": str(work / "cache/tectonic"),
            "SOURCE_DATE_EPOCH": "1700000000", "TZ": "UTC",
        }
        command = ["tectonic", "--only-cached", "--untrusted", "--keep-logs", "main.tex"]
        result = subprocess.run(command, cwd=source, env=environment,
                                capture_output=True, text=True, timeout=120)
        (output / "compiler.txt").write_text(result.stdout + result.stderr)
        for filename in ["main.pdf", "main.log", "main.tex"]:
            if (source / filename).exists():
                shutil.copy2(source / filename, output / filename)
        if result.returncode:
            print(result.stdout + result.stderr)
            return result.returncode
        log = (source / "main.log").read_text(errors="replace")
        defects = [line for line in log.splitlines() if any(
            token in line for token in ["Missing character", "Overfull", "Underfull", " Warning:"])]
        assert not defects, "\n".join(defects)
        subprocess.run(["pdftotext", "-bbox", "main.pdf", "positions.html"],
                       cwd=source, check=True, capture_output=True)
        tree = ET.parse(source / "positions.html")
        pages = []
        for number, page in enumerate(tree.findall(".//{*}page"), 1):
            words = [{"text": w.text, "xMin": float(w.attrib["xMin"]),
                      "yMin": float(w.attrib["yMin"])} for w in page.findall(".//{*}word")]
            pages.append({"page": number, "words": words})
        def locate(phrase):
            tokens = phrase.split()
            found = []
            for page in pages:
                words = page["words"]
                for index in range(len(words) - len(tokens) + 1):
                    if [w["text"] for w in words[index:index + len(tokens)]] == tokens:
                        found.append({"page": page["page"], "x": words[index]["xMin"],
                                      "y": words[index]["yMin"]})
            assert len(found) == 1, (phrase, found)
            return found[0]
        positions = {"before": locate(before), "pilot_heading": locate("2.3.1 Sprint 0"),
                     "original_last_paragraph": locate("Apesar dos empecilhos,"),
                     "original_last_words": locate("no meu aprendizado."),
                     "after_heading": locate("Synthetic continuation heading"),
                     "after": locate(after)}
        assert positions["before"]["page"] == positions["pilot_heading"]["page"] == 1
        assert positions["before"]["y"] < positions["pilot_heading"]["y"]
        assert positions["original_last_paragraph"]["page"] == positions["after"]["page"]
        assert positions["original_last_words"]["page"] == positions["after_heading"]["page"]
        assert positions["original_last_words"]["y"] < positions["after_heading"]["y"] < positions["after"]["y"]
        assert sha(unit) == original_hash, "Source was modified during test"
        report = {"status": "PASS", "purpose": "synthetic-neighbor pagination test",
                  "unit": entry["id"], "command": command, "exit_code": result.returncode,
                  "source_records_exactly_preserved": entry["source_record_ids"],
                  "source_sha256": original_hash, "pdf_sha256": sha(source / "main.pdf"),
                  "log_sha256": sha(source / "main.log"), "pages": len(pages),
                  "positions": positions, "warnings": defects,
                  "limitations": ["Source identity includes tabs/spaces; their displayed geometry requires visual review.",
                                   "Synthetic neighbors exercise continuity; no real next Sprint is converted."]}
        (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        shutil.copy2(source / "positions.html", output / "positions.html")
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
