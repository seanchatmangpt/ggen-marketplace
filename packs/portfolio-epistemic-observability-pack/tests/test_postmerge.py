import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[3]

class R34PostmergeCourt(unittest.TestCase):
    def test_receipt_identity(self):
        r=json.loads((ROOT/'receipts/measure/2026-08-25-r34-postmerge.json').read_text())
        self.assertEqual(r['qualified_head'],'30f56e4b3d30746e5cd559be6a0ee7fe86922c6b')
        self.assertEqual(r['merge_sha'],'6d0df7496946e371ab883d39678019e3eb0adbab')
        self.assertEqual(r['capability_standing'],'ALIVE')
        self.assertEqual(r['live_portfolio_rollout_standing'],'PARTIAL_ALIVE')
        self.assertFalse(r['consequential_do'])

if __name__=='__main__': unittest.main()
