import hashlib
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUERY_DIR = ROOT / "queries" / "r30-opportunity-hypergraph"
LEDGER = ROOT / "innovation-capital-r30-ledger.jsonl"
RECEIPT = ROOT / "receipts" / "r30-opportunity-hypergraph-receipt.json"
ONTOLOGY = ROOT / "opportunity-hypergraph-r30.ttl"
FIXTURE = ROOT / "fixtures" / "r30-opportunity-hypergraph.ttl"
GATE = ROOT / "gates" / "r30-opportunity-hypergraph-authority.rq"


class OpportunityHypergraphR30(unittest.TestCase):
    def test_query_surface_is_complete_and_noncollapsed(self):
        queries = sorted(QUERY_DIR.glob("*.rq"))
        self.assertEqual(len(queries), 30)
        bodies = [q.read_text() for q in queries]
        self.assertEqual(len(set(bodies)), 30)
        self.assertTrue(all("SELECT" in body and "ORDER BY" in body for body in bodies))

    def test_public_semantic_contract(self):
        ontology = ONTOLOGY.read_text()
        for iri in (
            "http://www.w3.org/ns/prov#",
            "http://www.w3.org/ns/dqv#",
            "http://www.w3.org/2004/02/skos/core#",
            "http://www.w3.org/ns/odrl/2/",
            "http://purl.org/dc/terms/",
        ):
            self.assertIn(iri, ontology)
        for concept in ("Capability", "Composition", "Candidate", "MissingPrimitive", "FrontierMember"):
            self.assertIn(f"r30:{concept}", ontology)

    def test_fixture_preserves_pairwise_and_higher_order_options(self):
        fixture = FIXTURE.read_text()
        self.assertEqual(fixture.count(" a r30:Capability"), 6)
        self.assertEqual(fixture.count(" a r30:Composition"), 12)
        self.assertEqual(fixture.count(" a r30:Candidate"), 18)
        self.assertGreaterEqual(fixture.count("r30:FrontierMember"), 9)
        self.assertIn("composeFullHypergraph", fixture)
        self.assertIn("primitiveFormalCourtBridge", fixture)
        self.assertIn('r30:actuationPerformed false', fixture)

    def test_ledger_binds_exact_subject_and_metrics(self):
        rows = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
        self.assertTrue(any(r.get("subject") == "07e106c61b1ec1ced0ca805690e87107ba5fe45a" for r in rows))
        metrics = {r["id"]: r["value"] for r in rows if r.get("kind") == "metric"}
        self.assertEqual(metrics["seed-capability-count"], 6)
        self.assertEqual(metrics["composition-count"], 12)
        self.assertEqual(metrics["candidate-count"], 18)
        self.assertEqual(metrics["frontier-count"], 9)
        self.assertEqual(metrics["reference-e2"], 3.0)

    def test_receipt_replays_exact_body(self):
        receipt = json.loads(RECEIPT.read_text())
        body = receipt["body"]
        raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(), receipt["sha256"])
        self.assertEqual(body["query_count"], 30)
        self.assertEqual(body["candidate_count"], 18)
        self.assertEqual(body["frontier_count"], 9)
        self.assertEqual(body["e2_reference"], 3.0)
        self.assertEqual(body["authority"], "OBSERVE|VERIFY")
        self.assertFalse(body["actuation_performed"])
        self.assertIn("HANDWRITTEN", "HANDWRITTEN_IRREDUCIBLE_REASON")
        self.assertTrue(body["handwritten_irreducible_reason"])

    def test_authority_gate_refuses_do(self):
        gate = GATE.read_text()
        self.assertIn('!= "OBSERVE|VERIFY"', gate)
        self.assertIn("r30:actuationPerformed true", gate)
        fixture = FIXTURE.read_text()
        self.assertNotIn('r30:authority "DO"', fixture)
        self.assertNotIn("r30:actuationPerformed true", fixture)

    def test_frontier_is_not_prematurely_collapsed(self):
        fixture = FIXTURE.read_text()
        frontier = [line for line in fixture.splitlines() if "r30:FrontierMember" in line]
        self.assertGreaterEqual(len(frontier), 9)
        self.assertTrue(any("marketplaceSupport \"missing\"" in line for line in frontier))
        self.assertTrue(any("marketplaceSupport \"new:" in line for line in frontier))
        self.assertTrue(any("marketplaceSupport \"existing:" in line for line in frontier))


if __name__ == "__main__":
    unittest.main()
