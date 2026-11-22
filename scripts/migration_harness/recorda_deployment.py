"""Verify the Recorda deployment correction against its exact predecessor."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import shutil
import tempfile


APPROVAL = "migration/approvals/recorda-deployment-2026-11-18.json"
APPROVAL_SHA256 = "376276e6320893a23683eee2df048ff85f343f2c3fe9c0103f4422a1a03569ac"
BIBLIOGRAPHY = "relatorio_AGES_eduardo/bibliografia/bibliografia.bib"
REMOVED_CITATION = "ages-iv-supabase"


def load(repo: Path) -> dict:
    raw = (repo / APPROVAL).read_bytes()
    if hashlib.sha256(raw).hexdigest() != APPROVAL_SHA256:
        raise ValueError("Recorda deployment approval hash mismatch")
    return json.loads(raw)


def previous_bytes(data: bytes, spec: dict) -> bytes:
    if hashlib.sha256(data).hexdigest() != spec["after_sha256"]:
        raise ValueError("Recorda deployment target differs from the exact approved bytes")
    for edit in reversed(spec["edits"]):
        offset = edit["offset"]
        after = edit["after"].encode("utf-8")
        end = offset + len(after)
        if data[offset:end] != after:
            raise ValueError("Recorda deployment edit no longer matches its approved interval")
        data = data[:offset] + edit["before"].encode("utf-8") + data[end:]
    if hashlib.sha256(data).hexdigest() != spec["before_sha256"]:
        raise ValueError("Recorda deployment predecessor hash mismatch")
    return data


def verify_figure_asset(repo: Path, figure: dict) -> None:
    path = (repo / figure["asset_path"]).resolve()
    if not path.is_relative_to(repo.resolve()):
        raise ValueError("Recorda deployment image escapes the repository")
    if hashlib.sha256(path.read_bytes()).hexdigest() != figure["asset_sha256"]:
        raise ValueError("Recorda deployment image does not match the supplied PNG")


@contextmanager
def predecessor(repo: Path, approval: dict):
    """Replay the preservation ledger against the audited predecessor in isolation."""
    verify_figure_asset(repo, approval["figure_25"])
    originals = {}
    for relative, spec in approval["files"].items():
        path = (repo / relative).resolve()
        if not path.is_relative_to(repo):
            raise ValueError("Recorda deployment target escapes the repository")
        try:
            originals[relative] = previous_bytes(path.read_bytes(), spec)
        except ValueError as error:
            raise ValueError(f"{relative}: {error}") from error

    with tempfile.TemporaryDirectory(prefix="ages-recorda-predecessor-") as temporary:
        snapshot = Path(temporary)
        shutil.copyfile(repo / "RELATORIO_ATUAL.odt", snapshot / "RELATORIO_ATUAL.odt")
        for relative in ("relatorio_AGES_eduardo", "migration", "docs", "tests/fixtures"):
            shutil.copytree(repo / relative, snapshot / relative)
        (snapshot / APPROVAL).unlink()
        for relative, data in originals.items():
            (snapshot / relative).write_bytes(data)
        yield snapshot
