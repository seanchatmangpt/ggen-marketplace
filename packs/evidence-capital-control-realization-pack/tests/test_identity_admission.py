import unittest
from datetime import datetime,timezone,timedelta
from scripts.types import Subject,Decision,Realization,Refused
from scripts.admission import admit
class T(unittest.TestCase):
 def test_future_and_fabricated_counterfactual_refuse(self):
  now=datetime.now(timezone.utc);s=Subject('o/r','a'*40,'b'*64,1);d=Decision('d','RETAIN',.2,'c'*64,'d'*64)
  with self.assertRaises(Refused): admit(s,[Realization(s,d,'o',1,.8,0,0,False,None,'m','e','r',now+timedelta(seconds=1))],now)
  with self.assertRaises(Refused): admit(s,[Realization(s,d,'x',1,.8,0,0,False,.5,'m','e','r',now)],now)
