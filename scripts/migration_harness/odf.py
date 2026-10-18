"""Read-only ODF inventory. No renderer, converter or network access is used.

The package bytes and every parsed XML node are hashed. ``text`` belongs only
to p/h blocks: inline markup is expanded, nested frames are not. Hyperlink
anchors are ``source_text``, not another paragraph. This avoids counting a
reflection twice through the paragraph containing its frame.
"""
from __future__ import annotations

import copy
import hashlib
import io
import re
import struct
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

NS = {
    "xml": "http://www.w3.org/XML/1998/namespace",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "manifest": "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
    "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "math": "http://www.w3.org/1998/Math/MathML",
    "chart": "urn:oasis:names:tc:opendocument:xmlns:chart:1.0",
}
T = lambda local: f"{{{NS['text']}}}{local}"
D = lambda local: f"{{{NS['draw']}}}{local}"
BLOCKS = {T("p"), T("h")}
BLOCK_CONTAINERS = {D("frame"), D("text-box"), T("list"),
                    f"{{{NS['table']}}}table", T("note"), T("index-body")}
SEMANTIC = {"paragraph", "heading", "caption", "reference", "acronym",
            "subheading", "hyperlink", "list", "list-item", "list-header",
            "image", "reflection", "text-box", "table", "embedded-object",
            "formula", "chart", "note", "annotation", "citation", "cross-reference"}
AUDITED_SOURCE = "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"


def sha256(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _display_text(element: ET.Element) -> str:
    """Displayed inline characters, without nested block content or caches.

    Whitespace is never collapsed. text:s, tab and line-break have explicit
    semantics. Ordinary span/link/sequence text and tails preserve order.
    """
    out = [element.text or ""]
    for child in element:
        if child.tag == T("s"):
            out.append(" " * int(child.get(T("c"), "1")))
        elif child.tag == T("tab"):
            out.append("\t")
        elif child.tag == T("line-break"):
            out.append("\n")
        elif child.tag == T("soft-page-break"):
            pass
        elif child.tag not in BLOCK_CONTAINERS and child.tag not in BLOCKS:
            out.append(_display_text(child))
        out.append(child.tail or "")
    return "".join(out)


def _canonical_hash(element: ET.Element) -> str:
    node = copy.copy(element)
    node.tail = None  # tail belongs to the parent, recorded separately
    return sha256(ET.canonicalize(ET.tostring(node, encoding="unicode")))


def _image_size(data: bytes) -> tuple[int | None, int | None]:
    """Dimensions from PNG/JPEG headers, not image decoding."""
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"\xff\xd8"):
        i = 2
        while i < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            while i < len(data) and data[i] == 0xFF:
                i += 1
            if i >= len(data):
                break
            marker = data[i]
            i += 1
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                continue
            if i + 2 > len(data):
                break
            length = int.from_bytes(data[i:i+2], "big")
            if length < 2 or i + length > len(data):
                break
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                          0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF} and length >= 7:
                height, width = struct.unpack(">HH", data[i+3:i+7])
                return width, height
            if marker == 0xDA:
                break
            i += length
    return None, None


def _safe_package_path(href: str) -> str | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or parsed.fragment or parsed.query:
        return None
    name = unquote(parsed.path).removeprefix("./")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        return None
    return path.as_posix()


def extract_manifest(source: Path, destination_root: str = "relatorio_AGES_eduardo") -> dict:
    """Return a deterministic inventory; neither source nor destination is written.

    Classification is conservative. Heading exceptions specific to the audited
    ODT are activated only for its SHA-256. A different ODT needs renewed review.
    """
    source = Path(source)
    original = source.read_bytes()
    source_hash = sha256(original)
    audited = source_hash == AUDITED_SOURCE
    trees, blobs, entries, namespaces = {}, {}, [], dict(NS)
    with zipfile.ZipFile(io.BytesIO(original)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Ambiguous ODF package: duplicate entry names")
        for entry in archive.infolist():
            data = archive.read(entry)  # checks CRC, including unused resources
            blobs[entry.filename] = data
            entries.append({"path": entry.filename, "sha256": sha256(data),
                            "size_bytes": len(data), "directory": entry.is_dir()})
            if entry.filename.endswith((".xml", ".rdf")):
                if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
                    raise ValueError(f"Unsupported DTD/entity declaration: {entry.filename}")
                for _, (prefix, uri) in ET.iterparse(io.BytesIO(data), events=("start-ns",)):
                    if uri not in namespaces.values():
                        candidate = prefix or "default"
                        if candidate in namespaces and namespaces[candidate] != uri:
                            candidate = f"ns{len(namespaces)}"
                        namespaces[candidate] = uri
                trees[entry.filename] = ET.fromstring(data)
    if "content.xml" not in trees:
        raise ValueError("ODF package has no content.xml")
    prefixes = {uri: prefix for prefix, uri in namespaces.items()}

    def qname(tag):
        if tag.startswith("{"):
            uri, local = tag[1:].split("}", 1)
            return f"{prefixes[uri]}:{local}"
        return tag

    media_types = {}
    if "META-INF/manifest.xml" in trees:
        for element in trees["META-INF/manifest.xml"].iter():
            name = element.get(f"{{{NS['manifest']}}}full-path")
            if name:
                media_types[name] = element.get(f"{{{NS['manifest']}}}media-type", "")

    # Global style catalog: keep inherited properties available without assuming
    # that a style name corresponds to its semantic meaning.
    style_catalog = {}
    list_styles = {}
    for part, tree in trees.items():
        for element in tree.iter():
            if element.tag == f"{{{NS['style']}}}style":
                name = element.get(f"{{{NS['style']}}}name")
                family = element.get(f"{{{NS['style']}}}family")
                style_catalog[f"{family}:{name}"] = {
                    "part": part, "name": name, "family": family,
                    "parent": element.get(f"{{{NS['style']}}}parent-style-name"),
                    "attributes": {qname(k): v for k, v in sorted(element.attrib.items())},
                    "properties": [{"type": qname(child.tag),
                                    "attributes": {qname(k): v for k, v in sorted(child.attrib.items())}}
                                   for child in element],
                }
            elif element.tag == T("list-style"):
                name = element.get(f"{{{NS['style']}}}name")
                list_styles[name] = [{"type": qname(child.tag),
                                     "attributes": {qname(k): v for k, v in sorted(child.attrib.items())}}
                                    for child in element]

    records = []
    nodes = {}
    by_id = {}
    parents = {}
    per_part_counts = {}
    # content first ensures stable familiar IDs; remaining parts have disjoint IDs.
    part_order = ["content.xml"] + sorted(p for p in trees if p != "content.xml")
    for part in part_order:
        counters = Counter()
        part_prefix = "" if part == "content.xml" else part.replace("/", "-").replace(".", "-") + "-"

        def walk(element, parent_id=None, xpath="", sibling_index=1, ancestor_ids=()):
            name = qname(element.tag)
            counters[name] += 1
            identifier = f"{part_prefix}{name.replace(':', '-')}-{counters[name]:04d}"
            path = f"{xpath}/{name}[{sibling_index}]"
            ancestors = [by_id[x] for x in ancestor_ids]
            types = {r["type"] for r in ancestors}
            in_body = "office:text" in types
            derived = "text:index-body" in types
            is_text = element.tag in BLOCKS
            displayed = _display_text(element) if is_text or element.tag == T("a") else None
            semantic = "layout"
            if part != "content.xml":
                semantic = ("metadata" if part in {"meta.xml", "manifest.rdf", "settings.xml", "META-INF/manifest.xml"}
                            else "style" if part == "styles.xml" else "embedded-data")
            elif not in_body:
                semantic = "style"
            elif derived:
                semantic = "derived-index"
            elif is_text:
                if displayed.strip():
                    semantic = "heading" if element.tag == T("h") else "paragraph"
                    if re.match(r"^(?:Figure|Figura|Quadro|Tabela)\s+\d+\s*[:–—-]", displayed.strip(), re.I):
                        semantic = "caption"
                elif any(x.tag == D("frame") for x in element.iter()):
                    semantic = "anchor-container"
            elif element.tag == D("text-box"):
                semantic = "text-box" if any(x.tag == D("image") for x in element.iter()) else "reflection"
            else:
                semantic = {T("a"): "hyperlink", T("list"): "list", T("list-item"): "list-item",
                            T("list-header"): "list-header", D("image"): "image",
                            D("object"): "embedded-object", D("object-ole"): "embedded-object",
                            T("note"): "note", f"{{{NS['table']}}}table": "table",
                            T("bibliography-mark"): "citation", T("sequence-ref"): "cross-reference",
                            T("reference-ref"): "cross-reference", T("bookmark-ref"): "cross-reference",
                            f"{{{NS['office']}}}annotation": "annotation",
                            f"{{{NS['math']}}}math": "formula",
                            f"{{{NS['chart']}}}chart": "chart"}.get(element.tag, "layout")
            record = {
                "id": identifier, "part": part, "xpath": path, "order": len(records) + 1,
                "parent_id": parent_id, "type": name,
                "attributes": {qname(k): v for k, v in sorted(element.attrib.items())},
                "xml_sha256": _canonical_hash(element),
                "text": displayed if is_text else None,
                "text_sha256": sha256(displayed) if is_text else None,
                "source_text": displayed, "direct_text": element.text, "tail": element.tail,
                "unit_id": None, "semantic_type": semantic, "context_ids": [],
                "planned_destination": None, "ancestor_ids": list(ancestor_ids),
            }
            if element.tag == T("a"):
                record["href"] = element.get(f"{{{NS['xlink']}}}href", "")
            if name in {"text:list", "text:list-item", "text:list-header"}:
                list_ancestors = [r for r in ancestors if r["type"] == "text:list"]
                list_style = element.get(T("style-name"))
                if not list_style:
                    list_style = next((r["attributes"].get("text:style-name") for r in reversed(list_ancestors)
                                       if r["attributes"].get("text:style-name")), None)
                record["list_context"] = {
                    "xml_depth": len(list_ancestors) + (name == "text:list"),
                    "style_name": list_style, "style_levels": list_styles.get(list_style, []),
                    "start_value": element.get(T("start-value")),
                    "continue_numbering": element.get(T("continue-numbering")),
                    "continue_list": element.get(T("continue-list")),
                }
            records.append(record)
            by_id[identifier] = record
            nodes[identifier] = element
            parents[identifier] = parent_id
            siblings = Counter()
            for child in element:
                siblings[child.tag] += 1
                walk(child, identifier, path, siblings[child.tag], ancestor_ids + (identifier,))
        walk(trees[part])
        per_part_counts[part] = {"nodes": sum(counters.values()), "types": dict(sorted(counters.items()))}

    # A paragraph can contain "before [frame] after". Its own text is still
    # one block, but the anchor offset and segments retain the original logical
    # insertion point. Never derive media order from a flattened text dump.
    node_ids = {id(element): identifier for identifier, element in nodes.items()}

    def segments(element):
        result = []
        if element.text:
            result.append({"kind": "text", "text": element.text})
        for child in element:
            if child.tag in BLOCK_CONTAINERS or child.tag in BLOCKS:
                result.append({"kind": "embedded-block", "record_id": node_ids[id(child)]})
            elif child.tag == T("s"):
                result.append({"kind": "text", "text": " " * int(child.get(T("c"), "1"))})
            elif child.tag == T("tab"):
                result.append({"kind": "text", "text": "\t"})
            elif child.tag == T("line-break"):
                result.append({"kind": "text", "text": "\n"})
            elif child.tag != T("soft-page-break"):
                result.extend(segments(child))
            if child.tail:
                result.append({"kind": "text", "text": child.tail})
        return result

    for record in records:
        if record["type"] in {"text:p", "text:h"}:
            record["inline_segments"] = segments(nodes[record["id"]])

    # Heading reliability review is explicit and source-bound. No XML content is
    # discarded: a bogus heading becomes a paragraph; frame-only h keeps children.
    if audited:
        by_id["text-h-0068"]["semantic_type"] = "paragraph"
        by_id["text-h-0068"]["classification_reason"] = "Audited paragraph incorrectly styled as level-2 heading"
        for identifier in ("text-h-0084", "text-h-0118"):
            by_id[identifier]["semantic_type"] = "subheading"
            by_id[identifier]["classification_reason"] = "Audited local label; does not begin a migration unit"

    units = []
    current = None
    chapter = None
    headings = []
    phase = "pretext"
    reference_mode = False
    acronym_mode = False

    def new_unit(identifier, title, kind, heading_id=None, level=0):
        nonlocal current
        destination = f"{destination_root}/conteudo/migracao/{identifier}.tex"
        current = {"id": identifier, "title": title, "chapter": chapter,
                   "kind": kind, "heading_id": heading_id, "heading_level": level,
                   "record_ids": [], "source_record_ids": [], "source_text": [],
                   "destination": destination, "state": "unconverted", "empty": True}
        units.append(current)

    new_unit("pretext", "Elementos pré-textuais", "pretext")
    for record in records:
        if record["part"] != "content.xml" or record["semantic_type"] in {"style", "derived-index"}:
            record["destination_reason"] = "Configuration/metadata or derived index, not authored body content"
            continue
        if "office:text" not in {by_id[x]["type"] for x in record["ancestor_ids"]}:
            continue
        semantic = record["semantic_type"]
        text = record["source_text"] or ""
        in_box = any(by_id[x]["type"] == "draw:text-box" for x in record["ancestor_ids"])
        title = text.strip()
        if semantic == "heading" and not in_box:
            level = int(record["attributes"].get("text:outline-level", "1"))
            if level == 1:
                chapter_match = re.match(r"^(\d+)\s*[-–—]", title)
                chapter = int(chapter_match[1]) if chapter_match else chapter
                phase = "body"
                reference_mode = False
            headings = [(lev, rid) for lev, rid in headings if lev < level]
            headings.append((level, record["id"]))
            sprint = re.search(r"\bSprint\s+(\d+)\s*$", title, re.I)
            if sprint:
                prefix = {2: "ages-i", 3: "cliente-hoortech", 4: "ages-ii", 5: "ages-iii", 6: "ages-iv"}.get(chapter, f"chapter-{chapter}")
                identifier = f"{prefix}-sprint-{int(sprint[1])}"
                kind = "sprint"
            else:
                identifier = f"chapter-{chapter:02d}-{record['id']}" if chapter is not None else f"heading-{record['id']}"
                kind = "chapter" if level == 1 else "section"
            new_unit(identifier, text, kind, record["id"], level)
        elif not in_box and record["type"] == "text:p" and title.upper() in {"REFERÊNCIAS", "APÊNDICES", "RESUMO"}:
            reference_mode = title.upper() == "REFERÊNCIAS"
            phase = "references" if reference_mode else "appendices" if title.upper() == "APÊNDICES" else "pretext"
            headings = []
            new_unit(phase if phase != "pretext" else "resumo", text, phase, record["id"])
        if not in_box and record["type"] == "text:p" and title.casefold() == "lista de siglas":
            acronym_mode = True
        elif acronym_mode and (semantic == "heading" or title.casefold() == "sumário"):
            acronym_mode = False
        if acronym_mode and semantic == "paragraph" and re.match(r"^[A-Z0-9/]+\s*[-–—]\s+", title):
            record["semantic_type"] = semantic = "acronym"
            abbreviation, expansion = re.split(r"\s*[-–—]\s+", title, maxsplit=1)
            record["abbreviation"] = abbreviation
            record["expansion"] = expansion
        if reference_mode and semantic == "paragraph" and record["id"] != current["heading_id"]:
            if re.search(r"Disponível em\s*:", title, re.I):
                record["semantic_type"] = "reference"
                semantic = "reference"
        record["unit_id"] = current["id"]
        record["context_ids"] = [rid for _, rid in headings] + [rid for rid in record["ancestor_ids"]
                                    if by_id[rid]["type"] in {"draw:frame", "draw:text-box", "text:list", "text:list-item", "table:table"}]
        if semantic in SEMANTIC:
            record["planned_destination"] = current["destination"]
            current["record_ids"].append(record["id"])
        else:
            record["destination_reason"] = "Layout/anchor/inline node retained for forensic tracing; parent supplies destination"
        if record["type"] in {"text:p", "text:h"} and text.strip():
            current["source_record_ids"].append(record["id"])
            current["source_text"].append(text)
            if record["id"] != current["heading_id"]:
                current["empty"] = False
        if semantic in {"image", "embedded-object", "formula", "chart", "table"}:
            current["empty"] = False

    assets = []
    issues = [{"code": "embedded-xml-review-required", "part": part,
               "message": "XML outside the standard document parts must be reviewed as embedded content"}
              for part in trees if part not in {"content.xml", "styles.xml", "meta.xml", "settings.xml", "manifest.rdf", "META-INF/manifest.xml"}]
    asset_occurrences = defaultdict(list)
    captions = [r for r in records if r["semantic_type"] == "caption"]
    for image in (r for r in records if r["semantic_type"] == "image"):
        boxes = [rid for rid in reversed(image["ancestor_ids"]) if by_id[rid]["type"] == "draw:text-box"]
        matching = []
        for box_id in boxes:
            matching = [r for r in captions if box_id in r["ancestor_ids"]]
            if matching:
                break
        image["caption_ids"] = [r["id"] for r in matching]
        for caption in matching:
            caption.setdefault("image_ids", []).append(image["id"])
    for record in records:
        if record["semantic_type"] in {"image", "embedded-object"}:
            href = record["attributes"].get("xlink:href", "")
            package_path = _safe_package_path(href)
            record["resource_path"] = package_path
            record["anchor_context"] = {"unit_id": record["unit_id"], "ordered_context_ids": record["context_ids"],
                                        "frame_ids": [rid for rid in record["ancestor_ids"] if by_id[rid]["type"] == "draw:frame"]}
            object_parts = [name for name in blobs if package_path and
                            name.startswith(package_path.rstrip("/") + "/") and blobs[name]]
            if record["semantic_type"] == "embedded-object" and object_parts:
                record["embedded_parts"] = [{"path": name, "sha256": sha256(blobs[name]),
                                              "size_bytes": len(blobs[name])} for name in sorted(object_parts)]
                issues.append({"code": "embedded-object-review-required", "record_id": record["id"],
                               "message": "Embedded object bytes inventoried; automatic text rendering not claimed"})
            elif package_path is not None and package_path in blobs:
                asset_occurrences[package_path].append(record["id"])
            else:
                issues.append({"code": "unresolved-resource", "record_id": record["id"], "href": href,
                               "message": "Resource is absent, external or not a safe package path"})
    for name in sorted(blobs):
        mime = media_types.get(name, "")
        if (name.startswith("Pictures/") and blobs[name]) or name in asset_occurrences or mime.startswith("image/"):
            data = blobs[name]
            width, height = _image_size(data)
            if not mime:
                mime = "image/png" if data.startswith(b"\x89PNG") else "image/jpeg" if data.startswith(b"\xff\xd8") else "application/octet-stream"
            assets.append({"id": f"asset-{len(assets)+1:04d}", "path": name, "sha256": sha256(data),
                           "size_bytes": len(data), "mime_type": mime, "width_px": width, "height_px": height,
                           "occurrence_ids": asset_occurrences[name],
                           "role": "document-media" if asset_occurrences[name] else "package-resource"})

    content = [r for r in records if r["part"] == "content.xml"]
    c = Counter(r["type"] for r in content)
    semantic_counts = Counter(r["semantic_type"] for r in content)
    counts = {
        "package_entries": len(entries), "xml_parts": len(trees), "xml_nodes": len(records),
        "content_xml_nodes": len(content), "paragraphs": c["text:p"], "headings": c["text:h"],
        "lists": c["text:list"], "list_items": c["text:list-item"], "list_headers": c["text:list-header"],
        "frames": c["draw:frame"], "text_boxes": c["draw:text-box"], "images": c["draw:image"],
        "hyperlinks": c["text:a"], "tables": c["table:table"], "notes": c["text:note"],
        "bibliography_marks": c["text:bibliography-mark"], "embedded_objects": c["draw:object"] + c["draw:object-ole"],
        "formulas": c["math:math"], "charts": c["chart:chart"], "annotations": c["office:annotation"],
        "reflections": semantic_counts["reflection"], "captions": semantic_counts["caption"],
        "references": semantic_counts["reference"], "acronyms": semantic_counts["acronym"],
        "soft_page_breaks": c["text:soft-page-break"],
        "sprint_units": sum(u["kind"] == "sprint" for u in units), "units": len(units),
        "document_media": sum(a["role"] == "document-media" for a in assets),
        "hyperlinks_authored": sum(r["semantic_type"] == "hyperlink" for r in content),
        "semantic_types": dict(sorted(semantic_counts.items())), "parts": per_part_counts,
    }
    # Filename is sufficient to locate the immutable source relative to repo root;
    # absolute machine-specific paths and wall-clock timestamps are excluded.
    return {"schema_version": 1,
            "source": {"path": source.name, "sha256": source_hash, "size_bytes": len(original),
                       "odf_version": trees["content.xml"].get(f"{{{NS['office']}}}version")},
            "destination_root": destination_root, "namespaces": dict(sorted(namespaces.items())),
            "package_entries": entries, "counts": counts, "records": records, "assets": assets,
            "units": units, "styles": style_catalog, "list_styles": list_styles,
            "extraction": {"engine": "python-stdlib-zipfile-elementtree", "hash": "sha256",
                           "xml_hash": "C14N2 of each subtree, without the root tail",
                           "text_policy": "p/h displayed inline text; explicit spaces, tabs and breaks; exclude nested blocks",
                           "classification": "audited-source-bound" if audited else "generic-needs-review",
                           "issues": issues,
                           "limitations": ["No page positions are inferred from XML; use rendered PDF for pagination.",
                                           "Reflection means a non-media text-box; generic sources need semantic review.",
                                           "XML-depth list metadata is not a claim about displayed list depth.",
                                           "Figure provenance, missing diagrams and absent bibliography metadata are not invented."]}}


def verify_manifest(manifest: dict, source: Path) -> list[dict]:
    """Re-extract from source and report structural/content mutations in manifest.

    Every field is compared, including record order, units, destinations and
    assets. This verifies inventory consistency, not migrated LaTeX fidelity.
    """
    expected = extract_manifest(source, manifest.get("destination_root", "relatorio_AGES_eduardo"))
    differences = []

    def compare(actual, wanted, path):
        if type(actual) is not type(wanted):
            differences.append({"code": "manifest-type-mismatch", "path": path,
                                "expected": type(wanted).__name__, "actual": type(actual).__name__})
        elif isinstance(wanted, dict):
            for key in sorted(actual.keys() | wanted.keys()):
                p = f"{path}.{key}"
                if key not in actual:
                    differences.append({"code": "manifest-field-missing", "path": p})
                elif key not in wanted:
                    differences.append({"code": "manifest-unexpected-field", "path": p})
                else:
                    compare(actual[key], wanted[key], p)
        elif isinstance(wanted, list):
            if len(actual) != len(wanted):
                differences.append({"code": "manifest-length-mismatch", "path": path,
                                    "expected": len(wanted), "actual": len(actual)})
            for index, (a, w) in enumerate(zip(actual, wanted)):
                compare(a, w, f"{path}[{index}]")
        elif actual != wanted:
            differences.append({"code": "manifest-value-mismatch", "path": path,
                                "expected": wanted, "actual": actual})
    inventory = dict(manifest)
    overlay = inventory.pop("migration_overlay", None)
    compare(inventory, expected, "$")
    if overlay is not None:
        if not isinstance(overlay, dict) or overlay.get("schema_version") != 1 or not isinstance(overlay.get("tasks"), dict):
            differences.append({"code": "manifest-invalid-overlay", "path": "$.migration_overlay"})
            return differences
        allowed_fields = {"schema_version", "tasks", "document_order"}
        if set(overlay) - allowed_fields:
            differences.append({"code": "manifest-invalid-overlay-field", "path": "$.migration_overlay"})
        units = {u["id"]: u for u in expected["units"]}
        records = {record["id"]: record for record in expected["records"]}
        for uid, task in overlay["tasks"].items():
            location = "$.migration_overlay.tasks." + uid
            if uid not in units or not isinstance(task, dict):
                differences.append({"code": "manifest-unknown-task-unit", "path": location})
                continue
            allowed_task_fields = {"task_id", "stage", "scope", "baseline_commit", "source_sha256",
                                   "destination", "heading_id", "source_record_ids", "evidence", "evidence_sha256",
                                   "authorization_evidence", "ledger", "ledger_sha256", "target_sha256", "pdf",
                                   "pdf_sha256", "content_audit", "content_audit_sha256", "visual_audit", "visual_audit_sha256"}
            if set(task) - allowed_task_fields:
                differences.append({"code": "manifest-invalid-task-field", "path": location})
            unit = units[uid]
            for key, value in {"source_sha256": expected["source"]["sha256"], "scope": [uid],
                               "destination": unit["destination"], "heading_id": unit["heading_id"],
                               "source_record_ids": unit["source_record_ids"]}.items():
                if task.get(key) != value:
                    differences.append({"code": "manifest-overlay-source-mismatch", "path": location + "." + key})
            if task.get("stage") not in {"extracted", "converted", "audited", "review-ready"}:
                differences.append({"code": "manifest-invalid-task-stage", "path": location + ".stage"})
            for key in {"evidence", "authorization_evidence", "ledger", "pdf", "content_audit", "visual_audit"}:
                if key not in {"evidence", "authorization_evidence"} and key not in task:
                    continue
                value = task.get(key)
                if not isinstance(value, str) or PurePosixPath(value).is_absolute() or ".." in PurePosixPath(value).parts:
                    differences.append({"code": "manifest-unsafe-task-path", "path": location + "." + key})
            for key, length in {"evidence_sha256": 64, "baseline_commit": 40, "ledger_sha256": 64,
                                "target_sha256": 64, "pdf_sha256": 64, "content_audit_sha256": 64,
                                "visual_audit_sha256": 64}.items():
                if key not in {"evidence_sha256", "baseline_commit"} and key not in task:
                    continue
                if not isinstance(task.get(key), str) or not re.fullmatch("[0-9a-f]{" + str(length) + "}", task[key]):
                    differences.append({"code": "manifest-invalid-task-hash", "path": location + "." + key})
        document_order = overlay.get("document_order")
        if document_order is not None:
            location = "$.migration_overlay.document_order"
            required = {
                "schema_version", "status", "authorization_evidence", "authorization_evidence_sha256",
                "baseline_commit", "source_sha256", "moved_units", "affected_units", "affected_source_ids",
                "final_chapter_sequence", "planned_unit_sequence_under_chapters", "heading_numbering",
                "figure_caption_numbering", "unchanged_figure_range", "inline_reference_adjustments",
                "validation_status", "constraints", "scope_note",
            }
            if not isinstance(document_order, dict) or set(document_order) != required:
                differences.append({"code": "manifest-invalid-document-order-overlay", "path": location})
                return differences
            if (document_order.get("schema_version") != 1
                    or document_order.get("status") not in {"authorized-pending-integration-and-audit", "integrated-pending-audit", "audited-pending-human-review"}
                    or document_order.get("authorization_evidence") != "migration/approvals/cliente-hoortech-and-document-order-authorization.json"
                    or document_order.get("source_sha256") != expected["source"]["sha256"]):
                differences.append({"code": "manifest-invalid-document-order-metadata", "path": location})
            for key, length in {"authorization_evidence_sha256": 64, "baseline_commit": 40, "source_sha256": 64}.items():
                if not isinstance(document_order.get(key), str) or not re.fullmatch("[0-9a-f]{" + str(length) + "}", document_order[key]):
                    differences.append({"code": "manifest-invalid-document-order-hash", "path": location + "." + key})
            for key in ("moved_units", "affected_units", "affected_source_ids", "planned_unit_sequence_under_chapters"):
                value = document_order.get(key)
                if not isinstance(value, list) or any(not isinstance(item, str) for item in value) or len(value) != len(set(value)):
                    differences.append({"code": "manifest-invalid-document-order-list", "path": location + "." + key})
            sequence = document_order.get("final_chapter_sequence")
            if (not isinstance(sequence, list)
                    or [item.get("chapter") for item in sequence if isinstance(item, dict)] != list(range(1, 8))
                    or any(not isinstance(item, dict) or set(item) != {"chapter", "unit", "title"}
                           or item.get("unit") not in units or not isinstance(item.get("title"), str)
                           for item in sequence)):
                differences.append({"code": "manifest-invalid-final-chapter-sequence", "path": location + ".final_chapter_sequence"})
            all_mappings = {}
            for key in ("heading_numbering", "figure_caption_numbering"):
                mappings = document_order.get(key)
                if not isinstance(mappings, list):
                    differences.append({"code": "manifest-invalid-document-order-map", "path": location + "." + key})
                    continue
                seen = set()
                for item in mappings:
                    if not isinstance(item, dict) or "source_id" not in item:
                        differences.append({"code": "manifest-invalid-document-order-entry", "path": location + "." + key})
                        continue
                    source_id = item["source_id"]
                    if source_id in seen:
                        differences.append({"code": "manifest-duplicate-document-order-id", "path": location + "." + key})
                    seen.add(source_id)
                    record = records.get(source_id)
                    if (record is None or item.get("unit_id") != record.get("unit_id")
                            or item.get("source_text") != record.get("text")):
                        differences.append({"code": "manifest-document-order-source-mismatch",
                                            "path": location + "." + key + "." + str(source_id)})
                    all_mappings[source_id] = item
            inline = document_order.get("inline_reference_adjustments")
            if not isinstance(inline, list):
                differences.append({"code": "manifest-invalid-document-order-map", "path": location + ".inline_reference_adjustments"})
                inline = []
            for item in inline:
                if not isinstance(item, dict) or item.get("source_id") not in records:
                    differences.append({"code": "manifest-invalid-document-order-entry", "path": location + ".inline_reference_adjustments"})
                    continue
                rid = item["source_id"]
                if item.get("unit_id") != records[rid].get("unit_id") or item.get("source_text") != records[rid].get("text"):
                    differences.append({"code": "manifest-document-order-source-mismatch",
                                        "path": location + ".inline_reference_adjustments." + str(rid)})
                all_mappings[rid] = item
            ids = document_order.get("affected_source_ids", [])
            if set(ids) != set(all_mappings) or len(ids) != len(all_mappings):
                differences.append({"code": "manifest-document-order-id-set-mismatch", "path": location + ".affected_source_ids"})
    return differences
