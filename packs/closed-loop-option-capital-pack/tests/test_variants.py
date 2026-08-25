from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]

class VariantTest(unittest.TestCase):
    def test_distinct_policy_queries_exist(self):
        expected = {
            '40-thompson-proxy.rq','41-ucb.rq','42-reuse-adjusted.rq','43-cost-normalized.rq',
            '44-latency-normalized.rq','45-balanced.rq','46-missing-primitive.rq',
            '47-marketplace-supported.rq','48-frontier.rq'
        }
        actual = {p.name for p in (ROOT / 'queries').glob('*.rq')}
        self.assertEqual(expected, actual)

    def test_frontier_requires_reversibility(self):
        self.assertIn('cloc:reversible true', (ROOT / 'queries/48-frontier.rq').read_text())

if __name__ == '__main__':
    unittest.main()
