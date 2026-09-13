#!/usr/bin/env python3
"""Canonical/legacy scope calculus for the DfCM marketplace consolidation."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable, Protocol, TypeVar

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("REFUSED:PYTHON_3_11_REQUIRED") from exc

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_TOML = ROOT / "marketplace.active.toml"


class Named(Protocol):
    name: str


T = TypeVar("T", bound=Named)


def refusal(code: str, detail: str) -> str:
    return f"REFUSED:{code}:{detail}"


def active_pack_names(path: Path = ACTIVE_TOML) -> tuple[str, ...]:
    if not path.is_file():
        raise ValueError(refusal("ACTIVE_SCOPE_MISSING", str(path.relative_to(ROOT))))
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(refusal("ACTIVE_SCOPE_INVALID", str(exc))) from exc
    active = document.get("active")
    raw = active.get("packs") if isinstance(active, dict) else None
    if not isinstance(raw, list) or not raw or not all(isinstance(name, str) and name.strip() for name in raw):
        raise ValueError(refusal("ACTIVE_SCOPE_PACKS", "active.packs must be a non-empty string array"))
    names = tuple(raw)
    if len(names) != len(set(names)):
        raise ValueError(refusal("ACTIVE_SCOPE_DUPLICATE", "active.packs"))
    if tuple(sorted(names)) != names:
        raise ValueError(refusal("ACTIVE_SCOPE_ORDER", "active.packs must be sorted"))
    return names


def select_packs(packs: Iterable[T], scope: str) -> list[T]:
    ordered = sorted(packs, key=lambda pack: pack.name)
    if scope == "all":
        return ordered
    if scope != "active":
        raise ValueError(refusal("MARKETPLACE_SCOPE", scope))
    wanted = set(active_pack_names())
    by_name = {pack.name: pack for pack in ordered}
    missing = sorted(wanted - set(by_name))
    if missing:
        raise ValueError(refusal("ACTIVE_SCOPE_PACK_MISSING", ",".join(missing)))
    return [by_name[name] for name in sorted(wanted)]


def snapshot(packs: Iterable[Named]) -> dict[str, object]:
    all_names = sorted(pack.name for pack in packs)
    active = list(active_pack_names())
    legacy = sorted(set(all_names) - set(active))
    return {
        "active_count": len(active),
        "active_packs": active,
        "legacy_count": len(legacy),
        "legacy_packs": legacy,
        "schema": "https://ggen.dev/marketplace/scope/v1",
        "total_count": len(all_names),
    }


def main() -> int:
    from marketplace import require_admitted

    try:
        payload = snapshot(require_admitted())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
