import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ContractCourt(unittest.TestCase):
    def test_no_do_authority(self):
        text = (ROOT / "ontology.ttl").read_text(encoding="utf-8")
        self.assertNotIn('clm:authority "DO"', text)
        self.assertIn('clm:zeroUnreceiptedActuation true', text)

if __name__ == "__main__": unittest.main()
