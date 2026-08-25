import unittest
from pathlib import Path

class PropagationContractTests(unittest.TestCase):
    def test_contract_surface_exists(self):
        root=Path(__file__).parents[1]
        required=['pack.toml','ontology.ttl','ggen.toml','queries/10-qualified-source.rq','queries/20-lineage-frontier.rq','queries/30-clean-plan.rq','gates/01-qualified-source.rq','gates/02-no-force-no-do.rq']
        for rel in required:
            self.assertTrue((root/rel).exists(), rel)

    def test_no_force_or_actuation(self):
        text=(Path(__file__).parents[1]/'ontology.ttl').read_text()
        self.assertIn('forcePushAllowed false', text)
        self.assertIn('actuationPerformed false', text)
        self.assertIn('semanticDelta 0', text)

if __name__ == '__main__':
    unittest.main()
