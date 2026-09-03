import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class RevenueLaunderingCourt(unittest.TestCase):
 def test_structural_claim_gate_exists(self): self.assertTrue((ROOT/'gates'/'07-no-structural-revenue-claim.rq').exists())
if __name__=='__main__': unittest.main()
