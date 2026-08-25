import hashlib
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUERY_DIR = ROOT / "queries" / "r29-sensor-yield"
LEDGER = ROOT / "innovation-capital-r29-ledger.jsonl"
RECEIPT = ROOT / "receipts" / "r29-sensor-yield-calibration-receipt.json"
ONTOLOGY = ROOT / "sensor-yield-calibration-r29.ttl"
FIXTURE = ROOT / "fixtures" / "r29-sensor-yield-calibration.ttl"


class SensorYieldCalibrationR29(unittest.TestCase):
    def test_query_surface_is_complete_and_noncollapsed(self):
        queries = sorted(QUERY_DIR.glob("*.rq"))
        self.assertEqual(len(queries), 30)
        bodies = [q.read_text() for q in queries]
        self.assertEqual(len(set(bodies)), 30)
        self.assertTrue(all("SELECT" in body and "ORDER BY" in body for body in bodies))

    def test_public_semantic_contract_and_grounded_fixture(self):
        ontology = ONTOLOGY.read_text()
        self.assertIn("http://www.w3.org/ns/prov#", ontology)
        self.assertIn("http://www.w3.org/ns/dqv#", ontology)
        self.assertIn("http://purl.org/dc/terms/", ontology)
        fixture = FIXTURE.read_text()
        for sensor in ("sensorA", "sensorB", "sensorC"):
            self.assertIn(sensor, fixture)
        self.assertIn('r29:actuationPerformed false', fixture)

    def test_ledger_preserves_exact_base_and_better_eyes_edges(self):
        rows = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
        self.assertTrue(any(r.get("subject") == "5710efa0fec47242f5709790803f0129f3b29999" for r in rows))
        opportunities = [r for r in rows if r.get("kind") == "opportunity"]
        self.assertGreaterEqual(len(opportunities), 5)
        self.assertTrue(all(r.get("sensor") == "r29-sensor-yield-calibration" for r in opportunities))

    def test_receipt_replays_and_carries_no_do(self):
        receipt = json.loads(RECEIPT.read_text())
        body = receipt["body"]
        raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(), receipt["sha256"])
        self.assertEqual(body["authority"], "OBSERVE|VERIFY")
        self.assertFalse(body["actuation_performed"])
        self.assertEqual(body["query_count"], 30)
        self.assertEqual(body["discovery_multiplier"], 1.0)

    def test_reference_corpus_contains_failure_pressure(self):
        fixture = FIXTURE.read_text()
        self.assertIn("r29:falsePositiveCount 2", fixture)
        self.assertIn("r29:falseNegativeCount 3", fixture)
        self.assertIn("r29:novelCount 0", fixture)
        self.assertIn('dcterms:status "STALE"', fixture)


if __name__ == "__main__":
    unittest.main()
