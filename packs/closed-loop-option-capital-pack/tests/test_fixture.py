from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]

class FixtureTest(unittest.TestCase):
    def test_fixture_binds_exact_subject_and_receipt(self):
        fixture = (ROOT / 'fixtures/realized-frontier.ttl').read_text()
        self.assertIn('cloc:exactSubject', fixture)
        self.assertIn('ggen-marketplace@1bb2340cad5425047f1a8fcdb5e58d969a6f41da', fixture)
        self.assertIn('cloc:receiptDigest', fixture)
        self.assertIn('cloc:missingPrimitive "consumer-replay-adapter"', fixture)

if __name__ == '__main__':
    unittest.main()
