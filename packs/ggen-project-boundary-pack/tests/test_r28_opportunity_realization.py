import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class R28OpportunityRealizationCourt(unittest.TestCase):
    def test_query_surface(self):
        queries = sorted((ROOT / "queries" / "r28-opportunity-realization").glob("*.rq"))
        self.assertEqual(len(queries), 8)
        self.assertEqual(len({q.read_text() for q in queries}), 8)

    def test_merge_and_capability_exact_identities(self):
        fixture = (ROOT / "fixtures" / "r28-opportunity-realization.ttl").read_text()
        for sha in [
            "304314c865ab3fe42404ad816d26f3871ab72026",
            "28aeda79d3654f81ced23b1d728e7129ddca761e",
            "92868812558dbbc597c2650fdb0f97cdcb8637f0",
            "df9b0d92b4d78360577c8b127e159b1827c79b59",
        ]:
            self.assertIn(sha, fixture)

    def test_ledger_closes_one_of_eight_opportunities(self):
        rows = [json.loads(line) for line in (ROOT / "innovation-capital-r28-ledger.jsonl").read_text().splitlines() if line]
        metric = next(r for r in rows if r.get("name") == "opportunity_closure_rate")
        self.assertEqual(metric["realized"], 1)
        self.assertEqual(metric["actionable"], 8)
        self.assertEqual(metric["value"], 0.125)
        self.assertEqual(len([r for r in rows if r["type"] == "opportunity"]), 3)

    def test_receipt_replay_and_zero_do(self):
        receipt = json.loads((ROOT / "receipts" / "r28-opportunity-realization-receipt.json").read_text())
        raw = json.dumps(receipt["body"], sort_keys=True, separators=(",", ":"))
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(), receipt["sha256"])
        self.assertEqual(receipt["body"]["authority"], "OBSERVE|VERIFY")
        self.assertFalse(receipt["body"]["actuation_performed"])

if __name__ == "__main__":
    unittest.main()
