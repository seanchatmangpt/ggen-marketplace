import unittest
from scripts.types import Subject, Refused
from scripts.calibration import Calibration
from scripts.receipt import manufacture
from scripts.replay import replay

class T(unittest.TestCase):
    def test_tamper_refuses(self):
        receipt = manufacture(Subject("o/r","a"*40,"b"*64,1), Calibration(6,.1,0,0,.5,"CALIBRATED"), ("x",.2), "PARTIAL_ALIVE")
        self.assertEqual(replay(receipt), "REPLAY_MATCH")
        receipt["body"]["standing"] = "ALIVE"
        with self.assertRaises(Refused): replay(receipt)
