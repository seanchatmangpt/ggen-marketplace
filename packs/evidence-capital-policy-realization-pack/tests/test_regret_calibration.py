import unittest
from datetime import datetime, timezone
from scripts.types import Subject, PolicyDecision, PolicyOutcome, Refused
from scripts.regret import observed_regret
from scripts.calibration import calibrate

class T(unittest.TestCase):
    def test_regret_and_calibration(self):
        now = datetime.now(timezone.utc)
        subject = Subject("o/r", "a"*40, "b"*64, 1)
        rows = []
        for i in range(8):
            d = PolicyDecision(subject, str(i), "MAX_GAIN", .5, 1.0, chr(100+i)*64)
            o = PolicyOutcome(subject, str(i), .55, .05, .2, now, True, "x")
            rows.append((d,o))
        self.assertEqual(calibrate(rows).state, "CALIBRATED")
        with self.assertRaises(Refused): observed_regret(rows[:1], {})
        self.assertAlmostEqual(observed_regret(rows[:1], {"0":[("observed:alt", .8)]})["0"], .25)
