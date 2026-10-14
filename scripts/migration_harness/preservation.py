"""Independent preservation audit, using source records and actual target bytes.

Ledger schema 1 maps each source record to a UTF-8 byte interval in a file:
{source_id, target_file, start_byte, end_byte, target_sha256,
 serializations?: ["tex_quotes", "tex_dashes", "canonical_unicode", "original_whitespace"]}.
original_whitespace requires macro_contract {path, sha256} in the unit ledger
(or top-level ledger) and the exact audited originaltab/originalspace definitions.
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


DIAGRAM_PLACEHOLDER_BODY = r"\par\noindent\fbox{\parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule\relax}{\textbf{Diagrama ausente — placeholder provisório}\par Identificador: #1\par Pendência: #2}}\par"


class UnsupportedSerialization(ValueError):
    pass


@dataclass(frozen=True)
class _ExplicitWhitespace:
    value: str


def displayed_text(source: str, serializations=(), *, macro_contract_verified=False) -> str:
    """Decode a conservative token projection; markers cannot be text-injected."""
    tokens = _display_tokens(source, serializations, macro_contract_verified)
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


def _display_tokens(source: str, serializations, macro_contract_verified) -> list:
    """Decode only syntax with a known, local displayed-text equivalent.

    Ordinary TeX code folding collapses to one visible space. Explicit source
    tabs, line breaks, repeated or edge spaces are rejected by the audit rather
    than normalized. Explicit target line breaks/tabs are also unsupported.
    Accents, punctuation, case, numbers and symbols compare exactly.
    No macro expansion, citation expansion or counter-generated text is guessed.
    """
    allowed = {"tex_quotes", "tex_dashes", "canonical_unicode", "original_whitespace"}
    if set(serializations) - allowed:
        raise UnsupportedSerialization("Unrecognized serialization policy")
    if "original_whitespace" in serializations and not macro_contract_verified:
        raise UnsupportedSerialization("original_whitespace requires a verified macro contract")
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
            if name in {"originaltab", "originalspace"}:
                if "original_whitespace" not in serializations or not macro_contract_verified:
                    raise UnsupportedSerialization("Explicit whitespace macro requires verified original_whitespace policy")
                if text[i:i + 2] != "{}":
                    raise UnsupportedSerialization("Whitespace macro must have an explicit empty group")
                i += 2
                output.append(_ExplicitWhitespace("\t" if name == "originaltab" else " "))
                continue
            if name in symbols:
                output.append(symbols[name])
                if text[i:i + 2] == "{}":
                    i += 2
                continue
            if name in {"newline", "linebreak", "\\"}:
                raise UnsupportedSerialization("Explicit target line break requires rendered/source whitespace review")
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
                output.extend(_display_tokens(first, serializations, macro_contract_verified))
                continue
            raise UnsupportedSerialization(f"Unsupported command \\{name}; rendered equivalence is unproven")
        if char == "{":
            group, i = _group(text, i, "{", "}")
            output.extend(_display_tokens(group, serializations, macro_contract_verified))
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


def _strict_source(text: str, original_whitespace=False) -> str:
    """No source whitespace is silently discarded or collapsed.

    XML extraction already distinguishes text:s, text:tab and text:line-break.
    Without a rendered layout proof, these cannot be declared equivalent to an
    ordinary TeX space, even if the converter copies the same raw characters.
    """
    if any(char in text for char in "\n\r\f\v") or "\t" in text and not original_whitespace:
        raise UnsupportedSerialization("Explicit source tab/line break requires rendered whitespace review")
    if original_whitespace and "\t" in text and (text.count("\t") != 1 or not text.startswith("\t")):
        raise UnsupportedSerialization("Audited originaltab contract supports one leading source tab only")
    if not original_whitespace and ("  " in text or text.startswith(" ") or text.endswith(" ")):
        raise UnsupportedSerialization("Repeated or edge source spaces require rendered whitespace review")
    return text


def _index(records):
    if isinstance(records, dict):
        return records
    return {record["id"]: record for record in records}


def _kind(record):
    return str(record.get("type", "")).split("}")[-1].split(":")[-1]


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
    findings, differences, facts = [], {}, {"scope": unit_id or "all", "proof": "actual UTF-8 bytes and conservative lexical projection; not TeX execution", "text_records_checked": 0, "text_records_matched": 0, "links_checked": 0, "images_checked": 0, "converted_units": 0, "source_text_records": 0, "coverage_percent": 0.0}

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
        unit = units[uid]
        state = ledger_units.get(uid, {}).get("state", "unconverted")
        unit_ledger = ledger_units.get(uid, {})
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
        mapping_ids = [item.get("source_id") for item in mappings]
        duplicate_ids = [rid for rid, count in Counter(mapping_ids).items() if count > 1]
        for rid in duplicate_ids:
            report("duplicate_mapping", uid, "Source element mapped more than once", rid)
        allowed_ids = set(unit.get("record_ids", [])) | set(source_ids)
        for rid in set(mapping_ids) - allowed_ids:
            report("unknown_or_wrong_unit_mapping", uid, "Mapping does not belong to this source unit", rid)
        by_id = {item.get("source_id"): item for item in mappings}
        uses_original_whitespace = any("original_whitespace" in item.get("serializations", []) for item in mappings)
        macro_verified = False
        if uses_original_whitespace:
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
                for name, body in bodies.items():
                    found = [item for item in definitions if item["name"] == name]
                    if len(found) != 1 or found[0]["declaration"] != "newcommand" or found[0]["arity"] != 0 or found[0]["optional_default"] or canonical_macro_body(found[0]["body"]) != canonical_macro_body(body):
                        raise ValueError(f"Actual {name} definition differs from audited contract")
                if re.search(r"\\(?:let|futurelet)\s*\\(?:originaltab|originalspace)\b", strip_comments(contract_text)):
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
                if any(item["name"] in {"originaltab", "originalspace"} for item in macro_definitions(actual_text)) or re.search(r"\\(?:let|futurelet)\s*\\(?:originaltab|originalspace)\b", strip_comments(actual_text)):
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
                expected = _strict_source(original, "original_whitespace" in serializations and macro_verified)
            except UnsupportedSerialization as exc:
                report("explicit_source_whitespace", uid, str(exc), rid, str(path.relative_to(repo)))
                differences[uid].append({"source_id": rid, "target_file": str(path.relative_to(repo)), "expected": original, "observed": None, "diff": "Whitespace equivalence is unproven; no automatic normalization accepted"})
                continue
            try:
                observed = displayed_text(value, serializations, macro_contract_verified=macro_verified)
            except (UnsupportedSerialization, ValueError) as exc:
                report("unsupported_serialization", uid, str(exc), rid)
                continue
            facts["text_records_checked"] += 1
            if expected != observed:
                difference = {"source_id": rid, "target_file": str(path.relative_to(repo)), "expected": expected, "observed": observed, "diff": "\n".join(difflib.unified_diff([expected], [observed], fromfile="ODT", tofile="LaTeX", lineterm=""))}
                differences[uid].append(difference)
                report("text_changed", uid, "Text differs in actual target bytes", rid, str(path.relative_to(repo)))
            else:
                facts["text_records_matched"] += 1
        if [pos for _, pos in positions] != sorted(pos for _, pos in positions):
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
            if strip_comments(value[:token.start] + value[token.end:]).strip():
                report("unmapped_link_span_content", uid, "Link interval contains additional unproved content", rid)
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
                if observed_anchor != _strict_source(record.get("source_text") or "", "original_whitespace" in policies and macro_verified):
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
                evidence = "migration/approvals/ages-i-authorization.json"
                auth = json.loads(safe_path(evidence).read_text())
                quote = "Vamos começar com AGES I. Lembre-se que os itens faltantes como arquitetura, banco de dados precisarão de placeholders que serão preenchidos posteriormente"
                if apparatus.get("authorization_evidence") != evidence or config.get("phase") != "edition" or config.get("authorization_evidence") != evidence or uid not in config.get("authorized_units", []) or uid not in auth.get("scope", []) or auth.get("kind") != "user_execution_authorization" or auth.get("quoted_instruction") != quote or spec[2].strip() not in auth.get("placeholders_explicitly_authorized", []):
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
                if _kind(records[rid]) != "h" or rid not in actual or actual[rid][0] != path:
                    continue
                _, start, end, _ = actual[rid]
                policies = by_id[rid].get("serializations", [])
                for token in target_tokens:
                    token_start = len(target_text[:token.start].encode("utf-8"))
                    token_end = len(target_text[:token.end].encode("utf-8"))
                    if token.name not in {"chapter", "section", "subsection", "subsubsection"} or len(token.args) != 1 or not token_start <= start <= end <= token_end:
                        continue
                    try:
                        title = displayed_text(token.args[0], policies, macro_contract_verified=macro_verified)
                        expected = _strict_source(records[rid]["text"], "original_whitespace" in policies and macro_verified)
                        if title == expected:
                            headings.append((rid, expected, policies, token))
                    except UnsupportedSerialization:
                        pass  # Existing source/target text findings remain authoritative.
            for rid in source_ids:
                if _kind(records[rid]) != "h" or rid not in actual or actual[rid][0] != path:
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
                            if heading.starred and token.args[1] == heading.name and displayed_text(token.args[2], policies, macro_contract_verified=macro_verified) == expected:
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
        declarations = {"centering", "raggedright", "raggedleft", "small", "footnotesize", "normalsize", "bfseries", "itshape", "normalfont", "noindent", "par", "newline", "item"}
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
                    if token.name in structural_commands:
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
