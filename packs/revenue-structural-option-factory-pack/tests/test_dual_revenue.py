import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class DualRevenueCourt(unittest.TestCase):
 def test_from_and_for_remain_distinct(self):
  t=(ROOT/'ontology.ttl').read_text(); self.assertIn('RevenueFROMCustomer',t); self.assertIn('RevenueFORCustomer',t)
if __name__=='__main__': unittest.main()
