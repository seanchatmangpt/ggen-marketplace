import unittest
from datetime import datetime,timezone
from scripts.types import *
from scripts.clusters import clusters
from scripts.capital import effective_capital
class T(unittest.TestCase):
 def test_common_cause_collapses(self):
  n=datetime.now(timezone.utc);s=Subject("o/r","a"*40,"b"*64,1);r=[Source(s,str(i),chr(99+i)*64,"d"*64,"e"*64,"same",frozenset({"f"*64}),n) for i in range(4)]
  self.assertEqual(effective_capital(r,clusters(r),[1]),1)
