import unittest
from datetime import datetime,timezone
from scripts.types import *
from scripts.calibration import calibrate
from scripts.qualify import qualify
from scripts.replay import replay
class T(unittest.TestCase):
 def test_independent_surfaces(self):
  n=datetime.now(timezone.utc);s=Subject("seanchatmangpt/ex4pm","a"*40,"b"*64,7);r=[Source(s,str(i),chr(99+i)*64,chr(103+i)*64,chr(107+i)*64,f"d{i}",frozenset({chr(111+i)*64}),n) for i in range(4)]
  q=qualify(s,r,calibrate(["INDEPENDENT"]*5,["INDEPENDENT"]*5),n,[0]*6);self.assertEqual(q["standing"],"PARTIAL_ALIVE");self.assertEqual(q["verdict"].capital,4);self.assertEqual(replay(q["receipt"]),"REPLAY_MATCH")
