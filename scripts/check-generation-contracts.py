#!/usr/bin/env python3
"""Fail closed on deterministic ggen generation-contract defects across packs."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tomllib


def inspect_pack(pack_dir: Path) -> list[str]:
    manifest = pack_dir / "ggen.toml"
    if not manifest.is_file():
        return []

    data = tomllib.loads(manifest.read_text())
    rules = data.get("generation", {}).get("rules", [])
    failures: list[str] = []
    for rule in rules:
        name = rule.get("name", "<unnamed>")
        query_rel = (rule.get("query") or {}).get("file")
        template_rel = (rule.get("template") or {}).get("file")

        if query_rel:
            query = pack_dir / query_rel
            if not query.is_file():
                failures.append(f"{pack_dir.name}:{name}:missing query {query_rel}")
            else:
                text = query.read_text()
                if "SELECT" in text.upper() and "ORDER BY" not in text.upper():
                    failures.append(
                        f"{pack_dir.name}:{name}:SELECT query lacks ORDER BY: {query_rel}"
                    )

        if template_rel:
            template = pack_dir / template_rel
            if not template.is_file():
                failures.append(f"{pack_dir.name}:{name}:missing template {template_rel}")
            else:
                text = template.read_text()
                if "for row in rows" in text:
                    failures.append(
                        f"{pack_dir.name}:{name}:legacy rows context in {template_rel}; use admitted results"
                    )
    return failures


def inspect(root: Path) -> list[str]:
    packs = root / "packs"
    failures: list[str] = []
    for pack_dir in sorted(path for path in packs.iterdir() if path.is_dir()):
        failures.extend(inspect_pack(pack_dir))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    failures = inspect(args.root)
    if failures:
        print("REFUSED:GENERATION_CONTRACT_PREFLIGHT")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("GENERATION_CONTRACT_PREFLIGHT=ALIVE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
