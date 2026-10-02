import unittest
from scripts.selector import Candidate, pareto, maximin, information_gain

class SelectorCourt(unittest.TestCase):
    def test_frontier_and_policy_noncollapse(self):
        a=Candidate("a",.9,.1,1,4,5); b=Candidate("b",.8,.05,1,5,5); c=Candidate("c",.4,.4,4,1,1)
        names={x.name for x in pareto([a,b,c])}
        self.assertEqual(names,{"a","b"})
        self.assertIn(maximin([a,b]).name,{"a","b"})
    def test_information_gain_positive(self):
        self.assertGreater(information_gain(.5,.9),0)

if __name__=="__main__": unittest.main()
