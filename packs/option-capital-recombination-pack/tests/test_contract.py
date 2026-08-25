import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ContractTest(unittest.TestCase):
    def test_authority_is_non_actuating(self):
        ontology = (ROOT / "ontology.ttl").read_text()
        self.assertIn('ocr:authority "SELECT"', ontology)
        self.assertNotIn('ocr:authority "DO"', ontology)

if __name__ == "__main__": unittest.main()
