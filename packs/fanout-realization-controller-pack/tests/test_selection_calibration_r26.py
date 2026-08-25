import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class SelectionCalibrationR26Court(unittest.TestCase):
    def test_public_semantics_bind_calibration_law(self):
        ontology = (ROOT / "ontology.ttl").read_text(encoding="utf-8")
        self.assertIn("frc:SelectionCalibrationRun a prov:Activity", ontology)
        self.assertIn("frc:FalseNegativeSelectionMetric a dqv:Metric", ontology)
        self.assertIn("frc:CounterfactualCoverageMetric a dqv:Metric", ontology)
        self.assertIn("frc:EvidenceRootDiversityMetric a dqv:Metric", ontology)
        self.assertIn("frc:ReliefRoiMetric a dqv:Metric", ontology)
        self.assertIn("frc:PolicyDriftMetric a dqv:Metric", ontology)
        self.assertIn("frc:r26SelectionCalibrationLaw", ontology)
        self.assertIn("frc:requiresIndependentEvidenceRoots true", ontology)
        self.assertNotIn('frc:authority "DO"', ontology)

    def test_calibration_sensor_surface_is_complete_and_ordered(self):
        sensors = sorted((ROOT / "queries").glob("r26-*.rq"))
        self.assertEqual(len(sensors), 48)
        names = {sensor.name for sensor in sensors}
        for required in {
            "r26-01-confusion-matrix.rq",
            "r26-01-selected-positive-value-rate.rq",
            "r26-30-clean-calibration-frontier.rq",
            "r26-31-calibration-capital-yield.rq",
            "r26-32-root-discounted-yield.rq",
            "r26-33-latency-normalized-relief.rq",
            "r26-34-negative-value-selection.rq",
            "r26-35-clean-capital-frontier.rq",
        }:
            self.assertIn(required, names)
        for sensor in sensors:
            text = sensor.read_text(encoding="utf-8")
            self.assertIn("PREFIX frc:", text, sensor.name)
            self.assertIn("SELECT", text, sensor.name)

    def test_regret_sensors_require_observed_alternatives(self):
        for name in ("r26-03-false-negative-opportunity.rq", "r26-05-observed-only-regret.rq", "r26-22-generation-missed-benefit.rq", "r26-23-subject-regret-frontier.rq"):
            text = (ROOT / "queries" / name).read_text(encoding="utf-8")
            self.assertIn("frc:observedAlternative true", text, name)

    def test_clean_frontier_preserves_zero_actuation(self):
        frontier = (ROOT / "queries/r26-30-clean-calibration-frontier.rq").read_text(encoding="utf-8")
        self.assertIn("frc:actuationPerformed false", frontier)
        self.assertIn('frc:standing "PARTIAL_ALIVE"', frontier)


if __name__ == "__main__":
    unittest.main()
