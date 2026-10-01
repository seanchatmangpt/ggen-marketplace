"""Lane-7 tests for packs/evidence-capability-pack (witness court + real-ggen surface)."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.check_gate_witness_courts import qualify

PACK = Path(__file__).parents[1] / "packs" / "evidence-capability-pack"
VERIFY = PACK / "qualification" / "verify.py"

GATES = (
    "010_pinned_capability_identity",
    "020_capability_contract_complete",
    "030_capability_without_realization",
    "040_realization_without_qualification",
    "050_receipt_missing_field",
    "060_evidence_unbound_to_subject",
)


class EvidenceCapabilityPackTests(unittest.TestCase):
    def test_witness_court_runner_admits(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VERIFY)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"verify.py refused:\nstdout={result.stdout}\nstderr={result.stderr}",
        )
        self.assertIn("ADMITTED", result.stdout)

    def test_gate_witness_court_structure_is_alive(self) -> None:
        record = qualify(PACK)
        self.assertEqual(record["standing"], "ALIVE")
        self.assertEqual(record["case_count"], len(GATES))

    def test_pinned_capability_ids_present(self) -> None:
        ontology = (PACK / "ontology.ttl").read_text(encoding="utf-8")
        for pinned in (
            "Evidence.Establish",
            "Evidence.Bind",
            "Receipt.Sign",
            "Provenance.Record",
        ):
            self.assertIn(f'"{pinned}"', ontology)

    def test_receipt_law_reuses_qce_not_redefines(self) -> None:
        ontology = (PACK / "ontology.ttl").read_text(encoding="utf-8")
        for reused in ("qce:QualificationReceipt", "qce:subjectCommit", "qce:consequenceDigest"):
            self.assertIn(reused, ontology)
        self.assertNotIn("ecap:QualificationReceipt a", ontology)

    def test_no_shapes_ttl_and_manifest_keys(self) -> None:
        self.assertFalse((PACK / "shapes.ttl").exists(), "FM-PACK-012: no shapes.ttl")
        manifest = (PACK / "pack.toml").read_text(encoding="utf-8")
        self.assertIn("name =", manifest)
        self.assertIn("version =", manifest)
        self.assertIn("description =", manifest)


if __name__ == "__main__":
    unittest.main()
