from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ContractCourt(unittest.TestCase):
    def test_source_contract_is_select_only(self):
        ontology = (ROOT / "ontology.ttl").read_text()
        gate = (ROOT / "gates/02-select-only-authority.rq").read_text()
        self.assertIn("rch:SELECT", ontology)
        self.assertIn('rch:authority "DO"', gate)
        self.assertIn("rch:actuationPerformed true", gate)

    def test_generation_contract_has_no_generated_source_dependency(self):
        contract = (ROOT / "ggen.toml").read_text()
        self.assertIn('query = { file = "queries/80-calibrated-frontier.rq" }', contract)
        self.assertNotIn('source = "generated/', contract)


if __name__ == "__main__":
    unittest.main()
