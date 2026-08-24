import unittest
from datetime import datetime, timezone
from scripts.types import Subject, PolicyDecision, PolicyOutcome, Refused
from scripts.gamma import gamma_robustness
from scripts.frontier import current_frontier

class T(unittest.TestCase):
    def test_gamma_and_frontier(self):
        now = datetime.now(timezone.utc)
        subject = Subject("o/r", "a"*40, "b"*64, 1)
        a = PolicyDecision(subject,"a","GAMMA_ROBUST",.5,1.0,"c"*64)
        b = PolicyDecision(subject,"b","GAMMA_ROBUST",.4,2.0,"d"*64)
        with self.assertRaises(Refused):
            gamma_robustness(((a,PolicyOutcome(subject,"a",.2,.1,.2,now,True,"x")),(b,PolicyOutcome(subject,"b",.4,.1,.2,now,True,"x"))))
        with self.assertRaises(Refused): current_frontier([a,b])
