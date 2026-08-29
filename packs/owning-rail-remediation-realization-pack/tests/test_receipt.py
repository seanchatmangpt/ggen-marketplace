import hashlib
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parents[1] / "scripts"
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class ReceiptCourt(unittest.TestCase):
    def test_replay_and_tamper(self):
        receipt = load("receipt").manufacture("a" * 40, "b" * 64, "REALIZED", 2, 0)
        replay = load("replay")
        self.assertEqual(replay.replay(receipt), "REPLAY_MATCH")
        receipt["body"]["actuation_performed"] = True
        with self.assertRaises(replay.Refused):
            replay.replay(receipt)
