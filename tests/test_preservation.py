"""Adversarial synthetic fixtures; no memorial content is converted."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.migration_harness.preservation import (
    audit_conversion,
    displayed_text,
    UnsupportedSerialization,
    _project_approved_presentation,
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
    _load_presentation_authorization,
    AGES_II_TECHNOLOGY_REFERENCE_KEYS,
    AGES_II_TECHNOLOGY_TEXT_IDS,
    AGES_II_TECHNOLOGY_CITATIONS_AFTER,
    AGES_II_INLINE_TAB_COUNTS,
    AGES_II_LEADING_TAB_COUNTS,
    AGES_II_LEADING_SPACE_COUNTS,
    AGES_II_LEADING_LINE_BREAK_COUNTS,
    AGES_II_PRESENTATION_AUTHORIZATION,
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

    def test_ages_ii_authorized_citation_keys_exist_in_integrated_bibliography(self):
        repo = Path(__file__).resolve().parents[1]
        bibliography = (repo / "relatorio_AGES_eduardo/bibliografia/bibliografia.bib").read_text(encoding="utf-8")
        for key in AGES_II_TECHNOLOGY_REFERENCE_KEYS.values():
            with self.subTest(key=key):
                self.assertIn(f"@online{{{key},", bibliography)

    def test_ages_ii_prefix_tokens_project_exactly_and_are_scope_gated(self):
        repo = Path(__file__).resolve().parents[1]
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in manifest["records"]}
        self.assertTrue(records["text-h-0068"]["text"].startswith(" " * 4))
        self.assertEqual(len(records["text-h-0068"]["text"]) - len(records["text-h-0068"]["text"].lstrip(" ")), 4)
        self.assertEqual(records["text-p-0961"]["text"][:1], "\n")
        self.assertEqual(records["text-p-0969"]["text"][:1], "\n")
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
            for key in AGES_II_TECHNOLOGY_CITATIONS_AFTER.get(rid, []):
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
        self.assertEqual(evidence["displayed"], "Figura 1 – Foto do time – AGES I")
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
        unit["reference_paragraph_layout"] = {"authorization_evidence": REFERENCE_LAYOUT_AUTHORIZATION, "source_ids": [rid]}
        macros = (self.root / "macros.tex").read_text().replace(r"\noindent\hspace*{1.251cm}", r"\hspace*{0pt}") + "\n" + r"\newcommand{\originalleadingspace}{\hspace*{0pt}}"
        self.write(macros, "macros.tex")
        self.ledger["macro_contract"]["sha256"] = hashlib.sha256(macros.encode()).hexdigest()
        (self.root / "migration/approvals").mkdir(parents=True, exist_ok=True)
        authorization = {"kind": "user_reference_style_request", "scope": list(REFERENCE_LAYOUT_UNITS), "paragraph_source_ids": list(REFERENCE_LAYOUT_PARAGRAPHS), "quoted_instruction": REFERENCE_LAYOUT_USER_INSTRUCTION, "baseline_commit": REFERENCE_LAYOUT_BASELINE, "status": "proposed_for_review", "future_projects_approved": False, "execution_authorized": True, "promoted_to_reusable_policy": False, "human_presentation_approval": None}
        self.write(json.dumps(authorization), REFERENCE_LAYOUT_AUTHORIZATION)
        return unit

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
        unit = self.reference_case("Título", "Título", "text-h-0002", "chapter-02-text-h-0002")
        self.manifest["records"][0].update(type="text:h", semantic_type="heading")
        unit["reference_paragraph_layout"]["source_ids"] = []
        self.write(r"\section*{Título}")
        unit["element_map"][0].update(self.mapping("text-h-0002", "Título"))
        unit["element_map"][0]["serializations"] = ["original_whitespace"]
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
