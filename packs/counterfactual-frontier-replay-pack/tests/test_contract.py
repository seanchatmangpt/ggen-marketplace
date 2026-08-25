import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class CounterfactualFrontierContractTest(unittest.TestCase):
    def test_authority_and_receipt_contract(self):
        ontology = (ROOT / "ontology.ttl").read_text(encoding="utf-8")
        self.assertIn('cfr:zeroUnreceiptedActuation true', ontology)
        self.assertIn('cfr:preserveParetoFrontier true', ontology)
        self.assertNotIn('cfr:authority "DO"', ontology)
        self.assertNotIn('cfr:actuationPerformed true', ontology)


if __name__ == "__main__":
    unittest.main()
