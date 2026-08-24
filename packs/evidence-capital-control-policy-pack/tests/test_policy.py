import unittest
from scripts.policy import Policy, admitted, max_gain, min_false_capital, min_concentration
from scripts.sensitivity import Sensitivity

class PolicyCourt(unittest.TestCase):
    def test_noncollapsed_selectors(self):
        a=Policy("gain",.8,.15,.7,1.2,10); b=Policy("safe",.5,.02,.4,1.5,10); c=Policy("spread",.4,.05,.1,1.1,10)
        self.assertEqual(max_gain([a,b,c]).name,"gain")
        self.assertEqual(min_false_capital([a,b,c]).name,"safe")
        self.assertEqual(min_concentration([a,b,c]).name,"spread")
    def test_sensitivity_and_owner_failure(self):
        self.assertGreater(Sensitivity(2,.8).lower_gain(),0)
        self.assertFalse(admitted(Policy("red",1,0,0,1,10,"BUILD_BROKEN")))

if __name__=="__main__": unittest.main()
