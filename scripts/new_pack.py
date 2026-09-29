#!/usr/bin/env python3
"""Scaffold a marketplace pack that passes `marketplace.py check <name>` on first run.

Usage: python3 scripts/new_pack.py <name> --profile semantic|projection|project [--dir packs]

Files come from scaffolds/pack-skeleton/{common,<profile>}/ with __NAME__, __PROFILE__ and
__IRI__ substituted. Existing directories and invalid names are refused (exit 2).
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKELETON = ROOT / "scaffolds" / "pack-skeleton"
PROFILES = ("semantic", "projection", "project")
NAME = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
IRI_BASE = "https://seanchatmangpt.github.io/packs/"


def refusal(code: str, detail: str) -> str:
    return f"REFUSED:{code}:{detail}"


def scaffold(name: str, profile: str, packs_dir: Path) -> Path:
    if not NAME.fullmatch(name):
        raise SystemExit(refusal("PACK_NAME_INVALID", f"{name!r} must be kebab-case [a-z][a-z0-9-]*"))
    if profile not in PROFILES:
        raise SystemExit(refusal("PROFILE_INVALID", profile))
    target = packs_dir / name
    if target.exists() or target.is_symlink():
        raise SystemExit(refusal("PACK_EXISTS", target.as_posix()))
    values = {"__NAME__": name, "__PROFILE__": profile, "__IRI__": f"{IRI_BASE}{name}"}
    sources = [SKELETON / "common"]
    if profile != "semantic":
        sources.append(SKELETON / profile)
    for source in sources:
        if not source.is_dir():
            raise SystemExit(refusal("SKELETON_MISSING", source.as_posix()))
    try:
        for source in sources:
            for path in sorted(p for p in source.rglob("*") if p.is_file() and p.name != ".gitkeep"):
                destination = target / path.relative_to(source)
                destination.parent.mkdir(parents=True, exist_ok=True)
                text = path.read_text(encoding="utf-8")
                for key, value in values.items():
                    text = text.replace(key, value)
                destination.write_text(text, encoding="utf-8")
    except BaseException:
        shutil.rmtree(target, ignore_errors=True)
        raise
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("--profile", choices=PROFILES, required=True)
    parser.add_argument("--dir", type=Path, default=ROOT / "packs")
    args = parser.parse_args()
    target = scaffold(args.name, args.profile, args.dir)
    print(f"scaffolded {args.profile} pack {target}")
    print(f"next: python3 scripts/marketplace.py check {args.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
