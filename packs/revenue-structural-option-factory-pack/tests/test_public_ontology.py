import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class PublicOntologyCourt(unittest.TestCase):
 def test_public_semantics(self):
  text=(ROOT/'ontology.ttl').read_text(); self.assertIn('www.w3.org/ns/prov',text); self.assertIn('www.w3.org/2004/02/skos',text)
if __name__=='__main__': unittest.main()
