from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EvidenceCourt(unittest.TestCase):
    def test_fixture_has_exact_subject_and_digest(self):
        fixture = (ROOT / "fixtures/realization.ttl").read_text()
        self.assertIn("rch:exactSubject", fixture)
        digest = re.search(r'rch:receiptDigest "([0-9a-f]+)"', fixture)
        self.assertIsNotNone(digest)
        self.assertEqual(64, len(digest.group(1)))

    def test_fixture_has_no_actuation(self):
        fixture = (ROOT / "fixtures/realization.ttl").read_text()
        self.assertIn("rch:actuationPerformed false", fixture)
        self.assertNotIn("rch:actuationPerformed true", fixture)


if __name__ == "__main__":
    unittest.main()
