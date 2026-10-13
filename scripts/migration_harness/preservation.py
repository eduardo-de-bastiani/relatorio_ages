"""Independent preservation audit, using source records and actual target bytes.

Ledger schema 1 maps each source record to a UTF-8 byte interval in a file:
{source_id, target_file, start_byte, end_byte, target_sha256,
 serializations?: ["tex_quotes", "tex_dashes", "canonical_unicode"]}.
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
import hashlib
import re
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from .latex import _group, commands, strip_comments


class UnsupportedSerialization(ValueError):
    pass


def displayed_text(source: str, serializations=()) -> str:
    """Decode only syntax with a known, local displayed-text equivalent.

    Ordinary TeX code folding collapses to one visible space. Explicit source
    tabs, line breaks, repeated or edge spaces are rejected by the audit rather
    than normalized. Explicit target line breaks/tabs are also unsupported.
    Accents, punctuation, case, numbers and symbols compare exactly.
    No macro expansion, citation expansion or counter-generated text is guessed.
    """
    allowed = {"tex_quotes", "tex_dashes", "canonical_unicode"}
    if set(serializations) - allowed:
        raise UnsupportedSerialization("Unrecognized serialization policy")
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
                output.append(displayed_text(first, serializations))
                continue
            raise UnsupportedSerialization(f"Unsupported command \\{name}; rendered equivalence is unproven")
        if char == "{":
            group, i = _group(text, i, "{", "}")
            output.append(displayed_text(group, serializations))
            continue
        if char == "}" or char in "$&#_^":
            raise UnsupportedSerialization(f"Unescaped special character {char!r}")
        if char == "~":
            output.append(" ")
        else:
            output.append(char)
        i += 1
    result = "".join(output)
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
    return _space(result)


def _space(text: str) -> str:
    # Target code folding only. Never use this function on source text.
    return re.sub(r"[\t\n\r\f\v ]+", " ", text).strip(" ")


def _strict_source(text: str) -> str:
    """No source whitespace is silently discarded or collapsed.

    XML extraction already distinguishes text:s, text:tab and text:line-break.
    Without a rendered layout proof, these cannot be declared equivalent to an
    ordinary TeX space, even if the converter copies the same raw characters.
    """
    if any(char in text for char in "\t\n\r\f\v"):
        raise UnsupportedSerialization("Explicit source tab/line break requires rendered whitespace review")
    if "  " in text or text.startswith(" ") or text.endswith(" "):
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
            seen.add(path)
            file_order.append(path)
            text = path.read_text(encoding="utf-8")
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
            if "canonical_unicode" in serializations:
                original = unicodedata.normalize("NFC", original)
            try:
                expected = _strict_source(original)
            except UnsupportedSerialization as exc:
                report("explicit_source_whitespace", uid, str(exc), rid, str(path.relative_to(repo)))
                differences[uid].append({"source_id": rid, "target_file": str(path.relative_to(repo)), "expected": original, "observed": None, "diff": "Whitespace equivalence is unproven; no automatic normalization accepted"})
                continue
            try:
                observed = displayed_text(value, serializations)
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
                observed_anchor = displayed_text(anchor) if token.name == "href" else _url(anchor)
                if observed_anchor != _strict_source(record.get("source_text") or ""):
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
                tokens = [token for token in commands(actual[rid][3]) if token.name == "includegraphics" and token.args]
                if len(tokens) != 1:
                    raise ValueError("Image interval must contain exactly one includegraphics")
                if len(tokens[0].args) != 1:
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
