from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ControlRealizationR25Court(unittest.TestCase):
    def test_measurement_surface_is_complete(self):
        queries = sorted((ROOT / "queries").glob("r25-*.rq"))
        self.assertEqual(len(queries), 40)
        names = {p.name for p in queries}
        for required in {
            "r25-13-observed-only-regret.rq",
            "r25-18-duplicate-evidence-root.rq",
            "r25-30-discovery-multiplier-e.rq",
            "r25-40-clean-realization-court.rq",
        }:
            self.assertIn(required, names)

    def test_public_semantics_bind_no_actuation(self):
        text = (ROOT / "control-realization-r25.ttl").read_text()
        self.assertIn("http://www.w3.org/ns/prov#", text)
        self.assertIn("http://www.w3.org/ns/dqv#", text)
        self.assertIn('frc:authority "OBSERVE|VERIFY"', text)
        self.assertIn("frc:actuationPerformed false", text)

    def test_innovation_capital_ledger_is_executable_shape(self):
        rows = [json.loads(line) for line in (ROOT / "control-realization-r25-ledger.jsonl").read_text().splitlines()]
        self.assertTrue(any(row["type"] == "sensor" for row in rows))
        self.assertGreaterEqual(sum(row["type"] == "opportunity" for row in rows), 3)

    def test_reference_corpus_contains_selected_and_observed_alternatives(self):
        text = (ROOT / "fixtures" / "control-realization-r25-reference.ttl").read_text()
        self.assertIn("frc:selected true", text)
        self.assertIn("frc:observedAlternative true", text)
        self.assertIn("frc:realizedDependencyRelief 0", text)

if __name__ == "__main__":
    unittest.main()
