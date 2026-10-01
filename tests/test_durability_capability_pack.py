"""Adversarial court for packs/durability-capability-pack (lane 5, v26.9.30).

Nothing is stubbed: every case runs the pack's real gates through a real SPARQL
engine (rdflib) or the real court subprocess over real Turtle. Each negative
fixture must be refused by exactly its declared gates -- a vacuous gate (fires
nowhere) and an over-firing court (fires everywhere) both fail here.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "durability-capability-pack"
QUALIFICATION = PACK / "qualification"
DCAP = "https://ggen.dev/ontology/durability-capability#"
QCE = "https://ggen.dev/ontology/qualified-capability-ecology#"


def _load_verify():
    spec = importlib.util.spec_from_file_location("dcap_verify", QUALIFICATION / "verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify = _load_verify()

POSITIVE = QUALIFICATION / "fixtures" / "positive.ttl"


class GateCourtProcessTests(unittest.TestCase):
    def test_court_process_exits_zero_and_reports_alive(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(QUALIFICATION / "verify.py")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual(payload["standing"], "ALIVE")
        self.assertEqual(payload["gate_count"], 7)
        self.assertEqual(payload["negative_fixture_count"], 8)
        self.assertEqual(payload["case_count"], 15)

    def test_every_gate_has_order_by(self) -> None:
        # real-ggen E0013: multi-row SPARQL needs ORDER BY -- enforced statically so
        # the refusal surface never becomes nondeterministic.
        for gate in verify.gates():
            self.assertIn("ORDER BY", gate.read_text(encoding="utf-8"), gate.name)

    def test_pack_table_admits_only_name_version_description(self) -> None:
        # FM-PACK-003: the real ggen [pack] loader admits exactly these keys.
        import tomllib
        manifest = tomllib.loads((PACK / "pack.toml").read_text(encoding="utf-8"))
        self.assertEqual(sorted(manifest), ["pack"])
        self.assertEqual(sorted(manifest["pack"]), ["description", "name", "version"])

    def test_no_symlinks_under_pack(self) -> None:
        for path in PACK.rglob("*"):
            self.assertFalse(path.is_symlink(), path)


class FixtureExactnessTests(unittest.TestCase):
    def test_positive_fixture_is_gate_clean(self) -> None:
        self.assertEqual(verify.refusing_gates(verify.load_graph(POSITIVE)), {})

    def test_each_negative_fires_exactly_its_declared_gates(self) -> None:
        for fixture_name, expected in verify.NEGATIVE_EXPECTATIONS.items():
            fired = set(verify.refusing_gates(verify.load_graph(QUALIFICATION / "fixtures" / fixture_name)))
            self.assertEqual(fired, expected, fixture_name)

    def test_expectation_matrix_covers_every_gate(self) -> None:
        covered = set().union(*verify.NEGATIVE_EXPECTATIONS.values())
        self.assertEqual(covered, {gate.name for gate in verify.gates()})


def _positive_graph() -> Graph:
    return verify.load_graph(POSITIVE)


class AdversarialMutationTests(unittest.TestCase):
    """Each mutation of the conforming fixture must hit exactly the gate owning the violated law."""

    def assert_fires_exactly(self, graph: Graph, *gate_names: str) -> None:
        self.assertEqual(set(verify.refusing_gates(graph)), set(gate_names))

    def test_conforming_fixture_is_admitted(self) -> None:
        self.assert_fires_exactly(_positive_graph())

    def test_removing_checkpoint_state_digest_fires_content_identity_gate(self) -> None:
        from rdflib import URIRef
        graph = _positive_graph()
        checkpoint = URIRef(DCAP + "cp-onboarding-1")
        digest = URIRef(QCE + "closureDigest")
        graph.remove((checkpoint, digest, None))
        self.assert_fires_exactly(graph, "030_checkpoint_without_subject_digest.rq")

    def test_disabling_byte_identical_requirement_fires_determinism_gate(self) -> None:
        from rdflib import Literal, URIRef
        graph = _positive_graph()
        contract = URIRef(DCAP + "determinism-byte-identical")
        graph.remove((contract, URIRef(DCAP + "byteIdenticalRequired"), None))
        graph.add((contract, URIRef(DCAP + "byteIdenticalRequired"), Literal(False)))
        self.assert_fires_exactly(graph, "040_replay_without_determinism_evidence.rq")

    def test_revoking_the_requalification_receipt_fires_version_boundary_gate(self) -> None:
        from rdflib import URIRef
        graph = _positive_graph()
        resume = URIRef(DCAP + "rc-migration-requalified")
        graph.remove((resume, URIRef(DCAP + "requalificationReceipt"), None))
        self.assert_fires_exactly(graph, "050_resume_across_version_without_requalification.rq")

    def test_silently_resuming_a_halted_workflow_fires_authority_gap_gate(self) -> None:
        from rdflib import URIRef
        graph = _positive_graph()
        resume = URIRef(DCAP + "rc-onboarding-resume")
        envelope = URIRef(DCAP + "env-resume-1")
        graph.remove((resume, URIRef(DCAP + "authorityEnvelope"), envelope))
        graph.remove((envelope, None, None))
        self.assert_fires_exactly(graph, "060_authority_gap_unmodeled_on_halt.rq")

    def test_closing_the_resume_outcome_enum_removes_vacuity(self) -> None:
        """The enum check must keep refusing: mutating the positive outcome to an
        undeclared value fires exactly gate 010 (the anti-vacuity proof for the
        third check of that gate)."""
        from rdflib import Literal, URIRef
        graph = _positive_graph()
        resume = URIRef(DCAP + "rc-onboarding-resume")
        graph.remove((resume, URIRef(DCAP + "resumeOutcome"), None))
        graph.add((resume, URIRef(DCAP + "resumeOutcome"), Literal("MAYBE")))
        self.assert_fires_exactly(graph, "010_required.rq")


if __name__ == "__main__":
    unittest.main()
