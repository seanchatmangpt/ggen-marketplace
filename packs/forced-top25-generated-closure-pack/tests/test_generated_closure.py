import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class GeneratedClosureCourt(unittest.TestCase):
    def test_every_observed_dspygen_projection_has_validator(self):
        fixture = (ROOT / "qualification" / "dspygen.ttl").read_text(encoding="utf-8")
        self.assertEqual(fixture.count("a fgc:GeneratedArtifact"), 3)
        self.assertEqual(fixture.count("fgc:validatorCommand"), 3)

    def test_projection_is_deterministically_ordered(self):
        query = (ROOT / "queries" / "10-generated-closure.rq").read_text(encoding="utf-8")
        self.assertIn("ORDER BY ?consumer ?path ?language ?validator", query)

    def test_authority_excludes_do(self):
        ontology = (ROOT / "ontology.ttl").read_text(encoding="utf-8")
        self.assertIn('fgc:consequentialDo false', ontology)
        self.assertNotIn('fgc:authority "DO"', ontology)


if __name__ == "__main__":
    unittest.main()
