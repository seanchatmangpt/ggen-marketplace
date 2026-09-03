import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class RevenueStructuralOptionContract(unittest.TestCase):
    def test_select_only_and_dual_revenue(self):
        ontology = (ROOT / "ontology.ttl").read_text()
        pack = (ROOT / "pack.toml").read_text()
        self.assertIn("RevenueFromCustomer", ontology)
        self.assertIn("RevenueForCustomer", ontology)
        self.assertIn('select = true', pack)
        self.assertIn('do = false', pack)
        self.assertNotIn('rsof:authority "DO"', ontology)

if __name__ == "__main__":
    unittest.main()
