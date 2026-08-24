import importlib.util
import pathlib
import unittest
from datetime import datetime, timedelta, timezone

PATH = pathlib.Path(__file__).parents[1] / "scripts" / "freshness.py"
SPEC = importlib.util.spec_from_file_location("freshness", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

class FreshnessCourt(unittest.TestCase):
    def test_future_and_stale(self):
        now = datetime.now(timezone.utc)
        with self.assertRaises(MOD.Refused):
            MOD.freshness(now + timedelta(seconds=1), now, 10)
        self.assertEqual(MOD.freshness(now - timedelta(seconds=20), now, 10), "STALE")
