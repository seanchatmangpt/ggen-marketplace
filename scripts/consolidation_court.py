#!/usr/bin/env python3
"""Machine-generated pack-consolidation court.

Implements the "Machine-generation requirement" of
docs/jira/v26.8.19/03-TICKET-consolidation-court-methodology.md: given a
proposed pack family (a kernel candidate + member packs), run pairwise
ontology/query/template correspondence over every member pair and emit a
single deterministic JSON report with a computed verdict.

Diff strategy — v3, corrected from v2, corrected from v1
----------------------------------------------------------
v3 (2026-09-14) excludes GENERIC_VOCAB (standard RDF/RDFS/OWL/XSD
meta-vocabulary — Class, Property, domain, range, label, comment, and
similar terms every hand-authored ontology.ttl uses to declare its OWN
classes/properties) from the vocabulary_diff/vocabulary_shared
computation. v2 counted these as "shared vocabulary" between any two
packs, which is true of any two valid ontology.ttl files in this repo
and is not evidence of real domain overlap — confirmed by direct
measurement: a wasm4pm-algorithms-pack/wasm4pm-breed-provenance-pack
pair (PARTIAL under v2) showed vocabulary_diff.common=7, but 6 of those
7 terms were exactly Class/Property/comment/domain/label/range. Re-run
under v3 across all 9 families previously judged under v2 (see
docs/jira/v26.8.19/README.md's v2->v3 comparison table for the full
before/after). See GENERIC_VOCAB's own module comment for the exact
excluded-term list. Full v2 rationale (which v3 keeps) follows.
v1 of this script diffed ontologies as raw (s, p, o) triple sets and
declared a pair "conflicting" whenever neither side's triple set was a
subset of the other's. Run against every family in this marketplace, v1
returned REFUTED for 100% of 9 real families (0/205 pairs admitted) —
which turned out to be a methodology defect, not a real finding: every
pack in this repo mints its OWN RDF namespace (e.g.
`tcps-core-pack/ontology.ttl` uses `<.../tcps-core#>`, while
`tcps-cli-pack/ontology.ttl` uses `<.../tcps-cli#>` for the *same*
`Module`/`name`/`order`/`dependsOnModule` vocabulary), and every pack's
ontology also embeds pack-specific instance data (literal source-code
text, per-crate case names). Under raw triple equality, two packs that
obviously share a real schema get common=0 simply because their subject
IRIs live in different namespaces and their literals are pack-unique by
design — v1 could never distinguish "no shared kernel" from "every pack
correctly owns its own instance data," so it always returned the latter
as if it were the former.

v2 adds a second, primary diff dimension — **vocabulary correspondence**
— alongside the original **instance correspondence**:

- **Instance diff** (what v1 measured, kept and reported unchanged as
  `ontology_diff`/`ontology_conflict` per pair): raw (s, p, o) triple-set
  overlap via `rdflib` if importable, else a line-normalized fallback.
  Two packs' *instance data* differing is EXPECTED and is not evidence
  against a shared kernel — it is reported for transparency, not used to
  compute the verdict.
- **Vocabulary diff** (new, `vocabulary_diff`/`vocabulary_shared` per
  pair, `diff_method.ontology_vocabulary` records the method): the local
  name (URI fragment after `#`, or last path segment) of every
  `rdf:type` class and every predicate used, prefix/namespace-stripped
  before comparison. Two packs sharing real classes/predicates under
  different namespaces now correctly show `common > 0`. Only available
  when `rdflib` is importable (namespace-aware parsing is required); if
  unavailable, `vocabulary_diff` is `null` per pair and the verdict falls
  back to the old instance-only rule, explicitly flagged in
  `diff_method.vocabulary_fallback_to_instance_only`.

Verdict rule (stated exactly — vocabulary correspondence is now the
PRIMARY signal, since "does this family share a kernel ontology" is a
schema-level question, not an instance-data-equality question; query and
template diffs are still reported per pair but do not change the
verdict):

    shared_pairs = pairs where vocabulary common > 0 (share ≥1 real
                   class or predicate local name)
    - ADMITTED  if shared_pairs == total_pairs (every pair shares vocabulary)
    - REFUTED   if shared_pairs == 0 (no pair shares any vocabulary)
    - PARTIAL   otherwise

`instance_conflicting_pairs` (v1's old metric) is still computed and
reported for every pair, but no longer drives `verdict` — it is
informational context, since instance-level divergence is the normal,
expected shape of a kernel+profile split, not evidence against one.

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

# v3 fix (2026-09-14): standard RDF/RDFS/OWL/XSD vocabulary that appears in
# the TBox schema-declaration triples of virtually every hand-authored
# ontology.ttl in this repo (every pack that defines its OWN classes/
# properties uses rdfs:Class/rdf:Property/rdfs:domain/rdfs:range/
# rdfs:label/rdfs:comment to declare them). Confirmed by direct
# measurement: wasm4pm-algorithms-pack and wasm4pm-breed-provenance-pack
# (a PARTIAL-verdict pair in the v2 wasm4pm court report) showed
# vocabulary_diff.common=7, but rdf_vocabulary_set() on each pack directly
# shows 6 of those 7 terms are exactly this generic set (Class, Property,
# comment, domain, label, range) -- present because BOTH packs declare
# their own unrelated domain vocabulary using the same RDFS meta-
# vocabulary, not because they share real domain content. v2's
# "vocabulary_shared = common > 0" rule cannot distinguish "these two
# packs share a real kernel" from "these two packs both wrote valid
# Turtle," which is true of any two ontology.ttl files in this repo. v3
# excludes this set before computing vocabulary_diff/vocabulary_shared so
# the verdict tracks real domain-vocabulary correspondence, not RDF's own
# meta-vocabulary. Local names only (namespace-stripped, matching
# local_name()'s own convention) -- kept flat (not split by class/
# predicate kind) since a term like "type" can appear as either.
GENERIC_VOCAB: frozenset[str] = frozenset(
    {
        # RDFS/OWL/RDF class-level meta-vocabulary
        "Class", "Property", "ObjectProperty", "DatatypeProperty",
        "AnnotationProperty", "FunctionalProperty",
        "InverseFunctionalProperty", "TransitiveProperty",
        "SymmetricProperty", "ReflexiveProperty", "IrreflexiveProperty",
        "AsymmetricProperty", "Ontology", "Restriction", "NamedIndividual",
        "Class_", "Thing", "Nothing", "Datatype",
        # RDFS/OWL/RDF predicate-level meta-vocabulary
        "type", "domain", "range", "label", "comment", "subClassOf",
        "subPropertyOf", "seeAlso", "isDefinedBy", "versionInfo",
        "imports", "equivalentClass", "equivalentProperty",
        "disjointWith", "unionOf", "intersectionOf", "complementOf",
        "onProperty", "someValuesFrom", "allValuesFrom", "hasValue",
        "minCardinality", "maxCardinality", "cardinality",
        "minQualifiedCardinality", "maxQualifiedCardinality",
        "qualifiedCardinality", "onClass", "onDataRange", "first", "rest",
        "nil", "value", "inverseOf", "sameAs", "differentFrom",
        "allDifferent", "distinctMembers", "propertyChainAxiom",
        # XSD datatypes routinely used as rdfs:range values
        "string", "integer", "boolean", "dateTime", "date", "float",
        "double", "decimal", "anyURI", "nonNegativeInteger", "positiveInteger",
    }
)


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


def rdf_graphs(paths: tuple[Path, ...]) -> list:
    graphs = []
    for path in paths:
        graph = rdflib.Graph()
        try:
            graph.parse(str(path), format="turtle")
        except (OSError, UnicodeError) as exc:
            raise SystemExit(refusal("FILE_UNREADABLE", f"{path}:{exc}")) from exc
        except Exception as exc:  # rdflib raises its own parse-error types
            raise SystemExit(refusal("TURTLE_PARSE_ERROR", f"{path}:{exc}")) from exc
        graphs.append(graph)
    return graphs


def rdf_triple_set(paths: tuple[Path, ...]) -> frozenset[tuple[str, str, str]]:
    triples: set[tuple[str, str, str]] = set()
    for graph in rdf_graphs(paths):
        for s, p, o in graph:
            triples.add((str(s), str(p), str(o)))
    return frozenset(triples)


def local_name(iri: str) -> str:
    """URI fragment after `#`, or last `/`-segment — the namespace-stripped
    identifier two packs using different base namespaces for the same
    vocabulary term would still share (e.g. `.../tcps-core#Module` and
    `.../tcps-cli#Module` both yield `Module`).
    """
    if "#" in iri:
        return iri.rsplit("#", 1)[-1]
    return iri.rstrip("/").rsplit("/", 1)[-1]


def rdf_vocabulary_set(paths: tuple[Path, ...]) -> frozenset[tuple[str, str]]:
    """Namespace-stripped vocabulary used by these ontology files: every
    `("class", local_name)` for an `rdf:type` object, and every
    `("predicate", local_name)` for a predicate actually used (excluding
    `rdf:type` itself, tracked separately as class membership). This is
    the schema-level signal for "do these packs share a kernel
    vocabulary" — orthogonal to whether their instance data (subjects,
    literals) happens to be identical, which it normally won't be.

    v3: excludes GENERIC_VOCAB (standard RDF/RDFS/OWL/XSD terms every
    hand-authored ontology.ttl uses to declare its OWN classes/
    properties) — those terms being "shared" between two packs is a
    property of both packs writing valid Turtle, not of the packs
    sharing real domain vocabulary. See GENERIC_VOCAB's module comment
    for the measurement that motivated this.
    """
    RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    vocab: set[tuple[str, str]] = set()
    for graph in rdf_graphs(paths):
        for _s, p, o in graph:
            p_str = str(p)
            if p_str == RDF_TYPE:
                name = local_name(str(o))
                if name not in GENERIC_VOCAB:
                    vocab.add(("class", name))
            else:
                name = local_name(p_str)
                if name not in GENERIC_VOCAB:
                    vocab.add(("predicate", name))
    return frozenset(vocab)


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
    vocabulary_fallback_to_instance_only = not RDFLIB_AVAILABLE

    pairs_report: dict[str, Any] = {}
    instance_conflicts = 0
    vocabulary_shared_pairs = 0
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
            instance_conflicts += 1

        vocab_diff: dict[str, Any] | None = None
        vocab_shared = False
        if RDFLIB_AVAILABLE:
            vocab_a = rdf_vocabulary_set(a.ontologies)
            vocab_b = rdf_vocabulary_set(b.ontologies)
            vocab_diff = diff_summary(vocab_a, vocab_b)
            vocab_shared = vocab_diff["common"] > 0
        else:
            # No rdflib: cannot namespace-strip reliably. Fall back to the
            # instance-only signal (inverted: "not conflicting" stands in
            # for "shared"), explicitly flagged via
            # vocabulary_fallback_to_instance_only above.
            vocab_shared = not onto_conflicts
        if vocab_shared:
            vocabulary_shared_pairs += 1

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
            "vocabulary_diff": vocab_diff,
            "vocabulary_shared": vocab_shared,
            "query_diff": query_diff,
            "template_diff": template_result,
            "template_diff_applicable": template_result is not None,
        }

    if vocabulary_shared_pairs == total_pairs:
        verdict = "ADMITTED"
    elif vocabulary_shared_pairs == 0:
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
            "ontology_vocabulary": "namespace_stripped_class_predicate_set_v3_generic_excluded" if RDFLIB_AVAILABLE else None,
            "query": "line_normalized_text_set",
            "template": "line_normalized_text_set",
            "rdflib_available": RDFLIB_AVAILABLE,
            "vocabulary_fallback_to_instance_only": vocabulary_fallback_to_instance_only,
        },
        "pairs": pairs_report,
        "total_pairs": total_pairs,
        "instance_conflicting_pairs": instance_conflicts,
        "vocabulary_shared_pairs": vocabulary_shared_pairs,
        "verdict": verdict,
        "verdict_rule": (
            "v3: ADMITTED if vocabulary_shared_pairs == total_pairs (every "
            "pair shares >=1 real class/predicate local name across "
            "namespaces, EXCLUDING GENERIC_VOCAB -- standard RDF/RDFS/OWL/"
            "XSD meta-vocabulary every hand-authored ontology.ttl uses to "
            "declare its own classes/properties, which is not evidence of "
            "shared domain content); REFUTED if vocabulary_shared_pairs == "
            "0; PARTIAL otherwise. v2->v3 change (2026-09-14): v2 counted "
            "GENERIC_VOCAB terms (Class, Property, domain, range, label, "
            "comment, ...) as shared vocabulary, which is true of any two "
            "valid ontology.ttl files in this repo regardless of real "
            "domain overlap -- confirmed by direct measurement on a "
            "wasm4pm PARTIAL pair where 6 of 7 v2-counted 'shared' terms "
            "were exactly this generic set. instance_conflicting_pairs "
            "(raw triple-set overlap, v1's old metric) is reported per "
            "pair but does NOT drive verdict — instance data (subjects, "
            "literals) differing between packs is expected and is not "
            "evidence against a shared kernel."
        ),
        "consumer_boundary_check": None,
        "consumer_boundary_check_note": (
            "Item 4 of the ticket (generate from current pack vs. proposed "
            "kernel+profile split via a real ggen runtime against an "
            "isolated consumer project) is out of scope for this "
            "marketplace-only script and is not evaluated here."
        ),
        "schema": "https://ggen.dev/marketplace/consolidation-court/v2",
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
