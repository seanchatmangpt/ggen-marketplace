import unittest
from pathlib import Path

class MultiCellContractTests(unittest.TestCase):
    def test_contract_surface_exists(self):
        root=Path(__file__).parents[1]
        required=['pack.toml','ontology.ttl','ggen.toml','queries/10-admitted-cells.rq','queries/20-compatible-frontier.rq','queries/30-clean-frontier.rq','gates/01-exact-subject.rq','gates/02-no-ambient-do.rq']
        for rel in required:
            self.assertTrue((root/rel).exists(), rel)

    def test_authority_is_non_actuating(self):
        text=(Path(__file__).parents[1]/'ontology.ttl').read_text()
        self.assertIn('actuationPerformed false', text)
        self.assertIn('authority "SELECT|CONSTRUCT|VERIFY"', text)

if __name__ == '__main__':
    unittest.main()
