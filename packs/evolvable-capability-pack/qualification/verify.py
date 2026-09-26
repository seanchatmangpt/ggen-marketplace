#!/usr/bin/env python3
"""Executable anti-vacuity court for evolvable-capability-pack.

Two matrices are executed with a real SPARQL engine (rdflib) over the pack
ontology unioned with each input graph:

* the gate witness matrix: every ``gates/<stem>.rq`` must return zero rows on
  ``witnesses/pass/<stem>.ttl`` and at least one row on
  ``witnesses/fail/<stem>.ttl``;
* the fixture matrix: every ``qualification/fixtures/*.ttl`` and the ggen
  qualification consumer graph must be refused by exactly the gate set
  declared in ``FIXTURE_EXPECTATIONS`` (empty set = admitted by all gates).
  An undeclared fixture is refused, so a fixture cannot silently stop being
  executed. Each declared fixture also carries a ``DIGEST_BINDING_EXPECTATIONS``
  entry: every ``ecap:closureDigest`` must equal the digest recomputed from the
  closure's own member rows (court-507 A3: a format-valid digest naming
  members that were never frozen must be refused, so the frozen identity is
  bound to the frozen set, not merely shape-checked).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rdflib import Graph

PACK = Path(__file__).resolve().parents[1]
GATES = PACK / "gates"
PASS = PACK / "witnesses" / "pass"
FAIL = PACK / "witnesses" / "fail"
ONTOLOGY = PACK / "ontology.ttl"
QUALIFICATION = PACK / "qualification"
FIXTURES = QUALIFICATION / "fixtures"
CONSUMER = QUALIFICATION / "consumer.ttl"

# fixture path relative to qualification/ -> gate stems that must refuse it.
FIXTURE_EXPECTATIONS: dict[str, frozenset[str]] = {
    "consumer.ttl": frozenset(),
    "fixtures/positive.ttl": frozenset(),
    "fixtures/neg-promotion-without-pair.ttl": frozenset({"010_promotion_requires_paired_evidence"}),
    "fixtures/neg-released-without-evidence.ttl": frozenset({"020_released_requires_evidence"}),
    "fixtures/neg-candidate-in-closure.ttl": frozenset({"030_closure_released_only"}),
    # Court-507 adversarial corpus, permanent fixtures (A1-A6):
    "fixtures/neg-admitted-in-closure.ttl": frozenset({"030_closure_released_only"}),  # A1
    "fixtures/neg-duplicate-member-version.ttl": frozenset({"090_closure_member_version_required"}),  # A2
    "fixtures/neg-closure-digest-unbound.ttl": frozenset(),  # A3: refused by digest binding, not by a gate
    "fixtures/neg-untyped-closure-member.ttl": frozenset({"030_closure_released_only", "130_declared_lifecycle_state"}),  # A4
    "fixtures/pos-shared-impl-digest.ttl": frozenset(),  # A5: sharing an implementation is lawful; pinned
    "fixtures/neg-empty-member-version.ttl": frozenset({"090_closure_member_version_required"}),  # A6
}

# fixture path relative to qualification/ -> True when every declared
# ecap:closureDigest must equal the digest recomputed from member rows,
# False when the fixture is an unbound-digest defect that must be refused.
DIGEST_BINDING_EXPECTATIONS: dict[str, bool] = {
    "consumer.ttl": True,
    "fixtures/positive.ttl": True,
    "fixtures/neg-promotion-without-pair.ttl": True,
    "fixtures/neg-released-without-evidence.ttl": True,
    "fixtures/neg-candidate-in-closure.ttl": True,
    "fixtures/neg-admitted-in-closure.ttl": True,
    "fixtures/neg-duplicate-member-version.ttl": True,
    "fixtures/neg-closure-digest-unbound.ttl": False,
    "fixtures/neg-untyped-closure-member.ttl": True,
    "fixtures/pos-shared-impl-digest.ttl": True,
    "fixtures/neg-empty-member-version.ttl": True,
}

# Same member projection as templates/closure_summary.json.tmpl: the frozen
# identity is computed over exactly the rows the runtime projects.
MEMBER_ROWS_QUERY = """
PREFIX ecap: <https://seanchatmangpt.github.io/packs/evolvable-capability#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?closure ?declared ?capability ?version ?implementationDigest WHERE {
  ?closure a ecap:ExecutionClosure ;
           ecap:closureMember ?capability .
  OPTIONAL { ?closure ecap:closureDigest ?declared }
  OPTIONAL { ?capability dcterms:hasVersion ?version }
  OPTIONAL { ?capability ecap:implementationDigest ?implementationDigest }
} ORDER BY ?closure ?capability ?version ?implementationDigest
"""


def closure_digest(rows: list[tuple[str, str, str, str]]) -> str:
    """Recompute the frozen closure identity from its member rows.

    Canonical form: one ``closure|capability|version|implementationDigest\\n``
    line per member row (absent optionals become the empty string), sorted,
    SHA-256 over the concatenation, ``sha256:<hex>``. Deterministic pure
    function, so the court and any consumer recompute the same value.
    """
    canonical = "".join(sorted("|".join(row) + "\n" for row in rows))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def digest_binding_verdict(graph: Graph) -> tuple[str, list[dict[str, str]]]:
    """("bound" | "MISMATCH" | "n/a", per-closure detail) for a graph.

    "n/a": no closure declares a digest (gate 040 owns that refusal).
    "MISMATCH": some declared digest differs from the member-row digest.
    """
    observed: dict[str, list[tuple[str, str, str, str]]] = {}
    declared: dict[str, list[str]] = {}
    for row in graph.query(MEMBER_ROWS_QUERY):
        closure = str(row[0])
        observed.setdefault(closure, [])
        declared.setdefault(closure, [])
        if row[1] is not None:
            if str(row[1]) not in declared[closure]:
                declared[closure].append(str(row[1]))
        observed[closure].append(
            (
                closure,
                str(row[2]),
                "" if row[3] is None else str(row[3]),
                "" if row[4] is None else str(row[4]),
            )
        )
    detail: list[dict[str, str]] = []
    mismatch = False
    any_declared = False
    for closure in sorted(observed):
        expected = closure_digest(sorted(observed[closure]))
        for declared_digest in declared[closure]:
            any_declared = True
            ok = declared_digest == expected
            mismatch = mismatch or not ok
            detail.append(
                {
                    "closure": closure,
                    "declared": declared_digest,
                    "expected": expected,
                    "standing": "bound" if ok else "MISMATCH",
                }
            )
    if not any_declared:
        return "n/a", detail
    return ("MISMATCH" if mismatch else "bound"), detail


def gates() -> list[Path]:
    return sorted(GATES.glob("*.rq"))


class MalformedInput(ValueError):
    """An input graph could not be parsed; it is refused, never admitted."""


def load_graph(*inputs: Path | str, data_format: str = "turtle") -> Graph:
    """Pack ontology unioned with each input (a path or inline Turtle text).

    Any parser failure (rdflib raises BadSyntax, but also bare AssertionError
    or ValueError for some truncations) is normalized to MalformedInput so a
    caller can refuse it with a typed reason instead of crashing.
    """
    graph = Graph()
    graph.parse(ONTOLOGY, format="turtle")
    for item in inputs:
        label = item.name if isinstance(item, Path) else "<inline>"
        try:
            if isinstance(item, Path):
                graph.parse(item, format=data_format)
            else:
                graph.parse(data=item, format=data_format)
        except Exception as error:  # noqa: BLE001 - every parse failure is a refusal
            raise MalformedInput(f"REFUSED:MALFORMED_INPUT:{label}: {type(error).__name__}: {error}") from error
    return graph


def rows(gate: Path, graph: Graph) -> list[tuple[object, ...]]:
    return [tuple(row) for row in graph.query(gate.read_text(encoding="utf-8"))]


def execute(gate: Path, witness: Path) -> int:
    return len(rows(gate, load_graph(witness)))


def refusing_gates(graph: Graph) -> dict[str, int]:
    """Gate stem -> row count, for every gate that refuses the graph."""
    refused: dict[str, int] = {}
    for gate in gates():
        count = len(rows(gate, graph))
        if count:
            refused[gate.stem] = count
    return refused


def witness_matrix() -> tuple[list[dict[str, object]], bool]:
    results: list[dict[str, object]] = []
    refused = False
    for gate in gates():
        positive = PASS / f"{gate.stem}.ttl"
        negative = FAIL / f"{gate.stem}.ttl"
        if not positive.is_file() or not negative.is_file():
            print(f"REFUSED:MISSING_WITNESS:{gate.stem}")
            refused = True
            continue

        try:
            pass_rows = execute(gate, positive)
            fail_rows = execute(gate, negative)
        except MalformedInput as error:
            print(error)
            refused = True
            continue
        case_ok = pass_rows == 0 and fail_rows > 0
        refused = refused or not case_ok
        results.append(
            {
                "gate": gate.name,
                "pass_rows": pass_rows,
                "fail_rows": fail_rows,
                "standing": "ALIVE" if case_ok else "REFUSED",
            }
        )
    return results, refused


def fixture_matrix(
    qualification: Path = QUALIFICATION,
    expectations: dict[str, frozenset[str]] | None = None,
    digest_expectations: dict[str, bool] | None = None,
) -> tuple[list[dict[str, object]], bool]:
    """Run the fixture matrix over ``qualification`` (default: this pack's).

    Parameterized on the directory so the undeclared-fixture refusal can be
    exercised against a real on-disk copy with an extra file in it. Every
    declared fixture must also carry a ``digest_expectations`` entry (True:
    closure digests bound to member rows; False: an unbound-digest defect that
    must be observed), so a digest-binding check cannot be silently dropped
    from a fixture.
    """
    if expectations is None:
        expectations = FIXTURE_EXPECTATIONS
    if digest_expectations is None:
        digest_expectations = DIGEST_BINDING_EXPECTATIONS
    results: list[dict[str, object]] = []
    refused = False
    present = {qualification / CONSUMER.name} | set((qualification / FIXTURES.name).glob("*.ttl"))
    for path in sorted(present):
        key = path.relative_to(qualification).as_posix()
        expected = expectations.get(key)
        if expected is None:
            print(f"REFUSED:UNDECLARED_FIXTURE:{key}")
            refused = True
            continue
        expected_binding = digest_expectations.get(key)
        if expected_binding is None:
            print(f"REFUSED:UNDECLARED_DIGEST_EXPECTATION:{key}")
            refused = True
            continue
        if not path.is_file():
            print(f"REFUSED:MISSING_FIXTURE:{key}")
            refused = True
            continue
        try:
            graph = load_graph(path)
            observed = refusing_gates(graph)
            binding, binding_detail = digest_binding_verdict(graph)
        except MalformedInput as error:
            print(error)
            refused = True
            continue
        # "bound" expectation: "bound" or "n/a" (no declared digest; gate 040
        # owns that refusal) is lawful, "MISMATCH" is not. "MISMATCH"
        # expectation (A3): only a witnessed mismatch is lawful.
        binding_ok = (binding != "MISMATCH") if expected_binding else (binding == "MISMATCH")
        case_ok = set(observed) == set(expected) and binding_ok
        refused = refused or not case_ok
        results.append(
            {
                "fixture": key,
                "expected_refusals": sorted(expected),
                "observed_refusals": sorted(observed),
                "expected_digest_binding": "MISMATCH" if not expected_binding else "bound",
                "closure_digest_binding": binding,
                "closure_digest_detail": binding_detail,
                "standing": "ALIVE" if case_ok else "REFUSED",
            }
        )
    for key in sorted(expectations):
        if not (qualification / key).is_file():
            print(f"REFUSED:MISSING_FIXTURE:{key}")
            refused = True
    for key in sorted(digest_expectations):
        if key not in expectations:
            print(f"REFUSED:UNDECLARED_DIGEST_EXPECTATION:{key}")
            refused = True
    return results, refused


def main() -> int:
    cases, witness_refused = witness_matrix()
    fixtures, fixture_refused = fixture_matrix()
    refused = witness_refused or fixture_refused
    payload = {
        "pack": PACK.name,
        "case_count": len(cases),
        "cases": cases,
        "fixture_count": len(fixtures),
        "fixtures": fixtures,
        "standing": "REFUSED" if refused else "ALIVE",
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 2 if refused else 0


if __name__ == "__main__":
    raise SystemExit(main())
