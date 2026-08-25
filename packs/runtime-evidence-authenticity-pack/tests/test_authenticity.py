import unittest
from datetime import datetime,timezone
from scripts.types import Subject,Evidence
from scripts.authenticity import measure
class T(unittest.TestCase):
 def test_hardcoded(self):
  s=Subject("o/r","a"*40,"b"*64,1);now=datetime.now(timezone.utc);rows=[Evidence(s,str(i),"runtime",chr(99+i)*64,"1","1",i!=0,i==0,True,True,True,now) for i in range(4)]
  self.assertEqual(measure(rows).state,"UNAUTHENTIC")
