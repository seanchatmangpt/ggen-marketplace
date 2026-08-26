import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class GateSurfaceCourt(unittest.TestCase):
 def test_enterprise_gates_exist(self): self.assertGreaterEqual(len(list((ROOT/'gates').glob('*.rq'))),8)
if __name__=='__main__': unittest.main()
