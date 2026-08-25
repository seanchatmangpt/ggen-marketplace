import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Contract(unittest.TestCase):
 def test_no_ambient_do(self):
  o=(ROOT/'ontology.ttl').read_text(); self.assertNotIn('fd:authority "DO"',o)
 def test_reversible_seed(self):
  self.assertIn('fd:reversible true',(ROOT/'ontology.ttl').read_text())
if __name__=='__main__': unittest.main()
