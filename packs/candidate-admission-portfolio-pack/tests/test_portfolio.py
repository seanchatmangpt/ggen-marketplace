import unittest
from scripts.portfolio import Candidate, Refused, frontier

class PortfolioCourt(unittest.TestCase):
    def test_pareto_preserves_distinct_winners(self):
        a=Candidate("a",3,.1,2,8,4); b=Candidate("b",3,.2,1,6,8); c=Candidate("c",3,.2,4,4,2)
        self.assertEqual({x.name for x in frontier([a,b,c])},{"a","b"})
    def test_sparse_candidate_refuses(self):
        with self.assertRaises(Refused): frontier([Candidate("x",1,.1,1,9,9)])

if __name__=="__main__": unittest.main()
