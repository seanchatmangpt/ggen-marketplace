"""Lane-6 tests for packs/capability-ecology-pack (witness court + real-ggen surface)."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.check_gate_witness_courts import qualify

PACK = Path(__file__).parents[1] / "packs" / "capability-ecology-pack"
VERIFY = PACK / "qualification" / "verify.py"


class A2aCapabilityPackTests(unittest.TestCase):
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
        self.assertGreaterEqual(record["case_count"], 5)  # merged pack: one court, 59 cases

    def test_pinned_capability_ids_present(self) -> None:
        ontology = (PACK / "ontology/a2a.ttl").read_text(encoding="utf-8")
        for pinned in ("A2A.Invoke", "A2A.Discover", "A2A.Await"):
            self.assertIn(f'"{pinned}"', ontology)

    def test_no_shapes_ttl_and_manifest_keys(self) -> None:
        self.assertFalse((PACK / "shapes.ttl").exists(), "FM-PACK-012: no shapes.ttl")
        manifest = (PACK / "pack.toml").read_text(encoding="utf-8")
        self.assertIn("name =", manifest)
        self.assertIn("version =", manifest)
        self.assertIn("description =", manifest)


if __name__ == "__main__":
    unittest.main()
