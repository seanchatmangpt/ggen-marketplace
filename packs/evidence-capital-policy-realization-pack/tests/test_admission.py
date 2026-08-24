import unittest
from datetime import datetime, timezone, timedelta
from scripts.types import Subject, PolicyDecision, PolicyOutcome, Refused
from scripts.admission import admit

class T(unittest.TestCase):
    def test_admission_falsifiers(self):
        now = datetime.now(timezone.utc)
        subject = Subject("o/r", "a"*40, "b"*64, 1)
        foreign = Subject("o/r", "c"*40, "b"*64, 1)
        decision = PolicyDecision(subject, "d", "MAX_GAIN", .5, 1.0, "d"*64)
        with self.assertRaises(Refused):
            admit(subject, [decision], [PolicyOutcome(foreign,"d",.5,.1,.2,now,True,"x")], now)
        with self.assertRaises(Refused):
            admit(subject, [decision], [PolicyOutcome(subject,"d",.5,.1,.2,now+timedelta(seconds=1),True,"x")], now)
        with self.assertRaises(Refused):
            admit(subject, [decision], [PolicyOutcome(subject,"d",.5,.1,.2,now,False,"x")], now)
