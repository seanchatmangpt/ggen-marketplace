#!/usr/bin/env python3
"""Courts for composition-solver-pack.

Chicago style: the real pack source on disk, the real gate court (rdflib), and, when a
real ggen binary is present, real manufacture in an isolated copy. Without a binary the
ggen-dependent cases are skipped with standing BLOCKED:ggen_binary_unavailable; nothing
here is promoted to ALIVE by a proxy.

The "known limit" tests pin behavior that the tracked sJira tickets (see
docs/reference/composition-solver-contract.md) say is NOT yet solved. If one of them starts
failing because the limit was fixed, update the ticket and the test together.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "composition-solver-pack"
PREFIXES = (
    "@prefix p: <https://seanchatmangpt.github.io/packs/composition-solver-pack#> .\n"
    "@prefix b: <https://seanchatmangpt.github.io/packs/composition-solver-pack/basis#> .\n"
)


def ggen_binary() -> str | None:
    explicit = os.environ.get("GGEN_BIN")
    if explicit and Path(explicit).is_file():
        return explicit
    return shutil.which("ggen")


GGEN = ggen_binary()
needs_ggen = unittest.skipUnless(GGEN, "BLOCKED:ggen_binary_unavailable")


class Manufacture:
    """An isolated copy of the pack with a chosen requirement set and basis edits."""

    def __init__(self, extra_basis: str = "", extra_requirements: str = "", basis_edit=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "pack"
        shutil.copytree(PACK, self.root)
        demo = (self.root / "fixtures" / "demo-requirements.ttl").read_text(encoding="utf-8")
        (self.root / "ontology" / "requirements.ttl").write_text(
            demo + "\n" + extra_requirements, encoding="utf-8"
        )
        basis = self.root / "ontology" / "basis.ttl"
        text = basis.read_text(encoding="utf-8")
        if basis_edit:
            text = basis_edit(text)
        basis.write_text(text + "\n" + extra_basis, encoding="utf-8")

    def sync(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [GGEN, "sync", "run"], cwd=self.root, capture_output=True, text=True, timeout=120
        )

    def rows(self, name: str) -> list[dict]:
        path = self.root / "generated" / "composition-solver" / name
        return json.loads(path.read_text(encoding="utf-8"))["rows"]

    def close(self) -> None:
        self.tmp.cleanup()


class GateCourt(unittest.TestCase):
    def test_every_gate_refuses_its_fail_witness_and_admits_its_pass_witness(self):
        done = subprocess.run(
            [sys.executable, "qualification/verify.py"], cwd=PACK, capture_output=True, text=True
        )
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        payload = json.loads(done.stdout)
        self.assertEqual(payload["standing"], "ALIVE")
        self.assertEqual(payload["case_count"], 4)
        for case in payload["cases"]:
            self.assertEqual(case["pass_rows"], 0, case)
            self.assertGreater(case["fail_rows"], 0, case)

    def test_ontology_declares_no_do_vocabulary(self):
        text = (PACK / "ontology.ttl").read_text(encoding="utf-8")
        self.assertNotIn("p:DO", text)
        self.assertNotIn("DoAuthority", text)

    def test_every_gate_is_wired_into_sync(self):
        import tomllib

        manifest = tomllib.loads((PACK / "ggen.toml").read_text(encoding="utf-8"))
        wired = {Path(g).name for g in manifest["validation"]["gates"]}
        shipped = {g.name for g in (PACK / "gates").glob("*.rq")}
        self.assertEqual(wired, shipped)

    def test_every_inference_stage_is_ordered_for_strict_mode(self):
        import tomllib

        manifest = tomllib.loads((PACK / "ggen.toml").read_text(encoding="utf-8"))
        for rule in manifest["inference"]["rules"]:
            self.assertIn("ORDER BY", rule["construct"], rule["name"])


@needs_ggen
class RealManufacture(unittest.TestCase):
    def test_demo_cover_residual_and_authority_fence(self):
        m = Manufacture()
        self.addCleanup(m.close)
        done = m.sync()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        status = {r["requirement"]: r["status"] for r in m.rows("coverage.json")}
        self.assertEqual(
            status,
            {"REQ-1": "COVERED", "REQ-2": "BLOCKED_AUTHORITY", "REQ-3": "UNCOVERED"},
        )
        classes = {r["authorityClass"] for r in m.rows("selected-atoms.json")}
        self.assertNotIn("DO", classes)
        self.assertEqual(
            {r["atom"] for r in m.rows("selected-atoms.json")},
            {"knowledge-admission", "residual-computation", "workorder-projection", "feedback-routing"},
        )

    def test_replay_is_byte_identical(self):
        m = Manufacture()
        self.addCleanup(m.close)
        self.assertEqual(m.sync().returncode, 0)
        out = m.root / "generated" / "composition-solver"
        first = {p.name: p.read_bytes() for p in out.glob("*.json")}
        again = m.sync()
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertEqual(first, {p.name: p.read_bytes() for p in out.glob("*.json")})
        fresh = Manufacture()
        self.addCleanup(fresh.close)
        self.assertEqual(fresh.sync().returncode, 0)
        out2 = fresh.root / "generated" / "composition-solver"
        self.assertEqual(first, {p.name: p.read_bytes() for p in out2.glob("*.json")})

    def test_depth_beyond_stage_bound_is_refused_not_missed(self):
        m = Manufacture(
            extra_basis=PREFIXES
            + 'b:p5 a p:Proposition ; p:propId "p5" .\n'
            + 'b:atom-extra a p:CapabilityAtom ; p:atomId "extra" ; p:fromPack "x" ;'
            + ' p:authorityClass "SELECT" ; p:requires b:residual-feedback-routed ; p:provides b:p5 .\n',
            extra_requirements=PREFIXES + '<urn:x:r> a p:Requirement ; p:reqId "REQ-9" ; p:needs b:p5 .\n',
        )
        self.addCleanup(m.close)
        done = m.sync()
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("FM-LAW-018", done.stdout + done.stderr)
        self.assertIn("stage bound", done.stdout + done.stderr)

    def test_known_limit_L2_authority_class_is_self_declared(self):
        m = Manufacture(
            basis_edit=lambda t: t.replace('p:authorityClass "DO"', 'p:authorityClass "CONSTRUCT"')
        )
        self.addCleanup(m.close)
        self.assertEqual(m.sync().returncode, 0)
        status = {r["requirement"]: r["status"] for r in m.rows("coverage.json")}
        # Tracked as ticket SJ-CSP-002: a mislabeled DO atom is not detected.
        self.assertEqual(status["REQ-2"], "COVERED")

    def test_known_limit_L3_no_selection_among_alternative_providers(self):
        m = Manufacture(
            extra_basis=PREFIXES
            + 'b:atom-alt a p:CapabilityAtom ; p:atomId "feedback-routing-alt" ; p:fromPack "alt-pack" ;'
            + ' p:authorityClass "CONSTRUCT" ; p:requires b:workorder-projected ;'
            + " p:provides b:residual-feedback-routed .\n"
        )
        self.addCleanup(m.close)
        self.assertEqual(m.sync().returncode, 0)
        atoms = {r["atom"] for r in m.rows("selected-atoms.json") if r["requirement"] == "REQ-1"}
        # Tracked as ticket SJ-CSP-003: both providers are returned; nothing chooses or ranks.
        self.assertIn("feedback-routing", atoms)
        self.assertIn("feedback-routing-alt", atoms)


class VisionBasisGap(unittest.TestCase):
    def test_known_limit_L5_vision_2030_capabilities_carry_no_dependency_data(self):
        text = (ROOT / "packages" / "vision-2030-capability-generator" / "ontology.ttl").read_text(
            encoding="utf-8"
        )
        self.assertGreaterEqual(text.count("a v30:Capability "), 50)
        # Tracked as ticket SJ-CSP-005: no provides/requires edges exist to compose over.
        for edge in ("v30:requires", "v30:provides", "v30:dependsOn"):
            self.assertNotIn(edge, text)


if __name__ == "__main__":
    unittest.main()
