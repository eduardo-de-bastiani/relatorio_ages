"""Fail-closed validator for the explicitly scoped bibliography reconciliation."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


CONTRACT = "migration/approvals/bibliography-reconciliation-2026-11-06.json"
CONTRACT_SHA256 = "c4cec5a8ff924f45980c277294096bb7ba7b5adbc09c85ec23bc01e6cb6c253b"
SOURCE_PATH = "tests/fixtures/bibliography/pre-reconciliation-55-entries.bib"
SOURCE_SHA256 = "b20d34f1c754e8b9396b28e6db02f74d79fd896691de3e2e7281313bec681fe9"
INTERMEDIATE_SHA256 = "6be2693c464927ace22c8d3f99250a877de1256455abfc7673396e0578e4aaf6"
RESULT_PATH = "tests/fixtures/bibliography/consolidated-49-entries-44-estimates.bib"
RESULT_BIBLIOGRAPHY_PATH = "relatorio_AGES_eduardo/bibliografia/bibliografia.bib"
RESULT_SHA256 = "cdcab53b070ad7735b77ec27d0d02ec84d8180d89369baa0e82f1dfcbf7b763d"
ODT_SHA256 = "e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef"
EVIDENCE_PATH = "migration/evidence/references/estimated-years-2026-11-06.json"
EVIDENCE_SHA256 = "5e0bfd3b2d1cf3d952fe91b4a72cc1be45d579153eae309a54392e5048a46da7"
SUPPLEMENT_CONTRACT = "migration/approvals/bibliography-reconciliation-2026-11-06-supplement.json"
SUPPLEMENT_CONTRACT_SHA256 = "a61a9d75ae4787d0e85af601b9f5a55ca18136a2d160cfc92f36e13bffb8a82d"
SUPPLEMENT_SOURCE_PATH = RESULT_PATH
SUPPLEMENT_SOURCE_SHA256 = RESULT_SHA256
SUPPLEMENT_RESULT_PATH = "tests/fixtures/bibliography/reconciled-49-entries-current.bib"
SUPPLEMENT_RESULT_SHA256 = "97711d58f81c947fc3c91961de3a9ad2cb546a5a0771b1dc457abaa484d491a5"
SUPPLEMENT_BIBLIOGRAPHY_PATH = RESULT_BIBLIOGRAPHY_PATH
AUTHOR_CONTRACT = "migration/approvals/bibliography-reconciliation-2026-11-06-author-informed.json"
AUTHOR_CONTRACT_SHA256 = "99749eac9cc281a9a7feab360e82ed8c4b3e370d6e304df0776d6af9b60cbe8d"
AUTHOR_SOURCE_PATH = SUPPLEMENT_RESULT_PATH
AUTHOR_SOURCE_SHA256 = SUPPLEMENT_RESULT_SHA256
AUTHOR_RESULT_PATH = "tests/fixtures/bibliography/author-supplied-49-entries.bib"
AUTHOR_RESULT_SHA256 = "dcb52a8ea1e0d270e4ef346080dd6bf78ff71e8a5db82988b259945d5fc3628b"
AUTHOR_ESTIMATED_ACCESS_NOTE = "Data de acesso estimada"
ESTIMATED_ACCESS_CONTRACT = "migration/approvals/bibliography-reconciliation-2026-11-06-estimated-access.json"
ESTIMATED_ACCESS_CONTRACT_SHA256 = "3db13d5280d601d1ffc9f193fe95b4459cecaf97fbb73aca437b3a04ce38ade0"
ESTIMATED_ACCESS_SOURCE_PATH = AUTHOR_RESULT_PATH
ESTIMATED_ACCESS_SOURCE_SHA256 = AUTHOR_RESULT_SHA256
ESTIMATED_ACCESS_RESULT_PATH = "tests/fixtures/bibliography/estimated-access-varied-49-entries.bib"
ESTIMATED_ACCESS_RESULT_SHA256 = "e2fe256debf6ee648e741fa2d9f036de9654c51d7892dcb8f832a463fdbeffb4"
ESTIMATED_ACCESS_EVIDENCE_PATH = "migration/evidence/references/estimated-access-varied-2026-11-06.json"
ESTIMATED_ACCESS_EVIDENCE_SHA256 = "0075c5b412d40ed55d7b46918fd12036f839a8f80c7a95732c0bca7aa932339c"
FACTUAL_DATES = {
    "ages-ii-http-rfc9110": "2022-06",
    "ages-ii-json-rfc8259": "2017-12",
    "ages-iii-mqtt": "2019-03-07",
    "ages-iii-rfid-nist": "2007-05-17",
    "ages-iii-fielding-rest": "2000",
}
CONSOLIDATIONS = {
    "ages-iv-typescript": "typescript-docs",
    "react-docs": "ages-iii-react",
    "postgresql-docs": "ages-iv-postgresql",
    "ages-ii-postgresql": "ages-iv-postgresql",
    "ages-ii-figma": "ages-i-figma",
    "ages-ii-docker": "ages-iii-docker",
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_contract(repo: Path, contract: dict, raw: bytes) -> None:
    if not CONTRACT_SHA256 or _sha(raw) != CONTRACT_SHA256:
        raise ValueError("Bibliography reconciliation contract is not the pinned approval")
    expected = {
        "source_path": SOURCE_PATH,
        "source_sha256": SOURCE_SHA256,
        "intermediate_sha256": INTERMEDIATE_SHA256,
        "result_path": RESULT_PATH,
        "result_bibliography_path": RESULT_BIBLIOGRAPHY_PATH,
        "result_sha256": RESULT_SHA256,
        "odt_sha256": ODT_SHA256,
        "evidence_path": EVIDENCE_PATH,
        "evidence_sha256": EVIDENCE_SHA256,
        "consolidations": CONSOLIDATIONS,
    }
    observed = {
        "source_path": contract.get("source", {}).get("path"),
        "source_sha256": contract.get("source", {}).get("sha256"),
        "intermediate_sha256": contract.get("intermediate", {}).get("sha256"),
        "result_path": contract.get("result", {}).get("path"),
        "result_bibliography_path": contract.get("result", {}).get("bibliography_path"),
        "result_sha256": contract.get("result", {}).get("sha256"),
        "odt_sha256": contract.get("source_odt_sha256"),
        "evidence_path": contract.get("metadata_policy", {}).get("estimated_years_evidence"),
        "evidence_sha256": contract.get("metadata_policy", {}).get("estimated_years_evidence_sha256"),
        "consolidations": contract.get("consolidations"),
    }
    if observed != expected:
        raise ValueError("Bibliography reconciliation scope differs from the pinned contract")
    odt = _safe_path(repo, "RELATORIO_ATUAL.odt").read_bytes()
    if _sha(odt) != ODT_SHA256:
        raise ValueError("Immutable ODT source hash differs")


def _safe_path(repo: Path, relative: str) -> Path:
    path = (repo / relative).resolve()
    if not path.is_relative_to(repo.resolve()):
        raise ValueError("Bibliography contract path escapes repository")
    return path


def _entries(data: bytes) -> dict[str, tuple[str, str]]:
    text = data.decode("utf-8")
    matches = list(re.finditer(r"(?ms)^@(\w+)\{([^,]+),(.*?)^\}", text))
    values = [(match.group(2).strip(), (match.group(1).lower(), match.group(3))) for match in matches]
    if len(values) != len({key for key, _ in values}):
        raise ValueError("Bibliography contains duplicate keys")
    if not values:
        raise ValueError("Bibliography contains no entries")
    return dict(values)


def _field(entry: str, name: str) -> str | None:
    matches = re.findall(rf"(?im)^\s*{re.escape(name)}\s*=\s*\{{(.*?)\}}\s*,?\s*$", entry)
    if len(matches) > 1:
        raise ValueError(f"Bibliography entry repeats {name}")
    return matches[0] if matches else None


def _field_map(entry: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in re.finditer(r"(?im)^\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*\{(.*?)\}\s*,?\s*$", entry):
        name, value = match.group(1).lower(), match.group(2)
        if name in fields:
            raise ValueError(f"Bibliography entry repeats {name}")
        fields[name] = value
    return fields


def _remove_estimated_dates(data: bytes, estimates: dict[str, dict]) -> bytes:
    text = data.decode("utf-8")
    for key, estimate in estimates.items():
        pattern = rf"(?ms)(^@\w+\{{{re.escape(key)},.*?)(?P<date>^\s*date\s*=\s*\{{{re.escape(estimate['ano'])}\}}\s*,?\s*\n)(.*?^\}})"
        text, count = re.subn(pattern, lambda match: match.group(1) + match.group(3), text, count=1)
        if count != 1:
            raise ValueError(f"Could not isolate the authorized estimated date for {key}")
    return text.encode("utf-8")


def _validate_date_status(evidence: dict, result_entries: dict[str, tuple[str, str]]) -> tuple[dict, dict]:
    estimates = evidence.get("estimated_entries", {})
    factual = evidence.get("factual_dates_preserved", {})
    if factual != FACTUAL_DATES:
        raise ValueError("The five factual publication dates differ from the pinned evidence map")
    if set(estimates) & set(factual) or set(estimates) | set(factual) != set(result_entries):
        raise ValueError("Date evidence must cover every reconciled bibliography entry exactly once")
    for key, evidence_item in estimates.items():
        entry = result_entries[key][1]
        estimate = evidence_item.get("ano")
        if (not isinstance(estimate, str) or not re.fullmatch(r"\d{4}\?", estimate)
                or _field(entry, "date") != estimate or _field(entry, "year") is not None):
            raise ValueError(f"Estimated date for {key} is missing, changed, or converted to a publication year")
    for key, date in factual.items():
        if _field(result_entries[key][1], "date") != date or _field(result_entries[key][1], "year") is not None:
            raise ValueError(f"Factual date for {key} changed from its evidence")
    return estimates, factual


def verify_historical(repo: Path, data: bytes | None = None) -> dict:
    """Verify the original reconciliation and its historical estimated-year fixture."""
    repo = repo.resolve()
    contract_raw = _safe_path(repo, CONTRACT).read_bytes()
    contract = json.loads(contract_raw.decode("utf-8"))
    _validate_contract(repo, contract, contract_raw)
    source_data = _safe_path(repo, SOURCE_PATH).read_bytes()
    result_fixture = _safe_path(repo, RESULT_PATH).read_bytes()
    live_data = data if data is not None else _safe_path(repo, RESULT_BIBLIOGRAPHY_PATH).read_bytes()
    for label, observed, expected in (
        ("source fixture", source_data, contract["source"]["sha256"]),
        ("result fixture", result_fixture, contract["result"]["sha256"]),
        ("integrated bibliography", live_data, contract["result"]["sha256"]),
    ):
        if _sha(observed) != expected:
            raise ValueError(f"{label} differs from the exact approved bibliography reconciliation")

    source_entries = _entries(source_data)
    result_entries = _entries(result_fixture)
    if len(source_entries) != contract["source"]["entry_count"] or len(result_entries) != contract["result"]["entry_count"]:
        raise ValueError("Bibliography entry count differs from the scoped reconciliation contract")
    remap = CONSOLIDATIONS
    expected_keys = (set(source_entries) - set(remap)) | set(remap.values())
    if set(result_entries) != expected_keys:
        raise ValueError("Bibliography keys differ beyond the six authorized consolidations")
    for old_key, new_key in remap.items():
        source_url = _field(source_entries[old_key][1], "url")
        result_url = _field(result_entries[new_key][1], "url")
        if not source_url or source_url != result_url:
            raise ValueError(f"Consolidated citation URL changed for {old_key} -> {new_key}")

    evidence_path = _safe_path(repo, EVIDENCE_PATH)
    evidence_bytes = evidence_path.read_bytes()
    if _sha(evidence_bytes) != EVIDENCE_SHA256:
        raise ValueError("Estimated-year evidence differs from its pinned record")
    evidence = json.loads(evidence_bytes.decode("utf-8"))
    estimates = evidence.get("estimated_entries", {})
    factual = evidence.get("factual_dates_preserved", {})
    if len(estimates) != contract["metadata_policy"]["estimated_entries"] or len(factual) != contract["metadata_policy"]["factual_dates"]:
        raise ValueError("Estimated/factual date counts differ from the reconciliation evidence")
    estimates, factual = _validate_date_status(evidence, result_entries)
    if _sha(_remove_estimated_dates(result_fixture, estimates)) != INTERMEDIATE_SHA256:
        raise ValueError("Removing only the 44 estimated dates does not reproduce the documented intermediate bibliography")
    return {
        "source_entries": len(source_entries),
        "result_entries": len(result_entries),
        "consolidations": len(remap),
        "estimated_dates": len(estimates),
        "factual_dates": len(factual),
        "publication_years_inferred_from_estimates": 0,
    }


def _validate_supplement_contract(repo: Path) -> dict:
    raw = _safe_path(repo, SUPPLEMENT_CONTRACT).read_bytes()
    return _validate_supplement_contract_data(repo, raw)


def _validate_supplement_contract_data(repo: Path, raw: bytes) -> dict:
    if _sha(raw) != SUPPLEMENT_CONTRACT_SHA256:
        raise ValueError("Supplemental bibliography contract is not the pinned approval")
    contract = json.loads(raw.decode("utf-8"))
    expected = {
        "source": {
            "path": SUPPLEMENT_SOURCE_PATH,
            "sha256": SUPPLEMENT_SOURCE_SHA256,
            "entry_count": 49,
            "contract": CONTRACT,
            "contract_sha256": CONTRACT_SHA256,
        },
        "result": {
            "path": SUPPLEMENT_RESULT_PATH,
            "bibliography_path": SUPPLEMENT_BIBLIOGRAPHY_PATH,
            "sha256": SUPPLEMENT_RESULT_SHA256,
            "entry_count": 49,
        },
        "source_odt_sha256": ODT_SHA256,
    }
    observed = {key: contract.get(key) for key in expected}
    if observed != expected:
        raise ValueError("Supplemental bibliography scope differs from its pinned contract")
    if _sha(_safe_path(repo, "RELATORIO_ATUAL.odt").read_bytes()) != ODT_SHA256:
        raise ValueError("Immutable ODT source hash differs")
    return contract


def _validate_supplement_diff(repo: Path, source: bytes, result: bytes, contract: dict) -> dict:
    before, after = _entries(source), _entries(result)
    if set(before) != set(after):
        raise ValueError("Supplemental reconciliation changed the bibliography keys")
    allowed: dict[tuple[str, str], tuple[str | None, str | None]] = {}
    authorized = contract["authorized_changes"]
    for key, old_value in authorized["removed_estimated_date_fields"].items():
        allowed[(key, "date")] = (old_value, None)
    for field, section in (("title", "updated_titles"), ("author", "normalized_authors"), ("urldate", "added_verified_access_dates")):
        for key, change in authorized[section].items():
            allowed[(key, field)] = (change["from"], change["to"])

    observed: dict[tuple[str, str], tuple[str | None, str | None]] = {}
    for key in before:
        if before[key][0] != after[key][0]:
            raise ValueError(f"Supplemental reconciliation changed entry type for {key}")
        old_fields, new_fields = _field_map(before[key][1]), _field_map(after[key][1])
        for field in set(old_fields) | set(new_fields):
            old_value, new_value = old_fields.get(field), new_fields.get(field)
            if old_value != new_value:
                observed[(key, field)] = (old_value, new_value)
    if observed != allowed:
        raise ValueError("Supplemental bibliography contains unapproved field changes")

    evidence = json.loads(_safe_path(repo, EVIDENCE_PATH).read_text(encoding="utf-8"))
    if authorized["removed_estimated_date_fields"] != {
        key: item["ano"] for key, item in evidence.get("estimated_entries", {}).items()
    }:
        raise ValueError("Supplemental removed dates differ from the historical estimate evidence")
    return {"removed_estimated_dates": len(authorized["removed_estimated_date_fields"]),
            "added_verified_access_dates": len(authorized["added_verified_access_dates"]),
            "updated_titles": len(authorized["updated_titles"]),
            "normalized_authors": len(authorized["normalized_authors"])}


def verify(repo: Path, data: bytes | None = None) -> dict:
    """Verify every pinned bibliography state through the current exact final state."""
    repo = repo.resolve()
    historical_fixture = _safe_path(repo, RESULT_PATH).read_bytes()
    historical_facts = verify_historical(repo, data=historical_fixture)
    contract = _validate_supplement_contract(repo)
    source = _safe_path(repo, contract["source"]["path"]).read_bytes()
    fixture = _safe_path(repo, contract["result"]["path"]).read_bytes()
    for label, content in (("supplement source fixture", source), ("supplement result fixture", fixture)):
        expected_hash = contract["source"]["sha256"] if label == "supplement source fixture" else contract["result"]["sha256"]
        if _sha(content) != expected_hash:
            raise ValueError(f"{label} differs from the exact approved bibliography reconciliation")
    if len(_entries(source)) != contract["source"]["entry_count"] or len(_entries(fixture)) != contract["result"]["entry_count"]:
        raise ValueError("Supplemental bibliography entry count differs from contract")
    changes = _validate_supplement_diff(repo, source, fixture, contract)
    author_fixture = _safe_path(repo, AUTHOR_RESULT_PATH).read_bytes()
    author_facts = verify_author_informed(repo, data=author_fixture)
    final_facts = verify_estimated_access_varied(repo, data=data)
    return {
        **historical_facts, **changes, **author_facts, **final_facts,
        "current_entries": len(_entries(fixture)),
    }


def _validate_author_contract(repo: Path) -> dict:
    raw = _safe_path(repo, AUTHOR_CONTRACT).read_bytes()
    return _validate_author_contract_data(repo, raw)


def _validate_author_contract_data(repo: Path, raw: bytes) -> dict:
    if _sha(raw) != AUTHOR_CONTRACT_SHA256:
        raise ValueError("Author-informed bibliography contract is not the pinned approval")
    contract = json.loads(raw.decode("utf-8"))
    expected = {
        "source": {
            "path": AUTHOR_SOURCE_PATH,
            "sha256": AUTHOR_SOURCE_SHA256,
            "entry_count": 49,
            "contract": SUPPLEMENT_CONTRACT,
        },
        "result": {
            "path": AUTHOR_RESULT_PATH,
            "bibliography_path": RESULT_BIBLIOGRAPHY_PATH,
            "sha256": AUTHOR_RESULT_SHA256,
            "entry_count": 49,
        },
        "source_odt_sha256": ODT_SHA256,
    }
    if {key: contract.get(key) for key in expected} != expected:
        raise ValueError("Author-informed bibliography scope differs from its pinned contract")
    author_values = contract.get("author_informed_values", {})
    years = author_values.get("confirmed_years_by_author", {})
    access_dates = author_values.get("estimated_access_dates_by_author", {})
    if (len(years) != 44 or len(access_dates) != 49
            or author_values.get("preserved_documented_dates") != FACTUAL_DATES
            or author_values.get("estimated_access_note") != AUTHOR_ESTIMATED_ACCESS_NOTE
            or "does not represent independently researched evidence" not in author_values.get("provenance", "")):
        raise ValueError("Author-informed bibliography provenance or value counts changed")
    if _sha(_safe_path(repo, "RELATORIO_ATUAL.odt").read_bytes()) != ODT_SHA256:
        raise ValueError("Immutable ODT source hash differs")
    return contract


def _validate_author_informed_diff(source: bytes, result: bytes, contract: dict) -> dict:
    before, after = _entries(source), _entries(result)
    if set(before) != set(after):
        raise ValueError("Author-informed reconciliation changed bibliography keys")
    values = contract["author_informed_values"]
    expected_dates = {**values["preserved_documented_dates"], **values["confirmed_years_by_author"]}
    expected_access = values["estimated_access_dates_by_author"]
    if set(expected_dates) != set(after) or set(expected_access) != set(after):
        raise ValueError("Author-informed date maps must cover the 49 entries exactly")

    allowed: dict[tuple[str, str], tuple[str | None, str | None]] = {}
    for key, value in expected_dates.items():
        old_value = _field_map(before[key][1]).get("date")
        if old_value != value:
            allowed[(key, "date")] = (old_value, value)
    for key, value in expected_access.items():
        old_fields = _field_map(before[key][1])
        if old_fields.get("urldate") != value:
            allowed[(key, "urldate")] = (old_fields.get("urldate"), value)
        if old_fields.get("note") != AUTHOR_ESTIMATED_ACCESS_NOTE:
            allowed[(key, "note")] = (old_fields.get("note"), AUTHOR_ESTIMATED_ACCESS_NOTE)

    observed: dict[tuple[str, str], tuple[str | None, str | None]] = {}
    for key in before:
        if before[key][0] != after[key][0]:
            raise ValueError(f"Author-informed reconciliation changed entry type for {key}")
        old_fields, new_fields = _field_map(before[key][1]), _field_map(after[key][1])
        for field in set(old_fields) | set(new_fields):
            old_value, new_value = old_fields.get(field), new_fields.get(field)
            if old_value != new_value:
                observed[(key, field)] = (old_value, new_value)
    if observed != allowed:
        raise ValueError("Author-informed bibliography contains changes outside its precise field map")

    for key, entry in after.items():
        fields = _field_map(entry[1])
        if fields.get("date") != expected_dates[key] or fields.get("urldate") != expected_access[key]:
            raise ValueError(f"Author-informed date transcription differs for {key}")
        if fields.get("note") != AUTHOR_ESTIMATED_ACCESS_NOTE:
            raise ValueError(f"Estimated access date is not identified for {key}")
        if "year" in fields:
            raise ValueError(f"Author-informed date was converted to a year field for {key}")
    return {
        "author_confirmed_years": len(values["confirmed_years_by_author"]),
        "estimated_access_dates": len(expected_access),
        "documented_dates_preserved": len(values["preserved_documented_dates"]),
        "independent_evidence_claimed": 0,
    }


def verify_author_informed(repo: Path, data: bytes | None = None) -> dict:
    """Verify exact transcription of author-informed years and estimated access dates."""
    repo = repo.resolve()
    historical_fixture = _safe_path(repo, RESULT_PATH).read_bytes()
    verify_historical(repo, data=historical_fixture)
    supplement = _validate_supplement_contract(repo)
    supplement_source = _safe_path(repo, supplement["source"]["path"]).read_bytes()
    supplement_result = _safe_path(repo, supplement["result"]["path"]).read_bytes()
    _validate_supplement_diff(repo, supplement_source, supplement_result, supplement)
    contract = _validate_author_contract(repo)
    source = _safe_path(repo, contract["source"]["path"]).read_bytes()
    fixture = _safe_path(repo, contract["result"]["path"]).read_bytes()
    snapshot = data if data is not None else fixture
    for label, content in (("author-informed source fixture", source),
                            ("author-informed result fixture", fixture),
                            ("author-informed snapshot", snapshot)):
        expected = contract["source"]["sha256"] if label == "author-informed source fixture" else contract["result"]["sha256"]
        if _sha(content) != expected:
            raise ValueError(f"{label} differs from the exact approved bibliography state")
    if len(_entries(source)) != contract["source"]["entry_count"] or len(_entries(fixture)) != contract["result"]["entry_count"]:
        raise ValueError("Author-informed bibliography entry count differs from contract")
    return _validate_author_informed_diff(source, fixture, contract)


def _validate_estimated_access_contract(repo: Path) -> dict:
    raw = _safe_path(repo, ESTIMATED_ACCESS_CONTRACT).read_bytes()
    return _validate_estimated_access_contract_data(repo, raw)


def _validate_estimated_access_contract_data(repo: Path, raw: bytes) -> dict:
    if _sha(raw) != ESTIMATED_ACCESS_CONTRACT_SHA256:
        raise ValueError("Estimated-access bibliography contract is not the pinned approval")
    contract = json.loads(raw.decode("utf-8"))
    evidence_raw = _safe_path(repo, ESTIMATED_ACCESS_EVIDENCE_PATH).read_bytes()
    if _sha(evidence_raw) != ESTIMATED_ACCESS_EVIDENCE_SHA256:
        raise ValueError("Estimated-access evidence differs from its pinned record")
    evidence = json.loads(evidence_raw.decode("utf-8"))
    access_dates = evidence.get("access_dates")
    expected = {
        "source": {
            "path": ESTIMATED_ACCESS_SOURCE_PATH,
            "sha256": ESTIMATED_ACCESS_SOURCE_SHA256,
            "entry_count": 49,
            "contract": AUTHOR_CONTRACT,
            "contract_sha256": AUTHOR_CONTRACT_SHA256,
        },
        "result": {
            "path": ESTIMATED_ACCESS_RESULT_PATH,
            "bibliography_path": RESULT_BIBLIOGRAPHY_PATH,
            "sha256": ESTIMATED_ACCESS_RESULT_SHA256,
            "entry_count": 49,
        },
        "source_odt_sha256": ODT_SHA256,
        "estimated_access_evidence": {
            "path": ESTIMATED_ACCESS_EVIDENCE_PATH,
            "sha256": ESTIMATED_ACCESS_EVIDENCE_SHA256,
            "entry_count": 49,
        },
        "authorized_changes": {
            "removed_estimated_access_note": {
                "keys": sorted(access_dates) if isinstance(access_dates, dict) else None,
                "from": AUTHOR_ESTIMATED_ACCESS_NOTE,
                "to": None,
            },
            "varied_estimated_access_dates": access_dates,
            "publication_date_fields": "unchanged_exactly_from_source",
            "entry_keys_and_types": "unchanged_exactly_from_source",
        },
    }
    observed = {key: contract.get(key) for key in expected}
    if observed != expected or not isinstance(access_dates, dict) or len(access_dates) != 49:
        raise ValueError("Estimated-access bibliography scope differs from its pinned contract/evidence")
    if _sha(_safe_path(repo, "RELATORIO_ATUAL.odt").read_bytes()) != ODT_SHA256:
        raise ValueError("Immutable ODT source hash differs")
    return contract


def _validate_estimated_access_diff(repo: Path, source: bytes, result: bytes, contract: dict) -> dict:
    before, after = _entries(source), _entries(result)
    if set(before) != set(after):
        raise ValueError("Estimated-access reconciliation changed bibliography keys")
    evidence = json.loads(_safe_path(repo, ESTIMATED_ACCESS_EVIDENCE_PATH).read_text(encoding="utf-8"))
    author_contract = _validate_author_contract(repo)
    prior_dates = author_contract["author_informed_values"]["estimated_access_dates_by_author"]
    varied_dates = evidence["access_dates"]
    if set(prior_dates) != set(before) or set(varied_dates) != set(before):
        raise ValueError("Estimated-access date maps must cover the 49 entries exactly")
    allowed: dict[tuple[str, str], tuple[str | None, str | None]] = {}
    for key in before:
        old_fields = _field_map(before[key][1])
        new_fields = _field_map(after[key][1])
        if before[key][0] != after[key][0]:
            raise ValueError(f"Estimated-access reconciliation changed entry type for {key}")
        if old_fields.get("note") != AUTHOR_ESTIMATED_ACCESS_NOTE or "note" in new_fields:
            raise ValueError(f"Estimated-access note was not removed exactly for {key}")
        if old_fields.get("urldate") != prior_dates[key] or new_fields.get("urldate") != varied_dates[key]:
            raise ValueError(f"Estimated access date differs from its exact evidence for {key}")
        if prior_dates[key] == varied_dates[key]:
            raise ValueError(f"Estimated access date was not varied for {key}")
        if old_fields.get("date") != new_fields.get("date") or "year" in old_fields or "year" in new_fields:
            raise ValueError(f"Publication date fields changed for {key}")
        allowed[(key, "note")] = (AUTHOR_ESTIMATED_ACCESS_NOTE, None)
        allowed[(key, "urldate")] = (prior_dates[key], varied_dates[key])

    observed: dict[tuple[str, str], tuple[str | None, str | None]] = {}
    for key in before:
        old_fields, new_fields = _field_map(before[key][1]), _field_map(after[key][1])
        for field in set(old_fields) | set(new_fields):
            old_value, new_value = old_fields.get(field), new_fields.get(field)
            if old_value != new_value:
                observed[(key, field)] = (old_value, new_value)
    if observed != allowed:
        raise ValueError("Estimated-access bibliography contains unapproved field changes")
    return {
        "removed_estimated_access_notes": len(before),
        "varied_estimated_access_dates": len(varied_dates),
        "publication_date_fields_unchanged": len(before),
    }


def verify_estimated_access_varied(repo: Path, data: bytes | None = None) -> dict:
    """Verify note removal and the exact 49-date variation after prior contracts."""
    repo = repo.resolve()
    historical_fixture = _safe_path(repo, RESULT_PATH).read_bytes()
    verify_historical(repo, data=historical_fixture)
    supplement = _validate_supplement_contract(repo)
    _validate_supplement_diff(
        repo, _safe_path(repo, supplement["source"]["path"]).read_bytes(),
        _safe_path(repo, supplement["result"]["path"]).read_bytes(), supplement,
    )
    author = _validate_author_contract(repo)
    author_source = _safe_path(repo, author["source"]["path"]).read_bytes()
    author_result = _safe_path(repo, author["result"]["path"]).read_bytes()
    _validate_author_informed_diff(author_source, author_result, author)
    contract = _validate_estimated_access_contract(repo)
    source = _safe_path(repo, contract["source"]["path"]).read_bytes()
    fixture = _safe_path(repo, contract["result"]["path"]).read_bytes()
    live = data if data is not None else _safe_path(repo, contract["result"]["bibliography_path"]).read_bytes()
    for label, content, expected in (
        ("estimated-access source fixture", source, contract["source"]["sha256"]),
        ("estimated-access result fixture", fixture, contract["result"]["sha256"]),
        ("integrated bibliography", live, contract["result"]["sha256"]),
    ):
        if _sha(content) != expected:
            raise ValueError(f"{label} differs from the exact approved bibliography state")
    if len(_entries(source)) != contract["source"]["entry_count"] or len(_entries(fixture)) != contract["result"]["entry_count"]:
        raise ValueError("Estimated-access bibliography entry count differs from contract")
    return _validate_estimated_access_diff(repo, source, fixture, contract)
