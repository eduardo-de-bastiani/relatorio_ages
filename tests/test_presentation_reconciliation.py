"""Adversarial checks for the exact approved figure/title presentation changes."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.migration_harness import presentation_reconciliation as reconciliation
from scripts.migration_harness import recorda_deployment
from scripts.migration_harness.latex import _authorized_ages_iii_iv_figure_source


ROOT = Path(__file__).resolve().parents[1]


class PresentationReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ages-presentation-contract-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        paths = list(reconciliation.PINNED_AUTHORIZATION_SHA256.keys() - {reconciliation.FIGURE_REMOVAL_AUTHORIZATION})
        paths.extend(f"migration/ledgers/{unit}.json" for unit in (
            "chapter-05-text-h-0074", "chapter-06-text-h-0105"))
        for relative in paths:
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def test_offsets_compose_after_document_order_and_gantt(self):
        for previous, final in ((1, 1), (2, 4), (6, 8), (7, 10), (32, 35), (33, 36), (35, 38)):
            with self.subTest(previous=previous):
                self.assertEqual(reconciliation.figure_number(previous), final)
        for invalid in (0, 36):
            with self.assertRaises(ValueError):
                reconciliation.figure_number(invalid)
        caption, evidence = reconciliation.projected_caption(
            self.repo, "Figure 6: Foto do time - CLIENTE AGES",
            "Figura 33 – Foto do time - CLIENTE AGES")
        self.assertEqual(caption, "Figura 36 – Foto do time - CLIENTE AGES")
        self.assertEqual(evidence["previous_figure_number"], 33)

    def test_caption_tab_is_preserved_and_cannot_be_silently_removed(self):
        source = "\tFigure 16: Foto do Time - AGES III"
        caption, evidence = reconciliation.projected_caption(
            self.repo, source, "\tFigura 13 – Foto do Time - AGES III")
        self.assertEqual(caption, "\tFigura 16 – Foto do Time - AGES III")
        self.assertEqual(evidence["figure_number"], 16)
        with self.assertRaises(ValueError):
            reconciliation.projected_caption(self.repo, source, "Figura 13 – Foto do Time - AGES III")

    def test_altered_numbering_authorization_fails_closed(self):
        path = self.repo / reconciliation.DIAGRAM_AUTHORIZATION
        data = json.loads(path.read_text())
        data["renumbering"] = "Accept any figure number"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            reconciliation.load(self.repo)

    def test_gantt_uses_legacy_number_only_when_new_contract_is_absent(self):
        self.assertEqual(reconciliation.sprint3_gantt_number(self.repo), 35)
        path = self.repo / reconciliation.DIAGRAM_AUTHORIZATION
        path.write_text("{}")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            reconciliation.sprint3_gantt_number(self.repo)
        path.unlink()
        self.assertEqual(reconciliation.sprint3_gantt_number(self.repo), 32)

    def test_figure_removal_shifts_only_following_numbers(self):
        relative = reconciliation.FIGURE_REMOVAL_AUTHORIZATION
        shutil.copyfile(ROOT / relative, self.repo / relative)
        for previous, final in ((16, 19), (18, 20), (19, 21), (20, 22), (35, 37)):
            base = f"Figura {previous} – Legenda"
            caption, _ = reconciliation.projected_caption(self.repo, base)
            self.assertEqual(caption, f"Figura {final} – Legenda")
        with self.assertRaisesRegex(ValueError, "Removed figure"):
            reconciliation.projected_caption(self.repo, "Figura 17 – Legenda")
        self.assertEqual(reconciliation.sprint3_gantt_number(self.repo), 34)
        (self.repo / relative).write_text("{}")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            reconciliation.sprint3_gantt_number(self.repo)

    def test_latest_figure_15_source_supersedes_old_personal_collection(self):
        label = "fig:ages-ii-sprint-4-presenca-digital"
        self.assertEqual(reconciliation.authorized_source(
            self.repo, label, "Fonte: Eduardo Colla De Bastiani, 2024."),
            reconciliation.FIGURE_SOURCE_SUPPLEMENT)
        self.assertIsNone(reconciliation.authorized_source(
            self.repo, label, "Fonte: Acervo pessoal do autor."))
        correct = r"Fonte: \url{https://tools.ages.pucrs.br/easy-choose/wiki/-/wikis/home}"
        self.assertIsNotNone(reconciliation.authorized_source(
            self.repo, "ages-i:draw-image-0001", correct))
        self.assertIsNone(reconciliation.authorized_source(
            self.repo, "ages-i:draw-image-0001", correct.replace("/home", "/other")))

    def test_exact_four_figure_sources_reject_old_and_wrong_year(self):
        cases = (
            ("fig:ages-ii-sprint-4-presenca-digital", 2024),
            ("ages-iv:draw-image-0033", 2026),
            ("ages-iv:draw-image-0034", 2026),
            ("ages-iv:sprint3:gantt", 2026),
        )
        for label, year in cases:
            with self.subTest(label=label):
                self.assertEqual(reconciliation.authorized_source(self.repo, label, f"Fonte: Eduardo Colla De Bastiani, {year}."), reconciliation.FIGURE_SOURCE_SUPPLEMENT)
                self.assertIsNone(reconciliation.authorized_source(self.repo, label, "Fonte: elaboração própria."))
                self.assertIsNone(reconciliation.authorized_source(self.repo, label, f"Fonte: Eduardo Colla De Bastiani, {year + 1}."))
        self.assertIsNone(reconciliation.authorized_source(self.repo, "wrong-label", "Fonte: Eduardo Colla De Bastiani, 2026."))

    def test_source_supplement_tampering_fails_closed(self):
        path = self.repo / reconciliation.FIGURE_SOURCE_SUPPLEMENT
        data = json.loads(path.read_text())
        data["scope"][0]["after_markup"] = "Fonte: outra pessoa."
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            reconciliation.authorized_source(self.repo, "fig:ages-ii-sprint-4-presenca-digital", "Fonte: outra pessoa.")

    def test_diagram_is_bound_to_exact_unit_path_and_actual_asset_hash(self):
        for item in reconciliation.load(self.repo)["images"]:
            with self.subTest(image=item["destination"]):
                digest = hashlib.sha256((ROOT / item["destination"]).read_bytes()).hexdigest()
                self.assertEqual(digest, item["sha256"])
                self.assertIsNotNone(reconciliation.authorized_asset(
                    self.repo, item["unit"], item["destination"], digest))
                self.assertIsNone(reconciliation.authorized_asset(
                    self.repo, "other-unit", item["destination"], digest))
                self.assertIsNone(reconciliation.authorized_asset(
                    self.repo, item["unit"], item["destination"], hashlib.sha256(b"corrupt").hexdigest()))

    def test_title_correction_requires_separate_pinned_approval_and_ledger(self):
        result = reconciliation.title_corrections(self.repo)
        self.assertEqual(result["scope"]["text-h-0105"]["target_text"],
                         "5 PROJETO AGES IV - RECORDA ")
        path = self.repo / reconciliation.TITLE_CORRECTION_AUTHORIZATION
        data = json.loads(path.read_text())
        data["scope"][0]["target_text"] = "Unauthorized new chapter"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            reconciliation.title_corrections(self.repo)

    def test_recorda_deployment_requires_the_exact_supplied_png_and_caption(self):
        approval = recorda_deployment.load(ROOT)
        figure = approval["figure_25"]
        for relative in (recorda_deployment.APPROVAL, figure["asset_path"]):
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        root = self.repo / "relatorio_AGES_eduardo"
        local_unit = (self.repo / figure["target_file"]).relative_to(root)
        args = tuple(figure["figure_args"])
        self.assertTrue(_authorized_ages_iii_iv_figure_source(root, local_unit, args))
        self.assertFalse(_authorized_ages_iii_iv_figure_source(root, local_unit, args[:4] + ("0.92",)))
        asset = self.repo / figure["asset_path"]
        asset.write_bytes(asset.read_bytes() + b"changed")
        self.assertFalse(_authorized_ages_iii_iv_figure_source(root, local_unit, args))

    def test_title_approval_cannot_cover_missing_user_decision(self):
        path = self.repo / "migration/ledgers/chapter-06-text-h-0105.json"
        data = json.loads(path.read_text())
        del data["units"]["chapter-06-text-h-0105"]["user_title_correction"]
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "ledger is missing or stale"):
            reconciliation.title_corrections(self.repo)


if __name__ == "__main__":
    unittest.main()
