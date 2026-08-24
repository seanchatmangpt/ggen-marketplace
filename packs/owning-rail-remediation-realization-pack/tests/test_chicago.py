import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parents[1] / "scripts"
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class ChicagoCourt(unittest.TestCase):
    def test_owner_red_remains_non_alive_until_blockers_clear(self):
        realization = load("realization")
        reliability = load("reliability")
        self.assertEqual(realization.Realization(3, 1, "PASS").classify(), "UNREALIZED")
        self.assertEqual(realization.Realization(1, 1, "FAIL").classify(), "BUILD_BROKEN")
        self.assertGreater(reliability.realized_rate(["REALIZED", "REALIZED", "UNREALIZED"]), 0.5)
