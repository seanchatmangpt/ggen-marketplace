import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class CounterfactualFrontierSurfaceTest(unittest.TestCase):
    def test_queries_gates_templates_are_dependency_closed(self):
        self.assertEqual(len(list((ROOT / "queries").glob("*.rq"))), 10)
        self.assertEqual(len(list((ROOT / "gates").glob("*.rq"))), 3)
        self.assertEqual(len(list((ROOT / "templates").glob("*.tera"))), 2)
        self.assertTrue((ROOT / "qualification" / "fortune5-profile.json").is_file())
        config = (ROOT / "ggen.toml").read_text(encoding="utf-8")
        self.assertIn("90-pareto-frontier.rq", config)
        self.assertIn("91-replayable-frontier.rq", config)


if __name__ == "__main__":
    unittest.main()
