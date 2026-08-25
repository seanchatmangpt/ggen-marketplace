import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class StructuralMultiplierCourt(unittest.TestCase):
    def test_structural_frontier_exceeds_thousand_without_claiming_execution(self):
        text = (ROOT / "ontology.ttl").read_text()
        schemes = {
            "RealizationSurface": 5,
            "VerifierStrategy": 5,
            "DependencyRelief": 5,
            "ReceiptStrategy": 3,
            "ResilienceStrategy": 3,
        }
        for scheme, expected in schemes.items():
            self.assertEqual(expected, len(re.findall(rf"skos:inScheme crf:{scheme}\b", text)))
        self.assertEqual(1125, 5 * 5 * 5 * 3 * 3)
        template = (ROOT / "templates/frontier-cardinality.json.tera").read_text()
        self.assertIn("INFERRED_STRUCTURAL_NOT_OBSERVED", template)

if __name__ == "__main__": unittest.main()
