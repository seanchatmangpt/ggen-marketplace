import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class R27OptionObservabilityCourt(unittest.TestCase):
    def test_sensor_surface_is_noncollapsed(self):
        queries = sorted((ROOT / "queries" / "r27-option-observability").glob("*.rq"))
        self.assertEqual(len(queries), 30)
        self.assertEqual(len({q.read_text() for q in queries}), 30)

    def test_live_ledger_has_eight_opportunities_from_five_seeds(self):
        rows = [json.loads(line) for line in (ROOT / "innovation-capital-r27-ledger.jsonl").read_text().splitlines() if line]
        run = rows[0]
        self.assertEqual(run["seed_observations"], 5)
        self.assertEqual(run["actionable_opportunities"], 8)
        self.assertEqual(run["E"], 1.6)
        self.assertEqual(len([r for r in rows if r["type"] == "edge"]), 8)

    def test_receipt_replays_exactly_and_has_no_do(self):
        receipt = json.loads((ROOT / "receipts" / "r27-option-observability-receipt.json").read_text())
        body = receipt["body"]
        raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(), receipt["sha256"])
        self.assertEqual(body["authority"], "OBSERVE|VERIFY")
        self.assertFalse(body["actuation_performed"])

    def test_fixture_uses_exact_pr_subjects(self):
        fixture = (ROOT / "fixtures" / "r27-option-observability-live-window.ttl").read_text()
        for sha in [
            "1d526362c60632229281d970a6bae1cba30e5754",
            "8586e4c1a93b2c6d1e21db2e5c8ebaf556a0700b",
            "7d8dc58dc82ef8886a2abbd4d7e5c92c6ea6c5ac",
            "25f9f4a32e15702e5bb286d396b06f8f5e33324b",
            "6996f43dcc771011afef4be37a4f352c1f5222ba",
        ]:
            self.assertIn(sha, fixture)

if __name__ == "__main__":
    unittest.main()
