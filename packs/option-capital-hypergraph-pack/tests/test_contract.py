import unittest
from pathlib import Path


class OptionCapitalContractTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parents[1]
        self.ontology = (self.root / "ontology.ttl").read_text()

    def test_dependency_closed_source_surface_exists(self):
        required = [
            "pack.toml",
            "ontology.ttl",
            "ggen.toml",
            "queries/10-opportunity-edges.rq",
            "queries/20-pareto-frontier.rq",
            "templates/opportunity-ledger.json.tera",
            "templates/pareto-frontier.json.tera",
            "gates/01-no-ambient-do.rq",
        ]
        for rel in required:
            self.assertTrue((self.root / rel).exists(), rel)

    def test_opportunity_edge_carries_required_ledger_dimensions(self):
        for predicate in [
            "oc:capability",
            "oc:composition",
            "oc:candidate",
            "oc:repository",
            "oc:marketplaceSupport",
            "oc:missingPrimitive",
            "oc:qualification",
            "oc:reversibility",
            "oc:expectedReuse",
            "oc:expectedCapabilitySpaceDelta",
        ]:
            self.assertIn(predicate, self.ontology)

    def test_explorer_has_no_do_authority(self):
        self.assertIn('oc:authority "SELECT|CONSTRUCT|VERIFY"', self.ontology)
        self.assertIn("oc:actuationPerformed false", self.ontology)
        self.assertNotIn('oc:authority "DO"', self.ontology)

    def test_frontier_is_reversible_and_non_dominated(self):
        self.assertIn("oc:reversible true", self.ontology)
        self.assertIn("oc:dominated false", self.ontology)


if __name__ == "__main__":
    unittest.main()
