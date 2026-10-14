"""Adversarial synthetic fixtures; no memorial content is converted."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.migration_harness.preservation import audit_conversion, displayed_text, UnsupportedSerialization


class PreservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest = {"records": [{"id": "p1", "type": "text:p", "text": "Ação: 20% — café!", "unit_id": "sprint-test"}], "units": [{"id": "sprint-test", "record_ids": ["p1"], "source_record_ids": ["p1"]}], "assets": []}
        self.ledger = {"schema_version": 1, "units": {"sprint-test": {"state": "converted", "tex_path": "unit.tex", "element_map": []}}}

    def tearDown(self):
        self.temp.cleanup()

    def write(self, value, path="unit.tex"):
        (self.root / path).write_text(value, encoding="utf-8")

    def mapping(self, rid, fragment, path="unit.tex", occurrence=0):
        data = (self.root / path).read_bytes()
        wanted = fragment.encode("utf-8")
        start = -1
        for _ in range(occurrence + 1):
            start = data.index(wanted, start + 1)
        return {"source_id": rid, "target_file": path, "start_byte": start, "end_byte": start + len(wanted), "target_sha256": hashlib.sha256(data).hexdigest()}

    def audit(self):
        return audit_conversion(self.manifest, self.ledger, self.root)

    def codes(self, report):
        return {item["code"] for item in report["findings"]}

    def valid_text(self):
        self.write(r"Ação: 20\% — \emph{café!}")
        self.ledger["units"]["sprint-test"]["element_map"] = [self.mapping("p1", r"Ação: 20\% — \emph{café!}")]

    def test_known_serialization_preserves_accents_and_punctuation(self):
        self.valid_text()
        report = self.audit()
        self.assertEqual(report["status"], "pass", report)
        self.assertEqual(report["facts"]["coverage_percent"], 100)
        self.assertIn("pdf_evidence_pending", self.codes(report))

    def test_unconverted_never_claims_integrity(self):
        self.ledger["units"]["sprint-test"]["state"] = "unconverted"
        report = self.audit()
        self.assertEqual(report["status"], "unconverted")
        self.assertEqual(report["facts"]["coverage_percent"], 0)

    def test_diacritic_or_punctuation_loss_fails(self):
        for value in [r"Acao: 20\% — café!", r"Ação: 20\% — café", r"ação: 20\% — café!"]:
            self.write(value)
            self.ledger["units"]["sprint-test"]["element_map"] = [self.mapping("p1", value)]
            report = self.audit()
            self.assertEqual(report["status"], "blocked")
            self.assertIn("text_changed", self.codes(report))
            self.assertEqual(len(report["differences"]["sprint-test"]), 1)

    def test_extra_text_not_in_ledger_cannot_be_hidden(self):
        self.write(r"Ação: 20\% — café! Inventado.")
        self.ledger["units"]["sprint-test"]["element_map"] = [self.mapping("p1", r"Ação: 20\% — café!")]
        self.assertIn("unmapped_visible_content", self.codes(self.audit()))

    def test_unknown_macro_never_accepted_using_claimed_text(self):
        self.write(r"\inventado{Ação: 20\% — café!}")
        mapping = self.mapping("p1", r"\inventado{Ação: 20\% — café!}")
        mapping["text"] = "Ação: 20% — café!"
        self.ledger["units"]["sprint-test"]["element_map"] = [mapping]
        self.assertIn("unsupported_serialization", self.codes(self.audit()))

    def test_stale_hash_and_utf8_middle_offset_fail(self):
        self.valid_text()
        mapping = self.ledger["units"]["sprint-test"]["element_map"][0]
        mapping["target_sha256"] = "0" * 64
        self.assertIn("invalid_target_evidence", self.codes(self.audit()))
        mapping["target_sha256"] = hashlib.sha256((self.root / "unit.tex").read_bytes()).hexdigest()
        mapping["start_byte"] = 2  # Inside ç.
        self.assertIn("invalid_target_evidence", self.codes(self.audit()))

    def test_order_is_from_actual_bytes_not_ledger_order(self):
        self.manifest["records"] = [{"id": "p1", "type": "text:p", "text": "Primeiro."}, {"id": "p2", "type": "text:p", "text": "Segundo."}]
        self.manifest["units"][0].update(record_ids=["p1", "p2"], source_record_ids=["p1", "p2"])
        self.write("Segundo.\nPrimeiro.")
        self.ledger["units"]["sprint-test"]["element_map"] = [self.mapping("p1", "Primeiro."), self.mapping("p2", "Segundo.")]
        self.assertIn("element_order_changed", self.codes(self.audit()))

    def test_parent_child_parent_expansion_order(self):
        texts = ["Antes.", "Dentro.", "Depois."]
        self.manifest["records"] = [{"id": f"p{i}", "type": "text:p", "text": text} for i, text in enumerate(texts, 1)]
        self.manifest["units"][0].update(record_ids=["p1", "p2", "p3"], source_record_ids=["p1", "p2", "p3"])
        self.write("Antes.\n\\input{child}\nDepois.")
        self.write("Dentro.", "child.tex")
        self.ledger["units"]["sprint-test"]["element_map"] = [self.mapping("p1", "Antes."), self.mapping("p2", "Dentro.", "child.tex"), self.mapping("p3", "Depois.")]
        self.assertEqual(self.audit()["status"], "pass", self.audit())

    def test_missing_and_duplicate_mapping_fail(self):
        self.valid_text()
        self.ledger["units"]["sprint-test"]["element_map"] *= 2
        self.assertIn("duplicate_mapping", self.codes(self.audit()))
        self.ledger["units"]["sprint-test"]["element_map"] = []
        self.assertIn("missing_element", self.codes(self.audit()))

    def test_quotes_dashes_and_unicode_are_explicit_and_exact(self):
        self.assertEqual(displayed_text("``ação'' -- café", ["tex_quotes", "tex_dashes"]), "“ação” – café")
        with self.assertRaises(UnsupportedSerialization):
            displayed_text("``ação'' -- café")
        self.assertEqual(displayed_text("cafe\u0301", ["canonical_unicode"]), "café")
        self.assertNotEqual(displayed_text("cafe\u0301"), "café")
        with self.assertRaises(UnsupportedSerialization):
            displayed_text("Ação", ["remove_accents"])

    def test_comment_suppresses_newline_not_inserted_space(self):
        self.assertEqual(displayed_text("ca% comentário\nfé"), "café")
        self.assertEqual(displayed_text("ca % comentário\nfé"), "ca fé")
        self.assertEqual(displayed_text(r"20\%"), "20%")
        self.assertEqual(displayed_text(r"\url{https://example.org/a_b%20c}"), "https://example.org/a_b%20c")

    def test_explicit_odf_spaces_tabs_and_breaks_never_auto_normalize(self):
        for source, target in [("A  B", "A B"), ("A\tB", "A B"), ("A\nB", "A B"), (" A B", "A B"), ("A B ", "A B")]:
            with self.subTest(source=repr(source)):
                self.manifest["records"][0]["text"] = source
                self.write(target)
                self.ledger["units"]["sprint-test"]["element_map"] = [self.mapping("p1", target)]
                report = self.audit()
                self.assertEqual(report["status"], "blocked", report)
                self.assertIn("explicit_source_whitespace", self.codes(report))
                self.assertEqual(report["facts"]["text_records_matched"], 0)

    def test_copying_raw_explicit_whitespace_is_not_rendered_proof(self):
        for source in ["A  B", "A\tB", "A\nB"]:
            with self.subTest(source=repr(source)):
                self.manifest["records"][0]["text"] = source
                self.write(source)
                self.ledger["units"]["sprint-test"]["element_map"] = [self.mapping("p1", source)]
                self.assertEqual(self.audit()["status"], "blocked")

    def test_only_code_folding_not_explicit_target_break_is_allowed(self):
        self.manifest["records"][0]["text"] = "A B"
        self.write("A\nB")
        self.ledger["units"]["sprint-test"]["element_map"] = [self.mapping("p1", "A\nB")]
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        for target in [r"A\newline B", r"A\\ B", r"A\linebreak B", "A\n\nB"]:
            with self.subTest(target=target):
                self.write(target)
                self.ledger["units"]["sprint-test"]["element_map"] = [self.mapping("p1", target)]
                self.assertEqual(self.audit()["status"], "blocked")
                self.assertIn("unsupported_serialization", self.codes(self.audit()))

    def test_links_independently_verify_url_and_anchor(self):
        self.manifest["records"] = [{"id": "p1", "type": "text:p", "text": "Veja Ação."}, {"id": "a1", "type": "text:a", "href": "https://example.org/a%20b", "source_text": "Ação"}]
        self.manifest["units"][0]["record_ids"] = ["p1", "a1"]
        self.write(r"Veja \href{https://example.org/a\%20b}{Ação}.")
        unit = self.ledger["units"]["sprint-test"]
        unit["element_map"] = [self.mapping("p1", r"Veja \href{https://example.org/a\%20b}{Ação}."), self.mapping("a1", r"\href{https://example.org/a\%20b}{Ação}")]
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        self.manifest["records"][1]["href"] = "https://example.org/other"
        self.assertIn("url_changed", self.codes(self.audit()))
        self.manifest["records"][1]["href"] = "https://example.org/a%20b"
        unit["element_map"] = unit["element_map"][:1]
        self.assertIn("missing_hyperlink", self.codes(self.audit()))

    def test_image_bytes_and_actual_reference_both_required(self):
        self.valid_text()
        image = b"synthetic image bytes"
        (self.root / "image.png").write_bytes(image)
        self.manifest["records"].append({"id": "i1", "type": "draw:image", "text": None})
        self.manifest["assets"] = [{"id": "asset1", "sha256": hashlib.sha256(image).hexdigest(), "occurrence_ids": ["i1"]}]
        self.manifest["units"][0]["record_ids"].append("i1")
        self.write(r"Ação: 20\% — café!" + "\n" + r"\includegraphics[width=3cm]{image.png}")
        unit = self.ledger["units"]["sprint-test"]
        unit["element_map"] = [self.mapping("p1", r"Ação: 20\% — café!"), self.mapping("i1", r"\includegraphics[width=3cm]{image.png}")]
        unit["asset_map"] = [{"source_id": "i1", "target_file": "image.png"}]
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        (self.root / "image.png").write_bytes(b"modified")
        self.assertIn("image_hash_changed", self.codes(self.audit()))

    def test_path_escape_is_rejected(self):
        self.valid_text()
        self.ledger["units"]["sprint-test"]["element_map"][0]["target_file"] = "../unit.tex"
        self.assertIn("invalid_target_evidence", self.codes(self.audit()))

    def whitespace_contract(self):
        self.write(r"\newcommand{\originaltab}{\noindent\hspace*{1.251cm}}" + "\n" + r"\newcommand{\originalspace}{\hspace*{\fontdimen2\font}}", "macros.tex")
        return {"path": "macros.tex", "sha256": hashlib.sha256((self.root / "macros.tex").read_bytes()).hexdigest()}

    def whitespace_case(self, original, target):
        self.manifest["records"][0]["text"] = original
        self.write(target)
        self.ledger["macro_contract"] = self.whitespace_contract()
        mapping = self.mapping("p1", target)
        mapping["serializations"] = ["original_whitespace"]
        self.ledger["units"]["sprint-test"]["element_map"] = [mapping]

    def test_verified_original_whitespace_markers_preserve_exact_values(self):
        for source, target in [("\t Palavra ", r"\originaltab{}\originalspace{}Palavra\originalspace{}"), (" A  B ", r"\originalspace{}A\originalspace{}\originalspace{}B\originalspace{}"), ("\tA B", r"\originaltab{}A B")]:
            with self.subTest(source=repr(source)):
                self.whitespace_case(source, target)
                report = self.audit()
                self.assertEqual(report["status"], "pass", report)
                self.assertEqual(report["facts"]["text_records_matched"], 1)

    def test_whitespace_macro_contract_missing_tampered_or_redefined_blocks(self):
        self.whitespace_case("\tA", r"\originaltab{}A")
        contract = self.ledger.pop("macro_contract")
        self.assertIn("invalid_macro_contract", self.codes(self.audit()))
        self.ledger["macro_contract"] = contract
        self.write(r"\newcommand{\originaltab}{\hspace*{0cm}}" + "\n" + r"\newcommand{\originalspace}{\hspace*{\fontdimen2\font}}", "macros.tex")
        self.assertIn("invalid_macro_contract", self.codes(self.audit()))
        self.ledger["macro_contract"]["sha256"] = hashlib.sha256((self.root / "macros.tex").read_bytes()).hexdigest()
        self.assertIn("invalid_macro_contract", self.codes(self.audit()))
        self.ledger["macro_contract"] = self.whitespace_contract()
        self.write(r"\renewcommand{\originaltab}{Nada}\originaltab{}A")
        mapping = self.mapping("p1", r"\originaltab{}A")
        mapping["serializations"] = ["original_whitespace"]
        self.ledger["units"]["sprint-test"]["element_map"] = [mapping]
        self.assertIn("whitespace_macro_redefinition", self.codes(self.audit()))

    def test_original_whitespace_policy_never_normalizes_source(self):
        for source, target in [("\tA", "A"), ("\tA", "\tA"), ("A  B", "A  B"), (" A ", "A"), ("\tA ", r"\originaltab{}A"), ("A\nB", r"A\newline B"), ("A\tB", r"A\originaltab{}B")]:
            with self.subTest(source=repr(source), target=target):
                self.whitespace_case(source, target)
                self.assertEqual(self.audit()["status"], "blocked", self.audit())

    def test_xml_text_cannot_inject_internal_whitespace_markers(self):
        self.whitespace_case("\tA", "\ue000A\ue001")
        self.assertEqual(self.audit()["status"], "blocked")
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(r"\originaltab{}A", ["original_whitespace"])

    def toc_case(self, toc_title=r"2.3.1 Sprint 0\originalspace{}", actual_title=None, counter=""):
        actual_title = actual_title or r"2.3.1 Sprint 0\originalspace{}"
        source = "2.3.1 Sprint 0 "
        self.manifest["records"][0].update(type="text:h", text=source)
        self.whitespace_case(source, counter + "\\subsection*{" + actual_title + "}\n\\addcontentsline{toc}{subsection}{" + toc_title + "}")
        mapping = self.mapping("p1", actual_title)
        mapping["serializations"] = ["original_whitespace"]
        self.ledger["units"]["sprint-test"]["element_map"] = [mapping]

    def test_toc_is_proved_against_source_and_actual_starred_heading(self):
        self.toc_case()
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        self.toc_case(toc_title="Inventado")
        self.assertIn("unproved_toc_entry", self.codes(self.audit()))
        self.toc_case(actual_title=r"2.3.1 Sprint 0\originalspace{}Inventado")
        self.assertEqual(self.audit()["status"], "blocked")

    def test_counter_step_requires_matching_literal_heading_and_subsection(self):
        self.toc_case(counter=r"\refstepcounter{subsection}" + "\n")
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        self.assertIn("counter_aux_review_required", self.codes(self.audit()))
        self.toc_case(counter=r"\refstepcounter{chapter}" + "\n")
        self.assertIn("unproved_counter_step", self.codes(self.audit()))

    def test_bookmark_requires_real_source_pair_exact_name_and_no_text(self):
        self.toc_case()
        self.manifest["records"].extend([{"id": "bs", "type": "text:bookmark-start", "parent_id": "p1", "attributes": {"text:name": "original_anchor"}}, {"id": "be", "type": "text:bookmark-end", "parent_id": "p1", "attributes": {"text:name": "original_anchor"}}])
        old = (self.root / "unit.tex").read_text()
        self.write(r"\hypertarget{original_anchor}{}" + "\n" + old)
        unit = self.ledger["units"]["sprint-test"]
        unit["element_map"] = [self.mapping("p1", r"2.3.1 Sprint 0\originalspace{}")]
        unit["element_map"][0]["serializations"] = ["original_whitespace"]
        mapping = self.mapping("p1", r"\hypertarget{original_anchor}{}")
        mapping.update(source_heading_id="p1", source_name="original_anchor", target_anchor="original_anchor", command="hypertarget", source_start_id="bs", source_end_id="be")
        unit["bookmark_map"] = [mapping]
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        mapping["target_anchor"] = "invented"
        self.assertIn("invalid_bookmark_evidence", self.codes(self.audit()))
        mapping["target_anchor"] = "original_anchor"
        self.manifest["records"][-1]["attributes"]["text:name"] = "different"
        self.assertIn("invalid_bookmark_evidence", self.codes(self.audit()))

    def figure_case(self):
        from scripts.migration_harness.latex import MEMORIAL_FIGURE_BODY
        self.manifest["records"] = [{"id": "c1", "type": "text:p", "text": "Figure 1: Ação"}, {"id": "i1", "type": "draw:image", "caption_ids": ["c1"]}]
        self.manifest["units"][0].update(record_ids=["i1", "c1"], source_record_ids=["c1"])
        image = b"synthetic intact asset"
        (self.root / "image.png").write_bytes(image)
        self.manifest["assets"] = [{"id": "asset1", "sha256": hashlib.sha256(image).hexdigest(), "occurrence_ids": ["i1"]}]
        self.write(r"\newcommand{\memorialfigure}[5]{" + MEMORIAL_FIGURE_BODY + "}", "figures.tex")
        self.ledger["figure_contract"] = {"path": "figures.tex", "sha256": hashlib.sha256((self.root / "figures.tex").read_bytes()).hexdigest()}
        value = r"\memorialfigure{image.png}{Figure 1: Ação}{fig:one}{Fonte: pendente de identificação}{0.8}"
        self.write(value)
        unit = self.ledger["units"]["sprint-test"]
        unit["asset_map"] = [{"source_id": "i1", "target_file": "image.png"}]
        self.figure_maps(value)
        return value

    def figure_maps(self, value):
        self.write(value)
        unit = self.ledger["units"]["sprint-test"]
        unit["element_map"] = [self.mapping("i1", value), self.mapping("c1", "Figure 1: Ação")]

    def test_figure_contract_literal_caption_source_association_and_bytes(self):
        value = self.figure_case()
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        self.assertEqual(self.audit()["facts"]["images_checked"], 1)
        for changed in [value.replace("pendente de identificação", "Autor, 2026"), value.replace("{0.8}", "{1.1}"), value.replace("{0.8}", r"{\input{evil}}"), value.replace("{fig:one}", "{}"), value.replace("\\memorialfigure", "\\memorialfigure[trim=1]")]:
            with self.subTest(changed=changed):
                self.figure_maps(changed)
                self.assertIn("invalid_image_evidence", self.codes(self.audit()))
        self.figure_maps(value)
        self.manifest["records"][1]["caption_ids"] = ["other-caption"]
        self.assertIn("invalid_image_evidence", self.codes(self.audit()))
        self.manifest["records"][1]["caption_ids"] = ["c1"]
        (self.root / "image.png").write_bytes(b"changed")
        self.assertIn("image_hash_changed", self.codes(self.audit()))

    def test_figure_contract_stale_malicious_caption_and_unmatched_media_fail(self):
        value = self.figure_case()
        self.ledger["figure_contract"]["sha256"] = "0" * 64
        self.assertIn("invalid_figure_contract", self.codes(self.audit()))
        self.figure_case()
        text = (self.root / "figures.tex").read_text().replace(r"\caption*{#2}", r"\caption*{Inventado}")
        self.write(text, "figures.tex")
        self.ledger["figure_contract"]["sha256"] = hashlib.sha256(text.encode()).hexdigest()
        self.assertIn("invalid_figure_contract", self.codes(self.audit()))
        self.figure_case()
        self.figure_maps(value.replace("Figure 1: Ação", "Figure 1: Ação extra"))
        self.assertIn("invalid_image_evidence", self.codes(self.audit()))
        self.figure_case()
        self.ledger["units"]["sprint-test"]["asset_map"] = []
        self.assertIn("missing_image", self.codes(self.audit()))

    def placeholder_case(self):
        import json
        from scripts.migration_harness.preservation import DIAGRAM_PLACEHOLDER_BODY
        uid = "chapter-02-text-h-0009"
        heading = "text-h-0009"
        self.manifest = {"records": [{"id": heading, "type": "text:h", "text": "Banco de dados utilizado "}], "units": [{"id": uid, "record_ids": [heading], "source_record_ids": [heading]}], "assets": []}
        self.ledger["units"] = {uid: {"state": "converted", "tex_path": "unit.tex"}}
        macro = self.whitespace_contract()
        text = (self.root / "macros.tex").read_text() + r"\newcommand{\diagramplaceholder}[2]{" + DIAGRAM_PLACEHOLDER_BODY + "}"
        self.write(text, "macros.tex")
        macro["sha256"] = hashlib.sha256(text.encode()).hexdigest()
        self.ledger["macro_contract"] = macro
        call = r"\diagramplaceholder{ages-i-database}{Esquema do banco de dados não incorporado ao ODT; preenchimento posterior.}"
        title = r"Banco de dados utilizado\originalspace{}"
        self.write(r"\subsection{" + title + "}\n" + call)
        mapping = self.mapping(heading, title)
        mapping["serializations"] = ["original_whitespace"]
        unit = self.ledger["units"][uid]
        unit["element_map"] = [mapping]
        apparatus = self.mapping(heading, call)
        apparatus.pop("source_id")
        evidence = "migration/approvals/ages-i-authorization.json"
        apparatus.update(kind="diagram_placeholder", source_heading_id=heading, placeholder_id="ages-i-database", authorization_evidence=evidence)
        unit["approved_apparatus"] = [apparatus]
        self.write(json.dumps({"phase": "edition", "authorization_evidence": evidence, "authorized_units": [uid]}), "harness.json")
        (self.root / "migration/approvals").mkdir(parents=True)
        self.write(json.dumps({"kind": "user_execution_authorization", "scope": [uid], "quoted_instruction": "Vamos começar com AGES I. Lembre-se que os itens faltantes como arquitetura, banco de dados precisarão de placeholders que serão preenchidos posteriormente", "placeholders_explicitly_authorized": ["Banco de dados utilizado"]}), evidence)
        return unit, apparatus

    def test_placeholder_requires_exact_user_evidence_heading_and_schema(self):
        unit, apparatus = self.placeholder_case()
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        for key, invalid in [("source_heading_id", "p1"), ("authorization_evidence", "fake.json"), ("placeholder_id", "inventado"), ("kind", "ignore_text")]:
            original = apparatus[key]
            apparatus[key] = invalid
            self.assertIn("invalid_approved_apparatus", self.codes(self.audit()))
            apparatus[key] = original
        apparatus["ignore_text"] = True
        self.assertIn("invalid_approved_apparatus", self.codes(self.audit()))
        apparatus.pop("ignore_text")
        self.write("{}", "harness.json")
        self.assertIn("invalid_approved_apparatus", self.codes(self.audit()))
        unit["approved_apparatus"] = []
        self.assertIn("unsupported_target_scaffolding", self.codes(self.audit()))


if __name__ == "__main__":
    unittest.main()
