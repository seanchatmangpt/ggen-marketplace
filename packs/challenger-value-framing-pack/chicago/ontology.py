"""
Orthogonal Vector Space for Chicago Enterprise Challenger Sales.
Formalizes: M_Challenger = T_Archetype (x) I_TargetSector (x) S_StatutoryPinch (x) R_ConstructiveTension
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List

class ExecutivePersona(str, Enum):
    CFO = "Chief Financial Officer (Cash/Working Capital)"
    VP_SUPPLY_CHAIN_OPS = "VP of Supply Chain / Operations (Throughput/Dwell Time)"
    COO = "Chief Operating Officer"
    GENERAL_COUNSEL = "General Counsel / Risk VP (Lien/Regulatory Exposure)"
    OWNER_CFO = "Owner / CFO (Equity & Subordinated Debt Exposure)"

class TargetSector(str, Enum):
    INTERMODAL_LOGISTICS = "Intermodal Logistics (Joliet/Elwood)"
    INDUSTRIAL_CRE = "Multi-Facility Industrial CRE (Cook Co.)"
    PARTS_FABRICATION = "Middle-Market Metal/Parts Fabricators"
    COLD_CHAIN_DISTRIBUTION = "Food Processing / Cold Chain Distribution"

class StatutoryPinch(str, Enum):
    UIIA_PER_DIEM = "Freight Per Diem / UIIA Intermodal Arbitration"
    MECHANICS_LIEN_770_ILCS_60 = "Illinois Mechanic's Lien Act (770 ILCS 60/)"
    UCC_ARTICLE_2_9 = "UCC Article 2 & 9 Consignment, Purchase-Money Priority & Perfection"
    FRE_902_14_TORT = "Split-Custody Tort Liability & FRE 902(14) Electronic Authentication"
    COOK_COUNTY_CLASS_6B_8 = "Cook County Class 6b/8 Property Tax Assessment & Covenant Exposure"

class ConstructiveTension(str, Enum):
    HIDDEN_EBITDA_LEAK = "Hidden Balance-Sheet Drag (Unasserted Offsets & Leakage)"
    DOWNSTREAM_CARRIER_RISK = "Unmitigated Downstream Carrier Risk & Split-Custody Spoilage"
    MANUAL_EXCEPTION_OVERHEAD = "Manual Exception Overhead (>4% Gross Revenue)"
    UNBONDED_LIEN_DEFAULT = "Unbonded Mechanics Lien Default on Primary CRE Bank Debt"
    SUBORDINATED_FLOAT = "Interest-Free Subordinated Floating Debt to Tier-1 Assemblers"

@dataclass(frozen=True)
class EnterpriseProfile:
    company_name: str
    sector: TargetSector
    persona: ExecutivePersona
    statutory_pinch: StatutoryPinch
    constructive_tension: ConstructiveTension
    annual_revenue: float
    county_footprint: List[str]
    parameters: Dict[str, Any]
