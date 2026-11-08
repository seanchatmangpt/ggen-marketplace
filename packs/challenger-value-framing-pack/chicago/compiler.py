"""
Challenger Commercial Teaching Choreography & Audit Compiler.
Produces the 6-stage pitch structure and 2-page Executive Consequence Audit.
"""

from dataclasses import dataclass
from typing import Dict, Any
from ontology import EnterpriseProfile, TargetSector, ExecutivePersona
from proofs import (
    ProofResult,
    prove_intermodal_per_diem_leak,
    prove_mechanics_lien_refi_default,
    prove_unhedged_trade_credit_drag,
    prove_split_custody_spoilage_exposure,
)

@dataclass(frozen=True)
class ChallengerPitch:
    warmer: str
    reframe: str
    rational_drowning: str
    emotional_impact: str
    new_way: str
    liquidation_kernel: str

@dataclass(frozen=True)
class ExecutiveConsequenceAudit:
    target_company: str
    persona: str
    sector: str
    jurisdiction: str
    total_dollar_drag: float
    proof: ProofResult
    pitch: ChallengerPitch

class ChallengerCompiler:
    @staticmethod
    def compile(profile: EnterpriseProfile) -> ExecutiveConsequenceAudit:
        params = profile.parameters
        
        if profile.sector == TargetSector.INTERMODAL_LOGISTICS:
            moves = params.get("annual_moves", 65000)
            proof = prove_intermodal_per_diem_leak(annual_moves=moves)
            warmer = (
                f"As a prominent carrier/3PL handling {moves:,} moves across CenterPoint Joliet, BNSF Logistics Park Chicago, "
                f"and UP Global IV, you have invested millions into modern TMS systems and telematics visibility."
            )
            reframe = (
                "Your container visibility platform is actively concealing a 6.2% EBITDA leak in contested demurrage "
                "and UIIA per-diem penalties at the rail yards, paying rail carriers on demand simply to avoid credit freezes."
            )
            rational_drowning = proof.mathematical_derivation
            emotional_impact = (
                f"Every month your logistics operators burn {proof.operational_falsifier} while {profile.persona.value} "
                f"approves over ${proof.annual_dollar_drag:,.2f} in non-recoverable line-item losses to keep trains rolling."
            )
            new_way = (
                "Move from retrospective 45-day invoice reconciliation to an automated, cryptographically timestamped "
                "pre-clearance net settlement network using Arcus Go/C-ABI zero-copy Arrow ingress that refuses payment for yard clock drift."
            )
            liquidation_kernel = (
                f"Deploy the UIIA Programmatic Netting Kernel backed by Arcus Arrow C Data Interface ({proof.substrate_claim.component}): "
                f"Zero-day dispute resolution, eliminating ${proof.annual_dollar_drag:,.2f} in annual leakage immediately."
            )

        elif profile.sector == TargetSector.INDUSTRIAL_CRE:
            val = params.get("portfolio_valuation", 250000000.0)
            debt = params.get("outstanding_senior_debt", 140000000.0)
            spend = params.get("annual_facility_spend", 15000000.0)
            proof = prove_mechanics_lien_refi_default(val, debt, spend)
            warmer = (
                f"Managing a ${val:,.0f} industrial CRE footprint across Cook and DuPage County with ${spend:,.0f} in annual "
                f"turnover and improvements requires coordination across dozens of general and specialty trade contractors."
            )
            reframe = (
                "Your automated facility dispatch platform exposes your property portfolio to unbonded 770 ILCS 60/ "
                "mechanic's liens, threatening non-monetary default across your senior debt refinance covenants."
            )
            rational_drowning = proof.mathematical_derivation
            emotional_impact = (
                "An uncollected $12,000 sub-tier HVAC or roofing invoice instantly clouds title under Illinois strict compliance. "
                "When your banking syndicate runs title for your refinance, a single unbonded lien accelerates the debt facility."
            )
            new_way = (
                "Eliminate manual paper lien waiver affidavits by coupling every progress draw payment directly to an "
                "atomic, cryptographically sealed statutory lien release under UCC § 3-311 using cgap Wide-SIMD tree hashing."
            )
            liquidation_kernel = (
                f"Deploy the 770 ILCS 60 Statutory Clearing Kernel powered by cgap-blake3 ({proof.substrate_claim.challenger_measurement}): "
                "Zero progress disbursements leave escrow without irrevocable cryptographic lien perfection. 100% title cloud elimination across all Cook County properties."
            )

        elif profile.sector == TargetSector.PARTS_FABRICATION:
            rev = params.get("annual_revenue", profile.annual_revenue)
            dso_actual = params.get("current_dso", 68.0)
            dso_contract = params.get("target_dso", 41.0)
            proof = prove_unhedged_trade_credit_drag(rev, dso_actual, dso_contract)
            warmer = (
                f"As a Midwest precision manufacturer delivering ${rev:,.0f}/year in parts to tier-1 automotive and industrial OEMs, "
                "your shop floor runs lean, precision machinery with ISO-certified tolerances."
            )
            reframe = (
                "Your Net-60 supplier terms are serving as an interest-free, unhedged subordinated loan to tier-1 assemblers "
                "who are intentionally delaying payments because your manual billing cannot enforce UCC priority."
            )
            rational_drowning = proof.mathematical_derivation
            emotional_impact = (
                f"You are locking up ${proof.annual_dollar_drag:,.2f} in annual debt carry cost to fund your customers' working capital. "
                "In an automotive bankruptcy, you sit as an unsecured general creditor with zero reclamation leverage."
            )
            new_way = (
                "Transition from passive receivables aging to programmatic UCC Article 2 purchase-money priority enforcement "
                "evaluated via cgap branchless SIMD quad predicates at 12.5 GB/s in-chain scan speeds."
            )
            liquidation_kernel = (
                f"Deploy the UCC Article 2/9 Liquidation Gateway driven by cgap-arrow ({proof.substrate_claim.speedup_ratio}): "
                f"Compresses DSO to net-scheduled wire releases. Reclaims ${proof.annual_dollar_drag:,.2f} in annual capital drag with zero new external debt."
            )

        elif profile.sector == TargetSector.COLD_CHAIN_DISTRIBUTION:
            rev = params.get("annual_cold_revenue", profile.annual_revenue)
            proof = prove_split_custody_spoilage_exposure(rev)
            warmer = (
                f"Distributing ${rev:,.0f}/yr in temperature-sensitive food and pharmaceuticals through Chicago's cold corridor "
                "requires rigorous FSMA compliance and continuous telematics monitoring."
            )
            reframe = (
                "Your standard vendor indemnities are legally unenforceable under Illinois tort law when temperature spoilage "
                "occurs across split-custody transport, creating a multi-million-dollar forensic discovery trap."
            )
            rational_drowning = proof.mathematical_derivation
            emotional_impact = (
                "When a $80k reefer load spoils after a cross-dock dwell, carriers and warehouse operators spend $250k in forensic "
                "discovery and expert witnesses. You write off the loss because the telemetry log is legally inadmissible."
            )
            new_way = (
                "Establish continuous, self-authenticating electronic chains-of-custody satisfying Federal Rule of Evidence 902(14) "
                "using Smalt AoQ UDP telematics ingest (<=128 B/op heap allocation) paired with cgap-blake3 tree hashes."
            )
            liquidation_kernel = (
                f"Deploy the Smalt + cgap Cryptographic Telematics Engine ({proof.substrate_claim.speedup_ratio}): "
                f"Compress dispute resolution from 9 months to 4 seconds, recovering ${proof.annual_dollar_drag:,.2f} in contested spoilage and forensic legal expenses."
            )
        else:
            raise ValueError(f"Unsupported sector: {profile.sector}")

        pitch = ChallengerPitch(
            warmer=warmer,
            reframe=reframe,
            rational_drowning=rational_drowning,
            emotional_impact=emotional_impact,
            new_way=new_way,
            liquidation_kernel=liquidation_kernel
        )

        return ExecutiveConsequenceAudit(
            target_company=profile.company_name,
            persona=profile.persona.value,
            sector=profile.sector.value,
            jurisdiction=", ".join(profile.county_footprint) + " (Illinois)",
            total_dollar_drag=proof.annual_dollar_drag,
            proof=proof,
            pitch=pitch
        )
