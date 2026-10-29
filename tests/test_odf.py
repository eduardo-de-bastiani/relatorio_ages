"""Extraction regressions, including non-linear content and immutable baseline."""
import copy
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migration_harness.odf import AUDITED_SOURCE, NS, extract_manifest, verify_manifest


def package(path, body, extra_entries=None):
    declarations = " ".join(f'xmlns:{p}="{u}"' for p, u in NS.items())
    content = f'<office:document-content {declarations} office:version="1.4"><office:body><office:text>{body}</office:text></office:body></office:document-content>'
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        z.writestr("content.xml", content)
        for name, data in (extra_entries or {}).items():
            z.writestr(name, data)


class FixtureExtractionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / "fixture.odt"

    def test_inline_whitespace_unicode_and_link_are_exact(self):
        package(self.source, '<text:p>á<text:s text:c="3"/><text:span>ç &amp; €</text:span><text:tab/><text:a xlink:href="https://example.org/á?q=1&amp;x=2">âncora</text:a><text:line-break/>fim.</text:p>')
        m = extract_manifest(self.source)
        p = next(r for r in m["records"] if r["type"] == "text:p")
        a = next(r for r in m["records"] if r["type"] == "text:a")
        self.assertEqual(p["text"], "á   ç & €\tâncora\nfim.")
        self.assertIsNone(a["text"])
        self.assertEqual(a["source_text"], "âncora")
        self.assertEqual(a["href"], "https://example.org/á?q=1&x=2")
        self.assertEqual(m["units"][0]["source_text"], [p["text"]])

    def test_implicit_xml_namespace_is_recognized(self):
        package(self.source, '<text:p xml:lang="pt-BR">texto</text:p>')
        m = extract_manifest(self.source)
        p = next(r for r in m["records"] if r["type"] == "text:p")
        self.assertEqual(p["attributes"]["xml:lang"], "pt-BR")

    def test_nested_boxes_do_not_duplicate_text_or_drop_media(self):
        png = b"\x89PNG\r\n\x1a\n" + b"\0\0\0\rIHDR" + (12).to_bytes(4, "big") + (34).to_bytes(4, "big")
        package(self.source, '''<text:h text:outline-level="1">2 - Projeto</text:h>
        <text:p>antes<draw:frame><draw:text-box><text:p>reflexão<draw:frame><draw:text-box><text:p>interna</text:p></draw:text-box></draw:frame></text:p></draw:text-box></draw:frame>depois</text:p>
        <text:h text:outline-level="3"><draw:frame><draw:text-box><text:p><draw:image xlink:href="Pictures/a.png"/></text:p><text:p>Figura 1: imagem</text:p></draw:text-box></draw:frame></text:h>''', {"Pictures/a.png": png})
        m = extract_manifest(self.source)
        self.assertEqual([r["text"] for r in m["records"] if r["type"] == "text:p"],
                         ["antesdepois", "reflexão", "interna", "", "Figura 1: imagem"])
        p = next(r for r in m["records"] if r["type"] == "text:p")
        self.assertEqual(p["inline_segments"], [{"kind": "text", "text": "antes"},
                                              {"kind": "embedded-block", "record_id": "draw-frame-0001"},
                                              {"kind": "text", "text": "depois"}])
        self.assertEqual(m["assets"][0]["width_px"], 12)
        self.assertEqual(m["assets"][0]["height_px"], 34)
        self.assertEqual(m["assets"][0]["occurrence_ids"], ["draw-image-0001"])
        frame_h = next(r for r in m["records"] if r["id"] == "text-h-0002")
        self.assertEqual(frame_h["semantic_type"], "anchor-container")
        self.assertEqual(m["counts"]["captions"], 1)
        self.assertEqual(len(m["units"]), 2)

    def test_index_cache_is_not_authored_text(self):
        package(self.source, '<text:table-of-content><text:index-body><text:p><text:a xlink:href="#old">Sprint 99</text:a></text:p><text:h text:outline-level="1">Cache</text:h></text:index-body></text:table-of-content><text:p>real</text:p>')
        m = extract_manifest(self.source)
        self.assertEqual(m["units"][0]["source_text"], ["real"])
        self.assertEqual(m["counts"]["hyperlinks_authored"], 0)
        self.assertEqual(len(m["units"]), 1)

    def test_lists_and_objects_are_traced_not_flattened(self):
        package(self.source, '<text:list text:style-name="L"><text:list-item text:start-value="3"><text:p>um</text:p><text:list><text:list-item><text:p>dois</text:p></text:list-item></text:list></text:list-item></text:list><text:p><draw:frame><draw:object xlink:href="../missing"/></draw:frame></text:p>')
        m = extract_manifest(self.source)
        item = next(r for r in m["records"] if r["id"] == "text-list-item-0001")
        self.assertEqual(item["list_context"]["start_value"], "3")
        self.assertEqual(item["list_context"]["style_name"], "L")
        second_list = next(r for r in m["records"] if r["id"] == "text-list-0002")
        self.assertEqual(second_list["list_context"]["xml_depth"], 2)
        obj = next(r for r in m["records"] if r["semantic_type"] == "embedded-object")
        self.assertIn(obj["id"], m["units"][0]["record_ids"])
        self.assertEqual(m["extraction"]["issues"][0]["code"], "unresolved-resource")

    def test_embedded_xml_and_object_bytes_require_review(self):
        package(self.source, '<text:p><draw:frame><draw:object xlink:href="./Object 1"/></draw:frame></text:p>',
                {"Object 1/content.xml": '<math:math xmlns:math="http://www.w3.org/1998/Math/MathML"><math:mi>x</math:mi></math:math>'})
        m = extract_manifest(self.source)
        obj = next(r for r in m["records"] if r["semantic_type"] == "embedded-object")
        self.assertEqual(obj["embedded_parts"][0]["path"], "Object 1/content.xml")
        self.assertTrue(any(r["semantic_type"] == "embedded-data" for r in m["records"]))
        self.assertEqual({i["code"] for i in m["extraction"]["issues"]},
                         {"embedded-xml-review-required", "embedded-object-review-required"})

    def test_reverification_detects_text_order_omission_and_hash_tampering(self):
        package(self.source, '<text:p>á, X!</text:p><text:p>segundo</text:p>')
        m = extract_manifest(self.source)
        self.assertEqual(verify_manifest(m, self.source), [])
        changed = copy.deepcopy(m)
        p = next(r for r in changed["records"] if r["type"] == "text:p")
        p["text"] = "a X"
        changed["units"][0]["source_record_ids"].reverse()
        changed["package_entries"].pop()
        changed["source"]["sha256"] = "0" * 64
        diffs = verify_manifest(changed, self.source)
        self.assertTrue(any(d["path"].endswith(".text") for d in diffs))
        self.assertTrue(any("source_record_ids" in d["path"] for d in diffs))
        self.assertTrue(any(d["code"] == "manifest-length-mismatch" for d in diffs))
        self.assertTrue(any(d["path"] == "$.source.sha256" for d in diffs))

    def test_dtd_is_rejected_without_resolution(self):
        with zipfile.ZipFile(self.source, "w") as z:
            z.writestr("content.xml", '<!DOCTYPE x [<!ENTITY y "bad">]><x>&y;</x>')
        with self.assertRaisesRegex(ValueError, "DTD/entity"):
            extract_manifest(self.source)


class AuditedDocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ROOT / "RELATORIO_ATUAL.odt"
        cls.manifest = extract_manifest(cls.source)

    def test_audited_baseline_and_counts(self):
        m = self.manifest
        self.assertEqual(m["source"]["sha256"], AUDITED_SOURCE)
        expected = {"package_entries": 51, "xml_parts": 6, "xml_nodes": 9298,
                    "content_xml_nodes": 8136, "paragraphs": 1634, "headings": 123,
                    "lists": 281, "list_items": 230, "list_headers": 75,
                    "frames": 86, "text_boxes": 52, "images": 34,
                    "hyperlinks": 188, "hyperlinks_authored": 84,
                    "reflections": 17, "captions": 34, "tables": 0,
                    "references": 36, "acronyms": 39,
                    "document_media": 34, "sprint_units": 25}
        for field, value in expected.items():
            with self.subTest(field=field):
                self.assertEqual(m["counts"][field], value)

    def test_audited_exceptions_and_empty_recorda_are_preserved(self):
        m = self.manifest
        records = {r["id"]: r for r in m["records"]}
        units = {u["id"]: u for u in m["units"]}
        self.assertEqual(records["text-h-0068"]["semantic_type"], "paragraph")
        self.assertEqual(records["text-h-0068"]["unit_id"], "ages-ii-sprint-4")
        for heading in ("text-h-0081", "text-h-0088"):
            self.assertEqual(records[heading]["semantic_type"], "anchor-container")
            self.assertIsNotNone(records[heading]["unit_id"])
        self.assertEqual(records["draw-text-box-0035"]["unit_id"], "ages-iii-sprint-0")
        self.assertEqual(records["text-h-0118"]["unit_id"], "ages-iv-sprint-1")
        self.assertEqual(records["text-h-0023"]["unit_id"], "chapter-03-text-h-0023")
        for n in (2, 3, 4):
            self.assertTrue(units[f"ages-iv-sprint-{n}"]["empty"])
        self.assertFalse(units["ages-iv-sprint-1"]["empty"])

    def test_manifest_file_is_reproducible_and_every_xml_node_has_parent(self):
        stored = json.loads((ROOT / "docs/CONTENT_MANIFEST.json").read_text())
        inventory = dict(stored)
        inventory.pop("migration_overlay", None)
        self.assertEqual(inventory, self.manifest)
        self.assertEqual(verify_manifest(stored, self.source), [])
        records = {r["id"]: r for r in stored["records"]}
        self.assertEqual(len(records), 9298)
        for record in records.values():
            if record["parent_id"] is not None:
                self.assertIn(record["parent_id"], records)
            self.assertEqual(len(record["xml_sha256"]), 64)

    def test_overlay_does_not_hide_source_mutation_or_wrong_scope(self):
        stored = json.loads((ROOT / "docs/CONTENT_MANIFEST.json").read_text())
        if "migration_overlay" not in stored:
            self.skipTest("No migration task registered yet")
        self.assertEqual(verify_manifest(stored, self.source), [])
        task = stored["migration_overlay"]["tasks"]["ages-i-sprint-0"]
        task["scope"] = ["ages-i-sprint-1"]
        self.assertTrue(any(x["code"] == "manifest-overlay-source-mismatch" for x in verify_manifest(stored, self.source)))
        stored["records"][0]["xml_sha256"] = "0" * 64
        self.assertTrue(any(x["code"] == "manifest-value-mismatch" for x in verify_manifest(stored, self.source)))


if __name__ == "__main__":
    unittest.main()
