#!/usr/bin/env python3
"""Machine-generated pack-consolidation court.

Implements the "Machine-generation requirement" of
docs/jira/v26.8.19/03-TICKET-consolidation-court-methodology.md: given a
proposed pack family (a kernel candidate + member packs), run pairwise
ontology/query/template correspondence over every member pair and emit a
single deterministic JSON report with a computed verdict.

Diff strategy
-------------
For each artifact class (ontology `.ttl`, gate `.rq`, template
`.tmpl`/`.tera`) this script diffs two packs as a *set of normalized lines*:

- If `rdflib` is importable, ontology files are parsed as real RDF graphs
  and diffed as sets of (s, p, o) triples (a real graph diff, not text).
  `rdflib` availability is recorded in the report's `diff_method` field.
- Otherwise (rdflib unavailable, or for `.rq`/template files which are not
  RDF), each file's non-blank, non-comment lines are stripped of leading/
  trailing whitespace and unioned per pack into one line-set; this is a
  documented, explicitly-labeled fallback ("line_normalized_triple_set" /
  "line_normalized_text_set"), not a claim of semantic equivalence.

For a pair (A, B): common = |A ∩ B|, only_a = |A - B|, only_b = |B - A|.
A pair "conflicts" on an artifact class when both only_a > 0 and only_b > 0
for that class (each pack has content the other lacks — i.e. neither is a
strict subset of the other, so there is no clean common-kernel/profile-
parameter split without loss). A pair with only_a == 0 or only_b == 0 (one
side is a subset of, or equal to, the other) is NOT a conflict — it is a
clean common/parameterized split.

Verdict rule (stated exactly, computed only from ontology conflicts per
the ticket's item 5 / acceptance criteria — query and template conflicts
are reported but do not change the verdict, since the ticket's `ADMITTED`
condition is phrased in terms of "every pair's ontology conflict-triple
count"):

    conflicting_pairs = pairs where ontology only_a > 0 AND only_b > 0
    - ADMITTED  if conflicting_pairs == 0 (no pair conflicts)
    - REFUTED   if conflicting_pairs == total_pairs (every pair conflicts)
    - PARTIAL   otherwise (some pairs conflict, some don't)

This script does NOT perform the ticket's item 4 (consumer-boundary
check against a real ggen runtime) — that requires an isolated consumer
project and the matching ggen binary, out of scope for a marketplace-only
script; the report's `consumer_boundary_check` field is explicitly `null`
with a note, so downstream family tickets cannot mistake this report for
full item-1-through-5 evidence.

Exit code: 0 on any successful run (verdict is data, not a process
failure). Nonzero only on real I/O/parse/config errors, each reported as
a `REFUSED:<code>:<detail>` line on stderr, matching scripts/marketplace.py's
`refusal()` convention.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("REFUSED:PYTHON_3_11_REQUIRED") from exc

rdflib: Any = None
try:
    import rdflib  # type: ignore

    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"
TEMPLATE_SUFFIXES = (".tmpl", ".tera")


def refusal(code: str, detail: str) -> str:
    return f"REFUSED:{code}:{detail}"


def ontology_files(directory: Path) -> tuple[Path, ...]:
    candidates: set[Path] = set()
    for path in directory.glob("*.ttl"):
        if path.is_file():
            candidates.add(path)
    nested = directory / "ontology"
    if nested.is_dir():
        for path in nested.rglob("*.ttl"):
            if path.is_file():
                candidates.add(path)
    return tuple(sorted(candidates, key=lambda p: p.relative_to(directory).as_posix()))


def gate_query_files(directory: Path) -> tuple[Path, ...]:
    gates_dir = directory / "gates"
    if not gates_dir.is_dir():
        return ()
    return tuple(
        sorted(
            (path for path in gates_dir.rglob("*.rq") if path.is_file()),
            key=lambda p: p.relative_to(directory).as_posix(),
        )
    )


def template_files(directory: Path) -> tuple[Path, ...]:
    templates_dir = directory / "templates"
    if not templates_dir.is_dir():
        return ()
    return tuple(
        sorted(
            (
                path
                for path in templates_dir.rglob("*")
                if path.is_file() and path.name.endswith(TEMPLATE_SUFFIXES)
            ),
            key=lambda p: p.relative_to(directory).as_posix(),
        )
    )


def pack_profile(directory: Path) -> str:
    if (directory / "ggen.toml").is_file():
        return "project"
    if template_files(directory):
        return "projection"
    return "semantic"


def normalized_line_set(paths: tuple[Path, ...]) -> frozenset[str]:
    """Fallback line-normalized set: non-blank, non-comment (#-prefixed),
    whitespace-stripped lines, unioned across all given files.
    """
    lines: set[str] = set()
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise SystemExit(refusal("FILE_UNREADABLE", f"{path}:{exc})")) from exc
        for raw in text.splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            lines.add(stripped)
    return frozenset(lines)


def rdf_triple_set(paths: tuple[Path, ...]) -> frozenset[tuple[str, str, str]]:
    triples: set[tuple[str, str, str]] = set()
    for path in paths:
        graph = rdflib.Graph()
        try:
            graph.parse(str(path), format="turtle")
        except (OSError, UnicodeError) as exc:
            raise SystemExit(refusal("FILE_UNREADABLE", f"{path}:{exc}")) from exc
        except Exception as exc:  # rdflib raises its own parse-error types
            raise SystemExit(refusal("TURTLE_PARSE_ERROR", f"{path}:{exc}")) from exc
        for s, p, o in graph:
            triples.add((str(s), str(p), str(o)))
    return frozenset(triples)


def diff_summary(set_a: frozenset, set_b: frozenset) -> dict[str, int]:
    common = set_a & set_b
    only_a = set_a - set_b
    only_b = set_b - set_a
    return {
        "common": len(common),
        "only_a": len(only_a),
        "only_b": len(only_b),
    }


@dataclass(frozen=True)
class Member:
    name: str
    path: Path
    profile: str
    ontologies: tuple[Path, ...]
    queries: tuple[Path, ...]
    templates: tuple[Path, ...]


def load_family(family_toml: Path) -> tuple[str, str, list[str]]:
    try:
        document = tomllib.loads(family_toml.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit(refusal("FAMILY_TOML_INVALID", f"{family_toml}:{exc}")) from exc
    table = document.get("family")
    if not isinstance(table, dict):
        raise SystemExit(refusal("FAMILY_TABLE_MISSING", str(family_toml)))
    name = table.get("name")
    kernel_candidate = table.get("kernel_candidate")
    members = table.get("members")
    if not isinstance(name, str) or not name.strip():
        raise SystemExit(refusal("FAMILY_NAME_MISSING", str(family_toml)))
    if not isinstance(kernel_candidate, str) or not kernel_candidate.strip():
        raise SystemExit(refusal("FAMILY_KERNEL_CANDIDATE_MISSING", str(family_toml)))
    if not isinstance(members, list) or not all(isinstance(m, str) for m in members) or not members:
        raise SystemExit(refusal("FAMILY_MEMBERS_MISSING", str(family_toml)))
    if kernel_candidate not in members:
        raise SystemExit(refusal("FAMILY_KERNEL_NOT_IN_MEMBERS", f"{family_toml}:{kernel_candidate}"))
    return name, kernel_candidate, members


def load_member(pack_name: str) -> Member:
    directory = PACKS / pack_name
    if not directory.is_dir():
        raise SystemExit(refusal("PACK_NOT_FOUND", pack_name))
    manifest = directory / "pack.toml"
    if not manifest.is_file():
        raise SystemExit(refusal("MANIFEST_MISSING", pack_name))
    return Member(
        name=pack_name,
        path=directory,
        profile=pack_profile(directory),
        ontologies=ontology_files(directory),
        queries=gate_query_files(directory),
        templates=template_files(directory),
    )


def pair_key(a: str, b: str) -> str:
    return f"{a}__{b}"


def run(family_toml: Path) -> dict[str, Any]:
    family_name, kernel_candidate, member_names = load_family(family_toml)
    members = {name: load_member(name) for name in member_names}

    diff_method_ontology = "rdflib_triple_set" if RDFLIB_AVAILABLE else "line_normalized_triple_set"

    pairs_report: dict[str, Any] = {}
    ontology_conflicts = 0
    total_pairs = 0

    for a_name, b_name in itertools.combinations(sorted(member_names), 2):
        total_pairs += 1
        a, b = members[a_name], members[b_name]

        if RDFLIB_AVAILABLE:
            onto_a = rdf_triple_set(a.ontologies)
            onto_b = rdf_triple_set(b.ontologies)
        else:
            onto_a = normalized_line_set(a.ontologies)
            onto_b = normalized_line_set(b.ontologies)
        onto_diff = diff_summary(onto_a, onto_b)
        onto_conflicts = onto_diff["only_a"] > 0 and onto_diff["only_b"] > 0
        if onto_conflicts:
            ontology_conflicts += 1

        query_a = normalized_line_set(a.queries)
        query_b = normalized_line_set(b.queries)
        query_diff = diff_summary(query_a, query_b)

        template_result: dict[str, Any] | None = None
        if a.profile == "projection" and b.profile == "projection":
            tmpl_a = normalized_line_set(a.templates)
            tmpl_b = normalized_line_set(b.templates)
            template_result = diff_summary(tmpl_a, tmpl_b)

        pairs_report[pair_key(a_name, b_name)] = {
            "pack_a": a_name,
            "pack_b": b_name,
            "ontology_diff": onto_diff,
            "ontology_conflict": onto_conflicts,
            "query_diff": query_diff,
            "template_diff": template_result,
            "template_diff_applicable": template_result is not None,
        }

    if ontology_conflicts == 0:
        verdict = "ADMITTED"
    elif ontology_conflicts == total_pairs:
        verdict = "REFUTED"
    else:
        verdict = "PARTIAL"

    report = {
        "family": family_name,
        "kernel_candidate": kernel_candidate,
        "members": sorted(member_names),
        "member_profiles": {name: members[name].profile for name in member_names},
        "diff_method": {
            "ontology": diff_method_ontology,
            "query": "line_normalized_text_set",
            "template": "line_normalized_text_set",
            "rdflib_available": RDFLIB_AVAILABLE,
        },
        "pairs": pairs_report,
        "total_pairs": total_pairs,
        "ontology_conflicting_pairs": ontology_conflicts,
        "verdict": verdict,
        "verdict_rule": (
            "ADMITTED if ontology_conflicting_pairs == 0; "
            "REFUTED if ontology_conflicting_pairs == total_pairs; "
            "PARTIAL otherwise. A pair conflicts on ontology when both "
            "packs have ontology triples/lines absent from the other "
            "(only_a > 0 and only_b > 0)."
        ),
        "consumer_boundary_check": None,
        "consumer_boundary_check_note": (
            "Item 4 of the ticket (generate from current pack vs. proposed "
            "kernel+profile split via a real ggen runtime against an "
            "isolated consumer project) is out of scope for this "
            "marketplace-only script and is not evaluated here."
        ),
        "schema": "https://ggen.dev/marketplace/consolidation-court/v1",
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family_toml", type=Path, help="Path to a family TOML file")
    args = parser.parse_args()

    family_toml: Path = args.family_toml
    if not family_toml.is_file():
        print(refusal("FAMILY_TOML_MISSING", str(family_toml)), file=sys.stderr)
        return 2

    report = run(family_toml)
    json.dump(report, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
