#!/usr/bin/env python3
"""regen_solution_lock.py -- regenerate an AAIF solution lock from real inputs.

BO2 regenerated solution.json by hand; this tool makes the lock a projection
of the solution's actual inputs:

    python3 scripts/regen_solution_lock.py --solution solutions/enterprise-aaif
    python3 scripts/regen_solution_lock.py --solution solutions/enterprise-aaif --check

Both modes compute the exact folds the deployer's admission gate
(`deploy_aaif_solution.input_folds`, the same function the court exercises)
computes over the solution INPUTS:

- ``profile_sha256``  -- fingerprint_paths fold over every file in the solution
  dir except solution.json, dist/, and ggen runtime-state dirs;
- per-pack ``content_hash`` -- fingerprint_paths fold over each lock pack path.

Default mode writes the regenerated solution.json (schema preserved) and
prints the old->new diff. ``--check`` never writes: exit 0 when the lock is
fresh, exit 9 with ``REFUSED:LOCK_STALE`` plus the diff when it is not.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if sys.version_info < (3, 11):
    raise SystemExit("REFUSED:PYTHON_3_11_REQUIRED")

ROOT = Path(__file__).resolve().parent.parent
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from deploy_aaif_solution import input_folds  # noqa: E402

EMPTY_LOCK = {"packs": []}

LOCK_NAME = "solution.json"
LOCK_SCHEMA = "aaif-solution-lock/v1"


def load_lock(solution_dir: Path) -> dict[str, Any]:
    lock_path = solution_dir / LOCK_NAME
    if not lock_path.is_file():
        raise SystemExit(f"REFUSED:LOCK_MISSING {lock_path}")
    return json.loads(lock_path.read_text())


def pack_folds(solution_dir: Path, lock: dict[str, Any]) -> list[str]:
    """Per-pack input folds via the deployer's own input_folds.

    Called with an empty pack list so the same exclusion law the deployer
    applies to solution inputs (no solution.json, no dist/, no ggen
    runtime-state dirs) also governs the pack tree itself. Pack-local
    `dist/` and `.clap-noun-verb/` are gitignored runtime state -- folding
    them makes the lock drift on every manufacture, which is exactly the
    instability that killed the hand-regenerated lock.
    """
    folds: list[str] = []
    for pack in lock["packs"]:
        pack_path = (solution_dir / pack["path"]).resolve()
        if not pack_path.is_dir():
            raise SystemExit(f"REFUSED:PACK_MISSING {pack['name']} {pack_path}")
        fold, _ = input_folds(pack_path, EMPTY_LOCK)
        folds.append(fold)
    return folds


def recompute_lock(solution_dir: Path, lock: dict[str, Any]) -> dict[str, Any]:
    """Same schema, same pack order, digests recomputed from real inputs."""
    profile, _ = input_folds(solution_dir, lock)
    return {
        "schema": lock.get("schema", LOCK_SCHEMA),
        "profile_sha256": profile,
        "packs": [
            {**pack, "content_hash": f"sha256:{fold}"}
            for pack, fold in zip(lock["packs"], pack_folds(solution_dir, lock))
        ],
    }


def diff_locks(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    if old.get("profile_sha256") != new.get("profile_sha256"):
        lines.append(
            f"profile_sha256: {old.get('profile_sha256')} -> {new.get('profile_sha256')}"
        )
    old_packs = {p["name"]: p for p in old.get("packs", [])}
    for pack in new.get("packs", []):
        was = old_packs.get(pack["name"])
        old_hash = was["content_hash"] if was else "<absent>"
        if old_hash != pack["content_hash"]:
            lines.append(
                f"pack {pack['name']}: {old_hash} -> {pack['content_hash']}"
            )
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "usage").splitlines()[0])
    parser.add_argument("--solution", required=True, type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify only: exit 0 fresh, exit 9 REFUSED:LOCK_STALE (no write)",
    )
    args = parser.parse_args(argv)

    solution_dir = args.solution.resolve()
    lock = load_lock(solution_dir)
    fresh = recompute_lock(solution_dir, lock)
    lines = diff_locks(lock, fresh)

    if args.check:
        if lines:
            print("REFUSED:LOCK_STALE")
            for line in lines:
                print(line)
            return 9
        print(f"OK lock fresh: {solution_dir / LOCK_NAME}")
        return 0

    if lines:
        for line in lines:
            print(line)
    else:
        print("no changes")
    lock_path = solution_dir / LOCK_NAME
    lock_path.write_text(json.dumps(fresh, indent=2) + "\n")
    print(f"wrote {lock_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
