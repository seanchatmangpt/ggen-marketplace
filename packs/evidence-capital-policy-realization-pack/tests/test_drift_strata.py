import unittest
from datetime import datetime, timezone
from scripts.types import Subject, PolicyDecision, PolicyOutcome
from scripts.drift import cusum
from scripts.strata import worst_stratum

class T(unittest.TestCase):
    def test_drift_and_strata(self):
        self.assertEqual(cusum([.5,.5]), "DRIFT")
        now = datetime.now(timezone.utc)
        subject = Subject("o/r", "a"*40, "b"*64, 1)
        a = PolicyDecision(subject,"a","MAX_GAIN",.1,1.0,"c"*64)
        b = PolicyDecision(subject,"b","MIN_FALSE_CAPITAL",.1,1.0,"d"*64)
        rows = ((a,PolicyOutcome(subject,"a",.4,.1,.1,now,True,"good")),(b,PolicyOutcome(subject,"b",-.1,.1,.1,now,True,"bad")))
        self.assertEqual(worst_stratum(rows), ("bad", -.1))
