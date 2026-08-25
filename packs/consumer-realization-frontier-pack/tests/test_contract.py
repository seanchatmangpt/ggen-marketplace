import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ContractCourt(unittest.TestCase):
    def test_zero_unreceipted_actuation_and_public_ontologies(self):
        text = (ROOT / "ontology.ttl").read_text()
        self.assertIn("crf:zeroUnreceiptedActuation true", text)
        for iri in ("http://www.w3.org/ns/prov#", "http://www.w3.org/2004/02/skos/core#", "http://www.w3.org/ns/dqv#"):
            self.assertIn(iri, text)

if __name__ == "__main__": unittest.main()
