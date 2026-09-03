import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class OptionBreadthCourt(unittest.TestCase):
 def test_query_frontier_is_broad(self): self.assertGreaterEqual(len(list((ROOT/'queries').glob('*.rq'))),20)
if __name__=='__main__': unittest.main()
