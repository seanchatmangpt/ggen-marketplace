import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class Fortune5QualificationProfileTest(unittest.TestCase):
    def test_required_truths_have_all_three_proof_surfaces(self):
        profile = json.loads((ROOT / "qualification" / "fortune5-profile.json").read_text())
        required = {"compiler-truth", "conflict-truth", "trust-truth", "proof-truth"}
        capabilities = {item["id"]: item for item in profile["required_capabilities"]}
        self.assertEqual(set(capabilities), required)
        for item in capabilities.values():
            self.assertTrue(item["positive_execution"])
            self.assertTrue(item["negative_refusal"])
            self.assertTrue(item["receipt_replay"])

    def test_enterprise_authority_is_fail_closed(self):
        profile = json.loads((ROOT / "qualification" / "fortune5-profile.json").read_text())
        self.assertEqual(profile["subject"]["authority_ceiling"], "SELECT|CONSTRUCT|VERIFY")
        self.assertFalse(profile["subject"]["consequential_do"])
        gate = (ROOT / "gates" / "03-fortune5-control-plane.rq").read_text()
        self.assertIn('CONTAINS(STR(?authority), "DO")', gate)
        self.assertIn("STRLEN(STR(?receipt)) != 64", gate)

    def test_projection_queries_are_deterministic(self):
        config = (ROOT / "ggen.toml").read_text()
        for query_name in ("90-pareto-frontier.rq", "91-replayable-frontier.rq"):
            query = (ROOT / "queries" / query_name).read_text()
            self.assertIn("ORDER BY", query)
            self.assertIn(query_name, config)


if __name__ == "__main__":
    unittest.main()
