import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class PublicOntologyTest(unittest.TestCase):
    def test_public_vocabularies_are_declared(self):
        ontology = (ROOT / "ontology.ttl").read_text()
        for iri in ("http://www.w3.org/ns/prov#", "http://www.w3.org/2004/02/skos/core#", "http://www.w3.org/ns/dqv#"):
            self.assertIn(iri, ontology)

if __name__ == "__main__": unittest.main()
