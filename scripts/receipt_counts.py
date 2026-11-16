#!/usr/bin/env python3
"""Derive pack/template/test counts from disk; exit 1 if a root receipt disagrees.

A receipt opts in with one or more machine lines of the form

    Counts: packs=363 templates=1848 test_files=137 test_functions=1569
    Counts: test_aaif_enterprise_court.py=12 test_cdbr_isolation_court.py=4

Keys: packs (dirs under packs/ holding pack.toml), templates (packs/**/*.tmpl),
test_files (tests/test_*.py), test_functions (`def test_` lines in those files),
or a tests/ file name (its `def test_` count). Every root `_*_RECEIPT.md` must
carry at least one Counts line; a missing line, unknown key, or differing number
is a mismatch and the exit code is 1. Exit 2 on a missing repo layout.

Reproduce: python3 scripts/receipt_counts.py [--repo PATH] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

TEST_DEF = re.compile(r"^\s*(?:async\s+)?def test_", re.M)
COUNTS_LINE = re.compile(r"^Counts:\s*(.+?)\s*$", re.M)
PAIR = re.compile(r"([\w./-]+)=(\d+)")


def derive(repo: Path) -> dict[str, int]:
    packs_dir, tests_dir = repo / "packs", repo / "tests"
    if not packs_dir.is_dir() or not tests_dir.is_dir():
        raise SystemExit(f"receipt_counts: {repo} lacks packs/ or tests/")
    packs = sum(1 for p in packs_dir.iterdir() if (p / "pack.toml").is_file())
    templates = 0
    for _root, _dirs, files in os.walk(packs_dir):
        templates += sum(1 for f in files if f.endswith(".tmpl"))
    counts: dict[str, int] = {"packs": packs, "templates": templates}
    test_files = sorted(tests_dir.glob("test_*.py"))
    counts["test_files"] = len(test_files)
    total = 0
    for tf in test_files:
        n = len(TEST_DEF.findall(tf.read_text(encoding="utf-8", errors="replace")))
        counts[tf.name] = n
        total += n
    counts["test_functions"] = total
    return counts


def check(repo: Path) -> tuple[dict[str, int], list[str]]:
    disk = derive(repo)
    problems: list[str] = []
    receipts = sorted(repo.glob("_*_RECEIPT.md"))
    if not receipts:
        problems.append("no root _*_RECEIPT.md files found")
    for r in receipts:
        text = r.read_text(encoding="utf-8", errors="replace")
        lines = COUNTS_LINE.findall(text)
        if not lines:
            problems.append(f"{r.name}: no 'Counts:' line")
            continue
        for line in lines:
            for key, val in PAIR.findall(line):
                if key not in disk:
                    problems.append(f"{r.name}: unknown count key {key!r}")
                elif disk[key] != int(val):
                    problems.append(
                        f"{r.name}: {key} stated {val}, disk {disk[key]}"
                    )
    return disk, problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--json", action="store_true", help="print derived counts")
    args = ap.parse_args()
    disk, problems = check(Path(args.repo))
    if args.json:
        print(json.dumps(disk, indent=2, sort_keys=True))
    for p in problems:
        print(f"MISMATCH {p}", file=sys.stderr)
    if problems:
        return 1
    print(
        "receipt counts OK: packs={packs} templates={templates} "
        "test_files={test_files} test_functions={test_functions}".format(**disk)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
