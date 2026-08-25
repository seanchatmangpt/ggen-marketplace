import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Contract(unittest.TestCase):
 def test_no_ambient_do(self):
  o=(ROOT/'ontology.ttl').read_text(); self.assertNotIn('fd:authority "DO"',o)
 def test_reversible_seed(self):
  self.assertIn('fd:reversible true',(ROOT/'ontology.ttl').read_text())
 def test_canonical_ggen_results_context(self):
  t=(ROOT/'templates'/'frontier.json.tera').read_text(); self.assertIn('results | json_encode()',t); self.assertNotIn('rows | json_encode()',t)
 def test_r44_qualification_surface_count(self):
  self.assertEqual(50,len(list((ROOT/'qualification_queries').glob('*.rq'))))
if __name__=='__main__': unittest.main()
