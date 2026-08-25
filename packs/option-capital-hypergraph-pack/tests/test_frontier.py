import unittest
from pathlib import Path


class FrontierTests(unittest.TestCase):
    def setUp(self):
        self.ontology = (Path(__file__).parents[1] / "ontology.ttl").read_text()

    def test_pairwise_and_third_order_alternatives_coexist(self):
        self.assertEqual(self.ontology.count(" a oc:Composition ;"), 4)
        self.assertEqual(self.ontology.count(" a oc:Candidate ;"), 4)
        self.assertEqual(self.ontology.count(" a oc:OpportunityEdge ;"), 4)

    def test_every_seed_candidate_is_reversible(self):
        self.assertEqual(self.ontology.count("oc:reversible true"), 4)
        self.assertNotIn("oc:actuationPerformed true", self.ontology)

    def test_capability_space_delta_is_not_collapsed_to_one_winner(self):
        for delta in ["3", "4", "6"]:
            self.assertIn(f"oc:expectedCapabilitySpaceDelta {delta}", self.ontology)


if __name__ == "__main__":
    unittest.main()
