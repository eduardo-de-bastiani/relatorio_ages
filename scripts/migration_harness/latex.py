"""Read-only, conservative LaTeX dependency and reference audit (no TeX execution)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Command:
    name: str
    args: tuple[str, ...]
    start: int
    end: int
    starred: bool = False
    optionals: tuple[str, ...] = ()


def strip_comments(text: str) -> str:
    """Keep offsets and URL percent escapes; remove actual TeX comments.

    Literal percent in href/url is preserved for link auditing, but a warning
    below still flags unescaped percent as unsafe for TeX compilation.
    """
    chars = list(text)
    url_depth = None
    depth = 0
    i = 0
    while i < len(text):
        if text[i] == "\\":
            match = re.match(r"\\(href|url)\s*\{", text[i:])
            if match:
                # The first argument is verbatim-ish for forensic URL inspection.
                opening = i + match.end() - 1
                depth += 1
                url_depth = depth
                i = opening + 1
                continue
            if i + 1 < len(text) and not text[i + 1].isalpha():
                i += 2
                continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            if url_depth == depth:
                url_depth = None
            depth -= 1
        elif text[i] == "%" and url_depth is None:
            j = text.find("\n", i)
            j = len(text) if j < 0 else j
            chars[i:j] = " " * (j - i)
            i = j
            continue
        i += 1
    return "".join(chars)


def _group(text: str, offset: int, opening: str, closing: str) -> tuple[str, int]:
    depth, start, i = 1, offset + 1, offset + 1
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text) and not text[i + 1].isalpha():
            i += 2
            continue
        if text[i] == opening:
            depth += 1
        elif text[i] == closing:
            depth -= 1
            if depth == 0:
                return text[start:i], i + 1
        i += 1
    raise ValueError(f"Unclosed {opening} at offset {offset}")


def commands(text: str):
    """Yield commands including commands nested in arguments, preserving offsets."""
    clean = strip_comments(text)
    for match in re.finditer(r"\\([A-Za-z@]+|.)", clean):
        i = match.end()
        starred = i < len(clean) and clean[i] == "*"
        if starred:
            i += 1
        args, optionals = [], []
        while True:
            while i < len(clean) and clean[i].isspace():
                i += 1
            if i < len(clean) and clean[i] == "[":
                optional, i = _group(clean, i, "[", "]")
                optionals.append(optional)
            elif i < len(clean) and clean[i] == "{":
                arg, i = _group(clean, i, "{", "}")
                args.append(arg)
            else:
                break
        yield Command(match[1], tuple(args), match.start(), i, starred, tuple(optionals))


def macro_definitions(text: str) -> list[dict]:
    """Find explicit command/environment definitions; never execute their bodies.

    Primitive definitions are recognized sufficiently to keep their bodies out
    of the operational dependency graph. Argument expansion remains unsupported.
    """
    definitions, occupied = [], []
    clean = strip_comments(text)
    names = {"newcommand", "renewcommand", "providecommand", "DeclareRobustCommand", "newenvironment", "renewenvironment"}
    for token in commands(text):
        if any(start <= token.start < end for start, end in occupied):
            continue
        if token.name in names and len(token.args) >= 2:
            environment = token.name.endswith("environment")
            name = token.args[0] if environment else token.args[0].removeprefix("\\")
            arity = int(token.optionals[0]) if token.optionals and token.optionals[0].isdigit() else 0
            item = dict(name=name, body=token.args[1], arity=arity, start=token.start, end=token.end, environment=environment, primitive=False, optional_default=len(token.optionals) > 1, declaration=token.name)
            if environment and len(token.args) >= 3:
                item["end_body"] = token.args[2]
            definitions.append(item)
            occupied.append((token.start, token.end))
        elif token.name in {"def", "edef", "gdef", "xdef"}:
            match = re.match(r"\s*\\([A-Za-z@]+)([^{}]*)\{", clean[token.start + len(token.name) + 1:])
            if match:
                start = token.start + len(token.name) + 1 + match.end() - 1
                body, end = _group(clean, start, "{", "}")
                parameters = re.findall(r"#([1-9])", match[2])
                definitions.append(dict(name=match[1], body=body, arity=max(map(int, parameters), default=0), start=token.start, end=end, environment=False, primitive=True, optional_default=False, declaration=token.name))
                occupied.append((token.start, end))
    return definitions


MEMORIAL_FIGURE_BODY = r'\begin{figure}[htbp]\refstepcounter{figure}\caption*{{\normalfont\upshape #2}}\label{#3}\addcontentsline{lof}{figure}{{\normalfont\upshape #2}}\noindent\makebox[\linewidth][c]{\XeTeXpicfile "#1" width #5\linewidth\relax}\par\small\SingleSpacing #4\par\end{figure}'


def canonical_macro_body(body: str) -> str:
    return re.sub(r"\s+", "", strip_comments(body))


def bib_keys(text: str) -> tuple[set[str], list[str]]:
    """Read BibTeX entry keys, ignoring nested braces and quoted fields."""
    keys, duplicates = set(), []
    i = 0
    while i < len(text):
        if text[i] == "%":
            end = text.find("\n", i)
            i = len(text) if end < 0 else end + 1
            continue
        match = re.match(r"@([A-Za-z]+)\s*([({])", text[i:])
        if not match:
            i += 1
            continue
        kind, opening = match.groups()
        start = i + match.end()
        stack, quote, escaped, j = ["}" if opening == "{" else ")"], False, False, start
        closing = "}" if opening == "{" else ")"
        while j < len(text) and stack:
            char = text[j]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"' and len(stack) == 1:
                quote = not quote
            elif not quote and char == "{":
                stack.append("}")
            elif not quote and char == stack[-1]:
                stack.pop()
            j += 1
        if stack:
            raise ValueError(f"Unclosed bibliography entry at offset {i}")
        if kind.lower() not in {"comment", "preamble", "string"}:
            key = text[start:j - 1].split(",", 1)[0].strip()
            if not key or any(c.isspace() for c in key):
                raise ValueError(f"Invalid bibliography key at offset {i}")
            if key in keys:
                duplicates.append(key)
            keys.add(key)
        i = j
    return keys, duplicates


def audit_latex(root: Path, entry: Path) -> dict:
    root = root.resolve()
    findings, files, labels, refs, citations = [], [], {}, [], []
    keys, visited, active, defined = set(), set(), [], {}
    counts = {"labels": 0, "references": 0, "citations": 0, "bibliography_entries": 0, "images": 0}

    def report(code, path, line, message, severity="error"):
        findings.append(dict(severity=severity, code=code, path=str(path), line=line, message=message))

    def resolve(raw: str, extensions=()) -> Path | None:
        if "\\" in raw or "#" in raw:
            return None
        path = (root / raw).resolve()
        if not path.is_relative_to(root):
            return None
        if path.is_file():
            return path
        for extension in extensions:
            candidate = Path(str(path) + extension) if path.suffix != extension else path
            if candidate.is_file():
                return candidate
        return path

    def has_dependencies(name: str, seen=None) -> bool:
        seen = set() if seen is None else seen
        if name in seen or name not in defined:
            return False
        seen = seen | {name}
        body = defined[name]["body"] + defined[name].get("end_body", "")
        for item in commands(body):
            if item.name in {"includegraphics", "XeTeXpicfile", "input", "include", "label", "ref", "pageref", "autoref"} or "cite" in item.name.lower() or has_dependencies(item.name, seen):
                return True
        return False

    def walk(path: Path, pending_break: bool = False) -> bool:
        path = path.resolve()
        if not path.is_relative_to(root):
            report("unsafe_path", path, 1, "Path escapes compilation root")
            return pending_break
        if path in active:
            report("include_cycle", path, 1, " -> ".join(str(p.relative_to(root)) for p in active + [path]))
            return pending_break
        if path in visited:
            report("repeated_include", path.relative_to(root), 1, "File is included more than once; counters and text may duplicate")
            return pending_break
        if not path.is_file():
            report("missing_file", path, 1, "Required source file does not exist")
            return pending_break
        visited.add(path)
        active.append(path)
        relative = path.relative_to(root)
        files.append(str(relative))
        try:
            text = path.read_text(encoding="utf-8")
            tokens = list(commands(text))
            definitions = macro_definitions(text)
        except (UnicodeError, ValueError, OSError) as exc:
            report("parse_error", relative, 1, str(exc))
            active.pop()
            return pending_break
        sprint_file = "sprint" in path.stem.lower()
        for token in tokens:
            line = text.count("\n", 0, token.start) + 1
            name, args = token.name, token.args
            definition = next((item for item in definitions if item["start"] == token.start), None)
            if definition:
                defined[definition["name"]] = definition
                continue
            if any(item["start"] <= token.start < item["end"] for item in definitions):
                continue  # Dormant bodies are not operational invocations.
            if name == "memorialfigure":
                contract = defined.get(name)
                if contract is None or contract["arity"] != 5 or contract["optional_default"] or canonical_macro_body(contract["body"]) != canonical_macro_body(MEMORIAL_FIGURE_BODY):
                    report("unverified_figure_macro", relative, line, "memorialfigure definition does not match the audited five-argument contract")
                    continue
                if len(args) != 5:
                    report("invalid_figure_macro", relative, line, "memorialfigure requires file, caption, label, source, width")
                    continue
                counts["images"] += 1
                target = resolve(args[0], (".pdf", ".png", ".jpg", ".jpeg", ".eps"))
                if target is None or not target.is_file():
                    report("missing_or_dynamic_asset", relative, line, args[0])
                if args[3] != "Fonte: pendente de identificação" or not re.fullmatch(r"(?:0?\.\d+|1(?:\.0+)?)", args[4]) or not 0 < float(args[4]) <= 1 or token.optionals or token.starred:
                    report("invalid_figure_apparatus", relative, line, "Source must remain explicitly pending and width must be a fraction in (0,1]")
                if not args[1].strip() or not re.fullmatch(r"[A-Za-z0-9:._-]+", args[2]):
                    report("missing_figure_caption_or_label", relative, line, "Caption and label must be explicit")
                counts["labels"] += 1
                if args[2] in labels:
                    report("duplicate_label", relative, line, args[2])
                labels[args[2]] = (relative, line)
                continue
            if name in defined and has_dependencies(name):
                report("unsupported_operational_macro", relative, line, f"Invocation \\{name} contains dependencies/references; expansion is unproven")
                continue
            if name == "begin" and args and args[0] in defined and defined[args[0]]["environment"] and has_dependencies(args[0]):
                report("unsupported_operational_macro", relative, line, f"Environment {args[0]} contains dependencies/references; expansion is unproven")
                continue
            if name in {"newpage", "clearpage", "cleardoublepage", "pagebreak"}:
                pending_break = True
                if sprint_file:
                    report("sprint_page_break", relative, line, "Explicit page break in Sprint file")
            if name in {"chapter", "section", "subsection", "subsubsection"}:
                title = args[0] if args else ""
                if "sprint" in title.lower() and (pending_break or name == "chapter"):
                    report("sprint_page_break", relative, line, "Sprint title follows a forced break or uses chapter")
                pending_break = False
            if name in {"input", "include"} and not args:
                report("unsupported_include_syntax", relative, line, "Use an explicit braced path for deterministic auditing")
            elif name in {"input", "include"} and args:
                target = resolve(args[0], (".tex",))
                if target is None:
                    report("unsafe_or_dynamic_include", relative, line, args[0])
                else:
                    if name == "include" and "sprint" in target.name.lower():
                        report("sprint_include", relative, line, "include forces a page break; use input for Sprints")
                    if pending_break and "sprint" in target.name.lower():
                        report("sprint_page_break", relative, line, "Sprint input follows an explicit page break in its parent")
                    pending_break = walk(target, pending_break)
            elif name in {"addbibresource", "bibliography"} and args:
                for raw in args[0].split(","):
                    target = resolve(raw.strip(), (".bib",))
                    if target is None or not target.is_file():
                        report("missing_bibliography", relative, line, raw)
                    else:
                        try:
                            found, duplicates = bib_keys(target.read_text(encoding="utf-8"))
                            for duplicate in duplicates + sorted(keys & found):
                                report("duplicate_bib_key", relative, line, duplicate)
                            keys.update(found)
                        except (ValueError, OSError, UnicodeError) as exc:
                            report("bibliography_parse_error", relative, line, str(exc))
            elif name == "label" and args:
                counts["labels"] += 1
                if args[0] in labels:
                    report("duplicate_label", relative, line, args[0])
                labels[args[0]] = (relative, line)
            elif name in {"ref", "pageref", "autoref", "cref", "Cref", "eqref", "nameref"} and args:
                refs.extend((value.strip(), relative, line) for value in args[0].split(","))
            elif name in {"cite", "citep", "citet", "parencite", "textcite", "autocite", "footcite", "nocite", "citeauthor", "citeyear", "fullcite", "citealp", "citealt", "smartcite", "supercite"} and args:
                citations.extend((value.strip(), relative, line) for value in args[0].split(",") if value.strip() != "*")
            elif name in {"cites", "parencites", "textcites", "autocites", "footcites", "smartcites", "supercites"} and args:
                citations.extend((value.strip(), relative, line) for arg in args for value in arg.split(",") if value.strip() != "*")
            elif "cite" in name.lower() and name not in {"printbibliography", "addbibresource"}:
                report("unsupported_citation_command", relative, line, f"Cannot resolve \\{name} deterministically", "warning")
            elif name == "XeTeXpicfile":
                report("unsupported_native_image", relative, line, "Native picture syntax requires the canonical memorialfigure contract")
            elif name == "includegraphics" and args:
                counts["images"] += 1
                target = resolve(args[0], (".pdf", ".png", ".jpg", ".jpeg", ".eps"))
                if target is None or not target.is_file():
                    report("missing_or_dynamic_asset", relative, line, args[0])
            elif name in {"href", "url"} and args and re.search(r"(?<!\\)%", args[0]):
                report("unescaped_url_percent", relative, line, "URL retained for inspection; verify percent handling in the compiler/package", "warning")
        active.pop()
        return pending_break

    walk(entry if entry.is_absolute() else root / entry)
    for value, path, line in refs:
        if value not in labels:
            report("undefined_reference", path, line, value)
    for value, path, line in citations:
        if value not in keys:
            report("undefined_citation", path, line, value)
    counts.update(references=len(refs), citations=len(citations), bibliography_entries=len(keys), files=len(files))
    for path in sorted(root.rglob("*.tex")):
        if path.resolve() not in visited:
            report("unreachable_tex", path.relative_to(root), 1, "Not in active inclusion graph (may be an intentional example)", "warning")
    return {"status": "fail" if any(f["severity"] == "error" for f in findings) else "pass", "findings": findings, "files": files, "counts": counts}
