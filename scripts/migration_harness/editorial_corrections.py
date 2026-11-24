"""Exact authorization for the corrections requested after the editorial audit."""

import hashlib
import json
from pathlib import Path


APPROVAL = "migration/approvals/editorial-audit-corrections-2026-11-23.json"
APPROVAL_SHA256 = "e4306559f6c3d85a90711871f972bf5d409a8be2e8413b2c693148b48ac1b082"


def load(repo: Path) -> dict:
    raw = (repo / APPROVAL).read_bytes()
    if hashlib.sha256(raw).hexdigest() != APPROVAL_SHA256:
        raise ValueError("Editorial corrections approval hash mismatch")
    return json.loads(raw)
