"""Lane-1 tests for packs/domain-capability-pack (anti-vacuity court + pinned IDs + namespace alignment)."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

PACK = Path(__file__).parents[1] / "packs" / "domain-capability-pack"
VERIFY = PACK / "qualification" / "verify.py"
ONTOLOGY = PACK / "ontology.ttl"

NEW_GATES = [
    "040_required_contract_fields.rq",
    "050_capability_requires_realization.rq",
    "060_realization_requires_qualification.rq",
    "070_availability_requires_authority.rq",
    "080_no_do_authority.rq",
    "090_runtime_only_frozen.rq",
]

PINNED_IDS = ["Domain.Action.Invoke", "Domain.Query.Read", "Domain.Change.Apply"]

LEGACY_NAMESPACE = "http://seanchatmangpt.github.io/packs/domain-capability#"
PINNED_NAMESPACE = "https://ggen.dev/ontology/domain-capability#"


class DomainCapabilityPackTests(unittest.TestCase):
    def test_anti_vacuity_court_admits(self) -> None:
        """9 gates clean on the positive fixture; 6 negative fixtures witnessed firing."""
        result = subprocess.run(
            [sys.executable, str(VERIFY)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"verify.py refused: rc={result.returncode} out={result.stdout} err={result.stderr}",
        )
        self.assertIn("ADMITTED", result.stdout)

    def test_every_new_gate_has_a_witnessed_firing(self) -> None:
        """A gate with no witnessed refusal carries no bits: each new gate must be
        the named expectation of some negative fixture in verify.py."""
        expectations = VERIFY.read_text(encoding="utf-8")
        for gate in NEW_GATES:
            self.assertIn(gate, expectations, f"gate {gate} has no negative-fixture expectation")

    def test_pinned_capability_ids_are_admitted(self) -> None:
        """The three pinned dotted IDs exist as dcterms:identifier AND rdfs:label."""
        from rdflib import Graph

        graph = Graph()
        graph.parse(ONTOLOGY, format="turtle")
        query_template = """
            PREFIX dcp: <https://ggen.dev/ontology/domain-capability#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?cap WHERE {
                ?cap a dcp:DomainCapability ;
                    dcterms:identifier ?id ;
                    rdfs:label ?id .
                FILTER (STR(?id) = "%s")
            }
        """
        for pinned in PINNED_IDS:
            # PINNED_IDS are fixed literals in this file (no injection surface).
            rows = list(graph.query(query_template % pinned))
            self.assertEqual(len(rows), 1, f"pinned id {pinned!r}: expected exactly 1 capability")

    def test_namespace_alignment_recorded(self) -> None:
        """The v0.1.0 legacy namespace is republished at the pinned IRI with explicit
        per-term dcterms:isReplacedBy records (conservation: no silent rename)."""
        from rdflib import Graph

        graph = Graph()
        graph.parse(ONTOLOGY, format="turtle")
        legacy = Graph()
        for subject, predicate, obj in graph:
            if str(subject).startswith(LEGACY_NAMESPACE):
                legacy.add((subject, predicate, obj))
        replaced_by = list(
            legacy.triples(
                (
                    None,
                    __import__("rdflib").URIRef("http://purl.org/dc/terms/isReplacedBy"),
                    None,
                )
            )
        )
        self.assertGreaterEqual(
            len(replaced_by),
            15,
            f"expected >=15 legacy terms mapped via dcterms:isReplacedBy, found {len(replaced_by)}",
        )
        for _, _, target in replaced_by:
            self.assertTrue(str(target).startswith(PINNED_NAMESPACE), f"bad alignment target {target}")


if __name__ == "__main__":
    unittest.main()
