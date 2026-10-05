"""GROUP_CONCAT determinism court (marketplace-side law).

Why this court exists
=====================

The ggen engine refuses SELECT queries without ORDER BY (manifest lint
E0011/E0013) but does NOT enforce determinism of the GROUP_CONCAT fold itself:
SPARQL leaves the row order *within* a group implementation-defined, so an
aggregate over an unordered pattern can concatenate in a different order across
engines, engine versions, or blank-node labelings. Two syncs of the same pack
could then project byte-different templates from identical RDF. The engine
deliberately leaves this as marketplace-side law (plan lane 2: "GROUP_CONCAT
determinism is NOT engine-enforced -- must remain a marketplace-side court
rule"), so this file is the enforcement point.

The house idiom (exemplar: packs/affidavit-trust-plane-pack/queries/keys.rq)
is an *ordered inner sub-SELECT feeding the aggregate*:

    {
      SELECT (GROUP_CONCAT(?spec ; separator="@@") AS ?algs)
      WHERE {
        {
          SELECT ?spec WHERE { ... } ORDER BY ?name
        }
      }
    }

Heuristics (documented per the lane contract)
=============================================

The court is textual, not a full SPARQL parse. For every ``*.rq`` under
``packs/*/queries/`` and ``packs/*/gates/`` (plus pack ``families/*/``):

1. Comment lines (``#`` to end-of-line, respecting quoted strings) are
   stripped first, so a prose mention of "GROUP_CONCAT" in a header comment is
   neither a vacuous pass nor a false fail.
2. An *aggregate occurrence* is the token ``GROUP_CONCAT`` immediately
   followed by ``(`` (balanced-paren scan to the matching close).
3. separator check: the balanced GROUP_CONCAT(...) call text must contain
   ``separator=`` (case-insensitive). SPARQL's default separator is a single
   space; an explicit ``separator=`` pins the fold so templates can
   ``split(pat=)`` on it deterministically.
4. Ordered-sub-SELECT check: take the innermost ``{ ... }`` brace block that
   encloses the occurrence and require that block to contain both a ``SELECT``
   keyword and ``ORDER BY``. In the house idiom the aggregate's WHERE group
   wraps the ordered sub-SELECT, so the enclosing block carries both tokens.
   This is a heuristic, not a parse: an ORDER BY anywhere in the same group
   satisfies it. It cannot verify that the ORDER BY sorts the *aggregated*
   variable -- reviewers upgrading a query must keep that property by hand.

A file is a VIOLATOR if any of its aggregate occurrences lacks separator= or
lacks an ordered enclosing sub-SELECT. The failure message names the file, the
occurrence index, and which property is missing.

Non-vacuity
===========

``KNOWN_VIOLATORS`` entries are xfail(strict=True) per file: a listed file
that becomes compliant fails the court until the list is pruned, and a
compliant file that regresses fails hard. ``test_known_violator_list_is_current``
re-derives the classification so the list cannot silently rot.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"

# relative path -> {occurrence index -> set of missing properties}
# occurrence index = index of the GROUP_CONCAT( token in comment-stripped text.
# All 16 former violators repaired (v26.10.5): every GROUP_CONCAT now folds
# over an ordered inner sub-SELECT. The list is kept as the empty-map schema
# so new violators still surface via test_known_violator_list_is_current.
KNOWN_VIOLATORS: dict[str, dict[int, set[str]]] = {}


def strip_comments(text: str) -> str:
    """Blank out '#' comment tails, respecting quoted strings, preserving offsets."""
    out = list(text)
    in_quote = False
    quote_char = ""
    i = 0
    while i < len(text):
        c = text[i]
        if in_quote:
            if c == "\\" and i + 1 < len(text):
                out[i + 1] = " "
                i += 2
                continue
            if c == quote_char:
                in_quote = False
            i += 1
            continue
        if c in ('"', "'"):
            in_quote = True
            quote_char = c
            i += 1
        elif c == "#":
            j = i
            while j < len(text) and text[j] != "\n":
                out[j] = " "
                j += 1
            i = j
        else:
            i += 1
    return "".join(out)


def brace_blocks(clean: str) -> list[tuple[int, int]]:
    blocks: list[tuple[int, int]] = []
    stack: list[int] = []
    for i, c in enumerate(clean):
        if c == "{":
            stack.append(i)
        elif c == "}" and stack:
            blocks.append((stack.pop(), i))
    return blocks


def balanced_call(clean: str, open_paren: int) -> str:
    depth = 0
    for i in range(open_paren, len(clean)):
        if clean[i] == "(":
            depth += 1
        elif clean[i] == ")":
            depth -= 1
            if depth == 0:
                return clean[open_paren + 1 : i]
    return clean[open_paren + 1 :]


def innermost_enclosing(blocks: list[tuple[int, int]], pos: int) -> tuple[int, int] | None:
    best: tuple[int, int] | None = None
    for s, e in blocks:
        if s < pos < e and (best is None or s > best[0]):
            best = (s, e)
    return best


def scan_file(path: Path) -> dict[int, set[str]]:
    """Map occurrence index -> set of missing properties (empty set = compliant)."""
    clean = strip_comments(path.read_text(encoding="utf-8"))
    blocks = brace_blocks(clean)
    problems: dict[int, set[str]] = {}
    idx = 0
    for m in re.finditer(r"GROUP_CONCAT\s*\(", clean, re.IGNORECASE):
        call = balanced_call(clean, m.end() - 1)
        missing: set[str] = set()
        if not re.search(r"separator\s*=", call, re.IGNORECASE):
            missing.add("separator")
        blk = innermost_enclosing(blocks, m.start())
        seg = clean[blk[0] : blk[1]] if blk else ""
        if not (
            re.search(r"\bSELECT\b", seg, re.IGNORECASE)
            and re.search(r"\bORDER\s+BY\b", seg, re.IGNORECASE)
        ):
            missing.add("ordered_sub_select")
        problems[idx] = missing
        idx += 1
    return problems


def discover() -> list[Path]:
    files: set[Path] = set()
    for pattern in ("queries/*.rq", "gates/*.rq"):
        files.update(PACKS.glob(f"*/{pattern}"))
        files.update(PACKS.glob(f"*/families/*/{pattern}"))
    return sorted(
        p
        for p in files
        if re.search(
            r"GROUP_CONCAT\s*\(", strip_comments(p.read_text(encoding="utf-8")), re.IGNORECASE
        )
    )


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def actual_violations() -> dict[str, dict[int, set[str]]]:
    all_files = {rel(p): {i: m for i, m in scan_file(p).items() if m} for p in discover()}
    return {r: v for r, v in all_files.items() if v}


@pytest.mark.xfail(
    reason="GROUP_CONCAT determinism law violations (KNOWN_VIOLATORS)", strict=True
)
@pytest.mark.parametrize("path", sorted(KNOWN_VIOLATORS))
def test_known_violator_file(path: str) -> None:
    """xfail(strict): while the file still violates, this fails => xfailed.
    Once the file is repaired, this passes => XPASS(strict) fails the court,
    forcing removal of the entry from KNOWN_VIOLATORS."""
    observed = {i: m for i, m in scan_file(ROOT / path).items() if m}
    assert not observed, f"{path}: still violating: {observed}"


@pytest.mark.parametrize(
    "path", [p for p in discover() if rel(p) not in KNOWN_VIOLATORS], ids=rel
)
def test_query_file_group_concat_determinism(path: Path) -> None:
    missing = {i: m for i, m in scan_file(path).items() if m}
    assert not missing, (
        f"{rel(path)}: GROUP_CONCAT determinism law violated at occurrence(s) "
        + "; ".join(f"#{i} missing {sorted(m)}" for i, m in sorted(missing.items()))
    )


def test_known_violator_list_is_current() -> None:
    """Non-vacuity: every listed violator still exists and still violates in
    exactly the listed way; every discovered violator is listed."""
    assert actual_violations() == {
        r: v for r, v in KNOWN_VIOLATORS.items() if v
    }
