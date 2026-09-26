import importlib.util
import json
import sys
import unittest
from dataclasses import replace
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).parents[1]
CONTRACT = ROOT / "templates" / "governance_gate_contract.py.tera"
VECTORS = ROOT / "vectors" / "conformance.json"


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
            "vectors/conformance.json",
            "gate-court.toml",
        ):
            self.assertTrue((ROOT / rel).is_file(), rel)

        ontology = (ROOT / "ontology.ttl").read_text(encoding="utf-8")
        self.assertIn("gg:proposalImpliesAuthority false", ontology)
        self.assertIn("gg:admissionImpliesAuthority false", ontology)
        self.assertIn("gg:authorityImpliesPreparedReceipt false", ontology)

    def test_exhaustive_state_vectors(self):
        c = self.contract
        payload = json.loads(VECTORS.read_text(encoding="utf-8"))
        self.assertEqual(len(payload["cases"]), 8)

        for vector in payload["cases"]:
            decision = c.classify(c.GateInput(**vector["input"]))
            expected = vector["expected"]
            self.assertEqual(
                decision.standing.value,
                expected["standing"],
                vector["id"],
            )
            self.assertEqual(
                decision.ready_for_do,
                expected["ready_for_do"],
                vector["id"],
            )
            self.assertEqual(
                decision.refusal_code,
                expected["refusal_code"],
                vector["id"],
            )

    def test_only_admitted_authorized_prepared_is_ready_for_do(self):
        c = self.contract
        decision = c.require_ready_for_do(c.GateInput(True, True, True))
        self.assertEqual(decision.standing, c.Standing.PREPARED)
        self.assertTrue(decision.ready_for_do)

    def test_non_prepared_state_raises_typed_refusal(self):
        c = self.contract
        with self.assertRaises(c.GovernanceGateRefusal) as exc:
            c.require_ready_for_do(c.GateInput(True, True, False))
        self.assertEqual(exc.exception.decision.standing, c.Standing.AUTHORIZED)

    def test_decision_receipt_is_deterministic_and_replayable(self):
        c = self.contract
        value = c.GateInput(True, True, True)

        first = c.decision_receipt("subject-1", value)
        second = c.decision_receipt("subject-1", value)

        self.assertEqual(first.digest, second.digest)
        self.assertTrue(first.digest.startswith("sha256:"))
        self.assertEqual(c.replay_receipt(first), first.decision)
        self.assertEqual(first.to_dict()["decision"]["standing"], "PREPARED")

    def test_tampered_receipt_refuses_replay(self):
        c = self.contract
        receipt = c.decision_receipt(
            "subject-1",
            c.GateInput(True, True, True),
        )
        tampered = replace(receipt, digest="sha256:" + ("0" * 64))

        with self.assertRaisesRegex(ValueError, "RECEIPT_DIGEST_MISMATCH"):
            c.replay_receipt(tampered)

    def test_information_obstruction_enumerates_every_conflict(self):
        c = self.contract
        witnesses = c.evidence_obstructions(
            [
                ("a", {"docs": ["same"]}, frozenset({"GO"})),
                ("b", {"docs": ["same"]}, frozenset({"NO_GO"})),
                ("c", {"docs": ["same"]}, frozenset({"REWORK"})),
            ]
        )
        self.assertEqual(len(witnesses), 3)
        self.assertTrue(all(row["code"] == "EVIDENCE_CEILING" for row in witnesses))

    def test_empty_accepted_outputs_refuse_as_malformed_contract(self):
        c = self.contract
        with self.assertRaisesRegex(ValueError, "ACCEPTED_OUTPUTS_REQUIRED"):
            c.evidence_obstructions([("bad", {"x": 1}, frozenset())])

    def test_witness_court_has_exact_positive_negative_correspondence(self):
        gates = {path.stem for path in (ROOT / "gates").glob("*.rq")}
        positive = {path.stem for path in (ROOT / "witnesses" / "pass").glob("*.ttl")}
        negative = {path.stem for path in (ROOT / "witnesses" / "fail").glob("*.ttl")}
        self.assertEqual(gates, positive)
        self.assertEqual(gates, negative)
        self.assertEqual(len(gates), 3)


if __name__ == "__main__":
    unittest.main()
