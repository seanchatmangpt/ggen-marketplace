"""Spine court: enterprise-operating-model-pack -> industry-closure-pack, end to end.

One synthetic enterprise is pushed through the whole two-pass pipeline and one
full turn of the closure loop, using real collaborators only: the real Turtle on
disk parsed by rdflib, the real SPARQL gates and queries of both packs executed
by rdflib, the real templates rendered through the restricted Jinja2 proxy in
``ic_support`` (the subset Tera also executes), and no mocks.

    PASS 1  enterprise-operating-model-pack: strategy -> requirements + ABB skeletons
    PASS 2  industry-closure-pack:           residual ledger, work orders,
                                             feedback packet, closure-next
    turn    residual -> delta packet -> upstream lane acts -> re-closure,
            with Cl_{t+1} a strict superset of Cl_t on the recorded ledger.

What this proves, and what it does not
--------------------------------------
Standing: PARTIAL_ALIVE for composition under rdflib. Everything the "upstream
lanes" do below (approve a contract, declare/qualify an SBB, add execution
evidence) is test-simulated consumer data with synthetic digests and a
SYNTHETIC evidence kind. It is shaped like the real thing, never produced by a
pack, and never promotes anything to ALIVE. Real ggen manufacture of either
pass, two-pass replay, and native-engine behaviour of the gates are
BLOCKED:ggen_binary_unavailable; the Jinja2 proxy is PARTIAL evidence only.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

TESTS = Path(__file__).resolve().parent
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

import ic_support as S  # noqa: E402

# ---------------------------------------------------------------------------
# The two real packs under test (read from disk, never copied)
# ---------------------------------------------------------------------------

IC_PACK = S.PACK
EOM_PACK = S.PACKS / "enterprise-operating-model-pack"
EA_PACK = S.PACKS / "enterprise-architecture-pack"

IC_NS = S.IC
EA_NS = S.EA
EOM_NS = "https://seanchatmangpt.github.io/packs/enterprise-operating-model-pack#"
PROV = "http://www.w3.org/ns/prov#"

IC_ONTOLOGY = IC_PACK / "ontology.ttl"
EOM_ONTOLOGY = EOM_PACK / "ontology.ttl"
ENTERPRISE_INPUT = EOM_PACK / "qualification" / "project" / "ontology" / "enterprise-input.ttl"

EOM_Q_REQ = EOM_PACK / "queries" / "10-requirements.rq"
EOM_Q_SKEL = EOM_PACK / "queries" / "20-abb-skeletons.rq"
EOM_T_REQ = EOM_PACK / "templates" / "architecture-requirements.ttl.tera"
EOM_T_SKEL = EOM_PACK / "templates" / "abb-skeletons.ttl.tera"
IC_Q10 = IC_PACK / "queries" / "10-residual.rq"
IC_Q20 = IC_PACK / "queries" / "20-closure-frontier.rq"
IC_TEMPLATES = IC_PACK / "templates"

IC_GATES = sorted((IC_PACK / "gates").glob("*.rq"))
EOM_GATES = sorted((EOM_PACK / "gates").glob("*.rq"))
IC_GATE = {g.stem: g for g in IC_GATES}
EOM_GATE = {g.stem: g for g in EOM_GATES}

CLOSURE = "https://example.invalid/closure/acme"
BASE = "https://example.invalid/closure/acme/"
IND = "https://example.invalid/industry/acme/"

# rkey of every (requirement, capability) pair the scenario touches
R_O2C = "REQ-ACME-UNIF-order-to-cash--CAP-ORDER-TO-CASH"
R_CUST = "REQ-ACME-UNIF-customer-master--CAP-CUSTOMER-DATA"
R_INT = "REQ-ACME-UNIF-integration-bus--CAP-INTEGRATION"
R_PRICE = "REQ-ACME-PRICING--CAP-PRICING"
R_DO = "REQ-ACME-DISBURSE--CAP-DISBURSE"


def ic(name: str) -> URIRef:
    return URIRef(IC_NS + name)


def ea(name: str) -> URIRef:
    return URIRef(EA_NS + name)


# ---------------------------------------------------------------------------
# The synthetic industry side (test-owned consumer data, example.invalid IRIs).
# The enterprise side is the real qualification input shipped by the eom pack.
# ---------------------------------------------------------------------------

INDUSTRY_TTL = f"""
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ic: <{IC_NS}> .
@prefix ea: <{EA_NS}> .
@prefix prov: <{PROV}> .
@prefix ind: <{IND}> .

<{CLOSURE}> a ic:IndustryClosure ;
    ic:industryScope "synthetic bounded scope for the spine court" ;
    ic:baseIri "{BASE}" ;
    ic:boundPathPrefix "ontologies/public/synthetic/" ;
    ic:usesSource ind:src-pricing ;
    ic:hasSnapshot ind:snap0 .

ind:snap0 a ic:ClosureSnapshot ;
    ic:snapshotOf <{CLOSURE}> ;
    ic:epoch 0 .

ind:src-pricing a ic:KnowledgeSource ;
    ic:admission ic:ADMITTED ;
    ic:sourceIri <https://example.invalid/source/pricing> ;
    ic:sourceVersion "1.0.0" ;
    ic:sourceDigest "sha256:{hashlib.sha256(b"spine:src-pricing").hexdigest()}" ;
    ic:licenseBoundary "synthetic test source, no external licence" ;
    ic:sourceLocator "ontologies/public/synthetic/pricing.ttl" ;
    ic:providesConcept <https://example.invalid/concept/Pricing> .

ind:cap-pricing a ea:Capability ;
    ic:capabilityKey "CAP-PRICING" ;
    ic:groundedIn ind:src-pricing ;
    ic:concept <https://example.invalid/concept/Pricing> .

ind:req-pricing a ic:Requirement ;
    ic:requirementId "REQ-ACME-PRICING" ;
    ic:statement "Synthetic requirement: price a product offer, stated in paraphrase." ;
    ic:inClosure <{CLOSURE}> ;
    ic:disposition ic:IN_SCOPE ;
    ic:requiresCapability ind:cap-pricing ;
    ic:derivedFrom ind:src-pricing .

ind:cap-disburse a ea:Capability ;
    ic:capabilityKey "CAP-DISBURSE" ;
    ic:groundedIn ind:src-pricing ;
    ic:concept <https://example.invalid/concept/Pricing> .

ind:req-disburse a ic:Requirement ;
    ic:requirementId "REQ-ACME-DISBURSE" ;
    ic:statement "Synthetic requirement: move money autonomously, which needs consequential authority." ;
    ic:inClosure <{CLOSURE}> ;
    ic:disposition ic:IN_SCOPE ;
    ic:requiresCapability ind:cap-disburse ;
    ic:needsDoAuthority true ;
    ic:derivedFrom ind:src-pricing .

ind:req-oos a ic:Requirement ;
    ic:requirementId "REQ-ACME-OOS" ;
    ic:statement "Synthetic requirement outside the declared scope." ;
    ic:inClosure <{CLOSURE}> ;
    ic:disposition ic:OUT_OF_SCOPE ;
    ic:scopeJustification "The synthetic scope excludes this capability family." ;
    ic:derivedFrom ind:src-pricing .

ind:human-approver a prov:Agent .
ind:agent-builder a prov:Agent .
ind:agent-verifier a prov:Agent .
"""

HUMAN = URIRef(IND + "human-approver")
BUILDER = URIRef(IND + "agent-builder")
VERIFIER = URIRef(IND + "agent-verifier")


def sha(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Consumer state: the two input graphs a human owns, plus the last regenerated
# artifacts the human appended. Packs never write here; only the lanes below do.
# ---------------------------------------------------------------------------

def build(parts: list, seed: int | None = None) -> Graph:
    """A fresh graph from Paths, Turtle text and Graphs. With ``seed`` the triple
    insertion order is shuffled (after a canonical sort), so any dependence of
    the output on store iteration order shows up as a byte difference."""
    triples = []
    for part in parts:
        if isinstance(part, Graph):
            triples.extend(part)
        else:
            tmp = Graph()
            S.parse_into(tmp, part)
            triples.extend(tmp)
    if seed is not None:
        triples.sort(key=lambda t: tuple(x.n3() for x in t))
        random.Random(seed).shuffle(triples)
    graph = Graph()
    for triple in triples:
        graph.add(triple)
    return graph


@dataclass
class Consumer:
    seed: int | None = None
    ent: Graph = field(default_factory=Graph)
    ind: Graph = field(default_factory=Graph)
    ledger: str = ""
    workorders: str = ""

    def __post_init__(self) -> None:
        self.ent = build([ENTERPRISE_INPUT])
        self.ind = build([INDUSTRY_TTL])

    def b(self, *parts) -> Graph:
        return build(list(parts), self.seed)

    def cap_iri(self, key: str) -> URIRef:
        found = sorted(set(self.ent.subjects(ic("capabilityKey"), Literal(key)))
                       | set(self.ind.subjects(ic("capabilityKey"), Literal(key))))
        assert len(found) == 1, (key, found)
        return found[0]

    def abb_of(self, key: str) -> URIRef:
        cap = self.cap_iri(key)
        found = sorted(set(self.ent.subjects(ea("realizesCapability"), cap))
                       | set(self.ind.subjects(ea("realizesCapability"), cap)))
        assert len(found) == 1, (key, found)
        return found[0]

    def sbb_iri(self, key: str) -> URIRef:
        return URIRef(f"{IND}sbb/{key}")


@dataclass
class Run:
    """One full pass-1 + pass-2 execution on a consumer's current inputs."""
    eom: dict[str, str]
    imports: list[str]
    graph: Graph                      # the pass-2 world (what real ggen would load)
    rows10: list[dict[str, str]]
    rows20: list[dict[str, str]]
    ic_out: dict[str, str]
    skeleton_rows: list[dict[str, str]]
    requirement_rows: list[dict[str, str]]

    @property
    def classes(self) -> dict[str, str]:
        return {r["rkey"]: r["classCode"] for r in self.rows10}

    @property
    def packet(self) -> dict:
        return json.loads(self.ic_out["feedback-packet"])

    def all_text(self) -> dict[str, str]:
        out = {f"eom/{k}": v for k, v in self.eom.items()}
        out.update({f"ic/{k}": v for k, v in self.ic_out.items()})
        return out


def execute(c: Consumer, skeletons: bool = True, with_ledger: bool = False) -> Run:
    """PASS 1 (eom) then PASS 2 (ic). ``skeletons=False`` models a consumer that
    imports only the requirement file into pass 2; ``with_ledger`` appends the
    previously admitted ledger and work orders, which is the fixed-point check."""
    eom_graph = c.b(EOM_ONTOLOGY, c.ent)
    req_rows = S.query_rows(eom_graph, EOM_Q_REQ)
    skel_rows = S.query_rows(eom_graph, EOM_Q_SKEL)
    eom_out = {
        "architecture-requirements": S.render(EOM_T_REQ, req_rows),
        "abb-skeletons": S.render(EOM_T_SKEL, skel_rows),
    }
    imports = [eom_out["architecture-requirements"]]
    if skeletons:
        imports.append(eom_out["abb-skeletons"])
    if with_ledger:
        imports += [c.ledger, c.workorders]
    # pass 2 loads the kernel ontology, the industry input, the generated pass-1
    # files and the enterprise input (the capability individuals live there).
    graph = c.b(IC_ONTOLOGY, c.ind, c.ent, *imports)
    rows10 = S.query_rows(graph, IC_Q10)
    rows20 = S.query_rows(graph, IC_Q20)
    ic_out = {
        "residual-ledger": S.render(IC_TEMPLATES / "residual-ledger.ttl.tera", rows10),
        "sjira-workorders": S.render(IC_TEMPLATES / "sjira-workorders.ttl.tera", rows10),
        "closure-next": S.render(IC_TEMPLATES / "closure-next.ttl.tera", rows20),
        "feedback-packet": S.render(IC_TEMPLATES / "feedback-packet.json.tera", rows10),
    }
    return Run(eom_out, imports, graph, rows10, rows20, ic_out, skel_rows, req_rows)


def admit_ledger(c: Consumer, run: Run) -> None:
    """The human replaces the previously appended ledger with the regenerated one."""
    c.ledger = run.ic_out["residual-ledger"]
    c.workorders = run.ic_out["sjira-workorders"]


def admit_closure_next(c: Consumer, run: Run) -> None:
    """The human appends the proposed snapshot to the industry input."""
    S.parse_into(c.ind, run.ic_out["closure-next"])


def court_graph(c: Consumer, run: Run) -> Graph:
    """Everything a human would have after admitting this run's artifacts."""
    return c.b(IC_ONTOLOGY, EOM_ONTOLOGY, c.ind, c.ent, *run.imports, c.ledger, c.workorders)


def run_gates(graph: Graph, gates: dict[str, Path]) -> dict[str, list[tuple[str, str]]]:
    return {stem: S.gate_rows(graph, path) for stem, path in gates.items()}


def refusals(rows: dict[str, list[tuple[str, str]]]) -> dict[str, list[tuple[str, str]]]:
    return {stem: r for stem, r in rows.items() if r}


# ---------------------------------------------------------------------------
# Test-simulated upstream lanes. They are consumer data edits, shaped like the
# real artifacts, with synthetic receipts. None of this is produced by a pack.
# ---------------------------------------------------------------------------

def lane_architecture(c: Consumer, key: str) -> None:
    """A named human approves the skeleton contract (approver + receipt)."""
    abb = c.abb_of(key)
    contracts = sorted(c.ent.objects(abb, ea("governedByContract")))
    assert len(contracts) == 1, (key, contracts)
    k = contracts[0]
    assert (k, ic("approvalStatus"), ic("PENDING_HUMAN_APPROVAL")) in c.ent
    c.ent.remove((k, ic("approvalStatus"), ic("PENDING_HUMAN_APPROVAL")))
    c.ent.add((k, ic("approvalStatus"), ic("APPROVED")))
    c.ent.add((k, ic("approvedBy"), HUMAN))
    c.ent.add((k, ic("approvalReceipt"), Literal(f"receipt:approval:{key}")))


def lane_marketplace(c: Consumer, key: str) -> None:
    """Declare an SBB against the approved ABB: candidate, not yet qualified."""
    sbb = c.sbb_iri(key)
    c.ind.add((sbb, RDF.type, ea("SolutionBuildingBlock")))
    c.ind.add((sbb, ea("satisfiesABB"), c.abb_of(key)))
    c.ind.add((sbb, ea("hasStanding"), ea("CANDIDATE")))


def lane_qualification(c: Consumer, key: str) -> None:
    """Qualify the SBB and pin its exact subject (synthetic digest)."""
    sbb = c.sbb_iri(key)
    c.ind.remove((sbb, ea("hasStanding"), ea("CANDIDATE")))
    c.ind.add((sbb, ea("hasStanding"), ea("QUALIFIED")))
    c.ind.add((sbb, ea("exactSubject"), Literal(sha(f"spine:subject:{key}"))))


def add_evidence(c: Consumer, key: str, outcome: str, producer: URIRef = BUILDER,
                 verifier: URIRef = VERIFIER, tag: str = "ev") -> URIRef:
    sbb = c.sbb_iri(key)
    subject = next(c.ind.objects(sbb, ea("exactSubject")))
    ev = URIRef(f"{IND}evidence/{key}-{tag}")
    c.ind.add((ev, RDF.type, ic("ExecutionEvidence")))
    c.ind.add((ev, ic("evidenceFor"), sbb))
    c.ind.add((ev, ic("evidenceSubject"), subject))
    c.ind.add((ev, ic("outcome"), ic(outcome)))
    c.ind.add((ev, ic("receiptDigest"), Literal(sha(f"spine:receipt:{key}:{tag}"))))
    c.ind.add((ev, ic("producedBy"), producer))
    c.ind.add((ev, ic("verifiedBy"), verifier))
    c.ind.add((ev, ic("evidenceKind"), ic("SYNTHETIC")))
    return ev


def lane_court(c: Consumer, key: str) -> None:
    add_evidence(c, key, "VERIFIED")


# the delta code carried by the feedback packet selects the lane that acts
LANES = {
    "ARCHITECTURE_DELTA": lane_architecture,
    "PACK_DELTA": lane_marketplace,
    "QUALIFICATION_DELTA": lane_qualification,
    "COURT_DELTA": lane_court,
}

# the packet's target code is what routes an item to a lane
LANE_TARGET = {
    "ARCHITECTURE_DELTA": "UPSTREAM_ARCHITECTURE",
    "PACK_DELTA": "UPSTREAM_MARKETPLACE",
    "QUALIFICATION_DELTA": "UPSTREAM_QUALIFICATION",
    "COURT_DELTA": "UPSTREAM_QUALIFICATION",
}


@dataclass
class Step:
    """One executed turn of the loop: the packet item that was read and the lane
    that acted on it."""
    deficit: str
    delta: str
    target: str
    work_order: str
    run: Run


def close_capability(c: Consumer, key: str, steps: list[Step], max_turns: int = 8) -> Run:
    """Residual -> delta packet -> lane acts -> re-closure, until the capability
    no longer appears in the residual. Reads only the generated feedback packet
    to decide what happens next; never peeks at the classifier."""
    for _ in range(max_turns):
        run = execute(c)
        admit_ledger(c, run)
        items = [i for i in run.packet["items"] if i["capabilityKey"] == key]
        if not items:
            return run
        assert len(items) == 1, items
        item = items[0]
        lane = LANES[item["deltaCode"]]
        steps.append(Step(item["deficitClass"], item["deltaCode"], item["targetCode"], item["workOrderId"], run))
        lane(c, key)
    raise AssertionError(f"{key} did not close within {max_turns} turns")


# ---------------------------------------------------------------------------
# Cl_t on the recorded ledger: the set of (capability key, ABB) coverages
# recorded in snapshot epoch t, in any state (the ledger is monotone).
# ---------------------------------------------------------------------------

def ledger_set(graph: Graph, epoch: int) -> set[tuple[str, str]]:
    rows = graph.query(
        f"""SELECT ?key ?abb WHERE {{
              ?s <{IC_NS}epoch> {epoch} .
              ?cov a <{IC_NS}Coverage> ; <{IC_NS}inSnapshot> ?s ;
                   <{IC_NS}coversCapability> ?cap ; <{IC_NS}byABB> ?abb .
              ?cap <{IC_NS}capabilityKey> ?key }}"""
    )
    return {(str(r["key"]), str(r["abb"])) for r in rows}


def live_set(graph: Graph, epoch: int) -> set[tuple[str, str]]:
    rows = graph.query(
        f"""SELECT ?key ?abb WHERE {{
              ?s <{IC_NS}epoch> {epoch} .
              ?cov a <{IC_NS}Coverage> ; <{IC_NS}inSnapshot> ?s ; <{IC_NS}coverageState> <{IC_NS}LIVE> ;
                   <{IC_NS}coversCapability> ?cap ; <{IC_NS}byABB> ?abb .
              ?cap <{IC_NS}capabilityKey> ?key }}"""
    )
    return {(str(r["key"]), str(r["abb"])) for r in rows}


# ---------------------------------------------------------------------------
# The whole journey, played once per fixture (and again for determinism).
# ---------------------------------------------------------------------------

@dataclass
class Journey:
    consumer: Consumer
    baseline: Run                     # pass 2 imports only the requirements file
    with_skeletons: Run               # pass 2 also imports the skeletons
    merged: Run                       # the human merged the skeletons into the enterprise input
    walk1: list[Step]
    covered: Run                      # O2C chain complete, closure-next not yet admitted
    covered_court: Graph              # ... with ledger admitted but no next snapshot
    after_admit: Run                  # epoch 1 admitted; closure-next now proposes epoch 2
    walk2: list[Step]
    turn2: Run                        # CUSTOMER-DATA complete; closure-next proposes epoch 2 with two coverages
    final_run: Run
    final_court: Graph
    all_runs: list[Run]

    def fingerprint(self) -> str:
        h = hashlib.sha256()
        for i, run in enumerate(self.all_runs):
            for name, text in sorted(run.all_text().items()):
                h.update(f"{i}|{name}|{len(text)}|".encode())
                h.update(text.encode())
        return h.hexdigest()


def play(seed: int | None = None) -> Journey:
    c = Consumer(seed=seed)
    runs: list[Run] = []

    def keep(run: Run) -> Run:
        runs.append(run)
        return run

    baseline = keep(execute(c, skeletons=False))
    with_skel = keep(execute(c, skeletons=True))

    # the human merges the generated skeletons into the enterprise input
    S.parse_into(c.ent, with_skel.eom["abb-skeletons"])
    merged = keep(execute(c, skeletons=True))

    # turn t -> t+1: close the order-to-cash capability through the packet loop
    walk1: list[Step] = []
    covered = keep(close_capability(c, "CAP-ORDER-TO-CASH", walk1))
    covered_court = court_graph(c, covered)
    admit_closure_next(c, covered)

    after_admit = keep(execute(c))
    admit_ledger(c, after_admit)

    # turn t+1 -> t+2: close customer-data; the recorded coverage is carried forward
    walk2: list[Step] = []
    turn2 = keep(close_capability(c, "CAP-CUSTOMER-DATA", walk2))
    admit_closure_next(c, turn2)

    final_run = keep(execute(c))
    admit_ledger(c, final_run)
    final_court = court_graph(c, final_run)
    return Journey(c, baseline, with_skel, merged, walk1, covered, covered_court, after_admit,
                   walk2, turn2, final_run, final_court, runs)


@pytest.fixture(scope="module")
def journey() -> Journey:
    return play()


def local(iri: str) -> str:
    return iri.rsplit("/", 1)[-1]


def closure_problems(g: Graph) -> list[str]:
    """Spine-level coherence of the eom -> ic seam, judged on the merged graph:
    every decision aims at a declared ic:IndustryClosure whose baseIri equals the
    decision's targetBaseIri, and every requirement sits in a declared closure."""
    problems = []
    for decision in sorted(g.subjects(RDF.type, URIRef(EOM_NS + "OperatingModelDecision"))):
        target = next(g.objects(decision, URIRef(EOM_NS + "targetClosure")), None)
        target_base = next(g.objects(decision, URIRef(EOM_NS + "targetBaseIri")), None)
        if target is None or (target, RDF.type, ic("IndustryClosure")) not in g:
            problems.append(f"{decision}: targetClosure {target} is not a declared ic:IndustryClosure")
        elif str(next(g.objects(target, ic("baseIri")), None)) != str(target_base):
            problems.append(f"{decision}: targetBaseIri {target_base} != ic:baseIri of {target}")
    for req in sorted(g.subjects(RDF.type, ic("Requirement"))):
        for closure in g.objects(req, ic("inClosure")):
            if (closure, RDF.type, ic("IndustryClosure")) not in g:
                problems.append(f"{req}: inClosure {closure} is not a declared ic:IndustryClosure")
    return problems


# ---------------------------------------------------------------------------
# PASS 1: strategy -> requirements and skeletons (enterprise-operating-model-pack)
# ---------------------------------------------------------------------------

def test_the_real_enterprise_input_is_admitted_by_every_eom_gate() -> None:
    graph = build([EOM_ONTOLOGY, ENTERPRISE_INPUT])
    assert refusals(run_gates(graph, EOM_GATE)) == {}
    assert len(EOM_GATES) == 8


def test_pass1_derives_one_strategy_requirement_per_foundation_element(journey: Journey) -> None:
    req_rows = journey.baseline.requirement_rows
    assert {r["elementKey"] for r in req_rows} == {"order-to-cash", "customer-master", "integration-bus"}
    graph = build([journey.baseline.eom["architecture-requirements"]])
    reqs = sorted(graph.subjects(RDF.type, ic("Requirement")))
    assert [local(str(r)) for r in reqs] == [
        "REQ-ACME-UNIF-customer-master", "REQ-ACME-UNIF-integration-bus", "REQ-ACME-UNIF-order-to-cash",
    ]
    strategy = URIRef("https://example.invalid/enterprise/acme/strategy")
    for r in reqs:
        assert str(next(graph.objects(r, ic("requirementId")))) == local(str(r))
        assert next(graph.objects(r, ic("disposition"))) == ic("IN_SCOPE")
        assert next(graph.objects(r, ic("originAuthority"))) == strategy
        assert str(next(graph.objects(r, ic("inClosure")))) == CLOSURE
        assert (r, ic("derivedFrom"), None) not in graph, "a strategy-derived requirement never cites a source"


def test_pass1_skeletons_cover_only_capabilities_without_an_abb_and_stay_pending(journey: Journey) -> None:
    rows = journey.baseline.skeleton_rows
    assert {r["capabilityKey"] for r in rows} == {"CAP-ORDER-TO-CASH", "CAP-CUSTOMER-DATA"}, (
        "CAP-INTEGRATION already has an ABB in the enterprise input, so no skeleton is emitted for it"
    )
    graph = build([journey.baseline.eom["abb-skeletons"]])
    contracts = sorted(graph.subjects(RDF.type, ea("ArchitectureContract")))
    assert len(contracts) == 2
    for k in contracts:
        assert list(graph.objects(k, ic("approvalStatus"))) == [ic("PENDING_HUMAN_APPROVAL")]
        assert list(graph.objects(k, ic("authorityClaim"))) == [Literal("NONE")]
        assert list(graph.objects(k, ic("standing"))) == [Literal("UNKNOWN")]
        assert (k, ea("hasAuthorityBoundary"), None) in graph
        assert (k, ic("approvedBy"), None) not in graph and (k, ic("approvalReceipt"), None) not in graph
    # HIGH x HIGH axes select both compliance criteria
    assert {str(o).rsplit("#", 1)[-1] for o in graph.objects(contracts[0], URIRef(EOM_NS + "complianceCriterion"))} == {
        "StandardProcessVariant", "SharedDataContract",
    }


def test_the_merged_enterprise_and_industry_graphs_agree_on_the_closure(journey: Journey) -> None:
    g = journey.with_skeletons.graph
    assert closure_problems(g) == []
    decision = next(g.subjects(RDF.type, URIRef(EOM_NS + "OperatingModelDecision")))
    target = next(g.objects(decision, URIRef(EOM_NS + "targetClosure")))
    assert str(next(g.objects(decision, URIRef(EOM_NS + "targetBaseIri")))) == str(next(g.objects(target, ic("baseIri"))))
    # every generated requirement lands in that one closure
    in_closure = {str(o) for r in g.subjects(RDF.type, ic("Requirement")) for o in g.objects(r, ic("inClosure"))}
    assert in_closure == {str(target)}


def test_pass1_output_passes_the_ic_requirement_gates_on_the_merged_graph(journey: Journey) -> None:
    g = journey.with_skeletons.graph
    for stem in ("010_source_admission", "020_requirement_identity", "030_snapshot_identity", "080_authority_fence"):
        assert S.gate_rows(g, IC_GATE[stem]) == [], stem


# ---------------------------------------------------------------------------
# Residual movement: ABB -> CONTRACT (PENDING) once the skeletons arrive
# ---------------------------------------------------------------------------

def test_requirements_alone_leave_abb_deficits_and_skeletons_turn_them_into_pending_contract_deficits(
    journey: Journey,
) -> None:
    assert journey.baseline.classes == {
        R_O2C: "DEFICIT_ABB", R_CUST: "DEFICIT_ABB", R_INT: "DEFICIT_CONTRACT",
        R_PRICE: "DEFICIT_ABB", R_DO: "DEFICIT_AUTHORITY",
    }
    assert journey.with_skeletons.classes == {
        R_O2C: "DEFICIT_CONTRACT", R_CUST: "DEFICIT_CONTRACT", R_INT: "DEFICIT_CONTRACT",
        R_PRICE: "DEFICIT_ABB", R_DO: "DEFICIT_AUTHORITY",
    }
    # the contract deficit is the PENDING one: the contract exists, no human has approved it
    g = journey.with_skeletons.graph
    pending = {str(k) for k in g.subjects(ic("approvalStatus"), ic("PENDING_HUMAN_APPROVAL"))}
    assert pending == {BASE + "contract/CAP-ORDER-TO-CASH", BASE + "contract/CAP-CUSTOMER-DATA"}
    assert not list(g.subjects(ic("approvalStatus"), ic("APPROVED")))


def test_out_of_scope_requirement_is_never_in_the_residual_but_stays_justified(journey: Journey) -> None:
    for run in journey.all_runs:
        assert "REQ-ACME-OOS--UNMAPPED" not in run.classes
        assert all(r["rid"] != "REQ-ACME-OOS" for r in run.rows10)
    g = journey.final_court
    oos = URIRef(IND + "req-oos")
    assert list(g.objects(oos, ic("scopeJustification")))


def test_strategy_derived_residuals_name_the_unmanufactured_foundation_element(journey: Journey) -> None:
    elements = {r["elementKey"] for r in journey.baseline.requirement_rows}
    strategy_rows = [r for r in journey.with_skeletons.rows10 if r["rid"].startswith("REQ-ACME-UNIF-")]
    assert {r["rid"].removeprefix("REQ-ACME-UNIF-") for r in strategy_rows} == elements
    for row in strategy_rows:
        assert row["reqIri"].startswith(BASE + "requirement/"), "the residual points at the generated requirement"


# ---------------------------------------------------------------------------
# The skeleton merge is the pass-1 fixed point
# ---------------------------------------------------------------------------

def test_merging_the_skeletons_is_the_pass1_fixed_point(journey: Journey) -> None:
    first, merged = journey.with_skeletons, journey.merged
    assert first.skeleton_rows, "skeleton rows exist before the human merges them"
    assert merged.skeleton_rows == [], "once the ABBs exist in the input, pass 1 emits no skeleton rows"
    assert not list(build([merged.eom["abb-skeletons"]]).subjects(RDF.type, ea("ArchitectureContract")))
    # strategy requirements are re-derived, not merged, so they are unchanged byte for byte
    assert merged.eom["architecture-requirements"] == first.eom["architecture-requirements"]
    # pass 2 sees the same facts through the enterprise input instead of the import: same outputs
    assert merged.ic_out == first.ic_out


# ---------------------------------------------------------------------------
# One turn: residual -> delta packet -> upstream lane -> re-closure
# ---------------------------------------------------------------------------

def test_the_packet_carries_each_deficit_to_its_typed_target_with_a_matching_work_order(journey: Journey) -> None:
    packet = journey.with_skeletons.packet
    assert packet["doAuthority"] is False and packet["authorityCeiling"] == "NONE" and packet["standing"] == "UNKNOWN"
    items = packet["items"]
    assert [i["workOrderId"] for i in items] == sorted(i["workOrderId"] for i in items)
    by_key = {i["workOrderId"]: i for i in items}
    assert by_key["SJ-" + R_O2C]["targetCode"] == "UPSTREAM_ARCHITECTURE"
    assert by_key["SJ-" + R_O2C]["deltaCode"] == "ARCHITECTURE_DELTA"
    assert by_key["SJ-" + R_PRICE]["deltaCode"] == "ARCHITECTURE_DELTA"
    assert by_key["SJ-" + R_DO]["targetCode"] == "UPSTREAM_AUTHORITY"
    assert by_key["SJ-" + R_DO]["standing"] == "BLOCKED"
    # a work order exists for every item, with the same delta code and class text from the DeficitClass data
    g = build([IC_ONTOLOGY, journey.with_skeletons.ic_out["sjira-workorders"]])
    for item in items:
        wo = next(g.subjects(ic("workOrderId"), Literal(item["workOrderId"])))
        assert str(next(g.objects(wo, ic("deltaCode")))) == item["deltaCode"]
        assert str(next(g.objects(wo, ic("authorityClaim")))) == "NONE"
        assert str(next(g.objects(wo, ic("acceptance"))))
        assert str(next(g.objects(wo, ic("falsifier"))))


def test_the_walk_follows_abb_chain_order_and_each_item_is_routed_by_the_packet(journey: Journey) -> None:
    expected = [
        ("DEFICIT_CONTRACT", "ARCHITECTURE_DELTA"),
        ("DEFICIT_SBB", "PACK_DELTA"),
        ("DEFICIT_QUALIFICATION", "QUALIFICATION_DELTA"),
        ("DEFICIT_EVIDENCE", "COURT_DELTA"),
    ]
    for walk, key in ((journey.walk1, "CAP-ORDER-TO-CASH"), (journey.walk2, "CAP-CUSTOMER-DATA")):
        assert [(s.deficit, s.delta) for s in walk] == expected, key
        assert [s.target for s in walk] == [
            "UPSTREAM_ARCHITECTURE", "UPSTREAM_MARKETPLACE", "UPSTREAM_QUALIFICATION", "UPSTREAM_QUALIFICATION",
        ]
        for s in walk:
            assert LANE_TARGET[s.delta] == s.target
        assert all(s.work_order.startswith("SJ-") and s.work_order.endswith("--" + key) for s in walk)


def test_a_human_approval_moves_the_residual_from_contract_to_sbb(journey: Journey) -> None:
    after_approval = journey.walk1[1].run
    assert after_approval.classes[R_O2C] == "DEFICIT_SBB"
    assert after_approval.classes[R_CUST] == "DEFICIT_CONTRACT", "an approval for one capability does not leak to another"
    g = after_approval.graph
    k = URIRef(BASE + "contract/CAP-ORDER-TO-CASH")
    assert (k, ic("approvalStatus"), ic("APPROVED")) in g
    assert (k, ic("approvedBy"), HUMAN) in g and (k, ic("approvalReceipt"), None) in g


def test_an_unattributed_approval_is_refused_by_the_authority_fence_even_though_it_closes_the_contract_link() -> None:
    c = Consumer()
    first = execute(c)
    S.parse_into(c.ent, first.eom["abb-skeletons"])
    k = URIRef(BASE + "contract/CAP-ORDER-TO-CASH")
    c.ent.remove((k, ic("approvalStatus"), ic("PENDING_HUMAN_APPROVAL")))
    c.ent.add((k, ic("approvalStatus"), ic("APPROVED")))       # no approver, no receipt
    run = execute(c)
    admit_ledger(c, run)
    g = court_graph(c, run)
    rows = S.gate_rows(g, IC_GATE["080_authority_fence"])
    assert [(s, r) for s, r in rows] == [(str(k), "REFUSED:IC_CONTRACT_APPROVAL_UNATTRIBUTED")]


def test_a_qualified_sbb_has_the_shape_of_the_enterprise_architecture_packs_qualified_sbb(journey: Journey) -> None:
    ea_graph = build([EA_PACK / "ontology.ttl"])
    ingest_a = next(s for s in ea_graph.subjects(RDF.type, ea("SolutionBuildingBlock")) if str(s).endswith("#IngestA"))
    reference = {(p, o if p == RDF.type or p == ea("hasStanding") else None) for p, o in ea_graph.predicate_objects(ingest_a)}
    sbb = URIRef(IND + "sbb/CAP-ORDER-TO-CASH")
    ours = {(p, o if p == RDF.type or p == ea("hasStanding") else None)
            for p, o in journey.final_court.predicate_objects(sbb)}
    assert reference == ours, (sorted(map(str, reference)), sorted(map(str, ours)))
    subject = str(next(journey.final_court.objects(sbb, ea("exactSubject"))))
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", subject)


def test_the_walk_stops_at_evidence_and_synthetic_evidence_still_covers_but_never_makes_alive(journey: Journey) -> None:
    run = journey.covered
    assert R_O2C not in run.classes, "VERIFIED independent evidence at the current subject closes the residual"
    assert run.classes[R_CUST] == "DEFICIT_CONTRACT"
    g = journey.covered_court
    assert not list(g.subjects(ic("standing"), Literal("ALIVE")))
    assert {str(o) for o in g.objects(None, ic("evidenceKind"))} == {str(ic("SYNTHETIC"))}


def test_self_verified_evidence_does_not_cover_and_is_refused() -> None:
    c = Consumer()
    first = execute(c)
    S.parse_into(c.ent, first.eom["abb-skeletons"])
    for lane in (lane_architecture, lane_marketplace, lane_qualification):
        lane(c, "CAP-ORDER-TO-CASH")
    add_evidence(c, "CAP-ORDER-TO-CASH", "VERIFIED", producer=BUILDER, verifier=BUILDER, tag="self")
    run = execute(c)
    assert run.classes[R_O2C] == "DEFICIT_EVIDENCE"
    admit_ledger(c, run)
    reasons = {r for _, r in S.gate_rows(court_graph(c, run), IC_GATE["090_standing_evidence"])}
    assert reasons == {"REFUSED:IC_EVIDENCE_NOT_INDEPENDENT"}


# ---------------------------------------------------------------------------
# Cl_{t+1} strictly contains Cl_t on the recorded ledger, and every admission is gated
# ---------------------------------------------------------------------------

CHAIN = ("030_snapshot_identity", "040_closure_monotonicity", "050_coverage_chain", "055_frontier_recorded")


def test_closure_next_proposes_epoch_plus_one_with_the_newly_covered_capability(journey: Journey) -> None:
    rows = journey.covered.rows20
    assert [(r["source"], r["capabilityKey"], r["state"], r["nextEpoch"]) for r in rows] == [
        ("frontier", "CAP-ORDER-TO-CASH", "LIVE", "1"),
    ]
    assert rows[0]["snapshotIri"] == IND + "snap0"
    text = journey.covered.ic_out["closure-next"]
    assert "ALIVE" not in text and "APPROVED" not in text
    proposed = build([text])
    snap = URIRef(BASE + "snapshot/1")
    assert (snap, ic("supersedes"), URIRef(IND + "snap0")) in proposed
    assert list(proposed.objects(snap, ic("epoch"))) == [Literal(1)]
    standings = {str(o) for o in proposed.objects(None, ic("standing"))}
    assert standings == {"UNKNOWN"}, "a proposed coverage is never granted standing by generation"


def test_the_unrecorded_frontier_is_refused_until_closure_next_is_admitted(journey: Journey) -> None:
    rows = S.gate_rows(journey.covered_court, IC_GATE["055_frontier_recorded"])
    assert [(local(s), r) for s, r in rows] == [("cap-order-to-cash", "REFUSED:IC_FRONTIER_UNRECORDED")]
    # after admission the same gate, and the rest of the chain, are quiet
    after = journey.after_admit
    admitted = build([IC_ONTOLOGY, journey.consumer.ind, journey.consumer.ent, *after.imports])
    assert refusals(run_gates(admitted, {s: IC_GATE[s] for s in CHAIN})) == {}


def test_epoch1_strictly_contains_epoch0_on_the_ledger_and_every_chain_gate_admits_it(journey: Journey) -> None:
    g = journey.final_court
    cl0, cl1, cl2 = ledger_set(g, 0), ledger_set(g, 1), ledger_set(g, 2)
    abb_o2c = BASE + "abb/CAP-ORDER-TO-CASH"
    abb_cust = BASE + "abb/CAP-CUSTOMER-DATA"
    assert cl0 == set(), "epoch 0 is the empty ledger"
    assert cl1 == {("CAP-ORDER-TO-CASH", abb_o2c)}
    assert cl0 < cl1, "Cl_1 strictly contains Cl_0"
    assert cl1 < cl2 and cl2 == {("CAP-ORDER-TO-CASH", abb_o2c), ("CAP-CUSTOMER-DATA", abb_cust)}
    # every coverage in every epoch is LIVE here: growth is attributable to chains that hold
    assert live_set(g, 1) == cl1 and live_set(g, 2) == cl2
    assert refusals(run_gates(g, {s: IC_GATE[s] for s in CHAIN})) == {}


def test_after_admitting_epoch1_closure_next_carries_the_coverage_forward_and_the_ledger_is_stable(
    journey: Journey,
) -> None:
    rows = journey.after_admit.rows20
    assert [(r["source"], r["capabilityKey"], r["state"], r["nextEpoch"]) for r in rows] == [
        ("carried", "CAP-ORDER-TO-CASH", "LIVE", "2"),
    ]
    carried = build([journey.after_admit.graph, journey.after_admit.ic_out["closure-next"]])
    assert ledger_set(carried, 2) == ledger_set(carried, 1) == {("CAP-ORDER-TO-CASH", BASE + "abb/CAP-ORDER-TO-CASH")}


def test_the_second_turn_grows_the_ledger_again_and_keeps_the_first_coverage(journey: Journey) -> None:
    rows = journey.turn2.rows20
    assert [(r["source"], r["capabilityKey"], r["state"], r["nextEpoch"]) for r in rows] == [
        ("frontier", "CAP-CUSTOMER-DATA", "LIVE", "2"),   # rows are ordered by capability key
        ("carried", "CAP-ORDER-TO-CASH", "LIVE", "2"),
    ]
    assert journey.turn2.classes.keys() == {R_INT, R_PRICE, R_DO}


def test_dropping_a_recorded_coverage_from_the_next_snapshot_is_a_closure_shrink(journey: Journey) -> None:
    g = journey.final_court
    o2c_cov_epoch2 = next(
        cov for cov in g.subjects(ic("inSnapshot"), URIRef(BASE + "snapshot/2"))
        if next(g.objects(cov, ic("coversCapability"))) == journey.consumer.cap_iri("CAP-ORDER-TO-CASH")
    )
    damaged = build([g])
    for p, o in list(damaged.predicate_objects(o2c_cov_epoch2)):
        damaged.remove((o2c_cov_epoch2, p, o))
    # the coverage recorded in epoch 1 is gone from epoch 2, so the monotonicity gate must fire
    assert ledger_set(damaged, 1) - ledger_set(damaged, 2) == {("CAP-ORDER-TO-CASH", BASE + "abb/CAP-ORDER-TO-CASH")}
    reasons = {r for _, r in S.gate_rows(damaged, IC_GATE["040_closure_monotonicity"])}
    assert reasons == {"REFUSED:IC_CLOSURE_SHRINK"}


def test_a_receipted_reasoned_retirement_makes_that_removal_lawful(journey: Journey) -> None:
    g = journey.final_court
    cov1 = next(
        cov for cov in g.subjects(ic("inSnapshot"), URIRef(BASE + "snapshot/1"))
    )
    cov2 = next(
        cov for cov in g.subjects(ic("inSnapshot"), URIRef(BASE + "snapshot/2"))
        if next(g.objects(cov, ic("coversCapability"))) == next(g.objects(cov1, ic("coversCapability")))
    )
    damaged = build([g])
    for p, o in list(damaged.predicate_objects(cov2)):
        damaged.remove((cov2, p, o))
    ret = URIRef(IND + "retirement/o2c")
    damaged.add((ret, RDF.type, ic("Retirement")))
    damaged.add((ret, ic("retires"), cov1))
    damaged.add((ret, ic("receiptDigest"), Literal(sha("spine:retirement"))))
    damaged.add((ret, ic("retirementReason"), Literal("capability decommissioned by a named decision")))
    assert S.gate_rows(damaged, IC_GATE["040_closure_monotonicity"]) == []


# ---------------------------------------------------------------------------
# Authority fence and standing across everything generated
# ---------------------------------------------------------------------------

def test_the_do_requirement_stays_blocked_in_every_ledger_and_packet_to_the_end(journey: Journey) -> None:
    for run in journey.all_runs:
        assert run.classes[R_DO] == "DEFICIT_AUTHORITY"
        item = next(i for i in run.packet["items"] if i["workOrderId"] == "SJ-" + R_DO)
        assert item["targetCode"] == "UPSTREAM_AUTHORITY" and item["standing"] == "BLOCKED"
    g = journey.final_court
    residual = next(g.subjects(ic("residualKey"), Literal(R_DO)))
    assert list(g.objects(residual, ic("standing"))) == [Literal("BLOCKED")]
    assert list(g.objects(residual, ic("blockedReason"))) == [Literal("DO_AUTHORITY_REQUIRED")]
    assert list(g.objects(residual, ic("authorityClaim"))) == [Literal("NONE")]


GENERATED_FILES = {"eom/architecture-requirements", "eom/abb-skeletons", "ic/residual-ledger", "ic/sjira-workorders",
                   "ic/closure-next", "ic/feedback-packet"}
DO_TOKEN = re.compile(r"(?<![A-Za-z0-9_])DO(?![A-Za-z0-9_])")


def strip_comment_lines(text: str) -> str:
    """Template header comments may say 'no DO authority'; only emitted data is judged."""
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def test_no_generated_triple_carries_do_approved_alive_or_a_grant(journey: Journey) -> None:
    seen_files = set()
    for run in journey.all_runs:
        for name, text in run.all_text().items():
            seen_files.add(name)
            assert "APPROVED" not in text, name
            assert "ALIVE" not in text, name
            assert not DO_TOKEN.search(strip_comment_lines(text)), name
            assert "grantsDoAuthority" not in text, name
            if name.endswith("feedback-packet"):
                continue
            g = build([text])
            for s, p, o in g:
                assert o != ic("DO") and str(o).upper() != "DO", (name, s, p, o)
                assert p not in (ic("approvedBy"), ic("approvalReceipt"), ic("grantsDoAuthority")), (name, p)
                if p == ic("approvalStatus"):
                    assert o == ic("PENDING_HUMAN_APPROVAL"), (name, s, o)
                if p == ic("standing"):
                    assert str(o) in {"UNKNOWN", "BLOCKED"}, (name, s, o)
                if p == ic("authorityClaim"):
                    assert str(o) == "NONE", (name, s, o)
                if p == ic("authorityCeiling"):
                    assert str(o) in {"NONE", "OBSERVE", "SELECT", "CONSTRUCT"}, (name, s, o)
    assert seen_files == GENERATED_FILES


def test_every_standing_in_the_final_court_graph_is_below_alive(journey: Journey) -> None:
    g = journey.final_court
    standings = {str(o) for o in g.objects(None, ic("standing"))}
    assert standings <= {"UNKNOWN", "BLOCKED"}, standings


# ---------------------------------------------------------------------------
# All gates of both packs on the final graph
# ---------------------------------------------------------------------------

def test_all_ic_gates_and_all_eom_gates_return_zero_rows_on_the_final_graph(journey: Journey) -> None:
    g = journey.final_court
    assert len(IC_GATES) == 11 and len(EOM_GATES) == 8
    ic_rows = run_gates(g, IC_GATE)
    eom_rows = run_gates(g, EOM_GATE)
    assert refusals(ic_rows) == {}, refusals(ic_rows)
    assert refusals(eom_rows) == {}, refusals(eom_rows)
    # the final residual is exactly what no lane has touched: the gates are quiet because the ledger agrees
    assert journey.final_run.classes == {R_INT: "DEFICIT_CONTRACT", R_PRICE: "DEFICIT_ABB", R_DO: "DEFICIT_AUTHORITY"}


def test_every_intermediate_ledger_is_admitted_by_the_ic_gates(journey: Journey) -> None:
    for step in journey.walk1 + journey.walk2:
        # admit this step's own regenerated ledger and work orders onto its own world
        g = build([IC_ONTOLOGY, EOM_ONTOLOGY, step.run.graph, step.run.ic_out["residual-ledger"],
                   step.run.ic_out["sjira-workorders"]])
        assert refusals(run_gates(g, IC_GATE)) == {}, (step.deficit, step.work_order)
        assert refusals(run_gates(g, EOM_GATE)) == {}, (step.deficit, step.work_order)


def test_a_stale_ledger_is_refused_after_a_lane_acts_until_it_is_regenerated(journey: Journey) -> None:
    before, after = journey.walk1[0].run, journey.walk1[1].run
    g = build([after.graph, before.ic_out["residual-ledger"], before.ic_out["sjira-workorders"]])
    reasons = {r for _, r in S.gate_rows(g, IC_GATE["060_residual_ledger"])}
    assert "REFUSED:IC_RESIDUAL_STALE_OR_MISCLASSIFIED" in reasons
    fresh = build([after.graph, after.ic_out["residual-ledger"], after.ic_out["sjira-workorders"]])
    assert S.gate_rows(fresh, IC_GATE["060_residual_ledger"]) == []


# ---------------------------------------------------------------------------
# Fixed point and byte-identical replay
# ---------------------------------------------------------------------------

def test_pass2_is_a_fixed_point_once_its_ledger_and_work_orders_are_admitted(journey: Journey) -> None:
    c = journey.consumer
    again = execute(c, with_ledger=True)
    final = journey.final_run
    for name in ("residual-ledger", "sjira-workorders", "feedback-packet"):
        assert again.ic_out[name] == final.ic_out[name], name
    assert again.eom == final.eom
    # closure-next proposes the next epoch with the same coverage set: the ledger no longer changes
    nxt = build([again.graph, again.ic_out["closure-next"]])
    assert ledger_set(nxt, 3) == ledger_set(nxt, 2) == ledger_set(journey.final_court, 2) != set()


def test_jinja_proxy_a_second_full_run_is_byte_identical(journey: Journey) -> None:
    second = play()
    assert len(second.all_runs) == len(journey.all_runs)
    for i, (a, b) in enumerate(zip(journey.all_runs, second.all_runs)):
        assert a.all_text() == b.all_text(), i
    assert second.fingerprint() == journey.fingerprint()


def test_output_does_not_depend_on_triple_insertion_order(journey: Journey) -> None:
    shuffled = play(seed=7)
    assert shuffled.fingerprint() == journey.fingerprint()


def test_jinja_proxy_output_is_byte_identical_across_python_hash_seeds(journey: Journey) -> None:
    code = (
        "import sys; sys.path.insert(0, %r); import test_industry_closure_spine as T; "
        "print(T.play().fingerprint())" % str(TESTS)
    )
    prints = []
    for hash_seed in ("1", "424242"):
        done = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=True,
            env={**os.environ, "PYTHONHASHSEED": hash_seed},
        )
        prints.append(done.stdout.strip())
    assert prints[0] == prints[1] == journey.fingerprint()


# ---------------------------------------------------------------------------
# Spine-level consistency: a dangling closure is refused by gate 020, never silently dropped
# ---------------------------------------------------------------------------

def aimed_at_nowhere() -> Consumer:
    c = Consumer()
    decision = next(c.ent.subjects(RDF.type, URIRef(EOM_NS + "OperatingModelDecision")))
    c.ent.remove((decision, URIRef(EOM_NS + "targetClosure"), URIRef(CLOSURE)))
    c.ent.add((decision, URIRef(EOM_NS + "targetClosure"), URIRef("https://example.invalid/closure/nowhere")))
    return c


def test_the_spine_consistency_check_catches_a_decision_aimed_at_an_undeclared_closure() -> None:
    run = execute(aimed_at_nowhere())
    problems = closure_problems(run.graph)
    assert len(problems) == 1 + 3, problems          # the decision, plus the three requirements it generated
    assert any("targetClosure" in p for p in problems)
    # a base IRI that disagrees with the declared closure is caught too
    c = Consumer()
    decision = next(c.ent.subjects(RDF.type, URIRef(EOM_NS + "OperatingModelDecision")))
    c.ent.remove((decision, URIRef(EOM_NS + "targetBaseIri"), Literal(BASE)))
    c.ent.add((decision, URIRef(EOM_NS + "targetBaseIri"), Literal("https://example.invalid/closure/other/")))
    assert [p for p in closure_problems(execute(c).graph) if "targetBaseIri" in p]


def test_a_requirement_in_an_undeclared_closure_is_refused_not_silently_dropped() -> None:
    c = aimed_at_nowhere()
    run = execute(c)
    admit_ledger(c, run)
    court = court_graph(c, run)
    assert closure_problems(court), "the scenario really is incoherent"
    refused = refusals(run_gates(court, IC_GATE))
    # the dangling closure is refused by gate 020, once per requirement it strands (nothing vanishes silently)
    assert set(refused) == {"020_requirement_identity"}, refused
    codes = {reason for _, reason in refused["020_requirement_identity"]}
    assert codes == {"REFUSED:IC_REQUIREMENT_CLOSURE_UNDECLARED"}
    assert len(refused["020_requirement_identity"]) == 3
