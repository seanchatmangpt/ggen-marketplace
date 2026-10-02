import pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class CompositionContractCourt(unittest.TestCase):
    def test_composes_existing_factories_without_do(self):
        ontology = (ROOT / "ontology" / "r75-realization.ttl").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        query = (ROOT / "queries" / "ftr75_10-ready-realization-frontier.rq").read_text(encoding="utf-8")
        self.assertIn("forced-top25-standard-consumer-factory-pack", readme)
        self.assertIn("epistemic-sensor-factory-pack", readme)
        self.assertIn("r75:StructuralRealization", ontology)
        self.assertIn('compatibilityState "COMPATIBLE_READY"', query)
        self.assertIn("ORDER BY", query)
        self.assertIn("consequentialDo false", ontology)
        self.assertNotIn('authority "DO"', ontology)

if __name__ == "__main__":
    unittest.main()
