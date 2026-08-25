import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class AuthorityCourt(unittest.TestCase):
    def test_do_is_fenced_and_never_ambient(self):
        ontology = (ROOT / "ontology.ttl").read_text()
        self.assertIn('crf:requiresAuthority "DO"', ontology)
        self.assertIn('crf:reversible false', ontology)
        gate = (ROOT / "gates/10-authority-separation.rq").read_text()
        self.assertIn('"SELECT", "DO"', gate)
        for template in (ROOT / "templates").glob("*.tera"):
            self.assertNotIn("actuationPerformed", template.read_text())

if __name__ == "__main__": unittest.main()
