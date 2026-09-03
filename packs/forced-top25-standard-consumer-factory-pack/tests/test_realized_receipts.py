import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class RealizedReceiptCourt(unittest.TestCase):
 def test_ex4pm_and_gymact_are_only_realized_seed_consumers(self):
  text=(ROOT/'forced-top25.ttl').read_text()
  self.assertEqual(text.count('fts:fanoutState "DOWNSTREAM_REALIZED"'), 2)
  self.assertIn('fts:consumerCommitCount 5', text)
  self.assertIn('fts:consumerCommitCount 6', text)
if __name__=='__main__': unittest.main()
