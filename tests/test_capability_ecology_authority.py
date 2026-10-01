"""Lane-7 tests for packs/capability-ecology-pack (witness court + real-ggen surface)."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.check_gate_witness_courts import qualify

PACK = Path(__file__).parents[1] / "packs" / "capability-ecology-pack"
VERIFY = PACK / "qualification" / "verify.py"

GATES = (
    "authcap_010_pinned_capability_identity",
    "authcap_020_capability_contract_complete",
    "authcap_030_capability_without_realization",
    "authcap_040_realization_without_qualification",
    "authcap_050_actuation_without_envelope",
    "authcap_060_grant_without_authority",
    "authcap_070_no_authority_increase",
)


class AuthorityCapabilityPackTests(unittest.TestCase):
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
        self.assertIn("ALIVE", result.stdout)

    def test_gate_witness_court_structure_is_alive(self) -> None:
        record = qualify(PACK)
        self.assertEqual(record["standing"], "ALIVE")
        self.assertGreaterEqual(record["case_count"], len(GATES))  # merged pack: one court, 59 cases

    def test_pinned_capability_ids_present(self) -> None:
        ontology = (PACK / "ontology/authority.ttl").read_text(encoding="utf-8")
        for pinned in ("Authority.Verify", "Authority.Grant", "Actuation.Execute"):
            self.assertIn(f'"{pinned}"', ontology)

    def test_consequential_pinned_ids_declared_in_namespace(self) -> None:
        ontology = (PACK / "ontology/authority.ttl").read_text(encoding="utf-8")
        self.assertIn(
            "https://ggen.dev/ontology/authority-capability#", ontology,
            "pinned namespace missing",
        )

    def test_no_shapes_ttl_and_manifest_keys(self) -> None:
        self.assertFalse((PACK / "shapes.ttl").exists(), "FM-PACK-012: no shapes.ttl")
        manifest = (PACK / "pack.toml").read_text(encoding="utf-8")
        self.assertIn("name =", manifest)
        self.assertIn("version =", manifest)
        self.assertIn("description =", manifest)


if __name__ == "__main__":
    unittest.main()
