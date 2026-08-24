import unittest
from fractions import Fraction
from scripts.types import Subject,Refused
from scripts.calibration import CapitalCalibration
from scripts.gain import GainSummary
from scripts.receipt import manufacture
from scripts.replay import replay

class T(unittest.TestCase):
    def test_tamper_refuses(self):
        s=Subject("o/r","a"*40,"b"*64,1)
        c=CapitalCalibration(10,Fraction(0),0.2,"CALIBRATED")
        g=GainSummary(10,0.4,Fraction(1),Fraction(0))
        r=manufacture(s,c,g,{"mean_reported_gain":0.2},{"roots":2},{"stratum":"x","mean_loss_reduction":0.2},"PARTIAL_ALIVE")
        self.assertEqual(replay(r),"REPLAY_MATCH")
        r["body"]["standing"]="ALIVE"
        with self.assertRaises(Refused): replay(r)
