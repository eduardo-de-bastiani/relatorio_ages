"""Adversarial provenance/citation gates for the authorized three-unit rewrite.

None of these tests claims semantic equivalence of rewritten project narrative.
Real ledgers are exercised, then isolated copies are deliberately corrupted.
"""
import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.migration_harness import technology_prose as prose
from scripts.migration_harness.preservation import audit_conversion, _load_presentation_authorization


class TechnologyProseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.approval = prose.load_authorization(cls.repo)
        complete = json.loads((cls.repo / "docs/CONTENT_MANIFEST.json").read_text())
        unit_ids = set(prose.UNITS)
        record_ids = {rid for policy in cls.approval["units"].values() for rid in policy["source_record_ids"]}
        cls.manifest_template = {
            "source": complete["source"], "assets": [],
            "units": [unit for unit in complete["units"] if unit["id"] in unit_ids],
            "records": [record for record in complete["records"] if record["id"] in record_ids],
        }

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.uid = "chapter-05-text-h-0085"
        self.manifest = copy.deepcopy(self.manifest_template)
        paths = [prose.AUTHORIZATION, self.approval["bibliography"]["path"]]
        for policy in self.approval["units"].values():
            paths.extend((policy["tex_path"], policy["ledger_path"]))
        paths.extend(["docs/CONTENT_MANIFEST.json", "RELATORIO_ATUAL.odt"])
        paths.extend(
            str(path.relative_to(self.repo))
            for path in (self.repo / "migration/approvals").glob("*.json")
        )
        for raw in paths:
            target = self.root / raw
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.repo / raw, target)
        shutil.copyfile(self.repo / self.approval["source"]["path"], self.root / self.approval["source"]["path"])
        self.select(self.uid)

    def select(self, uid):
        self.uid = uid
        policy = self.approval["units"][uid]
        self.ledger = json.loads((self.root / policy["ledger_path"]).read_text())
        self.unit_ledger = self.ledger["units"][uid]
        self.target = self.root / policy["tex_path"]

    def verify(self):
        document_ids = self.unit_ledger.get("document_reordering_authorization", {}).get("source_ids")
        heading_display = None
        if document_ids is not None:
            authorization = _load_presentation_authorization(self.repo, self.uid)
            heading_id = next(item for item in self.manifest["units"] if item["id"] == self.uid)["heading_id"]
            heading_display = authorization["approved_document_reordering"]["scope"]["heading_numbering"][heading_id]["target_text"]
        return prose.verify(
            self.manifest, self.ledger, self.root, self.uid,
            document_reordering_ids=document_ids,
            heading_display_text=heading_display,
        )

    def audit(self):
        return audit_conversion(self.manifest, self.ledger, self.root, self.uid)

    def replace(self, old, new, update_spans=True, update_hash=True):
        """Rebase intervals so tests attack the rule, not only a stale hash."""
        data = self.target.read_bytes()
        old, new = old.encode(), new.encode()
        start = data.index(old)
        end, delta = start + len(old), len(new) - len(old)
        changed = data[:start] + new + data[end:]
        self.target.write_bytes(changed)
        for mapping in self.unit_ledger["element_map"] + self.unit_ledger["bookmark_map"]:
            if update_spans:
                for name in ("start_byte", "end_byte"):
                    offset = mapping[name]
                    if offset >= end:
                        mapping[name] += delta
                    elif start < offset < end:
                        mapping[name] = start if name == "start_byte" else start + len(new)
            if update_hash:
                mapping["target_sha256"] = hashlib.sha256(changed).hexdigest()

    def test_three_actual_units_have_traceability_but_no_semantic_pass(self):
        for uid in prose.UNITS:
            with self.subTest(unit=uid):
                self.select(uid)
                facts = self.verify()
                self.assertFalse(facts["lexical_equality_claimed"])
                self.assertEqual(facts["semantic_review"]["status"], "PENDING")
                self.assertEqual(facts["visual_review"], "PENDING")
                report = self.audit()
                self.assertEqual(report["status"], "pass", report["findings"])
                self.assertEqual(report["facts"]["text_records_matched"], 0)
                self.assertTrue(any(item["code"] == "technology_prose_independent_review_required" for item in report["findings"]))

    def test_document_order_extension_is_explicit_and_unit_scoped(self):
        unit = next(item for item in self.manifest["units"] if item["id"] == self.uid)
        heading_id = unit["heading_id"]
        self.unit_ledger["document_reordering_authorization"] = {
            "authorization_evidence": "migration/approvals/cliente-hoortech-and-document-order-authorization.json",
            "source_ids": [heading_id],
        }
        with self.assertRaisesRegex(ValueError, "missing fields"):
            prose.verify(self.manifest, self.ledger, self.root, self.uid)
        result = prose.verify(
            self.manifest, self.ledger, self.root, self.uid,
            document_reordering_ids=[heading_id],
            heading_display_text=_load_presentation_authorization(self.repo, self.uid)["approved_document_reordering"]["scope"]["heading_numbering"][heading_id]["target_text"],
        )
        self.assertEqual(result["unit_id"], self.uid)
        self.unit_ledger["document_reordering_authorization"]["source_ids"].append("text-p-0001")
        with self.assertRaisesRegex(ValueError, "document-order scope"):
            prose.verify(
                self.manifest, self.ledger, self.root, self.uid,
                document_reordering_ids=[heading_id],
                heading_display_text=_load_presentation_authorization(self.repo, self.uid)["approved_document_reordering"]["scope"]["heading_numbering"][heading_id]["target_text"],
            )

    def test_missing_source_narrative_mapping_rejected(self):
        self.unit_ledger["element_map"].pop(1)
        with self.assertRaisesRegex(ValueError, "element mappings"):
            self.verify()

    def test_missing_and_extra_source_record_ids_rejected(self):
        unit = next(item for item in self.manifest["units"] if item["id"] == self.uid)
        for ids in (unit["record_ids"][:-1], unit["record_ids"] + ["text-p-9999"]):
            with self.subTest(ids=ids[-2:]):
                original = unit["record_ids"]
                unit["record_ids"] = ids
                with self.assertRaisesRegex(ValueError, "source IDs"):
                    self.verify()
                unit["record_ids"] = original

    def test_wrong_and_duplicate_mapping_ids_rejected(self):
        self.unit_ledger["element_map"][1]["source_id"] = "text-p-9999"
        with self.assertRaisesRegex(ValueError, "element mappings"):
            self.verify()
        self.unit_ledger["element_map"][1]["source_id"] = self.unit_ledger["element_map"][0]["source_id"]
        with self.assertRaisesRegex(ValueError, "element mappings"):
            self.verify()

    def test_reordered_source_mappings_rejected(self):
        self.unit_ledger["element_map"][1:3] = reversed(self.unit_ledger["element_map"][1:3])
        with self.assertRaisesRegex(ValueError, "element mappings"):
            self.verify()

    def test_stale_target_hash_rejected(self):
        self.replace("utilizamos", "empregamos", update_hash=False)
        with self.assertRaisesRegex(ValueError, "stale prose target"):
            self.verify()

    def test_stale_source_hash_rejected(self):
        self.unit_ledger["element_map"][1]["source_text_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "original text hash"):
            self.verify()

    def test_forged_source_wording_even_with_ledger_hash_rejected(self):
        record = next(item for item in self.manifest["records"] if item["id"] == "text-p-1066")
        record["text"] += " invented"
        self.unit_ledger["element_map"][1]["source_text_sha256"] = hashlib.sha256(record["text"].encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, "frozen original"):
            self.verify()

    def test_invalid_utf8_span_and_outside_interval_rejected(self):
        mapping = self.unit_ledger["element_map"][1]
        data = self.target.read_bytes()
        offset = data.index("maturidade".encode())
        accent = data.index("integração".encode(), offset) + len("integra".encode()) + 1
        mapping["start_byte"] = accent
        with self.assertRaises(UnicodeError):
            self.verify()
        mapping["start_byte"] = -1
        with self.assertRaisesRegex(ValueError, "byte interval"):
            self.verify()

    def test_altered_original_url_and_anchor_inventory_rejected(self):
        link = self.unit_ledger["documentation_links"][0]
        for key in ("anchor", "url"):
            before = link[key]
            link[key] += "invented"
            with self.assertRaisesRegex(ValueError, "URL/anchor"):
                self.verify()
            link[key] = before

    def test_docker_label_without_original_href_gets_no_invented_url(self):
        self.select("chapter-04-text-h-0046")
        self.assertEqual(len(self.unit_ledger["documentation_links"]), 7)
        self.unit_ledger["documentation_links"].append({"source_id": "text-p-0839", "anchor": "Docker", "url": "https://docker.example"})
        with self.assertRaisesRegex(ValueError, "URL/anchor"):
            self.verify()

    def test_omission_applied_to_description_rejected(self):
        mapping = self.unit_ledger["element_map"][1]
        mapping["disposition"] = "omitted_documentation_label"
        mapping["end_byte"] = mapping["start_byte"]
        with self.assertRaisesRegex(ValueError, "source narrative"):
            self.verify()

    def test_documentation_omission_requires_empty_logical_interval(self):
        mapping = next(item for item in self.unit_ledger["element_map"] if item["disposition"] == "omitted_documentation_label")
        mapping["end_byte"] += 1
        with self.assertRaisesRegex(ValueError, "empty target spans"):
            self.verify()

    def test_original_heading_and_bookmark_identity_preserved(self):
        self.unit_ledger["bookmark_map"][0]["target_anchor"] = "invented"
        with self.assertRaisesRegex(ValueError, "bookmark identity"):
            self.verify()

    def test_heading_scaffolding_cannot_be_repeated_or_hidden_in_prose(self):
        self.replace("No backend", r"\subsection{Extra} No backend")
        with self.assertRaisesRegex(ValueError, "scaffold"):
            self.verify()

    def test_documentation_labels_and_boilerplate_rejected_even_when_mapped(self):
        for insertion in ("Documentação C#. ", "Mais informações podem ser encontradas em: "):
            with self.subTest(insertion=insertion):
                self.select(self.uid)
                original_data = self.target.read_bytes()
                self.replace("No backend", insertion + "No backend")
                with self.assertRaisesRegex(ValueError, "documentation"):
                    self.verify()
                self.target.write_bytes(original_data)

    def test_ages_iv_allows_source_documentation_prose_but_rejects_link_boilerplate(self):
        uid = prose.AIV_UNIT
        heading = prose.AGES_IV_HEADING
        _, heading_id, number, anchor, _, _ = heading
        full_title = f"{number} Tecnologias utilizadas"
        required = list(prose.AIV_REFERENCE_KEYS)
        citation_terms = {key: list(value[1]) for key, value in prose.AIV_REFERENCE_KEYS.items()}
        citations = " ".join(
            f"{citation_terms[key][0]} \\cite{{{prose.AIV_REFERENCE_KEYS[key][0]}}}"
            for key in required
        )
        header = (
            f"\\hypertarget{{{anchor}}}{{}}\n"
            "\\refstepcounter{subsection}\n"
            f"\\subsection*{{{full_title}}}\n"
            f"\\label{{ages-iv:{heading_id}}}\n"
            f"\\addcontentsline{{toc}}{{subsection}}{{{full_title}}}\n"
        )
        policy = {
            "required_citation_keys": [prose.AIV_REFERENCE_KEYS[key][0] for key in required],
            "citation_terms": {
                prose.AIV_REFERENCE_KEYS[key][0]: citation_terms[key]
                for key in required
            },
            "allow_narrative_documentation_mentions": True,
        }
        narrative = header + "A API fornece documentação automática OpenAPI. " + citations
        _, parsed, _ = prose._grammar(narrative, uid, policy)
        self.assertEqual(len(parsed), 13)
        for insertion, message in (
            ("Documentação FastAPI. ", "Standalone documentation labels"),
            ("Mais informações podem ser encontradas em: ", "Standalone documentation labels"),
        ):
            with self.subTest(insertion=insertion):
                with self.assertRaisesRegex(ValueError, message):
                    prose._grammar(header + insertion + citations, uid, policy)

    def test_direct_href_and_url_in_body_rejected(self):
        for command in (r"\href{https://example.test}{C\#}", r"\url{https://example.test}"):
            with self.subTest(command=command):
                self.select(self.uid)
                original_data = self.target.read_bytes()
                self.replace("No backend", command + " No backend")
                with self.assertRaisesRegex(ValueError, "Unauthorized prose TeX command"):
                    self.verify()
                self.target.write_bytes(original_data)

    def test_detached_colon_and_unknown_citations_rejected(self):
        variants = [
            (r"C\# \cite{ages-iii-csharp}", r"C\#: \cite{ages-iii-csharp}"),
            (r"C\# \cite{ages-iii-csharp}", r"C\# no projeto \cite{ages-iii-csharp}"),
            (r"\cite{ages-iii-csharp}", r"\cite{unapproved-key}"),
            (r"\cite{ages-iii-csharp}", r"\cite{ages-iii-csharp,ages-iii-dotnet}"),
            (r"\cite{ages-iii-csharp}", r"\cite[2026]{ages-iii-csharp}"),
        ]
        original_data = self.target.read_bytes()
        for old, new in variants:
            with self.subTest(new=new):
                self.select(self.uid)
                self.replace(old, new)
                with self.assertRaisesRegex(ValueError, "citation"):
                    self.verify()
                self.target.write_bytes(original_data)

    def test_missing_required_citation_rejected(self):
        self.replace(r"\cite{ages-iii-csharp}", "")
        with self.assertRaisesRegex(ValueError, "Missing required"):
            self.verify()

    def test_technology_colon_labels_rejected(self):
        self.replace("No backend", "React: No backend")
        with self.assertRaisesRegex(ValueError, "Bare technology label"):
            self.verify()

    def test_raw_url_cannot_bypass_prohibition_on_href(self):
        self.replace("No backend", "https://invented.example No backend")
        with self.assertRaisesRegex(ValueError, "prose URLs"):
            self.verify()

    def test_review_limitations_cannot_be_silently_cleared(self):
        self.unit_ledger["pending"] = []
        with self.assertRaisesRegex(ValueError, "retain explicit"):
            self.verify()

    def test_hidden_text_commands_lists_and_page_breaks_rejected(self):
        original_data = self.target.read_bytes()
        for command in (r"\phantom{forged}", r"\input{forged}", r"\newcommand{\hack}{x}", r"\begin{itemize}\item", r"\pagebreak", r"\vspace{10cm}", r"\color{white}"):
            with self.subTest(command=command):
                self.select(self.uid)
                self.replace("No backend", command + " No backend")
                with self.assertRaises(ValueError):
                    self.verify()
                self.target.write_bytes(original_data)

    def test_extra_visible_target_text_outside_spans_rejected(self):
        data = self.target.read_bytes() + b"\nInvented untracked content.\n"
        self.target.write_bytes(data)
        for mapping in self.unit_ledger["element_map"] + self.unit_ledger["bookmark_map"]:
            mapping["target_sha256"] = hashlib.sha256(data).hexdigest()
        with self.assertRaisesRegex(ValueError, "outside technology source spans"):
            self.verify()

    def test_missing_structural_source_container_rejected(self):
        self.unit_ledger["structural_dispositions"].pop()
        with self.assertRaisesRegex(ValueError, "container coverage"):
            self.verify()

    def test_stale_bibliography_rejected(self):
        path = self.root / self.approval["bibliography"]["path"]
        path.write_bytes(path.read_bytes() + b"\n@online{invented, title={Forged}}\n")
        with self.assertRaisesRegex(ValueError, "Bibliography differs"):
            self.verify()

    def test_missing_and_stale_authorization_fail_closed(self):
        path = self.root / prose.AUTHORIZATION
        original = path.read_bytes()
        for data in (None, original + b"\n"):
            with self.subTest(absent=data is None):
                if data is None:
                    path.unlink()
                else:
                    path.write_bytes(data)
                report = self.audit()
                self.assertEqual(report["status"], "blocked")
                self.assertTrue(any(item["code"] == "invalid_technology_prose_revision" for item in report["findings"]))

    def test_wrong_scope_authorization_rejected(self):
        approval = copy.deepcopy(self.approval)
        approval["units"]["ages-iv-sprint-0"] = approval["units"].pop(self.uid)
        (self.root / prose.AUTHORIZATION).write_text(json.dumps(approval))
        with self.assertRaisesRegex(ValueError, "authorization identity"):
            self.verify()

    def test_new_ledger_in_other_unit_fails_instead_of_legacy_fallback(self):
        unit = next(item for item in self.manifest["units"] if item["id"] == self.uid)
        unit["id"] = "ages-iv-sprint-0"
        self.ledger["units"][unit["id"]] = self.ledger["units"].pop(self.uid)
        self.uid = unit["id"]
        report = self.audit()
        self.assertEqual(report["status"], "blocked")
        self.assertIn("outside the three authorized", str(report["findings"]))

    def test_approval_present_disallows_legacy_ledger_fallback(self):
        self.unit_ledger.pop("technology_prose_revision")
        report = self.audit()
        self.assertEqual(report["status"], "blocked")
        self.assertIn("legacy presentation is revoked", str(report["findings"]))

    def test_revisions_cannot_claim_automatic_semantic_acceptance(self):
        self.unit_ledger["technology_prose_revision"]["semantic_review"] = "pass"
        with self.assertRaisesRegex(ValueError, "revision policy"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
