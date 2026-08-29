import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).parents[1] / "scripts" / "topology.py"
SPEC = importlib.util.spec_from_file_location("topology", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

class TopologyCourt(unittest.TestCase):
    def test_cut_and_cycle(self):
        self.assertEqual(MOD.blocker_cut([("b", "a"), ("c", "b")], {"a"}), ("a", "b", "c"))
        with self.assertRaises(MOD.Refused):
            MOD.admit_acyclic(["a", "b"], [("a", "b"), ("b", "a")])
