import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.models import Outcome,Refused
from scripts.effect import self_normalized
from scripts.regret import conservative_regret
from scripts.rollback import rollback_safe
from scripts.sensitivity import robust_positive
from scripts.selector import select
from scripts.receipt import issue
from scripts.replay import replay

class Court(unittest.TestCase):
    def outcomes(self):
        return [Outcome("a","a"*40,4,1,0.8,0.2),Outcome("b","a"*40,4,2,0.7,0.05)]
    def test_counterfactual_path(self):
        xs=self.outcomes(); effect=self_normalized(xs)
        self.assertGreater(effect,0)
        chosen=select(xs,"MAX_RELIEF")
        self.assertTrue(rollback_safe(chosen,0.5))
        self.assertTrue(robust_positive(effect,1.1))
        regret=conservative_regret(chosen.relief,[3.2,2.2])
        r=issue("a"*40,chosen.remediation_id,effect,regret,True)
        self.assertEqual(replay(r),"REPLAY_MATCH")
    def test_regression_refuses(self):
        bad=Outcome("bad","a"*40,1,3,1.0,0.1)
        with self.assertRaises(Refused): rollback_safe(bad,0.5)

if __name__=="__main__": unittest.main()
