"""
Automated Verification Suite for the Chicago Challenger Sales Engine.
Asserts mathematical precision, statutory alignment, and byte-level determinism.
"""

import unittest
import hashlib
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ontology import (
    EnterpriseProfile,
    TargetSector,
    ExecutivePersona,
    StatutoryPinch,
    ConstructiveTension
)
from proofs import (
    prove_intermodal_per_diem_leak,
    prove_mechanics_lien_refi_default,
    prove_unhedged_trade_credit_drag,
    prove_split_custody_spoilage_exposure
)
from compiler import ChallengerCompiler
from cli import format_audit_markdown

class TestChicagoChallengerEngine(unittest.TestCase):

    def test_intermodal_per_diem_proof(self):
        proof = prove_intermodal_per_diem_leak(annual_moves=50000)
        self.assertGreater(proof.annual_dollar_drag, 500000.0)
        self.assertIn("UIIA Standard Agreement", proof.statutory_basis)
        self.assertIn("CenterPoint Joliet", proof.operational_falsifier)

    def test_mechanics_lien_refi_default_proof(self):
        proof = prove_mechanics_lien_refi_default(
            portfolio_valuation=100000000.0,
            outstanding_senior_debt=60000000.0,
            annual_facility_spend=10000000.0
        )
        self.assertGreater(proof.annual_dollar_drag, 200000.0)
        self.assertIn("770 ILCS 60", proof.statutory_basis)
        self.assertIn("UCC § 3-311", proof.statutory_basis)

    def test_unhedged_trade_credit_drag_proof(self):
        proof = prove_unhedged_trade_credit_drag(
            annual_revenue=50000000.0,
            current_dso=68.0,
            target_dso=41.0
        )
        # 50,000,000 / 365 * 27 * 0.0875 = 323630.13698...
        self.assertAlmostEqual(proof.annual_dollar_drag, 323630.14, places=1)
        self.assertIn("UCC §§ 2-702", proof.statutory_basis)

    def test_split_custody_spoilage_proof(self):
        proof = prove_split_custody_spoilage_exposure(annual_cold_revenue=40000000.0)
        self.assertGreater(proof.annual_dollar_drag, 500000.0)
        self.assertIn("Federal Rules of Evidence 902(14)", proof.statutory_basis)

    def test_deterministic_compilation_byte_identity(self):
        """Ensures that identical inputs yield byte-identical outputs across repeated compilations."""
        prof = EnterpriseProfile(
            company_name="Test Joliet Logistics",
            sector=TargetSector.INTERMODAL_LOGISTICS,
            persona=ExecutivePersona.VP_SUPPLY_CHAIN_OPS,
            statutory_pinch=StatutoryPinch.UIIA_PER_DIEM,
            constructive_tension=ConstructiveTension.HIDDEN_EBITDA_LEAK,
            annual_revenue=80000000.0,
            county_footprint=["Will County"],
            parameters={"annual_moves": 40000}
        )
        audit1 = ChallengerCompiler.compile(prof)
        md1 = format_audit_markdown(audit1)
        hash1 = hashlib.sha256(md1.encode("utf-8")).hexdigest()

        audit2 = ChallengerCompiler.compile(prof)
        md2 = format_audit_markdown(audit2)
        hash2 = hashlib.sha256(md2.encode("utf-8")).hexdigest()

        self.assertEqual(hash1, hash2, "Compilation must be strictly deterministic and byte-identical")

if __name__ == "__main__":
    unittest.main()
