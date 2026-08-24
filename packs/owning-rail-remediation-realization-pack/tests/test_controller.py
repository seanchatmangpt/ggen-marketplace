import pathlib,sys,unittest
S=pathlib.Path(__file__).parents[1]/'scripts'; sys.path.insert(0,str(S))
from controller import Outcome,standing
class Court(unittest.TestCase):
    def test_realized_and_regressed(self):
        self.assertEqual(standing(Outcome(5,2,4)),'REALIZED')
        self.assertEqual(standing(Outcome(2,3,1)),'REGRESSED')
    def test_regret_is_observed_only(self):
        self.assertEqual(Outcome(5,3,4).regret,2)
if __name__=='__main__': unittest.main()
