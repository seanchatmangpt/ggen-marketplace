import importlib.util
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).parents[1]
CONTRACT = ROOT / "templates" / "governance_gate_contract.py.tera"


def load_contract():
    name = "governance_gate_contract"
    loader = SourceFileLoader(name, str(CONTRACT))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


class GovernanceGateContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = load_contract()

    def test_pack_surface_and_semantic_invariants(self):
        for rel in (
            "pack.toml",
            "ggen.toml",
            "ontology.ttl",
            "shapes.ttl",
            "queries/10-profile.rq",
            "templates/governance_gate_contract.py.tera",
        ):
            self.assertTrue((ROOT / rel).is_file(), rel)

        ontology = (ROOT / "ontology.ttl").read_text(encoding="utf-8")
        self.assertIn("gg:proposalImpliesAuthority false", ontology)
        self.assertIn("gg:admissionImpliesAuthority false", ontology)
        self.assertIn("gg:authorityImpliesPreparedReceipt false", ontology)

    def test_proposal_admission_and_authority_are_not_do(self):
        c = self.contract
        for value in (
            c.GateInput(False, False, False),
            c.GateInput(True, False, False),
            c.GateInput(True, True, False),
        ):
            self.assertFalse(c.classify(value).ready_for_do)

    def test_only_admitted_authorized_prepared_is_ready_for_do(self):
        c = self.contract
        decision = c.classify(c.GateInput(True, True, True))
        self.assertEqual(decision.standing, c.Standing.PREPARED)
        self.assertTrue(decision.ready_for_do)

    def test_receipt_without_authority_is_refused(self):
        c = self.contract
        decision = c.classify(c.GateInput(True, False, True))
        self.assertEqual(decision.standing, c.Standing.REFUSED)
        self.assertEqual(decision.refusal_code, "AUTHORITY_REQUIRED")

    def test_information_obstruction_is_machine_detectable(self):
        c = self.contract
        witness = c.evidence_ceiling(
            [
                ("left", {"docs": ["same"]}, frozenset({"GO"})),
                ("right", {"docs": ["same"]}, frozenset({"NO_GO"})),
            ]
        )
        self.assertEqual(witness["code"], "EVIDENCE_CEILING")


if __name__ == "__main__":
    unittest.main()
