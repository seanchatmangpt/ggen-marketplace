import unittest
from scripts.frontier import ControlModel,current_frontier
from scripts.drift import cusum
from scripts.types import Refused
class T(unittest.TestCase):
 def test_split_current_and_drift(self):
  with self.assertRaises(Refused): current_frontier([ControlModel('RETAIN',1,'a'*64,'CALIBRATED'),ControlModel('RETAIN',1,'b'*64,'CALIBRATED')])
  self.assertEqual(cusum([0,0,2],threshold=1),'DRIFT')
