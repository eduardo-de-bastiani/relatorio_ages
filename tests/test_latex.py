import tempfile
import unittest
from pathlib import Path

from scripts.migration_harness.latex import audit_latex, bib_keys, commands, strip_comments


class LatexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def audit(self):
        return audit_latex(self.root, Path("main.tex"))

    def codes(self, report):
        return {item["code"] for item in report["findings"]}

    def test_compilation_root_paths_options_nested_braces_and_bibliography(self):
        self.write("main.tex", r"\input{sub/unit}\addbibresource{refs.bib}")
        self.write("sub/unit.tex", r"\input{shared}\section[Curto]{Nome \emph{aninhado}}\label{sec:x}\ref{sec:x}\parencite[veja][p.~2]{corp}")
        self.write("shared.tex", "Texto.")
        self.write("refs.bib", '@online{corp, author={{Empresa {A} e "B"}}, title="Título {aninhado}", url={https://example.org/a@b}}')
        result = self.audit()
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["counts"]["files"], 3)
        self.assertEqual(result["counts"]["bibliography_entries"], 1)

    def test_comments_do_not_truncate_percent_encoded_url(self):
        text = r"\href{https://example.org/a%20b}{Nome} % ignore \input{missing}" + "\n" + r"\input{ok}"
        tokens = list(commands(text))
        self.assertEqual(tokens[0].args, ("https://example.org/a%20b", "Nome"))
        self.assertEqual([token.args[0] for token in tokens if token.name == "input"], ["ok"])
        self.assertIn(r"\%", strip_comments(r"20\% correto % comentário"))
        self.write("main.tex", text)
        self.write("ok.tex", "ok")
        self.assertIn("unescaped_url_percent", self.codes(self.audit()))

    def test_missing_duplicate_refs_and_cites(self):
        self.write("main.tex", r"\label{x}\label{x}\ref{missing}\cite{bad}\addbibresource{r.bib}")
        self.write("r.bib", "@book{good,title={A}}\n@book{good,title={B}}")
        codes = self.codes(self.audit())
        self.assertTrue({"duplicate_label", "undefined_reference", "undefined_citation", "duplicate_bib_key"}.issubset(codes))

    def test_include_cycle_escape_and_missing_asset(self):
        self.write("main.tex", r"\input{child}\includegraphics{absent}")
        self.write("child.tex", r"\input{main}\input{../outside}")
        codes = self.codes(self.audit())
        self.assertTrue({"include_cycle", "unsafe_or_dynamic_include", "missing_or_dynamic_asset"}.issubset(codes))

    def test_sprint_input_allowed_include_and_newpage_forbidden(self):
        self.write("main.tex", r"\input{sprint 0}")
        self.write("sprint 0.tex", r"\subsection{Sprint 0} Texto.")
        self.assertEqual(self.audit()["status"], "pass")
        self.write("main.tex", r"\include{sprint 0}")
        self.assertIn("sprint_include", self.codes(self.audit()))
        self.write("main.tex", r"\input{sprint 0}")
        self.write("sprint 0.tex", r"\newpage\subsection{Sprint 0} Texto.")
        self.assertIn("sprint_page_break", self.codes(self.audit()))

    def test_unreachable_demo_warns_not_fails(self):
        self.write("main.tex", "Texto.")
        self.write("util/example.tex", r"\cite{invalid-demo}")
        report = self.audit()
        self.assertEqual(report["status"], "pass")
        self.assertIn("unreachable_tex", self.codes(report))

    def test_extension_appended_to_dotted_name_not_replaced(self):
        self.write("main.tex", r"\input{0.1 - capa}")
        self.write("0.1 - capa.tex", "Capa.")
        self.assertEqual(self.audit()["status"], "pass", self.audit())

    def test_bib_parentheses_nested_corporate_quotes_and_preamble(self):
        keys, duplicates = bib_keys('@preamble{"literal"}\n@string{pub="ABC"}\n@book(corp,author={{Empresa ) e "filial"}}, title="Título ) {x}")\n@book{second,title={Outro}}')
        self.assertEqual(keys, {"corp", "second"})
        self.assertEqual(duplicates, [])
        with self.assertRaises(ValueError):
            bib_keys("@book{broken,title={no end}")

    def test_multicites_and_unbraced_include_fail_closed(self):
        self.write("main.tex", r"\parencites[p.~1]{exists}[p.~2]{missing}\input unknown.tex\addbibresource{r.bib}")
        self.write("r.bib", "@book{exists,title={A}}")
        codes = self.codes(self.audit())
        self.assertIn("undefined_citation", codes)
        self.assertIn("unsupported_include_syntax", codes)


if __name__ == "__main__":
    unittest.main()
