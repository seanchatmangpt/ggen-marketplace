import unittest
from scripts.calibration import Calibration
from scripts.standing import standing
from scripts.types import Subject,Refused
from scripts.receipt import manufacture
from scripts.replay import replay
class T(unittest.TestCase):
 def test_failure_dominance_and_tamper(self):
  c=Calibration(10,.1,0,0,.1,'CALIBRATED');self.assertEqual(standing(c,.2,'FAIL',True),'BUILD_BROKEN')
  r=manufacture(Subject('o/r','a'*40,'b'*64,1),c,(.2,('m','e','r'),5),'PARTIAL_ALIVE');self.assertEqual(replay(r),'REPLAY_MATCH');r['body']['standing']='ALIVE'
  with self.assertRaises(Refused): replay(r)
