import hashlib
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "r29-postmerge-capital-receipt.json"
FIXTURE = ROOT / "fixtures" / "r29-postmerge-capital.ttl"
LEDGER = ROOT / "innovation-capital-r29-postmerge-ledger.jsonl"
QUERIES = ROOT / "queries" / "r29-postmerge"

class R29PostmergeCapital(unittest.TestCase):
    def test_receipt_replays_exactly(self):
        receipt = json.loads(RECEIPT.read_text())
        raw = json.dumps(receipt["body"], sort_keys=True, separators=(",", ":"))
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(), receipt["sha256"])
        self.assertEqual(receipt["body"]["qualified_head"], "f042acf00b6ec4c269ddeabd00f0f6e6123864b9")
        self.assertEqual(receipt["body"]["merge_sha"], "07e106c61b1ec1ced0ca805690e87107ba5fe45a")
        self.assertEqual(receipt["body"]["authority"], "OBSERVE|VERIFY")
        self.assertFalse(receipt["body"]["actuation_performed"])

    def test_fixture_binds_containment_and_open_frontier(self):
        text = FIXTURE.read_text()
        self.assertIn("f042acf00b6ec4c269ddeabd00f0f6e6123864b9", text)
        self.assertIn("07e106c61b1ec1ced0ca805690e87107ba5fe45a", text)
        self.assertEqual(text.count('dcterms:status "OPEN"'), 3)
        self.assertIn('dcterms:status "ALIVE"', text)
        self.assertIn('dcterms:status "CONTAINED"', text)

    def test_ledger_is_append_only_capital_graph(self):
        rows = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
        self.assertTrue(any(row.get("kind") == "qualification" and row.get("standing") == "ALIVE" for row in rows))
        self.assertTrue(any(row.get("kind") == "merge-containment" and row.get("ahead_by") == 1 and row.get("behind_by") == 0 for row in rows))
        self.assertEqual(sum(row.get("kind") == "opportunity" for row in rows), 3)

    def test_postmerge_queries_are_noncollapsed(self):
        queries = sorted(QUERIES.glob("*.rq"))
        self.assertEqual(len(queries), 3)
        bodies = [q.read_text() for q in queries]
        self.assertEqual(len(set(bodies)), 3)
        self.assertTrue(all("SELECT" in body and "ORDER BY" in body for body in bodies))

if __name__ == "__main__":
    unittest.main()
