import unittest
from pathlib import Path

class FanoutContractTests(unittest.TestCase):
    def test_contract_surface_exists(self):
        root=Path(__file__).parents[1]
        required=['pack.toml','ontology.ttl','ggen.toml','queries/10-qualified-assets.rq','queries/20-consumer-frontier.rq','queries/30-high-y-frontier.rq','gates/01-qualified-factory.rq','gates/02-no-ambient-do.rq']
        for rel in required:
            self.assertTrue((root/rel).exists(), rel)

    def test_y_and_authority_are_bounded(self):
        text=(Path(__file__).parents[1]/'ontology.ttl').read_text()
        self.assertIn('expectedQualifiedActions', text)
        self.assertIn('investmentUnits', text)
        self.assertIn('actuationPerformed false', text)

if __name__ == '__main__':
    unittest.main()
