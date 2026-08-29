import unittest
from datetime import datetime,timezone,timedelta
from scripts.types import *
from scripts.admission import admit
class T(unittest.TestCase):
 def test_future(self):
  n=datetime.now(timezone.utc);s=Subject("o/r","a"*40,"b"*64,1);x=Source(s,"x","c"*64,"d"*64,"e"*64,"f",frozenset({"f"*64}),n+timedelta(seconds=1))
  with self.assertRaises(Refused):admit(s,[x],n)
