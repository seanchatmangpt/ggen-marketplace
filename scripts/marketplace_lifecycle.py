#!/usr/bin/env python3
"""Pack lifecycle registry: per-pack state plus planned intent, from lifecycle.toml.

The real ggen pack loader deserializes `[pack]` with deny-unknown-fields, so
lifecycle metadata cannot live in `pack.toml` (see the comment in
packs/clap-noun-verb-pack/pack.toml). The marketplace therefore owns it in a
root-level registry. Pure functions; stdlib only; an absent file is an empty
registry, never an error.

Two independent axes:

  state   what the pack IS now          active | deprecated | superseded | retired
  intent  what we PLAN for it (advisory) consolidate | upgrade | replace | review | keep-separate

`state` changes how consumers should treat the pack; `intent` is a review flag
that never changes generation output. Neither deletes anything.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

REGISTRY_RELATIVE = "lifecycle.toml"
SCHEMA_VERSION = "1.0.0"

STATES = ("active", "deprecated", "superseded", "retired")
INTENTS = ("consolidate", "upgrade", "replace", "review", "keep-separate")
ENTRY_KEYS = frozenset({"state", "intent", "successors", "related", "reason", "since", "evidence"})

# A state that obliges consumers to move: successors are mandatory and must be live.
MIGRATING_STATES = ("superseded", "retired")
# Intents that name peers/successors, and the field each one requires.
INTENT_REQUIRES = {"consolidate": "related", "keep-separate": "related", "replace": "successors"}
VERSION_TAG = re.compile(r"^v\d+\.\d+\.\d+$")

Refuse = Callable[[str, str], str]


def load(root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """(entries, structural problems as (code, detail) strings `CODE:detail`). Missing file -> ({}, [])."""
    path = root / REGISTRY_RELATIVE
    if not path.is_file():
        return {}, []
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        return {}, [f"LIFECYCLE_TOML_INVALID:{exc}"]
    problems: list[str] = []
    if document.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"LIFECYCLE_SCHEMA_VERSION:{document.get('schema_version')!r}!={SCHEMA_VERSION}")
    packs = document.get("packs", {})
    if not isinstance(packs, dict):
        return {}, problems + ["LIFECYCLE_PACKS_TYPE:[packs] must be a table of tables"]
    entries: dict[str, dict[str, Any]] = {}
    for name, entry in packs.items():
        if isinstance(entry, dict):
            entries[name] = entry
        else:
            problems.append(f"LIFECYCLE_ENTRY_TYPE:{name}")
    return entries, problems


def _string_list(value: Any) -> list[str] | None:
    if isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value):
        return list(value)
    return None


def entry_issues(
    entries: Mapping[str, Mapping[str, Any]],
    manifests: Mapping[str, Mapping[str, Any]],
    root: Path,
    refuse: Refuse,
) -> list[str]:
    """Refusals for malformed, dangling, contradictory or cyclic lifecycle entries.

    `manifests` maps every pack name to its `[pack]` table; its key set is the set of known packs.
    """
    known = set(manifests)
    issues: list[str] = []
    for name in sorted(entries):
        entry = entries[name]
        if name not in known:
            issues.append(refuse("LIFECYCLE_PACK_UNKNOWN", name))
            continue
        for key in sorted(set(entry) - ENTRY_KEYS):
            issues.append(refuse("LIFECYCLE_KEY_UNKNOWN", f"{name}:{key}"))
        state = entry.get("state", "active")
        intent = entry.get("intent")
        if state not in STATES:
            issues.append(refuse("LIFECYCLE_STATE_UNKNOWN", f"{name}:{state!r}"))
        if intent is not None and intent not in INTENTS:
            issues.append(refuse("LIFECYCLE_INTENT_UNKNOWN", f"{name}:{intent!r}"))
        if state == "active" and intent is None:
            issues.append(refuse("LIFECYCLE_ENTRY_EMPTY", f"{name}:active without intent carries no information"))
        if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
            issues.append(refuse("LIFECYCLE_REASON_MISSING", name))
        if "since" in entry and not (isinstance(entry["since"], str) and VERSION_TAG.match(entry["since"])):
            issues.append(refuse("LIFECYCLE_SINCE_FORMAT", f"{name}:{entry['since']!r}"))
        if intent == "keep-separate" and state != "active":
            issues.append(refuse("LIFECYCLE_KEEP_SEPARATE_STATE", f"{name}:{state}"))

        lists: dict[str, list[str]] = {}
        for key in ("successors", "related", "evidence"):
            if key not in entry:
                lists[key] = []
                continue
            parsed = _string_list(entry[key])
            if parsed is None:
                issues.append(refuse(f"LIFECYCLE_{key.upper()}_TYPE", name))
                parsed = []
            elif len(parsed) != len(set(parsed)):
                issues.append(refuse(f"LIFECYCLE_{key.upper()}_DUPLICATE", name))
            lists[key] = parsed

        if state in MIGRATING_STATES and not lists["successors"]:
            issues.append(refuse("LIFECYCLE_SUCCESSOR_REQUIRED", f"{name}:state={state}"))
        required = INTENT_REQUIRES.get(intent) if isinstance(intent, str) else None
        if required and not lists[required]:
            issues.append(refuse(f"LIFECYCLE_{required.upper()}_REQUIRED", f"{name}:intent={intent}"))
        for target in lists["successors"]:
            if target == name:
                issues.append(refuse("LIFECYCLE_SUCCESSOR_SELF", name))
            elif target not in known:
                issues.append(refuse("LIFECYCLE_SUCCESSOR_UNKNOWN", f"{name}:{target}"))
            elif entries.get(target, {}).get("state", "active") in MIGRATING_STATES:
                issues.append(refuse("LIFECYCLE_SUCCESSOR_NOT_LIVE", f"{name}:{target} is itself {entries[target].get('state')}"))
        for peer in lists["related"]:
            if peer == name:
                issues.append(refuse("LIFECYCLE_RELATED_SELF", name))
            elif peer not in known:
                issues.append(refuse("LIFECYCLE_RELATED_UNKNOWN", f"{name}:{peer}"))
        for relative in lists["evidence"]:
            target_path = (root / relative).resolve()
            if root.resolve() not in target_path.parents or not target_path.exists():
                issues.append(refuse("LIFECYCLE_EVIDENCE_MISSING", f"{name}:{relative}"))

        manifest = manifests.get(name, {})
        manifest_says_retired = bool(manifest.get("superseded_by")) or manifest.get("deprecated") is True
        if manifest_says_retired and state == "active":
            issues.append(refuse("LIFECYCLE_MANIFEST_CONFLICT", f"{name}:pack.toml marks it non-active, registry says active"))
    return issues


def resolve(
    name: str,
    entry: Mapping[str, Any] | None,
    manifest: Mapping[str, Any],
    manifest_lifecycle: Callable[[], Mapping[str, Any]],
) -> dict[str, Any]:
    """Catalog lifecycle projection: status/deprecated/successors (legacy keys) plus `lifecycle`.

    The registry is authoritative when it has an entry; otherwise the legacy pack.toml keys decide
    (`manifest_lifecycle` computes that fallback lazily).
    """
    if entry is None:
        base = dict(manifest_lifecycle())
        base["lifecycle"] = None
        return base
    state = entry.get("state", "active")
    successors = list(entry.get("successors", []))
    return {
        "deprecated": state != "active",
        "status": state,
        "successors": successors,
        "lifecycle": {
            "evidence": list(entry.get("evidence", [])),
            "intent": entry.get("intent"),
            "reason": entry["reason"],
            "related": list(entry.get("related", [])),
            "since": entry.get("since"),
        },
    }


def listing(records: Iterable[Mapping[str, Any]], state: str | None, intent: str | None) -> list[str]:
    """Tab-free fixed-column lines for packs carrying lifecycle information, filtered by state/intent."""
    lines: list[str] = []
    for record in sorted(records, key=lambda r: r["name"]):
        life = record.get("lifecycle")
        if life is None and record["status"] == "active":
            continue
        rec_intent = (life or {}).get("intent")
        if state and record["status"] != state:
            continue
        if intent and rec_intent != intent:
            continue
        reason = " ".join(((life or {}).get("reason") or "").split())
        links = ",".join(record["successors"] or (life or {}).get("related", []))
        lines.append(f"{record['name']} {record['status']} {rec_intent or '-'} {links or '-'} {reason}")
    return lines
