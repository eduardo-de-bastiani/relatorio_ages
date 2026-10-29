"""Adversarial synthetic fixtures; no memorial content is converted."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.migration_harness.preservation import (
    audit_conversion,
    displayed_text,
    _parse_user_supplied_markup,
    UnsupportedSerialization,
    _project_approved_presentation,
    _project_approved_toc_entry,
    _verify_document_order_unit,
    _is_authorized_ages_iii_group_label_removal,
    AGES_III_PROTOTYPE_GROUP_LABELS,
    PRESENTATION_HEADINGS,
    PRESENTATION_CAPTIONS,
    PRESENTATION_REPOSITORY_PARAGRAPHS,
    PRESENTATION_REPOSITORY_LINKS,
    PRESENTATION_CROSS_REFERENCES,
    PRESENTATION_LIST_MARKERS,
    PRESENTATION_LIST_MARKER_INSTRUCTION,
    PRESENTATION_OVERRIDES_BY_UNIT,
    _verify_markerless_list,
    TECHNOLOGY_PARAGRAPH_AUTHORIZATION,
    TECHNOLOGY_PARAGRAPH_RECORDS,
    _verify_technology_paragraph,
    _verify_ages_ii_technology_paragraph,
    _verify_ages_iii_technology_paragraph,
    _verify_ages_iv_partial_source_scope,
    _is_authorized_ages_iv_presentation,
    AGES_IV_UNITS,
    AGES_IV_TITLE_ONLY_UNIT,
    AGES_IV_TITLE_ONLY_OMITTED_IDS,
    FRONTMATTER_UNITS,
    FRONTMATTER_TRANSFORM_IDS,
    _load_presentation_authorization,
    DOCUMENT_ORDER_AUTHORIZATION,
    AGES_IV_SPRINT3_FIGURE_DISPLAY_AUTHORIZATION,
    AGES_II_TECHNOLOGY_REFERENCE_KEYS,
    AGES_II_ADDITIONAL_REFERENCE_RECORDS,
    AGES_II_RFC_REFERENCE_FIELDS,
    AGES_II_TECHNOLOGY_TEXT_IDS,
    AGES_II_TECHNOLOGY_CITATIONS_AFTER,
    AGES_II_INLINE_TAB_COUNTS,
    AGES_II_LEADING_TAB_COUNTS,
    AGES_II_LEADING_SPACE_COUNTS,
    AGES_II_LEADING_LINE_BREAK_COUNTS,
    AGES_II_PRESENTATION_AUTHORIZATION,
    AGES_III_LEADING_TAB_COUNTS,
    AGES_III_INLINE_TAB_COUNTS,
    AGES_III_INTERNAL_TAB_REMOVAL_POLICY,
    AGES_III_INTERNAL_TAB_REMOVAL_AUTHORIZATION,
    AGES_I_II_WIKI_SENTENCES,
    AGES_IV_WIKI_SENTENCES,
    AGES_IV_TECHNICAL_CITATIONS,
    AGES_IV_CITATION_TERMS,
    AGES_IV_CITATION_EVIDENCE,
    AGES_IV_REPOSITORY_UNITS,
    AGES_IV_WIKI_UNITS,
    AGES_I_II_TECHNICAL_CITATIONS,
    AGES_I_II_TECHNICAL_CITATION_KEYS,
    _load_ages_i_ii_formatting_authorization,
    _citation_keys_in_fragment,
    _verify_ages_iii_bibliography_entries,
    _verify_ages_iv_bibliography_entries,
    _verify_citation_alignment,
    _is_source_heading,
    _leading_tab_paragraph_ids,
    _source_whitespace_verified,
    _strict_source,
    _project_source_text_order,
    _verify_linked_figure_source,
)


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

    def test_frontmatter_changes_are_source_bound_and_exactly_authorized(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "pretext")
        self.assertEqual(tuple(authorization["scope"]["units"]), FRONTMATTER_UNITS)
        for kind, records in authorization["scope"]["presentation_changes"].items():
            self.assertEqual(set(records), FRONTMATTER_TRANSFORM_IDS[kind])
            for source_id, spec in records.items():
                projected, evidence = _project_approved_presentation(
                    source_id, spec["source_text"], spec["target_text"], [kind], authorization,
                )
                self.assertEqual(projected, spec["source_text"])
                self.assertEqual(evidence["kind"], kind)
                self.assertEqual(evidence["displayed"], spec["target_text"])
                with self.assertRaises(UnsupportedSerialization):
                    _project_approved_presentation(
                        source_id, spec["source_text"], spec["target_text"] + " altered", [kind], authorization,
                    )

    def test_document_reordering_uses_exact_source_bound_heading_caption_and_reference_targets(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "chapter-03-text-h-0023")
        relocation = authorization["approved_document_reordering"]
        self.assertEqual(relocation["authorization_evidence"], DOCUMENT_ORDER_AUTHORIZATION)
        scope = relocation["scope"]

        for source_id, table_name in (
            ("text-h-0040", "heading_numbering"),
            ("text-p-0767", "figure_caption_numbering"),
            ("text-p-0679", "inline_reference_adjustments"),
        ):
            with self.subTest(source_id=source_id):
                entry = scope[table_name][source_id]
                projected, evidence = _project_approved_presentation(
                    source_id, entry["source_text"], entry["target_text"],
                    ["document_reordering_numbering"], authorization,
                )
                self.assertEqual(projected, entry["source_text"])
                self.assertEqual(evidence["displayed"], entry["target_text"])
                self.assertEqual(evidence["authorization_evidence"], DOCUMENT_ORDER_AUTHORIZATION)
                with self.assertRaises(UnsupportedSerialization):
                    _project_approved_presentation(
                        source_id, entry["source_text"], entry["target_text"] + " alterado",
                        ["document_reordering_numbering"], authorization,
                    )

    def test_document_reordering_rejects_unmapped_source_ids(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "chapter-03-text-h-0023")
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                "text-p-0768", "texto", "texto alterado",
                ["document_reordering_numbering"], authorization,
            )

    def test_document_order_unit_checks_exact_mapping_and_rendered_heading(self):
        repo = Path(__file__).resolve().parents[1]
        uid = "chapter-04-text-h-0046"
        authorization = _load_presentation_authorization(repo, uid)
        spec = authorization["approved_document_reordering"]["scope"]["heading_numbering"]["text-h-0046"]
        unit_ledger = {
            "document_reordering_authorization": {
                "authorization_evidence": DOCUMENT_ORDER_AUTHORIZATION,
                "source_ids": ["text-h-0046"],
            },
            "element_map": [{
                "source_id": "text-h-0046",
                "serializations": ["document_reordering_numbering"],
            }],
        }
        reader = lambda mapping: spec["target_text"]
        self.assertEqual(
            _verify_document_order_unit(uid, unit_ledger, {"text-h-0046": {}}, authorization, reader),
            ["text-h-0046"],
        )
        with self.assertRaises(UnsupportedSerialization):
            _verify_document_order_unit(
                uid, unit_ledger, {"text-h-0046": {}}, authorization,
                lambda mapping: spec["target_text"] + " alterado",
            )

    def test_sprint3_figure_append_is_source_bound_and_shifts_only_the_three_hoortech_figures(self):
        repo = Path(__file__).resolve().parents[1]
        auth_path = repo / AGES_IV_SPRINT3_FIGURE_DISPLAY_AUTHORIZATION
        auth = json.loads(auth_path.read_text(encoding="utf-8"))
        self.assertEqual(auth["figure_insertion"]["figure_number"], 32)
        for update in auth["following_figure_renumbering"]:
            with self.subTest(source_id=update["source_id"]):
                unit_auth = _load_presentation_authorization(repo, update["unit_id"])
                spec = unit_auth["approved_document_reordering"]["scope"]["figure_caption_numbering"][update["source_id"]]
                projected, evidence = _project_approved_presentation(
                    update["source_id"], spec["source_text"], update["target"],
                    ["document_reordering_numbering"], unit_auth,
                )
                self.assertEqual(projected, spec["source_text"])
                self.assertEqual(evidence["displayed"], update["target"])
                self.assertEqual(evidence["previous_displayed"], update["previous_target"])
                self.assertEqual(evidence["supplemental_authorization_evidence"], AGES_IV_SPRINT3_FIGURE_DISPLAY_AUTHORIZATION)
                with self.assertRaises(UnsupportedSerialization):
                    _project_approved_presentation(
                        update["source_id"], spec["source_text"], update["previous_target"],
                        ["document_reordering_numbering"], unit_auth,
                    )

    def test_sprint3_toc_adjustments_change_only_the_authorized_entries(self):
        repo = Path(__file__).resolve().parents[1]
        auth = json.loads((repo / AGES_IV_SPRINT3_FIGURE_DISPLAY_AUTHORIZATION).read_text(encoding="utf-8"))
        for update in auth["toc_entry_adjustments"]:
            with self.subTest(source_id=update["source_id"]):
                unit_auth = _load_presentation_authorization(repo, update["unit_id"])
                spec = unit_auth["approved_document_reordering"]["scope"]["heading_numbering"][update["source_id"]]
                projected, evidence = _project_approved_toc_entry(
                    update["source_id"], spec["source_text"], update["target"],
                    ["document_reordering_numbering"], unit_auth,
                )
                self.assertEqual(projected, spec["source_text"])
                self.assertEqual(evidence["displayed"], update["target"])
                self.assertTrue(evidence["body_heading_unchanged"])
                with self.assertRaises(UnsupportedSerialization):
                    _project_approved_toc_entry(
                        update["source_id"], spec["source_text"], update["target"] + " alterado",
                        ["document_reordering_numbering"], unit_auth,
                    )

    def test_frontmatter_authorization_fails_closed_for_source_or_scope_changes(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "resumo")
        authorization["scope"]["units"].append("chapter-02-text-h-0002")
        (self.root / "migration").mkdir()
        (self.root / "migration/approvals").mkdir()
        (self.root / "migration/approvals/ages-iv-frontmatter-authorization.json").write_text(
            json.dumps(authorization), encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "Frontmatter authorization"):
            _load_presentation_authorization(self.root, "resumo")

    def test_frontmatter_page_break_permission_is_exact_and_unit_scoped(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "resumo")
        controls = authorization["scope"]["layout_controls"]["resumo"]
        self.assertEqual(len(controls), 2)
        self.assertEqual([item["command"] for item in controls], ["clearpage", "clearpage"])
        controls[1]["before"] = "chapter"
        (self.root / "migration/approvals").mkdir(parents=True)
        (self.root / "migration/approvals/ages-iv-frontmatter-authorization.json").write_text(
            json.dumps(authorization), encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "Frontmatter authorization"):
            _load_presentation_authorization(self.root, "resumo")

    def test_ages_iv_authorization_and_caption_heading_overlays_are_exactly_scoped(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "chapter-06-text-h-0114")
        self.assertEqual(tuple(authorization["scope"]["units"]), AGES_IV_UNITS)
        self.assertTrue(_is_authorized_ages_iv_presentation(authorization, "text-p-1450"))
        self.assertFalse(_is_authorized_ages_iv_presentation(authorization, "text-p-1475"))
        caption = "Figure 31: Estrutura Analítica do Projeto (EAP) - AGES IV"
        projected, evidence = _project_approved_presentation(
            "text-p-1450", caption, "Figura 31 – Estrutura Analítica do Projeto (EAP) - AGES IV",
            ["abnt_figure_caption"], authorization,
        )
        self.assertEqual(projected, caption)
        self.assertEqual(evidence["kind"], "abnt_figure_caption_label")
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                "text-p-1450", caption, "Figura 31 – Estrutura alterada - AGES IV",
                ["abnt_figure_caption"], authorization,
            )
        chapter7_authorization = _load_presentation_authorization(repo, AGES_IV_TITLE_ONLY_UNIT)
        source = "7 - CONSIDERAÇÕES FINAIS (Somente AGES IV)"
        target = "7 CONSIDERAÇÕES FINAIS (Somente AGES IV)"
        self.assertEqual(PRESENTATION_HEADINGS["text-h-0123"], (source, target))
        projected, evidence = _project_approved_presentation(
            "text-h-0123", source, target,
            ["abnt_section_numbering"], chapter7_authorization,
        )
        self.assertEqual(projected, source)
        self.assertEqual(evidence["kind"], "abnt_section_numbering")
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                "text-h-0123", source, "7: CONSIDERAÇÕES FINAIS (Somente AGES IV)",
                ["abnt_section_numbering"], chapter7_authorization,
            )

    def test_ages_iv_title_only_unit_is_partial_and_omission_scope_fails_closed(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        unit = next(item for item in manifest["units"] if item["id"] == AGES_IV_TITLE_ONLY_UNIT)
        source_ids = list(unit["source_record_ids"])
        authorization = _load_presentation_authorization(repo, AGES_IV_TITLE_ONLY_UNIT)
        policy = authorization["scope"]["authorized_title_only_inclusion"]
        unit_ledger = {
            "authorized_title_only_inclusion": policy,
            "element_map": [{"source_id": "text-h-0123"}],
        }
        self.assertEqual(
            _verify_ages_iv_partial_source_scope(AGES_IV_TITLE_ONLY_UNIT, unit, unit_ledger, source_ids, authorization),
            policy,
        )
        self.assertEqual(len(AGES_IV_TITLE_ONLY_OMITTED_IDS), 18)
        self.assertEqual(len(policy["omitted_source_record_ids"]), 18)
        unit_ledger["element_map"].append({"source_id": "text-p-1539"})
        with self.assertRaisesRegex(ValueError, "map exactly its approved heading"):
            _verify_ages_iv_partial_source_scope(AGES_IV_TITLE_ONLY_UNIT, unit, unit_ledger, source_ids, authorization)
        with self.assertRaisesRegex(ValueError, "exact authorized chapter 7"):
            _verify_ages_iv_partial_source_scope("chapter-06-text-h-0122", unit, unit_ledger, source_ids, authorization)

    def test_ages_ii_presentation_reuse_authorization_is_current_and_edition_scoped(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "chapter-04-text-h-0040")
        self.assertEqual(authorization["edition"], "ages-ii")
        self.assertEqual(len(authorization["scope"]), 15)
        self.assertEqual(authorization["approved_presentation_changes"]["inline_tab_source_counts"], AGES_II_INLINE_TAB_COUNTS)
        self.assertEqual(authorization["approved_presentation_changes"]["leading_space_source_counts"], AGES_II_LEADING_SPACE_COUNTS)
        self.assertEqual(authorization["approved_presentation_changes"]["leading_line_break_source_counts"], AGES_II_LEADING_LINE_BREAK_COUNTS)
        self.assertIn("ages-ii-sprint-4", authorization["scope"])
        self.assertEqual(PRESENTATION_OVERRIDES_BY_UNIT["ages-ii-sprint-4"], {"text-p-0962"})
        self.assertNotIn("chapter-05-text-h-0074", authorization["scope"])

    def test_ages_i_presentation_authorization_remains_scoped_after_ages_ii_rules_are_added(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "chapter-02-text-h-0011")
        self.assertEqual(authorization["scope"], "AGES I / Easy Choose only")
        self.assertEqual(set(authorization["repository_links"]), {"text-a-0105", "text-a-0106", "text-a-0107"})
        self.assertEqual(
            set(authorization["approved_presentation_changes"]["section_numbering"]),
            {"text-h-0002", "text-h-0022"},
        )

    def test_ages_ii_authorized_citation_keys_exist_in_integrated_bibliography(self):
        repo = Path(__file__).resolve().parents[1]
        bibliography = (repo / "relatorio_AGES_eduardo/bibliografia/bibliografia.bib").read_text(encoding="utf-8")
        for key in AGES_II_TECHNOLOGY_REFERENCE_KEYS.values():
            with self.subTest(key=key):
                self.assertIn(f"@online{{{key},", bibliography)

    def test_ages_iii_bibliography_matches_curator_after_tex_literal_unescaping(self):
        repo = Path(__file__).resolve().parents[1]
        evidence = json.loads((repo / "migration/evidence/references/ages-iii.json").read_text(encoding="utf-8"))
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        bibliography = (repo / "relatorio_AGES_eduardo/bibliografia/bibliografia.bib").read_text(encoding="utf-8")
        self.assertIn(r"C\# Guide", bibliography)
        self.assertIn(r"Parking \& Access Control", bibliography)
        self.assertEqual(evidence["consultation_date"], "2026-10-16")
        self.assertNotIn("user_assigned_bibliographic_access_date_convention", evidence["policy"])
        _verify_ages_iii_bibliography_entries(bibliography, evidence, records)
        thesis_entry = bibliography.split("@thesis{ages-iii-fielding-rest,", 1)[1].split("\n}", 1)[0]
        self.assertIn("date = {2000}", thesis_entry)
        self.assertIn("urldate = {2026-10-16}", thesis_entry)
        self.assertNotIn("year =", thesis_entry)
        style = (repo / "relatorio_AGES_eduardo/util/style.tex").read_text(encoding="utf-8")
        self.assertIn(
            r"\DeclareLabeldate[thesis]{\field{urldate}\field{date}\field{year}}",
            style,
        )

    def test_ages_iii_unknown_publication_date_must_not_become_citation_year(self):
        repo = Path(__file__).resolve().parents[1]
        evidence = json.loads((repo / "migration/evidence/references/ages-iii.json").read_text(encoding="utf-8"))
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        bibliography_path = repo / "relatorio_AGES_eduardo/bibliografia/bibliografia.bib"
        bibliography = bibliography_path.read_text(encoding="utf-8")
        entry_start = bibliography.index("@online{ages-iii-cloudfront,")
        entry_end = bibliography.index("\n}", entry_start)
        entry = bibliography[entry_start:entry_end]
        self.assertNotRegex(entry, r"(?m)^\s*year\s*=")
        self.assertNotRegex(entry, r"(?m)^\s*date\s*=")
        fabricated_publication_year = bibliography[:entry_end] + "\n  year = {2026}," + bibliography[entry_end:]
        with patch("scripts.migration_harness.preservation.AGES_III_TECHNICAL_CITATION_KEYS", {"ages-iii-cloudfront"}):
            with self.assertRaises(ValueError):
                _verify_ages_iii_bibliography_entries(fabricated_publication_year, evidence, records)

    def test_legacy_ages_iii_technology_verifier_does_not_accept_prose_v2_ledger(self):
        # The latest scoped approval revokes the old single-paragraph/link
        # presentation for the real unit. The legacy verifier stays fail-closed
        # for synthetic/legacy callers, rather than weakening its old contract.
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        unit = next(item for item in manifest["units"] if item["id"] == "chapter-05-text-h-0085")
        ledger = json.loads((repo / "migration/ledgers/chapter-05-text-h-0085.json").read_text(encoding="utf-8"))["units"][unit["id"]]
        source = (repo / ledger["tex_path"]).read_text(encoding="utf-8")
        self.assertEqual(ledger["technology_prose_revision"]["format"], "mariah-project-prose-v2")
        with self.assertRaisesRegex(ValueError, "Technology narrative serialization"):
            _verify_ages_iii_technology_paragraph(
                source, ledger, unit, records,
                _load_presentation_authorization(repo, unit["id"]),
            )

    def test_ages_iii_technology_narrative_rewrite_is_limited_to_user_scope(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "chapter-05-text-h-0085")
        policy = authorization["approved_presentation_changes"]["technology_narrative_rewrite"]
        self.assertEqual(policy["source_ids"], [
            "text-p-1066", "text-p-1069", "text-p-1072", "text-p-1073",
            "text-p-1076", "text-p-1077", "text-p-1080", "text-p-1083",
            "text-p-1084", "text-p-1087", "text-p-1090", "text-p-1093",
            "text-p-1096", "text-p-1099", "text-p-1102", "text-p-1105",
        ])
        self.assertEqual(authorization["review_status"]["independent_content_audit"], "pending")
        self.assertIsNone(authorization["review_status"]["human_approval_of_final_AGES_III_edition"])
        projected, transform = _project_approved_presentation(
            "text-p-1066", "texto original", "prosa autorizada",
            ["technology_citation", "approved_technology_narrative"], authorization,
        )
        self.assertEqual(projected, "texto original")
        self.assertEqual(transform["kind"], "user_authorized_technology_narrative_rewrite")
        self.assertFalse(transform["lexical_equality"])
        self.assertEqual(transform["semantic_review"], "pending_independent_content_audit")
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                "text-p-1111", "texto original", "prosa autorizada",
                ["approved_technology_narrative"], authorization,
            )

    def test_ages_iii_documentation_links_use_authorized_mariah_style_prose(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "chapter-05-text-h-0085")
        projected, transform = _project_approved_presentation(
            "text-p-1067", "Documentação C#",
            "Mais informações podem ser encontradas em: Documentação C#.",
            ["technology_documentation_link_prose"], authorization,
        )
        self.assertEqual(projected, "Documentação C#")
        self.assertEqual(transform["kind"], "user_authorized_technology_documentation_link_prose")
        self.assertEqual(transform["authorization_evidence"], "migration/approvals/ages-iii-technology-narrative-authorization.json")
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                "text-p-1067", "Documentação C#",
                "Mais informações podem ser encontradas em: Documentação .NET.",
                ["technology_documentation_link_prose"], authorization,
            )

    def test_ages_iii_conclusion_heading_uses_abnt_section_punctuation(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "chapter-05-text-h-0097")
        expected, target = PRESENTATION_HEADINGS["text-h-0097"]
        projected, transform = _project_approved_presentation(
            "text-h-0097", expected, target, ["abnt_section_numbering"], authorization,
        )
        self.assertEqual(projected, expected)
        self.assertEqual(transform["displayed"], "5.4 Conclusão")
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        unit = next(item for item in manifest["units"] if item["id"] == "chapter-05-text-h-0097")
        ledger = json.loads((repo / "migration/ledgers/chapter-05-text-h-0097.json").read_text(encoding="utf-8"))
        heading_map = next(item for item in ledger["units"]["chapter-05-text-h-0097"]["element_map"] if item["source_id"] == "text-h-0097")
        self.assertIn("abnt_section_numbering", heading_map["serializations"])
        report = audit_conversion({**manifest, "units": [unit]}, ledger, repo)
        self.assertEqual(report["status"], "pass", report)

    def test_ages_iii_technology_unit_runs_the_full_audit_without_scope_leakage(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        unit = next(item for item in manifest["units"] if item["id"] == "chapter-05-text-h-0085")
        unit_manifest = {**manifest, "units": [unit]}
        ledger = json.loads((repo / "migration/ledgers/chapter-05-text-h-0085.json").read_text(encoding="utf-8"))
        report = audit_conversion(unit_manifest, ledger, repo)
        self.assertEqual(report["status"], "pass", report)

    def test_brand_authors_use_mixed_case_in_parenthetical_citations(self):
        repo = Path(__file__).resolve().parents[1]
        bibliography = (repo / "relatorio_AGES_eduardo/bibliografia/bibliografia.bib").read_text(encoding="utf-8")
        style = (repo / "relatorio_AGES_eduardo/util/style.tex").read_text(encoding="utf-8")
        self.assertIn("author = {{Figma}}", bibliography)
        self.assertIn("author = {{Docker}}", bibliography)
        self.assertNotIn("author = {{FIGMA}}", bibliography)
        self.assertNotIn("author = {{DOCKER}}", bibliography)
        self.assertIn(r"style=abnt,repeatfields=true", style)
        self.assertNotIn(r"\ExecuteBibliographyOptions{dashed=false}", style)

    def test_ages_ii_prefix_tokens_project_exactly_and_are_scope_gated(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        self.assertTrue(records["text-h-0068"]["text"].startswith(" " * 4))
        self.assertEqual(len(records["text-h-0068"]["text"]) - len(records["text-h-0068"]["text"].lstrip(" ")), 4)
        self.assertEqual(records["text-p-0961"]["text"][:1], "\n")
        self.assertEqual(records["text-p-0969"]["text"][:1], "\n")

    def test_ages_ii_leading_tab_gate_excludes_internal_tab_paragraphs(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        unit = next(item for item in manifest["units"] if item["id"] == "ages-ii-sprint-4")
        actual = _leading_tab_paragraph_ids(unit["source_record_ids"], records)
        self.assertEqual(actual, list(AGES_II_LEADING_TAB_COUNTS["ages-ii-sprint-4"]))
        self.assertTrue(all("\t" in records[rid]["text"] for rid in ("text-p-0975", "text-p-0976", "text-p-0977")))
        self.assertTrue(all(rid not in actual for rid in ("text-p-0975", "text-p-0976", "text-p-0977")))

    def test_ages_ii_h0068_is_a_paragraph_despite_odf_heading_element_type(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        self.assertTrue(_is_source_heading(records["text-h-0067"]))
        self.assertFalse(_is_source_heading(records["text-h-0068"]))
        self.assertEqual(records["text-h-0068"]["semantic_type"], "paragraph")

    def test_verified_reference_layout_projects_only_authorized_source_whitespace(self):
        serialization = ["reference_paragraph_layout"]
        self.assertFalse(_source_whitespace_verified(serialization, True, False))
        self.assertTrue(_source_whitespace_verified(serialization, True, True))
        self.assertFalse(_source_whitespace_verified(serialization, False, True))
        verified = _source_whitespace_verified(serialization, True, True)
        self.assertEqual(_strict_source("\nEtapa", verified, allowed_leading_line_breaks=1), "\nEtapa")
        with self.assertRaises(UnsupportedSerialization):
            _strict_source("\nEtapa", verified)
        with self.assertRaises(UnsupportedSerialization):
            _strict_source("\n\nEtapa", verified, allowed_leading_line_breaks=1)
        with self.assertRaises(UnsupportedSerialization):
            _strict_source("Etapa\nseguinte", verified, allowed_leading_line_breaks=1)
        source_tokens = [
            (("\\originalleadingspace{}" * 4) + "Na Sprint 4", "    Na Sprint 4"),
            (r"\originalleadbreak{}Primeira Etapa", "\nPrimeira Etapa"),
        ]
        for target, expected in source_tokens:
            with self.subTest(target=target):
                self.assertEqual(
                    displayed_text(target, ["original_whitespace", "reference_paragraph_layout"], macro_contract_verified=True, reference_layout_verified=True),
                    expected,
                )
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(r"\originalleadbreak{}Primeira Etapa", ["original_whitespace"], macro_contract_verified=True)

    def test_ages_ii_caption_heading_and_repository_overlays_are_exact(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "chapter-04-text-h-0040")
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        rid = "text-p-0767"
        source = records[rid]["text"]
        target = authorization["approved_presentation_changes"]["figure_caption_labels"][rid]
        projected, evidence = _project_approved_presentation(rid, source, target, ["abnt_figure_caption"], authorization)
        self.assertEqual(projected, source)
        self.assertEqual(evidence["displayed"], target)
        rid = "text-h-0039"
        source = records[rid]["text"]
        target = authorization["approved_presentation_changes"]["section_numbering"][rid]
        projected, _ = _project_approved_presentation(rid, source, target, ["abnt_section_numbering"], authorization)
        self.assertEqual(projected, source)
        rid = "text-p-0775"
        link_id = PRESENTATION_REPOSITORY_PARAGRAPHS[rid]
        rule = PRESENTATION_REPOSITORY_LINKS[link_id]
        projected, evidence = _project_approved_presentation(
            rid, rule["source_anchor"], rule["prefix"] + rule["anchor"] + rule["suffix"],
            ["repository_link_sentence"], authorization,
        )
        self.assertEqual(projected, rule["source_anchor"])
        self.assertEqual(evidence["href"], rule["href"])
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(rid, rule["source_anchor"], "Texto alterado", ["repository_link_sentence"], authorization)

    def ages_ii_technology_fixture(self, split_before_summary=False):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        unit = next(item for item in manifest["units"] if item["id"] == "chapter-04-text-h-0046")
        curation = json.loads((repo / "migration/evidence/references/ages-ii.json").read_text(encoding="utf-8"))
        curated = {item["source_record_id"]: item for item in curation["references"]}
        link_parents = {
            "text-p-0814": "text-a-0122", "text-p-0815": "text-a-0123",
            "text-p-0819": "text-a-0124", "text-p-0823": "text-a-0125",
            "text-p-0827": "text-a-0126", "text-p-0831": "text-a-0127",
            "text-p-0835": "text-a-0128",
        }
        parts = []
        mappings = []
        offset = 0
        for rid in AGES_II_TECHNOLOGY_TEXT_IDS:
            if split_before_summary and rid == "text-p-0841":
                parts.append(r"\par ")
                offset += len(r"\par ".encode())
            fragment = f"[{rid}]"
            encoded = fragment.encode("utf-8")
            mappings.append({"source_id": rid, "target_file": "technology.tex", "start_byte": offset, "end_byte": offset + len(encoded)})
            parts.append(fragment)
            offset += len(encoded)
            citation_gap = "" if records[rid].get("text", "").endswith((" ", "\t")) else r"\space"
            for key in AGES_I_II_TECHNICAL_CITATIONS["chapter-04-text-h-0046"].get(rid, []):
                suffix = citation_gap + r"\cite{" + key + "}"
                parts.append(suffix)
                offset += len(suffix.encode())
            if rid in link_parents:
                evidence = curated[link_parents[rid]]
                link = r"\href{" + evidence["original_url"] + "}{" + evidence["original_anchor"] + "}"
                parts.append(link)
                offset += len(link.encode())
            parts.append(" ")
            offset += 1
        parts.append(r"\href{https://www.docker.com/}{Documentação Docker} ")
        parts.append(r"\par")
        source = "".join(parts)
        bibliography = []
        for source_id, key in AGES_II_TECHNOLOGY_REFERENCE_KEYS.items():
            evidence = curated[source_id]
            bibliography.append(
                f"@online{{{key},\n"
                f"  title = {{{evidence['metadata']['title']}}},\n"
                f"  url = {{{evidence['original_url']}}},\n"
                "  year = {2024},\n"
                "  urldate = {2024-10-15},\n"
                "}\n"
            )
        for key, expected in AGES_II_ADDITIONAL_REFERENCE_RECORDS.items():
            author = f"  author = {{{{{expected['author']}}}}},\n" if expected["author"] else ""
            bibliography.append(
                f"@online{{{key},\n" + author
                + f"  title = {{{expected['title']}}},\n"
                + f"  url = {{{expected['url']}}},\n"
                + "  year = {2024},\n  urldate = {2024-10-15},\n}\n"
            )
        for key, expected in AGES_II_RFC_REFERENCE_FIELDS.items():
            additional = "".join(f"  {field} = {{{value}}},\n" for field, value in expected.items())
            bibliography.append(
                f"@online{{{key},\n" + additional
                + "  urldate = {2024-10-15},\n}\n"
            )
        disposition = {
            "source_id": "text-list-0109",
            "disposition": "approved-single-paragraph-technology-list",
            "presentation_override": {
                "authorization_evidence": AGES_II_PRESENTATION_AUTHORIZATION,
                "source_list_ids": [f"text-list-0{number}" for number in range(109, 116)],
                "target_structure": "one continuous paragraph retaining source text, links and order",
                "item_count": 7,
            },
        }
        authorization = _load_presentation_authorization(repo, "chapter-04-text-h-0046")
        ledger = {"tex_path": "technology.tex", "element_map": mappings}
        return source, "".join(bibliography), disposition, authorization, ledger, unit, records, curation

    def test_ages_ii_technology_paragraph_keeps_verified_and_pending_sources_separate(self):
        fixture = self.ages_ii_technology_fixture()
        self.assertTrue(_verify_ages_ii_technology_paragraph(*fixture))

    def test_ages_ii_technology_paragraph_rejects_split_paragraph_and_authorship_inference(self):
        fixture = self.ages_ii_technology_fixture(split_before_summary=True)
        with self.assertRaises(ValueError):
            _verify_ages_ii_technology_paragraph(*fixture)
        fixture = self.ages_ii_technology_fixture()
        fixture = list(fixture)
        fixture[1] = fixture[1].replace("title = {Angular},", "author = {{Angular}},\n  title = {Angular},")
        with self.assertRaises(ValueError):
            _verify_ages_ii_technology_paragraph(*fixture)

    def valid_text(self):
        self.write(r"Ação: 20\% — \emph{café!}")
        self.ledger["units"]["sprint-test"]["element_map"] = [self.mapping("p1", r"Ação: 20\% — \emph{café!}")]

    def test_known_serialization_preserves_accents_and_punctuation(self):
        self.valid_text()
        report = self.audit()
        self.assertEqual(report["status"], "pass", report)
        self.assertEqual(report["facts"]["coverage_percent"], 100)
        self.assertIn("pdf_evidence_pending", self.codes(report))

    def test_odf_character_style_cancellation_wrappers_preserve_visible_text(self):
        self.assertEqual(
            displayed_text(r"\textbf{Product Backlog\textmd{…}}"),
            "Product Backlog…",
        )
        self.assertEqual(
            displayed_text(r"\textit{força\textup{ tarefa}}"),
            "força tarefa",
        )

    def test_figure_references_require_explicit_serialization_and_keep_label(self):
        token = r"A Figura~\ref{ages-i:draw-image-0001}."
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(token)
        self.assertEqual(
            displayed_text(token, ["approved_figure_cross_reference"]),
            "A Figura ⟪ref:ages-i:draw-image-0001⟫.",
        )

    def test_explicit_nonbreaking_space_before_figure_reference_is_visible(self):
        token = r"Figura\nobreakspace{}\ref{fig:ages-i-projeto-destaque}."
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(token)
        self.assertEqual(
            displayed_text(token, ["approved_figure_cross_reference"]),
            "Figura ⟪ref:fig:ages-i-projeto-destaque⟫.",
        )

    def test_linked_starred_figure_reference_preserves_explicit_gap(self):
        token = r"Figura\hspace{0.6em}\hyperref[fig:ages-i-projeto-destaque]{\ref*{fig:ages-i-projeto-destaque}}."
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(token)
        self.assertEqual(
            displayed_text(token, ["approved_figure_cross_reference"]),
            "Figura ⟪ref:fig:ages-i-projeto-destaque⟫.",
        )
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(token.replace("0.6em", "0.5em"), ["approved_figure_cross_reference"])
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(token.replace("fig:ages-i-projeto-destaque}}", "fig:other}}"), ["approved_figure_cross_reference"])

    def test_abnt_caption_and_heading_overlays_are_exact_and_scoped(self):
        authorization = {
            "approved_presentation_changes": {
                "figure_caption_labels": {"text-p-0293": "Figura 1 – Foto do time – AGES I"},
                "section_numbering": {rid: target for rid, (_, target) in PRESENTATION_HEADINGS.items()},
            }
        }
        old_caption = "Figure 1: Foto do time – AGES I"
        projected, evidence = _project_approved_presentation(
            "text-p-0293", old_caption, "Figura 1 – Foto do time – AGES I",
            ["abnt_figure_caption"], authorization,
        )
        self.assertEqual(projected, old_caption)
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                "text-p-0293", old_caption, "Figura 1 – Foto do time alterado – AGES I",
                ["abnt_figure_caption"], authorization,
            )
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                "text-p-0303", "qualquer texto", "qualquer texto",
                ["abnt_figure_caption"], authorization,
            )

    def test_ages_iii_caption_overlay_preserves_the_source_leading_tab(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "chapter-05-text-h-0075")
        source = "\tFigure 16: Foto do Time - AGES III"
        displayed = "\tFigura 16 – Foto do Time - AGES III"
        projected, evidence = _project_approved_presentation(
            "text-p-1027", source, displayed, ["abnt_figure_caption"], authorization,
        )
        self.assertEqual(projected, source)
        self.assertEqual(evidence["displayed"], displayed)

    def test_ages_iii_prototype_group_labels_are_omitted_only_under_exact_user_decision(self):
        repo = Path(__file__).resolve().parents[1]
        authorization = _load_presentation_authorization(repo, "chapter-05-text-h-0080")
        self.assertEqual(
            PRESENTATION_OVERRIDES_BY_UNIT["chapter-05-text-h-0080"] & set(AGES_III_PROTOTYPE_GROUP_LABELS),
            set(AGES_III_PROTOTYPE_GROUP_LABELS),
        )
        for source_id, original in AGES_III_PROTOTYPE_GROUP_LABELS.items():
            with self.subTest(source_id=source_id):
                self.assertTrue(_is_authorized_ages_iii_group_label_removal(authorization, source_id))
                projected, evidence = _project_approved_presentation(
                    source_id, original, "", ["approved_group_label_removal"], authorization,
                )
                self.assertEqual(projected, original)
                self.assertEqual(evidence["displayed"], "")
                self.assertEqual(evidence["authorization_evidence"], "migration/approvals/ages-iii-prototype-group-labels.json")
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                "text-h-0085", "Tecnologias utilizadas", "",
                ["approved_group_label_removal"], authorization,
            )
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                "text-h-0084", "Telas de Cliente alterado:", "",
                ["approved_group_label_removal"], authorization,
            )
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                "text-h-0084", "Telas de Cliente:", "Telas de Cliente:",
                ["approved_group_label_removal"], authorization,
            )

    def test_repository_sentence_overlay_only_accepts_original_anchors(self):
        source_id = "text-p-0310"
        link_id = PRESENTATION_REPOSITORY_PARAGRAPHS[source_id]
        rule = PRESENTATION_REPOSITORY_LINKS[link_id]
        source = rule["source_anchor"]
        target = rule["prefix"] + rule["anchor"] + rule["suffix"]
        projected, evidence = _project_approved_presentation(
            source_id, source, target, ["repository_link_sentence"], {},
        )
        self.assertEqual(projected, source)
        self.assertEqual(evidence["href"], rule["href"])
        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                source_id, source, target + " Alterado", ["repository_link_sentence"], {},
            )

    def test_ages_i_ii_wiki_sentence_overlay_is_exact_and_keeps_the_odt_url(self):
        repo = Path(__file__).resolve().parents[1]
        auth = _load_ages_i_ii_formatting_authorization(repo, "chapter-02-text-h-0009")
        for paragraph_id, rule in AGES_I_II_WIKI_SENTENCES.items():
            with self.subTest(paragraph_id=paragraph_id):
                leading = "\t" * rule["leading_tabs"]
                expected = leading + rule["source_anchor"]
                displayed = leading + rule["prefix"] + rule["anchor"] + rule["suffix"]
                projected, evidence = _project_approved_presentation(
                    paragraph_id, expected, displayed, ["wiki_reference_sentence"], None, auth,
                )
                self.assertEqual(projected, expected)
                self.assertEqual(evidence["href"], rule["href"])
                linked, link_evidence = _project_approved_presentation(
                    rule["source_id"], rule["source_anchor"], rule["anchor"],
                    ["wiki_reference_sentence"], None, auth,
                )
                self.assertEqual(linked, rule["source_anchor"])
                self.assertEqual(link_evidence["displayed"], rule["anchor"])
                with self.assertRaises(UnsupportedSerialization):
                    _project_approved_presentation(
                        paragraph_id, expected, displayed + " inventado",
                        ["wiki_reference_sentence"], None, auth,
                    )

    def test_ages_iv_repository_and_wiki_sentences_match_approved_style_and_keep_original_urls(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        for unit_id, source_ids in AGES_IV_REPOSITORY_UNITS.items():
            authorization = _load_presentation_authorization(repo, unit_id)
            for paragraph_id, link_id in PRESENTATION_REPOSITORY_PARAGRAPHS.items():
                if link_id not in source_ids:
                    continue
                rule = PRESENTATION_REPOSITORY_LINKS[link_id]
                target = rule["prefix"] + rule["anchor"] + rule["suffix"]
                projected, evidence = _project_approved_presentation(
                    paragraph_id, rule["source_anchor"], target,
                    ["repository_link_sentence"], authorization,
                )
                self.assertEqual(projected, rule["source_anchor"])
                self.assertEqual(evidence["href"], records[link_id]["href"])
                linked, link_evidence = _project_approved_presentation(
                    link_id, rule["source_anchor"], target,
                    ["repository_link_sentence"], authorization,
                )
                self.assertEqual(linked, rule["source_anchor"])
                self.assertEqual(link_evidence["href"], records[link_id]["href"])
        for unit_id, source_ids in AGES_IV_WIKI_UNITS.items():
            authorization = _load_presentation_authorization(repo, unit_id)
            paragraph_id = next(rid for rid in source_ids if rid in AGES_IV_WIKI_SENTENCES)
            rule = AGES_IV_WIKI_SENTENCES[paragraph_id]
            target = rule["prefix"] + rule["anchor"] + rule["suffix"]
            projected, evidence = _project_approved_presentation(
                paragraph_id, rule["source_anchor"], target,
                ["wiki_reference_sentence"], authorization,
            )
            self.assertEqual(projected, rule["source_anchor"])
            self.assertEqual(evidence["href"], rule["href"])
            linked, link_evidence = _project_approved_presentation(
                rule["source_id"], rule["source_anchor"], rule["anchor"],
                ["wiki_reference_sentence"], authorization,
            )
            self.assertEqual(linked, rule["source_anchor"])
            self.assertEqual(link_evidence["href"], rule["href"])
            with self.assertRaises(UnsupportedSerialization):
                _project_approved_presentation(
                    paragraph_id, rule["source_anchor"], target + " alterado",
                    ["wiki_reference_sentence"], authorization,
                )
        approval = json.loads((repo / "migration/approvals/ages-iv-pending-references-acceptance.json").read_text(encoding="utf-8"))
        pending = {item["source_id"]: item for item in approval["original_links"]}
        expected_urls = {
            **{rid: rule["href"] for rid, rule in PRESENTATION_REPOSITORY_LINKS.items() if rid in {"text-a-0146", "text-a-0147"}},
            **{rule["source_id"]: rule["href"] for rule in AGES_IV_WIKI_SENTENCES.values()},
        }
        expected_urls.update({
            "text-a-0148": AGES_IV_WIKI_SENTENCES["text-p-1343"]["href"],
            "text-a-0150": AGES_IV_WIKI_SENTENCES["text-p-1362"]["href"],
        })
        self.assertEqual(set(pending), set(expected_urls))
        self.assertEqual(len(approval["original_links"]), 7)
        for link_id, url in expected_urls.items():
            self.assertEqual(pending[link_id]["url"], url)
            self.assertEqual(pending[link_id]["availability"], "PENDING")
            self.assertEqual(records[link_id]["href"], url)
        self.assertEqual(pending["text-a-0148"]["source_anchor"], "")
        self.assertEqual(pending["text-a-0150"]["source_anchor"], "")
        self.assertEqual(pending["text-a-0148"]["url"], pending["text-a-0149"]["url"])
        self.assertEqual(pending["text-a-0150"]["url"], pending["text-a-0151"]["url"])

    def test_ages_iv_citation_maps_and_bibliography_are_tied_to_curated_sources(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        evidence = json.loads((repo / "migration/evidence/references/ages-iv.json").read_text(encoding="utf-8"))
        supplemental_authorization = json.loads(
            (repo / "migration/approvals/ages-iv-supplemental-citations-authorization.json").read_text(encoding="utf-8")
        )
        bibliography = (repo / "relatorio_AGES_eduardo/bibliografia/bibliografia.bib").read_text(encoding="utf-8")
        self.assertEqual(set(AGES_IV_CITATION_EVIDENCE), {
            key for unit in AGES_IV_TECHNICAL_CITATIONS.values() for keys in unit.values() for key in keys
        })
        _verify_ages_iv_bibliography_entries(bibliography, evidence, records, supplemental_authorization)
        tampered_authorization = json.loads(json.dumps(supplemental_authorization))
        tampered_authorization["citations"]["ages-iv-app-store"]["verified_url"] = "https://example.invalid/"
        with self.assertRaises(ValueError):
            _verify_ages_iv_bibliography_entries(bibliography, evidence, records, tampered_authorization)
        with self.assertRaises(ValueError):
            _verify_ages_iv_bibliography_entries(bibliography, evidence, records, {})
        for unit_map in AGES_IV_TECHNICAL_CITATIONS.values():
            for source_id, keys in unit_map.items():
                terms = AGES_IV_CITATION_TERMS[source_id]
                self.assertEqual(len(keys), len(terms))
                fragment = " ".join(term + r"\space\cite{" + key + "}" for term, key in zip(terms, keys))
                _verify_citation_alignment(
                    source_id, fragment, keys, terms,
                    ["technology_citation"], False, False, False,
                )
                altered = fragment.replace(terms[0], "Termo alterado", 1)
                with self.assertRaises(ValueError):
                    _verify_citation_alignment(
                        source_id, altered, keys, terms,
                        ["technology_citation"], False, False, False,
                    )

    def test_ages_iv_citation_alignment_runs_in_full_unit_audit(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        unit_id = "chapter-06-text-h-0109"
        unit = next(item for item in manifest["units"] if item["id"] == unit_id)
        source_id = "text-p-1339"
        record = next(item for item in manifest["records"] if item["id"] == source_id)
        keys = AGES_IV_TECHNICAL_CITATIONS[unit_id][source_id]
        terms = AGES_IV_CITATION_TERMS[source_id]
        projected = record["text"]
        for term, key in reversed(list(zip(terms, keys))):
            projected = projected.replace(term, term + r"\space\cite{" + key + "}", 1)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            for relative in (
                "migration/approvals/ages-iv-partial-authorization.json",
                "migration/approvals/ages-iv-supplemental-citations-authorization.json",
                "migration/evidence/references/ages-iv.json",
                "relatorio_AGES_eduardo/bibliografia/bibliografia.bib",
            ):
                destination = temp_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((repo / relative).read_bytes())

            target_path = "relatorio_AGES_eduardo/conteudo/migracao/citation-fixture.tex"
            target = temp_root / target_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(projected, encoding="utf-8")
            target_data = target.read_bytes()
            start = target_data.index(projected.encode("utf-8"))
            fixture_unit = {**unit, "record_ids": [source_id], "source_record_ids": [source_id]}
            fixture_ledger = {
                "schema_version": 1,
                "compilation_root": "relatorio_AGES_eduardo",
                "units": {
                    unit_id: {
                        "state": "converted",
                        "tex_path": target_path,
                        "technology_citations": {
                            "authorization_evidence": "migration/approvals/ages-iv-partial-authorization.json",
                            "source_text_changed": False,
                            "source_id_to_keys": {source_id: keys},
                        },
                        "element_map": [{
                            "source_id": source_id,
                            "target_file": target_path,
                            "start_byte": start,
                            "end_byte": start + len(projected.encode("utf-8")),
                            "target_sha256": hashlib.sha256(target_data).hexdigest(),
                            "serializations": ["technology_citation"],
                        }],
                    }
                },
            }
            report = audit_conversion({**manifest, "units": [fixture_unit]}, fixture_ledger, temp_root, unit_id)

        self.assertNotIn("invalid_technology_citation_apparatus", self.codes(report), report)
        self.assertEqual(report["facts"]["technical_citations_verified"], len(keys))

    def test_ages_iv_chapter_heading_override_is_required_and_exactly_scoped(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        unit_id = "chapter-06-text-h-0105"
        unit = next(item for item in manifest["units"] if item["id"] == unit_id)
        ledger = json.loads((repo / "migration/ledgers/chapter-06-text-h-0105.json").read_text(encoding="utf-8"))
        accepted = audit_conversion({**manifest, "units": [unit]}, ledger, repo, unit_id)
        self.assertEqual(accepted["status"], "pass", accepted)

        omitted_override = json.loads(json.dumps(ledger))
        unit_ledger = omitted_override["units"][unit_id]
        unit_ledger.pop("document_reordering_authorization", None)
        rejected = audit_conversion({**manifest, "units": [unit]}, omitted_override, repo, unit_id)
        self.assertIn("invalid_document_reordering_authorization", self.codes(rejected), rejected)

    def test_document_order_reindex_keeps_edition_specific_wiki_placeholder_and_technology_gates_valid(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        for unit_id in (
            "chapter-04-text-h-0043", "chapter-04-text-h-0044", "chapter-04-text-h-0045",
            "chapter-05-text-h-0078", "chapter-06-text-h-0109", "chapter-06-text-h-0110",
            "chapter-06-text-h-0112",
            "chapter-06-text-h-0113",
        ):
            with self.subTest(unit_id=unit_id):
                unit = next(item for item in manifest["units"] if item["id"] == unit_id)
                ledger = json.loads((repo / "migration/ledgers" / f"{unit_id}.json").read_text(encoding="utf-8"))
                report = audit_conversion({**manifest, "units": [unit]}, ledger, repo, unit_id)
                errors = [item for item in report["findings"] if item.get("severity") == "error"]
                self.assertEqual(errors, [], report)
                self.assertEqual(report["status"], "pass", report)

    def test_technology_citation_serialization_is_removed_only_as_verified_apparatus(self):
        value = r"TypeScript\space\cite{ages-ii-typescript}"
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(value)
        self.assertEqual(displayed_text(value, ["technology_citation"]), "TypeScript")
        self.assertEqual(
            _citation_keys_in_fragment(value),
            ["ages-ii-typescript"],
        )
        self.assertEqual(
            set(key for values in AGES_I_II_TECHNICAL_CITATIONS["chapter-04-text-h-0046"].values() for key in values)
            - AGES_I_II_TECHNICAL_CITATION_KEYS,
            set(),
        )

    def test_authorized_cross_reference_overlay_has_exact_source_ids(self):
        source_id = "text-p-0325"
        rule = PRESENTATION_CROSS_REFERENCES[source_id]
        auth = {"approved_presentation_changes": {"figure_cross_references": PRESENTATION_CROSS_REFERENCES}}
        source = "Fotos dos protótipos:"
        target = "Fotos dos protótipos (Figuras ⟪ref:ages-i:draw-image-0002⟫ a ⟪ref:ages-i:draw-image-0004⟫):"
        projected, evidence = _project_approved_presentation(
            source_id, source, target, ["approved_figure_cross_reference"], auth,
        )
        self.assertEqual(projected, source)
        self.assertEqual(evidence["kind"], "figure_cross_reference")

    def test_authorized_final_figure_callout_has_space_and_exact_words(self):
        source_id = "text-p-0642"
        rule = PRESENTATION_CROSS_REFERENCES[source_id]
        auth = {"approved_presentation_changes": {"figure_cross_references": PRESENTATION_CROSS_REFERENCES}}
        source = "Original paragraph."
        target = r"Original paragraph. O registro do projeto selecionado está na Figura ⟪ref:fig:ages-i-projeto-destaque⟫."
        projected, evidence = _project_approved_presentation(
            source_id, source, target, ["approved_figure_cross_reference"], auth,
        )
        self.assertEqual(projected, source)
        self.assertEqual(evidence["kind"], "figure_cross_reference")

    def test_approved_technology_list_suppresses_only_markers_and_keeps_five_items(self):
        source_id, rule = next(iter(PRESENTATION_LIST_MARKERS.items()))
        auth = {
            "list_marker_instruction": PRESENTATION_LIST_MARKER_INSTRUCTION,
            "approved_presentation_changes": {"list_markers": PRESENTATION_LIST_MARKERS},
        }
        disposition = {
            "disposition": "approved-markerless-list-preserving-items",
            "presentation_override": {
                "authorization_evidence": "migration/approvals/ages-i-presentation-corrections.json",
                "source_marker": "bullet",
                "target_marker": "none",
                "item_count": 5,
            },
        }
        source = rule["tex_environment"] + "\n" + "\\item\n" * 5 + "\\end{itemize}"
        self.assertTrue(_verify_markerless_list(source_id, source, disposition, auth))
        with self.assertRaises(ValueError):
            _verify_markerless_list(source_id, source.replace(rule["tex_environment"], r"\begin{itemize}"), disposition, auth)
        with self.assertRaises(ValueError):
            _verify_markerless_list(source_id, source.replace("\\item\n", "", 1), disposition, auth)

    def technology_paragraph_fixture(self):
        references = [
            {
                "source_id": item["source_id"],
                "citation_key": item["citation_key"],
                "citation_author_label": item["label"],
                "year": 2024,
                "access_date": item["date"],
                "url": item["url"],
            }
            for item in TECHNOLOGY_PARAGRAPH_RECORDS
        ]
        authorization = {
            "schema_version": 1,
            "kind": "user_authorized_technology_presentation_and_citation",
            "status": "authorized_for_execution_pending_human_review",
            "scope": "AGES I / Easy Choose / subseção Tecnologias utilizadas / text-h-0012",
            "source_sha256": "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef",
            "user_decisions": {
                "author_date_year": "Use the access year as the publication/citation year, following Mariah's pattern."
            },
            "assigned_references": references,
            "human_approval_of_result": None,
            "promoted_to_reusable_policy": False,
        }
        sections = []
        entries = []
        for index, item in enumerate(TECHNOLOGY_PARAGRAPH_RECORDS):
            label = item["label"]
            key = item["citation_key"]
            sections.append(
                f"{label}:\\space\\cite{{{key}}} descrição "
                f"\\href{{{item['url']}}}{{Documentação {label}}}"
                f"{' ;'.strip() if index < 4 else '.'}"
            )
            entries.append(
                f"@online{{{key},\n"
                f"  author = {{{{{label}}}}},\n"
                "  title = {Documentação},\n"
                f"  url = {{{item['url']}}},\n"
                "  year = {2024},\n"
                f"  urldate = {{{item['date']}}},\n"
                "}\n"
            )
        source = (
            r"\label{ages-i:text-h-0012}" + "\n"
            + " ".join(sections) + " Integração final.\\par"
        )
        disposition = {
            "source_id": "text-list-0025",
            "disposition": "approved-single-paragraph-technology-list",
            "presentation_override": {
                "authorization_evidence": TECHNOLOGY_PARAGRAPH_AUTHORIZATION,
                "source_marker": "bullet list",
                "target_structure": "one continuous prose paragraph",
                "item_count": 5,
            },
        }
        return source, "\n".join(entries), disposition, authorization

    def test_authorized_technology_paragraph_keeps_citations_urls_and_assigned_dates(self):
        source, bibliography, disposition, authorization = self.technology_paragraph_fixture()
        self.assertTrue(_verify_technology_paragraph(source, bibliography, disposition, authorization))

    def test_authorized_technology_paragraph_rejects_split_text_or_missing_link(self):
        source, bibliography, disposition, authorization = self.technology_paragraph_fixture()
        with self.assertRaises(ValueError):
            _verify_technology_paragraph(source.replace(" Integração final.", r"\\par Integração final."), bibliography, disposition, authorization)
        with self.assertRaises(ValueError):
            _verify_technology_paragraph(source.replace("Documentação React", "React docs"), bibliography, disposition, authorization)

    def test_authorized_technology_paragraph_rejects_unapproved_access_date(self):
        source, bibliography, disposition, authorization = self.technology_paragraph_fixture()
        authorization["assigned_references"][0]["access_date"] = "2024-09-15"
        with self.assertRaises(ValueError):
            _verify_technology_paragraph(source, bibliography, disposition, authorization)

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

    def test_ages_ii_nested_textbox_order_uses_inline_odf_segments(self):
        parent_id, frame_id, box_id, caption_id = "text-p-0961", "draw-frame-0039", "draw-text-box-0025", "text-p-0962"
        self.manifest["records"] = [
            {"id": parent_id, "type": "text:p", "text": "Rótulo.", "inline_segments": [
                {"kind": "embedded-block", "record_id": frame_id}, {"kind": "text", "text": "Rótulo."},
            ]},
            {"id": frame_id, "type": "draw:frame", "parent_id": parent_id},
            {"id": box_id, "type": "draw:text-box", "parent_id": frame_id},
            {"id": caption_id, "type": "text:p", "text": "Legenda.", "parent_id": box_id},
        ]
        self.manifest["units"] = [{"id": "ages-ii-sprint-4", "record_ids": [parent_id, frame_id, box_id, caption_id], "source_record_ids": [parent_id, caption_id]}]
        self.ledger["units"] = {"ages-ii-sprint-4": {"state": "converted", "tex_path": "unit.tex", "element_map": []}}
        self.write("Legenda.\nRótulo.")
        unit = self.ledger["units"]["ages-ii-sprint-4"]
        unit["element_map"] = [self.mapping(caption_id, "Legenda."), self.mapping(parent_id, "Rótulo.")]
        self.assertNotIn("element_order_changed", self.codes(self.audit()))

    def test_ages_ii_nested_textbox_order_still_rejects_reversed_target(self):
        self.test_ages_ii_nested_textbox_order_uses_inline_odf_segments()
        self.write("Rótulo.\nLegenda.")
        unit = self.ledger["units"]["ages-ii-sprint-4"]
        unit["element_map"] = [self.mapping("text-p-0961", "Rótulo."), self.mapping("text-p-0962", "Legenda.")]
        self.assertIn("element_order_changed", self.codes(self.audit()))

    def test_ages_ii_nested_textbox_order_fails_closed_when_odf_structure_changes(self):
        self.test_ages_ii_nested_textbox_order_uses_inline_odf_segments()
        next(record for record in self.manifest["records"] if record["id"] == "draw-text-box-0025")["parent_id"] = "unexpected-frame"
        self.assertIn("unverified_embedded_source_order", self.codes(self.audit()))

    def test_ages_iv_linked_database_figure_order_uses_inline_odf_hierarchy(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        unit = next(item for item in manifest["units"] if item["id"] == "chapter-06-text-h-0109")
        records = {item["id"]: item for item in manifest["records"]}
        projected, error = _project_source_text_order(unit["id"], unit["source_record_ids"], records)
        self.assertIsNone(error)
        self.assertEqual(
            projected,
            ["text-h-0109", "text-p-1339", "text-p-1344", "text-p-1343"],
        )

    def test_ages_iv_linked_database_figure_order_fails_closed_on_changed_parent(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        unit = next(item for item in manifest["units"] if item["id"] == "chapter-06-text-h-0109")
        records = {item["id"]: item for item in manifest["records"]}
        records["draw-text-box-0041"]["parent_id"] = "unexpected-frame"
        projected, error = _project_source_text_order(unit["id"], unit["source_record_ids"], records)
        self.assertEqual(projected, unit["source_record_ids"])
        self.assertIn("hierarchy", error)

    def test_ages_iv_linked_figure_url_is_bound_to_exact_odf_ancestor(self):
        from scripts.migration_harness.preservation import AGES_IV_LINKED_FIGURE
        from scripts.migration_harness.latex import commands
        expected = AGES_IV_LINKED_FIGURE
        uri = "https://tools.ages.pucrs.br/2026-2/2jk-4jk/recorda/wiki/-/wikis/Banco%20de%20Dados"
        records = {
            expected["paragraph_id"]: {"id": expected["paragraph_id"], "type": "text:p", "inline_segments": [{"kind": "embedded-block", "record_id": expected["frame_id"]}, {"kind": "text", "text": "Banco de Dados"}]},
            expected["link_id"]: {"id": expected["link_id"], "type": "text:a", "parent_id": expected["paragraph_id"], "href": uri},
            expected["frame_id"]: {"id": expected["frame_id"], "type": "draw:frame", "parent_id": expected["link_id"]},
            expected["textbox_id"]: {"id": expected["textbox_id"], "type": "draw:text-box", "parent_id": expected["frame_id"]},
            expected["caption_id"]: {"id": expected["caption_id"], "type": "text:p", "parent_id": expected["textbox_id"], "ancestor_ids": [expected["link_id"]]},
            expected["image_frame_id"]: {"id": expected["image_frame_id"], "type": "draw:frame", "parent_id": expected["caption_id"]},
            expected["image_id"]: {"id": expected["image_id"], "type": "draw:image", "parent_id": expected["image_frame_id"], "ancestor_ids": [expected["link_id"]]},
        }
        tex_uri = uri.replace("%", r"\%")
        call = next(token for token in commands(r"\memorialfigurelinked{asset.png}{Figura 25}{fig:db}{Fonte: pendente de identificação}{0.92}{" + tex_uri + "}") if token.name == "memorialfigurelinked")
        preserved_links = [{"source_id": expected["link_id"], "original_url": uri}]
        self.assertEqual(_verify_linked_figure_source(expected["unit_id"], expected["image_id"], call, records, preserved_links), uri)
        wrong_url = next(token for token in commands(r"\memorialfigurelinked{asset.png}{Figura 25}{fig:db}{Fonte: pendente de identificação}{0.92}{https://example.org/other}") if token.name == "memorialfigurelinked")
        with self.assertRaisesRegex(ValueError, "differs"):
            _verify_linked_figure_source(expected["unit_id"], expected["image_id"], wrong_url, records, preserved_links)
        records[expected["image_id"]]["ancestor_ids"] = []
        with self.assertRaisesRegex(ValueError, "hierarchy"):
            _verify_linked_figure_source(expected["unit_id"], expected["image_id"], call, records, preserved_links)

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

    def test_breakable_space_macro_preserves_authorized_trailing_source_space(self):
        self.assertEqual(
            displayed_text(r"TypeScript:\space", ["original_whitespace"], macro_contract_verified=True),
            "TypeScript: ",
        )
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(r"TypeScript:\space", ["original_whitespace"])

    def test_multiple_leading_tabs_must_all_be_preserved(self):
        self.whitespace_case("\t\tApós ", r"\originaltab{}\originaltab{}Após\originalspace{}")
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        self.whitespace_case("\t\tApós ", r"\originaltab{}Após\originalspace{}")
        self.assertEqual(self.audit()["status"], "blocked")
        self.whitespace_case("\tA\tB", r"\originaltab{}A\originaltab{}B")
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        self.whitespace_case("\tA\tB", r"\originaltab{}\originaltab{}AB")
        self.assertEqual(self.audit()["status"], "blocked")

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
        for source, target in [("\tA", "A"), ("\tA", "\tA"), ("A  B", "A  B"), (" A ", "A"), ("\tA ", r"\originaltab{}A"), ("A\nB", r"A\newline B")]:
            with self.subTest(source=repr(source), target=target):
                self.whitespace_case(source, target)
                self.assertEqual(self.audit()["status"], "blocked", self.audit())

    def test_xml_text_cannot_inject_internal_whitespace_markers(self):
        self.whitespace_case("\tA", "\ue000A\ue001")
        self.assertEqual(self.audit()["status"], "blocked")
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(r"\originaltab{}A", ["original_whitespace"])

    def inline_case(self, rid="text-p-0303", source=None, target=None):
        import json
        from scripts.migration_harness.preservation import INLINE_TAB_COUNTS, INLINE_TAB_AUTHORIZATION, INLINE_TAB_USER_INSTRUCTION
        count = INLINE_TAB_COUNTS.get(rid, 1)
        source = source if source is not None else "\t" + "A\t" * count + "Fim."
        target = target if target is not None else r"\originaltab{}" + r"A\originalinlinetab{}" * count + "Fim."
        self.whitespace_case(source, target)
        self.manifest["records"][0]["id"] = rid
        self.manifest["units"][0].update(record_ids=[rid], source_record_ids=[rid])
        unit = self.ledger["units"]["sprint-test"]
        unit["element_map"][0].update(source_id=rid, serializations=["original_whitespace", "inline_tab_layout"])
        unit["inline_tab_layout"] = {"authorization_evidence": INLINE_TAB_AUTHORIZATION, "source_ids": [rid]}
        macros = (self.root / "macros.tex").read_text() + "\n" + r"\newcommand{\originalinlinetab}{\unskip\space}"
        self.write(macros, "macros.tex")
        self.ledger["macro_contract"]["sha256"] = hashlib.sha256(macros.encode()).hexdigest()
        (self.root / "migration/approvals").mkdir(parents=True, exist_ok=True)
        authorization = {"kind": "user_format_correction_authorization", "scope": ["sprint-test"], "quoted_instruction": INLINE_TAB_USER_INSTRUCTION, "status": "proposed_for_review", "future_projects_approved": False, "execution_authorized": True, "layout_source_ids": list(INLINE_TAB_COUNTS), "promoted_to_reusable_policy": False}
        self.write(json.dumps(authorization), INLINE_TAB_AUTHORIZATION)
        return unit

    def test_authorized_inline_layout_projects_all_three_original_token_sequences(self):
        for rid in ["text-p-0303", "text-p-0314", "text-p-0318"]:
            with self.subTest(rid=rid):
                self.inline_case(rid)
                self.assertEqual(self.audit()["status"], "pass", self.audit())
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(r"A\originalinlinetab{}B", ["original_whitespace", "inline_tab_layout"], macro_contract_verified=True)

    def test_inline_layout_rejects_wrong_scope_leading_tabs_and_changed_content(self):
        for rid, source, target in [
            ("p1", "A\tB", r"A\originalinlinetab{}B"),
            ("text-p-0303", "\tA\tB", r"\originalinlinetab{}A\originaltab{}B"),
            ("text-p-0303", "A\tB", r"A\originaltab{}B"),
            ("text-p-0303", "A\tB.", r"A\originalinlinetab{}B!"),
            ("text-p-0303", "A\tB", r"\originalinlinetab{}AB"),
            ("text-p-0303", "A\tB", "A B"),
            ("text-p-0303", "A\tB", r"A\originalinlinetab{}\originalinlinetab{}B"),
            ("text-p-0303", "A\tB\tC", r"A\originalinlinetab{}B\originalinlinetab{}C"),
        ]:
            with self.subTest(rid=rid, source=source, target=target):
                self.inline_case(rid, source, target)
                self.assertEqual(self.audit()["status"], "blocked", self.audit())

    def test_inline_layout_requires_exact_user_authorization_and_policy(self):
        import json
        from scripts.migration_harness.preservation import INLINE_TAB_AUTHORIZATION
        for key, value in [("quoted_instruction", ""), ("quoted_instruction", "Autorizado"), ("kind", "approved"), ("scope", []), ("execution_authorized", False), ("future_projects_approved", True), ("layout_source_ids", []), ("promoted_to_reusable_policy", True), ("status", "approved")]:
            with self.subTest(key=key):
                self.inline_case()
                path = self.root / INLINE_TAB_AUTHORIZATION
                data = json.loads(path.read_text())
                data[key] = value
                self.write(json.dumps(data), INLINE_TAB_AUTHORIZATION)
                self.assertIn("invalid_inline_tab_layout", self.codes(self.audit()))
        self.inline_case()
        (self.root / INLINE_TAB_AUTHORIZATION).unlink()
        self.assertIn("invalid_inline_tab_layout", self.codes(self.audit()))
        unit = self.inline_case()
        unit.pop("inline_tab_layout")
        self.assertIn("invalid_inline_tab_layout", self.codes(self.audit()))
        unit = self.inline_case()
        unit["inline_tab_layout"]["source_ids"].append("text-p-0314")
        self.assertIn("invalid_inline_tab_layout", self.codes(self.audit()))

    def test_inline_layout_contract_rejects_stale_body_alias_and_unit_redefinition(self):
        self.inline_case()
        self.ledger["macro_contract"]["sha256"] = "0" * 64
        self.assertIn("invalid_macro_contract", self.codes(self.audit()))
        for change in [r"\newcommand{\originalinlinetab}{\hspace{1cm}}", r"\newcommand{\originalinlinetab}{\unskip\space}\let\originalinlinetab\relax"]:
            self.inline_case()
            macros = (self.root / "macros.tex").read_text().replace(r"\newcommand{\originalinlinetab}{\unskip\space}", change)
            self.write(macros, "macros.tex")
            self.ledger["macro_contract"]["sha256"] = hashlib.sha256(macros.encode()).hexdigest()
            self.assertIn("invalid_macro_contract", self.codes(self.audit()))
        for redef in [r"\renewcommand{\originalinlinetab}{X}", r"\let\originalinlinetab\relax"]:
            unit = self.inline_case()
            value = (self.root / "unit.tex").read_text()
            self.write(redef + value)
            unit["element_map"] = [self.mapping("text-p-0303", value)]
            unit["element_map"][0]["serializations"] = ["original_whitespace", "inline_tab_layout"]
            self.assertIn("whitespace_macro_redefinition", self.codes(self.audit()))

    def reference_case(self, source="\tAção.", target=r"\originaltab{}Ação.", rid="text-p-0288", uid="chapter-02-text-h-0003"):
        import json
        from scripts.migration_harness.preservation import (REFERENCE_LAYOUT_AUTHORIZATION, REFERENCE_LAYOUT_USER_INSTRUCTION, REFERENCE_LAYOUT_BASELINE, REFERENCE_LAYOUT_UNITS, REFERENCE_LAYOUT_PARAGRAPHS)
        self.manifest = {"records": [{"id": "p1", "type": "text:p"}], "units": [{"id": "sprint-test"}], "assets": []}
        self.ledger = {"schema_version": 1, "units": {"sprint-test": {"state": "converted", "tex_path": "unit.tex", "element_map": []}}}
        self.whitespace_case(source, target)
        self.manifest["records"][0].update(id=rid, unit_id=uid, semantic_type="paragraph")
        self.manifest["units"][0].update(id=uid, record_ids=[rid], source_record_ids=[rid])
        unit = self.ledger["units"].pop("sprint-test", next(iter(self.ledger["units"].values())))
        self.ledger["units"] = {uid: unit}
        unit["element_map"][0].update(source_id=rid, serializations=["original_whitespace", "reference_paragraph_layout"])
        evidence = REFERENCE_LAYOUT_AUTHORIZATION
        if uid.startswith("ages-iii-") or uid.startswith("chapter-05-"):
            evidence = "migration/approvals/ages-iii-authorization.json"
        unit["reference_paragraph_layout"] = {"authorization_evidence": evidence, "source_ids": [rid]}
        macros = (self.root / "macros.tex").read_text().replace(r"\noindent\hspace*{1.251cm}", r"\hspace*{0pt}") + "\n" + r"\newcommand{\originalleadingspace}{\hspace*{0pt}}"
        self.write(macros, "macros.tex")
        self.ledger["macro_contract"]["sha256"] = hashlib.sha256(macros.encode()).hexdigest()
        (self.root / "migration/approvals").mkdir(parents=True, exist_ok=True)
        authorization = {"kind": "user_reference_style_request", "scope": list(REFERENCE_LAYOUT_UNITS), "paragraph_source_ids": list(REFERENCE_LAYOUT_PARAGRAPHS), "quoted_instruction": REFERENCE_LAYOUT_USER_INSTRUCTION, "baseline_commit": REFERENCE_LAYOUT_BASELINE, "status": "proposed_for_review", "future_projects_approved": False, "execution_authorized": True, "promoted_to_reusable_policy": False, "human_presentation_approval": None}
        self.write(json.dumps(authorization), REFERENCE_LAYOUT_AUTHORIZATION)
        if uid.startswith("ages-iii-") or uid.startswith("chapter-05-"):
            ages_iii_authorization = {
                "schema_version": 1,
                "record_type": "user_authorized_edition_scope",
                "edition": "AGES III / Sistema de Controle Inteligente de Estacionamento com RFID",
                "approval_status": "authorized_for_AGES_III_only; final edition approval pending",
                "source": {"path": "RELATORIO_ATUAL.odt", "sha256": "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef", "must_remain_unchanged": True},
                "scope": {"units": ["chapter-05-text-h-0074", "chapter-05-text-h-0075", "chapter-05-text-h-0076", "chapter-05-text-h-0077", "chapter-05-text-h-0078", "chapter-05-text-h-0079", "chapter-05-text-h-0080", "chapter-05-text-h-0085", "chapter-05-text-h-0086", "ages-iii-sprint-0", "ages-iii-sprint-1", "ages-iii-sprint-2", "ages-iii-sprint-3", "ages-iii-sprint-4", "chapter-05-text-h-0097"]},
                "presentation_and_preservation": {
                    "follow": "docs/STYLE_GUIDE.md and docs/QUALITY_GATES.md",
                    "source_text": "preserve exact wording, punctuation, order, and semantics; no editorial revisions",
                },
            }
            self.write(json.dumps(ages_iii_authorization), evidence)
        return unit

    def test_ages_iii_zero_width_leading_tab_uses_only_source_bound_style_policy(self):
        self.reference_case("\tAção.", r"\originaltab{}Ação.", "text-p-1111", "ages-iii-sprint-0")
        self.assertEqual(self.audit()["status"], "pass", self.audit())

    def test_ages_iii_whitespace_policy_matches_exact_manifest_prefixes(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        units = {item["id"]: item for item in manifest["units"]}
        for unit_id, expected_by_id in AGES_III_LEADING_TAB_COUNTS.items():
            unit = units[unit_id]
            actual_ids = _leading_tab_paragraph_ids(unit["source_record_ids"], records)
            with self.subTest(unit_id=unit_id):
                self.assertEqual(actual_ids, [rid for rid in unit["source_record_ids"] if rid in expected_by_id])
                for rid, count in expected_by_id.items():
                    source = records[rid]["text"]
                    self.assertEqual(len(source) - len(source.lstrip("\t")), count)
        self.assertEqual(AGES_III_INLINE_TAB_COUNTS, {"text-p-1084": 1})
        literal_tab = "consultas t\tipadas"
        with self.subTest(source_id="text-p-1084"):
            self.assertEqual(records["text-p-1084"]["text"].count(literal_tab), 1)
            self.assertEqual(records["text-p-1073"]["text"].count("\t"), 3)
            self.assertEqual(records["text-p-1077"]["text"].count("\t"), 2)

    def test_ages_iii_internal_tab_removal_is_exactly_authorized_and_source_mapped(self):
        repo = Path(__file__).resolve().parents[1]
        self.assertTrue((repo / AGES_III_INTERNAL_TAB_REMOVAL_AUTHORIZATION).is_file())
        authorization = _load_presentation_authorization(repo, "chapter-05-text-h-0085")
        self.assertEqual(
            authorization["approved_presentation_changes"]["internal_tab_removal"],
            AGES_III_INTERNAL_TAB_REMOVAL_POLICY,
        )
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        self.assertEqual(records["text-p-1084"]["text"].count("consultas t\tipadas"), 1)

        unit_id = "chapter-05-text-h-0085"
        unit = next(item for item in manifest["units"] if item["id"] == unit_id)
        ledger = json.loads((repo / "migration/ledgers/chapter-05-text-h-0085.json").read_text(encoding="utf-8"))["units"][unit_id]
        self.assertEqual(ledger["technology_prose_revision"]["format"], "mariah-project-prose-v2")
        self.assertEqual(ledger["technology_prose_revision"]["semantic_review"], "pending_independent_audit")
        target = (repo / ledger["tex_path"]).read_bytes()
        mapping = next(item for item in ledger["element_map"] if item["source_id"] == "text-p-1084")
        fragment = target[mapping["start_byte"]:mapping["end_byte"]].decode("utf-8")
        self.assertIn("consultas tipadas", fragment)
        self.assertNotIn(r"\originalinlinetab{}", fragment)
        self.assertEqual(mapping["disposition"], "narrative")
        self.assertEqual(mapping["source_text_sha256"], hashlib.sha256(records["text-p-1084"]["text"].encode()).hexdigest())

        with self.assertRaises(UnsupportedSerialization):
            _project_approved_presentation(
                "text-p-1085", "consultas t ipadas", "consultas tipadas",
                ["approved_technology_narrative", "approved_internal_tab_removal"], authorization,
            )

    def test_ages_iii_internal_tab_removal_rejects_stale_or_wrong_approval_file(self):
        repo = Path(__file__).resolve().parents[1]
        with patch(
            "scripts.migration_harness.preservation.AGES_III_INTERNAL_TAB_REMOVAL_AUTHORIZATION",
            "migration/approvals/ages-iii-authorization.json",
        ):
            with self.assertRaisesRegex(ValueError, "internal-tab removal approval"):
                _load_presentation_authorization(repo, "chapter-05-text-h-0085")

    def test_ages_iii_rejects_wrong_leading_tab_id_even_with_user_scope_authorization(self):
        self.reference_case("\tAção.", r"\originaltab{}Ação.", "text-p-0288", "ages-iii-sprint-0")
        self.assertIn("invalid_reference_paragraph_layout", self.codes(self.audit()))

    def test_ages_iii_prose_revision_keeps_original_internal_tabs_in_traceability(self):
        from scripts.migration_harness.technology_prose import verify
        from scripts.migration_harness.preservation import _load_presentation_authorization
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        uid = "chapter-05-text-h-0085"
        ledger = json.loads((repo / f"migration/ledgers/{uid}.json").read_text(encoding="utf-8"))
        authorization = _load_presentation_authorization(repo, uid)["approved_document_reordering"]["scope"]
        unit = next(item for item in manifest["units"] if item["id"] == uid)
        heading_id = unit["heading_id"]
        facts = verify(
            manifest, ledger, repo, uid,
            document_reordering_ids=ledger["units"][uid]["document_reordering_authorization"]["source_ids"],
            heading_display_text=authorization["heading_numbering"][heading_id]["target_text"],
        )
        self.assertEqual(records["text-p-1084"]["text"].count("consultas t\tipadas"), 1)
        self.assertFalse(facts["lexical_equality_claimed"])
        self.assertEqual(facts["semantic_review"]["status"], "PENDING")

    def test_ages_iii_internal_tab_policy_rejects_missing_marker(self):
        unit = self.reference_case("\tA\tB\tC", r"\originaltab{}A\originalinlinetab{}BC", "text-p-1073", "chapter-05-text-h-0085")
        unit["element_map"][0]["serializations"].append("inline_tab_layout")
        unit["inline_tab_layout"] = {
            "authorization_evidence": "migration/approvals/ages-iii-authorization.json",
            "source_ids": ["text-p-1073"],
        }
        macros = (self.root / "macros.tex").read_text() + "\n" + r"\newcommand{\originalinlinetab}{\unskip\space}"
        self.write(macros, "macros.tex")
        self.ledger["macro_contract"]["sha256"] = hashlib.sha256(macros.encode()).hexdigest()
        with patch.dict("scripts.migration_harness.preservation.AGES_III_TECHNICAL_CITATIONS", {"chapter-05-text-h-0085": {}}):
            report = self.audit()
        self.assertIn("unsupported_serialization", self.codes(report))

    def test_reference_layout_preserves_double_tabs_leading_space_and_emphasis(self):
        for source, target, rid, uid in [
            ("\tAção.", r"\originaltab{}\emph{Ação}.", "text-p-0288", "chapter-02-text-h-0003"),
            ("\t\tAção.", r"\originaltab{}\originaltab{}Ação.", "text-p-0473", "ages-i-sprint-1"),
            ("\t Ação.", r"\originaltab{}\originalleadingspace{}Ação.", "text-p-0413", "ages-i-sprint-0"),
        ]:
            with self.subTest(rid=rid):
                self.reference_case(source, target, rid, uid)
                self.assertEqual(self.audit()["status"], "pass", self.audit())

    def test_reference_layout_preserves_inline_tab_authorization_simultaneously(self):
        import json
        from scripts.migration_harness.preservation import INLINE_TAB_AUTHORIZATION, INLINE_TAB_USER_INSTRUCTION, INLINE_TAB_COUNTS
        uid = "chapter-02-text-h-0008"
        unit = self.reference_case("\tA\tFim.", r"\originaltab{}A\originalinlinetab{}Fim.", "text-p-0303", uid)
        unit["element_map"][0]["serializations"].append("inline_tab_layout")
        unit["inline_tab_layout"] = {"authorization_evidence": INLINE_TAB_AUTHORIZATION, "source_ids": ["text-p-0303"]}
        auth = {"kind": "user_format_correction_authorization", "scope": [uid], "quoted_instruction": INLINE_TAB_USER_INSTRUCTION, "status": "proposed_for_review", "future_projects_approved": False, "execution_authorized": True, "layout_source_ids": list(INLINE_TAB_COUNTS), "promoted_to_reusable_policy": False}
        self.write(json.dumps(auth), INLINE_TAB_AUTHORIZATION)
        macros = (self.root / "macros.tex").read_text() + "\n" + r"\newcommand{\originalinlinetab}{\unskip\space}"
        self.write(macros, "macros.tex")
        self.ledger["macro_contract"]["sha256"] = hashlib.sha256(macros.encode()).hexdigest()
        self.assertEqual(self.audit()["status"], "pass", self.audit())

    def test_reference_layout_requires_exact_request_review_boundary_and_scope(self):
        import json
        from scripts.migration_harness.preservation import REFERENCE_LAYOUT_AUTHORIZATION
        for key, value in [("quoted_instruction", "Autorizado"), ("kind", "approved"), ("scope", []), ("paragraph_source_ids", []), ("execution_authorized", False), ("baseline_commit", "0" * 40), ("future_projects_approved", True), ("promoted_to_reusable_policy", True), ("human_presentation_approval", "approved"), ("status", "approved")]:
            with self.subTest(key=key):
                self.reference_case()
                data = json.loads((self.root / REFERENCE_LAYOUT_AUTHORIZATION).read_text())
                data[key] = value
                self.write(json.dumps(data), REFERENCE_LAYOUT_AUTHORIZATION)
                self.assertIn("invalid_reference_paragraph_layout", self.codes(self.audit()))
        self.reference_case()
        (self.root / REFERENCE_LAYOUT_AUTHORIZATION).unlink()
        self.assertIn("invalid_reference_paragraph_layout", self.codes(self.audit()))

    def test_reference_layout_rejects_incomplete_or_wrong_record_policy(self):
        for mutation in ["missing_policy", "missing_flag", "extra_id", "wrong_id", "caption", "heading"]:
            with self.subTest(mutation=mutation):
                unit = self.reference_case()
                if mutation == "missing_policy":
                    unit.pop("reference_paragraph_layout")
                elif mutation == "missing_flag":
                    unit["element_map"][0]["serializations"].remove("reference_paragraph_layout")
                elif mutation == "extra_id":
                    unit["reference_paragraph_layout"]["source_ids"].append("text-p-0289")
                elif mutation == "wrong_id":
                    unit["reference_paragraph_layout"]["source_ids"] = ["text-p-0413"]
                elif mutation == "caption":
                    self.manifest["records"][0]["semantic_type"] = "caption"
                else:
                    self.manifest["records"][0]["type"] = "text:h"
                self.assertIn("invalid_reference_paragraph_layout", self.codes(self.audit()))
        self.reference_case(uid="ages-ii-sprint-0")
        self.assertIn("invalid_reference_paragraph_layout", self.codes(self.audit()))

    def test_reference_layout_rejects_missing_shifted_internal_markers_and_punctuation(self):
        for source, target, rid in [
            ("\t\tAção.", r"\originaltab{}Ação.", "text-p-0473"),
            ("\tAção.", r"\originaltab{}Ação!", "text-p-0288"),
            ("\t Ação.", r"\originaltab{}Ação.", "text-p-0413"),
            ("\t Ação.", r"\originaltab{}Ação.\originalleadingspace{}", "text-p-0413"),
            ("A B", r"A\originalleadingspace{}B", "text-p-0413"),
            (" Ação.", r"\originalleadingspace{}Ação.", "text-p-0288"),
            ("A\tB", r"A\originaltab{}B", "text-p-0288"),
        ]:
            with self.subTest(source=source, target=target):
                self.reference_case(source, target, rid)
                self.assertEqual(self.audit()["status"], "blocked", self.audit())

    def test_reference_layout_contract_and_new_macro_redefinition_fail_closed(self):
        self.reference_case()
        self.ledger["macro_contract"]["sha256"] = "0" * 64
        self.assertIn("invalid_macro_contract", self.codes(self.audit()))
        for replacement in [r"\newcommand{\originalleadingspace}{\hspace*{1pt}}", r"\newcommand{\originalleadingspace}{\hspace*{0pt}}\let\originalleadingspace\relax"]:
            self.reference_case()
            macros = (self.root / "macros.tex").read_text().replace(r"\newcommand{\originalleadingspace}{\hspace*{0pt}}", replacement)
            self.write(macros, "macros.tex")
            self.ledger["macro_contract"]["sha256"] = hashlib.sha256(macros.encode()).hexdigest()
            self.assertIn("invalid_macro_contract", self.codes(self.audit()))
        with self.assertRaises(UnsupportedSerialization):
            displayed_text(r"\originalleadingspace{}A", ["original_whitespace"], macro_contract_verified=True)

    def test_reference_structural_unit_can_verify_contract_without_body_policy_flags(self):
        unit = self.reference_case("Título", "Título", "fixture-heading-record", "fixture-heading")
        self.manifest["records"][0].update(type="text:h", semantic_type="heading")
        unit.pop("reference_paragraph_layout")
        unit["element_map"][0]["serializations"] = []
        self.write(r"\section*{Título}")
        unit["element_map"][0].update(self.mapping("fixture-heading-record", "Título"))
        unit["element_map"][0]["serializations"] = []
        self.assertEqual(self.audit()["status"], "pass", self.audit())

    def test_reference_indent_declaration_outside_source_span_is_structural(self):
        unit = self.reference_case()
        value = (self.root / "unit.tex").read_text()
        self.write(r"\indent " + value)
        unit["element_map"][0].update(self.mapping("text-p-0288", value))
        self.assertEqual(self.audit()["status"], "pass", self.audit())

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
        text = (self.root / "figures.tex").read_text().replace(
            r"\caption*{{\normalfont\upshape #2}}",
            r"\caption*{{\normalfont\upshape Inventado}}",
        )
        self.write(text, "figures.tex")
        self.ledger["figure_contract"]["sha256"] = hashlib.sha256(text.encode()).hexdigest()
        self.assertIn("invalid_figure_contract", self.codes(self.audit()))
        self.figure_case()
        self.figure_maps(value.replace("Figure 1: Ação", "Figure 1: Ação extra"))
        self.assertIn("invalid_image_evidence", self.codes(self.audit()))
        self.figure_case()
        self.ledger["units"]["sprint-test"]["asset_map"] = []
        self.assertIn("missing_image", self.codes(self.audit()))

    def test_canonical_figure_caption_and_list_entry_are_upright(self):
        from scripts.migration_harness.latex import MEMORIAL_FIGURE_BODY
        self.assertIn(r"\caption*{{\normalfont\upshape #2}}", MEMORIAL_FIGURE_BODY)
        self.assertIn(r"\addcontentsline{lof}{figure}{{\normalfont\upshape #2}}", MEMORIAL_FIGURE_BODY)
        self.assertNotIn(r"\textit", MEMORIAL_FIGURE_BODY)

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
        self.write(json.dumps({"schema_version": 1, "kind": "user_execution_authorization", "edition": "AGES I / Easy Choose", "baseline_commit": "68d159b9b4168f2a913f5c1e4913c30397310437", "scope": [uid], "quoted_instruction": "Vamos começar com AGES I. Lembre-se que os itens faltantes como arquitetura, banco de dados precisarão de placeholders que serão preenchidos posteriormente", "placeholders_explicitly_authorized": ["Banco de dados utilizado"]}), evidence)
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
        self.assertEqual(self.audit()["status"], "pass", self.audit())
        approval = json.loads((self.root / "migration/approvals/ages-i-authorization.json").read_text(encoding="utf-8"))
        approval["placeholders_explicitly_authorized"].remove("Banco de dados utilizado")
        self.write(json.dumps(approval), "migration/approvals/ages-i-authorization.json")
        self.assertIn("invalid_approved_apparatus", self.codes(self.audit()))
        unit["approved_apparatus"] = []
        self.assertIn("unsupported_target_scaffolding", self.codes(self.audit()))

    def user_supplied_content_case(self):
        uid = "ages-iv-sprint-2"
        self.manifest = {
            "records": [{"id": "text-h-0119", "type": "text:h", "text": "Sprint 2"}],
            "units": [{"id": uid, "record_ids": ["text-h-0119"], "source_record_ids": ["text-h-0119"]}],
            "assets": [],
        }
        report_tex = [
            r"Parágrafo com \textit{models} e \texttt{docs}.",
            "Segundo parágrafo.",
            "Terceiro parágrafo.",
            "Quarto parágrafo.",
            "Quinto parágrafo.",
        ]
        reflection_tex = ["Reflexão fiel.", "Segunda reflexão."]
        target = r"\subsection{Sprint 2}" + "\n"
        target += "\n".join(r"\indent " + text + r"\par" for text in report_tex) + "\n"
        target += r"\begin{reflection}" + "\n"
        target += "\n".join(r"\noindent " + text + r"\par" for text in reflection_tex) + "\n"
        target += r"\end{reflection}" + "\n"
        self.write(target)
        heading = self.mapping("text-h-0119", "Sprint 2")
        content = []
        for number, text in enumerate([
            "Parágrafo com *models* e `docs`.",
            "Segundo parágrafo.",
            "Terceiro parágrafo.",
            "Quarto parágrafo.",
            "Quinto parágrafo.",
        ], start=1):
            content.append({
                "content_id": f"user-ages-iv-sprint-2-report-p{number:02}",
                "kind": "report_paragraph",
                "source_markup": text,
                "sha256": hashlib.sha256(text.encode()).hexdigest(),
            })
        for number, text in enumerate(["Reflexão fiel.", "Segunda reflexão."], start=1):
            content.append({
                "content_id": f"user-ages-iv-sprint-2-reflection-p{number:02}",
                "kind": "reflection_paragraph",
                "source_markup": text,
                "sha256": hashlib.sha256(text.encode()).hexdigest(),
            })
        authorization = {
            "schema_version": 1,
            "record_type": "user_supplied_content_authorization",
            "approval_status": "authorized_for_inclusion_pending_human_review",
            "unit_id": uid,
            "user_instruction": "Agora vamos colocar o relatório da Sprint 2 (edição AGES IV) e também a caixa introspectiva.",
            "source": {
                "type": "direct_user_message",
                "source_odt_path": "RELATORIO_ATUAL.odt",
                "source_odt_sha256": "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef",
                "odt_relationship": "The ODF unit contains only its Sprint 2 heading; these seven paragraphs were supplied separately by the user and are not represented as ODT source records.",
            },
            "content": content,
        }
        auth_path = "migration/approvals/ages-iv-sprint-2-content-authorization.json"
        auth_data = json.dumps(authorization, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
        (self.root / "migration/approvals").mkdir(parents=True)
        (self.root / auth_path).write_bytes(auth_data)
        content_maps = []
        for source_item, tex_fragment in zip(content, report_tex + reflection_tex):
            mapping = self.mapping("unused", tex_fragment)
            mapping.pop("source_id")
            content_maps.append({"content_id": source_item["content_id"], **mapping})
        self.ledger = {
            "schema_version": 1,
            "compilation_root": ".",
            "units": {
                uid: {
                    "state": "converted",
                    "tex_path": "unit.tex",
                    "element_map": [heading],
                    "user_supplied_content": {
                        "authorization_evidence": auth_path,
                        "authorization_sha256": hashlib.sha256(auth_data).hexdigest(),
                        "content_map": content_maps,
                    },
                }
            },
        }
        return uid, content, target

    def test_user_supplied_sprint_text_is_authorized_and_compared_outside_odf_inventory(self):
        self.user_supplied_content_case()
        report = self.audit()
        self.assertEqual(report["status"], "pass", report)
        self.assertEqual(
            report["facts"]["user_supplied_content_checked"][0]["content_ids"],
            [
                "user-ages-iv-sprint-2-report-p01", "user-ages-iv-sprint-2-report-p02",
                "user-ages-iv-sprint-2-report-p03", "user-ages-iv-sprint-2-report-p04",
                "user-ages-iv-sprint-2-report-p05", "user-ages-iv-sprint-2-reflection-p01",
                "user-ages-iv-sprint-2-reflection-p02",
            ],
        )
        self.assertNotIn("unmapped_visible_content", self.codes(report))

    def test_user_supplied_sprint_text_rejects_changed_text(self):
        _, _, target = self.user_supplied_content_case()
        changed = target.replace(r"\textit{models}", r"\textit{modelos}")
        self.write(changed)
        self.assertIn("invalid_user_supplied_content", self.codes(self.audit()))

    def test_user_supplied_sprint_text_rejects_missing_inline_style(self):
        _, _, target = self.user_supplied_content_case()
        changed = target.replace(r"\textit{models}", "models")
        self.write(changed)
        self.assertIn("invalid_user_supplied_content", self.codes(self.audit()))

    def test_user_supplied_markup_supports_bold_caption_and_target_style_only(self):
        display, formatting = _parse_user_supplied_markup(
            "**Figura X – Planejamento** e *Fonte própria* com `moderation_action`"
        )
        self.assertEqual(display, "Figura X – Planejamento e Fonte própria com moderation_action")
        self.assertEqual(
            formatting,
            [("bold", "Figura X – Planejamento"), ("italic", "Fonte própria"), ("code", "moderation_action")],
        )
        target_display, target_formatting = _parse_user_supplied_markup(
            "**Figura X –** Planejamento e Fonte própria com `moderation_action`"
        )
        self.assertEqual(target_display, display)
        self.assertNotEqual(target_formatting, formatting)



if __name__ == "__main__":
    unittest.main()
