#!/usr/bin/env python3
"""Catalog trust tiers, lifecycle status, discovery and browse projection.

Pure functions over a pack directory: tiers derive from static structure only,
lifecycle from pack.toml [pack] keys plus the DEPRECATED_PACKS registry, and
qualification status only from the committed qualification/baseline.json
(never invented). Stdlib only.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any, Iterable, Mapping

THIN_MAX_FILES = 4
BASELINE_RELATIVE = "qualification/baseline.json"
BROWSE_RELATIVE = "docs/reference/pack-catalog.md"
DESCRIPTION_LIMIT = 80


def _files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.rglob("*") if p.is_file() and not p.name.startswith("."))


def signals(pack_dir: Path) -> dict[str, bool]:
    """Static readiness signals for a pack directory."""
    readme = any(p.is_file() and p.name.lower().startswith("readme") for p in pack_dir.iterdir())
    gates = bool(_files(pack_dir / "gates"))
    witnesses = (
        bool(_files(pack_dir / "witnesses"))
        or (pack_dir / "gate-court.toml").is_file()
        or (pack_dir / "witness.ttl").is_file()
    )
    verify = (
        (pack_dir / "verify.py").is_file()
        or any(bool(_files(pack_dir / name)) for name in ("verify", "verification", "tests", "qualification"))
    )
    return {"gates": gates, "readme": readme, "verify": verify, "witnesses": witnesses}


def file_count(pack_dir: Path) -> int:
    return len(_files(pack_dir))


def tier(sig: Mapping[str, bool], files: int) -> str:
    """thin | documented | verified, from static structure only."""
    if files <= THIN_MAX_FILES or not (sig["readme"] or sig["verify"]):
        return "thin"
    if sig["gates"] and (sig["witnesses"] or sig["verify"]):
        return "verified"
    if sig["readme"]:
        return "documented"
    return "thin"


def manifest_pack_table(pack_dir: Path) -> dict[str, Any]:
    try:
        document = tomllib.loads((pack_dir / "pack.toml").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return {}
    table = document.get("pack")
    return table if isinstance(table, dict) else {}


def lifecycle(name: str, table: Mapping[str, Any], registry: Mapping[str, tuple[str, ...]]) -> dict[str, Any]:
    """status = active|deprecated|superseded plus the successor names."""
    successors = list(registry.get(name, ()))
    superseded_by = table.get("superseded_by")
    if isinstance(superseded_by, str) and superseded_by:
        if superseded_by not in successors:
            successors.append(superseded_by)
        status = "superseded"
    elif name in registry or table.get("deprecated") is True:
        status = "deprecated"
    else:
        status = "active"
    return {"deprecated": status != "active", "status": status, "successors": successors}


def lifecycle_issues(
    tables: Mapping[str, Mapping[str, Any]], all_names: Iterable[str], refuse: Any
) -> list[str]:
    """Refusals for malformed or dangling lifecycle keys. `refuse(code, detail)` formats one."""
    known = set(all_names)
    issues: list[str] = []
    for name, table in sorted(tables.items()):
        if "deprecated" in table and not isinstance(table["deprecated"], bool):
            issues.append(refuse("PACK_DEPRECATED_TYPE", f"{name}:{table['deprecated']!r}"))
        if "superseded_by" in table:
            target = table["superseded_by"]
            if not isinstance(target, str) or not target.strip():
                issues.append(refuse("PACK_SUPERSEDED_BY_TYPE", f"{name}:{target!r}"))
            elif target == name:
                issues.append(refuse("PACK_SUPERSEDED_BY_SELF", name))
            elif target not in known:
                issues.append(refuse("PACK_SUPERSEDED_BY_MISSING", f"{name}:superseded_by={target}"))
    return issues


def load_baseline(root: Path) -> dict[str, str]:
    """pack name -> qualification status, from the committed baseline only; {} if absent."""
    path = root / BASELINE_RELATIVE
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    entries = data.get("packs", data) if isinstance(data, dict) else data
    result: dict[str, str] = {}
    if isinstance(entries, dict):
        items: Iterable[tuple[Any, Any]] = entries.items()
    elif isinstance(entries, list):
        items = ((e.get("name"), e) for e in entries if isinstance(e, dict))
    else:
        return {}
    for name, value in items:
        if isinstance(value, dict):
            value = value.get("status", value.get("standing"))
        if isinstance(name, str) and isinstance(value, str):
            result[name] = value
    return result


def search(records: Iterable[Mapping[str, Any]], terms: Iterable[str]) -> list[Mapping[str, Any]]:
    """Records whose name/description/target_languages/class contain every term (case-insensitive)."""
    wanted = [t.lower() for t in terms if t.strip()]
    hits = []
    for record in records:
        haystack = " ".join(
            [
                record["name"],
                record["description"],
                " ".join(record.get("target_languages", [])),
                record.get("pack_class") or "",
            ]
        ).lower()
        if all(term in haystack for term in wanted):
            hits.append(record)
    return sorted(hits, key=lambda r: r["name"])


def _cell(text: str) -> str:
    text = " ".join(text.split()).replace("|", "\\|")
    if len(text) > DESCRIPTION_LIMIT:
        text = text[: DESCRIPTION_LIMIT - 3].rstrip() + "..."
    return text


def browse_markdown(records: Iterable[Mapping[str, Any]]) -> str:
    rows = sorted(records, key=lambda r: r["name"])
    counts = {t: sum(r["tier"] == t for r in rows) for t in ("verified", "documented", "thin")}
    lines = [
        "# Pack Catalog",
        "",
        "Generated by `python3 scripts/marketplace.py browse`; do not edit by hand.",
        "",
        "## Contents",
        "",
        "- [Trust tiers](#trust-tiers)",
        "- [All packs](#all-packs)",
        "- [See Also](#see-also)",
        "",
        "## Trust tiers",
        "",
        "Tiers derive from static pack structure only; they are not qualification results.",
        "",
        f"- verified ({counts['verified']}): gates plus witnesses or verification material.",
        f"- documented ({counts['documented']}): has a README, lacks verified evidence.",
        f"- thin ({counts['thin']}): four or fewer files, or neither README nor verification.",
        "",
        "## All packs",
        "",
        "| name | version | profile | class | tier | description |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['name']} | {r['version']} | {r['profile']} | {r.get('pack_class') or '-'} "
            f"| {r['tier']} | {_cell(r['description'])} |"
        )
    lines += [
        "",
        "## See Also",
        "",
        "- [Catalog command](catalog-command.md)",
        "- [Pack contract](pack-contract.md)",
        "- [Pack classes](pack-classes.md)",
        "",
    ]
    return "\n".join(lines)
