"""TV-01..TV-05 black-box conformance vectors (dissertation conformance court).

Real collaborators: the pack's real SPARQL gates (queries/*.rq) executed by
real rdflib against fixture graphs built from the pack's f5ea:/ea: vocabulary
(ontology.ttl). No mocks. Zero rows = pass is the house falsifier shape; ASK
gates are fail-closed (true = PASS).

Vectors:
  TV-01  multi-tier SBB synthesis fiber completeness -> PASS -> stage5 qualified
  TV-02  conflation injection -> DoD #9 collision -> fail-closed
  TV-03  semantic alias (ea: term re-declared pack-locally) -> metamodel
         hygiene fail-closed
  TV-04  vacuous query -> vacuous qualification rejected
  TV-05  procedural mutation -> DO out of grammar
"""
from pathlib import Path

from rdflib import Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS

ROOT = Path(__file__).resolve().parents[1]
Q = ROOT / "queries"

EA = Namespace("https://chatman.ai/ontology/enterprise-architecture#")
F5EA = Namespace("https://ggen.io/ontology/fortune5-enterprise-architecture#")
IC = Namespace("https://seanchatmangpt.github.io/packs/industry-closure-ledger-pack#")
PROV = Namespace("http://www.w3.org/ns/prov#")

DIGEST = "sha256:" + "a" * 64

STAGE_GATES = [
    "010-stage0-closure.rq",
    "020-stage1-contract-pending.rq",
    "030-stage2-contract-approved.rq",
    "040-stage3-sbb-candidate.rq",
    "050-stage4-qualified-no-evidence.rq",
    "060-stage5-terminal.rq",
]

ASK_GATES_PASS_TRUE = [
    "120-zero-wildcard-iam.rq",
    "140-cmek-and-private-connectivity.rq",
    "150-azure-nist-800-53-rev5.rq",
]

ZERO_ROW_GATES = STAGE_GATES + [
    "100-ladder-monotonicity.rq",
    "110-aws-sbb-select.rq",
]


def run_gate(g, name):
    """Run a real pack gate (.rq) against graph/dataset g. Returns the ASK
    boolean for ASK gates, otherwise the list of result rows."""
    text = (Q / name).read_text()
    result = g.query(text)
    if result.type == "ASK":
        return bool(result.askAnswer)
    return list(result)


def base_graph():
    g = Graph()
    g.parse(ROOT / "ontology.ttl", format="turtle")
    return g


def admit_stage5(g):
    """Conformance admission over the real gate set: the qualification must be
    non-vacuous (>= 1 pinned SBB), then every stage gate (010..060), the
    ladder monotonicity gate and the fail-closed ASK gates must pass."""
    sbbs = list(g.subjects(RDF.type, EA.SolutionBuildingBlock))
    if not sbbs:
        return False, "E_VACUOUS_QUALIFICATION_REJECTED"
    for s in sbbs:
        pins = [str(d) for d in g.objects(s, EA.exactSubject)]
        if len(pins) != 1 or not pin_ok(pins[0]):
            return False, "E_PIN_MALFORMED"

    for name in STAGE_GATES:
        rows = run_gate(g, name)
        if rows:
            return False, f"{name}: {[tuple(r) for r in rows]}"
    if run_gate(g, "100-ladder-monotonicity.rq"):
        return False, "100-ladder-monotonicity.rq"
    if not run_gate(g, "110-aws-sbb-select.rq") == []:
        return False, "110-aws-sbb-select.rq"
    for name in ASK_GATES_PASS_TRUE:
        if run_gate(g, name) is not True:
            return False, f"{name}: ASK false"
    return True, "ALIVE"


def pin_ok(pin):
    return pin.startswith("sha256:") and len(pin) == len("sha256:") + 64


def synthesis_fiber():
    """TV-01 fixture: complete multi-tier synthesis fiber (requirement ->
    capability -> ABB -> approved attributed contract -> QUALIFIED SBB with
    sha256 exact-subject pin -> independent VERIFIED OBSERVED evidence ->
    head snapshot with LIVE coverage -> solution group -> AWS/GCP/Azure
    realizations) plus the OPEN deficit residuals the ladder requires."""
    g = base_graph()

    cap = EA["capability-f5"]
    req = IC["req-001"]
    g.add((req, RDF.type, IC.Requirement))
    g.add((req, IC.disposition, IC.IN_SCOPE))
    g.add((req, IC.requiresCapability, cap))

    abb = EA["abb-f5"]
    g.add((abb, RDF.type, EA.ArchitectureBuildingBlock))
    g.add((abb, EA.realizesCapability, cap))
    k = EA["contract-001"]
    g.add((abb, EA.governedByContract, k))
    g.add((k, RDF.type, EA.ArchitectureContract))
    g.add((k, IC.approvalStatus, IC.APPROVED))
    human = PROV["agent-human"]
    g.add((human, RDF.type, PROV.Agent))
    g.add((k, IC.approvedBy, human))
    g.add((k, IC.approvalReceipt, IC["receipt-001"]))
    g.add((k, IC.authorityClaim, Literal("NONE")))

    sbb = EA["sbb-f5"]
    g.add((sbb, RDF.type, EA.SolutionBuildingBlock))
    g.add((sbb, EA.satisfiesABB, abb))
    g.add((sbb, EA.hasStanding, EA.QUALIFIED))
    g.add((sbb, EA.exactSubject, Literal(DIGEST)))

    # OPEN deficit residuals required by the stage-2 and stage-4/5 gates.
    res_sbb = IC["residual-sbb"]
    g.add((res_sbb, RDF.type, IC.Residual))
    g.add((res_sbb, IC.deficitClass, IC.DEFICIT_SBB))
    g.add((res_sbb, IC.status, Literal("OPEN")))
    g.add((res_sbb, IC.residualOf, req))
    res_k = IC["residual-contract"]
    g.add((res_k, RDF.type, IC.Residual))
    g.add((res_k, IC.deficitClass, IC.DEFICIT_CONTRACT))
    g.add((res_k, IC.status, Literal("OPEN")))
    g.add((res_k, IC.residualOf, req))
    res_ev = IC["residual-evidence"]
    g.add((res_ev, RDF.type, IC.Residual))
    g.add((res_ev, IC.deficitClass, IC.DEFICIT_EVIDENCE))
    g.add((res_ev, IC.status, Literal("OPEN")))
    g.add((res_ev, IC.residualOf, req))

    producer = PROV["agent-producer"]
    verifier = PROV["agent-verifier"]
    for a in (producer, verifier):
        g.add((a, RDF.type, PROV.Agent))
    ev = IC["evidence-001"]
    g.add((ev, RDF.type, IC.ExecutionEvidence))
    g.add((ev, IC.evidenceFor, sbb))
    g.add((ev, IC.evidenceSubject, Literal(DIGEST)))
    g.add((ev, IC.outcome, IC.VERIFIED))
    g.add((ev, IC.receiptDigest, Literal("sha256:" + "b" * 64)))
    g.add((ev, IC.producedBy, producer))
    g.add((ev, IC.verifiedBy, verifier))
    g.add((ev, IC.evidenceKind, IC.OBSERVED))

    closure = IC["closure-f5"]
    head = IC["snapshot-head"]
    g.add((head, RDF.type, IC.ClosureSnapshot))
    g.add((head, IC.snapshotOf, closure))
    cov = IC["coverage-001"]
    g.add((cov, RDF.type, IC.Coverage))
    g.add((cov, IC.inSnapshot, head))
    g.add((cov, IC.coversCapability, cap))
    g.add((cov, IC.byABB, abb))
    g.add((cov, IC.bySBB, sbb))
    g.add((cov, IC.coverageState, IC.LIVE))

    group = F5EA["group-guest"]
    g.add((group, RDF.type, F5EA.SolutionGroup))
    g.add((group, F5EA.groupKey, Literal("guest")))
    g.add((group, F5EA.groupsSBB, sbb))

    # AWS realization (gates 110/120)
    aws = F5EA["realization-aws"]
    g.add((aws, RDF.type, F5EA.Realization))
    g.add((aws, F5EA.providerVariant, Literal("aws")))
    g.add((aws, F5EA.sbbSlug, Literal("f5-guest-sbb")))
    g.add((aws, F5EA.sbbDomain, Literal("guest")))
    g.add((aws, F5EA.region, Literal("us-east-1")))
    g.add((aws, F5EA.exactSubject, Literal(DIGEST)))
    g.add((aws, F5EA.airGapParityEgress, Literal(True)))
    g.add((aws, F5EA.airGapParityAudit, Literal(True)))
    r1 = F5EA["res-aws-1"]
    g.add((aws, F5EA.hasResource, r1))
    g.add((r1, RDF.type, F5EA.SbbResource))
    g.add((r1, F5EA.resourceClass, Literal("storagelike")))
    g.add((r1, F5EA.iamAction, Literal("s3:GetObject")))

    # GCP realization (gate 140)
    gcp = F5EA["realization-gcp"]
    g.add((gcp, RDF.type, F5EA.Realization))
    g.add((gcp, F5EA.providerVariant, Literal("gcp")))
    g1 = F5EA["res-gcp-1"]
    g.add((gcp, F5EA.hasResource, g1))
    g.add((g1, RDF.type, F5EA.SbbResource))
    g.add((g1, F5EA.resourceClass, Literal("storagelike")))
    g.add((g1, F5EA.hasCmekKey, F5EA["cmek-key-1"]))
    g2 = F5EA["res-gcp-2"]
    g.add((gcp, F5EA.hasResource, g2))
    g.add((g2, RDF.type, F5EA.SbbResource))
    g.add((g2, F5EA.resourceClass, Literal("servicelike")))
    g.add((g2, F5EA.ingressMode, Literal("psc")))

    # Azure realization (gate 150)
    azure = F5EA["realization-azure"]
    g.add((azure, RDF.type, F5EA.Realization))
    g.add((azure, F5EA.providerVariant, Literal("azure")))
    g.add((azure, F5EA.sbbSlug, Literal("f5-guest-sbb")))
    g.add((azure, F5EA.sbbDomain, Literal("guest")))
    g.add((azure, F5EA.exactSubject, Literal(DIGEST)))
    a1 = F5EA["res-azure-1"]
    g.add((azure, F5EA.hasResource, a1))
    g.add((a1, RDF.type, F5EA.SbbResource))
    g.add((a1, F5EA.resourceClass, Literal("storagelike")))
    for control in ("AC-2", "SC-28", "CM-6"):
        g.add((a1, F5EA.controlMapping, Literal(control)))

    return g


# ---------------------------------------------------------------- TV-01 ----
def test_tv01_synthesis_fiber_completeness_admitted_at_stage5():
    g = synthesis_fiber()
    ok, detail = admit_stage5(g)
    assert ok, detail

    # Stage-5 terminal gate passes with zero rows; the azure inventory SELECT
    # sees the well-bound realization.
    assert run_gate(g, "060-stage5-terminal.rq") == []
    inv = run_gate(g, "160-azure-sbb-select.rq")
    assert len(inv) == 1 and str(inv[0].exactSubject) == DIGEST


def test_tv01_falsifier_removing_the_pin_breaks_stage4():
    g = synthesis_fiber()
    g.remove((EA["sbb-f5"], EA.exactSubject, None))
    rows = run_gate(g, "050-stage4-qualified-no-evidence.rq")
    reasons = {str(r.reason) for r in rows}
    assert "REFUSED:F5_STAGE4_PIN_MALFORMED" in reasons


# ---------------------------------------------------------------- TV-02 ----
def manifest_dataset(group_typed_as=None, digest=DIGEST):
    """Dataset with the authoritative EA layer (named graph urn:ea, seeded
    from the pack ontology) plus an f5ea.sbb-group-manifest.v1 ingest in
    named graph <manifest>."""
    ds = Dataset()
    ds.default_union = True
    ea_ctx = ds.graph(URIRef("urn:ea"))
    ea_ctx.parse(ROOT / "ontology.ttl", format="turtle")
    abb = EA["abb-f5"]
    sbb = EA["sbb-f5"]
    ea_ctx.add((abb, RDF.type, EA.ArchitectureBuildingBlock))
    ea_ctx.add((sbb, RDF.type, EA.SolutionBuildingBlock))
    ea_ctx.add((sbb, EA.satisfiesABB, abb))
    ea_ctx.add((sbb, EA.exactSubject, Literal(DIGEST)))
    group = F5EA["group-guest"]
    ea_ctx.add((group, RDF.type, F5EA.SolutionGroup))
    ea_ctx.add((group, F5EA.groupKey, Literal("guest")))
    if group_typed_as is not None:
        ea_ctx.add((group, RDF.type, group_typed_as))
    man = ds.graph(URIRef("manifest"))
    group = F5EA["group-guest"]
    man.add((group, RDF.type, F5EA.ManifestEntry))
    man.add((group, F5EA.groupKey, Literal("guest")))
    man.add((group, F5EA.referencesOnly, Literal(True)))
    man.add((group, F5EA.groupsSBB, sbb))
    man.add((group, F5EA.referenceDigest, Literal(digest)))
    return ds


def lift(ds):
    return run_gate(ds, "170-sbb-group-lifting.rq")


DOD9_COLLISION_COURT = """
PREFIX f5ea: <https://ggen.io/ontology/fortune5-enterprise-architecture#>
PREFIX ea:   <https://chatman.ai/ontology/enterprise-architecture#>
SELECT ?s ?cls WHERE {
  ?s a f5ea:SolutionGroup .
  ?s a ?cls .
  FILTER(?cls IN (ea:SolutionBuildingBlock, ea:ArchitectureBuildingBlock,
                  ea:ArchitectureContract, ea:AuthorityBoundary))
}"""


def test_tv02_conflation_injection_fail_closed():
    # Baseline: the honest manifest lifts (group constructed with its
    # groupsSBB reference to the authoritative SBB).
    lifted = lift(manifest_dataset())
    assert (F5EA["group-guest"], RDF.type, F5EA.SolutionGroup) in lifted
    assert (F5EA["group-guest"], F5EA.groupsSBB, EA["sbb-f5"]) in lifted

    # Injection A: the group is conflated into an ea: element (DoD #9
    # collision). The lift must drop the group entirely (fail-closed).
    for cls in (EA.SolutionBuildingBlock, EA.ArchitectureBuildingBlock):
        conflated = manifest_dataset(group_typed_as=cls)
        assert lift(conflated) == [], f"DoD9 collision via {cls} must not lift"
        assert list(conflated.query(DOD9_COLLISION_COURT)), (
            "E_DOD9_COLLISION: collision court must fire on the injected graph"
        )

    # Injection B: stale reference digest -> dangling reference, dropped.
    assert lift(manifest_dataset(digest="sha256:" + "c" * 64)) == []

    # Clean graph: the collision court is silent (anti-vacuity).
    assert not list(manifest_dataset().query(DOD9_COLLISION_COURT))


# ---------------------------------------------------------------- TV-03 ----
def ea_declarations(g):
    """Terms declared in the ea: namespace (hygiene-law violation set)."""
    return sorted(
        (s, p, o)
        for s, p, o in g
        if isinstance(s, URIRef) and str(s).startswith(str(EA))
    )


def test_tv03_semantic_alias_metamodel_hygiene():
    # Hygiene law (ontology.ttl:3-7): ZERO ea: terms are declared pack-locally;
    # ea: is consumed by IRI only.
    clean = ea_declarations(base_graph())
    assert clean == [], f"E_METAMODEL_HYGIENE: pack-local ea: declarations {clean}"

    # Injection: a fixture that re-declares ea:SolutionBuildingBlock locally
    # (semantic alias) is refused by the same court.
    bad = base_graph()
    bad.add((EA.SolutionBuildingBlock, RDF.type, OWL.Class))
    bad.add((EA.SolutionBuildingBlock, RDFS.subClassOf, F5EA.SolutionGroup))
    injected = ea_declarations(bad)
    assert injected, "E_METAMODEL_HYGIENE: injected alias must be detected"
    assert any(p == RDF.type and o == OWL.Class for s, p, o in injected)


# ---------------------------------------------------------------- TV-04 ----
def test_tv04_vacuous_query_rejected():
    # A graph with ZERO SBBs vacuously passes every stage gate (zero rows).
    empty = base_graph()
    for name in STAGE_GATES:
        assert run_gate(empty, name) == [], name
    # The conformance court must not read that as qualification: without at
    # least one pinned SBB, admission is refused as vacuous.
    ok, detail = admit_stage5(empty)
    assert not ok
    assert detail == "E_VACUOUS_QUALIFICATION_REJECTED"

    # The real TV-01 fiber is non-vacuous and admitted.
    ok, detail = admit_stage5(synthesis_fiber())
    assert ok, detail


def test_tv04_falsifier_gate_goes_nonzero_on_real_defect():
    g = synthesis_fiber()
    # Procedural defect: evidence produced and verified by the same agent.
    g.set((IC["evidence-001"], IC.verifiedBy, PROV["agent-producer"]))
    rows = run_gate(g, "060-stage5-terminal.rq")
    assert any(
        str(r.reason) == "REFUSED:F5_STAGE5_EVIDENCE_NOT_INDEPENDENT"
        for r in rows
    )


# ---------------------------------------------------------------- TV-05 ----
AUTHORITY_GRAMMAR_COURT = """
PREFIX f5ea: <https://ggen.io/ontology/fortune5-enterprise-architecture#>
SELECT ?p ?v WHERE {
  { ?s f5ea:authority ?v . FILTER(?v != "NONE") }
  UNION
  { ?s f5ea:authorityCeiling ?v . FILTER(?v != "SELECT") }
}"""


def test_tv05_procedural_mutation_do_out_of_grammar():
    # The ontology's authority grammar is a hard ceiling: SELECT, never DO.
    g = base_graph()
    F5 = URIRef(str(F5EA))
    rows = list(g.query(
        """
        PREFIX f5ea: <https://ggen.io/ontology/fortune5-enterprise-architecture#>
        SELECT ?a ?c WHERE {
          <https://ggen.io/ontology/fortune5-enterprise-architecture#>
            f5ea:authority ?a ;
            f5ea:authorityCeiling ?c .
        }"""
    ))
    assert rows, "ontology must declare authority + authorityCeiling"
    for row in rows:
        assert str(row.a) == "NONE"
        assert str(row.c) == "SELECT"
    assert not list(g.query(AUTHORITY_GRAMMAR_COURT))

    # Mutation (a): DO enters the graph -> the real stage-2 gate refuses.
    mutated = synthesis_fiber()
    mutated.add((EA["contract-001"], IC.authorityClaim, IC.DO))
    gate_rows = run_gate(mutated, "030-stage2-contract-approved.rq")
    assert any(
        str(r.reason) == "REFUSED:F5_STAGE2_AUTHORITY_DO_FORBIDDEN"
        for r in gate_rows
    ), list(gate_rows)

    # Mutation (b): DO written into the authority grammar -> court fires.
    do_graph = base_graph()
    do_graph.add((F5, F5EA.authority, Literal("DO")))
    violations = list(do_graph.query(AUTHORITY_GRAMMAR_COURT))
    assert violations, "DO injection must be detected"
    assert all(str(v.v) == "DO" for v in violations)
