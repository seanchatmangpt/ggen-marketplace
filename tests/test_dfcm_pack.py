"""dfcm-pack uniform exact-stem witness court (v2.2.0 consolidation).

Drives qualification/verify.py as a module: the whole 64-gate corpus must be
witnessed (pass silent, fail fires), and a mutated pass witness must be refused
(anti-vacuity, composition law C05: reverting/mutating the subject must make
acceptance fail).
"""
import importlib.util
import sys
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "packs" / "dfcm-pack"

# Load namespaced ("dfcm_verify"), NOT via `import verify`: a bare module name
# here squats in sys.modules and any later `import verify` in the same pytest
# process (e.g. evolvable-capability-pack's bench.py) would silently bind THIS
# pack's module. One canonical name per module, no cross-pack squatting.
_spec = importlib.util.spec_from_file_location("dfcm_verify", PACK / "qualification" / "verify.py")
verify = importlib.util.module_from_spec(_spec)
sys.modules["dfcm_verify"] = verify
_spec.loader.exec_module(verify)


class DfcmCourt(unittest.TestCase):
    def test_all_gates_witnessed_and_admitted(self):
        self.assertEqual(verify.main.__module__, "dfcm_verify")
        for gate in verify.gates():
            pass_rows = verify.rows_for(verify.load_graph(verify.PASS / f"{gate.stem}.ttl"), gate)
            self.assertEqual(pass_rows, [], f"{gate.stem}: pass witness fired")
            fail_graph = verify.Graph()
            fail_graph.parse(verify.FAIL / f"{gate.stem}.ttl", format="turtle")
            self.assertTrue(verify.rows_for(fail_graph, gate), f"{gate.stem}: fail witness silent")

    def test_mutated_pass_witness_is_refused(self):
        gate = verify.gates()[0]
        mutated = verify.Graph()
        mutated.parse(verify.FAIL / f"{gate.stem}.ttl", format="turtle")
        self.assertTrue(verify.refusing_gates(mutated), "mutated world must carry refusing gates")

    def test_gate_corpus_size(self):
        self.assertGreaterEqual(len(verify.gates()), 60)


if __name__ == "__main__":
    unittest.main()
