"""Offline rendering check for uncertain and factual bibliography dates."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "relatorio_AGES_eduardo"


@unittest.skipUnless(shutil.which("tectonic") and shutil.which("biber") and shutil.which("pdftotext"),
                     "Tectonic, Biber and Poppler are required")
class DateRenderingTests(unittest.TestCase):
    def test_uncertain_years_keep_question_mark_in_citations_and_bibliography(self):
        with tempfile.TemporaryDirectory(prefix="ages-date-rendering-") as temp:
            root = Path(temp)
            (root / "util" / "fonts").mkdir(parents=True)
            shutil.copy2(SOURCE / "util" / "style.tex", root / "util" / "style.tex")
            shutil.copy2(SOURCE / "util" / "fonts" / "LiberationMono-Regular.ttf",
                         root / "util" / "fonts" / "LiberationMono-Regular.ttf")
            (root / "bibliografia").mkdir()
            (root / "bibliografia" / "bibliografia.bib").write_text(r"""@online{uncertain-a,
  author = {Example Organization}, title = {Uncertain A}, date = {2026?},
  url = {https://example.org/a}, urldate = {2026-10-01}
}
@online{uncertain-b,
  author = {Example Organization}, title = {Uncertain B}, date = {2026?},
  url = {https://example.org/b}, urldate = {2026-10-02}
}
@online{factual,
  author = {Example Organization}, title = {Factual}, date = {2024},
  url = {https://example.org/c}, urldate = {2026-10-03}
}
""", encoding="utf-8")
            (root / "main.tex").write_text(r"""\documentclass[a4paper,12pt,oneside,chapter=TITLE,english,brazil]{abntex2}
\input{util/style.tex}
\begin{document}
Incerteza A: \parencite{uncertain-a}. Incerteza B: \parencite{uncertain-b}.
Data factual: \parencite{factual}.
\printbibliography[title={Referências}]
\end{document}
""", encoding="utf-8")

            env = os.environ.copy()
            env["TECTONIC_CACHE_DIR"] = str(Path.home() / ".cache" / "tectonic")
            first = subprocess.run(
                ["tectonic", "--only-cached", "--untrusted", "--keep-intermediates", "--keep-logs", "main.tex"],
                cwd=root, env=env, text=True, capture_output=True, timeout=120)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertTrue((root / "main.bcf").exists(), first.stdout + first.stderr)
            biber = subprocess.run(["biber", "main"], cwd=root, env=env, text=True,
                                   capture_output=True, timeout=120)
            self.assertEqual(biber.returncode, 0, biber.stdout + biber.stderr)
            final = subprocess.run(
                ["tectonic", "--only-cached", "--untrusted", "--keep-intermediates", "--keep-logs", "main.tex"],
                cwd=root, env=env, text=True, capture_output=True, timeout=120)
            self.assertEqual(final.returncode, 0, final.stdout + final.stderr)
            extracted = subprocess.run(["pdftotext", "main.pdf", "-"], cwd=root, text=True,
                                       capture_output=True, check=True).stdout

            self.assertIn("[2026?a]", extracted)
            self.assertIn("[2026?b]", extracted)
            self.assertGreaterEqual(extracted.count("[2026?a]"), 2, extracted)
            self.assertGreaterEqual(extracted.count("[2026?b]"), 2, extracted)
            self.assertIn("2024", extracted)
            self.assertNotIn("[2024?]", extracted)


if __name__ == "__main__":
    unittest.main()
