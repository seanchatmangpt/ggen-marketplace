import unittest
from datetime import datetime,timezone
from scripts.types import Subject,Decision,Realization
from scripts.gain import realized_gain,net_gain
from scripts.regret import observed_regret
class T(unittest.TestCase):
 def test_observed_only_regret(self):
  s=Subject('o/r','a'*40,'b'*64,1);d=Decision('d','ACQUIRE',.5,'c'*64,'d'*64);r=Realization(s,d,'o',1,.4,.1,0,True,.2,'m','e','r',datetime.now(timezone.utc))
  self.assertAlmostEqual(realized_gain(r),.6);self.assertAlmostEqual(net_gain(r),.5);self.assertAlmostEqual(observed_regret(r),.2)
