"""Offline synthetic tests; no memorial text is read or converted.

Run from any directory with the frozen Tectonic cache. Generated PDFs/logs
remain in build/pilot-macro-test. Temporary source/cache copies are removed.
"""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile


def main():
    destination = Path(__file__).resolve().parents[1]
    repo = destination.parent
    output = repo / "build" / "pilot-macro-test"
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ages-pilot-macros-") as work:
        work = Path(work)
        source = work / "source"
        source.mkdir()
        shutil.copytree(destination / "util", source / "util")
        shutil.copytree(Path.home() / ".cache" / "tectonic", work / "cache" / "tectonic")
        preamble = r"""\documentclass[a4paper,12pt,oneside,chapter=TITLE,english,brazil]{abntex2}
\input{util/style.tex}\input{util/macros.tex}
\begin{document}\textual\pagestyle{simple}
\chapter{Synthetic macro verification}
\section{Continuity}
\subsection{First synthetic unit}
Synthetic verification “curly quotes” – symbols.
\begin{reflection}
"""
        paragraphs = "\n\n".join(
            "Synthetic paragraph %d. " % number
            + "This text exercises a long breakable box with the body font. " * 3
            for number in range(1, 61)
        )
        ending = r"""
\end{reflection}
\subsection{Second synthetic unit}
The second title follows preceding text without a mandatory page break.
\diagramplaceholder{synthetic-only}{No actual diagram is claimed.}
\end{document}
"""
        (source / "main.tex").write_text(preamble + paragraphs + ending, encoding="utf-8")
        environment = os.environ | {
            "XDG_CACHE_HOME": str(work / "cache"),
            "TECTONIC_CACHE_DIR": str(work / "cache" / "tectonic"),
            "SOURCE_DATE_EPOCH": "1700000000",
            "TZ": "UTC",
        }
        command = ["tectonic", "--only-cached", "--untrusted", "--keep-logs", "main.tex"]
        result = subprocess.run(command, cwd=source, env=environment,
                                capture_output=True, text=True, timeout=120)
        (output / "compiler.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
        for name in ["main.pdf", "main.log", "main.tex"]:
            if (source / name).exists():
                shutil.copy2(source / name, output / name)
        if result.returncode:
            print(result.stdout + result.stderr)
            return result.returncode
        log = (source / "main.log").read_text(errors="replace")
        defects = [line for line in log.splitlines()
                   if any(word in line for word in ["Missing character", "Overfull", "Underfull", "LaTeX Warning", "Package caption Warning"])]
        if defects:
            print("\n".join(defects))
            return 1
        text = subprocess.run(["pdftotext", "main.pdf", "-"], cwd=source,
                              capture_output=True, text=True, check=True).stdout
        for number in range(1, 61):
            if text.count("Synthetic paragraph %d." % number) != 1:
                raise AssertionError("Paragraph missing/duplicated: %d" % number)
        assert "“curly quotes” – symbols." in text
        assert "Second synthetic unit" in text
        print("PASS: 60 synthetic paragraphs retained once; Unicode glyphs and breakable borders compile.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
