"""Fail-closed traceability for narrowly scoped, authorized technology prose.

This validates scope, byte provenance and citation apparatus, NOT semantics.
The frozen I–III approval hash identifies the user's recorded instruction; it
cannot prove rewritten paragraphs retain source facts. AIV is separately
scoped to its exact authorized unit and evidence file. Semantic review remains
PENDING until an independent auditor compares the ODT and rendered result.
Legacy units retain their conservative lexical validator in preservation.py.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .latex import bib_keys, commands, strip_comments

AUTHORIZATION = "migration/approvals/ages-i-ii-iii-technology-prose-correction.json"
AUTHORIZATION_SHA256 = "8e33f6eaf6510aee20f660b64869bf3d4ded862f02e119eacb09bf0a3a58eecc"
FORMAT = "mariah-project-prose-v2"
SOURCE_DIGESTS = {
    "chapter-02-text-h-0012": "f51b99bffcdcba1068451c8eb5600026b9c4ed59e18016365ebeb819b06b7487",
    "chapter-04-text-h-0046": "ce1be3d0f26f52d7e80b19e7540065c40cfcaaa2d16968e3f37864e253b8ef17",
    "chapter-05-text-h-0085": "f10d9a957e1cb0728be5fb5187a463ba3fb721c3a721d561c4d2bee2788f7fd1",
}
UNITS = frozenset(SOURCE_DIGESTS)
AIV_UNIT = "chapter-06-text-h-0113"
AIV_AUTHORIZATION = "migration/approvals/ages-iv-partial-authorization.json"
AIV_CURATION = "migration/evidence/references/ages-iv.json"
AIV_BIBLIOGRAPHY = "relatorio_AGES_eduardo/bibliografia/bibliografia.bib"
AIV_BIBLIOGRAPHY_MARKER = b"% AGES IV / Recorda technology documentation."
# Exact authorized AGES IV suffix, including the two supplemental entries whose
# source URLs are not present in the ODT and are separately scoped by approval.
AIV_BIBLIOGRAPHY_EXTENSION_SHA256 = "8b1d2da0417447f6cef8de1fec0df23d20105d300022e39147d2a121285c9f41"
AIV_TEX_PATH = "relatorio_AGES_eduardo/conteudo/migracao/chapter-06-text-h-0113.tex"
AIV_REFERENCE_KEYS = {
    "text-a-0153": ("ages-iv-python", ("Python",)),
    "text-a-0154": ("ages-iv-fastapi", ("FastAPI",)),
    "text-a-0155": ("ages-iv-pydantic", ("Pydantic",)),
    "text-a-0156": ("ages-iv-react-native", ("React Native",)),
    "text-a-0157": ("ages-iv-expo", ("Expo",)),
    "text-a-0158": ("ages-iv-typescript", ("TypeScript",)),
    "text-a-0159": ("ages-iv-supabase", ("Supabase",)),
    "text-a-0160": ("ages-iv-postgresql", ("PostgreSQL",)),
    "text-a-0161": ("ages-iv-docker", ("Docker",)),
    "text-a-0162": ("ages-iv-github-actions", ("GitHub Actions",)),
    "text-a-0163": ("ages-iv-sonar", ("SonarQube / SonarCloud", "SonarQube", "SonarCloud")),
    "text-a-0164": ("ages-iv-pytest", ("Pytest",)),
    "text-a-0165": ("ages-iv-jest", ("Jest",)),
}
AGES_IV_HEADING = ("ages-iv", "text-h-0113", "6.2.5", "__RefHeading___Toc4841_3118176633", "text-bookmark-start-0075", "text-bookmark-end-0075")
HEADINGS = {
    "chapter-02-text-h-0012": ("ages-i", "text-h-0012", None, "__RefHeading___Toc4741_3118176633", "text-bookmark-start-0013", "text-bookmark-end-0013"),
    "chapter-04-text-h-0046": ("ages-ii", "text-h-0046", "4.2.5", "__RefHeading___Toc4781_3118176633", "text-bookmark-start-0043", "text-bookmark-end-0043"),
    "chapter-05-text-h-0085": ("ages-iii", "text-h-0085", "5.2.5", "__RefHeading___Toc4811_3118176633", "text-bookmark-start-0058", "text-bookmark-end-0058"),
    AIV_UNIT: AGES_IV_HEADING,
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _path(repo: Path, value: str) -> Path:
    if not isinstance(value, str) or Path(value).is_absolute():
        raise ValueError("Prose target must be a repository-relative path")
    path = (repo / value).resolve()
    if not path.is_relative_to(repo.resolve()):
        raise ValueError("Prose target escapes repository")
    return path


def source_digest(records: dict, record_ids: list[str]) -> str:
    projection = [
        {key: records[rid].get(key) for key in ("id", "type", "text", "source_text", "href", "attributes")}
        for rid in record_ids
    ]
    return _sha(json.dumps(projection, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def load_authorization(repo: Path) -> dict:
    data = _path(repo, AUTHORIZATION).read_bytes()
    if _sha(data) != AUTHORIZATION_SHA256:
        raise ValueError("Missing/stale technology prose authorization identity")
    approval = json.loads(data)
    if set(approval["units"]) != UNITS:
        raise ValueError("Technology prose authorization has wrong scope")
    return approval


def applies(repo: Path, uid: str, unit_ledger: dict) -> bool:
    """A present authorization supersedes old ledgers, never silently falls back.

    A claimed new-format ledger is dispatched even without its approval, so the
    caller reports an error rather than accidentally using a legacy verifier.
    """
    return "technology_prose_revision" in unit_ledger or (
        uid in UNITS and _path(repo, AUTHORIZATION).exists()
    )


def _source_text(record: dict) -> str:
    value = record.get("text")
    value = value if isinstance(value, str) else record.get("source_text")
    if not isinstance(value, str):
        raise ValueError("Text/link source record has no source text")
    return value


def _interval(mapping: dict, data: bytes, digest: str, tex_path: str) -> tuple[int, int, str]:
    if mapping.get("target_file") != tex_path or mapping.get("target_sha256") != digest:
        raise ValueError("Missing or stale prose target path/hash")
    start, end = mapping.get("start_byte"), mapping.get("end_byte")
    if type(start) is not int or type(end) is not int or not 0 <= start <= end <= len(data):
        raise ValueError("Invalid prose UTF-8 byte interval")
    data[:start].decode("utf-8")
    return start, end, data[start:end].decode("utf-8")


def _visible(text: str) -> str:
    """Project only the transparent text grammar allowed below; never run TeX."""
    value = strip_comments(text)
    value = re.sub(r"\\cite\s*\{[^{}]*\}", "", value)
    value = re.sub(r"\\(?:emph|textit|textbf|texttt|textrm|textsf|textnormal|underline)\s*", "", value)
    value = re.sub(r"\\(?:space|par|indent)\b(?:\{\})?", " ", value)
    value = re.sub(r"\\([#$%&_{}])", r"\1", value)
    return re.sub(r"\s+", " ", value.replace("{", "").replace("}", "")).strip()


def _grammar(text: str, uid: str, policy: dict) -> tuple[list, list, str]:
    """Check finite transparent grammar, exact heading scaffold, attached cites."""
    clean = strip_comments(text)
    tokens = list(commands(clean))
    scaffold_names = {"hypertarget", "subsection", "label", "refstepcounter", "addcontentsline"}
    transparent = {"emph", "textit", "textbf", "texttt", "textrm", "textsf", "textnormal", "underline"}
    escapes = set("#$%&_{}")
    noargs = {"space", "par", "indent"}
    citations, scaffolds = [], []
    for token in tokens:
        if token.name in scaffold_names:
            scaffolds.append(token)
        elif token.name == "cite":
            if token.starred or token.optionals or len(token.args) != 1 or token.args[0] not in policy["required_citation_keys"]:
                raise ValueError("Unknown, multiple, optional or malformed technology citation")
            key = token.args[0]
            before = _visible(clean[:token.start])
            terms = policy["citation_terms"][key]
            if not any(re.search(r"(?<![\w])" + re.escape(term) + r"$", before) for term in terms):
                raise ValueError(f"Detached technology citation {key}; must immediately follow an authorized technology term")
            # Only whitespace or an explicit space may separate name and cite.
            prefix = clean[:token.start]
            tail = re.sub(r"\\space(?:\{\})?\s*$", "", prefix).rstrip()
            if not any(tail.endswith(term.replace("#", r"\#")) or tail.endswith(term) for term in terms):
                raise ValueError(f"Detached technology citation {key}; intervening command/content")
            citations.append(token)
        elif token.name in transparent:
            if token.starred or token.optionals or len(token.args) != 1:
                raise ValueError("Unsupported transparent prose command")
        elif token.name in noargs:
            if token.starred or token.optionals or token.args not in ((), ("",)):
                raise ValueError("Unsupported prose spacing command")
        elif token.name in escapes:
            if token.starred or token.optionals or token.args:
                raise ValueError("Malformed literal escape")
        else:
            raise ValueError(f"Unauthorized prose TeX command \\{token.name}")
    edition, heading_id, number, anchor, _, _ = HEADINGS[uid]
    title = "Tecnologias utilizadas"
    full_title = f"{number} {title}" if number else title
    expected = [("hypertarget", (anchor, ""), False)]
    if number:
        expected.append(("refstepcounter", ("subsection",), False))
    expected.extend([("subsection", (full_title,), bool(number)), ("label", (f"{edition}:{heading_id}",), False)])
    if number:
        expected.append(("addcontentsline", ("toc", "subsection", full_title), False))
    actual = [(token.name, token.args, token.starred) for token in scaffolds]
    if actual != expected or any(token.optionals for token in scaffolds):
        raise ValueError("Technology heading/bookmark/numbering scaffold differs from approved structure")
    # Scaffolding must precede the prose; it may not hide a title in a paragraph.
    residue = clean
    for token in reversed(scaffolds):
        residue = residue[:token.start] + " " * (token.end - token.start) + residue[token.end:]
    if clean[:scaffolds[-1].end].strip() and _visible(residue[:scaffolds[-1].end]):
        raise ValueError("Technology narrative precedes or interrupts the heading scaffold")
    body = residue[scaffolds[-1].end:]
    visible = _visible(body)
    boilerplate = r"mais informa[çc][õo]es podem ser encontradas|mais detalhes podem ser encontrados"
    if policy.get("allow_narrative_documentation_mentions"):
        technology_names = sorted(
            {term for terms in policy["citation_terms"].values() for term in terms},
            key=len,
            reverse=True,
        )
        label_names = "|".join(re.escape(term) for term in technology_names)
        if re.search(boilerplate, visible, re.I) or re.search(
            rf"(?<!\w)Documenta[çc][ãa]o\s+(?:{label_names})(?!\w)", visible, re.I
        ):
            raise ValueError("Standalone documentation labels/repeated documentation boilerplate are revoked")
    elif re.search(rf"documenta[çc][ãa]o|{boilerplate}", visible, re.I):
        raise ValueError("Standalone documentation labels/repeated documentation boilerplate are revoked")
    if re.search(r"https?://|www\.", visible, re.I):
        raise ValueError("Technology prose URLs belong in traceability and bibliography, not the typeset explanation")
    # No label-style 'Technology:' survives the authorized narrative rewrite.
    all_terms = {term for terms in policy["citation_terms"].values() for term in terms}
    if any(re.search(r"(?<!\w)" + re.escape(term) + r"\s*:", visible) for term in all_terms):
        raise ValueError("Bare technology label with colon is not project prose")
    # Raw TeX math/alignment/parameter syntax is never ordinary text here.
    escaped = re.sub(r"\\[#$%&_{}]", " ", residue)
    if re.search(r"[$&#_^]", escaped):
        raise ValueError("Unescaped special syntax in technology prose")
    depth = 0
    for char in re.sub(r"\\[{}]", "", clean):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        if depth < 0:
            raise ValueError("Unbalanced prose grouping")
    if depth:
        raise ValueError("Unbalanced prose grouping")
    missing = set(policy["required_citation_keys"]) - {token.args[0] for token in citations}
    if missing:
        raise ValueError("Missing required technology citations: " + ", ".join(sorted(missing)))
    return scaffolds, citations, visible


def _matches_frozen_bibliography(repo: Path, data: bytes, expected_sha256: str) -> bool:
    """Allow only the exact centrally integrated AGES IV suffix after the frozen I–III bib."""
    if _sha(data) == expected_sha256:
        return True
    marker = data.find(AIV_BIBLIOGRAPHY_MARKER)
    if marker < 0:
        return False
    return (
        _sha(data[:marker]) == expected_sha256
        and _sha(data[marker:]) == AIV_BIBLIOGRAPHY_EXTENSION_SHA256
    )


def _verify_legacy(manifest: dict, ledger: dict, repo: Path, uid: str) -> dict:
    """Return honest traceability facts or fail closed; semantic equality is pending."""
    approval = load_authorization(repo)
    if uid not in UNITS:
        raise ValueError("Technology prose ledger is outside the three authorized units")
    policy = approval["units"][uid]
    unit = next(item for item in manifest["units"] if item["id"] == uid)
    unit_ledger = ledger["units"][uid]
    records = {item["id"]: item for item in manifest["records"]}
    if unit.get("record_ids") != policy["source_record_ids"] or unit.get("source_record_ids") != policy["source_text_ids"]:
        raise ValueError("Wrong/extra source IDs or order in technology prose unit")
    if source_digest(records, unit["record_ids"]) != SOURCE_DIGESTS[uid]:
        raise ValueError("Technology prose source records differ from frozen original extraction")
    source = approval["source"]
    if manifest.get("source", {}).get("sha256") != source["sha256"] or ledger.get("source_sha256") != source["sha256"] or _sha(_path(repo, source["path"]).read_bytes()) != source["sha256"]:
        raise ValueError("Immutable original ODT source hash differs")
    expected_revision = {"format": FORMAT, "authorization_evidence": AUTHORIZATION, "source_record_ids": unit["record_ids"], "semantic_review": "pending_independent_audit"}
    if unit_ledger.get("technology_prose_revision") != expected_revision:
        raise ValueError("Missing/stale scoped technology prose revision policy; legacy presentation is revoked")
    expected_keys = {"state", "tex_path", "asset_map", "bookmark_map", "pending", "element_map", "technology_prose_revision", "documentation_links", "structural_dispositions"}
    if set(unit_ledger) != expected_keys or unit_ledger.get("state") != "converted" or unit_ledger.get("asset_map") != []:
        raise ValueError("Prose ledger has missing fields, legacy policies or unauthorized assets")
    if not isinstance(unit_ledger["pending"], list) or not unit_ledger["pending"] or any(not isinstance(item, str) or not item.strip() for item in unit_ledger["pending"]):
        raise ValueError("Prose ledger must retain explicit unresolved review/reference limitations")
    if unit_ledger.get("tex_path") != policy["tex_path"]:
        raise ValueError("Wrong technology prose target path")
    data = _path(repo, policy["tex_path"]).read_bytes()
    digest = _sha(data)
    text = data.decode("utf-8")
    bibliography = approval["bibliography"]
    bib_data = _path(repo, bibliography["path"]).read_bytes()
    if not _matches_frozen_bibliography(repo, bib_data, bibliography["sha256"]):
        raise ValueError("Bibliography differs from frozen approved metadata")
    keys, duplicates = bib_keys(bib_data.decode("utf-8"))
    if duplicates or set(policy["required_citation_keys"]) - keys:
        raise ValueError("Required citations have no unique integrated bibliography entries")
    scaffolds, citations, _ = _grammar(text, uid, policy)
    heading_id = unit["heading_id"]
    # Every significant original paragraph/title/link is accounted for in order.
    significant = [rid for rid in unit["record_ids"] if records[rid]["type"] in {"text:p", "text:h", "text:a"}]
    mappings = unit_ledger["element_map"]
    if [item.get("source_id") for item in mappings] != significant:
        raise ValueError("Missing, duplicated, extra or reordered prose element mappings")
    omissions = set(policy["omitted_documentation_ids"])
    covered = bytearray(len(data))
    last_position = 0
    for mapping in mappings:
        rid = mapping["source_id"]
        if mapping.get("source_text_sha256") != _sha(_source_text(records[rid]).encode("utf-8")):
            raise ValueError(f"Stale original text hash on {rid}")
        start, end, value = _interval(mapping, data, digest, policy["tex_path"])
        if start < last_position:
            raise ValueError("Prose source mapping order changed")
        last_position = start
        disposition = mapping.get("disposition")
        if rid in omissions:
            expected = "omitted_documentation_link" if records[rid]["type"] == "text:a" else "omitted_documentation_label"
            if disposition != expected or start != end:
                raise ValueError("Only exactly authorized documentation labels/links may have empty target spans")
        elif rid == heading_id:
            if disposition != "heading" or value != _source_text(records[rid]):
                raise ValueError("Original technology heading changed")
            covered[start:end] = b"\1" * (end - start)
        else:
            if disposition != "narrative" or not _visible(value):
                raise ValueError("A source narrative record was omitted or disposed as documentation")
            covered[start:end] = b"\1" * (end - start)
    expected_structural = [{"source_id": rid, "disposition": "odf-container-replaced-by-prose", "authorization_evidence": AUTHORIZATION} for rid in unit["record_ids"] if rid not in significant]
    if unit_ledger.get("structural_dispositions") != expected_structural:
        raise ValueError("ODF container coverage/order differs from source")
    expected_links = [{"source_id": rid, "anchor": _source_text(records[rid]), "url": records[rid]["href"]} for rid in unit["record_ids"] if records[rid]["type"] == "text:a"]
    if unit_ledger.get("documentation_links") != expected_links:
        raise ValueError("Original documentation URL/anchor inventory changed or reordered")
    # Empty omission spans must occur between the surrounding source mappings,
    # not at arbitrary earlier positions; narrative spans may intentionally
    # overlap when one rewritten sentence represents a label and description.
    for index, mapping in enumerate(mappings):
        if mapping["source_id"] in omissions:
            prior_end = max((item["end_byte"] for item in mappings[:index] if item["source_id"] not in omissions), default=0)
            if mapping["start_byte"] < prior_end:
                raise ValueError("Omitted documentation is not at its logical source position")
    # Scaffold and literal whitespace/comments need no narrative source span.
    residue = bytearray(data)
    for index, flag in enumerate(covered):
        if flag:
            residue[index] = 32
    for token in scaffolds:
        start = len(text[:token.start].encode("utf-8"))
        end = len(text[:token.end].encode("utf-8"))
        residue[start:end] = b" " * (end - start)
    if strip_comments(residue.decode("utf-8")).strip():
        raise ValueError("Extra visible content or commands outside technology source spans")
    # Require exactly the inherited bookmark, including actual bytes and hash.
    edition, _, _, anchor, source_start, source_end = HEADINGS[uid]
    bookmarks = unit_ledger.get("bookmark_map")
    if not isinstance(bookmarks, list) or len(bookmarks) != 1:
        raise ValueError("Original technology heading bookmark missing")
    bookmark = bookmarks[0]
    required_bookmark = {"source_heading_id": heading_id, "source_name": anchor, "target_file": policy["tex_path"], "target_anchor": anchor, "command": "hypertarget", "source_start_id": source_start, "source_end_id": source_end}
    if any(bookmark.get(key) != value for key, value in required_bookmark.items()):
        raise ValueError("Original technology heading bookmark identity changed")
    _, _, bookmark_text = _interval(bookmark, data, digest, policy["tex_path"])
    if bookmark_text != rf"\hypertarget{{{anchor}}}{{}}":
        raise ValueError("Original technology heading bookmark bytes changed")
    return {"unit_id": uid, "format": FORMAT, "authorization_evidence": AUTHORIZATION, "authorization_sha256": AUTHORIZATION_SHA256, "target_sha256": digest, "source_text_records_checked": len(policy["source_text_ids"]), "element_records_checked": len(significant), "structural_records_checked": len(expected_structural), "links_inventoried": len(expected_links), "citation_occurrences_checked": len(citations), "required_citation_keys": policy["required_citation_keys"], "semantic_review": {"status": "PENDING", "reason": "Traceability and attached citations do not prove semantic preservation; independent ODT-to-result audit required"}, "reference_availability": "PENDING_AS_PREVIOUSLY_RECORDED", "visual_review": "PENDING", "lexical_equality_claimed": False}


def _entry(bibliography: str, key: str) -> str:
    match = re.search(rf"(?ms)^@online\{{{re.escape(key)},(?P<entry>.*?)^\}}", bibliography)
    if not match:
        raise ValueError(f"Missing @online bibliography entry for {key}")
    return match.group("entry")


def _field_line(entry: str, field: str, value: str, *, nested: bool = False) -> bool:
    rendered = "{{" + value + "}}" if nested else "{" + value + "}"
    pattern = rf"(?m)^\s*{re.escape(field)}\s*=\s*{re.escape(rendered)}\s*,?\s*$"
    return re.search(pattern, entry) is not None


def _verify_ages_iv(manifest: dict, ledger: dict, repo: Path) -> dict:
    """Validate the one AIV technology prose unit without broadening I–III scope."""
    authorization_path = _path(repo, AIV_AUTHORIZATION)
    authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
    if (authorization.get("schema_version") != 1
            or authorization.get("record_type") != "user_authorized_partial_edition_scope"
            or authorization.get("edition") != "AGES IV / Recorda"
            or AIV_UNIT not in authorization.get("scope", {}).get("units", [])
            or len(authorization.get("scope", {}).get("units", [])) != 17
            or authorization.get("source", {}).get("path") != "RELATORIO_ATUAL.odt"
            or authorization.get("source", {}).get("sha256") != "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"
            or authorization.get("source", {}).get("must_remain_unchanged") is not True
            or authorization.get("presentation_and_preservation", {}).get("technology_prose") != "use the user-approved Mariah project prose pattern with project-specific relationship and citations adjacent to technology names; retain all source facts and document original URLs in ledgers/references"):
        raise ValueError("AGES IV technology prose is outside its exact user-authorized scope")
    if uid := ledger.get("units", {}).get(AIV_UNIT):
        unit_ledger = uid
    else:
        raise ValueError("AGES IV technology prose ledger unit missing")
    unit = next((item for item in manifest.get("units", []) if item.get("id") == AIV_UNIT), None)
    if not unit:
        raise ValueError("AGES IV technology unit missing from manifest")
    records = {item["id"]: item for item in manifest.get("records", [])}
    significant_ids = [rid for rid in unit.get("record_ids", []) if rid in records and records[rid].get("type") in {"text:p", "text:h"}]
    if (any(rid not in records for rid in unit.get("record_ids", []))
            or significant_ids != unit.get("source_record_ids")):
        raise ValueError("AGES IV technology source IDs/order differ from extracted manifest")
    source = authorization["source"]
    source_bytes = _path(repo, source["path"]).read_bytes()
    if (_sha(source_bytes) != source["sha256"]
            or manifest.get("source", {}).get("sha256") != source["sha256"]
            or ledger.get("source_sha256") != source["sha256"]):
        raise ValueError("Immutable original ODT hash differs for AGES IV technology prose")
    expected_revision = {
        "format": "ages-iv-mariah-prose-v1",
        "authorization_evidence": AIV_AUTHORIZATION,
        "source_record_ids": unit["record_ids"],
        "semantic_review": "pending_independent_audit",
    }
    if unit_ledger.get("technology_prose_revision") != expected_revision:
        raise ValueError("Missing/stale AGES IV-specific technology prose policy")
    required_fields = {
        "state", "tex_path", "asset_map", "bookmark_map", "pending", "element_map",
        "technology_prose_revision", "documentation_links", "structural_dispositions",
        "candidate_citations", "omitted_documentation_fragments", "presentation_transformations",
    }
    if (set(unit_ledger) != required_fields or unit_ledger.get("state") != "converted"
            or unit_ledger.get("tex_path") != AIV_TEX_PATH or unit_ledger.get("asset_map") != []):
        raise ValueError("AGES IV technology prose ledger has missing, legacy, or unauthorized fields")
    if not isinstance(unit_ledger["pending"], list) or not unit_ledger["pending"]:
        raise ValueError("AGES IV technology prose must retain unresolved independent-review limitations")

    curation = json.loads(_path(repo, AIV_CURATION).read_text(encoding="utf-8"))
    if curation.get("edition") != "AGES IV / Recorda" or curation.get("record_type") != "reference_curator_evidence":
        raise ValueError("AGES IV reference curation evidence is missing or for the wrong edition")
    curated_sources = {}
    for item in curation.get("sources", []):
        for link_id in item.get("original_link_ids", []):
            if link_id in curated_sources:
                raise ValueError(f"Duplicate curated source mapping for {link_id}")
            curated_sources[link_id] = item
    expected_link_ids = list(AIV_REFERENCE_KEYS)
    candidate_list = unit_ledger["candidate_citations"]
    if not isinstance(candidate_list, list) or [item.get("source_link_id") for item in candidate_list] != expected_link_ids:
        raise ValueError("AGES IV citation candidates are missing, duplicated, or reordered")
    candidate_by_link = {item["source_link_id"]: item for item in candidate_list}
    required_keys, citation_terms = [], {}
    for link_id, (key, terms) in AIV_REFERENCE_KEYS.items():
        curated = curated_sources.get(link_id)
        candidate = candidate_by_link[link_id]
        source_record = records.get(link_id)
        if not curated or not source_record:
            raise ValueError(f"Missing original or curated citation evidence for {link_id}")
        observed_title = curated.get("observed_page_title")
        observed_author = curated.get("observed_responsibility")
        access_date = curated.get("access_date")
        expected_candidate = {
            "candidate_key": key,
            "technology_anchor": curated.get("original_anchor_text", [None])[0],
            "observed_responsibility_or_title": observed_author or observed_title,
            "basis": "author" if observed_author else "title",
            "url": source_record.get("href"),
            "curation_evidence": AIV_CURATION,
            "curated_source_id": curated.get("id"),
            "access_date": access_date,
            "author_date_label_year": curated.get("author_date_label_year"),
            "year_basis": curated.get("year_basis"),
            "candidate_only": True,
        }
        if curated.get("original_url") != source_record.get("href") or any(candidate.get(k) != v for k, v in expected_candidate.items()):
            raise ValueError(f"Citation candidate metadata/URL differs from original and curated evidence for {link_id}")
        if curated.get("retrieval") != "RETRIEVED_BY_WEB_TOOL; HTTP status not exposed":
            raise ValueError(f"Official citation destination was not retrieved for {link_id}")
        required_keys.append(key)
        citation_terms[key] = list(terms)

    text_path = _path(repo, AIV_TEX_PATH)
    data = text_path.read_bytes()
    digest = _sha(data)
    text = data.decode("utf-8")
    bibliography = _path(repo, AIV_BIBLIOGRAPHY).read_text(encoding="utf-8")
    legacy_approval = load_authorization(repo)
    bib_bytes = bibliography.encode("utf-8")
    if not _matches_frozen_bibliography(repo, bib_bytes, legacy_approval["bibliography"]["sha256"]):
        raise ValueError("AGES IV bibliography extension changed outside its exact scoped integration")
    keys, duplicates = bib_keys(bibliography)
    if duplicates or set(required_keys) - keys:
        raise ValueError("AGES IV technology citations have missing or duplicate bibliography keys")
    for link_id, (key, _) in AIV_REFERENCE_KEYS.items():
        curated = curated_sources[link_id]
        entry = _entry(bibliography, key)
        author = curated.get("observed_responsibility")
        title = curated.get("observed_page_title")
        if (not _field_line(entry, "title", title)
                or not _field_line(entry, "url", curated["original_url"])
                or not _field_line(entry, "urldate", curated["access_date"])
                or not _field_line(entry, "year", str(curated["author_date_label_year"]))
                or (author and not _field_line(entry, "author", author, nested=True))
                or (not author and re.search(r"(?m)^\s*author\s*=", entry))):
            raise ValueError(f"Bibliography metadata for {key} differs from verified source evidence/access date")
    scaffolds, citations, _ = _grammar(text, AIV_UNIT, {
        "required_citation_keys": required_keys,
        "citation_terms": citation_terms,
        "allow_narrative_documentation_mentions": True,
    })
    if [token.args[0] for token in citations] != required_keys:
        raise ValueError("AGES IV citations are detached, duplicated, missing, or reordered")

    significant = [rid for rid in unit["record_ids"] if records[rid].get("type") in {"text:p", "text:h", "text:a"}]
    mappings = unit_ledger["element_map"]
    if [item.get("source_id") for item in mappings] != significant:
        raise ValueError("AGES IV technology element mappings are missing, duplicated, extra, or reordered")
    link_ids = set(AIV_REFERENCE_KEYS)
    anchor_by_link = {rid: _source_text(records[rid]) for rid in expected_link_ids}
    label_ids = [rid for rid in significant if records[rid].get("type") == "text:p" and _source_text(records[rid]) in anchor_by_link.values()]
    expected_omissions = set(label_ids) | link_ids
    expected_mixed_fragments = []
    parent_to_link = {records[rid].get("parent_id"): rid for rid in expected_link_ids}
    for rid in significant:
        record = records[rid]
        if record.get("type") != "text:p":
            continue
        source_text = _source_text(record)
        link_id = parent_to_link.get(rid)
        if link_id and source_text != anchor_by_link[link_id] and anchor_by_link[link_id] in source_text:
            expected_mixed_fragments.append({
                "source_id": rid,
                "fragment": anchor_by_link[link_id],
                "disposition": "replaced_by_bibliography_citation",
                "citation_source_id": link_id,
            })
    if unit_ledger["omitted_documentation_fragments"] != expected_mixed_fragments:
        raise ValueError("Inline documentation-label removals are not exactly mapped to their bibliography citations")

    omissions_seen = set()
    covered = bytearray(len(data))
    last_position = 0
    for mapping in mappings:
        rid = mapping["source_id"]
        if mapping.get("source_text_sha256") != _sha(_source_text(records[rid]).encode("utf-8")):
            raise ValueError(f"Stale original text hash on {rid}")
        start, end, value = _interval(mapping, data, digest, AIV_TEX_PATH)
        if start < last_position:
            raise ValueError("AGES IV technology source mappings changed order")
        last_position = start
        disposition = mapping.get("disposition")
        if rid in expected_omissions:
            expected_disposition = "omitted_documentation_link" if rid in link_ids else "omitted_documentation_label"
            if disposition != expected_disposition or start != end:
                raise ValueError("Only authorized documentation links/standalone labels may use empty spans")
            omissions_seen.add(rid)
        elif rid == unit["heading_id"]:
            if disposition != "heading" or value != _source_text(records[rid]):
                raise ValueError("AGES IV original technology heading changed")
            covered[start:end] = b"\1" * (end - start)
        else:
            if disposition != "narrative" or not _visible(value):
                raise ValueError(f"AGES IV narrative record was omitted or disposed: {rid}")
            covered[start:end] = b"\1" * (end - start)
    if omissions_seen != expected_omissions:
        raise ValueError("Some authorized original documentation anchors/labels were not traced")
    expected_structural = [
        {"source_id": rid, "disposition": "odf-container-replaced-by-prose", "authorization_evidence": AIV_AUTHORIZATION}
        for rid in unit["record_ids"] if rid not in significant
    ]
    if unit_ledger["structural_dispositions"] != expected_structural:
        raise ValueError("AGES IV source list/container coverage differs from the extracted ODF")
    expected_links = [
        {"source_id": rid, "anchor": _source_text(records[rid]), "url": records[rid].get("href")}
        for rid in expected_link_ids
    ]
    if unit_ledger["documentation_links"] != expected_links:
        raise ValueError("AGES IV original documentation URLs/anchors changed or reordered")
    for mapping in mappings:
        if mapping["source_id"] in expected_omissions:
            index = mappings.index(mapping)
            prior_end = max((item["end_byte"] for item in mappings[:index] if item["source_id"] not in expected_omissions), default=0)
            if mapping["start_byte"] < prior_end:
                raise ValueError("Omitted documentation is not at its logical source position")
    residue = bytearray(data)
    for index, flag in enumerate(covered):
        if flag:
            residue[index] = 32
    for token in scaffolds:
        start = len(text[:token.start].encode("utf-8"))
        end = len(text[:token.end].encode("utf-8"))
        residue[start:end] = b" " * (end - start)
    # The four explicit paragraph breaks separate the source-derived groups;
    # their text remains covered by the adjacent narrative record intervals.
    residual_text = strip_comments(residue.decode("utf-8"))
    residual_commands = list(commands(residual_text))
    if len([token for token in residual_commands if token.name == "par"]) != 4:
        raise ValueError("AGES IV technology prose has unexpected paragraph-break scaffolding")
    for token in residual_commands:
        if token.name != "par" or token.args or token.optionals or token.starred:
            raise ValueError("Unexpected untraced command/content remains outside source spans")
        residual_text = residual_text[:token.start] + " " * (token.end - token.start) + residual_text[token.end:]
    if residual_text.strip():
        raise ValueError("Extra visible text/commands remain outside AGES IV technology source mappings")

    bookmarks = unit_ledger.get("bookmark_map")
    if not isinstance(bookmarks, list) or len(bookmarks) != 1:
        raise ValueError("AGES IV original technology heading bookmark missing")
    edition, heading_id, _, anchor, source_start, source_end = AGES_IV_HEADING
    bookmark = bookmarks[0]
    expected_bookmark = {"source_heading_id": heading_id, "source_name": anchor, "target_file": AIV_TEX_PATH, "target_anchor": anchor, "command": "hypertarget", "source_start_id": source_start, "source_end_id": source_end}
    if any(bookmark.get(key) != value for key, value in expected_bookmark.items()):
        raise ValueError("AGES IV bookmark identity differs from source heading")
    _, _, bookmark_text = _interval(bookmark, data, digest, AIV_TEX_PATH)
    if bookmark_text != rf"\hypertarget{{{anchor}}}{{}}":
        raise ValueError("AGES IV bookmark bytes differ from source")
    return {
        "unit_id": AIV_UNIT,
        "format": "ages-iv-mariah-prose-v1",
        "authorization_evidence": AIV_AUTHORIZATION,
        "target_sha256": digest,
        "source_text_records_checked": len([rid for rid in unit["record_ids"] if records[rid].get("type") in {"text:p", "text:h", "text:a"}]),
        "element_records_checked": len(significant),
        "structural_records_checked": len(expected_structural),
        "links_inventoried": len(expected_links),
        "citation_occurrences_checked": len(citations),
        "required_citation_keys": required_keys,
        "semantic_review": {"status": "PENDING", "reason": "Traceability and citations do not prove semantic preservation; independent ODT-to-result audit required"},
        "reference_availability": "VERIFIED_OFFICIAL_DESTINATIONS; Sonar product capabilities verified but Recorda configuration remains a source-fact audit item",
        "visual_review": "PENDING",
        "lexical_equality_claimed": False,
    }


def verify(manifest: dict, ledger: dict, repo: Path, uid: str) -> dict:
    if uid == AIV_UNIT:
        return _verify_ages_iv(manifest, ledger, repo)
    return _verify_legacy(manifest, ledger, repo, uid)
