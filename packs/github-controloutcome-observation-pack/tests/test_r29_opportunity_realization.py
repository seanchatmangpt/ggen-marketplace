import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class R29OpportunityRealizationCourt(unittest.TestCase):
    def test_query_surface_is_noncollapsed(self):
        queries = sorted((ROOT / "queries" / "r29-opportunity-realization").glob("*.rq"))
        self.assertEqual(len(queries), 20)
        self.assertEqual(len({q.read_text() for q in queries}), 20)

    def test_generation_frontier_is_deterministic(self):
        text = (ROOT / "queries" / "r29-opportunity-realization" / "20-clean-realization-candidate-frontier.rq").read_text()
        self.assertIn("ORDER BY", text)
        manifest = (ROOT / "ggen.toml").read_text()
        self.assertIn('name = "opportunity-realization-r29"', manifest)
        self.assertIn('name = "opportunity-realization-r29-court"', manifest)

    def test_exact_grounded_controloutcome_realization(self):
        fixture = (ROOT / "fixtures" / "r29-opportunity-realization.ttl").read_text()
        for sha in [
            "92868812558dbbc597c2650fdb0f97cdcb8637f0",
            "df9b0d92b4d78360577c8b127e159b1827c79b59",
        ]:
            self.assertIn(sha, fixture)
        self.assertIn("github-run-job-pr-controloutcome-adapter", fixture)

    def test_fail_closed_gates_exist(self):
        self.assertTrue((ROOT / "gates" / "r29-exact-realization-subject.rq").exists())
        self.assertTrue((ROOT / "gates" / "r29-no-red-owning-court.rq").exists())

    def test_generated_outputs_are_not_editing_surfaces(self):
        self.assertTrue((ROOT / "templates" / "opportunity-realization-r29.json.tera").exists())
        self.assertTrue((ROOT / "templates" / "opportunity-realization-r29-court.py.tera").exists())
        self.assertFalse((ROOT / "opportunity-realization-r29.json").exists())
        self.assertFalse((ROOT / "qualify-opportunity-realization-r29.py").exists())

if __name__ == "__main__":
    unittest.main()
