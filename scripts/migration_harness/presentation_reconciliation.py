"""Pinned 2026-11-05 figure/source reconciliation contract.

This module recognizes only the user's approved diagram replacements and
figure-number offsets. It does not verify that URLs resolve or prove image
authorship; those remain separate human/source-review questions.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


DIAGRAM_AUTHORIZATION = "migration/approvals/ages-i-ii-diagrams-2026-11-05.json"
SOURCE_AUTHORIZATIONS = {
    "ages-i": "migration/approvals/ages-i-figure-sources-2026-11-05.json",
    "ages-ii": "migration/approvals/ages-ii-figure-sources-2026-11-05.json",
    "ages-iii-iv": "migration/approvals/ages-iii-iv-figure-sources-2026-11-05.json",
    "hoortech": "migration/approvals/hoortech-figure-sources-2026-11-05.json",
}
FIGURE_SOURCE_SUPPLEMENT = "migration/approvals/figure-source-identification-2026-11-11.json"
FIGURE_SOURCE_SUPPLEMENT_SHA256 = "1a9309b127ede59a031e9d42dd11715e0b70706681503a58e12a6ff1e27b655f"
TITLE_CORRECTION_AUTHORIZATION = "migration/approvals/body-chapter-title-corrections-2026-11-05.json"
TITLE_CORRECTION_SHA256 = "84d0d7560ff3cbe82dbfc9e69716a9265d4d882fd659d820fa26e17b17d2006f"
TITLE_CORRECTION_RECORD_TYPE = "user_authorized_body_title_corrections"
PINNED_AUTHORIZATION_SHA256 = {
    FIGURE_SOURCE_SUPPLEMENT: FIGURE_SOURCE_SUPPLEMENT_SHA256,
    DIAGRAM_AUTHORIZATION: "36e0b181dd61ec381978a1c58c7c153e02799440d7bbe28293c7c4a14c8c6c32",
    SOURCE_AUTHORIZATIONS["ages-i"]: "7c779878bf004ddb4f4fc8da35cf38d1d2b1e3303fbbe1cb30990c8c97852691",
    SOURCE_AUTHORIZATIONS["ages-ii"]: "2d1e33416b492f5ecc67c252d56ac35575ed0300c4dbafdb5e44efcafc28ef2a",
    SOURCE_AUTHORIZATIONS["ages-iii-iv"]: "ea7836f5c31a96ef62150bc03babeabdab0f87e2577a687c99f1e79bb39d2021",
    SOURCE_AUTHORIZATIONS["hoortech"]: "ac1dee75376c229347b3de10adae0136e8d10d52470b3dd9ad4d4a55faa15bbc",
    TITLE_CORRECTION_AUTHORIZATION: TITLE_CORRECTION_SHA256,
}
EXPECTED_RENUMBERING = "Figura 1 inalterada; anteriores 2–6 somam 2; anteriores 7–35 somam 3. Figura anterior 7 substituída pela nova figura 10."
SOURCE_STATUS = "NOT_CHECKED"
TITLE_CORRECTIONS = {
    "text-h-0074": {
        "source_text": "5 - PROJETOS AGES III – SISTEMA DE CONTROLE INTELIGENTE DE ESTACIONAMENTO COM RFID",
        "document_order_text": "4 PROJETOS AGES III – SISTEMA DE CONTROLE INTELIGENTE DE ESTACIONAMENTO COM RFID",
        "target_text": "4 PROJETO AGES III – SISTEMA DE CONTROLE INTELIGENTE DE ESTACIONAMENTO COM RFID",
    },
    "text-h-0105": {
        "source_text": "6 - PROJETOS AGES IV - RECORDA ",
        "document_order_text": "5 PROJETOS AGES IV - RECORDA ",
        "target_text": "5 PROJETO AGES IV - RECORDA ",
    },
}


def _load_pinned(repo: Path, relative_path: str) -> dict:
    path = repo / relative_path
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != PINNED_AUTHORIZATION_SHA256[relative_path]:
        raise ValueError(f"Figure/source authorization hash mismatch: {relative_path}")
    return json.loads(data.decode("utf-8"))


def load(repo: Path) -> dict:
    """Validate all approved contracts and return the pinned diagram record."""
    diagrams = _load_pinned(repo, DIAGRAM_AUTHORIZATION)
    if (diagrams.get("date") != "2026-11-05"
            or diagrams.get("renumbering") != EXPECTED_RENUMBERING
            or len(diagrams.get("images", [])) != 4
            or diagrams.get("source_pending") != "As fontes/autorias das quatro imagens permanecem pendentes de identificação."):
        raise ValueError("Diagram authorization is stale or its exact scope changed")
    for relative in SOURCE_AUTHORIZATIONS.values():
        _load_pinned(repo, relative)
    return diagrams


def title_corrections(repo: Path) -> dict:
    """Return exact body-title edits from the user's 2026-11-05 instruction."""
    approval = _load_pinned(repo, TITLE_CORRECTION_AUTHORIZATION)
    expected_scope = [
        {
            "unit_id": "chapter-05-text-h-0074",
            "source_id": "text-h-0074",
            **TITLE_CORRECTIONS["text-h-0074"],
            "change": "Only the displayed chapter-body title wording changes from PROJETOS to PROJETO after the approved chapter-order renumbering. The ODT source record remains unchanged.",
        },
        {
            "unit_id": "chapter-06-text-h-0105",
            "source_id": "text-h-0105",
            **TITLE_CORRECTIONS["text-h-0105"],
            "change": "Only the displayed chapter-body title wording changes from PROJETOS to PROJETO after the approved chapter-order renumbering. The ODT source record remains unchanged.",
        },
    ]
    if (approval.get("schema_version") != 1
            or approval.get("record_type") != TITLE_CORRECTION_RECORD_TYPE
            or approval.get("date") != "2026-11-05"
            or approval.get("approval_status") != "authorized_for_exact_body_title_corrections_pending_human_review"
            or approval.get("source") != {
                "path": "RELATORIO_ATUAL.odt",
                "sha256": "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef",
                "must_remain_unchanged": True,
            }
            or approval.get("scope") != expected_scope
            or approval.get("review_status") != {"odt_source_unchanged": True, "human_review": "pending"}):
        raise ValueError("Body title correction approval is stale or exceeds its exact scope")
    for source_id, spec in TITLE_CORRECTIONS.items():
        unit_id = "chapter-05-text-h-0074" if source_id == "text-h-0074" else "chapter-06-text-h-0105"
        ledger = json.loads((repo / "migration/ledgers" / f"{unit_id}.json").read_text(encoding="utf-8"))
        unit_ledger = ledger.get("units", {}).get(unit_id, {})
        expected_title_record = {
            "decision": "PROJETOS alterado para PROJETO no título do corpo, a pedido explícito do autor em 05/11/2026; sumário já estava no singular.",
            "source_id": source_id,
        }
        if (unit_ledger.get("user_title_correction") != expected_title_record
                or unit_ledger.get("document_reordering_authorization", {}).get("authorization_evidence")
                != "migration/approvals/cliente-hoortech-and-document-order-authorization.json"):
            raise ValueError(f"Body title correction ledger is missing or stale for {source_id}")
    return {
        "authorization_evidence": TITLE_CORRECTION_AUTHORIZATION,
        "source_odt_unchanged": True,
        "scope": TITLE_CORRECTIONS,
    }


def figure_number(old_number: int) -> int:
    """Map original caption numbers through the exact approved 2026-11-05 rule."""
    if old_number == 1:
        return 1
    if 2 <= old_number <= 6:
        return old_number + 2
    if 7 <= old_number <= 35:
        return old_number + 3
    raise ValueError(f"Original figure number outside authorized range: {old_number}")


def sprint3_gantt_number(repo: Path) -> int:
    """Return the approved Gantt display number, retaining Figure 32 for legacy roots.

    A missing overlay means a historical fixture. A present but invalid overlay
    must fail closed rather than silently selecting the historical number.
    """
    if not (repo / DIAGRAM_AUTHORIZATION).exists():
        return 32
    load(repo)
    return figure_number(32)


def projected_caption(repo: Path, source_text: str, post_order_target: str | None = None) -> tuple[str, dict]:
    """Apply the approved global offset after any earlier ordering overlays."""
    load(repo)
    source_leading = re.match(r"^[ \t\r\n]*", source_text)[0]
    match = re.match(r"^(Figure|Figura)\s+(\d+)(:|\s+[–-]\s+)(.*)$", source_text[len(source_leading):], re.DOTALL)
    if not match:
        raise ValueError("Source caption is outside the pinned figure reconciliation contract")
    base = post_order_target if post_order_target is not None else source_text
    base_leading = re.match(r"^[ \t\r\n]*", base)[0]
    if base_leading != source_leading:
        raise ValueError("Prior caption target changed its source leading whitespace")
    base_match = re.match(r"^(Figure|Figura)\s+(\d+)(:|\s+[–-]\s+)(.*)$", base[len(base_leading):], re.DOTALL)
    if not base_match:
        raise ValueError("Prior presentation target is outside the pinned figure reconciliation contract")
    old_number = int(base_match.group(2))
    new_number = figure_number(old_number)
    body = base_match.group(4)
    displayed = source_leading + f"Figura {new_number} – {body}"
    return displayed, {
        "kind": "user_authorized_figure_number_reconciliation",
        "source": source_text,
        "previous_displayed": base,
        "displayed": displayed,
        "previous_figure_number": old_number,
        "figure_number": new_number,
        "authorization_evidence": DIAGRAM_AUTHORIZATION,
        "source_status": SOURCE_STATUS,
    }


def authorized_asset(repo: Path, unit_id: str, target_file: str, digest: str) -> dict | None:
    """Match a replacement image by exact unit, path, and approved SHA-256."""
    diagrams = load(repo)
    for item in diagrams["images"]:
        if (item.get("unit") == unit_id and item.get("destination") == target_file
                and item.get("sha256") == digest):
            return item
    return None


def figure_specs(repo: Path) -> list[dict]:
    """Return the four exact user-supplied diagrams, including the replacement."""
    diagrams = load(repo)
    specs = []
    for item in diagrams["images"]:
        spec = dict(item)
        spec["target_file"] = "relatorio_AGES_eduardo/conteudo/migracao/" + item["unit"] + ".tex"
        spec["source_record_id"] = None
        specs.append(spec)
    replaced = diagrams.get("replaced_original", {})
    if replaced != {
        "source_id": "draw-image-0010",
        "caption_id": "text-p-0788",
        "asset": "relatorio_AGES_eduardo/imagens/original/asset-0008.png",
        "disposition": "preservado no repositório, retirado do PDF a pedido do autor",
    }:
        raise ValueError("Replacement record differs from its exact user authorization")
    match = next(item for item in specs if item["unit"] == "chapter-04-text-h-0044")
    match["source_record_id"] = replaced["source_id"]
    match["source_caption_id"] = replaced["caption_id"]
    match["source_asset"] = replaced["asset"]
    return specs


def authorized_source(repo: Path, label: str, source_markup: str) -> str | None:
    """Match figure-source markup exactly; do not claim the URL was visited."""
    load(repo)
    effective: dict[str, tuple[str, str]] = {}
    for key, relative in SOURCE_AUTHORIZATIONS.items():
        approval = _load_pinned(repo, relative)
        for source_label, markup in approval.get("source_markup", {}).items():
            effective[source_label] = (markup, relative)
        for source_label, value in approval.get("sources", {}).items():
            if not isinstance(value, str):
                continue
            escaped = value.replace("%", r"\%")
            effective[source_label] = (f"Fonte: \\url{{{escaped}}}", relative)
    # The later, separately pinned decision supersedes only these four labels.
    supplement_path = repo / FIGURE_SOURCE_SUPPLEMENT
    if supplement_path.exists():
        supplement = _load_pinned(repo, FIGURE_SOURCE_SUPPLEMENT)
        for item in supplement["scope"]:
            effective[item["label"]] = (item["after_markup"], FIGURE_SOURCE_SUPPLEMENT)
    expected = effective.get(label)
    if expected is None:
        return None
    markup, relative = expected
    return relative if markup == source_markup else None
