import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.migration_harness import bibliography_reconciliation as reconciliation


class BibliographyReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.contract = json.loads((cls.repo / reconciliation.CONTRACT).read_text(encoding="utf-8"))
        cls.result = (cls.repo / cls.contract["result"]["path"]).read_bytes()

    def test_historical_and_consolidated_fixtures_reproduce_exact_contract(self):
        facts = reconciliation.verify_historical(self.repo, data=self.result)
        self.assertEqual(facts, {
            "source_entries": 55,
            "result_entries": 49,
            "consolidations": 6,
            "estimated_dates": 44,
            "factual_dates": 5,
            "publication_years_inferred_from_estimates": 0,
        })

    def test_unapproved_url_change_fails_even_when_shape_is_unchanged(self):
        altered = self.result.replace(b"https://www.typescriptlang.org/docs/", b"https://example.invalid/docs/", 1)
        with self.assertRaisesRegex(ValueError, "exact approved bibliography"):
            reconciliation.verify_historical(self.repo, altered)

    def test_estimated_date_cannot_be_promoted_to_year_field(self):
        altered = self.result.replace(b"  date = {2026?},", b"  year = {2026},\n  date = {2026?},", 1)
        with self.assertRaisesRegex(ValueError, "exact approved bibliography"):
            reconciliation.verify_historical(self.repo, altered)

    def test_consolidation_mapping_is_explicit_and_exact(self):
        self.assertEqual(self.contract["consolidations"], {
            "ages-iv-typescript": "typescript-docs",
            "react-docs": "ages-iii-react",
            "postgresql-docs": "ages-iv-postgresql",
            "ages-ii-postgresql": "ages-iv-postgresql",
            "ages-ii-figma": "ages-i-figma",
            "ages-ii-docker": "ages-iii-docker",
        })

    def test_altered_contract_or_remap_fails_against_code_pinned_approval(self):
        raw = (self.repo / reconciliation.CONTRACT).read_bytes()
        altered = json.loads(raw)
        altered["consolidations"]["react-docs"] = "forged-key"
        with self.assertRaisesRegex(ValueError, "pinned approval"):
            reconciliation._validate_contract(self.repo, altered, json.dumps(altered).encode())

    def test_altered_fixture_hash_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "exact approved bibliography"):
            reconciliation.verify_historical(self.repo, self.result + b"\n")

    def test_factual_date_cannot_be_reclassified_as_an_estimate(self):
        evidence = json.loads((self.repo / reconciliation.EVIDENCE_PATH).read_text(encoding="utf-8"))
        entries = reconciliation._entries(self.result)
        key = "ages-ii-http-rfc9110"
        date = evidence["factual_dates_preserved"].pop(key)
        evidence["estimated_entries"][key] = {"ano": date + "?"}
        with self.assertRaisesRegex(ValueError, "factual publication dates"):
            reconciliation._validate_date_status(evidence, entries)

    def test_estimated_date_must_match_pinned_edtf_value(self):
        evidence = json.loads((self.repo / reconciliation.EVIDENCE_PATH).read_text(encoding="utf-8"))
        entries = reconciliation._entries(self.result)
        key = "typescript-docs"
        entry_type, body = entries[key]
        entries[key] = (entry_type, body.replace("date = {2026?}", "date = {2025?}"))
        with self.assertRaisesRegex(ValueError, "Estimated date"):
            reconciliation._validate_date_status(evidence, entries)

    def test_supplemental_contract_accepts_current_integrated_bibliography(self):
        facts = reconciliation.verify(self.repo)
        self.assertEqual(facts, {
            "source_entries": 55,
            "result_entries": 49,
            "consolidations": 6,
            "estimated_dates": 44,
            "factual_dates": 5,
            "publication_years_inferred_from_estimates": 0,
            "removed_estimated_dates": 44,
            "added_verified_access_dates": 2,
            "updated_titles": 2,
            "normalized_authors": 3,
            "author_confirmed_years": 44,
            "estimated_access_dates": 49,
            "documented_dates_preserved": 5,
            "independent_evidence_claimed": 0,
            "removed_estimated_access_notes": 49,
            "varied_estimated_access_dates": 49,
            "publication_date_fields_unchanged": 49,
            "current_entries": 49,
        })

    def test_supplemental_url_change_is_rejected(self):
        current = (self.repo / reconciliation.SUPPLEMENT_RESULT_PATH).read_bytes()
        changed = current.replace(b"https://www.figma.com}", b"https://example.invalid}", 1)
        with self.assertRaisesRegex(ValueError, "exact approved bibliography state"):
            reconciliation.verify(self.repo, changed)

    def test_supplemental_new_publication_date_is_rejected(self):
        current = (self.repo / reconciliation.SUPPLEMENT_RESULT_PATH).read_bytes()
        changed = current.replace(
            b"  title = {Documenta\xc3\xa7\xc3\xa3o Python 3},",
            b"  title = {Documenta\xc3\xa7\xc3\xa3o Python 3},\n  year = {2026},",
            1,
        )
        with self.assertRaisesRegex(ValueError, "exact approved bibliography state"):
            reconciliation.verify(self.repo, changed)

    def test_supplemental_access_date_cannot_be_changed_or_added_as_publication_date(self):
        current = (self.repo / reconciliation.SUPPLEMENT_RESULT_PATH).read_bytes()
        changed = current.replace(b"urldate = {2026-11-06}", b"date = {2026-11-06}", 1)
        with self.assertRaisesRegex(ValueError, "exact approved bibliography state"):
            reconciliation.verify(self.repo, changed)

    def test_supplemental_contract_hash_is_pinned(self):
        raw = (self.repo / reconciliation.SUPPLEMENT_CONTRACT).read_bytes()
        changed = json.loads(raw)
        changed["authorized_changes"]["updated_titles"]["ages-i-figma"]["to"] = "forged"
        with self.assertRaisesRegex(ValueError, "pinned approval"):
            reconciliation._validate_supplement_contract_data(
                self.repo, json.dumps(changed, ensure_ascii=False).encode("utf-8")
            )

    def test_unlisted_field_change_fails_supplemental_diff(self):
        contract = reconciliation._validate_supplement_contract(self.repo)
        source = (self.repo / contract["source"]["path"]).read_bytes()
        result = (self.repo / contract["result"]["path"]).read_bytes()
        changed = result.replace(b"title = {Figma: The collaborative canvas for design, code, and AI}",
                                b"title = {Figma: Unauthorized title}", 1)
        with self.assertRaisesRegex(ValueError, "unapproved field changes"):
            reconciliation._validate_supplement_diff(self.repo, source, changed, contract)

    def test_author_informed_contract_records_no_independent_evidence(self):
        contract = reconciliation._validate_author_contract(self.repo)
        facts = reconciliation.verify_author_informed(self.repo)
        self.assertEqual(len(contract["author_informed_values"]["confirmed_years_by_author"]), 44)
        self.assertEqual(len(contract["author_informed_values"]["estimated_access_dates_by_author"]), 49)
        self.assertEqual(facts["independent_evidence_claimed"], 0)
        self.assertEqual(facts["documented_dates_preserved"], 5)

    def test_author_informed_diff_rejects_any_unlisted_field_change(self):
        contract = reconciliation._validate_author_contract(self.repo)
        source = (self.repo / contract["source"]["path"]).read_bytes()
        result = (self.repo / contract["result"]["path"]).read_bytes()
        changed = result.replace(b"Data de acesso estimada", b"Data de acesso comprovada", 1)
        with self.assertRaisesRegex(ValueError, "outside its precise field map"):
            reconciliation._validate_author_informed_diff(source, changed, contract)

    def test_author_informed_date_cannot_be_promoted_to_year_field(self):
        contract = reconciliation._validate_author_contract(self.repo)
        source = (self.repo / contract["source"]["path"]).read_bytes()
        result = (self.repo / contract["result"]["path"]).read_bytes()
        changed = result.replace(b"  date = {2026},", b"  year = {2026},\n  date = {2026},", 1)
        with self.assertRaisesRegex(ValueError, "outside its precise field map"):
            reconciliation._validate_author_informed_diff(source, changed, contract)

    def test_author_informed_contract_hash_is_pinned(self):
        raw = (self.repo / reconciliation.AUTHOR_CONTRACT).read_bytes()
        changed = json.loads(raw)
        changed["author_informed_values"]["estimated_access_dates_by_author"]["typescript-docs"] = "2026-11-06"
        with self.assertRaisesRegex(ValueError, "pinned approval"):
            reconciliation._validate_author_contract_data(self.repo, json.dumps(changed).encode())

    def test_estimated_access_final_state_is_pinned_and_chained(self):
        facts = reconciliation.verify(self.repo)
        self.assertEqual(facts["removed_estimated_access_notes"], 49)
        self.assertEqual(facts["varied_estimated_access_dates"], 49)
        self.assertEqual(facts["publication_date_fields_unchanged"], 49)
        contract = reconciliation._validate_estimated_access_contract(self.repo)
        self.assertEqual(contract["source"]["contract"], reconciliation.AUTHOR_CONTRACT)
        self.assertEqual(len(contract["authorized_changes"]["varied_estimated_access_dates"]), 49)

    def test_estimated_access_notes_must_be_absent_from_all_final_entries(self):
        current = (self.repo / reconciliation.ESTIMATED_ACCESS_RESULT_PATH).read_bytes()
        changed = current.replace(b"  urldate = {2024-04-26},", b"  urldate = {2024-04-26},\n  note = {Data de acesso estimada},", 1)
        with self.assertRaisesRegex(ValueError, "exact approved bibliography state"):
            reconciliation.verify(self.repo, changed)

    def test_every_varied_access_date_is_evidence_bound(self):
        current = (self.repo / reconciliation.ESTIMATED_ACCESS_RESULT_PATH).read_bytes()
        changed = current.replace(b"urldate = {2024-04-26}", b"urldate = {2024-04-27}", 1)
        with self.assertRaisesRegex(ValueError, "exact approved bibliography state"):
            reconciliation.verify(self.repo, changed)

    def test_publication_dates_cannot_change_in_final_access_date_layer(self):
        current = (self.repo / reconciliation.ESTIMATED_ACCESS_RESULT_PATH).read_bytes()
        changed = current.replace(b"date = {2026},", b"date = {2025},", 1)
        with self.assertRaisesRegex(ValueError, "exact approved bibliography state"):
            reconciliation.verify(self.repo, changed)

    def test_final_contract_and_evidence_are_pinned(self):
        raw = (self.repo / reconciliation.ESTIMATED_ACCESS_CONTRACT).read_bytes()
        changed = json.loads(raw)
        changed["authorized_changes"]["varied_estimated_access_dates"]["typescript-docs"] = "2025-11-16"
        with self.assertRaisesRegex(ValueError, "pinned approval"):
            reconciliation._validate_estimated_access_contract_data(
                self.repo, json.dumps(changed, ensure_ascii=False).encode("utf-8")
            )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in ("RELATORIO_ATUAL.odt", reconciliation.ESTIMATED_ACCESS_EVIDENCE_PATH):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.repo / relative, target)
            tampered_contract = (self.repo / reconciliation.ESTIMATED_ACCESS_CONTRACT).read_bytes()
            tampered_contract_path = root / reconciliation.ESTIMATED_ACCESS_CONTRACT
            tampered_contract_path.parent.mkdir(parents=True, exist_ok=True)
            tampered_contract_path.write_bytes(tampered_contract)
            self.assertEqual(
                reconciliation._validate_estimated_access_contract_data(root, tampered_contract)["result"]["sha256"],
                reconciliation.ESTIMATED_ACCESS_RESULT_SHA256,
            )
            evidence_path = root / reconciliation.ESTIMATED_ACCESS_EVIDENCE_PATH
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["access_dates"]["typescript-docs"] = "2025-11-16"
            evidence_path.write_text(json.dumps(evidence, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "evidence differs from its pinned record"):
                reconciliation._validate_estimated_access_contract_data(root, tampered_contract)


if __name__ == "__main__":
    unittest.main()
