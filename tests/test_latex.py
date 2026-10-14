import tempfile
import unittest
from pathlib import Path

from scripts.migration_harness.latex import audit_latex, bib_keys, commands, strip_comments, MEMORIAL_FIGURE_BODY


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

    def test_break_state_follows_included_headings_without_leaking_from_pretext(self):
        self.write("main.tex", r"\clearpage\input{chapter}\input{sprint-0}")
        self.write("chapter.tex", r"\chapter*{Original chapter}Narrative.")
        self.write("sprint-0.tex", r"\subsection*{Sprint 0}Text.")
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        self.write("chapter.tex", "")
        self.assertIn("sprint_page_break", self.codes(self.audit()))
        self.write("main.tex", r"\input{chapter}\input{sprint-0}")
        self.write("chapter.tex", r"\clearpage")
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

    def test_dormant_macro_body_is_not_a_dynamic_asset_invocation(self):
        self.write("main.tex", r"\newcommand{\unused}[1]{\includegraphics{#1}\label{#1}}" + "\nTexto.")
        report = self.audit()
        self.assertEqual(report["status"], "pass", report)
        self.assertEqual(report["counts"]["images"], 0)
        self.assertEqual(report["counts"]["labels"], 0)
        self.write("main.tex", r"\def\unused#1{\includegraphics{#1}}" + "\nTexto.")
        self.assertEqual(self.audit()["status"], "pass", self.audit())

    def test_unknown_invoked_asset_macro_blocks_instead_of_hiding_dependency(self):
        self.write("main.tex", r"\newcommand{\customfigure}[1]{\includegraphics{#1}}\customfigure{missing.png}")
        self.assertIn("unsupported_operational_macro", self.codes(self.audit()))
        self.write("main.tex", r"\newcommand{\alias}[1]{\customfigure{#1}}\newcommand{\customfigure}[1]{\includegraphics{#1}}\alias{missing.png}")
        self.assertIn("unsupported_operational_macro", self.codes(self.audit()))
        self.write("main.tex", r"\newenvironment{customfigure}{\includegraphics{missing.png}}{}\begin{customfigure}Texto.\end{customfigure}")
        self.assertIn("unsupported_operational_macro", self.codes(self.audit()))

    def test_memorialfigure_invocation_checks_actual_asset_label_and_caption(self):
        definition = r"\newcommand{\memorialfigure}[5]{" + MEMORIAL_FIGURE_BODY + "}"
        self.write("main.tex", definition + r"\memorialfigure{missing.png}{Legenda}{fig:sample}{Fonte: pendente de identificação}{0.8}\ref{fig:sample}")
        self.assertIn("missing_or_dynamic_asset", self.codes(self.audit()))
        (self.root / "image.png").write_bytes(b"synthetic image")
        self.write("main.tex", definition + r"\memorialfigure{image.png}{Legenda}{fig:sample}{Fonte: pendente de identificação}{0.8}\ref{fig:sample}")
        result = self.audit()
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["counts"]["images"], 1)
        self.assertEqual(result["counts"]["labels"], 1)
        self.write("main.tex", definition + r"\memorialfigure{image.png}{}{fig:sample}{Fonte: pendente de identificação}{0.8}")
        self.assertIn("missing_figure_caption_or_label", self.codes(self.audit()))
        self.write("main.tex", definition.replace(r"\caption*{#2}", r"\caption*{Texto inventado}") + r"\memorialfigure{image.png}{Legenda}{fig:sample}{Fonte: pendente de identificação}{0.8}")
        self.assertIn("unverified_figure_macro", self.codes(self.audit()))


if __name__ == "__main__":
    unittest.main()
