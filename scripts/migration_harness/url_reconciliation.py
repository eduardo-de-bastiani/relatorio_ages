"""Exact, supplemental URL presentation; historical preservation stays in force."""
import hashlib
import json

CONTRACT = "migration/approvals/url-presentation-2026-11-11.json"
SHA256 = "cbee9a91bde5a6a72c8dc1fb90fa470b382ffb6fc5ee6b9a57eb4f3f86f5dbe2"


def load_unit(repo, uid, unit, records):
    path = repo / CONTRACT
    claimed = unit.get("url_presentation_authorization")
    if not path.exists() and claimed is None:
        return {}
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("URL presentation supplement does not match pinned authorization")
    contract = json.loads(data)
    spec = contract["units"].get(uid)
    if spec is None:
        if claimed is not None:
            raise ValueError("URL presentation claimed outside authorized units")
        return {}
    changes = spec["changes"]
    ids = [change["source_id"] for change in changes]
    if claimed != {"evidence": CONTRACT, "source_ids": ids} or unit.get("tex_path") != spec["tex_path"]:
        raise ValueError("URL presentation ledger scope missing or changed")
    data = (repo / spec["tex_path"]).read_bytes()
    layout = spec.get("local_layout")
    if layout and data.decode("utf-8").count(layout["after"]) != 1:
        raise ValueError("Authorized local URL layout differs from exact supplement")
    mappings = {m["source_id"]: m for m in unit.get("element_map", [])}
    projections = {}
    for change in changes:
        rid = change["source_id"]
        mapping = mappings[rid]
        if (records[rid].get("href") != change["destination"]
                or mapping.get("target_file") != spec["tex_path"]
                or mapping.get("target_sha256") != hashlib.sha256(data).hexdigest()):
            raise ValueError(f"URL source, target or ledger digest changed for {rid}")
        start, end = mapping["start_byte"], mapping["end_byte"]
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(data):
            raise ValueError(f"Invalid URL evidence interval for {rid}")
        actual = data[start:end].decode("utf-8")
        if actual != change["after"]:
            raise ValueError(f"URL evidence differs from authorized exact text for {rid}")
        for source_id in (rid, change["paragraph_id"]):
            if source_id:
                projections.setdefault(source_id, []).append((change["after"], change["before"]))
    return projections


def project(mapping, value, projections):
    for after, before in projections.get(mapping.get("source_id"), []):
        if value.count(after) != 1:
            raise ValueError("Authorized URL transformation is missing or ambiguous in mapped interval")
        value = value.replace(after, before, 1)
    return value


def previous_bytes(repo, uid, data):
    """Recover pinned predecessor only when the entire successor matches exactly."""
    raw = (repo / CONTRACT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError("URL presentation supplement does not match pinned authorization")
    spec = json.loads(raw)["units"].get(uid)
    if not spec or hashlib.sha256(data).hexdigest() != spec["after_sha256"]:
        raise ValueError("URL presentation successor bytes differ from authorization")
    def restore(text, index):
        if index == len(spec["changes"]):
            candidate = text.encode("utf-8")
            return candidate if hashlib.sha256(candidate).hexdigest() == spec["before_sha256"] else None
        change = spec["changes"][index]
        after, before = change["after"], change["before"]
        start = 0
        while (position := text.find(after, start)) >= 0:
            result = restore(text[:position] + before + text[position + len(after):], index + 1)
            if result is not None:
                return result
            start = position + len(after)
        return None
    text = data.decode("utf-8")
    layout = spec.get("local_layout")
    if layout:
        if text.count(layout["after"]) != 1:
            raise ValueError("Authorized local URL layout differs from supplement")
        text = text.replace(layout["after"], layout["before"], 1)
    result = restore(text, 0)
    if result is None:
        raise ValueError("URL presentation predecessor bytes differ from authorization")
    return result


def layout_group_spans(repo, uid, data):
    raw = (repo / CONTRACT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError("URL presentation supplement does not match pinned authorization")
    spec = json.loads(raw)["units"].get(uid, {})
    layout = spec.get("local_layout")
    if not layout:
        return []
    line = layout["after"].encode("utf-8")
    if data.count(line) != 1:
        raise ValueError("Authorized local URL layout differs from exact supplement")
    start = data.index(line)
    prefix, suffix = b"\\begingroup", b"\\endgroup"
    if not line.startswith(prefix) or not line.endswith(suffix):
        raise ValueError("Invalid group layout")
    return [(start, start + len(prefix)), (start + len(line) - len(suffix), start + len(line))]
