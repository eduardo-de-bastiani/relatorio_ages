"""Independent preservation audit, using source records and actual target bytes.

Ledger schema 1 maps each source record to a UTF-8 byte interval in a file:
{source_id, target_file, start_byte, end_byte, target_sha256,
 serializations?: ["tex_quotes", "tex_dashes", "canonical_unicode", "original_whitespace", "inline_tab_layout", "reference_paragraph_layout"]}.
original_whitespace requires macro_contract {path, sha256} in the unit ledger
(or top-level ledger) and the exact audited originaltab/originalspace definitions.
inline_tab_layout is a narrowly authorized formatting correction for three AGES I
records: its originalinlinetab projects back to the original tab token while the
verified macro prints ordinary word spacing. This proves source-token position
and count, not literal PDF whitespace equivalence or approval for other projects.
reference_paragraph_layout requires the exact original 82 body paragraphs in the
15 authorized units, the user request evidence, and zero-width leading metadata
macros. It preserves source tokens without claiming PDF whitespace equivalence.
AGES II uses the same narrowly scoped token contract for its audited leading
tabs and the Sprint 4 heading/line-break prefixes; those IDs and counts are
frozen in its presentation authorization. The leading line-break marker has
zero width because the target paragraph/figure boundary carries the layout.
Intervals are half-open. Text copied into the ledger is never audit evidence.
Asset maps use {source_id: image occurrence id, target_file: image path}.
The image occurrence also requires an element_map interval containing exactly
one includegraphics command. Target paths are repository-relative; LaTeX asset
paths are relative to ledger.compilation_root (default repository root).

This is a conservative lexical proof, not a TeX interpreter. Unsupported
macros fail closed. PDF inspection and human approval are separate gates.
"""
from __future__ import annotations

import difflib
import json
import hashlib
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .latex import _group, commands, strip_comments, macro_definitions, canonical_macro_body, MEMORIAL_FIGURE_BODY


INLINE_TAB_COUNTS = {"text-p-0303": 1, "text-p-0314": 4, "text-p-0318": 4}
INLINE_TAB_AUTHORIZATION = "migration/approvals/ages-i-format-correction.json"
INLINE_TAB_USER_INSTRUCTION = "Você cometeu alguns erros de formatação. Precisamos corrigir esses erros, validar novamente e, depois que eu aprovar, registrar essas mudanças como algo permanente para os demais projetos da AGES"
AGES_II_INLINE_TAB_COUNTS = {
    "text-p-0814": 1,
    "text-p-0975": 2,
    "text-p-0976": 2,
    "text-p-0977": 2,
}
AGES_II_INLINE_TAB_AUTHORIZATION = "migration/approvals/ages-ii-presentation-reuse.json"


REFERENCE_LAYOUT_AUTHORIZATION = "migration/approvals/ages-i-mariah-style.json"
REFERENCE_LAYOUT_USER_INSTRUCTION = 'Batendo com o relatório da Mariah, estamos utilizando a mesma formatação? Eu gostaria de usar a mesma formatação que ela'
REFERENCE_LAYOUT_BASELINE = 'e5a367d438fe865223879ed4742d52379e563335'
REFERENCE_LAYOUT_UNITS = (
    'chapter-02-text-h-0002', 'chapter-02-text-h-0003', 'chapter-02-text-h-0007', 'chapter-02-text-h-0008',
    'chapter-02-text-h-0009', 'chapter-02-text-h-0010', 'chapter-02-text-h-0011', 'chapter-02-text-h-0012',
    'chapter-02-text-h-0014', 'ages-i-sprint-0', 'ages-i-sprint-1', 'ages-i-sprint-2',
    'ages-i-sprint-3', 'ages-i-sprint-4', 'chapter-02-text-h-0022',
)
REFERENCE_LAYOUT_PARAGRAPHS = (
    'text-p-0288', 'text-p-0289', 'text-p-0290', 'text-p-0303',
    'text-p-0304', 'text-p-0306', 'text-p-0307', 'text-p-0309',
    'text-p-0310', 'text-p-0314', 'text-p-0315', 'text-p-0318',
    'text-p-0319', 'text-p-0322', 'text-p-0323', 'text-p-0325',
    'text-p-0376', 'text-p-0378', 'text-p-0379', 'text-p-0380',
    'text-p-0381', 'text-p-0385', 'text-p-0386', 'text-p-0387',
    'text-p-0388', 'text-p-0390', 'text-p-0391', 'text-p-0392',
    'text-p-0394', 'text-p-0395', 'text-p-0396', 'text-p-0398',
    'text-p-0399', 'text-p-0400', 'text-p-0402', 'text-p-0413',
    'text-p-0415', 'text-p-0417', 'text-p-0419', 'text-p-0424',
    'text-p-0425', 'text-p-0426', 'text-p-0427', 'text-p-0428',
    'text-p-0465', 'text-p-0466', 'text-p-0467', 'text-p-0468',
    'text-p-0469', 'text-p-0470', 'text-p-0472', 'text-p-0473',
    'text-p-0474', 'text-p-0475', 'text-p-0476', 'text-p-0509',
    'text-p-0510', 'text-p-0511', 'text-p-0521', 'text-p-0522',
    'text-p-0523', 'text-p-0557', 'text-p-0558', 'text-p-0559',
    'text-p-0560', 'text-p-0561', 'text-p-0562', 'text-p-0565',
    'text-p-0566', 'text-p-0592', 'text-p-0593', 'text-p-0594',
    'text-p-0595', 'text-p-0606', 'text-p-0607', 'text-p-0637',
    'text-p-0638', 'text-p-0639', 'text-p-0640', 'text-p-0641',
    'text-p-0642', 'text-p-0643',
)
AGES_II_UNITS = (
    "chapter-04-text-h-0039", "chapter-04-text-h-0040", "chapter-04-text-h-0041",
    "chapter-04-text-h-0042", "chapter-04-text-h-0043", "chapter-04-text-h-0044",
    "chapter-04-text-h-0045", "chapter-04-text-h-0046", "chapter-04-text-h-0047",
    "ages-ii-sprint-0", "ages-ii-sprint-1", "ages-ii-sprint-2", "ages-ii-sprint-3",
    "ages-ii-sprint-4", "chapter-04-text-h-0073",
)
AGES_II_LEADING_TAB_COUNTS = {
    "chapter-04-text-h-0040": {"text-p-0763": 1, "text-p-0764": 1, "text-p-0765": 1},
    "chapter-04-text-h-0046": {
        "text-p-0814": 1, "text-p-0815": 1, "text-p-0819": 2,
        "text-p-0823": 2, "text-p-0831": 1,
    },
    "ages-ii-sprint-0": {rid: 1 for rid in ("text-p-0844", "text-p-0845", "text-p-0846", "text-p-0847", "text-p-0848", "text-p-0851", "text-p-0852")},
    "ages-ii-sprint-1": {rid: 1 for rid in ("text-p-0876", "text-p-0877", "text-p-0878", "text-p-0879", "text-p-0880")},
    "ages-ii-sprint-2": {rid: 1 for rid in ("text-p-0915", "text-p-0916", "text-p-0917")},
    "ages-ii-sprint-3": {rid: 1 for rid in ("text-p-0942", "text-p-0943")},
    "ages-ii-sprint-4": {rid: 1 for rid in ("text-p-0971", "text-p-0973", "text-p-0979", "text-p-0983", "text-p-0984", "text-p-0998", "text-p-1004", "text-p-1005", "text-p-1006")},
}
AGES_II_LEADING_SPACE_COUNTS = {"ages-ii-sprint-4": {"text-h-0068": 4}}
AGES_II_LEADING_LINE_BREAK_COUNTS = {
    "ages-ii-sprint-4": {"text-p-0961": 1, "text-p-0969": 1},
}
AGES_II_PRESENTATION_AUTHORIZATION = "migration/approvals/ages-ii-presentation-reuse.json"

PRESENTATION_AUTHORIZATION = "migration/approvals/ages-i-presentation-corrections.json"
PRESENTATION_USER_INSTRUCTION = (
    'Sobre as alterações que você pontuou, pode aplicar todas, exceto aquelas que nós precisamos validar manualmente cada uma, '
    'como por exemplo a identificação da fonte de cada uma das imagens, e isso eu vou fazer manualmente. Sobre os links dos '
    'repositórios, nós temos que fazer da mesma maneira que a Mariah fez, que é colocar como forma de texto, por exemplo: '
    '"mais informações podem ser encontradas no repositório Easy Choose API" (com um link direto para o repositório, com já existe). '
    'Então esses pontos nós precisamos fazer muito similar à Mariah, nessa questão de estrutura. E mais pra frente, depois que '
    'fizermos toda a estruturação de todas as edições da AGES, nós vamos começar a melhorar questões como conteúdo do relatório.'
)
PRESENTATION_LIST_MARKER_INSTRUCTION = (
    "You're are not following Mariah's practices of formatting. You must follow the same pattern as she is. I have uploaded some printscreens of her memorial so you can use it as a reference. Not only that, you are also using useless spacings, italic in links and picture descriptions and bullet points. This goes totally against ABNT practices. Do it again, but YOU MUST USE Mariah's memorial as reference. Her structure is the goal"
)
PRESENTATION_LIST_MARKERS = {
    "text-list-0025": {
        "target_file": "relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0012.tex",
        "item_count": 5,
        "tex_environment": r"\begin{itemize}[label={},leftmargin=0pt,labelsep=0pt]",
        "visible_marker": "suppressed",
    }
}
PRESENTATION_CAPTIONS = {
    "text-p-0293": ("Figure 1: ", "Figura 1 – "),
    "text-p-0328": ("Figure 2: ", "Figura 2 – "),
    "text-p-0356": ("Figure 3: ", "Figura 3 – "),
    "text-p-0372": ("Figure 4: ", "Figura 4 – "),
    "text-p-0650": ("Figure 5: ", "Figura 5 – "),
    "text-p-0767": ("Figure 9: ", "Figura 9 – "),
    "text-p-0788": ("Figure 10: ", "Figura 10 – "),
    "text-p-0797": ("Figure 11: ", "Figura 11 – "),
    "text-p-0800": ("Figure 12: ", "Figura 12 – "),
    "text-p-0802": ("Figure 13: ", "Figura 13 – "),
    "text-p-0804": ("Figure 14: ", "Figura 14 – "),
    "text-p-0962": ("Figure 15: ", "Figura 15 – "),
}
PRESENTATION_HEADINGS = {
    "text-h-0002": ("2 - PROJETO AGES I – EASY CHOOSE", "2 PROJETO AGES I – EASY CHOOSE"),
    "text-h-0022": ("2.4. Conclusão", "2.4 Conclusão"),
    "text-h-0039": ("4 - PROJETO AGES II – INDÚSTRIA DIGITAL", "4 PROJETO AGES II – INDÚSTRIA DIGITAL"),
    "text-h-0073": ("4.4. Conclusão", "4.4 Conclusão"),
}
PRESENTATION_CROSS_REFERENCES = {
    "text-p-0290": {"suffix": " A equipe está retratada na Figura~\\ref{ages-i:draw-image-0001}."},
    "text-p-0325": {"replace_suffix": {"from": ":", "to": " (Figuras~\\ref{ages-i:draw-image-0002} a~\\ref{ages-i:draw-image-0004}):"}},
    "text-p-0642": {"suffix": " O registro do projeto selecionado está na Figura\\hspace{0.6em}\\hyperref[fig:ages-i-projeto-destaque]{\\ref*{fig:ages-i-projeto-destaque}}."},
}
PRESENTATION_REPOSITORY_LINKS = {
    "text-a-0105": {"href": "https://tools.ages.pucrs.br/easy-choose/easychooseadmin", "source_anchor": "Repositório EasyChooseAdmin", "prefix": "Mais informações podem ser encontradas no repositório ", "anchor": "Easy Choose Admin", "suffix": "."},
    "text-a-0106": {"href": "https://tools.ages.pucrs.br/easy-choose/easychoosevarejista", "source_anchor": "Repositório EasyChooseStore", "prefix": "Mais informações podem ser encontradas no repositório ", "anchor": "Easy Choose Store", "suffix": "."},
    "text-a-0107": {"href": "https://tools.ages.pucrs.br/easy-choose/easychooseapi", "source_anchor": "Repositório EasyChooseApi", "prefix": "Mais informações podem ser encontradas no repositório ", "anchor": "Easy Choose API", "suffix": "."},
    "text-a-0116": {"href": "https://tools.ages.pucrs.br/industria-digital/industria-digital-frontend", "source_anchor": "Repositório Indústria Digital Frontend", "prefix": "Mais informações podem ser encontradas no repositório ", "anchor": "Indústria Digital Frontend", "suffix": "."},
    "text-a-0117": {"href": "https://tools.ages.pucrs.br/industria-digital/industria-digital-backend", "source_anchor": "Repositório Indústria Digital Backend", "prefix": "Mais informações podem ser encontradas no repositório ", "anchor": "Indústria Digital Backend", "suffix": "."},
}
PRESENTATION_REPOSITORY_PARAGRAPHS = {
    "text-p-0304": "text-a-0105",
    "text-p-0307": "text-a-0106",
    "text-p-0310": "text-a-0107",
    "text-p-0775": "text-a-0116",
    "text-p-0778": "text-a-0117",
}
PRESENTATION_AUTHORIZATION_BY_UNIT = {
    **{uid: PRESENTATION_AUTHORIZATION for uid in REFERENCE_LAYOUT_UNITS},
    **{uid: AGES_II_PRESENTATION_AUTHORIZATION for uid in AGES_II_UNITS},
}
PRESENTATION_SERIALIZATIONS = {
    "abnt_figure_caption": set(PRESENTATION_CAPTIONS),
    "abnt_section_numbering": set(PRESENTATION_HEADINGS),
    "approved_figure_cross_reference": set(PRESENTATION_CROSS_REFERENCES),
    "repository_link_sentence": set(PRESENTATION_REPOSITORY_LINKS) | set(PRESENTATION_REPOSITORY_PARAGRAPHS),
}
PRESENTATION_OVERRIDES_BY_UNIT = {
    "chapter-02-text-h-0002": {"text-h-0002"},
    "chapter-02-text-h-0003": {"text-p-0290", "text-p-0293"},
    "chapter-02-text-h-0008": set(PRESENTATION_REPOSITORY_LINKS) | set(PRESENTATION_REPOSITORY_PARAGRAPHS),
    "chapter-02-text-h-0011": {"text-p-0325", "text-p-0328", "text-p-0356", "text-p-0372"},
    "chapter-02-text-h-0022": {"text-h-0022", "text-p-0642", "text-p-0650"},
}
PRESENTATION_OVERRIDES_BY_UNIT.update({
    "chapter-04-text-h-0039": {"text-h-0039"},
    "chapter-04-text-h-0040": {"text-p-0767"},
    "chapter-04-text-h-0042": {"text-p-0775", "text-p-0778", "text-a-0116", "text-a-0117"},
    "chapter-04-text-h-0044": {"text-p-0788"},
    "chapter-04-text-h-0045": {"text-p-0797", "text-p-0800", "text-p-0802", "text-p-0804"},
    "ages-ii-sprint-4": {"text-p-0962"},
    "chapter-04-text-h-0073": {"text-h-0073"},
})


def _load_presentation_authorization(repo: Path, unit_id: str | None = None) -> dict:
    if unit_id in AGES_II_UNITS:
        path = repo / AGES_II_PRESENTATION_AUTHORIZATION
        authorization = json.loads(path.read_text(encoding="utf-8"))
        changes = authorization.get("approved_presentation_changes")
        expected_caption_ids = {rid for rid in PRESENTATION_CAPTIONS if rid in {"text-p-0767", "text-p-0788", "text-p-0797", "text-p-0800", "text-p-0802", "text-p-0804", "text-p-0962"}}
        expected_caption_targets = {}
        manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
        records = _index(manifest.get("records", []))
        for rid in expected_caption_ids:
            old_prefix, new_prefix = PRESENTATION_CAPTIONS[rid]
            original = records.get(rid, {}).get("text")
            if not isinstance(original, str) or not original.startswith(old_prefix):
                raise ValueError("AGES II source caption differs from its audited Figure prefix")
            expected_caption_targets[rid] = new_prefix + original[len(old_prefix):]
        technology = {
            "source_list_ids": [f"text-list-0{number}" for number in range(109, 116)],
            "heading_numbering_wrapper_ids": ["text-list-0116", "text-list-0117"],
            "item_count": 7,
            "target_structure": "one continuous paragraph retaining all source text, original hyperlink anchors and order; add only the approved author-date citation apparatus for verified sources",
            "citation_keys": ["ages-ii-angular", "ages-ii-typescript", "ages-ii-python", "ages-ii-fastapi", "ages-ii-sqlalchemy", "ages-ii-postgresql"],
            "pending_sources": ["text-a-0126", "text-p-0839"],
        }
        expected_changes = {
            "figure_caption_labels": expected_caption_targets,
            "section_numbering": {rid: target for rid, (_, target) in PRESENTATION_HEADINGS.items() if rid in {"text-h-0039", "text-h-0073"}},
            "repository_links": {rid: PRESENTATION_REPOSITORY_LINKS[rid] for rid in ("text-a-0116", "text-a-0117")},
            "technology_paragraph": technology,
            "leading_tab_source_ids_by_unit": AGES_II_LEADING_TAB_COUNTS,
            "inline_tab_source_counts": AGES_II_INLINE_TAB_COUNTS,
            "leading_space_source_counts": AGES_II_LEADING_SPACE_COUNTS,
            "leading_line_break_source_counts": AGES_II_LEADING_LINE_BREAK_COUNTS,
        }
        edition_authorization = json.loads((repo / "migration/approvals/ages-ii-authorization.json").read_text(encoding="utf-8"))
        if (authorization.get("schema_version") != 1
                or authorization.get("kind") != "user_authorized_ages_ii_presentation_reuse"
                or authorization.get("status") != "authorized_for_execution_pending_human_review"
                or authorization.get("edition") != "ages-ii"
                or authorization.get("scope") != list(AGES_II_UNITS)
                or authorization.get("source") != {"path": "RELATORIO_ATUAL.odt", "sha256": edition_authorization.get("source_sha256")}
                or authorization.get("user_instruction") != "Gostaria de utilizar a mesma estrutura que a Mariah. Para as datas de acesso, vamos fazer o seguinte: Todos os projetos AGES I e AGES II tiveram data de acesso em 2024. Q3: utilize o ano de acesso como o ano de publicação, assim como a Mariah fez."
                or authorization.get("style_basis") != {
                    "accepted_decision": "migration/approvals/ages-i-presentation-accepted.json",
                    "style_guide": "docs/STYLE_GUIDE.md",
                    "approved_reference_pattern": "Mariah memorial, used only for presentation",
                    "content_from_reference_project_allowed": False,
                }
                or authorization.get("approved_presentation_changes") != expected_changes
                or authorization.get("technology_reference_convention") != {
                    "publication_year": 2024,
                    "access_date": "2024-10-15",
                    "provenance": "User-authorized assigned date within AGES II's August-November 2024 period; not browser history and not a verified publication date.",
                    "use_current_documentation_version_as_project_version": False,
                    "infer_missing_author": False,
                    "human_review_after_edition": True,
                }
                or authorization.get("human_approval_of_result") is not None
                or authorization.get("promoted_to_reusable_policy") is not False
                or authorization.get("future_editions_authorized") is not False
                or edition_authorization.get("authorized") is not True
                or edition_authorization.get("edition") != "ages-ii"
                or edition_authorization.get("source_sha256") != authorization.get("source", {}).get("sha256")):
            raise ValueError("AGES II presentation reuse evidence is missing, stale, or exceeds the authorized edition scope")
        return authorization

    path = repo / PRESENTATION_AUTHORIZATION
    authorization = json.loads(path.read_text(encoding="utf-8"))
    changes = authorization.get("approved_presentation_changes")
    if (authorization.get("schema_version") != 1
            or authorization.get("kind") != "user_presentation_correction_authorization"
            or authorization.get("status") != "authorized_for_execution_pending_human_review"
            or authorization.get("quoted_instruction") != PRESENTATION_USER_INSTRUCTION
            or authorization.get("scope") != "AGES I / Easy Choose only"
            or authorization.get("execution_authorized") is not True
            or authorization.get("human_approval") is not None
            or authorization.get("future_projects_approved") is not False
            or authorization.get("manual_pending") != ["Identifying the source/provenance of each of the five real images"]
            or not isinstance(changes, dict)
            or set(changes) != {"figure_caption_labels", "section_numbering", "figure_cross_references", "list_markers"}
            or changes.get("section_numbering") != {rid: new for rid, (_, new) in PRESENTATION_HEADINGS.items()}
            or changes.get("figure_cross_references") != PRESENTATION_CROSS_REFERENCES
            or changes.get("list_markers") != PRESENTATION_LIST_MARKERS
            or authorization.get("list_marker_instruction") != PRESENTATION_LIST_MARKER_INSTRUCTION
            or authorization.get("repository_links") != PRESENTATION_REPOSITORY_LINKS):
        raise ValueError("Presentation authorization is missing, stale, or exceeds the explicit AGES I scope")
    captions = changes.get("figure_caption_labels")
    if not isinstance(captions, dict) or set(captions) != set(PRESENTATION_CAPTIONS):
        raise ValueError("Caption localization authorization does not cover exactly the five AGES I captions")
    return authorization


def _verify_markerless_list(source_id, source, disposition, authorization):
    """Prove the one approved list keeps its five items and omits glyph markers."""
    rule = PRESENTATION_LIST_MARKERS.get(source_id)
    if not rule or authorization is None:
        raise ValueError("List marker change is outside the authorized source list")
    changes = authorization.get("approved_presentation_changes", {})
    if (authorization.get("list_marker_instruction") != PRESENTATION_LIST_MARKER_INSTRUCTION
            or changes.get("list_markers") != PRESENTATION_LIST_MARKERS
            or disposition.get("disposition") != "approved-markerless-list-preserving-items"
            or disposition.get("presentation_override") != {
                "authorization_evidence": PRESENTATION_AUTHORIZATION,
                "source_marker": "bullet",
                "target_marker": "none",
                "item_count": rule["item_count"],
            }
            or source.count(rule["tex_environment"]) != 1
            or len(re.findall(r"(?m)^\\item(?:\s|$)", source)) != rule["item_count"]):
        raise ValueError("Markerless list differs from the exact authorized five-item presentation")
    return True


TECHNOLOGY_PARAGRAPH_AUTHORIZATION = "migration/approvals/ages-i-technologies-paragraph.json"
TECHNOLOGY_PARAGRAPH_RECORDS = (
    {"source_id": "text-a-0111", "citation_key": "typescript-docs", "label": "TypeScript", "url": "https://www.typescriptlang.org/docs/", "date": "2024-04-10"},
    {"source_id": "text-a-0112", "citation_key": "react-docs", "label": "React", "url": "https://react.dev/", "date": "2024-04-10"},
    {"source_id": "text-a-0113", "citation_key": "nodejs-docs", "label": "Node.js", "url": "https://nodejs.org/docs/latest/api/", "date": "2024-04-10"},
    {"source_id": "text-a-0114", "citation_key": "prisma-docs", "label": "Prisma", "url": "https://www.prisma.io/docs", "date": "2024-04-10"},
    {"source_id": "text-a-0115", "citation_key": "postgresql-docs", "label": "PostgreSQL", "url": "https://www.postgresql.org/docs/", "date": "2024-04-10"},
)
AGES_II_TECHNOLOGY_REFERENCE_KEYS = {
    "text-a-0122": "ages-ii-angular",
    "text-a-0123": "ages-ii-typescript",
    "text-a-0124": "ages-ii-python",
    "text-a-0125": "ages-ii-fastapi",
    "text-a-0127": "ages-ii-sqlalchemy",
    "text-a-0128": "ages-ii-postgresql",
}
AGES_II_TECHNOLOGY_TEXT_IDS = (
    "text-p-0812", "text-p-0813", "text-p-0814", "text-p-0815",
    "text-p-0817", "text-p-0818", "text-p-0819", "text-p-0821",
    "text-p-0822", "text-p-0823", "text-p-0825", "text-p-0826",
    "text-p-0827", "text-p-0829", "text-p-0830", "text-p-0831",
    "text-p-0833", "text-p-0834", "text-p-0835", "text-p-0837",
    "text-p-0838", "text-p-0839", "text-p-0841",
)
AGES_II_TECHNOLOGY_CITATIONS_AFTER = {
    "text-p-0812": ["ages-ii-angular", "ages-ii-typescript"],
    "text-p-0817": ["ages-ii-python"],
    "text-p-0821": ["ages-ii-fastapi"],
    "text-p-0829": ["ages-ii-sqlalchemy"],
    "text-p-0833": ["ages-ii-postgresql"],
}


def _verify_technology_paragraph(source, bibliography, disposition, authorization):
    """Verify the narrowly authorized AGES I technology paragraph and citations."""
    if (disposition.get("source_id") != "text-list-0025"
            or disposition.get("disposition") != "approved-single-paragraph-technology-list"
            or disposition.get("presentation_override") != {
                "authorization_evidence": TECHNOLOGY_PARAGRAPH_AUTHORIZATION,
                "source_marker": "bullet list",
                "target_structure": "one continuous prose paragraph",
                "item_count": 5,
            }):
        raise ValueError("Technology-list disposition differs from the exact AGES I paragraph approval")
    expected_authorization = {
        "schema_version": 1,
        "kind": "user_authorized_technology_presentation_and_citation",
        "status": "authorized_for_execution_pending_human_review",
        "scope": "AGES I / Easy Choose / subseção Tecnologias utilizadas / text-h-0012",
        "source_sha256": "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef",
        "promoted_to_reusable_policy": False,
        "human_approval_of_result": None,
    }
    if any(authorization.get(key) != value for key, value in expected_authorization.items()):
        raise ValueError("Technology-paragraph authorization is missing, stale, or outside the reviewed AGES I scope")
    if authorization.get("assigned_references") != [
        {
            "source_id": item["source_id"], "citation_key": item["citation_key"],
            "citation_author_label": item["label"], "year": 2024,
            "access_date": item["date"], "url": item["url"],
        }
        for item in TECHNOLOGY_PARAGRAPH_RECORDS
    ]:
        raise ValueError("Assigned citation/access-date records differ from the authorized five technology links")
    if authorization.get("user_decisions", {}).get("author_date_year") != "Use the access year as the publication/citation year, following Mariah's pattern.":
        raise ValueError("Author-date year convention differs from the user's explicit decision")

    marker = r"\label{ages-i:text-h-0012}"
    if marker not in source:
        raise ValueError("Technology subsection label is missing")
    body = source.split(marker, 1)[1]
    if body.count(r"\par") != 1 or not body.rstrip().endswith(r"\par"):
        raise ValueError("All technology text must form exactly one paragraph")
    if re.search(r"\\(?:begin\s*\{(?:itemize|enumerate)\}|item\b)", body):
        raise ValueError("The technology list still has visible list structure")

    citation_tokens = [token.args[0] for token in commands(body) if token.name == "cite" and token.args]
    if citation_tokens != [item["citation_key"] for item in TECHNOLOGY_PARAGRAPH_RECORDS]:
        raise ValueError("The five author-date citations are missing, duplicated, or out of order")
    for item in TECHNOLOGY_PARAGRAPH_RECORDS:
        expected_prefix = f'{item["label"]}:\\space\\cite{{{item["citation_key"]}}}'
        if expected_prefix not in body:
            raise ValueError(f"The {item['label']} citation is detached from its technology label")
    hrefs = [token.args for token in commands(body) if token.name == "href" and len(token.args) == 2]
    expected_hrefs = [
        (item["url"], f"Documentação {item['label']}")
        for item in TECHNOLOGY_PARAGRAPH_RECORDS
    ]
    if hrefs != expected_hrefs:
        raise ValueError("The five original documentation URLs/anchors must remain in source order")
    href_tokens = [token for token in commands(body) if token.name == "href" and len(token.args) == 2]
    separators = [body[token.end:token.end + 1] for token in href_tokens]
    if separators != [";", ";", ";", ";", "."]:
        raise ValueError("Technology group separators must be the four approved semicolons and final period")

    for item in TECHNOLOGY_PARAGRAPH_RECORDS:
        match = re.search(
            rf"(?ms)^@online\{{{re.escape(item['citation_key'])},(?P<entry>.*?)^\}}",
            bibliography,
        )
        if not match:
            raise ValueError(f"Bibliography entry {item['citation_key']} is missing")
        entry = match["entry"]
        fields = {
            "author": "{{" + item["label"] + "}}",
            "year": "{2024}",
            "urldate": "{" + item["date"] + "}",
            "url": "{" + item["url"] + "}",
        }
        for field, value in fields.items():
            if not re.search(rf"(?m)^\s*{field}\s*=\s*{re.escape(value)}\s*,?\s*$", entry):
                raise ValueError(f"Bibliography field {field} for {item['citation_key']} differs from its approval")
    return True


def _verify_ages_ii_technology_paragraph(source, bibliography, disposition, authorization, unit_ledger, unit, records, reference_evidence):
    """Verify AGES II's one-paragraph technology presentation from source-linked evidence."""
    auth_path = AGES_II_PRESENTATION_AUTHORIZATION
    technology_rule = authorization.get("approved_presentation_changes", {}).get("technology_paragraph")
    expected_lists = [f"text-list-0{number}" for number in range(109, 116)]
    if (disposition.get("source_id") != "text-list-0109"
            or disposition.get("disposition") != "approved-single-paragraph-technology-list"
            or disposition.get("presentation_override") != {
                "authorization_evidence": auth_path,
                "source_list_ids": expected_lists,
                "target_structure": "one continuous paragraph retaining source text, links and order",
                "item_count": 7,
            }
            or technology_rule is None
            or technology_rule.get("source_list_ids") != expected_lists
            or technology_rule.get("item_count") != 7):
        raise ValueError("Technology-list disposition differs from the exact AGES II presentation authorization")

    source_lists = [
        rid for rid in unit.get("record_ids", [])
        if rid in records and records[rid].get("type") == "text:list"
        and records[rid].get("parent_id") == "office-text-0001"
    ]
    heading_wrappers = technology_rule.get("heading_numbering_wrapper_ids")
    if source_lists != expected_lists + ["text-list-0116"] or heading_wrappers != ["text-list-0116", "text-list-0117"]:
        raise ValueError("The seven source technology lists differ from the frozen manifest scope")
    for list_id in heading_wrappers:
        if list_id not in unit.get("record_ids", []) or records.get(list_id, {}).get("type") != "text:list":
            raise ValueError("An expected ODF heading-numbering wrapper is absent")
        visible_descendants = [
            item for item in records.values()
            if list_id in item.get("context_ids", []) and isinstance(item.get("text"), str) and item["text"].strip()
        ]
        if [item.get("id") for item in visible_descendants] != ["text-h-0047"] or visible_descendants[0].get("unit_id") != "chapter-04-text-h-0047":
            raise ValueError(f"Heading-numbering wrapper {list_id} contains unexpected visible source text")

    element_map = unit_ledger.get("element_map", [])
    mappings = {item.get("source_id"): item for item in element_map}
    if any(rid not in mappings for rid in AGES_II_TECHNOLOGY_TEXT_IDS):
        raise ValueError("A source paragraph in the technology presentation is not mapped")
    expected_text_order = [rid for rid in unit.get("source_record_ids", []) if rid in AGES_II_TECHNOLOGY_TEXT_IDS]
    if expected_text_order != list(AGES_II_TECHNOLOGY_TEXT_IDS):
        raise ValueError("The source technology paragraphs differ from the audited source order")
    tex_path = unit_ledger.get("tex_path")
    if any(mappings[rid].get("target_file") != tex_path for rid in AGES_II_TECHNOLOGY_TEXT_IDS):
        raise ValueError("The approved technology paragraph must stay in its assigned unit file")
    first = mappings[AGES_II_TECHNOLOGY_TEXT_IDS[0]]
    last = mappings[AGES_II_TECHNOLOGY_TEXT_IDS[-1]]
    if (type(first.get("start_byte")) is not int or type(last.get("end_byte")) is not int
            or first["start_byte"] > last["end_byte"] or last["end_byte"] > len(source.encode("utf-8"))):
        raise ValueError("Technology paragraph byte interval is invalid")
    tail = source.encode("utf-8")[first["start_byte"]:].decode("utf-8")
    paragraph_end = next((token for token in commands(tail) if token.name == "par"), None)
    paragraph_end_byte = len(tail[:paragraph_end.start].encode("utf-8")) if paragraph_end is not None else None
    if paragraph_end is None or last["end_byte"] - first["start_byte"] > paragraph_end_byte:
        raise ValueError("All seven technology entries and the closing integration paragraph must form one paragraph")
    raw = tail[:paragraph_end.end]
    if sum(token.name == "par" for token in commands(raw)) != 1:
        raise ValueError("Technology content contains an additional paragraph break")
    if any(token.name == "item" or token.name in {"begin", "end"} and token.args and token.args[0] in {"itemize", "enumerate"} for token in commands(raw)):
        raise ValueError("The approved technology paragraph still contains list structure")

    citation_keys = [token.args[0] for token in commands(raw) if token.name == "cite" and token.args]
    expected_citation_keys = list(AGES_II_TECHNOLOGY_REFERENCE_KEYS.values())
    if citation_keys != expected_citation_keys:
        raise ValueError("The six verified technology citations are missing, duplicated, or out of order")
    for source_id, keys in AGES_II_TECHNOLOGY_CITATIONS_AFTER.items():
        mapping = mappings[source_id]
        relative_end = mapping["end_byte"] - first["start_byte"]
        suffix = raw.encode("utf-8")[relative_end:].decode("utf-8")
        source_text = records.get(source_id, {}).get("text", "")
        citation_gap = "" if source_text.endswith((" ", "\t")) else r"\space"
        expected = "".join(citation_gap + r"\cite{" + key + "}" for key in keys)
        if not suffix.startswith(expected):
            raise ValueError(f"Citation spacing or attachment differs from the exact source-ending whitespace for {source_id}")

    curated = {item.get("source_record_id"): item for item in reference_evidence.get("references", [])}
    assigned_date = authorization.get("technology_reference_convention", {}).get("access_date")
    assigned_year = authorization.get("technology_reference_convention", {}).get("publication_year")
    for source_id, key in AGES_II_TECHNOLOGY_REFERENCE_KEYS.items():
        evidence = curated.get(source_id)
        if (not evidence or evidence.get("metadata", {}).get("status") != "VERIFIED"
                or evidence.get("metadata", {}).get("author") is not None
                or evidence.get("metadata", {}).get("title") is None
                or evidence.get("original_url") != records[source_id].get("href")
                or evidence.get("original_anchor") != records[source_id].get("source_text")):
            raise ValueError(f"Curator evidence does not verify title, original URL and anchor for {source_id}")
        match = re.search(rf"(?ms)^@online\{{{re.escape(key)},(?P<entry>.*?)^\}}", bibliography)
        if not match:
            raise ValueError(f"Bibliography entry {key} is missing")
        entry = match["entry"]
        fields = {
            "title": "{" + evidence["metadata"]["title"] + "}",
            "url": "{" + evidence["original_url"] + "}",
            "year": "{" + str(assigned_year) + "}",
            "urldate": "{" + assigned_date + "}",
        }
        for field, value in fields.items():
            if not re.search(rf"(?m)^\s*{field}\s*=\s*{re.escape(value)}\s*,?\s*$", entry):
                raise ValueError(f"Bibliography field {field} for {key} differs from verified/assigned metadata")
        if re.search(r"(?mi)^\s*(?:author|editor|organization|institution)\s*=", entry):
            raise ValueError(f"Bibliography entry {key} asserts authorship not established by the curator")

    pending = curated.get("text-a-0126", {})
    if pending.get("status") != "PENDING" or pending.get("original_url") != records["text-a-0126"].get("href"):
        raise ValueError("Graph API reference must remain pending with the exact original URL")
    if re.search(r"(?mi)^@\w+\{ages-ii-(?:graph-api|docker)\s*,", bibliography):
        raise ValueError("Pending/unlinked sources must not receive inferred bibliography entries")
    expected_links = [
        (item["original_url"], item["original_anchor"])
        for item in reference_evidence.get("references", [])
        if item.get("source_record_id") in set(AGES_II_TECHNOLOGY_REFERENCE_KEYS) | {"text-a-0126"}
    ]
    observed_links = [(token.args[0], displayed_text(token.args[1])) for token in commands(raw) if token.name == "href" and len(token.args) == 2]
    if observed_links != expected_links:
        raise ValueError("Original technology documentation URLs/anchors differ from verified source order")

    return True


def _reference_suffix(value: str) -> str:
    value = value.replace(r"\nobreakspace{}", " ")
    value = value.replace(r"\hspace{0.6em}", " ")
    value = re.sub(
        r"\\hyperref\[([A-Za-z0-9:_-]+)\]\{\\ref\*\{([A-Za-z0-9:_-]+)\}\}",
        lambda match: f"⟪ref:{match[1]}⟫" if match[1] == match[2] else match[0],
        value,
    )
    value = re.sub(r"\\ref\{([A-Za-z0-9:_-]+)\}", r"⟪ref:\1⟫", value)
    return value.replace("~", " ")


def _project_approved_presentation(source_id, expected, observed, serializations, authorization):
    used = set(serializations) & set(PRESENTATION_SERIALIZATIONS)
    if not used:
        return observed, None
    if authorization is None:
        raise UnsupportedSerialization("Presentation override requires the explicit current user authorization")
    for kind in used:
        if source_id not in PRESENTATION_SERIALIZATIONS[kind]:
            raise UnsupportedSerialization(f"{kind} is not authorized for {source_id}")
    if "abnt_figure_caption" in used:
        old_prefix, new_prefix = PRESENTATION_CAPTIONS[source_id]
        if not expected.startswith(old_prefix):
            raise UnsupportedSerialization("Source caption no longer matches the audited Figure label")
        target = authorization["approved_presentation_changes"]["figure_caption_labels"][source_id]
        expected_target = new_prefix + expected[len(old_prefix):]
        if target != expected_target or observed != expected_target:
            raise UnsupportedSerialization("Figure caption changes exceed the authorized Portuguese label and ABNT dash")
        return expected, {"source_id": source_id, "kind": "abnt_figure_caption_label", "source": expected, "displayed": expected_target}
    if "abnt_section_numbering" in used:
        source, target = PRESENTATION_HEADINGS[source_id]
        if expected != source or authorization["approved_presentation_changes"]["section_numbering"][source_id] != target or observed != target:
            raise UnsupportedSerialization("Section indicator differs from the narrowly authorized ABNT punctuation adjustment")
        return expected, {"source_id": source_id, "kind": "abnt_section_numbering", "source": source, "displayed": target}
    if "repository_link_sentence" in used:
        link_id = PRESENTATION_REPOSITORY_PARAGRAPHS.get(source_id, source_id)
        rule = PRESENTATION_REPOSITORY_LINKS.get(link_id)
        if rule is None or expected != rule["source_anchor"]:
            raise UnsupportedSerialization("Repository prose is not attached to an original authorized anchor")
        target = rule["prefix"] + rule["anchor"] + rule["suffix"]
        if observed != target:
            raise UnsupportedSerialization("Repository prose or visible anchor differs from the exact user-approved sentence")
        return expected, {"source_id": source_id, "kind": "repository_link_in_prose", "source": expected, "displayed": target, "href": rule["href"]}
    if "approved_figure_cross_reference" in used:
        rule = PRESENTATION_CROSS_REFERENCES[source_id]
        policy = authorization["approved_presentation_changes"]["figure_cross_references"][source_id]
        if rule != policy:
            raise UnsupportedSerialization("Figure cross-reference differs from the authorized structural wording")
        if "suffix" in rule:
            expected_target = expected + _reference_suffix(rule["suffix"])
        else:
            replacement = rule["replace_suffix"]
            if not expected.endswith(replacement["from"]):
                raise UnsupportedSerialization("Source paragraph punctuation differs from the authorized figure callout")
            expected_target = expected[:-len(replacement["from"])] + _reference_suffix(replacement["to"])
        if observed != expected_target:
            raise UnsupportedSerialization("Figure callout is missing, altered, or contains unapproved words")
        return expected, {"source_id": source_id, "kind": "figure_cross_reference", "source": expected, "displayed": expected_target}
    raise UnsupportedSerialization("Unrecognized presentation transformation")

DIAGRAM_PLACEHOLDER_BODY = r"\par\noindent\fbox{\parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule\relax}{\textbf{Diagrama ausente — placeholder provisório}\par Identificador: #1\par Pendência: #2}}\par"


class UnsupportedSerialization(ValueError):
    pass


@dataclass(frozen=True)
class _ExplicitWhitespace:
    value: str
    inline_layout: bool = False
    leading_layout: bool = False


def displayed_text(source: str, serializations=(), *, macro_contract_verified=False, inline_layout_verified=False, reference_layout_verified=False) -> str:
    """Decode a conservative token projection; markers cannot be text-injected."""
    tokens = _display_tokens(source, serializations, macro_contract_verified, inline_layout_verified, reference_layout_verified)
    blocks = []
    for token in tokens:
        if isinstance(token, str) and blocks and isinstance(blocks[-1], str):
            blocks[-1] += token
        else:
            blocks.append(token)
    pieces = []
    for index, block in enumerate(blocks):
        if isinstance(block, _ExplicitWhitespace):
            pieces.append(block.value)
            continue
        folded = re.sub(r"[\t\n\r\f\v ]+", " ", block)
        if index == 0:
            folded = folded.lstrip(" ")
        if index == len(blocks) - 1:
            folded = folded.rstrip(" ")
        pieces.append(folded)
    result = "".join(pieces)
    if ("``" in result or "''" in result) and "tex_quotes" not in serializations:
        raise UnsupportedSerialization("TeX quote ligature needs explicit tex_quotes policy")
    if "--" in result and "tex_dashes" not in serializations:
        raise UnsupportedSerialization("TeX dash ligature needs explicit tex_dashes policy")
    if "tex_quotes" in serializations:
        result = result.replace("``", "“").replace("''", "”")
    if "tex_dashes" in serializations:
        result = result.replace("---", "—").replace("--", "–")
    if "canonical_unicode" in serializations:
        result = unicodedata.normalize("NFC", result)
    return result


def _display_tokens(source: str, serializations, macro_contract_verified, inline_layout_verified=False, reference_layout_verified=False) -> list:
    """Decode only syntax with a known, local displayed-text equivalent.

    Ordinary TeX code folding collapses to one visible space. Explicit source
    tabs, line breaks, repeated or edge spaces are rejected by the audit rather
    than normalized. Explicit target line breaks/tabs are also unsupported.
    Accents, punctuation, case, numbers and symbols compare exactly.
    No macro expansion, citation expansion or counter-generated text is guessed.
    """
    allowed = {"tex_quotes", "tex_dashes", "canonical_unicode", "original_whitespace", "inline_tab_layout", "reference_paragraph_layout", "abnt_figure_caption", "abnt_section_numbering", "approved_figure_cross_reference", "repository_link_sentence"}
    if set(serializations) - allowed:
        raise UnsupportedSerialization("Unrecognized serialization policy")
    if "original_whitespace" in serializations and not macro_contract_verified:
        raise UnsupportedSerialization("original_whitespace requires a verified macro contract")
    if "inline_tab_layout" in serializations and (not inline_layout_verified or "original_whitespace" not in serializations):
        raise UnsupportedSerialization("inline_tab_layout requires authorized source scope and original_whitespace")
    if "reference_paragraph_layout" in serializations and not reference_layout_verified:
        raise UnsupportedSerialization("reference_paragraph_layout requires verified explicit user authorization")
    masked = strip_comments(source)
    # A TeX comment suppresses its newline, rather than inserting a space.
    # Keep the offset-preserving lexer separate from this displayed projection.
    pieces, start, cursor = [], 0, 0
    while cursor < len(source):
        if source[cursor] == "%" and masked[cursor] == " ":
            pieces.append(source[start:cursor])
            newline = source.find("\n", cursor)
            cursor = len(source) if newline < 0 else newline + 1
            start = cursor
        else:
            cursor += 1
    pieces.append(source[start:])
    text = "".join(pieces)
    if re.search(r"\n[\t\r ]*\n", text):
        raise UnsupportedSerialization("Blank TeX line creates a paragraph break inside one source record")
    output, i = [], 0
    escapes = {"%": "%", "_": "_", "#": "#", "$": "$", "&": "&", "{": "{", "}": "}", " ": " "}
    wrappers = {"textbf", "textit", "emph", "texttt", "textrm", "textsf", "textnormal", "underline", "mbox"}
    symbols = {"textbackslash": "\\", "textasciitilde": "~", "textasciicircum": "^", "textless": "<", "textgreater": ">"}
    while i < len(text):
        char = text[i]
        if char == "\\":
            match = re.match(r"\\([A-Za-z@]+|.)", text[i:])
            if not match:
                raise UnsupportedSerialization("Dangling backslash")
            name = match[1]
            i += match.end()
            if name in escapes:
                output.append(escapes[name])
                continue
            while i < len(text) and text[i].isspace():
                i += 1
            if name in {"originaltab", "originalspace", "originalinlinetab", "originalleadingspace", "originalleadbreak"}:
                if "original_whitespace" not in serializations or not macro_contract_verified:
                    raise UnsupportedSerialization("Explicit whitespace macro requires verified original_whitespace policy")
                if text[i:i + 2] != "{}":
                    raise UnsupportedSerialization("Whitespace macro must have an explicit empty group")
                i += 2
                if name == "originalinlinetab" and ("inline_tab_layout" not in serializations or not inline_layout_verified):
                    raise UnsupportedSerialization("Inline tab layout requires verified explicit authorization")
                if name == "originalleadingspace" and ("reference_paragraph_layout" not in serializations or not reference_layout_verified):
                    raise UnsupportedSerialization("Leading space metadata requires authorized paragraph layout")
                if name == "originalleadbreak" and ("reference_paragraph_layout" not in serializations or not reference_layout_verified):
                    raise UnsupportedSerialization("Leading line-break metadata requires authorized paragraph layout")
                whitespace_value = "\n" if name == "originalleadbreak" else " " if name in {"originalspace", "originalleadingspace"} else "\t"
                output.append(_ExplicitWhitespace(whitespace_value, name == "originalinlinetab", name in {"originalleadingspace", "originalleadbreak"}))
                continue
            if name in symbols:
                output.append(symbols[name])
                if text[i:i + 2] == "{}":
                    i += 2
                continue
            if name == "space":
                if "original_whitespace" not in serializations or not macro_contract_verified:
                    raise UnsupportedSerialization("TeX space requires verified original_whitespace policy")
                output.append(_ExplicitWhitespace(" "))
                continue
            if name == "nobreakspace":
                if "approved_figure_cross_reference" not in serializations:
                    raise UnsupportedSerialization("A nonbreaking reference space requires its exact approved figure-callout mapping")
                if text[i:i + 2] != "{}":
                    raise UnsupportedSerialization("nobreakspace must use an explicit empty group")
                output.append(" ")
                i += 2
                continue
            if name == "hspace":
                if "approved_figure_cross_reference" not in serializations:
                    raise UnsupportedSerialization("A fixed reference gap requires its exact approved figure-callout mapping")
                if i >= len(text) or text[i] != "{":
                    raise UnsupportedSerialization("Missing argument of hspace")
                dimension, i = _group(text, i, "{", "}")
                if dimension != "0.6em":
                    raise UnsupportedSerialization("Only the approved figure-reference gap is supported")
                output.append(" ")
                continue
            if name in {"newline", "linebreak", "\\"}:
                raise UnsupportedSerialization("Explicit target line break requires rendered/source whitespace review")
            if name == "ref":
                if "approved_figure_cross_reference" not in serializations:
                    raise UnsupportedSerialization("A generated reference requires its exact authorized figure-callout mapping")
                if i >= len(text) or text[i] != "{":
                    raise UnsupportedSerialization("Missing argument of ref")
                label, i = _group(text, i, "{", "}")
                if not re.fullmatch(r"[A-Za-z0-9:_-]+", label):
                    raise UnsupportedSerialization("Unsupported reference label")
                output.append(f"⟪ref:{label}⟫")
                continue
            if name == "hyperref":
                if "approved_figure_cross_reference" not in serializations:
                    raise UnsupportedSerialization("A linked starred reference requires its exact approved figure-callout mapping")
                if i >= len(text) or text[i] != "[":
                    raise UnsupportedSerialization("Missing destination of hyperref")
                destination, i = _group(text, i, "[", "]")
                if i >= len(text) or text[i] != "{":
                    raise UnsupportedSerialization("Missing text of hyperref")
                linked_text, i = _group(text, i, "{", "}")
                match = re.fullmatch(r"\\ref\*\{([A-Za-z0-9:_-]+)\}", linked_text)
                if not match or match[1] != destination:
                    raise UnsupportedSerialization("Only a live, matching starred figure reference may be linked")
                output.append(f"⟪ref:{destination}⟫")
                continue
            if name in wrappers | {"href", "url"}:
                if i >= len(text) or text[i] != "{":
                    raise UnsupportedSerialization(f"Missing argument of {name}")
                first, i = _group(text, i, "{", "}")
                if name == "url":
                    literal_url = _url(first)
                    if "\\" in literal_url:
                        raise UnsupportedSerialization("Unknown URL serialization")
                    output.append(literal_url)
                    continue
                if name == "href":
                    while i < len(text) and text[i].isspace():
                        i += 1
                    if i >= len(text) or text[i] != "{":
                        raise UnsupportedSerialization("Missing href anchor")
                    first, i = _group(text, i, "{", "}")
                output.extend(_display_tokens(first, serializations, macro_contract_verified, inline_layout_verified, reference_layout_verified))
                continue
            raise UnsupportedSerialization(f"Unsupported command \\{name}; rendered equivalence is unproven")
        if char == "{":
            group, i = _group(text, i, "{", "}")
            output.extend(_display_tokens(group, serializations, macro_contract_verified, inline_layout_verified, reference_layout_verified))
            continue
        if char == "}" or char in "$&#_^":
            raise UnsupportedSerialization(f"Unescaped special character {char!r}")
        if char == "~":
            output.append(" ")
        else:
            output.append(char)
        i += 1
    return output


def _space(text: str) -> str:
    # Target code folding only. Never use this function on source text.
    return re.sub(r"[\t\n\r\f\v ]+", " ", text).strip(" ")


def _strict_source(text: str, original_whitespace=False, allowed_leading_line_breaks=0) -> str:
    """No source whitespace is silently discarded or collapsed.

    XML extraction already distinguishes text:s, text:tab and text:line-break.
    Without a rendered layout proof, these cannot be declared equivalent to an
    ordinary TeX space, even if the converter copies the same raw characters.
    """
    if allowed_leading_line_breaks:
        leading_line_breaks = len(text) - len(text.lstrip("\n"))
        if leading_line_breaks != allowed_leading_line_breaks:
            raise UnsupportedSerialization("Source line breaks differ from the exact authorized leading count")
        text_without_authorized_breaks = text[leading_line_breaks:]
    else:
        text_without_authorized_breaks = text
    if any(char in text_without_authorized_breaks for char in "\n\r\f\v") or "\t" in text and not original_whitespace:
        raise UnsupportedSerialization("Explicit source tab/line break requires rendered whitespace review")
    if not original_whitespace and ("  " in text or text.startswith(" ") or text.endswith(" ")):
        raise UnsupportedSerialization("Repeated or edge source spaces require rendered whitespace review")
    return text


def _source_whitespace_verified(serializations, macro_contract_verified, reference_layout_verified=False):
    return macro_contract_verified and (
        "original_whitespace" in serializations
        or ("reference_paragraph_layout" in serializations and reference_layout_verified)
    )


def _index(records):
    if isinstance(records, dict):
        return records
    return {record["id"]: record for record in records}


def _kind(record):
    return str(record.get("type", "")).split("}")[-1].split(":")[-1]


def _is_source_heading(record):
    return _kind(record) == "h" and record.get("semantic_type", "heading") == "heading"


def _leading_tab_paragraph_ids(source_ids, records):
    return [
        rid for rid in source_ids
        if rid in records
        and _kind(records[rid]) == "p"
        and isinstance(records[rid].get("text"), str)
        and records[rid]["text"].startswith("\t")
    ]


def _project_source_text_order(unit_id, source_ids, records):
    """Project the audited AGES II Sprint 4 text-box flow onto text records.

    In the ODF source, the caption text is nested in a draw frame embedded at
    the start of text-p-0961, before that paragraph's visible text. The flat
    source_record_ids list records the parent paragraph first, so this exact,
    structure-checked projection corrects only that ordering comparison.
    """
    if unit_id != "ages-ii-sprint-4":
        return list(source_ids), None

    parent_id = "text-p-0961"
    frame_id = "draw-frame-0039"
    textbox_id = "draw-text-box-0025"
    nested_text_id = "text-p-0962"
    positions = {rid: index for index, rid in enumerate(source_ids)}
    parent = records.get(parent_id, {})
    frame = records.get(frame_id, {})
    textbox = records.get(textbox_id, {})
    nested_text = records.get(nested_text_id, {})
    segments = parent.get("inline_segments")
    structure_matches = (
        source_ids.count(parent_id) == 1
        and source_ids.count(nested_text_id) == 1
        and positions.get(nested_text_id) == positions.get(parent_id, -2) + 1
        and isinstance(segments, list)
        and bool(segments)
        and segments[0] == {"kind": "embedded-block", "record_id": frame_id}
        and not any(segment.get("kind") == "embedded-block" for segment in segments[1:])
        and any(segment.get("kind") == "text" and segment.get("text") for segment in segments[1:])
        and frame.get("parent_id") == parent_id
        and textbox.get("parent_id") == frame_id
        and nested_text.get("parent_id") == textbox_id
    )
    if not structure_matches:
        return list(source_ids), "Sprint 4 embedded-caption order no longer matches its audited ODF IDs and inline segments"

    projected = list(source_ids)
    parent_position = positions[parent_id]
    projected[parent_position], projected[parent_position + 1] = nested_text_id, parent_id
    return projected, None


def _url(raw: str) -> str:
    # No percent-unquoting, URL case changes, redirect resolution or trailing-slash normalization.
    return re.sub(r"\\([%_#$&{}])", r"\1", raw)


def _valid_url(value: str) -> bool:
    if not value or re.search(r"[\s\x00-\x1f]", value) or re.search(r"%(?![0-9a-fA-F]{2})", value):
        return False
    try:
        parsed = urlsplit(value)
        if parsed.scheme in {"http", "https"}:
            _ = parsed.port  # Force validation, including invalid/out-of-range ports.
            return bool(parsed.hostname)
        return value.startswith("#") or parsed.scheme == "mailto" and bool(parsed.path)
    except ValueError:
        return False


def audit_conversion(manifest: dict, ledger: dict, repo: Path, unit_id: str | None = None) -> dict:
    repo = repo.resolve()
    findings, differences, facts = [], {}, {"scope": unit_id or "all", "proof": "actual UTF-8 bytes and conservative lexical projection; not TeX execution", "text_records_checked": 0, "text_records_matched": 0, "inline_tab_layout_records_matched": 0, "reference_paragraph_layout_records_matched": 0, "links_checked": 0, "images_checked": 0, "converted_units": 0, "source_text_records": 0, "coverage_percent": 0.0, "approved_presentation_transformations": []}

    def report(code, uid, message, source_id=None, path=None, severity="error"):
        findings.append({"severity": severity, "code": code, "unit_id": uid, "source_id": source_id, "path": path, "message": message})

    if ledger.get("schema_version") != 1:
        report("ledger_schema", None, "Expected ledger schema_version 1")
        return {"status": "blocked", "findings": findings, "facts": facts, "differences": differences}
    records = _index(manifest.get("records", []))
    units = _index(manifest.get("units", []))
    assets = _index(manifest.get("assets", []))
    ledger_units = ledger.get("units", {})
    if unit_id is not None and unit_id not in units:
        report("unknown_unit", unit_id, "Unit does not exist in source manifest")
        return {"status": "blocked", "findings": findings, "facts": facts, "differences": differences}
    selected = [unit_id] if unit_id else list(units)

    def safe_path(raw):
        if not isinstance(raw, str) or Path(raw).is_absolute():
            raise ValueError("Target path must be repository-relative")
        path = (repo / raw).resolve()
        if not path.is_relative_to(repo):
            raise ValueError("Target path escapes repository")
        return path

    try:
        compilation_root = safe_path(ledger.get("compilation_root", "."))
    except ValueError as exc:
        report("unsafe_compilation_root", None, str(exc))
        return {"status": "blocked", "findings": findings, "facts": facts, "differences": differences}
    target_cache = {}
    presentation_authorization = None
    presentation_authorization_error = None

    def fragment(mapping):
        path = safe_path(mapping.get("target_file"))
        if path not in target_cache:
            data = path.read_bytes()
            target_cache[path] = (data, hashlib.sha256(data).hexdigest())
        data, digest = target_cache[path]
        if mapping.get("target_sha256") != digest:
            raise ValueError("Missing or stale target_sha256; actual file does not match mapping")
        start, end = mapping.get("start_byte"), mapping.get("end_byte")
        if type(start) is not int or type(end) is not int or not 0 <= start <= end <= len(data):
            raise ValueError("Invalid half-open byte interval")
        data[:start].decode("utf-8")  # Reject offsets inside a UTF-8 code point.
        return path, start, end, data[start:end].decode("utf-8")

    figure_labels = set()
    for uid in selected:
        try:
            presentation_authorization = _load_presentation_authorization(repo, uid)
            presentation_authorization_error = None
        except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
            presentation_authorization = None
            presentation_authorization_error = str(exc)
        unit = units[uid]
        state = ledger_units.get(uid, {}).get("state", "unconverted")
        unit_ledger = ledger_units.get(uid, {})
        technology_paragraph_verified = False
        differences[uid] = []
        source_ids = unit.get("source_record_ids")
        if source_ids is None:
            source_ids = [rid for rid in unit.get("record_ids", []) if rid in records and _kind(records[rid]) in {"p", "h"} and records[rid].get("text") is not None]
        source_ids = [rid for rid in source_ids if rid in records and records[rid].get("text") is not None]
        facts["source_text_records"] += len(source_ids)
        if state == "unconverted":
            report("unit_unconverted", uid, "No conversion claimed; preservation has not been demonstrated", severity="warning")
            continue
        if state != "converted":
            report("invalid_unit_state", uid, f"Unknown state {state!r}")
            continue
        facts["converted_units"] += 1
        mappings = unit_ledger.get("element_map", [])
        if uid in {"chapter-02-text-h-0012", "chapter-04-text-h-0046"}:
            try:
                source_path = safe_path(unit_ledger.get("tex_path"))
                source_text = source_path.read_text(encoding="utf-8")
                technology_list_id = "text-list-0025" if uid == "chapter-02-text-h-0012" else "text-list-0109"
                disposition = next(
                    item for item in unit_ledger.get("structural_dispositions", [])
                    if item.get("source_id") == technology_list_id
                )
                if disposition.get("disposition") == "approved-single-paragraph-technology-list":
                    bibliography = safe_path("relatorio_AGES_eduardo/bibliografia/bibliografia.bib").read_text(encoding="utf-8")
                    if uid == "chapter-02-text-h-0012":
                        technology_approval = json.loads(safe_path(TECHNOLOGY_PARAGRAPH_AUTHORIZATION).read_text(encoding="utf-8"))
                        _verify_technology_paragraph(source_text, bibliography, disposition, technology_approval)
                    else:
                        if presentation_authorization is None:
                            raise ValueError(presentation_authorization_error or "Missing AGES II presentation authorization")
                        reference_evidence = json.loads(safe_path("migration/evidence/references/ages-ii.json").read_text(encoding="utf-8"))
                        _verify_ages_ii_technology_paragraph(
                            source_text, bibliography, disposition, presentation_authorization,
                            unit_ledger, unit, records, reference_evidence,
                        )
                    technology_paragraph_verified = True
                    if uid == "chapter-02-text-h-0012":
                        facts["approved_presentation_transformations"].append({
                            "source_id": "text-list-0025",
                            "kind": "single_paragraph_with_author_date_citations",
                            "citation_keys": [item["citation_key"] for item in TECHNOLOGY_PARAGRAPH_RECORDS],
                            "access_dates_assigned_under_user_instruction": [item["date"] for item in TECHNOLOGY_PARAGRAPH_RECORDS],
                        })
                        report("approved_technology_paragraph_review_required", uid, "The five source technology entries form one paragraph; labels, descriptions, original documentation links and ordered author-date citations are verified. Assigned 2024 dates remain user-directed metadata, and human review is pending", source_id="text-list-0025", severity="warning")
                    else:
                        facts["approved_presentation_transformations"].append({
                            "source_id": "text-list-0109",
                            "kind": "single_paragraph_with_verified_author_date_citations",
                            "source_lists": [f"text-list-0{number}" for number in range(109, 116)],
                            "citation_keys": list(AGES_II_TECHNOLOGY_REFERENCE_KEYS.values()),
                            "pending_sources": ["text-a-0126", "text-p-0839"],
                            "assigned_access_date": "2024-10-15",
                        })
                        report("approved_technology_paragraph_review_required", uid, "Seven source technology entries remain in order as one paragraph; original URLs are preserved; six citations use only curated, authorless metadata; Graph API and Docker bibliography details remain pending. Human presentation review remains required", source_id="text-list-0109", severity="warning")
                else:
                    _verify_markerless_list("text-list-0025", source_text, disposition, presentation_authorization)
                    report("approved_list_marker_review_required", uid, "The five source list items remain in order; only their visible bullet glyphs are suppressed under explicit user presentation authorization. Human visual approval remains pending", source_id="text-list-0025", severity="warning")
            except (ValueError, OSError, KeyError, StopIteration, UnicodeError, TypeError) as exc:
                report("invalid_technology_list_presentation", uid, str(exc), source_id="text-list-0025")
        mapping_ids = [item.get("source_id") for item in mappings]
        duplicate_ids = [rid for rid, count in Counter(mapping_ids).items() if count > 1]
        for rid in duplicate_ids:
            report("duplicate_mapping", uid, "Source element mapped more than once", rid)
        allowed_ids = set(unit.get("record_ids", [])) | set(source_ids)
        for rid in set(mapping_ids) - allowed_ids:
            report("unknown_or_wrong_unit_mapping", uid, "Mapping does not belong to this source unit", rid)
        by_id = {item.get("source_id"): item for item in mappings}
        presentation_override_ids = {rid for rid, mapping in by_id.items() if set(mapping.get("serializations", [])) & set(PRESENTATION_SERIALIZATIONS)}
        repository_link_style_verified = False
        if presentation_override_ids or "approved_presentation_overrides" in unit_ledger:
            try:
                expected_override_ids = PRESENTATION_OVERRIDES_BY_UNIT.get(uid, set())
                policy = unit_ledger.get("approved_presentation_overrides")
                evidence_path = PRESENTATION_AUTHORIZATION_BY_UNIT.get(uid)
                if evidence_path is None:
                    raise ValueError("Presentation overrides are outside the specifically authorized edition units")
                if (policy != {"authorization_evidence": evidence_path, "source_ids": sorted(expected_override_ids)}
                        or presentation_override_ids != expected_override_ids):
                    raise ValueError("Presentation override ledger must cover exactly the user-authorized elements in this unit")
                if presentation_authorization is None:
                    raise ValueError(presentation_authorization_error or "Missing user authorization")
                repository_link_style_verified = True
                report("approved_presentation_review_required", uid, "Presentation overlays are narrowly authorized and source-linked; human presentation approval remains pending", severity="warning")
            except (ValueError, OSError, KeyError, UnicodeError, TypeError) as exc:
                report("invalid_repository_link_style", uid, str(exc))
        uses_original_whitespace = any("original_whitespace" in item.get("serializations", []) for item in mappings)
        inline_ids = {item.get("source_id") for item in mappings if "inline_tab_layout" in item.get("serializations", [])}
        unit_inline_counts = AGES_II_INLINE_TAB_COUNTS if uid in AGES_II_UNITS else INLINE_TAB_COUNTS
        inline_verified = False
        if inline_ids:
            try:
                policy = unit_ledger.get("inline_tab_layout")
                if not isinstance(policy, dict) or set(policy) != {"authorization_evidence", "source_ids"}:
                    raise ValueError("Inline tab layout requires exact authorization_evidence/source_ids policy")
                ages_ii_inline = uid in AGES_II_UNITS
                allowed_counts = AGES_II_INLINE_TAB_COUNTS if ages_ii_inline else INLINE_TAB_COUNTS
                evidence_path = AGES_II_INLINE_TAB_AUTHORIZATION if ages_ii_inline else INLINE_TAB_AUTHORIZATION
                expected_source_order = [rid for rid in source_ids if rid in allowed_counts]
                if (policy["authorization_evidence"] != evidence_path
                        or not isinstance(policy["source_ids"], list)
                        or policy["source_ids"] != expected_source_order
                        or set(policy["source_ids"]) != inline_ids
                        or not inline_ids <= allowed_counts.keys()):
                    raise ValueError("Inline tab policy differs from the exact source IDs authorized for this edition")
                authorization = presentation_authorization if ages_ii_inline else json.loads(safe_path(INLINE_TAB_AUTHORIZATION).read_text(encoding="utf-8"))
                if ages_ii_inline:
                    change_counts = (authorization or {}).get("approved_presentation_changes", {}).get("inline_tab_source_counts")
                    if change_counts != AGES_II_INLINE_TAB_COUNTS or uid not in (authorization or {}).get("scope", []):
                        raise ValueError("AGES II inline tab presentation evidence is incomplete or outside scope")
                elif (authorization.get("kind") != "user_format_correction_authorization"
                        or not isinstance(authorization.get("scope"), list)
                        or uid not in authorization["scope"]
                        or authorization.get("quoted_instruction") != INLINE_TAB_USER_INSTRUCTION
                        or authorization.get("execution_authorized") is not True
                        or authorization.get("layout_source_ids") != list(INLINE_TAB_COUNTS)
                        or authorization.get("promoted_to_reusable_policy") is not False
                        or authorization.get("status") != "proposed_for_review"
                        or authorization.get("future_projects_approved") is not False):
                    raise ValueError("Missing explicit user formatting authorization or review/future-project boundary")
                inline_verified = True
                report("inline_tab_layout_review_required", uid, "Explicit user formatting correction: original internal tab tokens project exactly while the verified macro prints word spacing; PDF layout and human presentation approval remain separate", severity="warning")
            except (ValueError, OSError, KeyError, UnicodeError, TypeError) as exc:
                report("invalid_inline_tab_layout", uid, str(exc))
        reference_ids = {item.get("source_id") for item in mappings if "reference_paragraph_layout" in item.get("serializations", [])}
        reference_verified = False
        expected_ages_ii_spaces = AGES_II_LEADING_SPACE_COUNTS.get(uid, {})
        expected_ages_ii_line_breaks = AGES_II_LEADING_LINE_BREAK_COUNTS.get(uid, {})
        if reference_ids or "reference_paragraph_layout" in unit_ledger:
            try:
                policy = unit_ledger.get("reference_paragraph_layout")
                if not isinstance(policy, dict) or set(policy) != {"authorization_evidence", "source_ids"}:
                    raise ValueError("Reference paragraph layout requires exact authorization_evidence/source_ids policy")
                if uid in AGES_II_UNITS:
                    expected_tabs = AGES_II_LEADING_TAB_COUNTS.get(uid, {})
                    expected_layout_records = {**expected_tabs, **expected_ages_ii_spaces, **expected_ages_ii_line_breaks}
                    tab_paragraph_ids = _leading_tab_paragraph_ids(source_ids, records)
                    if (policy["authorization_evidence"] != AGES_II_PRESENTATION_AUTHORIZATION
                            or policy["source_ids"] != [rid for rid in source_ids if rid in expected_layout_records]
                            or reference_ids != set(expected_layout_records)
                            or tab_paragraph_ids != [rid for rid in source_ids if rid in expected_tabs]
                            or set(tab_paragraph_ids) != set(expected_tabs)):
                        raise ValueError("AGES II zero-width prefix policy must cover exactly the explicitly authorized source records")
                    for rid, count in expected_tabs.items():
                        original_text = records[rid]["text"]
                        leading_tabs = len(original_text) - len(original_text.lstrip("\t"))
                        if leading_tabs != count:
                            raise ValueError(f"Original tab count for {rid} differs from the frozen AGES II presentation evidence")
                    for rid, count in expected_ages_ii_spaces.items():
                        original_text = records[rid]["text"]
                        leading_spaces = len(original_text) - len(original_text.lstrip(" "))
                        if leading_spaces != count or _kind(records[rid]) != "h":
                            raise ValueError(f"Original leading-space count or heading type for {rid} differs from the frozen AGES II evidence")
                    for rid, count in expected_ages_ii_line_breaks.items():
                        original_text = records[rid]["text"]
                        leading_line_breaks = len(original_text) - len(original_text.lstrip("\n"))
                        if leading_line_breaks != count or _kind(records[rid]) != "p":
                            raise ValueError(f"Original leading line-break count or paragraph type for {rid} differs from the frozen AGES II evidence")
                    if (presentation_authorization is None
                            or presentation_authorization.get("approved_presentation_changes", {}).get("leading_tab_source_ids_by_unit") != AGES_II_LEADING_TAB_COUNTS
                            or presentation_authorization.get("approved_presentation_changes", {}).get("leading_space_source_counts") != AGES_II_LEADING_SPACE_COUNTS
                            or presentation_authorization.get("approved_presentation_changes", {}).get("leading_line_break_source_counts") != AGES_II_LEADING_LINE_BREAK_COUNTS):
                        raise ValueError("Missing approved AGES II presentation reuse evidence for leading tabs")
                else:
                    paragraph_ids = [rid for rid in source_ids if _kind(records[rid]) == "p" and records[rid].get("semantic_type") == "paragraph" and records[rid].get("text")]
                    if (uid not in REFERENCE_LAYOUT_UNITS
                            or policy["authorization_evidence"] != REFERENCE_LAYOUT_AUTHORIZATION
                            or policy["source_ids"] != paragraph_ids
                            or reference_ids != set(paragraph_ids)
                            or not set(paragraph_ids) <= set(REFERENCE_LAYOUT_PARAGRAPHS)
                            or any(records[rid].get("unit_id", uid) != uid for rid in paragraph_ids)):
                        raise ValueError("Reference layout policy must match exactly this authorized unit's original body paragraphs")
                    authorization = json.loads(safe_path(REFERENCE_LAYOUT_AUTHORIZATION).read_text(encoding="utf-8"))
                    if (authorization.get("kind") != "user_reference_style_request"
                            or authorization.get("scope") != list(REFERENCE_LAYOUT_UNITS)
                            or authorization.get("paragraph_source_ids") != list(REFERENCE_LAYOUT_PARAGRAPHS)
                            or authorization.get("baseline_commit") != REFERENCE_LAYOUT_BASELINE
                            or authorization.get("quoted_instruction") != REFERENCE_LAYOUT_USER_INSTRUCTION
                            or authorization.get("execution_authorized") is not True
                            or authorization.get("status") != "proposed_for_review"
                            or authorization.get("future_projects_approved") is not False
                            or authorization.get("promoted_to_reusable_policy") is not False
                            or "human_presentation_approval" not in authorization
                            or authorization["human_presentation_approval"] is not None):
                        raise ValueError("Missing explicit reference-style request or original scope/review/future-project boundary")
                reference_verified = True
                report("reference_paragraph_layout_review_required", uid, "Original whitespace tokens project exactly; verified zero-width leading markers implement the requested reference paragraph layout. PDF review and human presentation approval remain separate", severity="warning")
            except (ValueError, OSError, KeyError, UnicodeError, TypeError) as exc:
                report("invalid_reference_paragraph_layout", uid, str(exc))
        macro_verified = False
        if uses_original_whitespace or inline_ids or reference_verified:
            try:
                contract = unit_ledger.get("macro_contract", ledger.get("macro_contract"))
                if not isinstance(contract, dict):
                    raise ValueError("original_whitespace requires macro_contract {path,sha256}")
                contract_path = safe_path(contract["path"])
                contract_data = contract_path.read_bytes()
                if hashlib.sha256(contract_data).hexdigest() != contract.get("sha256"):
                    raise ValueError("Missing/stale macro contract SHA-256")
                contract_text = contract_data.decode("utf-8")
                definitions = macro_definitions(contract_text)
                bodies = {"originaltab": r"\noindent\hspace*{1.251cm}", "originalspace": r"\hspace*{\fontdimen2\font}"}
                if reference_verified or uid in AGES_II_UNITS:
                    bodies["originaltab"] = r"\hspace*{0pt}"
                    bodies["originalleadingspace"] = r"\hspace*{0pt}"
                    if expected_ages_ii_line_breaks:
                        bodies["originalleadbreak"] = r"\hspace*{0pt}"
                if inline_ids:
                    bodies["originalinlinetab"] = r"\unskip\space"
                for name, body in bodies.items():
                    found = [item for item in definitions if item["name"] == name]
                    if len(found) != 1 or found[0]["declaration"] != "newcommand" or found[0]["arity"] != 0 or found[0]["optional_default"] or canonical_macro_body(found[0]["body"]) != canonical_macro_body(body):
                        raise ValueError(f"Actual {name} definition differs from audited contract")
                if re.search(r"\\(?:let|futurelet)\s*\\(?:originaltab|originalspace|originalinlinetab|originalleadingspace|originalleadbreak)\b", strip_comments(contract_text)):
                    raise ValueError("Whitespace macro is aliased/redefined outside its audited definition")
                macro_verified = True
            except (ValueError, OSError, KeyError, UnicodeError, TypeError) as exc:
                report("invalid_macro_contract", uid, str(exc))
        figure_verified = False
        contract = unit_ledger.get("figure_contract", ledger.get("figure_contract"))
        if contract is not None:
            try:
                if not isinstance(contract, dict) or set(contract) != {"path", "sha256"}:
                    raise ValueError("Contract requires exactly path and sha256")
                contract_data = safe_path(contract["path"]).read_bytes()
                if hashlib.sha256(contract_data).hexdigest() != contract.get("sha256"):
                    raise ValueError("Missing/stale figure contract SHA-256")
                found = [item for item in macro_definitions(contract_data.decode()) if item["name"] == "memorialfigure"]
                if len(found) != 1 or found[0]["declaration"] != "newcommand" or found[0]["arity"] != 5 or found[0]["optional_default"] or canonical_macro_body(found[0]["body"]) != canonical_macro_body(MEMORIAL_FIGURE_BODY):
                    raise ValueError("memorialfigure differs from audited canonical definition")
                if re.search(r"\\(?:let|futurelet)\s*\\memorialfigure\b", strip_comments(contract_data.decode())):
                    raise ValueError("Figure macro alias/redefinition")
                figure_verified = True
            except (ValueError, OSError, KeyError, UnicodeError, TypeError) as exc:
                report("invalid_figure_contract", uid, str(exc))
        actual = {}
        for rid, mapping in by_id.items():
            if rid not in allowed_ids:
                continue
            try:
                actual[rid] = fragment(mapping)
            except (ValueError, OSError, UnicodeError, TypeError) as exc:
                report("invalid_target_evidence", uid, str(exc), rid, mapping.get("target_file"))

        # Derive order from actual inclusion graph, not element_map list order.
        file_order, seen = [], set()
        def walk_target(path, active):
            if path in active:
                raise ValueError("Include cycle in unit target")
            if path in seen:
                raise ValueError("Target file included more than once")
            text = path.read_text(encoding="utf-8")
            seen.add(path)
            file_order.append(path)
            for token in commands(text):
                if token.name in {"include", "input"} and token.args:
                    child = (compilation_root / token.args[0]).resolve()
                    if not child.is_relative_to(repo):
                        raise ValueError("Include escapes repository")
                    if child.suffix != ".tex":
                        child = Path(str(child) + ".tex")
                    walk_target(child, active | {path})
        target_entry = unit_ledger.get("tex_path")
        try:
            walk_target(safe_path(target_entry), set())
        except (ValueError, OSError, UnicodeError, TypeError) as exc:
            report("invalid_unit_target", uid, str(exc), path=target_entry)
        order_index = {path: i for i, path in enumerate(file_order)}
        if uses_original_whitespace:
            for path in file_order:
                actual_text = path.read_text(encoding="utf-8")
                if any(item["name"] in {"originaltab", "originalspace", "originalinlinetab", "originalleadingspace", "originalleadbreak"} for item in macro_definitions(actual_text)) or re.search(r"\\(?:let|futurelet)\s*\\(?:originaltab|originalspace|originalinlinetab|originalleadingspace|originalleadbreak)\b", strip_comments(actual_text)):
                    report("whitespace_macro_redefinition", uid, "Unit target changes the verified whitespace macros", path=str(path.relative_to(repo)))
                    macro_verified = False
        for path in file_order:
            text = path.read_text(encoding="utf-8")
            if any(item["name"] == "memorialfigure" for item in macro_definitions(text)) or re.search(r"\\(?:let|futurelet)\s*\\memorialfigure\b", strip_comments(text)):
                report("figure_macro_redefinition", uid, "Unit redefines audited figure macro")
                figure_verified = False
        # Expansion position supports parent text both before and after an input.
        expansion_positions = {}
        expansion_cursor = 0
        def expand_positions(path, active):
            nonlocal expansion_cursor
            if path in active:
                return
            data = path.read_bytes()
            text = data.decode("utf-8")
            previous = 0
            for token in commands(text):
                if token.name not in {"input", "include"} or not token.args:
                    continue
                start_byte = len(text[:token.start].encode("utf-8"))
                end_byte = len(text[:token.end].encode("utf-8"))
                expansion_positions.setdefault(path, []).append((previous, start_byte, expansion_cursor - previous))
                expansion_cursor += start_byte - previous
                child = (compilation_root / token.args[0]).resolve()
                if child.suffix != ".tex":
                    child = Path(str(child) + ".tex")
                if child in seen:
                    expand_positions(child, active | {path})
                previous = end_byte
            expansion_positions.setdefault(path, []).append((previous, len(data), expansion_cursor - previous))
            expansion_cursor += len(data) - previous
        try:
            if file_order:
                expand_positions(file_order[0], set())
        except (OSError, UnicodeError, ValueError):
            pass  # Already reported by walk_target.

        positions = []
        text_spans = []
        for rid in source_ids:
            if rid not in by_id:
                report("missing_element", uid, "Source textual element has no target mapping", rid)
                continue
            if rid not in actual:
                continue
            path, start, end, value = actual[rid]
            if path not in order_index:
                report("unreachable_target", uid, "Mapped file is not included in the unit target", rid, str(path.relative_to(repo)))
            position = next((start + delta for lo, hi, delta in expansion_positions.get(path, []) if lo <= start and end <= hi), None)
            if position is None:
                report("invalid_text_span", uid, "Text span overlaps an inclusion boundary or unreachable source", rid)
            else:
                positions.append((rid, position))
            text_spans.append((path, start, end, rid))
            serializations = by_id[rid].get("serializations", [])
            original = records[rid]["text"]
            try:
                expected = _strict_source(
                    original,
                    _source_whitespace_verified(serializations, macro_verified, reference_verified),
                    expected_ages_ii_line_breaks.get(rid, 0) if reference_verified and "reference_paragraph_layout" in serializations else 0,
                )
            except UnsupportedSerialization as exc:
                report("explicit_source_whitespace", uid, str(exc), rid, str(path.relative_to(repo)))
                differences[uid].append({"source_id": rid, "target_file": str(path.relative_to(repo)), "expected": original, "observed": None, "diff": "Whitespace equivalence is unproven; no automatic normalization accepted"})
                continue
            try:
                inline_policy = "inline_tab_layout" in serializations
                if inline_policy:
                    if not inline_verified or rid not in unit_inline_counts:
                        raise UnsupportedSerialization("Inline tab layout is outside explicitly authorized source scope")
                    tokens = _display_tokens(value, serializations, macro_verified, inline_verified, reference_verified)
                    tabs = [token for token in tokens if isinstance(token, _ExplicitWhitespace) and token.value == "\t"]
                    tab_positions = [index for index, char in enumerate(original) if char == "\t"]
                    expected_layout = [bool(original[:index].strip()) for index in tab_positions]
                    if sum(expected_layout) != unit_inline_counts[rid] or [token.inline_layout for token in tabs] != expected_layout:
                        raise UnsupportedSerialization("Inline tab layout must preserve every leading tab and every authorized internal tab in exact order")
                if reference_verified:
                    tokens = _display_tokens(value, serializations, macro_verified, inline_verified, reference_verified)
                    prefix_end = len(original) - len(original.lstrip(" \t"))
                    whitespace = [token for token in tokens if isinstance(token, _ExplicitWhitespace)]
                    # The exact text comparison below also checks marker positions.
                    # Here distinguish zero-width source metadata from visible spaces.
                    if any(token.value == "\t" and not token.inline_layout for token in whitespace) and "original_whitespace" not in serializations:
                        raise UnsupportedSerialization("Leading tab metadata requires original_whitespace")
                    if "\t" in original[prefix_end:] and not inline_policy:
                        raise UnsupportedSerialization("Internal tabs require their separate authorized inline policy")
                    if sum(token.value == "\t" and not token.inline_layout for token in whitespace) != original[:prefix_end].count("\t"):
                        raise UnsupportedSerialization("Zero-width tab markers must preserve only the original leading tabs")
                    if any(token.leading_layout for token in whitespace):
                        allowed_leading_layout = (rid == "text-p-0413" and "reference_paragraph_layout" in serializations)
                        allowed_leading_layout = allowed_leading_layout or (uid in AGES_II_UNITS and rid in expected_ages_ii_spaces | expected_ages_ii_line_breaks and "reference_paragraph_layout" in serializations)
                        if not allowed_leading_layout:
                            raise UnsupportedSerialization("Leading space metadata is restricted to the scoped original paragraph")
                    if "reference_paragraph_layout" in serializations:
                        leading_spaces = sum(token.value == " " and token.leading_layout for token in whitespace)
                        source_leading_spaces = original[:prefix_end].count(" ")
                        if rid in expected_ages_ii_spaces:
                            source_leading_spaces = expected_ages_ii_spaces[rid]
                        if leading_spaces != source_leading_spaces:
                            raise UnsupportedSerialization("Leading spaces must preserve original prefix count as source metadata")
                        leading_line_breaks = sum(token.value == "\n" and token.leading_layout for token in whitespace)
                        source_leading_line_breaks = len(original) - len(original.lstrip("\n")) if rid in expected_ages_ii_line_breaks else 0
                        if leading_line_breaks != source_leading_line_breaks:
                            raise UnsupportedSerialization("Leading line breaks must preserve the exact authorized source prefix count")
                        # A leading-layout marker cannot replace an internal or trailing space.
                        projected = ""
                        for token in tokens:
                            if isinstance(token, _ExplicitWhitespace):
                                if token.leading_layout and projected.strip(" \t\n"):
                                    raise UnsupportedSerialization("Leading space metadata cannot occur inside text")
                                projected += token.value
                            else:
                                projected += token
                observed = displayed_text(value, serializations, macro_contract_verified=macro_verified, inline_layout_verified=inline_verified, reference_layout_verified=reference_verified)
                observed, presentation_transform = _project_approved_presentation(
                    rid, expected, observed, serializations, presentation_authorization
                )
                if presentation_transform is not None:
                    facts["approved_presentation_transformations"].append(presentation_transform)
            except (UnsupportedSerialization, ValueError) as exc:
                code = "invalid_presentation_serialization" if set(serializations) & set(PRESENTATION_SERIALIZATIONS) else "unsupported_serialization"
                report(code, uid, str(exc), rid)
                continue
            facts["text_records_checked"] += 1
            if expected != observed:
                difference = {"source_id": rid, "target_file": str(path.relative_to(repo)), "expected": expected, "observed": observed, "diff": "\n".join(difflib.unified_diff([expected], [observed], fromfile="ODT", tofile="LaTeX", lineterm=""))}
                differences[uid].append(difference)
                report("text_changed", uid, "Text differs in actual target bytes", rid, str(path.relative_to(repo)))
            else:
                facts["text_records_matched"] += 1
                if "inline_tab_layout" in serializations:
                    facts["inline_tab_layout_records_matched"] += 1
                if "reference_paragraph_layout" in serializations:
                    facts["reference_paragraph_layout_records_matched"] += 1
        projected_source_order, source_order_error = _project_source_text_order(uid, source_ids, records)
        if source_order_error:
            report("unverified_embedded_source_order", uid, source_order_error, "text-p-0961")
        else:
            position_by_id = dict(positions)
            projected_positions = [position_by_id[rid] for rid in projected_source_order if rid in position_by_id]
            if len(projected_positions) == len(positions) and projected_positions != sorted(projected_positions):
                report("element_order_changed", uid, "Source elements appear in a different target expansion order")
        for index, (path, start, end, rid) in enumerate(text_spans):
            for other_path, other_start, other_end, other_rid in text_spans[index + 1:]:
                if path == other_path and max(start, other_start) < min(end, other_end):
                    report("overlapping_text_evidence", uid, f"Text interval overlaps {other_rid}", rid)

        for rid in unit.get("record_ids", []):
            record = records.get(rid, {})
            if _kind(record) != "a" or not record.get("href"):
                continue
            if rid not in actual:
                report("missing_hyperlink", uid, "Hyperlink has no independently readable mapping", rid)
                continue
            path, _, _, value = actual[rid]
            links = [token for token in commands(value) if token.name in {"href", "url"} and token.args]
            if len(links) != 1:
                report("invalid_hyperlink_evidence", uid, "Link interval must contain exactly one href/url", rid)
                continue
            token = links[0]
            if len(token.args) != (2 if token.name == "href" else 1):
                report("invalid_hyperlink_evidence", uid, "Hyperlink has extra or missing arguments", rid)
            observed_url = _url(token.args[0])
            expected_url = record["href"]
            facts["links_checked"] += 1
            if observed_url != expected_url:
                report("url_changed", uid, f"Expected {expected_url!r}; observed {observed_url!r}", rid)
            if not _valid_url(observed_url):
                report("malformed_url", uid, observed_url, rid)
            anchor = token.args[1] if token.name == "href" and len(token.args) >= 2 else token.args[0]
            try:
                policies = by_id[rid].get("serializations", [])
                observed_anchor = displayed_text(anchor, policies, macro_contract_verified=macro_verified) if token.name == "href" else _url(anchor)
                repository_rule = PRESENTATION_REPOSITORY_LINKS.get(rid)
                if repository_rule is not None:
                    prefix = value[:token.start]
                    suffix = value[token.end:]
                    if (not repository_link_style_verified
                            or "repository_link_sentence" not in policies
                            or record.get("href") != repository_rule["href"]
                            or record.get("source_text") != repository_rule["source_anchor"]
                            or observed_url != repository_rule["href"]
                            or observed_anchor != repository_rule["anchor"]
                            or prefix != repository_rule["prefix"]
                            or suffix != repository_rule["suffix"]):
                        report("invalid_repository_link_sentence", uid, "Repository link sentence, visible anchor, or original direct URL differs from the exact user-approved form", rid)
                    else:
                        facts["approved_presentation_transformations"].append({"source_id": rid, "kind": "repository_link_in_prose", "source": repository_rule["source_anchor"], "displayed": prefix + observed_anchor + suffix, "href": observed_url})
                else:
                    if strip_comments(value[:token.start] + value[token.end:]).strip():
                        report("unmapped_link_span_content", uid, "Link interval contains additional unproved content", rid)
                    if observed_anchor != _strict_source(
                        record.get("source_text") or "",
                        _source_whitespace_verified(policies, macro_verified, reference_verified),
                        expected_ages_ii_line_breaks.get(rid, 0) if reference_verified and "reference_paragraph_layout" in policies else 0,
                    ):
                        report("link_anchor_changed", uid, "Displayed anchor differs from original", rid)
            except (ValueError, UnsupportedSerialization) as exc:
                report("unsupported_link_anchor", uid, str(exc), rid)

        asset_maps = unit_ledger.get("asset_map", [])
        asset_ids = [item.get("source_id") for item in asset_maps]
        for rid, count in Counter(asset_ids).items():
            if count != 1:
                report("duplicate_asset_mapping", uid, "Asset occurrence mapped more than once", rid)
        asset_by_occurrence = {item.get("source_id"): item for item in asset_maps}
        expected_images = {occurrence: asset for asset in assets.values() for occurrence in asset.get("occurrence_ids", []) if occurrence in allowed_ids}
        for rid, asset in expected_images.items():
            mapping = asset_by_occurrence.get(rid)
            if mapping is None or rid not in actual:
                report("missing_image", uid, "Image occurrence lacks asset or LaTeX mapping", rid)
                continue
            try:
                image_path = safe_path(mapping.get("target_file"))
                digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
                if digest != asset["sha256"]:
                    report("image_hash_changed", uid, "Actual image differs from embedded original", rid)
                tokens = [token for token in commands(actual[rid][3]) if token.name in {"includegraphics", "memorialfigure"} and token.args]
                if len(tokens) != 1:
                    raise ValueError("Image interval must contain exactly one includegraphics")
                token = tokens[0]
                if token.name == "memorialfigure":
                    if not figure_verified or len(token.args) != 5 or token.optionals or token.starred:
                        raise ValueError("memorialfigure requires verified five-argument contract")
                    if token.args[3] != "Fonte: pendente de identificação":
                        raise ValueError("Unknown image source must remain explicitly pending")
                    if not re.fullmatch(r"(?:0?\.\d+|1(?:\.0+)?)", token.args[4]) or not 0 < float(token.args[4]) <= 1:
                        raise ValueError("Invalid figure width fraction")
                    if not re.fullmatch(r"[A-Za-z0-9:._-]+", token.args[2]) or token.args[2] in figure_labels:
                        raise ValueError("Missing/invalid/duplicate figure label")
                    figure_labels.add(token.args[2])
                    caption_ids = records[rid].get("caption_ids", [])
                    if len(caption_ids) != 1 or caption_ids[0] not in actual:
                        raise ValueError("Figure needs its independently mapped source caption")
                    caption_id = caption_ids[0]
                    cp, cs, ce, cv = actual[caption_id]
                    value = actual[rid][3]
                    cursor = value.index("{", token.start)
                    _, cursor = _group(value, cursor, "{", "}")
                    while value[cursor].isspace():
                        cursor += 1
                    caption_start = cursor + 1
                    _, caption_end = _group(value, cursor, "{", "}")
                    base = actual[rid][1]
                    if cp != actual[rid][0] or cs != base + len(value[:caption_start].encode()) or ce != base + len(value[:caption_end - 1].encode()) or cv != token.args[1]:
                        raise ValueError("Caption interval must be exactly figure arg2 associated with this source image")
                elif len(token.args) != 1:
                    raise ValueError("Image interval contains extra or missing arguments")
                if strip_comments(actual[rid][3][:tokens[0].start] + actual[rid][3][tokens[0].end:]).strip():
                    raise ValueError("Image interval contains additional unproved content")
                referenced = (compilation_root / tokens[0].args[0]).resolve()
                if referenced.suffix.lower() not in {".pdf", ".png", ".jpg", ".jpeg", ".eps"}:
                    referenced = next((Path(str(referenced) + ext) for ext in (".pdf", ".png", ".jpg", ".jpeg") if Path(str(referenced) + ext).is_file()), referenced)
                if referenced != image_path:
                    raise ValueError("Mapped image is not the asset referenced by actual LaTeX")
                facts["images_checked"] += 1
            except (ValueError, OSError, KeyError, TypeError) as exc:
                report("invalid_image_evidence", uid, str(exc), rid)
        for rid in set(asset_ids) - set(expected_images):
            report("unexpected_asset_mapping", uid, "Image occurrence does not belong to the unit", rid)
        derived_spans = {}
        toc_counts = Counter()
        placeholder_specs = {
            "chapter-02-text-h-0009": ("text-h-0009", "ages-i-database", "Banco de dados utilizado ", "Esquema do banco de dados não incorporado ao ODT; preenchimento posterior."),
            "chapter-02-text-h-0010": ("text-h-0010", "ages-i-architecture", "Arquitetura utilizada ", "Diagrama de arquitetura não incorporado ao ODT; preenchimento posterior."),
            "chapter-04-text-h-0043": ("text-h-0043", "ages-ii-database", "4.2.2 Banco de dados utilizado", "Diagrama do banco de dados ausente no ODT; preenchimento posterior."),
        }
        if uid in placeholder_specs and len(unit_ledger.get("approved_apparatus", [])) != 1:
            report("missing_authorized_placeholder", uid, "Missing-diagram unit requires its one explicitly authorized provisional placeholder")
        for apparatus in unit_ledger.get("approved_apparatus", []):
            try:
                if set(apparatus) != {"kind", "source_heading_id", "placeholder_id", "authorization_evidence", "target_file", "start_byte", "end_byte", "target_sha256"}:
                    raise ValueError("Unknown/missing apparatus schema fields")
                contract = unit_ledger.get("macro_contract", ledger.get("macro_contract"))
                if not isinstance(contract, dict) or set(contract) != {"path", "sha256"}:
                    raise ValueError("Contract requires exactly path and sha256")
                contract_data = safe_path(contract["path"]).read_bytes()
                if hashlib.sha256(contract_data).hexdigest() != contract.get("sha256"):
                    raise ValueError("Missing/stale placeholder macro contract")
                found = [item for item in macro_definitions(contract_data.decode()) if item["name"] == "diagramplaceholder"]
                if len(found) != 1 or found[0]["declaration"] != "newcommand" or found[0]["arity"] != 2 or found[0]["optional_default"] or canonical_macro_body(found[0]["body"]) != canonical_macro_body(DIAGRAM_PLACEHOLDER_BODY):
                    raise ValueError("Placeholder macro differs from audited provisional body")
                for target in file_order:
                    text = target.read_text()
                    if any(item["name"] == "diagramplaceholder" for item in macro_definitions(text)) or re.search(r"\\(?:let|futurelet)\s*\\diagramplaceholder\b", strip_comments(text)):
                        raise ValueError("Unit redefines audited placeholder macro")
                spec = placeholder_specs.get(uid)
                if spec is None or apparatus.get("kind") != "diagram_placeholder" or apparatus.get("source_heading_id") != spec[0] or apparatus.get("placeholder_id") != spec[1] or spec[0] not in source_ids or records[spec[0]]["text"] != spec[2] or expected_images:
                    raise ValueError("Placeholder is not bound to the authorized original heading")
                config = json.loads(safe_path("harness.json").read_text())
                if uid == "chapter-04-text-h-0043":
                    evidence = "migration/approvals/ages-ii-authorization.json"
                    auth = json.loads(safe_path(evidence).read_text())
                    placeholder_decision = any(
                        item.get("element") == "database diagram"
                        and "placeholder" in item.get("action", "").lower()
                        for item in auth.get("missing_material", [])
                    )
                    valid_edition_evidence = (
                        config.get("authorization_evidence") == evidence
                        and config.get("authorized_edition") == "ages-ii"
                        and uid in auth.get("authorized_units", [])
                        and auth.get("authorized") is True
                        and placeholder_decision
                    )
                else:
                    evidence = "migration/approvals/ages-i-authorization.json"
                    auth = json.loads(safe_path(evidence).read_text())
                    quote = "Vamos começar com AGES I. Lembre-se que os itens faltantes como arquitetura, banco de dados precisarão de placeholders que serão preenchidos posteriormente"
                    valid_edition_evidence = (
                        config.get("phase") == "edition"
                        and config.get("authorization_evidence") == evidence
                        and uid in auth.get("scope", [])
                        and auth.get("kind") == "user_execution_authorization"
                        and auth.get("quoted_instruction") == quote
                        and spec[2].strip() in auth.get("placeholders_explicitly_authorized", [])
                    )
                if apparatus.get("authorization_evidence") != evidence or not valid_edition_evidence:
                    raise ValueError("Missing explicit edition/placeholder user authorization evidence")
                path, start, end, value = fragment(apparatus)
                tokens = list(commands(value))
                if path not in file_order or len(tokens) != 1 or tokens[0].name != "diagramplaceholder" or tokens[0].args != (spec[1], spec[3]) or tokens[0].starred or tokens[0].optionals or strip_comments(value[:tokens[0].start] + value[tokens[0].end:]).strip():
                    raise ValueError("Placeholder interval differs from authorized provisional apparatus")
                if len(unit_ledger["approved_apparatus"]) != 1:
                    raise ValueError("Exactly one authorized placeholder per missing-diagram unit")
                derived_spans.setdefault(path, []).append((start, end))
            except (ValueError, KeyError, TypeError, OSError, UnicodeError) as exc:
                report("invalid_approved_apparatus", uid, str(exc))
        for path in file_order:
            target_text = path.read_text(encoding="utf-8")
            target_tokens = list(commands(target_text))
            headings = []
            for rid in source_ids:
                if not _is_source_heading(records[rid]) or rid not in actual or actual[rid][0] != path:
                    continue
                _, start, end, _ = actual[rid]
                policies = by_id[rid].get("serializations", [])
                for token in target_tokens:
                    token_start = len(target_text[:token.start].encode("utf-8"))
                    token_end = len(target_text[:token.end].encode("utf-8"))
                    if token.name not in {"chapter", "section", "subsection", "subsubsection"} or len(token.args) != 1 or not token_start <= start <= end <= token_end:
                        continue
                    try:
                        title = displayed_text(
                            token.args[0], policies,
                            macro_contract_verified=macro_verified,
                            inline_layout_verified=inline_verified,
                            reference_layout_verified=reference_verified,
                        )
                        expected = _strict_source(
                            records[rid]["text"],
                            _source_whitespace_verified(policies, macro_verified, reference_verified),
                            expected_ages_ii_line_breaks.get(rid, 0) if reference_verified and "reference_paragraph_layout" in policies else 0,
                        )
                        title, _ = _project_approved_presentation(rid, expected, title, policies, presentation_authorization)
                        if title == expected:
                            headings.append((rid, expected, policies, token))
                    except UnsupportedSerialization:
                        pass  # Existing source/target text findings remain authoritative.
            for rid in source_ids:
                if not _is_source_heading(records[rid]) or rid not in actual or actual[rid][0] != path:
                    continue
                found = [item for item in headings if item[0] == rid]
                if len(found) != 1:
                    report("invalid_source_heading", uid, "Source heading must map to exactly one actual title argument", rid)
                    continue
                _, title, _, heading = found[0]
                level = records[rid].get("attributes", {}).get("text:outline-level")
                expected_kind = {"1": "chapter", "2": "section", "3": "subsection"}.get(level)
                manual = bool(re.match(r"^\d+(?:\.\d+)*[.]?\s", title))
                if expected_kind is not None and heading.name != expected_kind or manual and not heading.starred:
                    report("invalid_source_heading", uid, "Heading hierarchy or numbering representation differs from original", rid)
                if not heading.starred:
                    report("counter_aux_review_required", uid, "Automatically generated heading number needs separate compiled .aux review", rid, severity="warning")
            for token in target_tokens:
                if token.name != "addcontentsline":
                    continue
                matched = []
                if len(token.args) == 3 and token.args[0] == "toc":
                    for rid, expected, policies, heading in headings:
                        try:
                            entry = displayed_text(
                                token.args[2], policies,
                                macro_contract_verified=macro_verified,
                                inline_layout_verified=inline_verified,
                                reference_layout_verified=reference_verified,
                            )
                            entry, _ = _project_approved_presentation(rid, expected, entry, policies, presentation_authorization)
                            if heading.starred and token.args[1] == heading.name and entry == expected:
                                matched.append(rid)
                        except UnsupportedSerialization:
                            pass
                if len(matched) != 1:
                    report("unproved_toc_entry", uid, "TOC entry must equal one original heading and its actual subsection* title", path=str(path.relative_to(repo)))
                    continue
                toc_counts[matched[0]] += 1
                if toc_counts[matched[0]] > 1:
                    report("duplicate_toc_entry", uid, "Original heading has more than one derived TOC entry", matched[0])
                    continue
                derived_spans.setdefault(path, []).append((len(target_text[:token.start].encode("utf-8")), len(target_text[:token.end].encode("utf-8"))))
            for index, token in enumerate(target_tokens):
                if token.name != "refstepcounter":
                    continue
                next_token = target_tokens[index + 1] if index + 1 < len(target_tokens) else None
                matches = [(rid, title) for rid, title, _, heading_token in headings if next_token is heading_token and heading_token.starred and ((heading_token.name == "chapter" and re.match(r"^\d+ - ", title)) or (heading_token.name == "section" and re.match(r"^\d+\.\d+\.?\s", title)) or (heading_token.name == "subsection" and re.match(r"^\d+\.\d+\.\d+\s", title)))]
                gap = strip_comments(target_text[token.end:next_token.start]) if next_token else ""
                if next_token is None or token.args != (next_token.name,) or len(matches) != 1 or gap.strip():
                    report("unproved_counter_step", uid, "Only a subsection counter step immediately before its original manually numbered subsection* is allowed", path=str(path.relative_to(repo)))
                    continue
                derived_spans.setdefault(path, []).append((len(target_text[:token.start].encode("utf-8")), len(target_text[:token.end].encode("utf-8"))))
                report("counter_aux_review_required", uid, "Counter text is not printed; compare compiled .aux label number against original heading", matches[0][0], severity="warning")
        expected_bookmarks = {(rid, record.get("attributes", {}).get("text:name")) for rid, record in records.items() if _kind(record) == "bookmark-start" and record.get("parent_id") in source_ids and _kind(records[record["parent_id"]]) == "h"}
        mapped_bookmarks = Counter()
        for mapping in unit_ledger.get("bookmark_map", []):
            try:
                heading_id = mapping["source_heading_id"]
                if heading_id not in source_ids or _kind(records[heading_id]) != "h":
                    raise ValueError("Bookmark does not refer to a source heading in this unit")
                mapped_bookmarks[(mapping["source_start_id"], mapping["source_name"])] += 1
                original_start = records[mapping["source_start_id"]]
                original_end = records[mapping["source_end_id"]]
                source_name = mapping["source_name"]
                if _kind(original_start) != "bookmark-start" or _kind(original_end) != "bookmark-end" or original_start.get("attributes", {}).get("text:name") != source_name or original_end.get("attributes", {}).get("text:name") != source_name:
                    raise ValueError("Source bookmark names/start/end do not match")
                if original_start.get("parent_id") != heading_id or original_end.get("parent_id") != heading_id:
                    raise ValueError("Source bookmark is not inside the mapped heading")
                path, start, end, value = fragment(mapping)
                bookmarks = list(commands(value))
                if len(bookmarks) != 1 or bookmarks[0].name != "hypertarget" or bookmarks[0].args != (source_name, "") or mapping.get("target_anchor") != source_name or mapping.get("command") != "hypertarget" or strip_comments(value[:bookmarks[0].start] + value[bookmarks[0].end:]).strip():
                    raise ValueError("Target bookmark must retain the source name and have zero visible text")
                if path not in file_order:
                    raise ValueError("Bookmark target is not included in the unit")
                derived_spans.setdefault(path, []).append((start, end))
            except (ValueError, KeyError, TypeError, OSError, UnicodeError) as exc:
                report("invalid_bookmark_evidence", uid, str(exc))
        if set(mapped_bookmarks) != expected_bookmarks or any(count != 1 for count in mapped_bookmarks.values()):
            report("missing_or_duplicate_bookmark", uid, "Every original heading bookmark requires exactly one independently verified mapping")
        # Check the complement of proven intervals so added or duplicated words
        # cannot hide outside the ledger. Only documented nonprinting scaffolding
        # is allowed. Unknown macros/environments need a harness policy change,
        # not a converter's assertion that they are harmless.
        structural_commands = {"label", "input", "include"}
        wrapper_commands = {"chapter", "section", "subsection", "subsubsection", "paragraph", "caption", "textbf", "textit", "emph", "texttt", "textrm", "textsf", "textnormal", "underline", "mbox"}
        declarations = {"centering", "raggedright", "raggedleft", "small", "footnotesize", "normalsize", "bfseries", "itshape", "normalfont", "noindent", "indent", "par", "newline", "item"}
        environments = {"figure", "figure*", "center", "flushleft", "flushright", "itemize", "enumerate", "description", "reflection", "reflexao", "introspection"}
        printable_ids = set(source_ids) | {rid for rid in allowed_ids if _kind(records.get(rid, {})) == "a"} | set(expected_images)
        for path in file_order:
            data = bytearray(path.read_bytes())
            for rid in printable_ids:
                if rid in actual and actual[rid][0] == path:
                    _, start, end, _ = actual[rid]
                    data[start:end] = b" " * (end - start)
            for start, end in derived_spans.get(path, []):
                data[start:end] = b" " * (end - start)
            try:
                residue = strip_comments(data.decode("utf-8"))
                chars = list(residue)
                for token in commands(residue):
                    if token.name in structural_commands or (technology_paragraph_verified and token.name in {"cite", "space"}):
                        chars[token.start:token.end] = " " * (token.end - token.start)
                    elif token.name in {"begin", "end"} and token.args and token.args[0] in environments:
                        chars[token.start:token.end] = " " * (token.end - token.start)
                    elif token.name in wrapper_commands | declarations:
                        command_end = token.start + len(token.name) + 1
                        if command_end < len(residue) and residue[command_end] == "*":
                            command_end += 1
                        chars[token.start:command_end] = " " * (command_end - token.start)
                    else:
                        report("unsupported_target_scaffolding", uid, f"Unproved command \\{token.name} outside source mappings", path=str(path.relative_to(repo)))
                remainder = "".join(chars)
                remainder = re.sub(r"[{}\s]", "", remainder)
                if technology_paragraph_verified and uid == "chapter-02-text-h-0012":
                    if remainder != ";;;;.":
                        report("unmapped_visible_content", uid, "Technology paragraph contains unapproved visible punctuation outside the source mappings: " + remainder[:160], path=str(path.relative_to(repo)))
                    remainder = ""
                elif technology_paragraph_verified and uid == "chapter-04-text-h-0046":
                    if remainder:
                        report("unmapped_visible_content", uid, "AGES II technology paragraph contains visible content outside its element mappings: " + remainder[:160], path=str(path.relative_to(repo)))
                    remainder = ""
                if remainder:
                    report("unmapped_visible_content", uid, "Target contains content outside proven mappings: " + remainder[:160], path=str(path.relative_to(repo)))
            except (ValueError, UnicodeError) as exc:
                report("target_complement_parse_error", uid, str(exc), path=str(path.relative_to(repo)))
        if unit_ledger.get("rendered_pdf"):
            pdf = unit_ledger["rendered_pdf"]
            try:
                if not isinstance(pdf, dict):
                    raise ValueError("rendered_pdf requires path and sha256")
                data = safe_path(pdf["path"]).read_bytes()
                if not data.startswith(b"%PDF-") or hashlib.sha256(data).hexdigest() != pdf.get("sha256"):
                    raise ValueError("Invalid/stale PDF evidence")
                report("pdf_manual_review_required", uid, "PDF bytes verified; glyphs, numbering and layout require separate rendered review", severity="warning")
            except (ValueError, KeyError, OSError, TypeError) as exc:
                report("invalid_pdf_evidence", uid, str(exc))
        else:
            report("pdf_evidence_pending", uid, "No rendered PDF evidence; lexical preservation does not approve visual quality", severity="warning")

    facts["coverage_percent"] = round(100 * facts["text_records_checked"] / facts["source_text_records"], 2) if facts["source_text_records"] else 0.0
    if any(item["severity"] == "error" for item in findings):
        status = "blocked"
    elif facts["converted_units"] == 0:
        status = "unconverted"
    elif any(item["code"] == "unit_unconverted" for item in findings):
        status = "partial"
    else:
        status = "pass"
    return {"status": status, "findings": findings, "facts": facts, "differences": differences}
