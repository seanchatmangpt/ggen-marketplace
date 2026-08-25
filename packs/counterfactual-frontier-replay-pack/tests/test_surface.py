import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class CounterfactualFrontierSurfaceTest(unittest.TestCase):
    def test_queries_gates_templates_are_dependency_closed(self):
        queries = {path.name for path in (ROOT / "queries").glob("*.rq")}
        required_queries = {
            "10-capability-space-delta.rq",
            "20-reversibility.rq",
            "30-reuse-weighted-options.rq",
            "40-composition-order.rq",
            "50-current-qualified.rq",
            "60-receipt-safe.rq",
            "70-authority-safe.rq",
            "80-dominated-alternatives.rq",
            "90-pareto-frontier.rq",
            "91-replayable-frontier.rq",
        }
        self.assertTrue(required_queries <= queries, required_queries - queries)
        self.assertEqual(len(list((ROOT / "gates").glob("*.rq"))), 3)
        self.assertEqual(len(list((ROOT / "templates").glob("*.tera"))), 2)
        self.assertTrue((ROOT / "qualification" / "fortune5-profile.json").is_file())
        config = (ROOT / "ggen.toml").read_text(encoding="utf-8")
        self.assertIn("90-pareto-frontier.rq", config)
        self.assertIn("91-replayable-frontier.rq", config)


if __name__ == "__main__":
    unittest.main()
