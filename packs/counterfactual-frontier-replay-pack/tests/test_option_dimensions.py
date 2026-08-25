import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class OptionDimensionsCourt(unittest.TestCase):
    def test_required_dimensions_exist(self):
        ontology = (ROOT / "ontology.ttl").read_text(encoding="utf-8")
        for predicate in ("cfr:reversibility", "cfr:expectedReuse", "cfr:expectedCapabilitySpaceDelta"):
            self.assertIn(predicate, ontology)

if __name__ == "__main__":
    unittest.main()
