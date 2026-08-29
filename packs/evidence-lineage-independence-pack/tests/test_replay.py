import unittest
from scripts.types import *
from scripts.classifier import Verdict
from scripts.receipt import manufacture
from scripts.replay import replay
class T(unittest.TestCase):
 def test_tamper(self):
  r=manufacture(Subject("o/r","a"*40,"b"*64,1),Verdict("INDEPENDENT",0,0,4),"PARTIAL_ALIVE");self.assertEqual(replay(r),"REPLAY_MATCH");r["body"]["standing"]="ALIVE"
  with self.assertRaises(Refused):replay(r)
