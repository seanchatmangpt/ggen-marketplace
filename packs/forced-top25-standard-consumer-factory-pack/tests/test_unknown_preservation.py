import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class UnknownPreservationCourt(unittest.TestCase):
 def test_unknown_targets_are_not_deleted_or_promoted(self):
  text=(ROOT/'forced-top25.ttl').read_text()
  self.assertGreaterEqual(text.count('fta:compatibilityState "UNKNOWN"'), 22)
  self.assertGreaterEqual(text.count('UPSTREAM_ADMISSIBILITY_RECEIPT_MISSING'), 21)
if __name__=='__main__': unittest.main()
