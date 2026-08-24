import pathlib,sys,unittest
S=pathlib.Path(__file__).parents[1]/'scripts'; sys.path.insert(0,str(S))
from controller import Outcome
from qualification import qualify
class Court(unittest.TestCase):
    def test_build_broken_dominates(self):
        q=qualify(Outcome(3,0,3),[(3,0),(2,1)],'BUILD_BROKEN')
        self.assertEqual(q.standing,'BUILD_BROKEN')
    def test_realized_zero_blocker_path(self):
        q=qualify(Outcome(3,0,3),[(3,0),(2,1),(1,0)],'ALIVE')
        self.assertEqual(q.standing,'PARTIAL_ALIVE')
if __name__=='__main__': unittest.main()
