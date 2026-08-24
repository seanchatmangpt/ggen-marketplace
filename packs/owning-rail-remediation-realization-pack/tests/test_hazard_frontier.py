import pathlib,sys,unittest
S=pathlib.Path(__file__).parents[1]/'scripts'; sys.path.insert(0,str(S))
from hazard import estimate,require_bounded
from current_frontier import current
class Court(unittest.TestCase):
    def test_hazard_refusal(self):
        with self.assertRaisesRegex(ValueError,'REGRESSION_HAZARD'):
            require_bounded(estimate([(1,2),(1,2),(2,1)]),.2)
    def test_split_frontier_refusal(self):
        with self.assertRaisesRegex(ValueError,'SPLIT_REALIZATION_FRONTIER'):
            current([(4,'a'),(4,'b')])
if __name__=='__main__': unittest.main()
