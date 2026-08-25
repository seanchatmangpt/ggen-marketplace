import unittest
from datetime import datetime,timezone
from scripts.types import Subject,Evidence,Refused
from scripts.independence import require_independent_roots
class T(unittest.TestCase):
 def test_shared_root(self):
  s=Subject("o/r","a"*40,"b"*64,1);now=datetime.now(timezone.utc);rows=[Evidence(s,str(i),"runtime","c"*64,"1","1",True,False,True,True,True,now) for i in range(4)]
  with self.assertRaises(Refused):require_independent_roots(rows)
