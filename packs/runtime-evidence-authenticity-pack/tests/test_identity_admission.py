import unittest
from datetime import datetime,timezone,timedelta
from scripts.types import Subject,Evidence,Refused
from scripts.admission import admit
class T(unittest.TestCase):
 def test_future(self):
  now=datetime.now(timezone.utc);s=Subject("o/r","a"*40,"b"*64,1);e=Evidence(s,"e","runtime","c"*64,"1","1",True,False,True,True,True,now+timedelta(seconds=1))
  with self.assertRaises(Refused):admit(s,[e],now)
