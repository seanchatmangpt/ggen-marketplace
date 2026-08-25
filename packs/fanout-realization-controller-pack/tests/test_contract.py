import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class FanoutRealizationContractTest(unittest.TestCase):
    def test_authority_and_receipt_contract(self):
        ontology = (ROOT / "ontology.ttl").read_text(encoding="utf-8")
        self.assertIn('frc:actuationPerformed false', ontology)
        self.assertIn('frc:requiresReceipt true', ontology)
        self.assertIn('frc:requiresExactSubject true', ontology)
        self.assertNotIn('frc:authority "DO"', ontology)

    def test_complete_control_surface(self):
        queries = sorted((ROOT / "queries").glob("*.rq"))
        self.assertEqual(len(queries), 8)
        self.assertTrue((ROOT / "gates/01-exact-current-evidence.rq").is_file())
        self.assertTrue((ROOT / "gates/02-no-ambient-do.rq").is_file())

    def test_deterministic_generation_contract(self):
        config = (ROOT / "ggen.toml").read_text(encoding="utf-8")
        self.assertEqual(config.count('query = { file = "queries/80-clean-control-frontier.rq" }'), 2)
        frontier = (ROOT / "queries/80-clean-control-frontier.rq").read_text(encoding="utf-8")
        self.assertIn("ORDER BY", frontier)


if __name__ == "__main__":
    unittest.main()
