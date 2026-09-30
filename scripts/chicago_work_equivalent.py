#!/usr/bin/env python3
"""Chicago court for human-equivalent-work claims over ggen-marketplace.

The court is intentionally conservative. It never turns repository inventory,
commit count, lines of code, or unqualified combinatorics into person-years.
Only admitted lower-bound evidence contributes to the claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_SOURCE_TYPES = frozenset({
    "audited_record",
    "contract_record",
    "external_measurement",
    "published_study",
})
HEX = frozenset("0123456789abcdef")


class CourtRefusal(ValueError):
    """Evidence or subject state is inadmissible."""


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    capability: str
    person_hours_lower_bound: float
    overlap_group: str
    source_type: str
    source_uri: str
    source_digest_sha256: str
    subject_paths: tuple[str, ...]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_head(root: Path) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        raise CourtRefusal(f"EXACT_HEAD_UNAVAILABLE:{proc.stderr.strip()}")
    value = proc.stdout.strip()
    if len(value) != 40 or any(ch not in HEX for ch in value):
        raise CourtRefusal(f"EXACT_HEAD_INVALID:{value}")
    return value


def visible_pack_subjects(root: Path) -> tuple[Path, ...]:
    packs = root / "packs"
    if not packs.is_dir():
        raise CourtRefusal("PACKS_ROOT_MISSING")
    subjects: list[Path] = []
    for pack in sorted((p for p in packs.iterdir() if p.is_dir()), key=lambda p: p.name):
        manifest = pack / "pack.toml"
        turtle = tuple(sorted(pack.glob("*.ttl"))) + tuple(sorted((pack / "ontology").rglob("*.ttl"))) if (pack / "ontology").is_dir() else tuple(sorted(pack.glob("*.ttl")))
        if manifest.is_file() and turtle:
            subjects.append(pack)
    if not subjects:
        raise CourtRefusal("NO_ADMITTED_PACK_SUBJECTS")
    return tuple(subjects)


def corpus_fingerprint(root: Path, subjects: tuple[Path, ...]) -> str:
    h = hashlib.sha256()
    for subject in subjects:
        files = sorted((p for p in subject.rglob("*") if p.is_file()), key=lambda p: p.as_posix())
        for path in files:
            rel = path.relative_to(root).as_posix().encode("utf-8")
            data = path.read_bytes()
            h.update(len(rel).to_bytes(8, "big"))
            h.update(rel)
            h.update(len(data).to_bytes(8, "big"))
            h.update(data)
    return h.hexdigest()


def _require_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CourtRefusal(f"EVIDENCE_FIELD_INVALID:{key}")
    return value.strip()


def parse_item(raw: dict[str, Any], root: Path) -> EvidenceItem:
    evidence_id = _require_string(raw, "evidence_id")
    capability = _require_string(raw, "capability")
    overlap_group = _require_string(raw, "overlap_group")
    source_type = _require_string(raw, "source_type")
    source_uri = _require_string(raw, "source_uri")
    digest = _require_string(raw, "source_digest_sha256").lower()

    if source_type not in ALLOWED_SOURCE_TYPES:
        raise CourtRefusal(f"SOURCE_TYPE_NOT_INDEPENDENT:{evidence_id}:{source_type}")
    if source_uri.startswith(("self:", "repo:", "claim:")):
        raise CourtRefusal(f"SELF_ASSERTION_NOT_EVIDENCE:{evidence_id}")
    if len(digest) != 64 or any(ch not in HEX for ch in digest):
        raise CourtRefusal(f"SOURCE_DIGEST_INVALID:{evidence_id}")

    hours = raw.get("person_hours_lower_bound")
    if not isinstance(hours, (int, float)) or isinstance(hours, bool) or hours <= 0:
        raise CourtRefusal(f"PERSON_HOURS_INVALID:{evidence_id}")

    raw_paths = raw.get("subject_paths")
    if not isinstance(raw_paths, list) or not raw_paths or not all(isinstance(p, str) and p for p in raw_paths):
        raise CourtRefusal(f"SUBJECT_PATHS_INVALID:{evidence_id}")
    subject_paths: list[str] = []
    for value in raw_paths:
        candidate = (root / value).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError as exc:
            raise CourtRefusal(f"SUBJECT_PATH_ESCAPE:{evidence_id}:{value}") from exc
        if not candidate.exists():
            raise CourtRefusal(f"SUBJECT_PATH_MISSING:{evidence_id}:{value}")
        subject_paths.append(value)

    return EvidenceItem(
        evidence_id=evidence_id,
        capability=capability,
        person_hours_lower_bound=float(hours),
        overlap_group=overlap_group,
        source_type=source_type,
        source_uri=source_uri,
        source_digest_sha256=digest,
        subject_paths=tuple(sorted(subject_paths)),
    )


def load_ledger(root: Path, path: Path) -> tuple[float, float, tuple[EvidenceItem, ...]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CourtRefusal(f"LEDGER_INVALID:{exc}") from exc
    if payload.get("schema_version") != 1:
        raise CourtRefusal("LEDGER_SCHEMA_UNSUPPORTED")
    claim = payload.get("claim")
    if not isinstance(claim, dict):
        raise CourtRefusal("CLAIM_MISSING")
    target = claim.get("person_years")
    hours_per_year = claim.get("hours_per_person_year")
    if not isinstance(target, (int, float)) or isinstance(target, bool) or target <= 0:
        raise CourtRefusal("CLAIM_TARGET_INVALID")
    if not isinstance(hours_per_year, (int, float)) or isinstance(hours_per_year, bool) or hours_per_year <= 0:
        raise CourtRefusal("HOURS_PER_YEAR_INVALID")
    raw_items = payload.get("evidence", [])
    if not isinstance(raw_items, list):
        raise CourtRefusal("EVIDENCE_NOT_ARRAY")
    items = tuple(parse_item(item, root) for item in raw_items if isinstance(item, dict))
    if len(items) != len(raw_items):
        raise CourtRefusal("EVIDENCE_ITEM_NOT_OBJECT")
    ids = [item.evidence_id for item in items]
    if len(ids) != len(set(ids)):
        raise CourtRefusal("EVIDENCE_ID_DUPLICATE")
    return float(target), float(hours_per_year), items


def overlap_safe_hours(items: tuple[EvidenceItem, ...]) -> tuple[float, dict[str, float]]:
    """Take max within an overlap group; only disjoint groups add.

    This is deliberately anti-inflationary: two estimates covering the same
    capability/work history cannot be summed merely because they came from
    different documents.
    """
    groups: dict[str, list[float]] = defaultdict(list)
    for item in items:
        groups[item.overlap_group].append(item.person_hours_lower_bound)
    admitted = {name: max(values) for name, values in sorted(groups.items())}
    return sum(admitted.values()), admitted


def receipt(root: Path, ledger_path: Path) -> dict[str, Any]:
    subjects = visible_pack_subjects(root)
    target, hours_per_year, items = load_ledger(root, ledger_path)
    hours, groups = overlap_safe_hours(items)
    years = hours / hours_per_year
    standing = "ALIVE" if years >= target else "UNSUPPORTED:INSUFFICIENT_INDEPENDENT_HUMAN_BASELINE_EVIDENCE"
    return {
        "court": "CHICAGO_MARKETPLACE_WORK_EQUIVALENT_V1",
        "subject": {
            "repository": "seanchatmangpt/ggen-marketplace",
            "exact_head": exact_head(root),
            "pack_subject_count": len(subjects),
            "corpus_sha256": corpus_fingerprint(root, subjects),
        },
        "claim": {
            "target_person_years": target,
            "hours_per_person_year": hours_per_year,
        },
        "observation": {
            "admitted_evidence_items": len(items),
            "overlap_groups": len(groups),
            "overlap_safe_person_hours_lower_bound": hours,
            "person_years_lower_bound": years,
        },
        "standing": standing,
        "exclusions": [
            "commit_count_is_not_person_years",
            "loc_is_not_person_years",
            "pack_count_is_not_person_years",
            "raw_combinatorics_is_not_person_years",
            "self_assertion_is_not_evidence",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("evidence/chicago/marketplace-work-equivalent.json"),
    )
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    ledger = args.ledger if args.ledger.is_absolute() else root / args.ledger
    try:
        result = receipt(root, ledger)
    except CourtRefusal as exc:
        print(f"REFUSED:{exc}", file=sys.stderr)
        return 2

    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(encoded, encoding="utf-8")
    sys.stdout.write(encoded)

    if args.enforce and result["standing"] != "ALIVE":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
