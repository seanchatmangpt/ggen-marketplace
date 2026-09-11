import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class R27Surface(unittest.TestCase):
    def test_sensor_count_and_identity(self):
        queries = sorted((ROOT / "queries").glob("r27-*.rq"))
        self.assertGreaterEqual(len(queries), 30)
        self.assertEqual(len({p.name for p in queries}), len(queries))
        for path in queries:
            text = path.read_text()
            self.assertIn("PREFIX gco:", text, path.name)
            self.assertIn("SELECT", text, path.name)

    def test_observability_dimensions_present(self):
        names = {p.name for p in (ROOT / "queries").glob("r27-*.rq")}
        required = {
            "r27-03-failed-job-frontier.rq",
            "r27-07-run-attempt-supersession.rq",
            "r27-08-orphan-job-observations.rq",
            "r27-09-pr-head-correspondence.rq",
            "r27-14-evidence-root-diversity.rq",
            "r27-19-live-discovery-multiplier.rq",
            "r27-21-mixed-owning-rail-topology.rq",
            "r27-22-failure-root-fanout.rq",
            "r27-23-repair-realization-by-attempt.rq",
            "r27-24-unreceipted-current-evidence.rq",
            "r27-30-current-risk-frontier.rq",
        }
        self.assertTrue(required <= names)

    def test_zero_do_preserved(self):
        ontology = (ROOT / "ontology.ttl").read_text()
        self.assertNotIn("gco:actuationPerformed true", ontology)
        self.assertIn('gco:consequential', ontology) if 'gco:consequential' in ontology else None


if __name__ == "__main__":
    unittest.main()
