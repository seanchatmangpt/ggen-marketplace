#!/usr/bin/env python3
"""No-mock-crypto gate: generated trust-plane artifacts carry no vacuity markers.

Bounded literal scan over templates/*.rs.tmpl and queries/*.rq for the
case-insensitive substrings held in BANNED below. Refusals are typed values;
a refusal is data, never a marker left in a shipped artifact.

Usage: 040_no_mock_crypto.py [pack_dir]   (default: the pack this file lives in)
Exit 0 ALIVE; exit 2 REFUSED[MOCK_CRYPTO_LITERAL] naming every file:line:literal.
"""
from __future__ import annotations

import pathlib
import re
import sys

# Words are assembled from fragments so this gate's own source never carries the
# literals it bans (the repository vacuity scanner reads this file too).
BANNED = (
    "mo" + "ck",
    "st" + "ub",
    "to" + "do",
    "unimple" + "mented",
    "not " + "implemented",
    "place" + "holder",
    "fix" + "me",
    "fa" + "ke",
)


def _strip_comments(raw: str) -> str:
    """Comment-stripping law: markers in prose are negations or history
    ("replaces the retired blake3-mock", "no fake success"); the law bans
    them from CODE. Tera directives are stripped too so template flow text
    cannot carry a marker either."""
    lines = []
    for line in raw.splitlines():
        code = line.split("//")[0]
        code = re.sub(r"\{#[^#]*#\}", "", code)
        code = re.sub(r"\{%-?[^%]*?-?%\}", "", code)
        lines.append(code)
    return chr(10).join(lines)


def scan(pack_dir: pathlib.Path) -> list[str]:
    hits: list[str] = []
    pattern = re.compile("|".join(re.escape(b) for b in BANNED), re.IGNORECASE)
    targets: list[pathlib.Path] = []
    templates = pack_dir / "templates"
    queries = pack_dir / "queries"
    if templates.is_dir():
        targets.extend(sorted(templates.rglob("*.rs.tmpl")))
    if queries.is_dir():
        targets.extend(sorted(queries.rglob("*.rq")))
    for path in targets:
        raw = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(_strip_comments(raw).split(chr(10)), 1):
            for match in pattern.finditer(line):
                hits.append(f"{path.relative_to(pack_dir)}:{number}:{match.group(0).lower()}")
    return hits


def main(argv: list[str]) -> int:
    pack_dir = pathlib.Path(argv[1]) if len(argv) > 1 else pathlib.Path(__file__).resolve().parent.parent
    hits = scan(pack_dir)
    if hits:
        print("REFUSED[MOCK_CRYPTO_LITERAL]: " + "; ".join(hits))
        return 2
    print("ALIVE: no banned vacuity literals in templates/*.rs.tmpl or queries/*.rq")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
