import unittest
from fractions import Fraction
from scripts.types import Subject,Refused
from scripts.authenticity import Authenticity
from scripts.calibration import Calibration
from scripts.receipt import manufacture
from scripts.replay import replay
class T(unittest.TestCase):
 def test_tamper(self):
  r=manufacture(Subject("o/r","a"*40,"b"*64,1),Authenticity(4,Fraction(1),Fraction(1),Fraction(1),Fraction(1),"AUTHENTIC"),Calibration(10,Fraction(0),Fraction(0),"CALIBRATED"),"PARTIAL_ALIVE");self.assertEqual(replay(r),"REPLAY_MATCH");r["body"]["standing"]="ALIVE"
  with self.assertRaises(Refused):replay(r)
