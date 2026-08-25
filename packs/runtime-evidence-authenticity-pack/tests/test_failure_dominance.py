import unittest
from datetime import datetime,timezone
from fractions import Fraction
from scripts.types import Subject,Evidence
from scripts.authenticity import measure
from scripts.calibration import Calibration
from scripts.standing import standing
class T(unittest.TestCase):
 def test_owner_red(self):
  s=Subject("o/r","a"*40,"b"*64,1);now=datetime.now(timezone.utc);rows=[Evidence(s,str(i),o,chr(99+i)*64,"1","1",True,False,True,True,True,now) for i,o in enumerate(["runtime","rpc","dom","ocel"])]
  self.assertEqual(standing(measure(rows),Calibration(10,Fraction(0),Fraction(0),"CALIBRATED"),"FAIL"),"BUILD_BROKEN")
