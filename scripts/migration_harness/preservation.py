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
approved_group_label_removal records the two AGES III prototype group labels
as source-preserved but intentionally absent from the typeset output under the
user's exact decision evidence; it cannot be reused for other source records.
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

from .latex import _group, commands, strip_comments, macro_definitions, canonical_macro_body, MEMORIAL_FIGURE_BODY, MEMORIAL_FIGURE_LINKED_BODY
from . import technology_prose


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
AGES_III_AUTHORIZATION = "migration/approvals/ages-iii-authorization.json"
AGES_III_PROTOTYPE_GROUP_LABEL_REMOVAL_AUTHORIZATION = "migration/approvals/ages-iii-prototype-group-labels.json"
AGES_III_TECHNOLOGY_NARRATIVE_AUTHORIZATION = "migration/approvals/ages-iii-technology-narrative-authorization.json"
AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_TEXT_IDS = (
    "text-p-1067", "text-p-1070", "text-p-1074", "text-p-1078", "text-p-1081",
    "text-p-1085", "text-p-1088", "text-p-1091", "text-p-1094", "text-p-1097",
    "text-p-1100", "text-p-1103", "text-p-1106",
)
AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_ANCHORS = {
    "text-p-1067": "Documentação C#",
    "text-p-1070": "Documentação .NET",
    "text-p-1074": "Documentação React",
    "text-p-1078": "Documentação Typescript",
    "text-p-1081": "Documentação API Impinj R700",
    "text-p-1085": "Documentação Entity Framework",
    "text-p-1088": "Documentação AWS Lambda",
    "text-p-1091": "Documentação AWS S3",
    "text-p-1094": "Documentação AWS Cloudfront",
    "text-p-1097": "Documentação AWS RDS",
    "text-p-1100": "Documentação PostgreSQL",
    "text-p-1103": "Documentação Docker",
    "text-p-1106": "Documentação GitHub Actions",
}
AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_POLICY = {
    "source_ids": list(AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_TEXT_IDS),
    "prefix": "Mais informações podem ser encontradas em: ",
    "suffix": ".",
    "authorization_evidence": AGES_III_TECHNOLOGY_NARRATIVE_AUTHORIZATION,
}
AGES_III_PROTOTYPE_GROUP_LABELS = {
    "text-p-1056": "Telas de Administrador:",
    "text-h-0084": "Telas de Cliente:",
}
AGES_III_UNITS = (
    "chapter-05-text-h-0074", "chapter-05-text-h-0075", "chapter-05-text-h-0076",
    "chapter-05-text-h-0077", "chapter-05-text-h-0078", "chapter-05-text-h-0079",
    "chapter-05-text-h-0080", "chapter-05-text-h-0085", "chapter-05-text-h-0086",
    "ages-iii-sprint-0", "ages-iii-sprint-1", "ages-iii-sprint-2",
    "ages-iii-sprint-3", "ages-iii-sprint-4", "chapter-05-text-h-0097",
)
AGES_III_LEADING_TAB_COUNTS = {
    "chapter-05-text-h-0075": {"text-p-1022": 1, "text-p-1027": 1},
    "chapter-05-text-h-0078": {"text-p-1039": 1},
    "chapter-05-text-h-0079": {"text-p-1046": 1},
    "chapter-05-text-h-0085": {
        "text-p-1073": 1, "text-p-1074": 1, "text-p-1077": 1,
        "text-p-1078": 1, "text-p-1081": 1, "text-p-1084": 1,
        "text-p-1085": 1, "text-p-1088": 1, "text-p-1097": 1,
    },
    "ages-iii-sprint-0": {"text-p-1111": 1, "text-p-1123": 1, "text-p-1124": 1, "text-p-1125": 1},
    "ages-iii-sprint-1": {"text-p-1165": 1, "text-p-1166": 1, "text-p-1167": 1},
    "ages-iii-sprint-2": {"text-p-1199": 1, "text-p-1207": 1, "text-p-1209": 1},
    "ages-iii-sprint-3": {"text-p-1237": 1, "text-p-1246": 1, "text-p-1247": 1},
    "ages-iii-sprint-4": {"text-p-1278": 1, "text-p-1283": 1},
    "chapter-05-text-h-0097": {"text-p-1310": 1},
}
# The approved one-paragraph reflow treats the first two paragraphs' tabs as
# ODF line-layout whitespace. The internal tab is retained in the immutable
# source and removed from the target only under a separate, exact user approval.
AGES_III_INLINE_TAB_COUNTS = {"text-p-1084": 1}
AGES_III_INTERNAL_TAB_REMOVAL_AUTHORIZATION = "migration/approvals/ages-iii-internal-tab-removal.json"
AGES_III_TECHNOLOGY_LITERAL_TAB = {
    "source_id": "text-p-1084",
    "source_fragment": "consultas t\tipadas",
    "target_fragment": "consultas tipadas",
}
AGES_III_INTERNAL_TAB_REMOVAL_POLICY = {
    "authorization_evidence": AGES_III_INTERNAL_TAB_REMOVAL_AUTHORIZATION,
    "source_ids": ["text-p-1084"],
    "source_fragment": "consultas t\tipadas",
    "target_fragment": "consultas tipadas",
}
AGES_IV_AUTHORIZATION = "migration/approvals/ages-iv-partial-authorization.json"
AGES_IV_UNITS = (
    "chapter-06-text-h-0105", "chapter-06-text-h-0106", "chapter-06-text-h-0107",
    "chapter-06-text-h-0108", "chapter-06-text-h-0109", "chapter-06-text-h-0110",
    "chapter-06-text-h-0112", "chapter-06-text-h-0113", "chapter-06-text-h-0114",
    "chapter-06-text-h-0115", "ages-iv-sprint-0", "ages-iv-sprint-1",
    "ages-iv-sprint-2", "ages-iv-sprint-3", "ages-iv-sprint-4",
    "chapter-06-text-h-0122", "chapter-07-text-h-0123",
)
AGES_IV_LINKED_FIGURE = {
    "unit_id": "chapter-06-text-h-0109",
    "image_id": "draw-image-0025",
    "caption_id": "text-p-1344",
    "link_id": "text-a-0149",
    "paragraph_id": "text-p-1343",
    "frame_id": "draw-frame-0065",
    "textbox_id": "draw-text-box-0041",
    "image_frame_id": "draw-frame-0066",
    "macro_path": "relatorio_AGES_eduardo/util/figure-macros.tex",
}
AGES_IV_TITLE_ONLY_UNIT = "chapter-07-text-h-0123"
AGES_IV_TITLE_ONLY_HEADING_ID = "text-h-0123"
AGES_IV_TITLE_ONLY_OMITTED_IDS = (
    "text-p-1539", "text-p-1540", "text-p-1541", "text-list-0280",
    "text-list-item-0225", "text-p-1542", "text-list-0281", "text-list-item-0226",
    "text-p-1543", "text-list-item-0227", "text-p-1544", "text-list-item-0228",
    "text-p-1545", "text-list-item-0229", "text-p-1546", "text-list-item-0230",
    "text-p-1547", "text-p-1549",
)
FRONTMATTER_AUTHORIZATION = "migration/approvals/ages-iv-frontmatter-authorization.json"
FRONTMATTER_UNITS = ("pretext", "resumo", "chapter-01-text-h-0001")
DOCUMENT_ORDER_AUTHORIZATION = "migration/approvals/cliente-hoortech-and-document-order-authorization.json"
HOORTECH_UNITS = (
    "chapter-03-text-h-0023", "chapter-03-text-h-0024", "chapter-03-text-h-0025",
    "chapter-03-text-h-0026", "cliente-hoortech-sprint-0", "cliente-hoortech-sprint-1",
    "cliente-hoortech-sprint-2", "cliente-hoortech-sprint-3", "cliente-hoortech-sprint-4",
    "chapter-03-text-h-0038",
)
DOCUMENT_ORDER_BASELINE = "8f952a6e3b64c8783cef823e52ed2451af653eae"
DOCUMENT_ORDER_SOURCE_SHA256 = "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"
AGES_IV_SPRINT2_USER_CONTENT_AUTHORIZATION = "migration/approvals/ages-iv-sprint-2-content-authorization.json"
AGES_IV_SPRINT2_USER_CONTENT_IDS = (
    "user-ages-iv-sprint-2-report-p01",
    "user-ages-iv-sprint-2-report-p02",
    "user-ages-iv-sprint-2-report-p03",
    "user-ages-iv-sprint-2-report-p04",
    "user-ages-iv-sprint-2-report-p05",
    "user-ages-iv-sprint-2-reflection-p01",
    "user-ages-iv-sprint-2-reflection-p02",
)
FRONTMATTER_TRANSFORM_IDS = {
    "frontmatter_title": {"text-p-0003", "text-p-0004", "text-p-0017", "text-p-0018", "text-p-0034", "text-p-0068"},
    "frontmatter_placeholder": {"text-p-0097"},
    "frontmatter_omission": {
        "text-p-0062", "text-p-0064", "text-p-0066", "text-p-0067", "text-p-0091",
        "text-p-0092", "text-p-0094", "text-p-0099", "text-p-0101", "text-p-0139",
        "text-p-0278", "text-p-0279",
    },
}
FRONTMATTER_LAYOUT_CONTROLS = {
    "resumo": [
        {
            "command": "clearpage",
            "after_source_id": "text-p-0097",
            "before_command": "listoffigures",
            "reason": "Manter o resumo em página própria como na estrutura de referência da Mariah e iniciar a lista de ilustrações na página seguinte.",
        },
        {
            "command": "clearpage",
            "after_unit_input": "conteudo/migracao/lista-de-siglas.tex",
            "before": "tableofcontents",
            "reason": "Manter o sumário em página própria após a lista de siglas, como na estrutura de referência da Mariah e na ordem definida pelo usuário.",
        },
    ],
}

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
    "text-p-1027": ("Figure 16: ", "Figura 16 – "),
    "text-p-1042": ("Figure 17: ", "Figura 17 – "),
    "text-p-1051": ("Figure 18: ", "Figura 18 – "),
    "text-p-1058": ("Figure 19: ", "Figura 19 – "),
    "text-p-1059": ("Figure 20: ", "Figura 20 – "),
    "text-p-1060": ("Figure 21: ", "Figura 21 – "),
    "text-p-1063": ("Figure 22: ", "Figura 22 – "),
    "text-p-1064": ("Figure 23: ", "Figura 23 – "),
    "text-p-1329": ("Figure 24: ", "Figura 24 – "),
    "text-p-1344": ("Figure 25: ", "Figura 25 – "),
    "text-p-1350": ("Figure 26: ", "Figura 26 – "),
    "text-p-1378": ("Figure 27: ", "Figura 27 – "),
    "text-p-1385": ("Figure 28: ", "Figura 28 – "),
    "text-p-1387": ("Figure 29: ", "Figura 29 – "),
    "text-p-1392": ("Figure 30: ", "Figura 30 – "),
    "text-p-1450": ("Figure 31: ", "Figura 31 – "),
    "text-p-1455": ("Figure 32: ", "Figura 32 – "),
    "text-p-1475": ("Figure 33: ", "Figura 33 – "),
    "text-p-1478": ("Figure 34: ", "Figura 34 – "),
}
PRESENTATION_HEADINGS = {
    "text-h-0002": ("2 - PROJETO AGES I – EASY CHOOSE", "2 PROJETO AGES I – EASY CHOOSE"),
    "text-h-0022": ("2.4. Conclusão", "2.4 Conclusão"),
    "text-h-0039": ("4 - PROJETO AGES II – INDÚSTRIA DIGITAL", "4 PROJETO AGES II – INDÚSTRIA DIGITAL"),
    "text-h-0073": ("4.4. Conclusão", "4.4 Conclusão"),
    "text-h-0074": (
        "5 - PROJETOS AGES III – SISTEMA DE CONTROLE INTELIGENTE DE ESTACIONAMENTO COM RFID",
        "5 PROJETOS AGES III – SISTEMA DE CONTROLE INTELIGENTE DE ESTACIONAMENTO COM RFID",
    ),
    "text-h-0097": ("5.4. Conclusão", "5.4 Conclusão"),
    "text-h-0105": ("6 - PROJETOS AGES IV - RECORDA ", "6 PROJETOS AGES IV - RECORDA "),
    "text-h-0122": ("6.4. Conclusão", "6.4 Conclusão"),
    "text-h-0123": (
        "7 - CONSIDERAÇÕES FINAIS (Somente AGES IV)",
        "7 CONSIDERAÇÕES FINAIS (Somente AGES IV)",
    ),
}
AGES_IV_CAPTION_IDS = frozenset({
    "text-p-1329", "text-p-1344", "text-p-1350", "text-p-1378", "text-p-1385",
    "text-p-1387", "text-p-1392", "text-p-1450", "text-p-1455", "text-p-1475",
    "text-p-1478",
})
AGES_IV_HEADING_IDS = frozenset({"text-h-0105", "text-h-0122", "text-h-0123"})
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
    "text-a-0129": {"href": "https://tools.ages.pucrs.br/sistema-de-controle-inteligente-de-estacionamento-com-rfid/frontend", "source_anchor": "Repositório RFID Frontend", "prefix": "Mais informações podem ser encontradas no repositório ", "anchor": "RFID Frontend", "suffix": "."},
    "text-a-0130": {"href": "https://tools.ages.pucrs.br/sistema-de-controle-inteligente-de-estacionamento-com-rfid/backend", "source_anchor": "Repositório RFID Backend", "prefix": "Mais informações podem ser encontradas no repositório ", "anchor": "RFID Backend", "suffix": "."},
    "text-a-0131": {"href": "https://tools.ages.pucrs.br/sistema-de-controle-inteligente-de-estacionamento-com-rfid/gateway", "source_anchor": "Repositório RFID Gateway", "prefix": "Mais informações podem ser encontradas no repositório ", "anchor": "RFID Gateway", "suffix": "."},
    "text-a-0146": {"href": "https://tools.ages.pucrs.br/2026-2/2jk-4jk/recorda/frontend", "source_anchor": "Repositório Recorda Frontend", "prefix": "Mais informações podem ser encontradas no repositório ", "anchor": "Recorda Frontend", "suffix": "."},
    "text-a-0147": {"href": "https://tools.ages.pucrs.br/2026-2/2jk-4jk/recorda/backend", "source_anchor": "Repositório Recorda Backend", "prefix": "Mais informações podem ser encontradas no repositório ", "anchor": "Recorda Backend", "suffix": "."},
}
PRESENTATION_REPOSITORY_PARAGRAPHS = {
    "text-p-0304": "text-a-0105",
    "text-p-0307": "text-a-0106",
    "text-p-0310": "text-a-0107",
    "text-p-0775": "text-a-0116",
    "text-p-0778": "text-a-0117",
    "text-p-1030": "text-a-0129",
    "text-p-1033": "text-a-0130",
    "text-p-1036": "text-a-0131",
    "text-p-1333": "text-a-0146",
    "text-p-1336": "text-a-0147",
}
AGES_III_WIKI_SENTENCES = {
    "text-p-1043": {
        "source_id": "text-a-0132",
        "source_anchor": "Wiki do Banco de Dados",
        "href": "https://tools.ages.pucrs.br/sistema-de-controle-inteligente-de-estacionamento-com-rfid/impinj-rfid-wiki/-/wikis/Banco%20de%20Dados",
        "prefix": "Mais detalhes podem ser encontrados aqui: ",
        "anchor": "Banco de Dados",
        "suffix": "",
        "leading_tabs": 0,
    },
}
AGES_IV_WIKI_SENTENCES = {
    "text-p-1343": {
        "source_id": "text-a-0149",
        "source_anchor": "Wiki do Banco de Dados",
        "href": "https://tools.ages.pucrs.br/2026-2/2jk-4jk/recorda/wiki/-/wikis/Banco%20de%20Dados",
        "prefix": "Mais detalhes podem ser encontrados aqui: ",
        "anchor": "Banco de Dados",
        "suffix": "",
        "leading_tabs": 0,
    },
    "text-p-1362": {
        "source_id": "text-a-0151",
        "source_anchor": "Wiki da Arquitetura",
        "href": "https://tools.ages.pucrs.br/2026-2/2jk-4jk/recorda/wiki/-/wikis/arquitetura",
        "prefix": "Mais informações sobre a arquitetura estão disponíveis em: ",
        "anchor": "Arquitetura",
        "suffix": "",
        "leading_tabs": 0,
    },
    "text-p-1393": {
        "source_id": "text-a-0152",
        "source_anchor": "Wiki de Design/Mockups",
        "href": "https://tools.ages.pucrs.br/2026-2/2jk-4jk/recorda/wiki/-/wikis/design_mockups",
        "prefix": "Os mockups de cada tela podem ser visualizados no seguinte link: ",
        "anchor": "Protótipo das Telas",
        "suffix": "",
        "leading_tabs": 0,
    },
}
AGES_IV_REPOSITORY_UNITS = {
    "chapter-06-text-h-0108": {
        "text-p-1333", "text-a-0146", "text-p-1336", "text-a-0147",
    },
}
AGES_IV_WIKI_UNITS = {
    "chapter-06-text-h-0109": {"text-p-1343", "text-a-0149"},
    "chapter-06-text-h-0110": {"text-p-1362", "text-a-0151"},
    "chapter-06-text-h-0112": {"text-p-1393", "text-a-0152"},
}
AGES_IV_TECHNICAL_CITATIONS = {
    "chapter-06-text-h-0108": {
        "text-p-1332": ["ages-iv-app-store"],
    },
    "chapter-06-text-h-0109": {
        "text-p-1339": ["ages-iv-postgresql", "ages-iv-supabase"],
    },
    "chapter-06-text-h-0110": {
        "text-p-1347": [
            "ages-iv-react-native", "ages-iv-expo", "ages-iv-tanstack-query", "ages-iv-python", "ages-iv-fastapi",
            "ages-iv-docker", "ages-iv-pydantic", "ages-iv-supabase", "ages-iv-github-actions",
            "ages-iv-sonar", "ages-iv-pytest", "ages-iv-jest",
        ],
    },
}
AGES_IV_CITATION_TERMS = {
    "text-p-1332": ["App Store"],
    "text-p-1339": ["PostgreSQL", "Supabase"],
    "text-p-1347": [
        "React Native", "Expo", "TanStack Query", "Python", "FastAPI", "Docker", "Pydantic", "Supabase",
        "GitHub Actions", "SonarCloud", "Pytest", "Jest",
    ],
}
AGES_IV_CITATION_EVIDENCE = {
    "ages-iv-app-store": "app_store",
    "ages-iv-tanstack-query": "tanstack_query",
    "ages-iv-python": "python",
    "ages-iv-fastapi": "fastapi",
    "ages-iv-pydantic": "pydantic",
    "ages-iv-react-native": "react_native",
    "ages-iv-expo": "expo",
    "ages-iv-supabase": "supabase",
    "ages-iv-postgresql": "postgresql",
    "ages-iv-docker": "docker",
    "ages-iv-github-actions": "github_actions",
    "ages-iv-sonar": "sonar",
    "ages-iv-pytest": "pytest",
    "ages-iv-jest": "jest",
}
AGES_IV_SUPPLEMENTAL_CITATION_AUTHORIZATION = "migration/approvals/ages-iv-supplemental-citations-authorization.json"
AGES_IV_SUPPLEMENTAL_CITATIONS = {
    "ages-iv-app-store": {
        "unit_id": "chapter-06-text-h-0108",
        "source_record_id": "text-p-1332",
        "evidence_id": "app_store",
        "term": "App Store",
        "url": "https://developer.apple.com/app-store/",
    },
    "ages-iv-tanstack-query": {
        "unit_id": "chapter-06-text-h-0110",
        "source_record_id": "text-p-1347",
        "evidence_id": "tanstack_query",
        "term": "TanStack Query",
        "url": "https://tanstack.com/query/latest/docs/framework/react/guides/does-this-replace-client-state",
    },
}
AGES_IV_TECHNICAL_CITATION_KEYS = set(AGES_IV_CITATION_EVIDENCE)
AGES_IV_TECHNICAL_TEXT_IDS = frozenset(
    source_id for unit_map in AGES_IV_TECHNICAL_CITATIONS.values() for source_id in unit_map
)
AGES_III_REPOSITORY_UNITS = {
    "chapter-05-text-h-0077": {
        "text-p-1030", "text-a-0129", "text-p-1033", "text-a-0130", "text-p-1036", "text-a-0131",
    },
}
AGES_III_WIKI_UNITS = {"chapter-05-text-h-0078": {"text-p-1043", "text-a-0132"}}
AGES_III_TECHNOLOGY_TEXT_IDS = (
    "text-p-1066", "text-p-1067", "text-p-1069", "text-p-1070", "text-p-1072",
    "text-p-1073", "text-p-1074", "text-p-1076", "text-p-1077", "text-p-1078",
    "text-p-1080", "text-p-1081", "text-p-1083", "text-p-1084", "text-p-1085",
    "text-p-1087", "text-p-1088", "text-p-1090", "text-p-1091", "text-p-1093",
    "text-p-1094", "text-p-1096", "text-p-1097", "text-p-1099", "text-p-1100",
    "text-p-1102", "text-p-1103", "text-p-1105", "text-p-1106",
)
AGES_III_TECHNOLOGY_NARRATIVE_TEXT_IDS = (
    "text-p-1066", "text-p-1069", "text-p-1072", "text-p-1073",
    "text-p-1076", "text-p-1077", "text-p-1080", "text-p-1083",
    "text-p-1084", "text-p-1087", "text-p-1090", "text-p-1093",
    "text-p-1096", "text-p-1099", "text-p-1102", "text-p-1105",
)
AGES_III_TECHNOLOGY_PARAGRAPH_BOUNDARIES = tuple(
    zip(AGES_III_TECHNOLOGY_TEXT_IDS, AGES_III_TECHNOLOGY_TEXT_IDS[1:])
)
# The ODT has two source paragraphs with one explicit trailing space, already
# represented by originalspace. The other 26 paragraph boundaries need one
# approved interword space when the list is presented as a single paragraph.
AGES_III_TECHNOLOGY_SOURCE_TRAILING_SPACE_IDS = {"text-p-1069", "text-p-1087"}
AGES_III_TECHNOLOGY_INSERTED_SEPARATOR_SOURCE_IDS = tuple(
    left_id for left_id, _ in AGES_III_TECHNOLOGY_PARAGRAPH_BOUNDARIES
    if left_id not in AGES_III_TECHNOLOGY_SOURCE_TRAILING_SPACE_IDS
)
# Every source paragraph except the final link paragraph participates in the
# one-paragraph presentation: line breaks become spaces and/or a boundary
# separator is added. The exact output is checked against the source below.
AGES_III_TECHNOLOGY_PARAGRAPH_JOIN_SOURCE_IDS = frozenset(AGES_III_TECHNOLOGY_TEXT_IDS[:-1])
AGES_III_TECHNOLOGY_JOIN_POLICY = {
    "authorization_evidence": AGES_III_TECHNOLOGY_NARRATIVE_AUTHORIZATION,
    "source_ids": list(AGES_III_TECHNOLOGY_TEXT_IDS[:-1]),
    "space_boundaries": [
        {"left_source_id": left_id, "right_source_id": right_id}
        for left_id, right_id in AGES_III_TECHNOLOGY_PARAGRAPH_BOUNDARIES
    ],
    "inserted_separator_source_ids": list(AGES_III_TECHNOLOGY_INSERTED_SEPARATOR_SOURCE_IDS),
}
AGES_III_TECHNOLOGY_LINK_IDS = tuple(f"text-a-{number:04d}" for number in range(133, 146))
AGES_III_TECHNOLOGY_ELEMENT_IDS = tuple(
    rid for rid in (
        "text-p-1066", "text-p-1067", "text-a-0133", "text-p-1069", "text-p-1070", "text-a-0134",
        "text-p-1072", "text-p-1073", "text-p-1074", "text-a-0135", "text-p-1076", "text-p-1077",
        "text-p-1078", "text-a-0136", "text-p-1080", "text-p-1081", "text-a-0137", "text-p-1083",
        "text-p-1084", "text-p-1085", "text-a-0138", "text-p-1087", "text-p-1088", "text-a-0139",
        "text-p-1090", "text-p-1091", "text-a-0140", "text-p-1093", "text-p-1094", "text-a-0141",
        "text-p-1096", "text-p-1097", "text-a-0142", "text-p-1099", "text-p-1100", "text-a-0143",
        "text-p-1102", "text-p-1103", "text-a-0144", "text-p-1105", "text-p-1106", "text-a-0145",
    )
)
AGES_III_TECHNICAL_CITATIONS = {
    "chapter-05-text-h-0075": {
        "text-p-1022": ["ages-iii-rfid-parking-use-cases"],
        "text-p-1024": ["ages-iii-impinj-r700"],
    },
    "chapter-05-text-h-0077": {
        "text-p-1032": ["ages-iii-aws-lambda"],
        "text-p-1035": ["ages-iii-fielding-rest"],
    },
    "chapter-05-text-h-0078": {
        "text-p-1039": ["ages-iii-postgresql", "ages-iii-rds", "ages-iii-rfid-nist"],
    },
    "chapter-05-text-h-0079": {
        "text-p-1046": ["ages-iii-s3", "ages-iii-cloudfront", "ages-iii-dotnet", "ages-iii-aws-lambda"],
        "text-p-1047": ["ages-iii-postgresql", "ages-iii-rds", "ages-iii-rfid-nist", "ages-iii-aws-iot-core", "ages-iii-mqtt"],
        "text-p-1048": ["ages-iii-rfid-nist", "ages-iii-dotnet"],
        "text-p-1049": ["ages-iii-github-actions", "ages-iii-gitlab"],
    },
    "chapter-05-text-h-0080": {"text-p-1053": ["ages-iii-figma"]},
    "chapter-05-text-h-0085": {
        "text-p-1066": ["ages-iii-csharp", "ages-iii-dotnet"],
        "text-p-1069": ["ages-iii-dotnet"],
        "text-p-1072": ["ages-iii-react"],
        "text-p-1076": ["ages-iii-typescript"],
        "text-p-1077": ["ages-iii-javascript"],
        "text-p-1083": ["ages-iii-entity-framework"],
        "text-p-1084": ["ages-iii-dotnet"],
        "text-p-1087": ["ages-iii-aws-lambda"],
        "text-p-1090": ["ages-iii-s3"],
        "text-p-1093": ["ages-iii-cloudfront"],
        "text-p-1096": ["ages-iii-rds", "ages-iii-postgresql"],
        "text-p-1099": ["ages-iii-postgresql"],
        "text-p-1102": ["ages-iii-docker"],
        "text-p-1080": ["ages-iii-impinj-iot-interface", "ages-iii-rfid-nist"],
        "text-p-1105": ["ages-iii-github-actions", "ages-iii-gitlab"],
    },
}
AGES_III_PENDING_CITATIONS = {
    "chapter-05-text-h-0085": {"text-p-1080": ["text-a-0137"]},
}
AGES_III_TECHNICAL_CITATION_KEYS = {
    key for per_unit in AGES_III_TECHNICAL_CITATIONS.values()
    for keys in per_unit.values() for key in keys
}
AGES_III_CITATION_EVIDENCE = {
    "ages-iii-csharp": ("text-a-0133", None),
    "ages-iii-dotnet": ("text-a-0134", None),
    "ages-iii-react": ("text-a-0135", None),
    "ages-iii-typescript": ("text-a-0136", None),
    "ages-iii-entity-framework": ("text-a-0138", None),
    "ages-iii-aws-lambda": ("text-a-0139", None),
    "ages-iii-s3": ("text-a-0140", None),
    "ages-iii-cloudfront": ("text-a-0141", None),
    "ages-iii-rds": ("text-a-0142", None),
    "ages-iii-postgresql": ("text-a-0143", None),
    "ages-iii-docker": ("text-a-0144", None),
    "ages-iii-github-actions": ("text-a-0145", None),
    "ages-iii-aws-iot-core": (None, "ages-iii-supplement-aws-iot-core"),
    "ages-iii-mqtt": (None, "ages-iii-supplement-mqtt"),
    "ages-iii-gitlab": (None, "ages-iii-supplement-gitlab"),
    "ages-iii-figma": (None, "ages-iii-supplement-figma"),
    "ages-iii-javascript": (None, "ages-iii-supplement-javascript"),
    "ages-iii-rfid-nist": (None, "ages-iii-supplement-rfid"),
    "ages-iii-rfid-parking-use-cases": (None, "ages-iii-supplement-rfid-parking-use-cases"),
    "ages-iii-impinj-r700": (None, "ages-iii-supplement-impinj-r700"),
    "ages-iii-impinj-iot-interface": (None, "ages-iii-supplement-impinj-r700"),
    "ages-iii-fielding-rest": (None, "ages-iii-supplement-rest-fielding"),
}
AGES_III_CITATION_EVIDENCE_SOURCE_INDEX = {"ages-iii-impinj-iot-interface": 1}
AGES_III_CITATION_TYPES = {"ages-iii-fielding-rest": "thesis"}
AGES_III_BIBLIOGRAPHY_REQUIRED_FIELDS = {
    "ages-iii-fielding-rest": {
        "author": "Fielding, Roy Thomas",
        "type": "Doctoral dissertation in Information and Computer Science",
        "institution": "University of California, Irvine",
    },
}
AGES_III_CITATION_TERMS = {
    "text-p-1022": ["estacionamentos corporativos"],
    "text-p-1024": ["Impinj R700"],
    "text-p-1032": ["AWS Lambda"],
    "text-p-1035": ["API RESTful"],
    "text-p-1039": ["PostgreSQL", "Amazon RDS", "RFID"],
    "text-p-1046": ["Amazon S3", "Cloudfront", ".NET", "AWS Lambda"],
    "text-p-1047": ["PostgreSQL", "Amazon RDS", "RFID", "Amazon IoT Core", "MQTT"],
    "text-p-1048": ["RFID", ".NET"],
    "text-p-1049": ["integração contínua", "GitLab"],
    "text-p-1053": ["Figma"],
    "text-p-1066": ["C#", ".NET"],
    "text-p-1069": [".NET"],
    "text-p-1072": ["React"],
    "text-p-1076": ["TypeScript"],
    "text-p-1077": ["JavaScript"],
    "text-p-1080": ["Impinj R700 REST API", "RFID"],
    "text-p-1083": ["Entity Framework"],
    "text-p-1084": [".NET"],
    "text-p-1087": ["AWS Lambda"],
    "text-p-1090": ["Amazon S3"],
    "text-p-1093": ["CloudFront"],
    "text-p-1096": ["Amazon RDS", "PostgreSQL"],
    "text-p-1099": ["PostgreSQL"],
    "text-p-1102": ["Docker"],
    "text-p-1105": ["GitHub Actions", "GitLab"],
}
PRESENTATION_AUTHORIZATION_BY_UNIT = {
    **{uid: PRESENTATION_AUTHORIZATION for uid in REFERENCE_LAYOUT_UNITS},
    **{uid: AGES_II_PRESENTATION_AUTHORIZATION for uid in AGES_II_UNITS},
    **{uid: AGES_III_AUTHORIZATION for uid in AGES_III_UNITS},
    **{uid: AGES_IV_AUTHORIZATION for uid in AGES_IV_UNITS},
    **{uid: FRONTMATTER_AUTHORIZATION for uid in FRONTMATTER_UNITS},
}
PRESENTATION_SERIALIZATIONS = {
    "abnt_figure_caption": set(PRESENTATION_CAPTIONS),
    "abnt_section_numbering": set(PRESENTATION_HEADINGS),
    "approved_figure_cross_reference": set(PRESENTATION_CROSS_REFERENCES),
    "repository_link_sentence": set(PRESENTATION_REPOSITORY_LINKS) | set(PRESENTATION_REPOSITORY_PARAGRAPHS),
    "approved_group_label_removal": set(AGES_III_PROTOTYPE_GROUP_LABELS),
    "approved_technology_narrative": set(AGES_III_TECHNOLOGY_NARRATIVE_TEXT_IDS),
    "technology_documentation_link_prose": set(AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_TEXT_IDS),
    "approved_internal_tab_removal": {"text-p-1084"},
    # Validated against the exact per-record scope in the supplemental
    # document-order authorization, not a reusable generic serialization.
    "document_reordering_numbering": set(),
    **FRONTMATTER_TRANSFORM_IDS,
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
PRESENTATION_OVERRIDES_BY_UNIT.update({
    "chapter-05-text-h-0074": {"text-h-0074"},
    "chapter-05-text-h-0075": {"text-p-1027"},
    "chapter-05-text-h-0077": AGES_III_REPOSITORY_UNITS["chapter-05-text-h-0077"],
    "chapter-05-text-h-0078": (
        {"text-p-1042"} | AGES_III_WIKI_UNITS["chapter-05-text-h-0078"]
    ),
    "chapter-05-text-h-0079": {"text-p-1051"},
    "chapter-05-text-h-0080": {
        "text-p-1058", "text-p-1059", "text-p-1060", "text-p-1063", "text-p-1064",
        "text-p-1056", "text-h-0084",
    },
    # The full technology paragraph includes the original link anchors as
    # well as the text records between the joined source paragraphs.
    "chapter-05-text-h-0085": set(AGES_III_TECHNOLOGY_ELEMENT_IDS),
    "chapter-05-text-h-0097": {"text-h-0097"},
})
PRESENTATION_OVERRIDES_BY_UNIT.update({
    "chapter-06-text-h-0105": {"text-h-0105"},
    "chapter-06-text-h-0106": {"text-p-1329"},
    "chapter-06-text-h-0108": AGES_IV_REPOSITORY_UNITS["chapter-06-text-h-0108"],
    "chapter-06-text-h-0109": {"text-p-1344"} | AGES_IV_WIKI_UNITS["chapter-06-text-h-0109"],
    "chapter-06-text-h-0110": {"text-p-1350"} | AGES_IV_WIKI_UNITS["chapter-06-text-h-0110"],
    "chapter-06-text-h-0112": {"text-p-1378", "text-p-1385", "text-p-1387", "text-p-1392"} | AGES_IV_WIKI_UNITS["chapter-06-text-h-0112"],
    "chapter-06-text-h-0114": {"text-p-1450", "text-p-1455"},
    "ages-iv-sprint-0": {"text-p-1475", "text-p-1478"},
    "chapter-06-text-h-0122": {"text-h-0122"},
    "chapter-07-text-h-0123": {"text-h-0123"},
})
PRESENTATION_OVERRIDES_BY_UNIT.update({
    "pretext": {
        "text-p-0003", "text-p-0004", "text-p-0017", "text-p-0018",
        "text-p-0034", "text-p-0062", "text-p-0064", "text-p-0066", "text-p-0067",
        "text-p-0068", "text-p-0091", "text-p-0092", "text-p-0094",
    },
    "resumo": {"text-p-0097", "text-p-0099", "text-p-0101", "text-p-0139"},
    "chapter-01-text-h-0001": {"text-p-0278", "text-p-0279"},
})
AGES_III_PRESENTATION_SOURCE_IDS = frozenset(
    source_id for unit_id in AGES_III_UNITS
    for source_id in PRESENTATION_OVERRIDES_BY_UNIT.get(unit_id, set())
) | frozenset(AGES_III_TECHNOLOGY_ELEMENT_IDS)

# Narrow evidence-based additions authorized on 2026-10-16 for six wiki links
# and technology citations in the database/architecture/prototype passages.
AGES_I_II_FORMATTING_AUTHORIZATION = "migration/approvals/ages-i-ii-formatting-authorization.json"
AGES_I_II_WIKI_SENTENCES = {
    "text-p-0315": {
        "source_id": "text-a-0108", "source_anchor": "Wiki do Banco de Dados",
        "href": "https://tools.ages.pucrs.br/easy-choose/wiki/-/wikis/Banco%20de%20Dados",
        "prefix": "Mais detalhes podem ser encontrados aqui: ", "anchor": "Banco de Dados", "suffix": "", "leading_tabs": 1,
    },
    "text-p-0319": {
        "source_id": "text-a-0109", "source_anchor": "Wiki da Arquitetura",
        "href": "https://tools.ages.pucrs.br/easy-choose/wiki/-/wikis/arquitetura",
        "prefix": "Mais informações sobre a arquitetura estão disponíveis em: ", "anchor": "Arquitetura", "suffix": "", "leading_tabs": 1,
    },
    "text-p-0323": {
        "source_id": "text-a-0110", "source_anchor": "Wiki dos Protótipos",
        "href": "https://tools.ages.pucrs.br/easy-choose/wiki/-/wikis/design_mockups",
        "prefix": "Os mockups de cada tela podem ser visualizados no seguinte link: ", "anchor": "Protótipo das Telas", "suffix": "", "leading_tabs": 0,
    },
    "text-p-0782": {
        "source_id": "text-a-0118", "source_anchor": "Wiki do Banco de Dados",
        "href": "https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Banco%20de%20dados",
        "prefix": "Mais detalhes podem ser encontrados aqui: ", "anchor": "Banco de Dados", "suffix": "", "leading_tabs": 0,
    },
    "text-p-0789": {
        "source_id": "text-a-0120", "source_anchor": "Wiki da Arquitetura",
        "href": "https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Arquitetura",
        "prefix": "Mais informações sobre a arquitetura estão disponíveis em: ", "anchor": "Arquitetura", "suffix": "", "leading_tabs": 0,
    },
    "text-p-0793": {
        "source_id": "text-a-0121", "source_anchor": "Wiki dos Protótipos",
        "href": "https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Mockups",
        "prefix": "Os mockups de cada tela podem ser visualizados no seguinte link: ", "anchor": "Protótipo das Telas", "suffix": "", "leading_tabs": 0,
    },
}
AGES_I_II_FORMATTING_UNITS = {
    "chapter-02-text-h-0009", "chapter-02-text-h-0010", "chapter-02-text-h-0011",
    "chapter-04-text-h-0043", "chapter-04-text-h-0044", "chapter-04-text-h-0045",
    "chapter-04-text-h-0046",
}
AGES_I_II_WIKI_UNITS = {
    "chapter-02-text-h-0009": {"text-p-0315", "text-a-0108"},
    "chapter-02-text-h-0010": {"text-p-0319", "text-a-0109"},
    "chapter-02-text-h-0011": {"text-p-0323", "text-a-0110"},
    "chapter-04-text-h-0043": {"text-p-0782", "text-a-0118"},
    "chapter-04-text-h-0044": {"text-p-0789", "text-a-0120"},
    "chapter-04-text-h-0045": {"text-p-0793", "text-a-0121"},
}
AGES_I_II_TECHNICAL_CITATIONS = {
    "chapter-02-text-h-0009": {"text-p-0314": ["postgresql-docs", "prisma-docs"]},
    "chapter-02-text-h-0011": {"text-p-0322": ["ages-i-excalidraw", "ages-i-figma"]},
    "chapter-04-text-h-0043": {"text-p-0781": ["ages-ii-postgresql", "ages-ii-sqlalchemy"]},
    "chapter-04-text-h-0044": {"text-p-0785": [
        "ages-ii-angular", "ages-ii-http-rfc9110", "ages-ii-fastapi", "ages-ii-fastapi",
        "ages-ii-postgresql", "ages-ii-postgresql", "ages-ii-json-rfc8259", "ages-ii-angular",
    ]},
    "chapter-04-text-h-0045": {"text-p-0791": ["ages-ii-figma"]},
    "chapter-04-text-h-0046": {
        "text-p-0812": ["ages-ii-angular", "ages-ii-typescript"],
        "text-p-0813": ["ages-ii-typescript", "ages-ii-angular", "ages-ii-http-rfc9110", "ages-ii-json-rfc8259"],
        "text-p-0817": ["ages-ii-python"],
        "text-p-0818": ["ages-ii-graph-api", "ages-ii-python", "ages-ii-fastapi"],
        "text-p-0821": ["ages-ii-fastapi"],
        "text-p-0822": ["ages-ii-angular", "ages-ii-postgresql"],
        "text-p-0825": ["ages-ii-graph-api"],
        "text-p-0829": ["ages-ii-sqlalchemy"],
        "text-p-0830": ["ages-ii-postgresql", "ages-ii-python"],
        "text-p-0833": ["ages-ii-postgresql"],
        "text-p-0834": ["ages-ii-fastapi", "ages-ii-sqlalchemy"],
        "text-p-0837": ["ages-ii-docker"],
        "text-p-0838": ["ages-ii-postgresql"],
    },
}
AGES_I_II_TECHNICAL_CITATION_KEYS = {
    key for per_unit in AGES_I_II_TECHNICAL_CITATIONS.values()
    for keys in per_unit.values() for key in keys
}
PRESENTATION_SERIALIZATIONS.update({
    "wiki_reference_sentence": (
        set(AGES_I_II_WIKI_SENTENCES)
        | {rule["source_id"] for rule in AGES_I_II_WIKI_SENTENCES.values()}
        | set(AGES_III_WIKI_SENTENCES)
        | {rule["source_id"] for rule in AGES_III_WIKI_SENTENCES.values()}
        | set(AGES_IV_WIKI_SENTENCES)
        | {rule["source_id"] for rule in AGES_IV_WIKI_SENTENCES.values()}
    ),
    "technology_citation": (
        {source_id for unit_map in AGES_I_II_TECHNICAL_CITATIONS.values() for source_id in unit_map}
        | {source_id for unit_map in AGES_III_TECHNICAL_CITATIONS.values() for source_id in unit_map}
        | AGES_IV_TECHNICAL_TEXT_IDS
    ),
    "technology_paragraph_join": set(AGES_III_TECHNOLOGY_INSERTED_SEPARATOR_SOURCE_IDS),
})


def _load_base_presentation_authorization(repo: Path, unit_id: str | None = None) -> dict:
    if unit_id in FRONTMATTER_UNITS:
        authorization = json.loads((repo / FRONTMATTER_AUTHORIZATION).read_text(encoding="utf-8"))
        scope = authorization.get("scope", {})
        if (authorization.get("schema_version") != 1
                or authorization.get("record_type") != "user_authorized_frontmatter_scope"
                or authorization.get("approval_status") != "authorized_for_execution_pending_human_review"
                or authorization.get("source", {}).get("path") != "RELATORIO_ATUAL.odt"
                or authorization.get("source", {}).get("sha256") != "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"
                or authorization.get("source", {}).get("must_remain_unchanged") is not True
                or scope.get("units") != list(FRONTMATTER_UNITS)
                or set(scope.get("presentation_changes", {})) != set(FRONTMATTER_TRANSFORM_IDS)
                or scope.get("layout_controls") != FRONTMATTER_LAYOUT_CONTROLS
                or any(set(scope["presentation_changes"][kind]) != ids for kind, ids in FRONTMATTER_TRANSFORM_IDS.items())):
            raise ValueError("Frontmatter authorization is missing, stale, or exceeds the explicit supplemental scope")
        return authorization
    if unit_id in AGES_IV_UNITS:
        authorization = json.loads((repo / AGES_IV_AUTHORIZATION).read_text(encoding="utf-8"))
        expected_partial_inclusion = {
            "unit": AGES_IV_TITLE_ONLY_UNIT,
            "source_heading_id": AGES_IV_TITLE_ONLY_HEADING_ID,
            "source_heading_text": "7 - CONSIDERAÇÕES FINAIS (Somente AGES IV)",
            "included_source_record_ids": [AGES_IV_TITLE_ONLY_HEADING_ID],
            "omitted_source_record_ids": list(AGES_IV_TITLE_ONLY_OMITTED_IDS),
            "user_decision": "Incluir apenas o título",
            "treatment": "Omitir nesta entrega o corpo de orientação e seus contêineres/listas; não é uma omissão acidental. Manter rastreável para eventual redação futura.",
            "completion_state": "title included; source unit remains partial and body intentionally pending",
        }
        scope = authorization.get("scope", {})
        if (authorization.get("schema_version") != 1
                or authorization.get("record_type") != "user_authorized_partial_edition_scope"
                or authorization.get("approval_status") != "authorized_for_partial_AGES_IV_execution; chapter-07 title-only inclusion explicitly authorized; body remains intentionally omitted; human review pending"
                or authorization.get("edition") != "AGES IV / Recorda"
                or authorization.get("source", {}).get("path") != "RELATORIO_ATUAL.odt"
                or authorization.get("source", {}).get("sha256") != "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"
                or authorization.get("source", {}).get("must_remain_unchanged") is not True
                or scope.get("units") != list(AGES_IV_UNITS)
                or scope.get("title_only_partial_units") != [AGES_IV_TITLE_ONLY_UNIT]
                or scope.get("authorized_title_only_inclusion") != expected_partial_inclusion
                or authorization.get("presentation_and_preservation", {}).get("follow") != "docs/STYLE_GUIDE.md and docs/QUALITY_GATES.md"):
            raise ValueError("AGES IV presentation authorization is missing, stale, or exceeds the exact user-authorized scope")
        unit_overrides = PRESENTATION_OVERRIDES_BY_UNIT.get(unit_id, set())
        approved_changes = {
            "figure_caption_labels": {
                rid: PRESENTATION_CAPTIONS[rid][1]
                for rid in sorted(unit_overrides & AGES_IV_CAPTION_IDS)
            },
            "section_numbering": {
                rid: PRESENTATION_HEADINGS[rid][1]
                for rid in sorted(unit_overrides & AGES_IV_HEADING_IDS)
            },
            "repository_link_sentences": {
                rid: PRESENTATION_REPOSITORY_LINKS[PRESENTATION_REPOSITORY_PARAGRAPHS.get(rid, rid)]
                for rid in sorted(unit_overrides & (set(PRESENTATION_REPOSITORY_LINKS) | set(PRESENTATION_REPOSITORY_PARAGRAPHS)))
            },
            "wiki_link_sentences": {
                rid: (AGES_IV_WIKI_SENTENCES[rid] if rid in AGES_IV_WIKI_SENTENCES else next(
                    rule for rule in AGES_IV_WIKI_SENTENCES.values() if rule["source_id"] == rid
                ))
                for rid in sorted(unit_overrides & (
                    set(AGES_IV_WIKI_SENTENCES)
                    | {rule["source_id"] for rule in AGES_IV_WIKI_SENTENCES.values()}
                ))
            },
        }
        authorization = {**authorization, "approved_presentation_changes": approved_changes}
        return authorization
    if unit_id in AGES_III_UNITS:
        authorization = json.loads((repo / AGES_III_AUTHORIZATION).read_text(encoding="utf-8"))
        if (authorization.get("schema_version") != 1
                or authorization.get("record_type") != "user_authorized_edition_scope"
                or authorization.get("approval_status") != "authorized_for_AGES_III_only; final edition approval pending"
                or authorization.get("edition") != "AGES III / Sistema de Controle Inteligente de Estacionamento com RFID"
                or authorization.get("source", {}).get("path") != "RELATORIO_ATUAL.odt"
                or authorization.get("source", {}).get("sha256") != "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"
                or authorization.get("source", {}).get("must_remain_unchanged") is not True
                or authorization.get("scope", {}).get("units") != list(AGES_III_UNITS)
                or authorization.get("presentation_and_preservation", {}).get("follow") != "docs/STYLE_GUIDE.md and docs/QUALITY_GATES.md"
                or authorization.get("presentation_and_preservation", {}).get("source_text") != "preserve exact wording, punctuation, order, and semantics; no editorial revisions"):
            raise ValueError("AGES III presentation authorization is missing, stale, or exceeds its exact user-authorized edition scope")
        if unit_id == "chapter-05-text-h-0080":
            decision = json.loads((repo / AGES_III_PROTOTYPE_GROUP_LABEL_REMOVAL_AUTHORIZATION).read_text(encoding="utf-8"))
            expected_change = {
                "text-p-1056": {
                    "source_text": "Telas de Administrador:",
                    "typeset_text": "",
                    "treatment": "Omit this standalone group label from the typeset report; preserve its source text and omission evidence in the unit ledger.",
                },
                "text-h-0084": {
                    "source_text": "Telas de Cliente:",
                    "typeset_text": "",
                    "treatment": "Omit this unnumbered subordinate heading from the typeset report; preserve its source text and omission evidence in the unit ledger.",
                },
            }
            if (decision.get("schema_version") != 1
                    or decision.get("record_type") != "user_authorized_presentation_change"
                    or decision.get("date") != "2026-10-17"
                    or decision.get("user_response") != "Remover os dois rótulos (recomendado)"
                    or decision.get("scope") != {
                        "edition": "AGES III / Sistema de Controle Inteligente de Estacionamento com RFID",
                        "unit": "chapter-05-text-h-0080",
                        "source_ids": ["text-p-1056", "text-h-0084"],
                    }
                    or decision.get("change") != expected_change
                    or decision.get("approval_status") != "authorized_for_execution_pending_human_edition_review"):
                raise ValueError("AGES III prototype-label decision is missing, stale, or exceeds the user's exact unit scope")
            authorization = {
                **authorization,
                "approved_presentation_changes": {"prototype_group_label_removal": expected_change},
            }
        elif unit_id == "chapter-05-text-h-0085":
            decision = json.loads((repo / AGES_III_TECHNOLOGY_NARRATIVE_AUTHORIZATION).read_text(encoding="utf-8"))
            expected_scope = {
                "edition": "AGES III / Sistema de Controle Inteligente de Estacionamento com RFID",
                "unit": "chapter-05-text-h-0085",
                "source_ids": list(AGES_III_TECHNOLOGY_NARRATIVE_TEXT_IDS),
                "source": {
                    "path": "RELATORIO_ATUAL.odt",
                    "sha256": "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef",
                },
            }
            expected_limits = [
                "Retain every source fact, technical role, qualifier, and the order of technologies from the ODT.",
                "Only sentence connectors and grammatical recasting needed to form project-context prose are authorized; do not add capabilities, deployments, versions, or project history by inference.",
                "Preserve all 13 original documentation hyperlink URLs and anchors byte-for-byte and in source order.",
                "Present each original documentation hyperlink with the approved Mariah-style prose lead-in ‘Mais informações podem ser encontradas em:’ and a sentence-ending period; retain each original anchor and URL in place and in source order.",
                "Retain only verified, ordered author-date citations; keep the original Impinj support URL and anchor as PENDING, distinct from any separately verified citation source.",
                "Preserve the original internal tab in `consultas t<TAB>ipadas`; do not silently repair source wording or whitespace.",
            ]
            expected_documentation_link_presentation = {
                "source_ids": list(AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_TEXT_IDS),
                "prefix": AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_POLICY["prefix"],
                "suffix": AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_POLICY["suffix"],
                "pattern_basis": "The user's previously approved Mariah-style narrative-link convention, applied to the retained original technology documentation links.",
            }
            if (decision.get("schema_version") != 1
                    or decision.get("record_type") != "user_authorized_scoped_content_presentation_change"
                    or decision.get("date") != "2026-10-17"
                    or decision.get("user_instruction") != "O tópico \"Tecnologias utilizadas\" não está seguindo os padrões. Nós combinamos de construir parágrafos explicando onde as tecnologias foram utilizadas. Você simplesmente colocou um bloco de parágrafo das tecnologias e disse o que cada uma faz, sem correlação com o projeto. Está totalmente fora do padrão."
                    or decision.get("scope") != expected_scope
                    or decision.get("approved_change", {}).get("presentation") != "Replace the separate technology labels and descriptions with one continuous narrative paragraph in the Mariah reference pattern, explicitly relating each named technology to its use in the AGES III project."
                    or decision.get("approved_change", {}).get("documentation_link_presentation") != expected_documentation_link_presentation
                    or decision.get("approved_change", {}).get("limits") != expected_limits
                    or decision.get("approved_change", {}).get("not_authorized") != [
                        "Change to any other AGES III unit or shared LaTeX style/configuration.",
                        "Editorial review, expansion, omission of source claims, or correction of project facts.",
                        "Treat semantic equivalence as proven by the automatic lexical validator.",
                    ]
                    or decision.get("review_status") != {
                        "execution": "authorized",
                        "independent_content_audit": "pending",
                        "visual_audit": "pending",
                        "human_approval_of_final_AGES_III_edition": None,
                    }):
                raise ValueError("AGES III technology narrative authorization is missing, stale, or exceeds its exact user-authorized unit scope")
            tab_decision = json.loads((repo / AGES_III_INTERNAL_TAB_REMOVAL_AUTHORIZATION).read_text(encoding="utf-8"))
            expected_tab_decision = {
                "schema_version": 1,
                "record_type": "user_authorized_presentation_change",
                "date": "2026-10-17",
                "basis": "The user selected removal of only the internal tab after reviewing that it renders a space inside the word in the PDF.",
                "user_response": "Remover só o tab (recomendado)",
                "scope": {
                    "edition": "AGES III / Sistema de Controle Inteligente de Estacionamento com RFID",
                    "unit": "chapter-05-text-h-0085",
                    "source_ids": ["text-p-1084"],
                    "source": {
                        "path": "RELATORIO_ATUAL.odt",
                        "sha256": "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef",
                    },
                },
                "supersedes": {
                    "approval": AGES_III_TECHNOLOGY_NARRATIVE_AUTHORIZATION,
                    "limit": "Only the instruction to preserve the internal tab in text-p-1084 is superseded; all other limits remain in force.",
                },
                "change": {
                    "source_text_fragment": "consultas t\tipadas",
                    "typeset_text_fragment": "consultas tipadas",
                    "treatment": "Remove only the single tab between the existing letters ‘t’ and ‘ipadas’. Preserve every letter, all other source wording and whitespace, punctuation, citations, links, and order.",
                },
                "limits": [
                    "This authorization applies only to text-p-1084 in chapter-05-text-h-0085.",
                    "Do not alter any other tab, whitespace, wording, claim, citation, hyperlink, or unit.",
                    "Do not modify RELATORIO_ATUAL.odt.",
                    "This is a one-unit presentation correction and does not establish a general whitespace normalization rule for future projects.",
                    "Independent content and visual audits and human approval of AGES III remain pending.",
                ],
                "approval_status": "authorized_for_execution_pending_human_edition_review",
            }
            if tab_decision != expected_tab_decision:
                raise ValueError("AGES III internal-tab removal approval is missing, stale, or exceeds the user's exact unit scope")
            approved_changes = {
                "technology_narrative_rewrite": {
                    "source_ids": list(AGES_III_TECHNOLOGY_NARRATIVE_TEXT_IDS),
                    "authorization_evidence": AGES_III_TECHNOLOGY_NARRATIVE_AUTHORIZATION,
                    "independent_content_audit": "pending",
                },
                "technology_documentation_link_prose": AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_POLICY,
                "internal_tab_removal": AGES_III_INTERNAL_TAB_REMOVAL_POLICY,
            }
            authorization = {
                **authorization,
                "approved_presentation_changes": approved_changes,
                "review_status": decision["review_status"],
            }
        return authorization
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
            or changes.get("section_numbering") != {
                rid: PRESENTATION_HEADINGS[rid][1] for rid in ("text-h-0002", "text-h-0022")
            }
            or changes.get("figure_cross_references") != PRESENTATION_CROSS_REFERENCES
            or changes.get("list_markers") != PRESENTATION_LIST_MARKERS
            or authorization.get("list_marker_instruction") != PRESENTATION_LIST_MARKER_INSTRUCTION
            or authorization.get("repository_links") != {
                rid: PRESENTATION_REPOSITORY_LINKS[rid]
                for rid in ("text-a-0105", "text-a-0106", "text-a-0107")
            }):
        raise ValueError("Presentation authorization is missing, stale, or exceeds the explicit AGES I scope")
    captions = changes.get("figure_caption_labels")
    ages_i_caption_ids = {"text-p-0293", "text-p-0328", "text-p-0356", "text-p-0372", "text-p-0650"}
    if not isinstance(captions, dict) or set(captions) != ages_i_caption_ids:
        raise ValueError("Caption localization authorization does not cover exactly the five AGES I captions")
    return authorization


def _renumber_display_heading(current: str, chapter: int) -> str:
    """Change only the leading chapter component in an audited heading."""
    title = re.match(r"^(\d+)\s*-\s+(.*)$", current, re.DOTALL)
    if title:
        return f"{chapter} {title.group(2)}"
    numbered = re.match(r"^(\d+)(.*)$", current, re.DOTALL)
    if not numbered or not (numbered.group(2).startswith((".", " ", "\t")) or not numbered.group(2)):
        raise ValueError("Heading display does not begin with a standalone chapter number")
    return f"{chapter}{numbered.group(2)}"


def _load_document_order_authorization(repo: Path) -> dict:
    """Validate the narrowly authorized Hoortech relocation and its exact maps."""
    path = repo / DOCUMENT_ORDER_AUTHORIZATION
    raw_bytes = path.read_bytes()
    authorization = json.loads(raw_bytes.decode("utf-8"))
    scope = authorization.get("scope", {})
    expected_sequence = [
        {"chapter": 1, "unit": "chapter-01-text-h-0001", "title": "Apresentação da trajetória do aluno"},
        {"chapter": 2, "unit": "chapter-02-text-h-0002", "title": "AGES I"},
        {"chapter": 3, "unit": "chapter-04-text-h-0039", "title": "AGES II"},
        {"chapter": 4, "unit": "chapter-05-text-h-0074", "title": "AGES III"},
        {"chapter": 5, "unit": "chapter-06-text-h-0105", "title": "AGES IV"},
        {"chapter": 6, "unit": "chapter-03-text-h-0023", "title": "Participação como cliente Hoortech"},
        {"chapter": 7, "unit": "chapter-07-text-h-0123", "title": "Considerações finais (Somente AGES IV); title-only scope remains in force"},
    ]
    expected_scope_units = list(HOORTECH_UNITS)
    expected_order = {
        "schema_version": 1,
        "record_type": "user_authorized_document_order_and_numbering_scope",
        "date": "2026-10-17",
        "approval_status": "authorized_for_execution_pending_human_review",
        "source": {
            "path": "RELATORIO_ATUAL.odt",
            "sha256": DOCUMENT_ORDER_SOURCE_SHA256,
            "must_remain_unchanged": True,
        },
        "baseline": {
            "branch": "migration/ages-iii",
            "commit": DOCUMENT_ORDER_BASELINE,
            "working_tree_clean": True,
        },
        "user_decision": "Renumerar em sequência (recomendado)",
    }
    if any(authorization.get(key) != value for key, value in expected_order.items()):
        raise ValueError("Document-order authorization is missing, stale, or exceeds the approved source and baseline")
    if (scope.get("units") != expected_scope_units
            or scope.get("final_chapter_sequence") != expected_sequence
            or scope.get("figure_numbering") != "AGES I 1–5; AGES II 6–12; AGES III 13–20; AGES IV 21–31; Hoortech 32–34."):
        raise ValueError("Document-order scope differs from the exact user-approved unit or final sequence")

    manifest = json.loads((repo / "docs/CONTENT_MANIFEST.json").read_text(encoding="utf-8"))
    overlay = manifest.get("migration_overlay", {}).get("document_order")
    if not isinstance(overlay, dict):
        raise ValueError("Manifest has no document_order traceability overlay")
    affected_units = scope.get("affected_units")
    heading_map = scope.get("heading_numbering")
    caption_map = scope.get("figure_caption_numbering")
    inline_map = scope.get("inline_reference_adjustments")
    if (not isinstance(affected_units, list) or not isinstance(heading_map, dict)
            or not isinstance(caption_map, dict) or not isinstance(inline_map, dict)):
        raise ValueError("Document-order authorization maps have an invalid shape")
    if len(affected_units) != len(set(affected_units)) or affected_units != sorted(affected_units):
        raise ValueError("Affected units must be unique and in deterministic order")

    records = _index(manifest.get("records", []))
    units = _index(manifest.get("units", []))
    expected_heading_ids = {
        rid for rid, record in records.items()
        if (record.get("type") == "text:h" and record.get("unit_id") in set(affected_units)
            and re.match(r"^\d+(?:\.\d+)*\.?(?:\s|$|-)", record.get("text", "")))
    }
    expected_caption_ids = {
        rid for rid, record in records.items()
        if record.get("semantic_type") == "caption" and record.get("unit_id") in set(affected_units)
    }
    if set(heading_map) != expected_heading_ids or set(caption_map) != expected_caption_ids:
        raise ValueError("Heading/caption authorization IDs do not cover exactly the affected ODF records")
    if set(inline_map) != {"text-p-0679"}:
        raise ValueError("Inline reference authorization must cover exactly the Hoortech topic reference")
    derived_units = {
        spec.get("unit_id") for table in (heading_map, caption_map, inline_map)
        for spec in table.values()
    }
    if affected_units != sorted(derived_units):
        raise ValueError("Affected-unit list does not equal the units owning authorized source records")

    def heading_target_chapter(unit_id: str) -> int:
        if unit_id in HOORTECH_UNITS:
            return 6
        if unit_id.startswith("chapter-04-") or unit_id.startswith("ages-ii-"):
            return 3
        if unit_id.startswith("chapter-05-") or unit_id.startswith("ages-iii-"):
            return 4
        if unit_id.startswith("chapter-06-") or unit_id.startswith("ages-iv-"):
            return 5
        if unit_id.startswith("chapter-07-"):
            return 7
        raise ValueError("Heading belongs to an edition outside the authorized sequence")

    expected_chapter_by_unit = {
        **{uid: 3 for uid in HOORTECH_UNITS},
        **{uid: 4 for uid in AGES_II_UNITS},
        **{uid: 5 for uid in AGES_III_UNITS},
        **{uid: 6 for uid in AGES_IV_UNITS},
        "chapter-07-text-h-0123": 7,
    }
    for source_id, spec in heading_map.items():
        record = records[source_id]
        unit_id = record.get("unit_id")
        if unit_id not in units or spec.get("unit_id") != unit_id or spec.get("source_text") != record.get("text"):
            raise ValueError(f"Heading authorization is not bound to the original ODF record: {source_id}")
        source_chapter = expected_chapter_by_unit.get(unit_id)
        target_chapter = heading_target_chapter(unit_id)
        if spec.get("source_chapter") != source_chapter or spec.get("target_chapter") != target_chapter:
            raise ValueError(f"Heading chapter mapping is invalid for {source_id}")
        old_style = PRESENTATION_HEADINGS.get(source_id, (spec["source_text"], spec["source_text"]))[1]
        if spec.get("current_display_text") != old_style:
            raise ValueError(f"Heading display does not match the independently approved pre-relocation style: {source_id}")
        if spec.get("target_text") != _renumber_display_heading(old_style, target_chapter):
            raise ValueError(f"Heading target changes text beyond the authorized chapter number: {source_id}")

    expected_caption_targets = {"ages-ii": set(range(6, 13)), "ages-iii": set(range(13, 21)),
                                "ages-iv": set(range(21, 32)), "hoortech": set(range(32, 35))}
    actual_caption_targets = {key: set() for key in expected_caption_targets}
    for source_id, spec in caption_map.items():
        record = records[source_id]
        unit_id = record.get("unit_id")
        if unit_id not in units or spec.get("unit_id") != unit_id or spec.get("source_text") != record.get("text"):
            raise ValueError(f"Caption authorization is not bound to the original ODF record: {source_id}")
        match = re.match(r"^(\s*)Figure (\d+): (.*)$", spec["source_text"], re.DOTALL)
        if not match:
            raise ValueError(f"Caption source has an unexpected prefix: {source_id}")
        leading, number_text, body = match.groups()
        number = int(number_text)
        group = ("hoortech" if unit_id in HOORTECH_UNITS else
                 "ages-ii" if unit_id in AGES_II_UNITS else
                 "ages-iii" if unit_id in AGES_III_UNITS else
                 "ages-iv" if unit_id in AGES_IV_UNITS else None)
        if group is None:
            raise ValueError(f"Caption belongs to an edition outside the authorized order: {source_id}")
        current = f"{leading}Figura {number} – {body}"
        target_number = number + 26 if group == "hoortech" else number - 3
        target = f"{leading}Figura {target_number} – {body}"
        if (spec.get("current_display_text") != current
                or spec.get("source_figure") != number
                or spec.get("target_figure") != target_number
                or spec.get("target_text") != target):
            raise ValueError(f"Caption target changes label/body beyond the authorized numbering: {source_id}")
        actual_caption_targets[group].add(target_number)
    if actual_caption_targets != expected_caption_targets:
        raise ValueError("Reordered figure ranges must remain unique, gap-free and edition-specific")

    inline = inline_map["text-p-0679"]
    inline_source = records.get("text-p-0679", {}).get("text")
    if (inline.get("unit_id") != "chapter-03-text-h-0025"
            or inline.get("source_text") != inline_source
            or inline.get("source_fragment") != "No tópico 3.2,"
            or inline.get("target_fragment") != "No tópico 6.2,"
            or inline.get("target_text") != inline_source.replace("No tópico 3.2,", "No tópico 6.2,", 1)):
        raise ValueError("Hoortech internal topic reference differs from the exact approved replacement")

    mapped_ids = set(heading_map) | set(caption_map) | set(inline_map)
    if (overlay.get("schema_version") != 1
            or overlay.get("status") != "authorized-pending-integration-and-audit"
            or overlay.get("authorization_evidence") != DOCUMENT_ORDER_AUTHORIZATION
            or overlay.get("authorization_evidence_sha256") != hashlib.sha256(raw_bytes).hexdigest()
            or overlay.get("baseline_commit") != DOCUMENT_ORDER_BASELINE
            or overlay.get("source_sha256") != DOCUMENT_ORDER_SOURCE_SHA256
            or overlay.get("moved_units") != expected_scope_units
            or overlay.get("affected_units") != affected_units
            or overlay.get("final_chapter_sequence") != expected_sequence
            or set(overlay.get("affected_source_ids", [])) != mapped_ids
            or len(overlay.get("affected_source_ids", [])) != len(mapped_ids)):
        raise ValueError("Manifest document-order overlay differs from the current exact authorization")
    for key, mapping in (("heading_numbering", heading_map), ("figure_caption_numbering", caption_map)):
        overlay_items = overlay.get(key)
        if not isinstance(overlay_items, list):
            raise ValueError(f"Manifest overlay {key} must be a list")
        projected = {item.get("source_id"): item for item in overlay_items if isinstance(item, dict)}
        expected_overlay = {source_id: {"source_id": source_id, **spec} for source_id, spec in mapping.items()}
        if projected != expected_overlay or len(projected) != len(overlay_items):
            raise ValueError(f"Manifest overlay {key} does not exactly match authorization")
    if overlay.get("inline_reference_adjustments") != [
        {"source_id": source_id, **spec} for source_id, spec in inline_map.items()
    ]:
        raise ValueError("Manifest overlay inline reference differs from the exact authorization")
    return authorization


def _load_presentation_authorization(repo: Path, unit_id: str | None = None) -> dict:
    authorization = _load_base_presentation_authorization(repo, unit_id)
    document_order_units = set(HOORTECH_UNITS) | set(AGES_II_UNITS) | set(AGES_III_UNITS) | set(AGES_IV_UNITS)
    if unit_id in document_order_units and (repo / DOCUMENT_ORDER_AUTHORIZATION).is_file():
        document_authorization = _load_document_order_authorization(repo)
        authorization = {
            **authorization,
            "approved_document_reordering": {
                "authorization_evidence": DOCUMENT_ORDER_AUTHORIZATION,
                **document_authorization,
            },
        }
    return authorization


def _is_authorized_ages_iv_presentation(authorization, source_id):
    if authorization is None:
        return False
    scope = authorization.get("scope", {})
    if scope.get("units") != list(AGES_IV_UNITS):
        return False
    if source_id in AGES_IV_CAPTION_IDS:
        expected = PRESENTATION_CAPTIONS[source_id][1]
        return any(
            source_id in PRESENTATION_OVERRIDES_BY_UNIT.get(uid, set())
            and authorization.get("approved_presentation_changes", {}).get("figure_caption_labels", {}).get(source_id) == expected
            for uid in AGES_IV_UNITS
        )
    if source_id in AGES_IV_HEADING_IDS:
        expected = PRESENTATION_HEADINGS[source_id][1]
        return any(
            source_id in PRESENTATION_OVERRIDES_BY_UNIT.get(uid, set())
            and authorization.get("approved_presentation_changes", {}).get("section_numbering", {}).get(source_id) == expected
            for uid in AGES_IV_UNITS
        )
    if source_id in PRESENTATION_REPOSITORY_LINKS or source_id in PRESENTATION_REPOSITORY_PARAGRAPHS:
        link_id = PRESENTATION_REPOSITORY_PARAGRAPHS.get(source_id, source_id)
        expected = PRESENTATION_REPOSITORY_LINKS.get(link_id)
        return expected is not None and any(
            source_id in PRESENTATION_OVERRIDES_BY_UNIT.get(uid, set())
            and authorization.get("approved_presentation_changes", {}).get("repository_link_sentences", {}).get(source_id) == expected
            for uid in AGES_IV_UNITS
        )
    wiki_rules = {
        **AGES_IV_WIKI_SENTENCES,
        **{rule["source_id"]: rule for rule in AGES_IV_WIKI_SENTENCES.values()},
    }
    if source_id in wiki_rules:
        expected = wiki_rules[source_id]
        return any(
            source_id in PRESENTATION_OVERRIDES_BY_UNIT.get(uid, set())
            and authorization.get("approved_presentation_changes", {}).get("wiki_link_sentences", {}).get(source_id) == expected
            for uid in AGES_IV_UNITS
        )
    return False


def _verify_ages_iv_partial_source_scope(unit_id, unit, unit_ledger, source_ids, authorization):
    """Fail-closed exact proof of the approved AGES IV title-only partial unit."""
    scope = (authorization or {}).get("scope", {})
    policy = scope.get("authorized_title_only_inclusion")
    expected_text_ids = [AGES_IV_TITLE_ONLY_HEADING_ID] + [
        rid for rid in AGES_IV_TITLE_ONLY_OMITTED_IDS if rid.startswith("text-p-")
    ]
    expected_record_ids = [AGES_IV_TITLE_ONLY_HEADING_ID, *AGES_IV_TITLE_ONLY_OMITTED_IDS]
    if (unit_id != AGES_IV_TITLE_ONLY_UNIT
            or scope.get("title_only_partial_units") != [AGES_IV_TITLE_ONLY_UNIT]
            or policy is None
            or policy.get("included_source_record_ids") != [AGES_IV_TITLE_ONLY_HEADING_ID]
            or policy.get("omitted_source_record_ids") != list(AGES_IV_TITLE_ONLY_OMITTED_IDS)
            or unit.get("record_ids") != expected_record_ids
            or unit.get("source_record_ids") != expected_text_ids
            or source_ids != expected_text_ids
            or unit_ledger.get("authorized_title_only_inclusion") != policy):
        raise ValueError("Partial unit differs from the exact authorized chapter 7 title-only scope")
    mappings = unit_ledger.get("element_map", [])
    if [mapping.get("source_id") for mapping in mappings] != [AGES_IV_TITLE_ONLY_HEADING_ID]:
        raise ValueError("Title-only partial unit must map exactly its approved heading and no omitted body element")
    return policy


def _load_ages_i_ii_formatting_authorization(repo: Path, unit_id: str | None = None) -> dict | None:
    """Load the exact 2026-10-16 scope extension for the six wiki links/citations."""
    if unit_id not in AGES_I_II_FORMATTING_UNITS:
        return None
    authorization = json.loads((repo / AGES_I_II_FORMATTING_AUTHORIZATION).read_text(encoding="utf-8"))
    scope = authorization.get("scope", {})
    expected_units = sorted(AGES_I_II_FORMATTING_UNITS)
    expected_wikis = {
        paragraph_id: {**rule, "leading_tabs": rule["leading_tabs"]}
        for paragraph_id, rule in AGES_I_II_WIKI_SENTENCES.items()
    }
    expected_citations = AGES_I_II_TECHNICAL_CITATIONS
    if (authorization.get("schema_version") != 1
            or authorization.get("record_type") != "user_authorized_scope_extension"
            or authorization.get("date") != "2026-10-16"
            or authorization.get("branch") != "migration/ages-ii"
            or authorization.get("approval_status") != "scope_extension_authorized; revised PDFs and reports still require user review"
            or scope.get("units") != expected_units
            or scope.get("harness_validation") != ["scripts/migration_harness/preservation.py", "tests/test_preservation.py"]
            or authorization.get("approved_wiki_link_sentences") != expected_wikis
            or authorization.get("approved_technical_citations_by_unit") != expected_citations
            or "Do not modify RELATORIO_ATUAL.odt or relatorio_mariah/." not in authorization.get("explicit_limits", [])):
        raise ValueError("The AGES I/II formatting authorization is missing, stale, or outside its exact scope")
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
AGES_II_ADDITIONAL_REFERENCE_RECORDS = {
    "ages-ii-figma": {
        "source_record_id": "text-p-1582", "source_author": "FIGMA", "author": "Figma",
        "title": "Figma: the collaborative interface design tool", "url": "https://www.figma.com",
    },
    "ages-ii-docker": {
        "source_record_id": "text-p-1574", "source_author": "DOCKER", "author": "Docker",
        "title": "Enterprise Application Container Platform | Docker", "url": "https://www.docker.com/",
    },
    "ages-ii-graph-api": {
        "source_record_id": "text-p-1591", "author": None,
        "title": "Graph API - Documentation", "url": "https://developers.facebook.com/docs/graph-api/",
    },
}
AGES_II_RFC_REFERENCE_FIELDS = {
    "ages-ii-http-rfc9110": {
        "title": "RFC 9110: HTTP Semantics", "editor": "Roy T. Fielding and Mark Nottingham and Julian Reschke",
        "date": "2022-06", "organization": "Internet Engineering Task Force", "number": "9110",
        "url": "https://www.rfc-editor.org/info/rfc9110/",
    },
    "ages-ii-json-rfc8259": {
        "title": "RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format", "editor": "Tim Bray",
        "date": "2017-12", "organization": "Internet Engineering Task Force", "number": "8259",
        "url": "https://www.rfc-editor.org/info/rfc8259/",
    },
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
    expected_citation_keys = [
        key for source_id in AGES_II_TECHNOLOGY_TEXT_IDS
        for key in AGES_I_II_TECHNICAL_CITATIONS.get("chapter-04-text-h-0046", {}).get(source_id, [])
    ]
    if citation_keys != expected_citation_keys:
        raise ValueError("Technical citations across AGES II database/architecture/prototype/technology passages are missing, duplicated, or out of order")

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

    for key, expected in AGES_II_ADDITIONAL_REFERENCE_RECORDS.items():
        source_record = records.get(expected["source_record_id"], {})
        source_text = source_record.get("source_text") or source_record.get("text") or ""
        if (expected["title"] not in source_text or expected["url"] not in source_text
                or (expected.get("source_author") and not source_text.startswith(expected["source_author"] + "."))):
            raise ValueError(f"Original ODT bibliography record for {key} differs from the frozen manifest evidence")
        match = re.search(rf"(?ms)^@online\{{{re.escape(key)},(?P<entry>.*?)^\}}", bibliography)
        if not match:
            raise ValueError(f"Bibliography entry {key} is missing")
        entry = match["entry"]
        fields = {
            "title": "{" + expected["title"] + "}", "url": "{" + expected["url"] + "}",
            "year": "{2024}", "urldate": "{" + assigned_date + "}",
        }
        for field, value in fields.items():
            if not re.search(rf"(?m)^\s*{field}\s*=\s*{re.escape(value)}\s*,?\s*$", entry):
                raise ValueError(f"Bibliography field {field} for {key} differs from the original ODT or assigned date convention")
        author_field = re.search(r"(?m)^\s*author\s*=\s*(.*?)\s*,?\s*$", entry)
        if expected["author"] is None:
            if author_field:
                raise ValueError(f"Bibliography entry {key} infers authorship absent from the original ODT")
        elif author_field is None or author_field.group(1) != "{{" + expected["author"] + "}}":
            raise ValueError(f"Bibliography author for {key} differs from the original ODT")

    for key, expected in AGES_II_RFC_REFERENCE_FIELDS.items():
        match = re.search(rf"(?ms)^@online\{{{re.escape(key)},(?P<entry>.*?)^\}}", bibliography)
        if not match:
            raise ValueError(f"Verified official RFC entry {key} is missing")
        entry = match["entry"]
        for field, value in expected.items():
            if not re.search(rf"(?m)^\s*{field}\s*=\s*\{{{re.escape(value)}\}}\s*,?\s*$", entry):
                raise ValueError(f"Verified RFC field {field} for {key} differs from its curation evidence")
        if not re.search(rf"(?m)^\s*urldate\s*=\s*\{{{re.escape(assigned_date)}\}}\s*,?\s*$", entry):
            raise ValueError(f"Assigned AGES II access date for {key} differs from user instruction")

    pending = curated.get("text-a-0126", {})
    if pending.get("status") != "PENDING" or pending.get("original_url") != records["text-a-0126"].get("href"):
        raise ValueError("Graph API reference must remain pending with the exact original URL")
    expected_links = [
        (item["original_url"], item["original_anchor"])
        for item in reference_evidence.get("references", [])
        if item.get("source_record_id") in set(AGES_II_TECHNOLOGY_REFERENCE_KEYS) | {"text-a-0126"}
    ]
    docker_reference = records.get("text-a-0171", {})
    if docker_reference.get("href") != "https://www.docker.com/" or docker_reference.get("source_text") != "https://www.docker.com/":
        raise ValueError("The Docker citation target must come from its original ODT bibliography hyperlink")
    expected_links.append((docker_reference["href"], "Documentação Docker"))
    observed_links = [(token.args[0], displayed_text(token.args[1])) for token in commands(raw) if token.name == "href" and len(token.args) == 2]
    if observed_links != expected_links:
        raise ValueError("Original technology documentation URLs/anchors differ from verified source order")

    return True


def _verify_ages_iii_bibliography_entries(bibliography, reference_evidence, records):
    """Tie each AGES III citation key to the curator's exact verified source."""
    cited = {item.get("source_record_id"): item for item in reference_evidence.get("references", [])}
    supplements = {
        item.get("item_id"): item
        for item in reference_evidence.get("supplementary_inventory", {}).get("items", [])
    }
    keys = re.findall(r"(?m)^@\w+\{([^,]+),", bibliography)
    if len(keys) != len(set(keys)):
        raise ValueError("Bibliography contains duplicate citation keys")
    actual_consultation_date = reference_evidence.get("consultation_date")
    if actual_consultation_date != "2026-10-16":
        raise ValueError("AGES III bibliography must use the actual reference-curation date")
    for key in AGES_III_TECHNICAL_CITATION_KEYS:
        source_record_id, supplement_id = AGES_III_CITATION_EVIDENCE[key]
        if source_record_id is not None:
            evidence = cited.get(source_record_id)
            source_record = records.get(source_record_id, {})
            if (evidence is None
                    or evidence.get("verification_status") != "VERIFICADO"
                    or evidence.get("claim_support_status") not in {"VERIFICADO", "PARTIAL"}
                    or evidence.get("original_url") != source_record.get("href")
                    or evidence.get("original_anchor") != source_record.get("source_text")
                    or evidence.get("observed_title") is None
                    or evidence.get("user_assigned_citation_year") != 2026):
                raise ValueError(f"Curator evidence for {key}/{source_record_id} is incomplete or not verified")
            title = evidence["observed_title"]
            url = evidence["original_url"]
            actual_source_date = actual_consultation_date
            factual_publication_date = evidence.get("observed_publication_date")
        else:
            item = supplements.get(supplement_id)
            source_index = AGES_III_CITATION_EVIDENCE_SOURCE_INDEX.get(key, 0)
            sources = item.get("official_sources", []) if item else []
            if (item is None
                    or not str(item.get("verification_status", "")).startswith("VERIFICADO")
                    or item.get("user_assigned_citation_year") != 2026
                    or source_index >= len(sources)):
                raise ValueError(f"Supplementary curator evidence for {key}/{supplement_id} is missing or unverified")
            source = sources[source_index]
            if (not source.get("title") or not source.get("url")
                    or source.get("observed_url") != source.get("url")
                    or source.get("access_date") != actual_consultation_date):
                raise ValueError(f"Supplementary source identity/URL/date for {key} differs from its evidence")
            title = source["title"]
            url = source["url"]
            actual_source_date = source["access_date"]
            factual_publication_date = source.get("published_date")
        if actual_source_date != actual_consultation_date:
            raise ValueError(f"The actual AGES III source consultation date for {key} is not preserved in curator evidence")
        entry_type = AGES_III_CITATION_TYPES.get(key, "online")
        match = re.search(rf"(?ms)^@{re.escape(entry_type)}\{{{re.escape(key)},(?P<entry>.*?)^\}}", bibliography)
        if not match:
            raise ValueError(f"Bibliography entry {key} is missing")
        entry = match["entry"]
        fields = {
            "title": title,
            "url": url,
            "urldate": actual_consultation_date,
            **AGES_III_BIBLIOGRAPHY_REQUIRED_FIELDS.get(key, {}),
        }
        if factual_publication_date:
            fields["date"] = factual_publication_date
        for field, value in fields.items():
            field_match = re.search(rf"(?m)^\s*{field}\s*=\s*\{{(.*?)\}}\s*,?\s*$", entry)
            observed_value = re.sub(r"\\([#$%&_{}])", r"\1", field_match[1]) if field_match else None
            if not field_match or observed_value != value:
                raise ValueError(f"Bibliography field {field} for {key} differs from curator evidence/user citation-year convention")
        forbidden_date_fields = {"year"} if factual_publication_date else {"date", "year"}
        for field in forbidden_date_fields:
            if re.search(rf"(?m)^\s*{field}\s*=", entry):
                if factual_publication_date:
                    raise ValueError(f"Bibliography entry {key} has a conflicting factual publication year field")
                raise ValueError(
                    f"Bibliography entry {key} lacks a verified factual publication date; "
                    f"do not emit {field} from the user-authorized citation-year convention"
                )


def _verify_ages_iii_technology_paragraph(source, unit_ledger, unit, records, authorization):
    """Verify the scoped narrative override, all source mappings, links and citations."""
    source_bytes = source.encode("utf-8")
    mappings = {item.get("source_id"): item for item in unit_ledger.get("element_map", [])}
    expected_order = [rid for rid in unit.get("record_ids", []) if rid in AGES_III_TECHNOLOGY_ELEMENT_IDS]
    if expected_order != list(AGES_III_TECHNOLOGY_ELEMENT_IDS):
        raise ValueError("AGES III technology text/link elements differ from the audited source order")
    if any(rid not in mappings for rid in AGES_III_TECHNOLOGY_ELEMENT_IDS):
        raise ValueError("An original AGES III technology paragraph or hyperlink is not mapped")
    narrative_policy = authorization.get("approved_presentation_changes", {}).get("technology_narrative_rewrite", {})
    if (narrative_policy.get("source_ids") != list(AGES_III_TECHNOLOGY_NARRATIVE_TEXT_IDS)
            or narrative_policy.get("authorization_evidence") != AGES_III_TECHNOLOGY_NARRATIVE_AUTHORIZATION
            or narrative_policy.get("independent_content_audit") != "pending"):
        raise ValueError("The technology narrative rewrite lacks its exact user authorization or pending independent-review marker")
    narrative_serializations = {
        rid for rid, mapping in mappings.items()
        if "approved_technology_narrative" in mapping.get("serializations", [])
    }
    if narrative_serializations != set(AGES_III_TECHNOLOGY_NARRATIVE_TEXT_IDS):
        raise ValueError("Technology narrative serialization must cover exactly the authorized rewritten source paragraphs")
    internal_tab_removal_ids = {
        rid for rid, mapping in mappings.items()
        if "approved_internal_tab_removal" in mapping.get("serializations", [])
    }
    tab_policy = authorization.get("approved_presentation_changes", {}).get("internal_tab_removal")
    tab_mapping = mappings.get(AGES_III_TECHNOLOGY_LITERAL_TAB["source_id"], {})
    tab_fragment = source_bytes[
        tab_mapping.get("start_byte", 0):tab_mapping.get("end_byte", 0)
    ].decode("utf-8")
    tab_record = records.get(AGES_III_TECHNOLOGY_LITERAL_TAB["source_id"], {})
    if (internal_tab_removal_ids != {AGES_III_TECHNOLOGY_LITERAL_TAB["source_id"]}
            or tab_policy != AGES_III_INTERNAL_TAB_REMOVAL_POLICY
            or unit_ledger.get("approved_internal_tab_removal") != AGES_III_INTERNAL_TAB_REMOVAL_POLICY
            or tab_record.get("text", "").count(AGES_III_TECHNOLOGY_LITERAL_TAB["source_fragment"]) != 1
            or tab_fragment.count(AGES_III_TECHNOLOGY_LITERAL_TAB["target_fragment"]) != 1
            or r"\originalinlinetab{}" in tab_fragment
            or "inline_tab_layout" not in tab_mapping.get("serializations", [])):
        raise ValueError("The one approved tab removal must map only text-p-1084 from the exact source phrase to ‘consultas tipadas’")
    link_policy = authorization.get("approved_presentation_changes", {}).get("technology_documentation_link_prose", {})
    if (link_policy != AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_POLICY
            or unit_ledger.get("technology_documentation_link_prose") != AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_POLICY):
        raise ValueError("Technology documentation links lack the exact authorized Mariah-style prose policy")
    link_serializations = {
        rid for rid, mapping in mappings.items()
        if "technology_documentation_link_prose" in mapping.get("serializations", [])
    }
    if link_serializations != set(AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_TEXT_IDS):
        raise ValueError("Technology documentation-link prose must cover exactly the 13 original link paragraphs")
    for rid, anchor in AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_ANCHORS.items():
        if records[rid].get("text", "").strip(" \t\r\n") != anchor:
            raise ValueError(f"Original technology documentation anchor text changed for {rid}")
    literal_tab = AGES_III_TECHNOLOGY_LITERAL_TAB
    tab_source = records[literal_tab["source_id"]].get("text", "")
    tab_mapping = mappings[literal_tab["source_id"]]
    tab_fragment = source_bytes[tab_mapping["start_byte"]:tab_mapping["end_byte"]].decode("utf-8")
    if (tab_source.count(literal_tab["source_fragment"]) != 1
            or tab_fragment.count(literal_tab["target_fragment"]) != 1
            or "inline_tab_layout" not in tab_mapping.get("serializations", [])):
        raise ValueError("The source tab inside ‘consultas t\tipadas’ must be preserved at its exact mapped position")
    tex_path = unit_ledger.get("tex_path")
    if any(mappings[rid].get("target_file") != tex_path for rid in AGES_III_TECHNOLOGY_ELEMENT_IDS):
        raise ValueError("All AGES III technology elements must remain in the assigned unit file")
    positions = [(mappings[rid].get("start_byte"), mappings[rid].get("end_byte"), rid) for rid in AGES_III_TECHNOLOGY_ELEMENT_IDS]
    if any(type(start) is not int or type(end) is not int or start > end for start, end, _ in positions):
        raise ValueError("Technology paragraph mapping has invalid byte intervals")
    if [start for start, _, _ in positions] != sorted(start for start, _, _ in positions):
        raise ValueError("Technology text, direct links and anchors changed source order")
    source_bytes = source.encode("utf-8")
    start = positions[0][0]
    if positions[-1][1] > len(source_bytes):
        raise ValueError("Technology paragraph mapping extends beyond its target file")
    tail = source_bytes[start:].decode("utf-8")
    paragraph_end = next((token for token in commands(tail) if token.name == "par"), None)
    if paragraph_end is None:
        raise ValueError("The technology presentation lacks its closing paragraph boundary")
    paragraph_end_byte = len(tail[:paragraph_end.end].encode("utf-8"))
    if any(end - start > paragraph_end_byte for _, end, _ in positions):
        raise ValueError("A technology text span or original link falls outside the one-paragraph presentation")
    paragraph = tail[:paragraph_end.end]
    if sum(token.name == "par" for token in commands(paragraph)) != 1:
        raise ValueError("Technology presentation contains an artificial paragraph break")
    if any(token.name == "item" or token.name in {"begin", "end"} and token.args and token.args[0] in {"itemize", "enumerate"} for token in commands(paragraph)):
        raise ValueError("The approved technology paragraph still contains list structure")

    if unit_ledger.get("technology_paragraph_join") != AGES_III_TECHNOLOGY_JOIN_POLICY:
        raise ValueError("Technology paragraph join ledger must preserve every original boundary and distinguish inserted spaces")
    join_mappings = {
        rid for rid, mapping in mappings.items()
        if "technology_paragraph_join" in mapping.get("serializations", [])
    }
    if join_mappings != set(AGES_III_TECHNOLOGY_INSERTED_SEPARATOR_SOURCE_IDS):
        raise ValueError("Technology paragraph join serialization must cover exactly the 26 inserted separators")

    source_bytes = source.encode("utf-8")
    for left_id, right_id in AGES_III_TECHNOLOGY_PARAGRAPH_BOUNDARIES:
        left = mappings[left_id]
        right = mappings[right_id]
        left_fragment = source_bytes[left["start_byte"]:left["end_byte"]].decode("utf-8")
        visible_left = strip_comments(left_fragment).rstrip()
        has_inserted_join = left_id in AGES_III_TECHNOLOGY_INSERTED_SEPARATOR_SOURCE_IDS
        original_left_text = records[left_id].get("text", "")
        if (visible_left.count(r"\originalspace{}") != 1
                or not visible_left.endswith(r"\originalspace{}")
                or "original_whitespace" not in left.get("serializations", [])
                or ("technology_paragraph_join" in left.get("serializations", [])) != has_inserted_join
                or (left_id in AGES_III_TECHNOLOGY_SOURCE_TRAILING_SPACE_IDS) != original_left_text.endswith(" ")):
            raise ValueError(f"Technology paragraph boundary {left_id} → {right_id} lacks exactly one mapped separator")
        gap = source_bytes[left["end_byte"]:right["start_byte"]].decode("utf-8")
        if strip_comments(gap).strip():
            raise ValueError(f"Visible content occurs between technology source records {left_id} and {right_id}")

    output_projection = _normalize_ages_iii_technology_text(displayed_text(
        paragraph[:paragraph_end.start],
        {
            "original_whitespace", "inline_tab_layout", "reference_paragraph_layout",
            "technology_citation", "technology_paragraph_join", "approved_technology_narrative",
            "approved_internal_tab_removal",
        },
        macro_contract_verified=True,
        inline_layout_verified=True,
        reference_layout_verified=True,
    ))
    if not output_projection:
        raise ValueError("The authorized technology narrative has no visible text")

    observed_links = [
        (_url(token.args[0]), displayed_text(token.args[1]))
        for token in commands(paragraph) if token.name == "href" and len(token.args) == 2
    ]
    expected_links = [
        (records[rid].get("href"), records[rid].get("source_text"))
        for rid in AGES_III_TECHNOLOGY_LINK_IDS
    ]
    if observed_links != expected_links:
        raise ValueError("The 13 original technology documentation URLs/anchors changed or moved out of order")
    observed_citations = [key for token in commands(paragraph) if token.name == "cite" for key in token.args[0].split(",")]
    expected_citations = [
        key for rid in AGES_III_TECHNOLOGY_TEXT_IDS
        for key in AGES_III_TECHNICAL_CITATIONS["chapter-05-text-h-0085"].get(rid, [])
    ]
    if observed_citations != expected_citations:
        raise ValueError("Citations in the single technology paragraph differ from the exact mapped source order")


def _normalize_ages_iii_technology_text(value):
    """Collapse ODF layout whitespace only for the specifically approved one-paragraph technology layout."""
    return re.sub(r"[\t\n\r\f\v ]+", " ", value).strip(" ")


def _verify_ages_iii_citation_alignment(source_id, fragment_value, keys, serializations, macro_verified, inline_verified, reference_verified):
    terms = AGES_III_CITATION_TERMS.get(source_id)
    _verify_citation_alignment(source_id, fragment_value, keys, terms, serializations, macro_verified, inline_verified, reference_verified)


def _verify_citation_alignment(source_id, fragment_value, keys, terms, serializations, macro_verified, inline_verified, reference_verified):
    citations = [token for token in commands(strip_comments(fragment_value)) if token.name == "cite"]
    if terms is None or len(terms) != len(keys) or len(citations) != len(keys):
        raise ValueError(f"Citation-to-term evidence is incomplete for {source_id}")
    previous_end = 0
    for key, term, token in zip(keys, terms, citations):
        if token.starred or token.optionals or len(token.args) != 1 or token.args[0].strip() != key:
            raise ValueError(f"Each AGES III citation must be a separate author-date call attached in order for {source_id}")
        segment = fragment_value[previous_end:token.start]
        segment = re.sub(r"(?:\\space\s*)+$", "", segment)
        visible_segment = displayed_text(
            segment,
            serializations,
            macro_contract_verified=macro_verified,
            inline_layout_verified=inline_verified,
            reference_layout_verified=reference_verified,
        )
        if term not in visible_segment:
            raise ValueError(f"Citation {key} is not attached to the approved source term {term!r} in {source_id}")
        previous_end = token.end


def _verify_ages_iv_bibliography_entries(bibliography, reference_evidence, records, supplemental_authorization):
    """Tie AGES IV's newly inserted technology citations to curated sources and real access dates."""
    sources = {item.get("id"): item for item in reference_evidence.get("sources", [])}
    bib_keys = re.findall(r"(?m)^@\w+\{([^,]+),", bibliography)
    if len(bib_keys) != len(set(bib_keys)):
        raise ValueError("Bibliography contains duplicate citation keys")
    access_date = reference_evidence.get("curation_window", {}).get("date")
    if access_date != "2026-10-17":
        raise ValueError("AGES IV author-date labels must retain the evidenced actual curation/access date")
    supplemental_records = supplemental_authorization.get("citations", {}) if isinstance(supplemental_authorization, dict) else {}
    expected_supplemental_records = {
        key: {
            "unit_id": rule["unit_id"],
            "source_record_id": rule["source_record_id"],
            "evidence_id": rule["evidence_id"],
            "citation_key": key,
            "term": rule["term"],
            "verified_url": rule["url"],
        }
        for key, rule in AGES_IV_SUPPLEMENTAL_CITATIONS.items()
    }
    if (supplemental_authorization.get("record_type") != "user_authorized_supplemental_technology_citations"
            or supplemental_authorization.get("approval_status") != "authorized_for_exact_citations; edition acceptance pending"
            or supplemental_authorization.get("source", {}).get("path") != "RELATORIO_ATUAL.odt"
            or supplemental_authorization.get("source", {}).get("sha256") != "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"
            or supplemental_records != expected_supplemental_records):
        raise ValueError("AGES IV supplemental technology citations lack the exact scoped user authorization")
    for key, source_id in AGES_IV_CITATION_EVIDENCE.items():
        source = sources.get(source_id)
        if (source is None
                or source.get("retrieval") != "RETRIEVED_BY_WEB_TOOL; HTTP status not exposed"
                or source.get("access_date") != access_date
                or source.get("author_date_label_year") != 2026
                or not source.get("observed_page_title")):
            raise ValueError(f"AGES IV curator evidence for {key}/{source_id} is missing, stale, or unverified")
        if key in AGES_IV_SUPPLEMENTAL_CITATIONS:
            rule = AGES_IV_SUPPLEMENTAL_CITATIONS[key]
            citation = supplemental_records[key]
            reference_url = source.get("verified_reference_url")
            if (citation.get("unit_id") != rule["unit_id"]
                    or citation.get("source_record_id") != rule["source_record_id"]
                    or citation.get("term") != rule["term"]
                    or citation.get("verified_url") != rule["url"]
                    or source.get("original_link_ids") != []
                    or source.get("original_url") is not None
                    or source.get("reference_url_recommendation") != rule["url"]
                    or reference_url != rule["url"]):
                raise ValueError(f"AGES IV supplemental source {key} differs from its narrow user authorization or curated URL")
        else:
            if len(source.get("original_link_ids", [])) != 1:
                raise ValueError(f"AGES IV source {key}/{source_id} must match exactly one original link")
            original_id = source["original_link_ids"][0]
            original = records.get(original_id, {})
            if (original.get("href") != source.get("original_url")
                    or original.get("source_text") not in source.get("original_anchor_text", [])):
                raise ValueError(f"AGES IV source link {original_id} for {key} no longer matches the curator record")
            reference_url = source.get("original_url")
        match = re.search(rf"(?ms)^@online\{{{re.escape(key)},(?P<entry>.*?)^\}}", bibliography)
        if not match:
            raise ValueError(f"AGES IV bibliography entry {key} is missing")
        entry = match["entry"]
        expected_fields = {
            "title": "{" + source["observed_page_title"] + "}",
            "url": "{" + reference_url + "}",
            "year": "{2026}",
            "urldate": "{" + access_date + "}",
        }
        for field, expected in expected_fields.items():
            if not re.search(rf"(?m)^\s*{field}\s*=\s*{re.escape(expected)}\s*,?\s*$", entry):
                raise ValueError(f"AGES IV bibliography field {field} for {key} differs from its evidence")
        author = source.get("observed_responsibility")
        author_line = re.search(r"(?m)^\s*author\s*=\s*(.*?)\s*,?\s*$", entry)
        if author:
            if author_line is None or author_line[1] != "{{" + author + "}}":
                raise ValueError(f"AGES IV bibliography author for {key} differs from the explicitly observed responsibility")
        elif author_line is not None:
            raise ValueError(f"AGES IV bibliography invents an author for title-as-author source {key}")


def _verify_document_order_unit(uid, unit_ledger, records, authorization, read_fragment):
    """Verify a unit's supplemental chapter/figure numbering overlay exactly."""
    document_auth = (authorization or {}).get("approved_document_reordering")
    if not isinstance(document_auth, dict):
        raise ValueError("Document-order overlay requires the current supplemental authorization")
    scope = document_auth.get("scope", {})
    specs = {
        source_id: spec
        for table in ("heading_numbering", "figure_caption_numbering", "inline_reference_adjustments")
        for source_id, spec in scope.get(table, {}).items()
        if spec.get("unit_id") == uid
    }
    mappings = unit_ledger.get("element_map", [])
    mapped = {
        item.get("source_id"): item for item in mappings
        if "document_reordering_numbering" in item.get("serializations", [])
    }
    expected_ids = sorted(specs)
    expected_policy = {
        "authorization_evidence": DOCUMENT_ORDER_AUTHORIZATION,
        "source_ids": expected_ids,
    }
    if (not expected_ids
            or unit_ledger.get("document_reordering_authorization") != expected_policy
            or sorted(mapped) != expected_ids):
        raise ValueError("Document-order ledger must cover exactly the authorized source IDs in this unit")
    for source_id in expected_ids:
        mapping = mapped[source_id]
        spec = specs[source_id]
        serializations = mapping.get("serializations", [])
        raw = read_fragment(mapping)
        observed = displayed_text(raw, serializations)
        projected, evidence = _project_approved_presentation(
            source_id, spec.get("source_text"), observed, serializations, authorization,
        )
        if (projected != spec.get("source_text")
                or evidence is None
                or evidence.get("displayed") != spec.get("target_text")
                or source_id not in records):
            raise ValueError(f"Document-order projection differs from its exact authorized source mapping: {source_id}")
    return expected_ids


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


def _is_authorized_ages_iii_presentation(authorization, source_id):
    return source_id in AGES_III_PRESENTATION_SOURCE_IDS and isinstance(authorization, dict) and (
        authorization.get("record_type") == "user_authorized_edition_scope"
        and authorization.get("approval_status") == "authorized_for_AGES_III_only; final edition approval pending"
        and authorization.get("source", {}).get("path") == "RELATORIO_ATUAL.odt"
        and authorization.get("source", {}).get("sha256") == "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"
        and authorization.get("scope", {}).get("units") == list(AGES_III_UNITS)
    )


def _is_authorized_ages_iii_group_label_removal(authorization, source_id):
    changes = authorization.get("approved_presentation_changes", {}) if isinstance(authorization, dict) else {}
    expected_change = {
        "text-p-1056": {
            "source_text": "Telas de Administrador:",
            "typeset_text": "",
            "treatment": "Omit this standalone group label from the typeset report; preserve its source text and omission evidence in the unit ledger.",
        },
        "text-h-0084": {
            "source_text": "Telas de Cliente:",
            "typeset_text": "",
            "treatment": "Omit this unnumbered subordinate heading from the typeset report; preserve its source text and omission evidence in the unit ledger.",
        },
    }
    return (
        source_id in AGES_III_PROTOTYPE_GROUP_LABELS
        and _is_authorized_ages_iii_presentation(authorization, source_id)
        and changes.get("prototype_group_label_removal") == expected_change
    )


def _project_approved_presentation(source_id, expected, observed, serializations, authorization, formatting_authorization=None):
    if "document_reordering_numbering" in serializations:
        document_auth = (authorization or {}).get("approved_document_reordering")
        if not isinstance(document_auth, dict):
            raise UnsupportedSerialization("Document-order numbering requires the exact current supplemental authorization")
        scope = document_auth.get("scope", {})
        candidates = [
            scope.get(table, {}).get(source_id)
            for table in ("heading_numbering", "figure_caption_numbering", "inline_reference_adjustments")
        ]
        spec = next((item for item in candidates if isinstance(item, dict)), None)
        allowed_companions = {
            "document_reordering_numbering", "abnt_figure_caption", "abnt_section_numbering",
            "original_whitespace", "inline_tab_layout", "reference_paragraph_layout",
            "tex_quotes", "tex_dashes", "canonical_unicode",
        }
        if (spec is None
                or set(serializations) - allowed_companions
                or expected != spec.get("source_text")
                or observed != spec.get("target_text")):
            raise UnsupportedSerialization("Document-order target differs from the exact source-bound approved numbering map")
        return expected, {
            "source_id": source_id,
            "kind": "document_reordering_numbering",
            "source": expected,
            "displayed": observed,
            "authorization_evidence": DOCUMENT_ORDER_AUTHORIZATION,
        }
    if "wiki_reference_sentence" in serializations:
        wiki_rules = {**AGES_I_II_WIKI_SENTENCES, **AGES_III_WIKI_SENTENCES, **AGES_IV_WIKI_SENTENCES}
        paragraph_id = source_id if source_id in wiki_rules else next(
            (pid for pid, candidate in wiki_rules.items() if candidate["source_id"] == source_id),
            None,
        )
        rule = wiki_rules.get(paragraph_id)
        if paragraph_id in AGES_III_WIKI_SENTENCES:
            if rule is None or not _is_authorized_ages_iii_presentation(authorization, paragraph_id):
                raise UnsupportedSerialization("Wiki reference sentence is outside the exact AGES III authorization")
        elif paragraph_id in AGES_IV_WIKI_SENTENCES:
            if rule is None or not _is_authorized_ages_iv_presentation(authorization, paragraph_id):
                raise UnsupportedSerialization("Wiki reference sentence is outside the exact AGES IV authorization")
        elif (rule is None or formatting_authorization is None
                or formatting_authorization.get("approved_wiki_link_sentences", {}).get(paragraph_id) != rule):
            raise UnsupportedSerialization("Wiki reference sentence is outside the exact AGES I/II authorization")
        if source_id == paragraph_id:
            leading = "\t" * rule["leading_tabs"]
            if expected != leading + rule["source_anchor"]:
                raise UnsupportedSerialization("Original wiki anchor or its source leading tabs changed")
            target = leading + rule["prefix"] + rule["anchor"] + rule["suffix"]
        elif source_id == rule["source_id"]:
            if expected != rule["source_anchor"]:
                raise UnsupportedSerialization("Original wiki hyperlink anchor changed")
            target = rule["anchor"]
        else:
            raise UnsupportedSerialization("Wiki reference mapping is not the authorized paragraph or hyperlink")
        if observed != target:
            raise UnsupportedSerialization("Wiki prose or linked anchor differs from the exact user-approved form")
        return expected, {
            "source_id": source_id,
            "kind": "wiki_link_sentence" if source_id == paragraph_id else "wiki_link_anchor",
            "source": expected,
            "displayed": target,
            "href": rule["href"],
        }
    used = set(serializations) & set(PRESENTATION_SERIALIZATIONS)
    if not used:
        return observed, None
    if authorization is None:
        raise UnsupportedSerialization("Presentation override requires the explicit current user authorization")
    for kind in used:
        if source_id not in PRESENTATION_SERIALIZATIONS[kind]:
            raise UnsupportedSerialization(f"{kind} is not authorized for {source_id}")
    frontmatter_used = used & set(FRONTMATTER_TRANSFORM_IDS)
    if frontmatter_used:
        if (len(frontmatter_used) != 1
                or used != frontmatter_used
                or authorization.get("record_type") != "user_authorized_frontmatter_scope"
                or authorization.get("approval_status") != "authorized_for_execution_pending_human_review"
                or authorization.get("source", {}).get("sha256") != "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"
                or not set(FRONTMATTER_UNITS) <= set(authorization.get("scope", {}).get("units", []))):
            raise UnsupportedSerialization("Frontmatter presentation change is outside the exact supplemental user authorization")
        kind = next(iter(frontmatter_used))
        spec = authorization["scope"]["presentation_changes"].get(kind, {}).get(source_id)
        if (not isinstance(spec, dict)
                or expected != spec.get("source_text")
                or observed != spec.get("target_text")):
            raise UnsupportedSerialization("Frontmatter target text differs from its exact source-bound approved presentation")
        return expected, {
            "source_id": source_id,
            "kind": kind,
            "source": expected,
            "displayed": observed,
            "reason": spec.get("reason"),
            "authorization_evidence": FRONTMATTER_AUTHORIZATION,
        }
    if "approved_group_label_removal" in used:
        if (used != {"approved_group_label_removal"}
                or not _is_authorized_ages_iii_group_label_removal(authorization, source_id)
                or expected != AGES_III_PROTOTYPE_GROUP_LABELS[source_id]
                or observed != ""):
            raise UnsupportedSerialization("Prototype group label removal differs from the user's exact approved source IDs or displayed text")
        return expected, {
            "source_id": source_id,
            "kind": "approved_group_label_removal",
            "source": expected,
            "displayed": "",
            "authorization_evidence": AGES_III_PROTOTYPE_GROUP_LABEL_REMOVAL_AUTHORIZATION,
        }
    if "approved_technology_narrative" in used:
        policy = authorization.get("approved_presentation_changes", {}).get("technology_narrative_rewrite", {})
        tab_removal_approved = "approved_internal_tab_removal" in used
        tab_removal_policy = authorization.get("approved_presentation_changes", {}).get("internal_tab_removal")
        if (used - {
                    "technology_citation", "technology_paragraph_join",
                    "approved_technology_narrative", "inline_tab_layout",
                    "approved_internal_tab_removal",
                }
                or source_id not in policy.get("source_ids", [])
                or policy.get("authorization_evidence") != AGES_III_TECHNOLOGY_NARRATIVE_AUTHORIZATION
                or policy.get("independent_content_audit") != "pending"
                or (tab_removal_approved and (
                    source_id != AGES_III_TECHNOLOGY_LITERAL_TAB["source_id"]
                    or tab_removal_policy != AGES_III_INTERNAL_TAB_REMOVAL_POLICY
                    or expected.count("consultas t ipadas") != 1
                    or observed.count("consultas tipadas") != 1
                ))
                or not observed.strip()):
            raise UnsupportedSerialization("Technology narrative rewrite is outside its exact user-approved source scope or lacks visible content")
        return expected, {
            "source_id": source_id,
            "kind": "user_authorized_technology_narrative_rewrite",
            "source": expected,
            "displayed": observed,
            "authorization_evidence": AGES_III_TECHNOLOGY_NARRATIVE_AUTHORIZATION,
            "lexical_equality": observed == expected,
            "semantic_review": "pending_independent_content_audit",
            **({
                "approved_whitespace_change": {
                    "kind": "remove_one_internal_source_tab",
                    "source_id": source_id,
                    "source_fragment_after_layout_projection": "consultas t ipadas",
                    "displayed_fragment": "consultas tipadas",
                    "authorization_evidence": AGES_III_INTERNAL_TAB_REMOVAL_AUTHORIZATION,
                },
            } if tab_removal_approved else {}),
        }
    if "technology_documentation_link_prose" in used:
        policy = authorization.get("approved_presentation_changes", {}).get("technology_documentation_link_prose", {})
        anchor = AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_ANCHORS.get(source_id)
        expected_target = policy.get("prefix") + anchor + policy.get("suffix") if anchor else None
        if (used - {"technology_documentation_link_prose", "technology_paragraph_join"}
                or source_id not in policy.get("source_ids", [])
                or policy != AGES_III_TECHNOLOGY_DOCUMENTATION_LINK_POLICY
                or expected != anchor
                or observed != expected_target):
            raise UnsupportedSerialization("Technology documentation-link prose differs from the exact authorized lead-in, source anchor, or punctuation")
        return expected, {
            "source_id": source_id,
            "kind": "user_authorized_technology_documentation_link_prose",
            "source": expected,
            "displayed": observed,
            "authorization_evidence": AGES_III_TECHNOLOGY_NARRATIVE_AUTHORIZATION,
        }
    if used <= {"technology_citation", "technology_paragraph_join"}:
        if "technology_paragraph_join" in used and (
            source_id not in AGES_III_TECHNOLOGY_INSERTED_SEPARATOR_SOURCE_IDS
            or not _is_authorized_ages_iii_presentation(authorization, source_id)
        ):
            raise UnsupportedSerialization("Technology paragraph join is outside the exact AGES III authorization")
        if observed != expected:
            raise UnsupportedSerialization("Technology presentation may not change its original displayed text")
        return observed, None
    if "abnt_figure_caption" in used:
        old_prefix, new_prefix = PRESENTATION_CAPTIONS[source_id]
        leading = expected[:len(expected) - len(expected.lstrip(" \t\r\n"))]
        caption_body = expected[len(leading):]
        if not caption_body.startswith(old_prefix):
            raise UnsupportedSerialization("Source caption no longer matches the audited Figure label")
        expected_target = leading + new_prefix + caption_body[len(old_prefix):]
        if source_id in AGES_IV_CAPTION_IDS:
            if not _is_authorized_ages_iv_presentation(authorization, source_id):
                raise UnsupportedSerialization("AGES IV figure caption is outside the exact authorized edition")
            target = expected_target
        elif source_id in {"text-p-1027", "text-p-1042", "text-p-1051", "text-p-1058", "text-p-1059", "text-p-1060", "text-p-1063", "text-p-1064"}:
            if not _is_authorized_ages_iii_presentation(authorization, source_id):
                raise UnsupportedSerialization("AGES III figure caption is outside the exact authorized edition")
            target = expected_target
        else:
            target = authorization["approved_presentation_changes"]["figure_caption_labels"][source_id]
        if target != expected_target or observed != expected_target:
            raise UnsupportedSerialization("Figure caption changes exceed the authorized Portuguese label and ABNT dash")
        return expected, {"source_id": source_id, "kind": "abnt_figure_caption_label", "source": expected, "displayed": expected_target}
    if "abnt_section_numbering" in used:
        source, target = PRESENTATION_HEADINGS[source_id]
        if source_id in AGES_IV_HEADING_IDS:
            authorized = _is_authorized_ages_iv_presentation(authorization, source_id)
        elif source_id in {"text-h-0074", "text-h-0097"}:
            authorized = _is_authorized_ages_iii_presentation(authorization, source_id)
        else:
            authorized = authorization["approved_presentation_changes"]["section_numbering"][source_id] == target
        if expected != source or not authorized or observed != target:
            raise UnsupportedSerialization("Section indicator differs from the narrowly authorized ABNT punctuation adjustment")
        return expected, {"source_id": source_id, "kind": "abnt_section_numbering", "source": source, "displayed": target}
    if "repository_link_sentence" in used:
        link_id = PRESENTATION_REPOSITORY_PARAGRAPHS.get(source_id, source_id)
        rule = PRESENTATION_REPOSITORY_LINKS.get(link_id)
        if rule is None or expected != rule["source_anchor"]:
            raise UnsupportedSerialization("Repository prose is not attached to an original authorized anchor")
        if link_id in {"text-a-0146", "text-a-0147"} and not _is_authorized_ages_iv_presentation(authorization, source_id):
            raise UnsupportedSerialization("Repository sentence is outside the exact AGES IV authorization")
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


def _citation_keys_in_fragment(value):
    r"""Return ordered cite keys from the narrow supported \cite{key[,key]} form."""
    observed = []
    for token in commands(strip_comments(value)):
        if token.name != "cite":
            continue
        if token.starred or token.optionals or len(token.args) != 1:
            raise UnsupportedSerialization(r"Only unstarred \cite{key[,key]} is supported in technical citations")
        keys = [part.strip() for part in token.args[0].split(",")]
        if not keys or any(not re.fullmatch(r"[A-Za-z0-9:_-]+", key) for key in keys):
            raise UnsupportedSerialization("Malformed author-date citation key")
        observed.extend(keys)
    return observed

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
    allowed = {"tex_quotes", "tex_dashes", "canonical_unicode", "original_whitespace", "inline_tab_layout", "reference_paragraph_layout", "abnt_figure_caption", "abnt_section_numbering", "approved_figure_cross_reference", "repository_link_sentence", "wiki_reference_sentence", "technology_citation", "technology_paragraph_join", "approved_group_label_removal", "approved_technology_narrative", "technology_documentation_link_prose", "approved_internal_tab_removal", "frontmatter_title", "frontmatter_placeholder", "frontmatter_omission", "document_reordering_numbering"}
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
    # Font declarations may be nested to cancel an inherited ODF character
    # style (for example bold + medium, or italic + upright). The conservative
    # projection removes only these presentation wrappers and still compares
    # every visible character exactly.
    wrappers = {"textbf", "textmd", "textit", "textup", "emph", "texttt", "textrm", "textsf", "textnormal", "underline", "mbox"}
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
            if name == "cite":
                if "technology_citation" not in serializations:
                    raise UnsupportedSerialization("A citation requires the exact verified technology_citation policy")
                if i >= len(text) or text[i] != "{":
                    raise UnsupportedSerialization("Only a single braced cite-key group is supported")
                keys, i = _group(text, i, "{", "}")
                parts = [key.strip() for key in keys.split(",")]
                if not parts or any(not re.fullmatch(r"[A-Za-z0-9:_-]+", key) for key in parts):
                    raise UnsupportedSerialization("Citation keys are malformed")
                # Exact authorized key identity/order is checked against the
                # per-source ledger before this parser is called.
                continue
            if name == "space":
                if "technology_citation" in serializations and text[i:].startswith(r"\cite{"):
                    # TeX spacing inserted only before the citation is part of
                    # that citation apparatus, not source wording.
                    continue
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


def _parse_user_supplied_markup(value: str) -> tuple[str, list[tuple[str, str]]]:
    """Project the narrowly supported user-authored inline Markdown markers."""
    if not isinstance(value, str) or "\n" in value or "\r" in value:
        raise UnsupportedSerialization("User-supplied source paragraphs must be single-line strings")
    marker = re.compile(r"\*([^*`]+)\*|`([^*`]+)`")
    display, formatting, cursor = [], [], 0
    for match in marker.finditer(value):
        plain = value[cursor:match.start()]
        if "*" in plain or "`" in plain:
            raise UnsupportedSerialization("Unpaired or unsupported inline Markdown marker")
        display.append(plain)
        if match.group(1) is not None:
            formatting.append(("italic", match.group(1)))
            display.append(match.group(1))
        else:
            formatting.append(("code", match.group(2)))
            display.append(match.group(2))
        cursor = match.end()
    tail = value[cursor:]
    if "*" in tail or "`" in tail:
        raise UnsupportedSerialization("Unpaired or unsupported inline Markdown marker")
    display.append(tail)
    return "".join(display), formatting


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
    """Project explicitly audited ODF inline containers onto text order.

    In the ODF source, the caption text is nested in a draw frame embedded at
    the start of text-p-0961, before that paragraph's visible text. The flat
    source_record_ids list records the parent paragraph first, so this exact,
    structure-checked projection corrects only that ordering comparison.

    AGES IV's database paragraph uses the same ODF pattern, with its figure
    and caption nested inside an external-link frame before the paragraph's
    visible link text. Its target also places the figure before that text.
    """
    if unit_id == "chapter-06-text-h-0109":
        parent_id = "text-p-1343"
        link_id = "text-a-0149"
        frame_id = "draw-frame-0065"
        textbox_id = "draw-text-box-0041"
        nested_text_id = "text-p-1344"
        image_frame_id = "draw-frame-0066"
        image_id = "draw-image-0025"
        positions = {rid: index for index, rid in enumerate(source_ids)}
        parent = records.get(parent_id, {})
        link = records.get(link_id, {})
        frame = records.get(frame_id, {})
        textbox = records.get(textbox_id, {})
        nested_text = records.get(nested_text_id, {})
        image_frame = records.get(image_frame_id, {})
        image = records.get(image_id, {})
        segments = parent.get("inline_segments")
        structure_matches = (
            source_ids.count(parent_id) == 1
            and source_ids.count(nested_text_id) == 1
            and positions.get(nested_text_id, -2) > positions.get(parent_id, -1)
            and isinstance(segments, list)
            and bool(segments)
            and segments[0] == {"kind": "embedded-block", "record_id": frame_id}
            and not any(segment.get("kind") == "embedded-block" for segment in segments[1:])
            and any(segment.get("kind") == "text" and segment.get("text") for segment in segments[1:])
            and link.get("parent_id") == parent_id
            and bool(link.get("href"))
            and frame.get("parent_id") == link_id
            and textbox.get("parent_id") == frame_id
            and nested_text.get("parent_id") == textbox_id
            and image_frame.get("parent_id") == nested_text_id
            and image.get("parent_id") == image_frame_id
            and link_id in image.get("ancestor_ids", [])
            and link_id in nested_text.get("ancestor_ids", [])
        )
        if not structure_matches:
            return list(source_ids), "AGES IV Banco de Dados linked-frame order no longer matches its audited ODF hierarchy"
        projected = list(source_ids)
        parent_position = positions[parent_id]
        nested_position = positions[nested_text_id]
        projected.pop(nested_position)
        projected.insert(parent_position, nested_text_id)
        return projected, None

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


def _verify_linked_figure_source(unit_id, image_id, token, records, preserved_links):
    """Bind the one authorized linked figure macro to its exact ODF ancestor."""
    expected = AGES_IV_LINKED_FIGURE
    if (unit_id, image_id) != (expected["unit_id"], expected["image_id"]):
        raise ValueError("Linked figure macro is authorized only for the AGES IV database image occurrence")
    if token.name != "memorialfigurelinked" or len(token.args) != 6 or token.optionals or token.starred:
        raise ValueError("Linked figure must use the verified six-argument macro without options")

    image = records.get(image_id, {})
    caption = records.get(expected["caption_id"], {})
    link = records.get(expected["link_id"], {})
    parent = records.get(expected["paragraph_id"], {})
    frame = records.get(expected["frame_id"], {})
    textbox = records.get(expected["textbox_id"], {})
    image_frame = records.get(expected["image_frame_id"], {})
    segments = parent.get("inline_segments")
    hierarchy_matches = (
        _kind(link) == "a"
        and link.get("href")
        and link.get("parent_id") == expected["paragraph_id"]
        and isinstance(segments, list)
        and bool(segments)
        and segments[0] == {"kind": "embedded-block", "record_id": expected["frame_id"]}
        and frame.get("parent_id") == expected["link_id"]
        and textbox.get("parent_id") == expected["frame_id"]
        and caption.get("parent_id") == expected["textbox_id"]
        and image_frame.get("parent_id") == expected["caption_id"]
        and image.get("parent_id") == expected["image_frame_id"]
        and expected["link_id"] in image.get("ancestor_ids", [])
        and expected["link_id"] in caption.get("ancestor_ids", [])
    )
    if not hierarchy_matches:
        raise ValueError("ODF link-to-figure hierarchy differs from the audited source structure")

    matching_links = [item for item in preserved_links if item.get("source_id") == expected["link_id"]]
    if len(matching_links) != 1:
        raise ValueError("The linked figure needs exactly one preserved-link record for its ODF ancestor")
    original_url = link["href"]
    preserved_url = matching_links[0].get("original_url")
    observed_url = _url(token.args[5])
    if not _valid_url(original_url) or preserved_url != original_url or observed_url != _url(original_url):
        raise ValueError("Linked figure URI differs from the exact preserved ODF ancestor URL")
    return observed_url


def audit_conversion(manifest: dict, ledger: dict, repo: Path, unit_id: str | None = None) -> dict:
    repo = repo.resolve()
    findings, differences, facts = [], {}, {"scope": unit_id or "all", "proof": "actual UTF-8 bytes and conservative lexical projection; not TeX execution", "text_records_checked": 0, "text_records_matched": 0, "inline_tab_layout_records_matched": 0, "reference_paragraph_layout_records_matched": 0, "links_checked": 0, "images_checked": 0, "converted_units": 0, "partial_units": 0, "authorized_omitted_source_records": 0, "source_text_records": 0, "coverage_percent": 0.0, "approved_presentation_transformations": [], "user_supplied_content_checked": []}

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
        try:
            formatting_authorization = _load_ages_i_ii_formatting_authorization(repo, uid)
            formatting_authorization_error = None
        except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
            formatting_authorization = None
            formatting_authorization_error = str(exc)
        unit = units[uid]
        authorized_formatting_ids = (
            set(AGES_I_II_TECHNICAL_CITATIONS.get(uid, {}))
            | AGES_I_II_WIKI_UNITS.get(uid, set())
        )
        formatting_scope_present = (
            uid in AGES_I_II_FORMATTING_UNITS
            and bool(set(unit.get("record_ids", [])) & authorized_formatting_ids)
        )
        state = ledger_units.get(uid, {}).get("state", "unconverted")
        unit_ledger = ledger_units.get(uid, {})
        technology_paragraph_verified = False
        differences[uid] = []
        source_ids = unit.get("source_record_ids")
        if source_ids is None:
            source_ids = [rid for rid in unit.get("record_ids", []) if rid in records and _kind(records[rid]) in {"p", "h"} and records[rid].get("text") is not None]
        source_ids = [rid for rid in source_ids if rid in records and records[rid].get("text") is not None]
        full_source_ids = source_ids
        if state == "partial":
            try:
                partial_policy = _verify_ages_iv_partial_source_scope(
                    uid, unit, unit_ledger, full_source_ids, presentation_authorization
                )
                source_ids = list(partial_policy["included_source_record_ids"])
                facts["partial_units"] += 1
                facts["authorized_omitted_source_records"] += len(partial_policy["omitted_source_record_ids"])
                facts.setdefault("title_only_partial_units", []).append({
                    "unit_id": uid,
                    "included_source_record_ids": list(partial_policy["included_source_record_ids"]),
                    "omitted_source_record_ids": list(partial_policy["omitted_source_record_ids"]),
                    "completion_state": partial_policy["completion_state"],
                })
                report(
                    "authorized_title_only_partial_unit", uid,
                    "Only the user-approved source heading is included; the source body is intentionally omitted, so this unit remains PARTIAL and is not a completed conversion",
                    source_id=AGES_IV_TITLE_ONLY_HEADING_ID,
                    severity="warning",
                )
            except (ValueError, OSError, KeyError, TypeError, UnicodeError) as exc:
                report("invalid_authorized_partial_unit", uid, str(exc))
                continue
        facts["source_text_records"] += len(full_source_ids)
        if state == "unconverted":
            report("unit_unconverted", uid, "No conversion claimed; preservation has not been demonstrated", severity="warning")
            continue
        if state not in {"converted", "partial"}:
            report("invalid_unit_state", uid, f"Unknown state {state!r}")
            continue
        if state == "converted":
            facts["converted_units"] += 1
        # The specific cross-edition correction supersedes the old technology
        # presentation contracts. Never fall back to those contracts when a
        # new revision is claimed but invalid/unauthorized.
        if technology_prose.applies(repo, uid, unit_ledger):
            if uid not in technology_prose.UNITS and uid != technology_prose.AIV_UNIT:
                try:
                    technology_prose.verify(manifest, ledger, repo, uid)
                    report("invalid_technology_prose_revision", uid, "Technology prose revision is outside the three authorized source units")
                except (OSError, ValueError, KeyError, TypeError, UnicodeError, StopIteration) as exc:
                    report("invalid_technology_prose_revision", uid, str(exc))
                continue
            try:
                document_order_scope = (presentation_authorization or {}).get("approved_document_reordering", {}).get("scope", {})
                expected_technology_order_ids = sorted(
                    source_id
                    for table in ("heading_numbering", "figure_caption_numbering", "inline_reference_adjustments")
                    for source_id, spec in document_order_scope.get(table, {}).items()
                    if spec.get("unit_id") == uid
                )
                unit_mappings = unit_ledger.get("element_map", [])
                has_document_order_evidence = (
                    "document_reordering_authorization" in unit_ledger
                    or any("document_reordering_numbering" in item.get("serializations", []) for item in unit_mappings)
                )
                # Legacy ledgers remain auditable while a numbered chapter is
                # being migrated; once either marker appears, require the exact
                # per-unit authorization and validate every mapped display.
                order_ids = expected_technology_order_ids if has_document_order_evidence else None
                heading_display_text = None
                if has_document_order_evidence:
                    _verify_document_order_unit(
                        uid, unit_ledger, records, presentation_authorization,
                        lambda mapping: fragment(mapping)[3],
                    )
                    heading_id = unit.get("heading_id")
                    heading_spec = document_order_scope.get("heading_numbering", {}).get(heading_id)
                    if not isinstance(heading_spec, dict) or heading_spec.get("unit_id") != uid:
                        raise ValueError("Technology heading has no exact authorized document-order display")
                    heading_display_text = heading_spec.get("target_text")
                revision = technology_prose.verify(
                    manifest, ledger, repo, uid,
                    document_reordering_ids=order_ids,
                    heading_display_text=heading_display_text,
                )
                facts.setdefault("technology_prose_revisions", []).append(revision)
                facts["text_records_checked"] += revision["source_text_records_checked"]
                facts["links_checked"] += revision["links_inventoried"]
                facts["approved_presentation_transformations"].append({
                    "kind": "user_authorized_project_technology_prose_v2",
                    "unit_id": uid,
                    "authorization_evidence": technology_prose.AUTHORIZATION,
                    "lexical_equality_claimed": False,
                    "semantic_review": "PENDING",
                })
                differences[uid].append({
                    "kind": "authorized_narrative_rewrite",
                    "status": "PENDING_INDEPENDENT_SEMANTIC_REVIEW",
                    "source_ids": list(source_ids),
                    "authorization_evidence": technology_prose.AUTHORIZATION,
                })
                report(
                    "technology_prose_independent_review_required", uid,
                    "Scoped provenance, source coverage, frozen bibliography and attached citations verified; lexical equality is not claimed. Independent semantic and visual audits remain PENDING",
                    severity="warning",
                )
            except (OSError, ValueError, KeyError, TypeError, UnicodeError, StopIteration) as exc:
                report("invalid_technology_prose_revision", uid, str(exc))
            continue
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
                            "citation_keys": [
                                key for source_id in AGES_II_TECHNOLOGY_TEXT_IDS
                                for key in AGES_I_II_TECHNICAL_CITATIONS.get(uid, {}).get(source_id, [])
                            ],
                            "pending_sources": ["text-a-0126", "text-p-0839"],
                            "assigned_access_date": "2024-10-15",
                        })
                        report("approved_technology_paragraph_review_required", uid, "Seven source technology entries remain in order as one paragraph; all 22 authorized technology citations are linked to bibliography entries. The exact Graph API Explorer page and the Docker homepage's technical adequacy remain pending. Human presentation review remains required", source_id="text-list-0109", severity="warning")
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
        if uid in AGES_III_UNITS:
            expected_citations = AGES_III_TECHNICAL_CITATIONS.get(uid, {})
        elif uid in AGES_IV_UNITS:
            expected_citations = AGES_IV_TECHNICAL_CITATIONS.get(uid, {})
        else:
            expected_citations = AGES_I_II_TECHNICAL_CITATIONS.get(uid, {}) if formatting_scope_present else {}
        citation_policy = unit_ledger.get("technology_citations")
        if expected_citations:
            expected_policy = {
                "authorization_evidence": (
                    AGES_III_AUTHORIZATION if uid in AGES_III_UNITS
                    else AGES_IV_AUTHORIZATION if uid in AGES_IV_UNITS
                    else AGES_I_II_FORMATTING_AUTHORIZATION
                ),
                "source_text_changed": False,
                "source_id_to_keys": expected_citations,
            }
            try:
                if uid in AGES_III_UNITS or uid in AGES_IV_UNITS:
                    if presentation_authorization is None:
                        raise ValueError(presentation_authorization_error or "Missing edition authorization")
                elif formatting_authorization is None:
                    raise ValueError(formatting_authorization_error or "Missing formatting authorization")
                if citation_policy != expected_policy:
                    raise ValueError("Citation ledger must exactly match the approved source ID/key map")
                bibliography = safe_path("relatorio_AGES_eduardo/bibliografia/bibliografia.bib").read_text(encoding="utf-8")
                bibliography_keys = set(re.findall(r"(?m)^@\w+\{([^,]+),", bibliography))
                for rid, expected_keys in expected_citations.items():
                    mapping = by_id.get(rid)
                    if mapping is None or "technology_citation" not in mapping.get("serializations", []):
                        raise ValueError(f"{rid} requires the technology_citation serialization")
                    if _citation_keys_in_fragment(fragment(mapping)[3]) != expected_keys:
                        raise ValueError(f"Citations on {rid} differ from the approved ordered keys")
                    if any(key not in bibliography_keys for key in expected_keys):
                        raise ValueError(f"A verified citation on {rid} has no integrated bibliography entry")
                if uid in AGES_III_UNITS:
                    evidence = json.loads(safe_path("migration/evidence/references/ages-iii.json").read_text(encoding="utf-8"))
                    _verify_ages_iii_bibliography_entries(bibliography, evidence, records)
                elif uid in AGES_IV_UNITS:
                    evidence = json.loads(safe_path("migration/evidence/references/ages-iv.json").read_text(encoding="utf-8"))
                    supplemental_authorization = json.loads(
                        safe_path(AGES_IV_SUPPLEMENTAL_CITATION_AUTHORIZATION).read_text(encoding="utf-8")
                    )
                    _verify_ages_iv_bibliography_entries(
                        bibliography, evidence, records, supplemental_authorization,
                    )
                for rid, mapping in by_id.items():
                    if "technology_citation" in mapping.get("serializations", []) and rid not in expected_citations:
                        raise ValueError(f"Unapproved technology_citation serialization on {rid}")
                if uid == "chapter-05-text-h-0085":
                    technology_source_path = safe_path(unit_ledger.get("tex_path"))
                    _verify_ages_iii_technology_paragraph(
                        technology_source_path.read_text(encoding="utf-8"), unit_ledger, unit, records,
                        presentation_authorization,
                    )
                    facts["technology_narrative_semantic_review"] = {
                        "status": "PENDING",
                        "source_ids": list(AGES_III_TECHNOLOGY_NARRATIVE_TEXT_IDS),
                        "authorization": AGES_III_TECHNOLOGY_NARRATIVE_AUTHORIZATION,
                    }
                    report(
                        "approved_technology_narrative_review_required", uid,
                        "The user authorized a single project-context paragraph; lexical equality is not claimed for the listed source paragraphs. Independent source-to-prose review is required before the unit can be considered complete",
                        source_id="text-h-0085", severity="warning",
                    )
                facts.setdefault("technical_citations_verified", 0)
                facts["technical_citations_verified"] += sum(map(len, expected_citations.values()))
            except (ValueError, OSError, KeyError, UnicodeError, TypeError, UnsupportedSerialization) as exc:
                report("invalid_technology_citation_apparatus", uid, str(exc))
        elif citation_policy is not None or any("technology_citation" in item.get("serializations", []) for item in mappings):
            report("invalid_technology_citation_apparatus", uid, "Technology citation apparatus is outside the exact approved source IDs")
        if uid in AGES_III_UNITS:
            expected_wiki_ids = AGES_III_WIKI_UNITS.get(uid, set())
        elif uid in AGES_IV_UNITS:
            expected_wiki_ids = AGES_IV_WIKI_UNITS.get(uid, set())
        else:
            expected_wiki_ids = AGES_I_II_WIKI_UNITS.get(uid, set()) if formatting_scope_present else set()
        wiki_override_ids = {
            rid for rid, mapping in by_id.items()
            if "wiki_reference_sentence" in mapping.get("serializations", [])
        }
        wiki_policy = unit_ledger.get("wiki_link_overrides")
        if expected_wiki_ids:
            expected_wiki_policy = {
                "authorization_evidence": (
                    AGES_III_AUTHORIZATION if uid in AGES_III_UNITS
                    else AGES_IV_AUTHORIZATION if uid in AGES_IV_UNITS
                    else AGES_I_II_FORMATTING_AUTHORIZATION
                ),
                "source_ids": sorted(expected_wiki_ids),
            }
            expected_wiki_serializations = {rid for rid in expected_wiki_ids}
            try:
                if uid in AGES_III_UNITS:
                    if presentation_authorization is None:
                        raise ValueError(presentation_authorization_error or "Missing AGES III authorization")
                elif uid in AGES_IV_UNITS:
                    if presentation_authorization is None:
                        raise ValueError(presentation_authorization_error or "Missing AGES IV authorization")
                elif formatting_authorization is None:
                    raise ValueError(formatting_authorization_error or "Missing formatting authorization")
                if wiki_policy != expected_wiki_policy or wiki_override_ids != expected_wiki_serializations:
                    raise ValueError("Wiki-link overlay ledger must exactly match its authorized paragraph/anchor IDs")
            except (ValueError, TypeError) as exc:
                report("invalid_wiki_link_presentation", uid, str(exc))
        elif wiki_policy is not None or wiki_override_ids:
            report("invalid_wiki_link_presentation", uid, "Wiki-link prose is outside the exact approved source IDs")
        dedicated_presentation_kinds = {
            # These transformations each have a dedicated exact verifier in
            # this audit path; they must not require a duplicate generic policy.
            "repository_link_sentence", "wiki_reference_sentence",
            "approved_group_label_removal", "approved_technology_narrative",
            "technology_documentation_link_prose", "approved_internal_tab_removal",
            "frontmatter_title", "frontmatter_placeholder", "frontmatter_omission",
            "technology_citation", "technology_paragraph_join", "document_reordering_numbering",
        }
        presentation_override_kinds = set(PRESENTATION_SERIALIZATIONS) - dedicated_presentation_kinds
        separately_verified_presentation_ids = set().union(*(
            PRESENTATION_SERIALIZATIONS[kind]
            for kind in dedicated_presentation_kinds
            if kind in PRESENTATION_SERIALIZATIONS
        ))
        presentation_override_ids = {
            rid for rid, mapping in by_id.items()
            if set(mapping.get("serializations", [])) & presentation_override_kinds
        }
        if uid == "chapter-05-text-h-0085" and any(
            "technology_paragraph_join" in item.get("serializations", []) for item in by_id.values()
        ):
            presentation_override_ids |= set(by_id) & set(AGES_III_TECHNOLOGY_ELEMENT_IDS)
        repository_link_style_verified = False
        # A unit fixture may exercise one record from a larger real unit.
        # Use record_ids (not source_record_ids, which intentionally excludes
        # anchors and other nonparagraph records) to enforce exactly the
        # approved overlays that belong to this selected manifest unit.
        expected_override_ids = (
            PRESENTATION_OVERRIDES_BY_UNIT.get(uid, set()) & set(unit.get("record_ids", []))
        )
        document_order_scope = (presentation_authorization or {}).get("approved_document_reordering", {}).get("scope", {})
        scoped_document_order_ids = {
            source_id
            for table in ("heading_numbering", "figure_caption_numbering", "inline_reference_adjustments")
            for source_id, spec in document_order_scope.get(table, {}).items()
            if spec.get("unit_id") == uid
        }
        document_order_ids = {
            rid for rid, mapping in by_id.items()
            if "document_reordering_numbering" in mapping.get("serializations", [])
        }
        document_order_active = (
            bool(document_order_ids)
            or "document_reordering_authorization" in unit_ledger
        )
        expected_document_order_ids = scoped_document_order_ids if document_order_active else set()
        if expected_document_order_ids or document_order_ids or "document_reordering_authorization" in unit_ledger:
            try:
                policy = unit_ledger.get("document_reordering_authorization")
                expected_policy = {
                    "authorization_evidence": DOCUMENT_ORDER_AUTHORIZATION,
                    "source_ids": sorted(expected_document_order_ids),
                }
                if (presentation_authorization is None
                        or "approved_document_reordering" not in presentation_authorization
                        or policy != expected_policy
                        or document_order_ids != expected_document_order_ids):
                    raise ValueError("Document-order ledger must cover exactly the authorized source IDs in this unit")
                report("approved_document_order_review_required", uid,
                       "Heading/caption renumbering is source-bound to user approval; final document-order review remains pending",
                       severity="warning")
            except (ValueError, OSError, KeyError, UnicodeError, TypeError) as exc:
                report("invalid_document_reordering_authorization", uid, str(exc))
        # Numbering/caption maps supersede prior style serialization for the
        # same IDs. Keep any prior authorization as provenance, but require its
        # visible serialization only for IDs outside the exact relocation map.
        active_expected_override_ids = (
            expected_override_ids - expected_document_order_ids - separately_verified_presentation_ids
        )
        active_presentation_override_ids = presentation_override_ids - expected_document_order_ids
        override_policy_present = "approved_presentation_overrides" in unit_ledger
        if active_expected_override_ids or active_presentation_override_ids or override_policy_present:
            try:
                policy = unit_ledger.get("approved_presentation_overrides")
                evidence_path = PRESENTATION_AUTHORIZATION_BY_UNIT.get(uid)
                if evidence_path is None:
                    raise ValueError("Presentation overrides are outside the specifically authorized edition units")
                expected_policy = {"authorization_evidence": evidence_path, "source_ids": sorted(expected_override_ids)}
                if ((policy is not None and policy != expected_policy)
                        or (policy is None and active_expected_override_ids)
                        or active_presentation_override_ids != active_expected_override_ids):
                    raise ValueError("Presentation override ledger must cover exactly the user-authorized elements in this unit")
                if presentation_authorization is None:
                    raise ValueError(presentation_authorization_error or "Missing user authorization")
                repository_link_style_verified = True
                report("approved_presentation_review_required", uid, "Presentation overlays are narrowly authorized and source-linked; human presentation approval remains pending", severity="warning")
            except (ValueError, OSError, KeyError, UnicodeError, TypeError) as exc:
                report("invalid_repository_link_style", uid, str(exc))
        uses_original_whitespace = any("original_whitespace" in item.get("serializations", []) for item in mappings)
        inline_ids = {item.get("source_id") for item in mappings if "inline_tab_layout" in item.get("serializations", [])}
        if uid in AGES_II_UNITS:
            unit_inline_counts = AGES_II_INLINE_TAB_COUNTS
        elif uid in AGES_III_UNITS:
            unit_inline_counts = AGES_III_INLINE_TAB_COUNTS
        else:
            unit_inline_counts = INLINE_TAB_COUNTS
        inline_verified = False
        if inline_ids:
            try:
                policy = unit_ledger.get("inline_tab_layout")
                if not isinstance(policy, dict) or set(policy) != {"authorization_evidence", "source_ids"}:
                    raise ValueError("Inline tab layout requires exact authorization_evidence/source_ids policy")
                ages_ii_inline = uid in AGES_II_UNITS
                ages_iii_inline = uid in AGES_III_UNITS
                allowed_counts = unit_inline_counts
                evidence_path = AGES_II_INLINE_TAB_AUTHORIZATION if ages_ii_inline else AGES_III_AUTHORIZATION if ages_iii_inline else INLINE_TAB_AUTHORIZATION
                expected_source_order = [rid for rid in source_ids if rid in allowed_counts]
                if (policy["authorization_evidence"] != evidence_path
                        or not isinstance(policy["source_ids"], list)
                        or policy["source_ids"] != expected_source_order
                        or set(policy["source_ids"]) != inline_ids
                        or not inline_ids <= allowed_counts.keys()):
                    raise ValueError("Inline tab policy differs from the exact source IDs authorized for this edition")
                authorization = presentation_authorization if ages_ii_inline or ages_iii_inline else json.loads(safe_path(INLINE_TAB_AUTHORIZATION).read_text(encoding="utf-8"))
                if ages_ii_inline:
                    change_counts = (authorization or {}).get("approved_presentation_changes", {}).get("inline_tab_source_counts")
                    if change_counts != AGES_II_INLINE_TAB_COUNTS or uid not in (authorization or {}).get("scope", []):
                        raise ValueError("AGES II inline tab presentation evidence is incomplete or outside scope")
                elif ages_iii_inline:
                    if (authorization is None
                            or authorization.get("source", {}).get("sha256") != "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"
                            or uid not in authorization.get("scope", {}).get("units", [])
                            or set(inline_ids) - set(AGES_III_INLINE_TAB_COUNTS)):
                        raise ValueError("AGES III inline tab mapping is outside the exact authorized source unit and IDs")
                    if uid == "chapter-05-text-h-0085":
                        removal_ids = {
                            item.get("source_id") for item in mappings
                            if "approved_internal_tab_removal" in item.get("serializations", [])
                        }
                        if (removal_ids != {"text-p-1084"}
                                or unit_ledger.get("approved_internal_tab_removal") != AGES_III_INTERNAL_TAB_REMOVAL_POLICY
                                or authorization.get("approved_presentation_changes", {}).get("internal_tab_removal")
                                != AGES_III_INTERNAL_TAB_REMOVAL_POLICY):
                            raise ValueError("The AGES III internal-tab removal lacks its exact one-ID user approval")
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
                inline_message = (
                    "The original internal tab is source-mapped and its one-occurrence removal has exact user approval; PDF layout and human presentation approval remain separate"
                    if uid == "chapter-05-text-h-0085" and "text-p-1084" in inline_ids
                    else "Original internal tab tokens project exactly while the verified macro prints word spacing; PDF layout and human presentation approval remain separate"
                )
                report("inline_tab_layout_review_required", uid, inline_message, severity="warning")
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
                if uid in AGES_III_UNITS:
                    expected_tabs = AGES_III_LEADING_TAB_COUNTS.get(uid, {})
                    expected_layout_records = {rid: count for rid, count in expected_tabs.items() if rid in source_ids}
                    tab_paragraph_ids = _leading_tab_paragraph_ids(source_ids, records)
                    if (policy["authorization_evidence"] != AGES_III_AUTHORIZATION
                            or policy["source_ids"] != [rid for rid in source_ids if rid in expected_layout_records]
                            or reference_ids != set(expected_layout_records)
                            or tab_paragraph_ids != [rid for rid in source_ids if rid in expected_layout_records]
                            or set(tab_paragraph_ids) != set(expected_layout_records)
                            or presentation_authorization is None
                            or uid not in presentation_authorization.get("scope", {}).get("units", [])):
                        raise ValueError("AGES III zero-width prefix policy must cover exactly its source-bound leading tabs")
                    for rid, count in expected_layout_records.items():
                        original_text = records[rid]["text"]
                        leading_tabs = len(original_text) - len(original_text.lstrip("\t"))
                        if leading_tabs != count:
                            raise ValueError(f"Original tab count for {rid} differs from the source-bound AGES III policy")
                elif uid in AGES_II_UNITS:
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
                if (reference_verified or uid in AGES_II_UNITS or uid in AGES_III_UNITS
                        or uid in AGES_IV_UNITS or uid in HOORTECH_UNITS or uid in FRONTMATTER_UNITS):
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
        if (uid in AGES_III_UNITS or uid in AGES_IV_UNITS) and expected_citations:
            try:
                for rid, expected_keys in expected_citations.items():
                    mapping = by_id.get(rid)
                    if mapping is None:
                        continue
                    if uid in AGES_III_UNITS:
                        _verify_ages_iii_citation_alignment(
                            rid, fragment(mapping)[3], expected_keys,
                            mapping.get("serializations", []), macro_verified,
                            inline_verified, reference_verified,
                        )
                    else:
                        _verify_citation_alignment(
                            rid, fragment(mapping)[3], expected_keys,
                            AGES_IV_CITATION_TERMS.get(rid),
                            mapping.get("serializations", []), macro_verified,
                            inline_verified, reference_verified,
                        )
            except (ValueError, OSError, KeyError, UnicodeError, TypeError, UnsupportedSerialization) as exc:
                report("invalid_technology_citation_apparatus", uid, str(exc))
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
        linked_figure_verified = False
        linked_contract = unit_ledger.get("linked_figure_contract")
        if linked_contract is not None:
            try:
                if uid != AGES_IV_LINKED_FIGURE["unit_id"]:
                    raise ValueError("Linked-figure contract is authorized only for the AGES IV database unit")
                if not isinstance(linked_contract, dict) or set(linked_contract) != {"path", "sha256"}:
                    raise ValueError("Contract requires exactly path and sha256")
                if linked_contract.get("path") != AGES_IV_LINKED_FIGURE["macro_path"]:
                    raise ValueError("Linked-figure contract must use the dedicated shared macro file")
                linked_data = safe_path(linked_contract["path"]).read_bytes()
                if hashlib.sha256(linked_data).hexdigest() != linked_contract.get("sha256"):
                    raise ValueError("Missing/stale linked-figure contract SHA-256")
                linked_text = linked_data.decode("utf-8")
                found = [item for item in macro_definitions(linked_text) if item["name"] == "memorialfigurelinked"]
                if (len(found) != 1 or found[0]["declaration"] != "newcommand" or found[0]["arity"] != 6
                        or found[0]["optional_default"]
                        or canonical_macro_body(found[0]["body"]) != canonical_macro_body(MEMORIAL_FIGURE_LINKED_BODY)):
                    raise ValueError("memorialfigurelinked differs from the audited canonical definition")
                if re.search(r"\\(?:let|futurelet)\s*\\memorialfigurelinked\b", strip_comments(linked_text)):
                    raise ValueError("Linked-figure macro alias/redefinition")
                linked_figure_verified = True
            except (ValueError, OSError, KeyError, UnicodeError, TypeError) as exc:
                report("invalid_linked_figure_contract", uid, str(exc))
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
            if any(item["name"] == "memorialfigurelinked" for item in macro_definitions(text)) or re.search(r"\\(?:let|futurelet)\s*\\memorialfigurelinked\b", strip_comments(text)):
                report("linked_figure_macro_redefinition", uid, "Unit redefines audited linked-figure macro")
                linked_figure_verified = False
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
            ages_iii_join_projection = (
                uid == "chapter-05-text-h-0085"
                and rid in AGES_III_TECHNOLOGY_PARAGRAPH_JOIN_SOURCE_IDS
                and "original_whitespace" in serializations
            )
            try:
                if ages_iii_join_projection:
                    if not _source_whitespace_verified(serializations, macro_verified, reference_verified):
                        raise UnsupportedSerialization("AGES III technology paragraph join requires verified source whitespace markers")
                    expected = _normalize_ages_iii_technology_text(original)
                elif "frontmatter_omission" in serializations:
                    # An exact, source-bound omission is authorized for this
                    # frontmatter scope. Its original model text may contain
                    # trailing spaces, but none are emitted in the target.
                    expected = original
                else:
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
                    if uid == "chapter-05-text-h-0085":
                        exact_tab = AGES_III_TECHNOLOGY_LITERAL_TAB
                        removal_policy = (presentation_authorization or {}).get("approved_presentation_changes", {}).get("internal_tab_removal")
                        if ("approved_internal_tab_removal" not in serializations
                                or removal_policy != AGES_III_INTERNAL_TAB_REMOVAL_POLICY
                                or unit_ledger.get("approved_internal_tab_removal") != AGES_III_INTERNAL_TAB_REMOVAL_POLICY
                                or rid != exact_tab["source_id"]
                                or original.count(exact_tab["source_fragment"]) != 1
                                or value.count(exact_tab["target_fragment"]) != 1
                                or len(tabs) != 0
                                or r"\originalinlinetab{}" in value):
                            raise UnsupportedSerialization("Only the exact user-authorized removal of the tab inside ‘consultas t\tipadas’ is allowed")
                    else:
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
                if ages_iii_join_projection:
                    observed = _normalize_ages_iii_technology_text(observed)
                observed, presentation_transform = _project_approved_presentation(
                    rid, expected, observed, serializations, presentation_authorization, formatting_authorization
                )
                if presentation_transform is not None:
                    facts["approved_presentation_transformations"].append(presentation_transform)
            except (UnsupportedSerialization, ValueError) as exc:
                code = "invalid_presentation_serialization" if set(serializations) & set(PRESENTATION_SERIALIZATIONS) else "unsupported_serialization"
                report(code, uid, str(exc), rid)
                continue
            facts["text_records_checked"] += 1
            if (presentation_transform is not None
                    and presentation_transform.get("kind") in {
                        "user_authorized_technology_narrative_rewrite",
                        "user_authorized_technology_documentation_link_prose",
                    }
                    and not presentation_transform.get("lexical_equality", False)):
                facts.setdefault("authorized_text_rewrite_records", []).append(rid)
                continue
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
                all_wiki_rules = {**AGES_I_II_WIKI_SENTENCES, **AGES_III_WIKI_SENTENCES, **AGES_IV_WIKI_SENTENCES}
                wiki_rule = next((rule for rule in all_wiki_rules.values() if rule["source_id"] == rid), None)
                repository_rule = PRESENTATION_REPOSITORY_LINKS.get(rid)
                if wiki_rule is not None:
                    paragraph_id = next(
                        paragraph_id for paragraph_id, rule in all_wiki_rules.items()
                        if rule["source_id"] == rid
                    )
                    paragraph_mapping = by_id.get(paragraph_id)
                    if paragraph_mapping is None:
                        report("invalid_wiki_link_sentence", uid, "The linked wiki anchor has no independently mapped containing paragraph", rid)
                        continue
                    paragraph_path, _, _, paragraph_value = fragment(paragraph_mapping)
                    paragraph_serializations = paragraph_mapping.get("serializations", [])
                    paragraph_display = displayed_text(
                        paragraph_value, paragraph_serializations,
                        macro_contract_verified=macro_verified,
                        inline_layout_verified=inline_verified,
                        reference_layout_verified=reference_verified,
                    )
                    expected_paragraph_display = (
                        "\t" * wiki_rule["leading_tabs"] + wiki_rule["prefix"]
                        + wiki_rule["anchor"] + wiki_rule["suffix"]
                    )
                    paragraph_links = [candidate for candidate in commands(paragraph_value) if candidate.name == "href" and len(candidate.args) == 2]
                    hyperlink_only = not strip_comments(value[:token.start] + value[token.end:]).strip()
                    if ((uid in AGES_III_UNITS and not _is_authorized_ages_iii_presentation(presentation_authorization, paragraph_id))
                            or (uid in AGES_IV_UNITS and not _is_authorized_ages_iv_presentation(presentation_authorization, paragraph_id))
                            or (uid not in AGES_III_UNITS and (
                                uid not in AGES_IV_UNITS and (
                                formatting_authorization is None
                                or formatting_authorization.get("approved_wiki_link_sentences", {}).get(paragraph_id) != wiki_rule
                                )
                            ))
                            or "wiki_reference_sentence" not in policies
                            or "wiki_reference_sentence" not in paragraph_serializations
                            or record.get("href") != wiki_rule["href"]
                            or record.get("source_text") != wiki_rule["source_anchor"]
                            or observed_url != wiki_rule["href"]
                            or observed_anchor != wiki_rule["anchor"]
                            or not hyperlink_only
                            or paragraph_path != path
                            or paragraph_display != expected_paragraph_display
                            or len(paragraph_links) != 1
                            or _url(paragraph_links[0].args[0]) != wiki_rule["href"]
                            or displayed_text(
                                paragraph_links[0].args[1], paragraph_serializations,
                                macro_contract_verified=macro_verified,
                                inline_layout_verified=inline_verified,
                                reference_layout_verified=reference_verified,
                            ) != wiki_rule["anchor"]):
                        report("invalid_wiki_link_sentence", uid, "Wiki sentence, linked anchor, or preserved original URL differs from the exact user-approved form", rid)
                    else:
                        facts["approved_presentation_transformations"].append({
                            "source_id": rid, "kind": "wiki_link_in_prose",
                            "source": wiki_rule["source_anchor"],
                            "displayed": paragraph_display,
                            "href": observed_url,
                        })
                elif repository_rule is not None:
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
                tokens = [token for token in commands(actual[rid][3]) if token.name in {"includegraphics", "memorialfigure", "memorialfigurelinked"} and token.args]
                if len(tokens) != 1:
                    raise ValueError("Image interval must contain exactly one includegraphics")
                token = tokens[0]
                if token.name in {"memorialfigure", "memorialfigurelinked"}:
                    if token.name == "memorialfigurelinked":
                        if (not figure_verified or not linked_figure_verified or len(token.args) != 6
                                or token.optionals or token.starred):
                            raise ValueError("memorialfigurelinked requires its separately verified six-argument contract")
                        _verify_linked_figure_source(uid, rid, token, records, unit_ledger.get("preserved_links", []))
                    else:
                        if not figure_verified or len(token.args) != 5 or token.optionals or token.starred:
                            raise ValueError("memorialfigure requires verified five-argument contract")
                        if (uid, rid) == (AGES_IV_LINKED_FIGURE["unit_id"], AGES_IV_LINKED_FIGURE["image_id"]):
                            raise ValueError("ODF links this figure itself; use the linked-figure macro to preserve that association")
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
        supplemental_content = unit_ledger.get("user_supplied_content")
        if supplemental_content is not None or uid == "ages-iv-sprint-2":
            try:
                if uid != "ages-iv-sprint-2":
                    raise ValueError("User-supplied narrative supplement is authorized only for AGES IV Sprint 2")
                if not isinstance(supplemental_content, dict) or set(supplemental_content) != {
                    "authorization_evidence", "authorization_sha256", "content_map"
                }:
                    raise ValueError("Sprint 2 user-supplied content requires the exact authorization and content_map fields")
                if supplemental_content.get("authorization_evidence") != AGES_IV_SPRINT2_USER_CONTENT_AUTHORIZATION:
                    raise ValueError("Sprint 2 supplement points to an unapproved authorization record")
                auth_path = safe_path(AGES_IV_SPRINT2_USER_CONTENT_AUTHORIZATION)
                auth_bytes = auth_path.read_bytes()
                if hashlib.sha256(auth_bytes).hexdigest() != supplemental_content.get("authorization_sha256"):
                    raise ValueError("User-supplied content authorization hash is stale")
                authorization = json.loads(auth_bytes.decode("utf-8"))
                expected_instruction = "Agora vamos colocar o relatório da Sprint 2 (edição AGES IV) e também a caixa introspectiva."
                if (authorization.get("schema_version") != 1
                        or authorization.get("record_type") != "user_supplied_content_authorization"
                        or authorization.get("approval_status") != "authorized_for_inclusion_pending_human_review"
                        or authorization.get("unit_id") != uid
                        or authorization.get("user_instruction") != expected_instruction
                        or authorization.get("source") != {
                            "type": "direct_user_message",
                            "source_odt_path": "RELATORIO_ATUAL.odt",
                            "source_odt_sha256": "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef",
                            "odt_relationship": "The ODF unit contains only its Sprint 2 heading; these seven paragraphs were supplied separately by the user and are not represented as ODT source records.",
                        }):
                    raise ValueError("User authorization record does not match the exact Sprint 2 addition and frozen source relationship")
                source_content = authorization.get("content")
                if (not isinstance(source_content, list)
                        or [item.get("content_id") for item in source_content if isinstance(item, dict)] != list(AGES_IV_SPRINT2_USER_CONTENT_IDS)
                        or len(source_content) != len(AGES_IV_SPRINT2_USER_CONTENT_IDS)):
                    raise ValueError("Supplement authorization must contain the exact seven Sprint 2 report/reflection paragraphs in order")
                content_map = supplemental_content.get("content_map")
                if not isinstance(content_map, list) or [item.get("content_id") for item in content_map if isinstance(item, dict)] != list(AGES_IV_SPRINT2_USER_CONTENT_IDS) or len(content_map) != len(AGES_IV_SPRINT2_USER_CONTENT_IDS):
                    raise ValueError("Ledger content_map must cover all seven authorized paragraphs exactly once and in order")
                title_mapping = by_id.get("text-h-0119")
                if title_mapping is None or "text-h-0119" not in actual:
                    raise ValueError("Sprint 2 title mapping is required before the supplied narrative")
                heading_path, heading_start, _, _ = actual["text-h-0119"]
                unit_target = safe_path(unit_ledger.get("tex_path"))
                supplemental_positions = []
                checked_content_ids = []
                for source_item, mapping in zip(source_content, content_map):
                    expected_keys = {"content_id", "kind", "source_markup", "sha256"}
                    if set(source_item) != expected_keys:
                        raise ValueError("Supplement source record has unknown or missing fields")
                    content_id = source_item.get("content_id")
                    if source_item.get("kind") not in {"report_paragraph", "reflection_paragraph"}:
                        raise ValueError(f"Unsupported user-supplied paragraph kind for {content_id}")
                    source_markup = source_item.get("source_markup")
                    if not isinstance(source_markup, str) or hashlib.sha256(source_markup.encode("utf-8")).hexdigest() != source_item.get("sha256"):
                        raise ValueError(f"Source hash is missing or invalid for {content_id}")
                    expected_text, expected_formatting = _parse_user_supplied_markup(source_markup)
                    if set(mapping) != {"content_id", "target_file", "start_byte", "end_byte", "target_sha256"} or mapping.get("content_id") != content_id:
                        raise ValueError(f"Target mapping schema or ID is invalid for {content_id}")
                    path, start, end, value = fragment(mapping)
                    if path != unit_target or path not in file_order:
                        raise ValueError(f"User-supplied paragraph {content_id} must be inside the Sprint 2 unit file")
                    expansion_position = next((
                        start + delta for lo, hi, delta in expansion_positions.get(path, []) if lo <= start and end <= hi
                    ), None)
                    heading_position = next((
                        heading_start + delta for lo, hi, delta in expansion_positions.get(heading_path, [])
                        if lo <= heading_start and actual["text-h-0119"][2] <= hi
                    ), None)
                    if expansion_position is None or heading_position is None or expansion_position <= heading_position:
                        raise ValueError(f"User-supplied paragraph {content_id} is not reachable after the Sprint 2 heading")
                    observed_text = displayed_text(value)
                    observed_formatting = []
                    for token in commands(strip_comments(value)):
                        if token.name not in {"textit", "texttt"}:
                            continue
                        if token.starred or token.optionals or len(token.args) != 1:
                            raise ValueError(f"Unsupported emphasis/code command in {content_id}")
                        observed_formatting.append(("italic" if token.name == "textit" else "code", displayed_text(token.args[0])))
                    if observed_text != expected_text or observed_formatting != expected_formatting:
                        raise ValueError(f"Displayed text or inline formatting differs from the user source for {content_id}")
                    supplemental_positions.append(expansion_position)
                    checked_content_ids.append(content_id)
                    derived_spans.setdefault(path, []).append((start, end))
                if supplemental_positions != sorted(supplemental_positions):
                    raise ValueError("Sprint 2 report and reflection paragraphs are not in the authorized source order")
                report(
                    "user_supplied_content_human_review_required", uid,
                    "Seven paragraphs are bound to a direct user message and checked against the LaTeX display projection; they are not ODT records, and PDF presentation still requires human review",
                    severity="warning",
                )
                facts["user_supplied_content_checked"].append({
                    "unit_id": uid,
                    "authorization_evidence": AGES_IV_SPRINT2_USER_CONTENT_AUTHORIZATION,
                    "content_ids": checked_content_ids,
                    "source_is_odt": False,
                    "lexical_display_and_inline_formatting_checked": True,
                })
            except (ValueError, OSError, KeyError, TypeError, UnicodeError, UnsupportedSerialization) as exc:
                report("invalid_user_supplied_content", uid, str(exc))
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
                if uid == "chapter-04-text-h-0043":
                    evidence = "migration/approvals/ages-ii-authorization.json"
                    auth = json.loads(safe_path(evidence).read_text())
                    placeholder_decision = any(
                        item.get("element") == "database diagram"
                        and "placeholder" in item.get("action", "").lower()
                        for item in auth.get("missing_material", [])
                    )
                    valid_edition_evidence = (
                        auth.get("schema_version") == 1
                        and auth.get("edition") == "ages-ii"
                        and auth.get("project") == "Indústria Digital"
                        and auth.get("odt_source") == "RELATORIO_ATUAL.odt"
                        and auth.get("source_sha256") == "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"
                        and uid in auth.get("authorized_units", [])
                        and auth.get("authorized") is True
                        and placeholder_decision
                    )
                else:
                    evidence = "migration/approvals/ages-i-authorization.json"
                    auth = json.loads(safe_path(evidence).read_text())
                    quote = "Vamos começar com AGES I. Lembre-se que os itens faltantes como arquitetura, banco de dados precisarão de placeholders que serão preenchidos posteriormente"
                    valid_edition_evidence = (
                        auth.get("schema_version") == 1
                        and uid in auth.get("scope", [])
                        and auth.get("kind") == "user_execution_authorization"
                        and auth.get("edition") == "AGES I / Easy Choose"
                        and auth.get("baseline_commit") == "68d159b9b4168f2a913f5c1e4913c30397310437"
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
        structural_commands = {"label", "input", "include", "listoffigures", "refstepcounter", "addcontentsline"}
        wrapper_commands = {"chapter", "section", "subsection", "subsubsection", "paragraph", "caption", "textbf", "textit", "emph", "texttt", "textrm", "textsf", "textnormal", "underline", "mbox"}
        declarations = {"centering", "raggedright", "raggedleft", "small", "large", "footnotesize", "normalsize", "bfseries", "itshape", "normalfont", "noindent", "indent", "par", "newline", "item", "vfill"}
        environments = {"figure", "figure*", "center", "flushleft", "flushright", "itemize", "enumerate", "description", "reflection", "reflexao", "introspection"}
        printable_ids = set(source_ids) | {rid for rid in allowed_ids if _kind(records.get(rid, {})) == "a"} | set(expected_images)
        for path in file_order:
            authorized_layout_command = False
            if uid == "resumo" and path.is_file() and path.relative_to(compilation_root).as_posix() == "conteudo/migracao/resumo.tex":
                target = path.read_text(encoding="utf-8")
                target_commands = list(commands(target))
                page_breaks = [token for token in target_commands if token.name == "clearpage"]
                figure_lists = [token for token in target_commands if token.name == "listoffigures"]
                summary_mapping = actual.get("text-p-0097")
                layout_authorization = (presentation_authorization or {}).get("scope", {}).get("layout_controls", {}).get("resumo")
                acronym_input = "\\input{conteudo/migracao/lista-de-siglas.tex}"
                acronym_input_positions = [match.start() for match in re.finditer(re.escape(acronym_input), target)]
                if (layout_authorization == FRONTMATTER_LAYOUT_CONTROLS["resumo"]
                        and len(page_breaks) == 2 and len(figure_lists) == 1 and len(acronym_input_positions) == 1
                        and summary_mapping is not None and summary_mapping[0] == path
                        and summary_mapping[2] <= len(target[:page_breaks[0].start].encode("utf-8"))
                        and page_breaks[0].end <= figure_lists[0].start
                        and page_breaks[1].start > acronym_input_positions[0]
                        and not target[page_breaks[1].end:].strip()):
                    authorized_layout_command = True
                elif page_breaks:
                    report("unauthorized_frontmatter_layout_control", uid,
                           "The two frontmatter page breaks must match the exact positions authorized after the summary placeholder and after the siglas input.",
                           path=str(path.relative_to(repo)))
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
                    elif token.name == "clearpage" and authorized_layout_command:
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
    elif facts["partial_units"]:
        status = "partial"
    elif facts["converted_units"] == 0:
        status = "unconverted"
    elif any(item["code"] == "unit_unconverted" for item in findings):
        status = "partial"
    else:
        status = "pass"
    return {"status": status, "findings": findings, "facts": facts, "differences": differences}
