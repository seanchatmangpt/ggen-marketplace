"""F5 qualification ladder mechanized: one fixture graph per gate, run with rdflib.

Stage fixtures are synthetic (example.invalid IRIs), following the
industry-closure-ledger-pack fixtures/closure-growth precedent. Each stage-N
fixture is asserted to PASS its own gate (zero rows) and to PASS the
whole-ladder monotonicity gate (100); a skip-stage fixture must FIRE the
monotonicity violation. Zero rows = pass (house idiom).

Run: pytest packs/fortune5-enterprise-architecture-pack/tests/test_qualification_ladder.py -v
"""

from pathlib import Path

import pytest
from rdflib import Graph

PACK = Path(__file__).resolve().parents[1]
QUERIES = PACK / "queries"

GATES = {
    0: "010-stage0-closure.rq",
    1: "020-stage1-contract-pending.rq",
    2: "030-stage2-contract-approved.rq",
    3: "040-stage3-sbb-candidate.rq",
    4: "050-stage4-qualified-no-evidence.rq",
    5: "060-stage5-terminal.rq",
}

REASONS = {
    0: "REFUSED:F5_STAGE0_ABB_DEFICIT_UNRECORDED",
    1: "REFUSED:F5_STAGE1_CONTRACT_PENDING_UNREASONED",
    2: "REFUSED:F5_STAGE2_APPROVAL_UNATTRIBUTED",
    3: "REFUSED:F5_STAGE3_CANDIDATE_UNRECORDED",
    4: "REFUSED:F5_STAGE4_QUALIFIED_UNRECORDED",
    5: "REFUSED:F5_STAGE5_FRONTIER_UNRECORDED",
}

PIN = "sha256:" + "58fb837c25362a6184fa830bd12225cf3ac5f2b7274cdde66f66611962b892e2"

PREFIXES = """\
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ic: <https://seanchatmangpt.github.io/packs/industry-closure-ledger-pack#> .
@prefix ea: <https://chatman.ai/ontology/enterprise-architecture#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix ex: <https://example.invalid/synthetic/> .
"""

# Shared scaffolding: closure, head snapshot, source, capability, requirement.
# The head snapshot / coverage triples are inert on stages 0-4 (no gate reads
# them unless evidence exists).
SCAFFOLD = """
ex:closure a ic:IndustryClosure ;
    ic:industryScope "synthetic bounded scope for ladder fixtures" ;
    ic:hasSnapshot ex:snap0 .

ex:snap0 a ic:ClosureSnapshot ;
    ic:snapshotOf ex:closure ;
    ic:epoch 0 .

ex:srcA a ic:KnowledgeSource ;
    ic:admission ic:ADMITTED ;
    ic:sourceIri <https://example.invalid/source/a> ;
    ic:sourceVersion "1.0.0" ;
    ic:sourceDigest "sha256:c2922945bce9302c46fb563eb14f55a7d5fa796bcb3a229c49e9013ccc4e04bc" ;
    ic:licenseBoundary "synthetic test source" ;
    ic:sourceLocator "ontologies/public/synthetic/a.ttl" ;
    ic:providesConcept <https://example.invalid/concept/A> .

ex:agentBuilder a prov:Agent .
ex:agentVerifier a prov:Agent .
ex:humanApprover a prov:Agent .

ex:capA a ea:Capability ;
    ic:capabilityKey "CAP-A" ;
    ic:groundedIn ex:srcA ;
    ic:concept <https://example.invalid/concept/A> .

ex:reqA a ic:Requirement ;
    ic:requirementId "REQ-A" ;
    ic:statement "Synthetic requirement A stated in paraphrase." ;
    ic:inClosure ex:closure ;
    ic:disposition ic:IN_SCOPE ;
    ic:requiresCapability ex:capA ;
    ic:derivedFrom ex:srcA .
"""

# Contract at PENDING with authorityClaim "NONE" (stage-1 lawful state).
CONTRACT_PENDING = """
ex:abbA a ea:ArchitectureBuildingBlock ;
    ea:realizesCapability ex:capA ;
    ea:governedByContract ex:kA .

ex:kA a ea:ArchitectureContract ;
    ic:approvalStatus ic:PENDING_HUMAN_APPROVAL ;
    ic:authorityClaim "NONE" .
"""

# Contract APPROVED with attributed human approver + receipt (stage-2 lawful
# state, and the preconditions stages 3-5 need).
CONTRACT_APPROVED = """
ex:abbA a ea:ArchitectureBuildingBlock ;
    ea:realizesCapability ex:capA ;
    ea:governedByContract ex:kA .

ex:kA a ea:ArchitectureContract ;
    ic:approvalStatus ic:APPROVED ;
    ic:approvedBy ex:humanApprover ;
    ic:approvalReceipt "receipt:A-approval" ;
    ic:authorityClaim "NONE" .
"""

SBB_CANDIDATE = """
ex:sbbA a ea:SolutionBuildingBlock ;
    ea:satisfiesABB ex:abbA ;
    ea:hasStanding ea:CANDIDATE .
"""

SBB_QUALIFIED = """
ex:sbbA a ea:SolutionBuildingBlock ;
    ea:satisfiesABB ex:abbA ;
    ea:hasStanding ea:QUALIFIED ;
    ea:exactSubject "%s" .
""" % PIN

# Independent, VERIFIED, OBSERVED-kind evidence at the pinned subject, plus a
# LIVE coverage row in the head snapshot (stage-5 terminal state).
EVIDENCE_LIVE = """
ex:evA a ic:ExecutionEvidence ;
    ic:evidenceFor ex:sbbA ;
    ic:evidenceSubject "%s" ;
    ic:outcome ic:VERIFIED ;
    ic:receiptDigest "sha256:59bdd6b610a72ed789b8cdd0524817c91d42f77b083a101baaec2e47f891b48d" ;
    ic:producedBy ex:agentBuilder ;
    ic:verifiedBy ex:agentVerifier ;
    ic:evidenceKind ic:OBSERVED .

ex:snap0 ic:covers [
    a ic:Coverage ;
    ic:inSnapshot ex:snap0 ;
    ic:coversCapability ex:capA ;
    ic:byABB ex:abbA ;
    ic:bySBB ex:sbbA ;
    ic:coverageState ic:LIVE
] .
""" % PIN

# Open residual per stage: the recorded reason the ladder legitimately sits at
# stage N (e.g. stage0 = DEFICIT_ABB open, stage3 = DEFICIT_QUALIFICATION open).
RESIDUALS = {
    0: """
ex:resA a ic:Residual ;
    ic:residualOf ex:reqA ;
    ic:deficitClass ic:DEFICIT_ABB ;
    ic:status "OPEN" ;
    ic:authorityClaim "NONE" ;
    ic:feedbackTarget ic:UPSTREAM_ARCHITECTURE .
""",
    1: """
ex:resA a ic:Residual ;
    ic:residualOf ex:reqA ;
    ic:deficitClass ic:DEFICIT_CONTRACT ;
    ic:status "OPEN" ;
    ic:authorityClaim "NONE" ;
    ic:feedbackTarget ic:UPSTREAM_ARCHITECTURE .
""",
    2: """
ex:resA a ic:Residual ;
    ic:residualOf ex:reqA ;
    ic:deficitClass ic:DEFICIT_SBB ;
    ic:status "OPEN" ;
    ic:authorityClaim "NONE" ;
    ic:feedbackTarget ic:UPSTREAM_ARCHITECTURE .
""",
    3: """
ex:resA a ic:Residual ;
    ic:residualOf ex:reqA ;
    ic:deficitClass ic:DEFICIT_QUALIFICATION ;
    ic:status "OPEN" ;
    ic:authorityClaim "NONE" ;
    ic:feedbackTarget ic:UPSTREAM_QUALIFICATION .
""",
    4: """
ex:resA a ic:Residual ;
    ic:residualOf ex:reqA ;
    ic:deficitClass ic:DEFICIT_EVIDENCE ;
    ic:status "OPEN" ;
    ic:authorityClaim "NONE" ;
    ic:feedbackTarget ic:UPSTREAM_QUALIFICATION .
""",
}


def _stage_fixture(stage: int) -> str:
    parts = [PREFIXES, SCAFFOLD]
    if stage == 0:
        pass
    elif stage == 1:
        parts.append(CONTRACT_PENDING)
    elif stage in (2, 3, 4, 5):
        parts.append(CONTRACT_APPROVED)
    if stage == 3:
        parts.append(SBB_CANDIDATE)
    if stage in (4, 5):
        parts.append(SBB_QUALIFIED)
    if stage == 5:
        parts.append(EVIDENCE_LIVE)
    if stage in RESIDUALS:
        parts.append(RESIDUALS[stage])
    return "\n".join(parts)


# Skip-stage fixture: the residual claims DEFICIT_EVIDENCE (stage-4 terminal
# deficit) while the chain has no ABB at all -> F5_LADDER_REGRESSION must fire.
SKIP_STAGE_FIXTURE = PREFIXES + SCAFFOLD + """
ex:resA a ic:Residual ;
    ic:residualOf ex:reqA ;
    ic:deficitClass ic:DEFICIT_EVIDENCE ;
    ic:status "OPEN" ;
    ic:authorityClaim "NONE" ;
    ic:feedbackTarget ic:UPSTREAM_QUALIFICATION .
"""


def build_graph(ttl: str) -> Graph:
    g = Graph()
    g.parse(data=ttl, format="turtle")
    return g


def run_gate(graph: Graph, query_file: str) -> list:
    query = (QUERIES / query_file).read_text()
    return list(graph.query(query))


class TestStageGates:
    @pytest.mark.parametrize("stage", range(6))
    def test_stage_n_fixture_passes_its_own_gate(self, stage):
        rows = run_gate(build_graph(_stage_fixture(stage)), GATES[stage])
        assert rows == [], (
            f"stage {stage} fixture must pass gate {GATES[stage]} "
            f"(zero rows), got: {[(str(r)) for r in rows]}"
        )

    @pytest.mark.parametrize("stage", range(6))
    def test_stage_refusal_reasons_are_distinct(self, stage):
        """Each gate binds exactly one refusal family; the fixture documents it."""
        assert REASONS[stage] in (QUERIES / GATES[stage]).read_text()


class TestMonotonicity:
    @pytest.mark.parametrize("stage", range(6))
    def test_monotonicity_gate_passes_each_lawful_stage(self, stage):
        rows = run_gate(
            build_graph(_stage_fixture(stage)), "100-ladder-monotonicity.rq"
        )
        assert rows == [], f"lawful stage {stage} must not trip monotonicity: {rows}"

    def test_skip_stage_fixture_fires_regression(self):
        rows = run_gate(build_graph(SKIP_STAGE_FIXTURE), "100-ladder-monotonicity.rq")
        assert len(rows) > 0, "skip-stage fixture must fire F5_LADDER_REGRESSION"
        assert all(
            "REFUSED:F5_LADDER_REGRESSION" in str(row) for row in rows
        ), f"unexpected reasons: {rows}"
