import unittest
from datetime import datetime,timezone
from scripts.types import Subject,Trial
from scripts.gain import summarize
from scripts.calibration import calibrate

class T(unittest.TestCase):
    def test_false_capital_is_not_hidden(self):
        now=datetime.now(timezone.utc); s=Subject("o/r","a"*40,"b"*64,1)
        rows=[]
        for i in range(5):
            augmented=1.1 if i==0 else 0.5
            rows.append(Trial(s,str(i),"c"*64,chr(100+i)*64,2,0.8,1,1,augmented,0.2,now))
        summary=summarize(rows); calibration=calibrate(rows)
        self.assertEqual(summary.support,5)
        self.assertEqual(calibration.state,"CALIBRATED")
        self.assertEqual(float(calibration.false_capital_rate),0.2)
        self.assertGreater(calibration.wilson_upper,0.2)
