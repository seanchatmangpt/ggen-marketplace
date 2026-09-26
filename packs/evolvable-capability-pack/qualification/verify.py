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
  executed.
"""

from __future__ import annotations

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
}


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


def fixture_matrix() -> tuple[list[dict[str, object]], bool]:
    results: list[dict[str, object]] = []
    refused = False
    present = {CONSUMER} | set(FIXTURES.glob("*.ttl"))
    for path in sorted(present):
        key = path.relative_to(QUALIFICATION).as_posix()
        expected = FIXTURE_EXPECTATIONS.get(key)
        if expected is None:
            print(f"REFUSED:UNDECLARED_FIXTURE:{key}")
            refused = True
            continue
        if not path.is_file():
            print(f"REFUSED:MISSING_FIXTURE:{key}")
            refused = True
            continue
        try:
            observed = refusing_gates(load_graph(path))
        except MalformedInput as error:
            print(error)
            refused = True
            continue
        case_ok = set(observed) == set(expected)
        refused = refused or not case_ok
        results.append(
            {
                "fixture": key,
                "expected_refusals": sorted(expected),
                "observed_refusals": sorted(observed),
                "standing": "ALIVE" if case_ok else "REFUSED",
            }
        )
    for key in sorted(FIXTURE_EXPECTATIONS):
        if not (QUALIFICATION / key).is_file():
            print(f"REFUSED:MISSING_FIXTURE:{key}")
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
