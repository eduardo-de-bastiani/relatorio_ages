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


if __name__ == "__main__":
    unittest.main()
