import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class AuthorityPartitionCourt(unittest.TestCase):
    def test_no_candidate_has_do_authority(self):
        ontology = (ROOT / "ontology.ttl").read_text(encoding="utf-8")
        self.assertNotIn('cfr:authority "DO"', ontology)
        self.assertIn('cfr:zeroUnreceiptedActuation true', ontology)

if __name__ == "__main__":
    unittest.main()
