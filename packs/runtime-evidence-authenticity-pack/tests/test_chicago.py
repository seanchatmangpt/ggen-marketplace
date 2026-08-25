import unittest
from datetime import datetime,timezone
from fractions import Fraction
from scripts.types import Subject,Evidence
from scripts.calibration import Calibration
from scripts.qualify import qualify
from scripts.replay import replay
class T(unittest.TestCase):
 def test_live_shape(self):
  now=datetime.now(timezone.utc);s=Subject("seanchatmangpt/ex4pm","a"*40,"b"*64,7);origins=["runtime","rpc","dom","ocel"]
  rows=[Evidence(s,str(i),o,chr(99+i)*64,"42","42",True,False,True,True,True,now) for i,o in enumerate(origins)]
  q=qualify(s,rows,Calibration(20,Fraction(1,20),Fraction(1,20),"CALIBRATED"),now)
  self.assertEqual(q["standing"],"PARTIAL_ALIVE");self.assertFalse(q["actuation_performed"]);self.assertEqual(replay(q["receipt"]),"REPLAY_MATCH")
