#!/usr/bin/env python3
"""packs.lock.json read/write helpers shared by fetch_pack.py."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LOCK_SCHEMA = "https://ggen.dev/marketplace/packs-lock/v1"
LOCK_FIELDS = ("name", "version", "digest", "download_url")


class LockError(Exception):
    """Raised with a REFUSED:<CODE> message."""


def entry_from_catalog_record(record: dict[str, Any]) -> dict[str, str]:
    missing = [f for f in LOCK_FIELDS if not isinstance(record.get(f), str) or not record.get(f)]
    if missing:
        raise LockError(f"REFUSED:CATALOG_RECORD_INCOMPLETE {record.get('name')!r} missing {missing}")
    return {f: record[f] for f in LOCK_FIELDS}


def build_lock(catalog: dict[str, Any], names: list[str]) -> dict[str, Any]:
    by_name = {p.get("name"): p for p in catalog.get("packs", [])}
    entries = []
    for name in names:
        if name not in by_name:
            raise LockError(f"REFUSED:PACK_NOT_IN_CATALOG {name}")
        entries.append(entry_from_catalog_record(by_name[name]))
    entries.sort(key=lambda e: e["name"])
    return {"schema": LOCK_SCHEMA, "packs": entries}


def write_lock(path: Path, lock: dict[str, Any]) -> None:
    path.write_text(json.dumps(lock, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def read_lock(path: Path) -> dict[str, Any]:
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LockError(f"REFUSED:LOCK_UNREADABLE {path}: {exc}") from exc
    if lock.get("schema") != LOCK_SCHEMA or not isinstance(lock.get("packs"), list):
        raise LockError(f"REFUSED:LOCK_SCHEMA {path}")
    return lock


def lock_entry(lock: dict[str, Any], name: str) -> dict[str, str]:
    for entry in lock["packs"]:
        if entry.get("name") == name:
            return entry
    raise LockError(f"REFUSED:PACK_NOT_IN_LOCK {name}")
