"""Court A for packs/industry-closure-ledger-pack (Chicago style, real files, no mocks).

Real collaborators throughout: the real Turtle on disk parsed by rdflib, the
real SPARQL gates and queries executed by rdflib, the real gate-court structural
checker, the real marketplace catalog subprocess, and a Jinja2 proxy restricted
to the subset ggen's Tera also executes.

Standing of what this proves: PARTIAL_ALIVE for semantic source, admission and
authority fence under rdflib. Manufacture, execution and replay need a real ggen
binary and stay BLOCKED:ggen_binary_unavailable; template rendering here is a
PARTIAL proxy. Nothing here is ALIVE and no Level-5 claim is made.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tomllib
from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

TESTS = Path(__file__).resolve().parent
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))
ROOT = TESTS.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import ic_support as S  # noqa: E402
from scripts.check_gate_witness_courts import qualify  # noqa: E402

PACK = S.PACK
GATES = sorted((PACK / "gates").glob("*.rq"))
STEMS = [g.stem for g in GATES]
Q10 = PACK / "queries" / "10-residual.rq"
Q20 = PACK / "queries" / "20-closure-frontier.rq"
TEMPLATES = PACK / "templates"
GROWTH = PACK / "fixtures" / "closure-growth"
EXPECTED = PACK / "fixtures" / "expected"
OVERLAY = PACK / "qualification" / "project" / "ontology" / "industry-input.ttl"
EX = "https://example.invalid/synthetic/"
IC = S.IC

EXPECTED_STEMS = [
    "010_source_admission", "020_requirement_identity", "030_snapshot_identity", "040_closure_monotonicity",
    "050_coverage_chain", "055_frontier_recorded", "060_residual_ledger", "070_deficit_feedback",
    "080_authority_fence", "090_standing_evidence", "100_sjira_workorder",
]

GUARDED_TYPE = {
    "010_source_admission": "KnowledgeSource",
    "020_requirement_identity": "Requirement",
    "030_snapshot_identity": "ClosureSnapshot",
    "040_closure_monotonicity": "Coverage",
    "050_coverage_chain": "Coverage",
    "055_frontier_recorded": "Requirement",
    "060_residual_ledger": "Residual",
    "070_deficit_feedback": "Residual",
    "080_authority_fence": "WorkOrder",
    "090_standing_evidence": "ExecutionEvidence",
    "100_sjira_workorder": "WorkOrder",
}

# One intended violator per declared code, reviewed by hand against the fail
# witnesses (local name under the synthetic namespace, code without the prefix).
INTENDED = {
    "010_source_admission": {
        ("badAdmission", "IC_SOURCE_ADMISSION_INVALID"), ("badProvenance", "IC_SOURCE_PROVENANCE_MISSING"),
        ("badDigest", "IC_SOURCE_DIGEST_MALFORMED"), ("badVendored", "IC_SOURCE_NOT_VENDORED"),
        ("badScope", "IC_SOURCE_OUTSIDE_SCOPE"), ("badExcluded", "IC_SOURCE_EXCLUSION_UNREASONED"),
        ("badUnknown", "IC_SOURCE_UNKNOWN_NO_FALSIFIER"),
    },
    "020_requirement_identity": {
        ("reqMalformed", "IC_REQUIREMENT_MALFORMED"), ("reqUnsafe", "IC_KEY_UNSAFE"), ("capUnsafe", "IC_KEY_UNSAFE"),
        ("capNoKey", "IC_CAPABILITY_KEY_MISSING"), ("reqBadDisposition", "IC_REQUIREMENT_DISPOSITION_INVALID"),
        ("reqSilentDrop", "IC_REQUIREMENT_SILENT_DROP"), ("reqDup1", "IC_REQUIREMENT_DUPLICATE_ID"),
        ("reqProse", "IC_REQUIREMENT_ORIGIN_UNADMITTED"), ("reqNoClosure", "IC_REQUIREMENT_CLOSURE_UNDECLARED"),
        ("reqNeedsDoString", "IC_NEEDS_DO_MALFORMED"),
    },
    "030_snapshot_identity": {
        ("closureNoSnap", "IC_CLOSURE_NO_SNAPSHOT"), ("snapNoEpoch", "IC_SNAPSHOT_EPOCH_MISSING"),
        ("snapOrphanEpoch", "IC_SNAPSHOT_ORPHAN"), ("snapNoClosure", "IC_SNAPSHOT_ORPHAN"),
        ("snapSkip", "IC_SNAPSHOT_EPOCH_SKIP"), ("snapB0", "IC_SNAPSHOT_FORK"),
        ("snapMismatch", "IC_SNAPSHOT_CLOSURE_MISMATCH"), ("closureD", "IC_SNAPSHOT_MULTIPLE_HEADS"),
        ("snapD0a", "IC_SNAPSHOT_EPOCH_DUPLICATE"), ("closureBadBase", "IC_CLOSURE_BASEIRI_INVALID"),
        ("closureNoBase", "IC_CLOSURE_BASEIRI_INVALID"),
    },
    "040_closure_monotonicity": {
        ("covCs0", "IC_CLOSURE_SHRINK"), ("retNowhere", "IC_RETIREMENT_MALFORMED"),
        ("retDNoReceipt", "IC_RETIREMENT_UNRECEIPTED"), ("retENoReason", "IC_RETIREMENT_UNREASONED"),
        ("retBadDigest", "IC_RETIREMENT_DIGEST_MALFORMED"),
    },
    "050_coverage_chain": {
        ("covInc", "IC_COVERAGE_INCOMPLETE"), ("covState", "IC_COVERAGE_STATE_INVALID"),
        ("covNotRealizing", "IC_COVERAGE_ABB_NOT_REALIZING"), ("covPending", "IC_COVERAGE_CONTRACT_NOT_APPROVED"),
        ("covMismatch", "IC_COVERAGE_SBB_MISMATCH"), ("covNotQualified", "IC_COVERAGE_SBB_NOT_QUALIFIED"),
        ("covUnpinned", "IC_COVERAGE_SBB_UNPINNED"), ("sbbMf", "IC_SBB_SUBJECT_MALFORMED"),
        ("covNoEvidence", "IC_COVERAGE_EVIDENCE_MISSING"), ("covFalsified", "IC_COVERAGE_EVIDENCE_FALSIFIED"),
        ("covStaleUnreasoned", "IC_COVERAGE_STALE_UNREASONED"),
        ("sbbAmb", "IC_SBB_SUBJECT_AMBIGUOUS"),
    },
    "055_frontier_recorded": {("capB", "IC_FRONTIER_UNRECORDED")},
    "060_residual_ledger": {
        ("reqU", "IC_RESIDUAL_UNRECORDED"), ("resM", "IC_RESIDUAL_STALE_OR_MISCLASSIFIED"),
        ("resOrphan", "IC_RESIDUAL_ORPHAN"), ("resA", "IC_RESIDUAL_DUPLICATE_KEY"), ("resD", "IC_RESIDUAL_DUPLICATE_KEY"),
    },
    "070_deficit_feedback": {
        ("resUnclassified", "IC_RESIDUAL_UNCLASSIFIED"), ("resMulti", "IC_RESIDUAL_MULTICLASS"),
        ("resNoFeedback", "IC_RESIDUAL_NO_FEEDBACK"), ("resMisrouted", "IC_FEEDBACK_MISROUTED"),
        ("resNotBlocked", "IC_AUTHORITY_BLOCK_NOT_BLOCKED"), ("resUnreasoned", "IC_AUTHORITY_BLOCK_UNREASONED"),
        ("resPromoted", "IC_RESIDUAL_STANDING_PROMOTED"),
    },
    "080_authority_fence": {
        ("doObject", "IC_AUTHORITY_DO_FORBIDDEN"), ("doLiteral", "IC_AUTHORITY_DO_FORBIDDEN"),
        ("doGrant", "IC_AUTHORITY_DO_FORBIDDEN"), ("doGrantString", "IC_AUTHORITY_DO_FORBIDDEN"), ("badCeiling", "IC_AUTHORITY_CEILING_INVALID"),
        ("woNoClaim", "IC_AUTHORITY_CLAIM_MISSING"), ("resNoClaim", "IC_AUTHORITY_CLAIM_MISSING"),
        ("woClaimSelect", "IC_AUTHORITY_CLAIM_NOT_NONE"), ("kUnattributed", "IC_CONTRACT_APPROVAL_UNATTRIBUTED"),
    },
    "090_standing_evidence": {
        ("badStanding", "IC_STANDING_INVALID"), ("covAliveNoEv", "IC_STANDING_ALIVE_WITHOUT_EVIDENCE"),
        ("covStaleSubject", "IC_STANDING_STALE_SUBJECT"), ("covSynthAlive", "IC_STANDING_SYNTHETIC_ALIVE"),
        ("covPackUnbound", "IC_STANDING_ALIVE_PACK_UNBOUND"), ("evMalformed", "IC_EVIDENCE_MALFORMED"),
        ("evBadReceipt", "IC_EVIDENCE_MALFORMED"), ("evSelfVerified", "IC_EVIDENCE_NOT_INDEPENDENT"),
        ("evFuFals", "IC_EVIDENCE_FALSIFICATION_UNFED"),
        ("covAliveStale", "IC_STANDING_ALIVE_NOT_LIVE"), ("covAliveFalsified", "IC_STANDING_ALIVE_FALSIFIED"),
        ("covForeign", "IC_STANDING_EVIDENCE_FOREIGN"),
    },
    "100_sjira_workorder": {
        ("resM", "IC_WORKORDER_MISSING"), ("woresW", "IC_WORKORDER_MALFORMED"), ("woresF", "IC_WORKORDER_FALSIFIER_BLANK"),
        ("woDup", "IC_WORKORDER_DUPLICATE_ID"), ("woOrphan", "IC_WORKORDER_ORPHAN"),
        ("woresX", "IC_WORKORDER_DELTA_MISMATCH"), ("woresP", "IC_WORKORDER_STANDING_PROMOTED"),
        ("woresA", "IC_WORKORDER_DUPLICATE_FOR_RESIDUAL"),
    },
}


def gate(stem: str) -> Path:
    return PACK / "gates" / f"{stem}.rq"


def stage_file(n: int) -> Path:
    matches = sorted(GROWTH.glob(f"stage{n}-*.ttl"))
    assert len(matches) == 1, f"stage{n}: {matches}"
    return matches[0]


def stage_world(n: int) -> Graph:
    return S.world(stage_file(n))


def local(iri: str) -> str:
    return iri[len(EX):] if iri.startswith(EX) else iri


PFX = f"""@prefix ic: <{IC}> .
@prefix ea: <{S.EA}> .
@prefix ex: <{EX}> .
@prefix prov: <http://www.w3.org/ns/prov#> .
"""


def digest(label: str) -> str:
    import hashlib

    return "sha256:" + hashlib.sha256(label.encode()).hexdigest()


def classes(graph: Graph, query: Path = Q10) -> dict[str, str]:
    """rkey -> deficit class code for the computed residual."""
    return {row["rkey"]: row["classCode"] for row in S.query_rows(graph, query)}


def run_all(graph: Graph, stems: list[str]) -> dict[str, list[tuple[str, str]]]:
    return {stem: S.gate_rows(graph, gate(stem)) for stem in stems}


def render_all(graph: Graph) -> dict[str, str]:
    rows10 = S.query_rows(graph, Q10)
    rows20 = S.query_rows(graph, Q20)
    return {
        "residual-ledger": S.render(TEMPLATES / "residual-ledger.ttl.tera", rows10),
        "sjira-workorders": S.render(TEMPLATES / "sjira-workorders.ttl.tera", rows10),
        "closure-next": S.render(TEMPLATES / "closure-next.ttl.tera", rows20),
        "feedback-packet": S.render(TEMPLATES / "feedback-packet.json.tera", rows10),
    }


# ---------------------------------------------------------------------------
# 1. Structure
# ---------------------------------------------------------------------------

def test_pack_manifest_is_minimal_and_matches_directory() -> None:
    payload = tomllib.loads((PACK / "pack.toml").read_text(encoding="utf-8"))
    assert set(payload) == {"pack"}
    pack = payload["pack"]
    assert set(pack) == {"name", "version", "description"}
    assert pack["name"] == PACK.name == "industry-closure-ledger-pack"
    assert re.fullmatch(r"\d+\.\d+\.\d+", pack["version"])
    assert pack["description"].strip()


def test_declared_profile_inputs_exist_and_no_symlinks() -> None:
    assert (PACK / "ggen.toml").is_file()
    assert list(PACK.glob("*.ttl")) and (PACK / "ontology.ttl").is_file()
    for current, dirs, files in os.walk(PACK):
        for name in [*dirs, *files]:
            assert not (Path(current) / name).is_symlink(), f"symlink: {Path(current) / name}"
    assert not list((PACK / "templates").glob("*")) == [], "templates present"


def test_gate_and_template_directories_hold_only_their_kind() -> None:
    assert {p.suffix for p in (PACK / "gates").iterdir()} == {".rq"}
    assert all(p.name.endswith(".tera") for p in TEMPLATES.iterdir())
    assert {p.suffix for p in (PACK / "queries").iterdir()} == {".rq"}
    assert STEMS == EXPECTED_STEMS


def test_ontology_carries_vocabulary_only_and_no_specimen_abox() -> None:
    graph = Graph().parse(S.ONTOLOGY, format="turtle")
    value_classes = {
        URIRef(IC + n) for n in ("AdmissionState", "ScopeDisposition", "CoverageState", "EvidenceOutcome",
                                 "EvidenceKind", "ApprovalStatus", "DeficitClass", "FeedbackTarget")
    }
    domain_classes = {
        URIRef(IC + n) for n in ("IndustryClosure", "KnowledgeSource", "Requirement", "ClosureSnapshot", "Coverage",
                                 "Retirement", "ExecutionEvidence", "Residual", "WorkOrder")
    }
    for cls in domain_classes:
        assert not list(graph.subjects(RDF.type, cls)), f"specimen instance of {cls}"
    typed = {o for _, _, o in graph.triples((None, RDF.type, None))}
    assert not (typed & domain_classes)
    assert typed & value_classes
    assert "example.invalid" not in S.ONTOLOGY.read_text(encoding="utf-8")


def test_no_do_vocabulary_is_declared() -> None:
    graph = Graph().parse(S.ONTOLOGY, format="turtle")
    assert (URIRef(IC + "DO"), None, None) not in graph
    for s, p, o in graph:
        assert str(s) != IC + "DO" and str(o) != IC + "DO"
        assert not (isinstance(o, Literal) and str(o).strip().upper() == "DO")


def test_seven_deficit_classes_route_by_data() -> None:
    graph = Graph().parse(S.ONTOLOGY, format="turtle")
    got = {
        local_name(row["code"]): (local_name(row["target"]), str(row["delta"]))
        for row in graph.query(
            f"SELECT ?code ?target ?delta WHERE {{ ?c a <{IC}DeficitClass> ; <{IC}routesTo> ?target ; <{IC}deltaCode> ?delta "
            f"BIND(?c AS ?code) }}"
        )
    }
    assert got == {
        "DEFICIT_AUTHORITY": ("UPSTREAM_AUTHORITY", "AUTHORITY_BLOCK"),
        "DEFICIT_ONTOLOGY": ("UPSTREAM_KNOWLEDGE", "ONTOLOGY_DELTA"),
        "DEFICIT_ABB": ("UPSTREAM_ARCHITECTURE", "ARCHITECTURE_DELTA"),
        "DEFICIT_CONTRACT": ("UPSTREAM_ARCHITECTURE", "ARCHITECTURE_DELTA"),
        "DEFICIT_SBB": ("UPSTREAM_MARKETPLACE", "PACK_DELTA"),
        "DEFICIT_QUALIFICATION": ("UPSTREAM_QUALIFICATION", "QUALIFICATION_DELTA"),
        "DEFICIT_EVIDENCE": ("UPSTREAM_QUALIFICATION", "COURT_DELTA"),
    }
    sbb_text = str(next(graph.objects(URIRef(IC + "DEFICIT_SBB"), URIRef(IC + "acceptanceText"))))
    assert "extend" in sbb_text.lower() and "new pack" in sbb_text.lower()
    # Every declared code is spelled identically as a literal and as the local name.
    for cls in graph.subjects(RDF.type, URIRef(IC + "DeficitClass")):
        assert str(next(graph.objects(cls, URIRef(IC + "deficitCode")))) == local_name(str(cls))
    for target in graph.subjects(RDF.type, URIRef(IC + "FeedbackTarget")):
        assert str(next(graph.objects(target, URIRef(IC + "targetCode")))) == local_name(str(target))


def local_name(iri) -> str:
    return str(iri).split("#")[-1]


def test_ggen_toml_binds_existing_files_under_a_scoped_output_dir() -> None:
    config = tomllib.loads((PACK / "ggen.toml").read_text(encoding="utf-8"))
    assert config["ontology"]["source"] == "ontology.ttl"
    assert config["ontology"]["imports"] == ["ontology/industry-input.ttl"]
    assert (PACK / "ontology" / "industry-input.ttl").is_file()
    rules = config["generation"]["rules"]
    assert [r["name"] for r in rules] == ["residual-ledger", "sjira-workorders", "closure-next", "feedback-packet"]
    used_templates = set()
    for rule in rules:
        assert (PACK / rule["query"]["file"]).is_file()
        assert (PACK / rule["template"]["file"]).is_file()
        used_templates.add(rule["template"]["file"])
        out = rule["output_file"]
        assert out.startswith("generated/industry-closure/") and ".." not in out
        assert rule["skip_empty"] is False and rule["mode"] == "Overwrite"
    assert used_templates == {f"templates/{p.name}" for p in TEMPLATES.iterdir()}


def test_empty_input_contract_parses_and_adds_no_triples() -> None:
    graph = Graph().parse(PACK / "ontology" / "industry-input.ttl", format="turtle")
    assert len(graph) == 0


# ---------------------------------------------------------------------------
# 2. Gate court
# ---------------------------------------------------------------------------

def test_gate_witness_stem_correspondence_is_alive() -> None:
    record = qualify(PACK)
    assert record["standing"] == "ALIVE" and record["case_count"] == len(EXPECTED_STEMS)


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_pass_witness_returns_zero_rows_and_is_not_vacuous(stem: str) -> None:
    graph = S.world(PACK / "witnesses" / "pass" / f"{stem}.ttl")
    guarded = URIRef(IC + GUARDED_TYPE[stem])
    witness_only = Graph().parse(PACK / "witnesses" / "pass" / f"{stem}.ttl", format="turtle")
    assert list(witness_only.subjects(RDF.type, guarded)), f"vacuous pass witness: no {guarded}"
    assert S.gate_rows(graph, gate(stem)) == []


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_fail_witness_triggers_exactly_the_declared_codes(stem: str) -> None:
    declared = S.declared_codes(gate(stem).read_text(encoding="utf-8"))
    assert declared, "a gate with no REFUSED literal refuses nothing"
    rows = S.gate_rows(S.world(PACK / "witnesses" / "fail" / f"{stem}.ttl"), gate(stem))
    assert {reason for _, reason in rows} == declared


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_every_declared_code_is_hit_by_its_intended_violator(stem: str) -> None:
    rows = S.gate_rows(S.world(PACK / "witnesses" / "fail" / f"{stem}.ttl"), gate(stem))
    got = {(local(subject), reason.removeprefix("REFUSED:")) for subject, reason in rows}
    missing = INTENDED[stem] - got
    assert not missing, f"intended violator not refused: {sorted(missing)}"
    declared = {c.removeprefix("REFUSED:") for c in S.declared_codes(gate(stem).read_text(encoding="utf-8"))}
    assert {code for _, code in INTENDED[stem]} == declared


def test_fail_witness_is_pass_witness_plus_violators() -> None:
    for stem in EXPECTED_STEMS:
        base = Graph().parse(PACK / "witnesses" / "pass" / f"{stem}.ttl", format="turtle")
        worse = Graph().parse(PACK / "witnesses" / "fail" / f"{stem}.ttl", format="turtle")
        assert len(worse) > len(base), stem


def test_gates_are_deterministic_and_read_only() -> None:
    for stem in EXPECTED_STEMS:
        source = gate(stem).read_text(encoding="utf-8")
        body = re.sub(r"(?m)^\s*#.*$", "", source)
        assert re.search(r"\bSELECT\s+\?subject\s+\?reason\b", body), stem
        assert re.search(r"ORDER BY \?subject \?reason\s*$", body.strip()), stem
        keywords = re.sub(r'"[^"\n]*"', '""', body)
        assert not re.search(r"\b(CONSTRUCT|INSERT|DELETE|DESCRIBE|LOAD|CLEAR|DROP|SERVICE)\b", keywords), stem
        world = S.world(PACK / "witnesses" / "fail" / f"{stem}.ttl")
        assert S.gate_rows(world, gate(stem)) == S.gate_rows(world, gate(stem))
        assert not re.search(r"\bVALUES\b", body), f"{stem}: VALUES is avoided for native-engine safety"


# ---------------------------------------------------------------------------
# 3. R_CORE equality
# ---------------------------------------------------------------------------

def test_r_core_is_byte_identical_modulo_whitespace() -> None:
    sources = {
        "queries/10-residual.rq": Q10,
        "queries/20-closure-frontier.rq": Q20,
        "gates/055_frontier_recorded.rq": gate("055_frontier_recorded"),
        "gates/060_residual_ledger.rq": gate("060_residual_ledger"),
    }
    blocks = {name: S.extract_r_core(path.read_text(encoding="utf-8")) for name, path in sources.items()}
    assert {name: len(b) for name, b in blocks.items()} == {
        "queries/10-residual.rq": 1, "queries/20-closure-frontier.rq": 1,
        "gates/055_frontier_recorded.rq": 1, "gates/060_residual_ledger.rq": 2,
    }
    reference = blocks["queries/10-residual.rq"][0]
    assert "ic:DEFICIT_AUTHORITY" in reference and "ic:COVERED" in reference
    for name, found in blocks.items():
        for block in found:
            assert block == reference, name


# ---------------------------------------------------------------------------
# 4. Golden residuals
# ---------------------------------------------------------------------------

STAGE_CLASS = {0: "DEFICIT_ABB", 1: "DEFICIT_CONTRACT", 2: "DEFICIT_SBB", 3: "DEFICIT_QUALIFICATION",
               4: "DEFICIT_EVIDENCE", 5: None, 6: "DEFICIT_EVIDENCE"}


@pytest.mark.parametrize("n", range(7))
def test_golden_residual_matches_stage_fixture(n: int) -> None:
    rows = S.query_rows(stage_world(n), Q10)
    golden = (EXPECTED / f"residual-stage{n}.json").read_text(encoding="utf-8")
    assert S.rows_json(rows) == golden
    expected = STAGE_CLASS[n]
    assert [r["classCode"] for r in rows] == ([expected] if expected else [])
    if expected:
        assert rows[0]["rkey"] == "REQ-A--CAP-A" and rows[0]["standing"] == "UNKNOWN"


@pytest.mark.parametrize("n", range(7))
def test_out_of_scope_requirement_is_absent_from_residual_but_justified(n: int) -> None:
    graph = stage_world(n)
    assert "REQ-OOS--" not in "".join(classes(graph))
    assert list(graph.objects(URIRef(EX + "reqOOS"), URIRef(IC + "scopeJustification")))


DO_REQ = f"""{PFX}
ex:capDO a ea:Capability ; ic:capabilityKey "CAP-DO" ; ic:groundedIn ex:srcA .
ex:reqDO a ic:Requirement ; ic:requirementId "REQ-DO" ; ic:statement "Autonomously perform a consequential action." ;
    ic:inClosure ex:closure ; ic:disposition ic:IN_SCOPE ; ic:requiresCapability ex:capDO ;
    ic:needsDoAuthority true ; ic:derivedFrom ex:srcA .
"""
UNMAPPED_REQ = f"""{PFX}
ex:reqUnmapped a ic:Requirement ; ic:requirementId "REQ-UNMAPPED" ; ic:statement "A requirement with no capability mapping." ;
    ic:inClosure ex:closure ; ic:disposition ic:IN_SCOPE ; ic:derivedFrom ex:srcA .
"""


@pytest.mark.parametrize("n", range(7))
def test_do_needing_requirement_is_authority_blocked_at_every_stage(n: int) -> None:
    graph = S.merged(stage_world(n), DO_REQ)
    rows = {r["rkey"]: r for r in S.query_rows(graph, Q10)}
    row = rows["REQ-DO--CAP-DO"]
    assert (row["classCode"], row["standing"], row["targetCode"]) == ("DEFICIT_AUTHORITY", "BLOCKED", "UPSTREAM_AUTHORITY")


@pytest.mark.parametrize("n", range(7))
def test_unmapped_requirement_is_ontology_deficit_at_every_stage(n: int) -> None:
    graph = S.merged(stage_world(n), UNMAPPED_REQ)
    rows = {r["rkey"]: r for r in S.query_rows(graph, Q10)}
    assert rows["REQ-UNMAPPED--UNMAPPED"]["classCode"] == "DEFICIT_ONTOLOGY"
    assert rows["REQ-UNMAPPED--UNMAPPED"]["capabilityKey"] == "UNMAPPED"


def test_ungrounded_capability_is_an_ontology_deficit() -> None:
    graph = S.merged(stage_world(2), f"""{PFX}
ex:capFree a ea:Capability ; ic:capabilityKey "CAP-FREE" .
ex:reqFree a ic:Requirement ; ic:requirementId "REQ-FREE" ; ic:statement "A capability grounded in nothing." ;
    ic:inClosure ex:closure ; ic:disposition ic:IN_SCOPE ; ic:requiresCapability ex:capFree ; ic:derivedFrom ex:srcA .
""")
    assert classes(graph)["REQ-FREE--CAP-FREE"] == "DEFICIT_ONTOLOGY"


def test_unapproved_or_boundaryless_contract_never_covers() -> None:
    graph = S.merged(stage_world(5), f"""{PFX}
ex:capNB a ea:Capability ; ic:capabilityKey "CAP-NB" ; ic:groundedIn ex:srcA .
ex:reqNB a ic:Requirement ; ic:requirementId "REQ-NB" ; ic:statement "Approved contract without an authority boundary." ;
    ic:inClosure ex:closure ; ic:disposition ic:IN_SCOPE ; ic:requiresCapability ex:capNB ; ic:derivedFrom ex:srcA .
ex:abbNB a ea:ArchitectureBuildingBlock ; ea:realizesCapability ex:capNB ; ea:governedByContract ex:kNB .
ex:kNB a ea:ArchitectureContract ; ic:approvalStatus ic:APPROVED ; ic:approvedBy ex:humanApprover ; ic:approvalReceipt "receipt:nb" .
""")
    assert classes(graph)["REQ-NB--CAP-NB"] == "DEFICIT_CONTRACT"


# Hardening of the classifier against two holes the plan text left open.

def test_verification_is_tied_to_the_approved_chain_not_to_any_abb() -> None:
    graph = S.merged(stage_world(4), f"""{PFX}
ex:abbRogue a ea:ArchitectureBuildingBlock ; ea:realizesCapability ex:capA ; ea:governedByContract ex:kRogue .
ex:kRogue a ea:ArchitectureContract ; ic:approvalStatus ic:PENDING_HUMAN_APPROVAL ; ea:hasAuthorityBoundary ex:boundaryRogue .
ex:boundaryRogue a ea:AuthorityBoundary .
ex:sbbRogue a ea:SolutionBuildingBlock ; ea:satisfiesABB ex:abbRogue ; ea:hasStanding ea:QUALIFIED ; ea:exactSubject "{digest('rogue')}" .
ex:evRogue a ic:ExecutionEvidence ; ic:evidenceFor ex:sbbRogue ; ic:evidenceSubject "{digest('rogue')}" ; ic:outcome ic:VERIFIED ;
    ic:receiptDigest "{digest('rogue-receipt')}" ; ic:producedBy ex:agentBuilder ; ic:verifiedBy ex:agentVerifier ; ic:evidenceKind ic:OBSERVED .
""")
    assert classes(graph)["REQ-A--CAP-A"] == "DEFICIT_EVIDENCE"


def test_self_verified_evidence_does_not_cover() -> None:
    graph = stage_world(5)
    ev = URIRef(EX + "evAV")
    graph.set((ev, URIRef(IC + "verifiedBy"), URIRef(EX + "agentBuilder")))
    assert classes(graph)["REQ-A--CAP-A"] == "DEFICIT_EVIDENCE"
    assert {r for _, r in S.gate_rows(graph, gate("090_standing_evidence"))} == {"REFUSED:IC_EVIDENCE_NOT_INDEPENDENT"}


# ---------------------------------------------------------------------------
# 5. Growth court
# ---------------------------------------------------------------------------

CHAIN_GATES = ["030_snapshot_identity", "040_closure_monotonicity", "050_coverage_chain", "055_frontier_recorded"]


def next_snapshot(graph: Graph) -> str:
    return S.render(TEMPLATES / "closure-next.ttl.tera", S.query_rows(graph, Q20))


def test_the_ledger_grows_stage_by_stage_and_every_admission_is_gated() -> None:
    previous_covered = 0
    for n in range(7):
        graph = stage_world(n)
        text = next_snapshot(graph)
        admitted = S.merged(graph, text)
        assert all(rows == [] for rows in run_all(admitted, CHAIN_GATES).values()), (n, run_all(admitted, CHAIN_GATES))
        covers = len(list(admitted.subjects(RDF.type, URIRef(IC + "Coverage"))))
        assert covers >= previous_covered
        previous_covered = covers
        if n == 5:
            assert covers == 1


def test_stage5_without_the_next_snapshot_is_refused_for_an_unrecorded_frontier() -> None:
    rows = S.gate_rows(stage_world(5), gate("055_frontier_recorded"))
    assert [reason for _, reason in rows] == ["REFUSED:IC_FRONTIER_UNRECORDED"]


def test_closure_next_proposes_epoch_plus_one_with_unknown_standing() -> None:
    text = next_snapshot(stage_world(5))
    admitted = S.merged(stage_world(5), text)
    snap = URIRef(EX + "snapshot/1")
    assert (snap, URIRef(IC + "epoch"), None) in admitted
    assert str(next(admitted.objects(snap, URIRef(IC + "epoch")))) == "1"
    assert (snap, URIRef(IC + "supersedes"), URIRef(EX + "snap0")) in admitted
    standings = {str(o) for o in admitted.objects(None, URIRef(IC + "standing"))}
    assert standings == {"UNKNOWN"}
    assert "APPROVED" not in text and "ALIVE" not in text


def admitted_stage5() -> Graph:
    return S.merged(stage_world(5), next_snapshot(stage_world(5)))


def coverage_iri(graph: Graph) -> URIRef:
    found = sorted(graph.subjects(RDF.type, URIRef(IC + "Coverage")))
    assert len(found) == 1
    return found[0]


SNAP2 = f"""{PFX}
<{EX}snapshot/2> a ic:ClosureSnapshot ; ic:snapshotOf ex:closure ; ic:epoch 2 ; ic:supersedes <{EX}snapshot/1> .
ex:closure ic:hasSnapshot <{EX}snapshot/2> .
"""


def test_deleting_a_coverage_is_a_closure_shrink() -> None:
    graph = S.merged(admitted_stage5(), SNAP2)
    rows = S.gate_rows(graph, gate("040_closure_monotonicity"))
    assert [reason for _, reason in rows] == ["REFUSED:IC_CLOSURE_SHRINK"]
    assert rows[0][0] == str(coverage_iri(graph))


def test_a_receipted_reasoned_retirement_makes_the_removal_lawful() -> None:
    base = admitted_stage5()
    cov = coverage_iri(base)
    graph = S.merged(base, SNAP2, f"""{PFX}
<{EX}retire/1> a ic:Retirement ; ic:retires <{cov}> ; ic:receiptDigest "{digest('retire-1')}" ;
    ic:retirementReason "The capability was withdrawn from the synthetic scope." .
""")
    assert S.gate_rows(graph, gate("040_closure_monotonicity")) == []


def test_an_unreceipted_retirement_is_refused() -> None:
    base = admitted_stage5()
    cov = coverage_iri(base)
    graph = S.merged(base, SNAP2, f"""{PFX}
<{EX}retire/1> a ic:Retirement ; ic:retires <{cov}> ; ic:retirementReason "No receipt was recorded." .
""")
    reasons = {reason for _, reason in S.gate_rows(graph, gate("040_closure_monotonicity"))}
    assert "REFUSED:IC_RETIREMENT_UNRECEIPTED" in reasons and "REFUSED:IC_CLOSURE_SHRINK" in reasons


def test_swapping_a_qualified_evidenced_sbb_on_the_same_abb_is_still_monotone() -> None:
    graph = S.merged(admitted_stage5(), SNAP2, f"""{PFX}
ex:sbbB a ea:SolutionBuildingBlock ; ea:satisfiesABB ex:abbA ; ea:hasStanding ea:QUALIFIED ; ea:exactSubject "{digest('subject-B')}" .
ex:evBV a ic:ExecutionEvidence ; ic:evidenceFor ex:sbbB ; ic:evidenceSubject "{digest('subject-B')}" ; ic:outcome ic:VERIFIED ;
    ic:receiptDigest "{digest('receipt-B')}" ; ic:producedBy ex:agentBuilder ; ic:verifiedBy ex:agentVerifier ; ic:evidenceKind ic:SYNTHETIC .
<{EX}coverage/2/swap> a ic:Coverage ; ic:inSnapshot <{EX}snapshot/2> ; ic:coversCapability ex:capA ; ic:byABB ex:abbA ;
    ic:bySBB ex:sbbB ; ic:coverageState ic:LIVE ; ic:standing "UNKNOWN" .
""")
    assert all(rows == [] for rows in run_all(graph, CHAIN_GATES).values())


def test_stage6_marks_the_coverage_stale_and_keeps_it() -> None:
    graph = stage_world(6)
    assert classes(graph) == {"REQ-A--CAP-A": "DEFICIT_EVIDENCE"}
    rows = S.query_rows(graph, Q20)
    assert [(r["source"], r["state"], r["staleBecause"]) for r in rows] == [("carried", "STALE", "EVIDENCE_NOT_CURRENT")]
    admitted = S.merged(graph, next_snapshot(graph))
    assert all(r == [] for r in run_all(admitted, CHAIN_GATES).values())
    states = sorted(str(o).split("#")[-1] for o in admitted.objects(None, URIRef(IC + "coverageState")))
    assert states == ["LIVE", "STALE"], "history keeps its LIVE record; the new snapshot carries the STALE one"
    assert len(list(admitted.subjects(RDF.type, URIRef(IC + "Coverage")))) == 2


def test_a_superseded_snapshots_live_coverage_is_history_not_a_current_claim() -> None:
    # stage6 holds a LIVE coverage in snapshot 1 beside FALSIFIED evidence. While snapshot 1 is the head
    # gate 050 refuses it; once snapshot 2 supersedes it the history is no longer re-judged.
    graph = stage_world(6)
    assert {r for _, r in S.gate_rows(graph, gate("050_coverage_chain"))} == {"REFUSED:IC_COVERAGE_EVIDENCE_FALSIFIED"}
    admitted = S.merged(graph, next_snapshot(graph))
    assert S.gate_rows(admitted, gate("050_coverage_chain")) == []


def test_head_snapshot_is_found_through_snapshot_of_even_without_has_snapshot() -> None:
    graph = S.merged(stage_world(5), f"""{PFX}
<{EX}snapshot/1> a ic:ClosureSnapshot ; ic:snapshotOf ex:closure ; ic:epoch 1 ; ic:supersedes ex:snap0 .
""")
    assert [r for _, r in S.gate_rows(graph, gate("055_frontier_recorded"))] == ["REFUSED:IC_FRONTIER_UNRECORDED"]


def test_regression_reopens_the_residual_without_shrinking_the_ledger() -> None:
    covered = stage_world(5)
    assert classes(covered) == {}
    regressed = stage_world(6)
    assert classes(regressed) == {"REQ-A--CAP-A": "DEFICIT_EVIDENCE"}


# ---------------------------------------------------------------------------
# 6. Fixed point
# ---------------------------------------------------------------------------

def test_jinja_proxy_residual_ledger_is_a_fixed_point_at_every_stage() -> None:
    for n in range(7):
        graph = stage_world(n)
        first = S.render(TEMPLATES / "residual-ledger.ttl.tera", S.query_rows(graph, Q10))
        merged = S.merged(graph, first)
        assert S.gate_rows(merged, gate("060_residual_ledger")) == [], n
        second = S.render(TEMPLATES / "residual-ledger.ttl.tera", S.query_rows(merged, Q10))
        assert second == first, n


def test_closing_a_residual_in_the_input_is_stale_until_regenerated() -> None:
    old_ledger = S.render(TEMPLATES / "residual-ledger.ttl.tera", S.query_rows(stage_world(1), Q10))
    after_approval = S.merged(stage_world(2), old_ledger)
    reasons = {r for _, r in S.gate_rows(after_approval, gate("060_residual_ledger"))}
    assert "REFUSED:IC_RESIDUAL_STALE_OR_MISCLASSIFIED" in reasons
    regenerated = S.render(TEMPLATES / "residual-ledger.ttl.tera", S.query_rows(stage_world(2), Q10))
    assert S.gate_rows(S.merged(stage_world(2), regenerated), gate("060_residual_ledger")) == []
    # a residual recorded for a now-covered capability is stale until regenerated
    ledger4 = S.render(TEMPLATES / "residual-ledger.ttl.tera", S.query_rows(stage_world(4), Q10))
    covered = S.merged(stage_world(5), ledger4)
    assert "REFUSED:IC_RESIDUAL_STALE_OR_MISCLASSIFIED" in {r for _, r in S.gate_rows(covered, gate("060_residual_ledger"))}
    empty = S.render(TEMPLATES / "residual-ledger.ttl.tera", S.query_rows(stage_world(5), Q10))
    assert S.gate_rows(S.merged(stage_world(5), empty), gate("060_residual_ledger")) == []


def test_qualification_overlay_passes_input_gates_and_generated_outputs_pass_the_rest() -> None:
    base = S.world(OVERLAY)
    assert base.query("ASK { ?s a ?o }")
    input_gates = ["010_source_admission", "020_requirement_identity", "030_snapshot_identity", "040_closure_monotonicity",
                   "050_coverage_chain", "055_frontier_recorded", "070_deficit_feedback", "080_authority_fence",
                   "090_standing_evidence"]
    assert all(rows == [] for rows in run_all(base, input_gates).values())
    unrecorded = S.gate_rows(base, gate("060_residual_ledger"))
    assert {local(s) for s, _ in unrecorded} == {"reqA", "reqB", "reqC", "reqD", "reqU"}
    outputs = render_all(base)
    assert classes(base) == {
        "REQ-A--CAP-A": "DEFICIT_ABB", "REQ-B--CAP-B": "DEFICIT_CONTRACT", "REQ-C--CAP-C": "DEFICIT_SBB",
        "REQ-D--CAP-D": "DEFICIT_AUTHORITY", "REQ-U--UNMAPPED": "DEFICIT_ONTOLOGY",
    }
    full = S.merged(base, outputs["residual-ledger"], outputs["sjira-workorders"], outputs["closure-next"])
    everything = [s for s in STEMS]
    assert all(rows == [] for rows in run_all(full, everything).values()), run_all(full, everything)
    # a second run on the same input is byte-identical
    assert render_all(base) == outputs
    # the merged input yields the same ledger, work orders and packet again
    again = render_all(S.merged(base, outputs["residual-ledger"], outputs["sjira-workorders"]))
    for name in ("residual-ledger", "sjira-workorders", "feedback-packet"):
        assert again[name] == outputs[name], name


def test_work_orders_project_each_residual_and_inherit_class_text() -> None:
    base = S.world(OVERLAY)
    outputs = render_all(base)
    graph = S.merged(base, outputs["residual-ledger"], outputs["sjira-workorders"])
    rows = graph.query(
        f"""SELECT ?id ?delta ?acc ?fal ?standing ?claim WHERE {{ ?w a <{IC}WorkOrder> ; <{IC}workOrderId> ?id ; <{IC}deltaCode> ?delta ;
        <{IC}acceptance> ?acc ; <{IC}falsifier> ?fal ; <{IC}standing> ?standing ; <{IC}authorityClaim> ?claim }} ORDER BY ?id"""
    )
    got = [(str(r["id"]), str(r["delta"]), str(r["standing"]), str(r["claim"])) for r in rows]
    assert got == [
        ("SJ-REQ-A--CAP-A", "ARCHITECTURE_DELTA", "UNKNOWN", "NONE"),
        ("SJ-REQ-B--CAP-B", "ARCHITECTURE_DELTA", "UNKNOWN", "NONE"),
        ("SJ-REQ-C--CAP-C", "PACK_DELTA", "UNKNOWN", "NONE"),
        ("SJ-REQ-D--CAP-D", "AUTHORITY_BLOCK", "BLOCKED", "NONE"),
        ("SJ-REQ-U--UNMAPPED", "ONTOLOGY_DELTA", "UNKNOWN", "NONE"),
    ]
    ontology = Graph().parse(S.ONTOLOGY, format="turtle")
    acceptance_texts = {str(o) for o in ontology.objects(None, URIRef(IC + "acceptanceText"))}
    assert {str(r["acc"]) for r in rows} <= acceptance_texts
    sbb = next(r for r in rows if str(r["id"]).startswith("SJ-REQ-C"))
    assert "extend or compose an existing pack" in str(sbb["acc"])


def test_feedback_packet_is_deterministic_json_without_authority() -> None:
    outputs = render_all(S.world(OVERLAY))
    packet = json.loads(outputs["feedback-packet"])
    assert packet["doAuthority"] is False and packet["authorityCeiling"] == "NONE" and packet["standing"] == "UNKNOWN"
    ids = [item["workOrderId"] for item in packet["items"]]
    assert ids == sorted(ids) and len(ids) == 5
    assert {i["targetCode"] for i in packet["items"]} == {
        "UPSTREAM_ARCHITECTURE", "UPSTREAM_MARKETPLACE", "UPSTREAM_AUTHORITY", "UPSTREAM_KNOWLEDGE"}
    blocked = [i for i in packet["items"] if i["targetCode"] == "UPSTREAM_AUTHORITY"]
    assert [b["standing"] for b in blocked] == ["BLOCKED"]
    empty = json.loads(S.render(TEMPLATES / "feedback-packet.json.tera", []))
    assert empty["items"] == []


def test_jinja_proxy_empty_results_render_valid_empty_outputs() -> None:
    for name in ("residual-ledger.ttl.tera", "sjira-workorders.ttl.tera", "closure-next.ttl.tera"):
        text = S.render(TEMPLATES / name, [])
        assert len(Graph().parse(data=text, format="turtle")) == 0


# ---------------------------------------------------------------------------
# 7. Evidence courts
# ---------------------------------------------------------------------------

def test_falsified_evidence_at_a_superseded_subject_is_not_joined() -> None:
    graph = S.merged(stage_world(5), f"""{PFX}
ex:evOld a ic:ExecutionEvidence ; ic:evidenceFor ex:sbbA ; ic:evidenceSubject "{digest('subject-A-previous')}" ; ic:outcome ic:FALSIFIED ;
    ic:receiptDigest "{digest('old-receipt')}" ; ic:producedBy ex:agentBuilder ; ic:verifiedBy ex:agentVerifier ; ic:evidenceKind ic:OBSERVED .
""")
    assert classes(graph) == {}
    assert S.gate_rows(graph, gate("090_standing_evidence")) == []


def test_falsified_evidence_at_the_current_subject_reopens_and_must_feed_an_open_residual() -> None:
    graph = stage_world(6)
    assert classes(graph) == {"REQ-A--CAP-A": "DEFICIT_EVIDENCE"}
    unfed = S.gate_rows(graph, gate("090_standing_evidence"))
    assert [reason for _, reason in unfed] == ["REFUSED:IC_EVIDENCE_FALSIFICATION_UNFED"]
    ledger = S.render(TEMPLATES / "residual-ledger.ttl.tera", S.query_rows(graph, Q10))
    assert S.gate_rows(S.merged(graph, ledger), gate("090_standing_evidence")) == []


def test_a_new_subject_discards_old_success() -> None:
    graph = stage_world(5)
    sbb = URIRef(EX + "sbbA")
    graph.set((sbb, URIRef(S.EA + "exactSubject"), Literal(digest("subject-A-next"))))
    assert classes(graph) == {"REQ-A--CAP-A": "DEFICIT_EVIDENCE"}


def alive_world() -> Graph:
    return S.world(PACK / "witnesses" / "pass" / "090_standing_evidence.ttl")


def reasons090(graph: Graph) -> set[str]:
    return {r for _, r in S.gate_rows(graph, gate("090_standing_evidence"))}


def test_alive_requires_current_independent_observed_evidence_and_a_bound_pack() -> None:
    assert reasons090(alive_world()) == set()
    stale = alive_world()
    stale.set((URIRef(EX + "sbbA"), URIRef(S.EA + "exactSubject"), Literal(digest("subject-A-bumped"))))
    assert reasons090(stale) == {"REFUSED:IC_STANDING_STALE_SUBJECT"}
    selfv = alive_world()
    selfv.set((URIRef(EX + "evAobs"), URIRef(IC + "verifiedBy"), URIRef(EX + "agentBuilder")))
    assert reasons090(selfv) == {"REFUSED:IC_EVIDENCE_NOT_INDEPENDENT"}
    synth = alive_world()
    synth.set((URIRef(EX + "evAobs"), URIRef(IC + "evidenceKind"), URIRef(IC + "SYNTHETIC")))
    assert reasons090(synth) == {"REFUSED:IC_STANDING_SYNTHETIC_ALIVE"}
    unbound = alive_world()
    unbound.remove((URIRef(EX + "sbbA"), URIRef(IC + "marketplacePack"), None))
    assert reasons090(unbound) == {"REFUSED:IC_STANDING_ALIVE_PACK_UNBOUND"}
    bad = alive_world()
    bad.set((URIRef(EX + "covAlive"), URIRef(IC + "standing"), Literal("SUCCESS")))
    assert reasons090(bad) == {"REFUSED:IC_STANDING_INVALID"}


def test_qualified_alone_is_not_alive_and_no_generated_standing_is_alive() -> None:
    assert classes(stage_world(4)) == {"REQ-A--CAP-A": "DEFICIT_EVIDENCE"}
    outputs = render_all(S.world(OVERLAY))
    for name, text in outputs.items():
        assert "ALIVE" not in text, name


# ---------------------------------------------------------------------------
# 8. Authority and honesty lints
# ---------------------------------------------------------------------------

TEMPLATE_FILES = sorted(TEMPLATES.glob("*.tera"))
QUERY_FILES = sorted((PACK / "queries").glob("*.rq"))


def strip_hash_comments(text: str) -> str:
    return re.sub(r"(?m)^\s*#.*$", "", text)


def test_templates_queries_and_config_hold_no_authority_grant() -> None:
    files = TEMPLATE_FILES + QUERY_FILES + [PACK / "ggen.toml"]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"grantsDoAuthority\s+true", text), path.name
        for value in re.findall(r"authorityClaim\s+(\"[^\"]*\"|\S+)", text):
            assert value == '"NONE"', (path.name, value)
        for value in re.findall(r"authorityCeiling\"?:?\s*(\"[^\"]*\"|\S+)", text):
            assert value.strip('"') in {"NONE", "OBSERVE", "SELECT", "CONSTRUCT"}, (path.name, value)
        assert not re.search(r"\bic:DO\b|\"DO\"", text), path.name


def test_templates_and_config_never_emit_the_approved_token() -> None:
    for path in TEMPLATE_FILES + [PACK / "ggen.toml"]:
        assert "APPROVED" not in path.read_text(encoding="utf-8"), path.name
    # queries only SELECT: they may read APPROVED to classify, never construct it
    for path in QUERY_FILES:
        body = strip_hash_comments(path.read_text(encoding="utf-8"))
        assert re.match(r"\s*PREFIX", body) and re.search(r"\bSELECT\b", body)
        assert not re.search(r"\b(CONSTRUCT|INSERT|DELETE|DESCRIBE)\b", body), path.name


VERSIONISH = [
    re.compile(r"ggen[\w\- ]{0,12}v?\d+\.\d+", re.I),
    re.compile(r"\b[0-9a-f]{40}\b"),
    re.compile(r"sha256:[0-9a-f]{64}"),
    re.compile(r"\b[0-9a-f]{64}\b"),
    re.compile(r"(min|required|ggen)[_\-]?(ggen[_\-]?)?version", re.I),
    re.compile(r"timeout|workers", re.I),
]


def test_no_hardcoded_ggen_version_commit_digest_or_bound() -> None:
    for path in TEMPLATE_FILES + QUERY_FILES + [PACK / "ggen.toml"]:
        text = path.read_text(encoding="utf-8")
        for pattern in VERSIONISH:
            assert not pattern.search(text), (path.name, pattern.pattern)


def test_templates_stay_inside_the_shared_tera_jinja_subset() -> None:
    for path in TEMPLATE_FILES:
        S.check_subset(path.read_text(encoding="utf-8"))
    for bad in ("{{ row.x | upper }}", "{% set y = 1 %}", "{% include 'x' %}", "{{ results|length }}", "{# c #}",
                "{% if row.x | length > 1 %}{% endif %}"):
        with pytest.raises(S.TemplateSubsetError):
            S.check_subset(bad)


def test_every_generated_standing_is_unknown_or_blocked_and_claims_none() -> None:
    outputs = render_all(S.world(OVERLAY))
    graph = Graph()
    for name in ("residual-ledger", "sjira-workorders", "closure-next"):
        graph.parse(data=outputs[name], format="turtle")
    standings = {str(o) for o in graph.objects(None, URIRef(IC + "standing"))}
    assert standings <= {"UNKNOWN", "BLOCKED"} and standings
    assert {str(o) for o in graph.objects(None, URIRef(IC + "authorityClaim"))} == {"NONE"}
    assert not [t for t in graph if "DO" in {str(t[2]).split("#")[-1], str(t[2])}]
    blocked = [s for s, _, o in graph.triples((None, URIRef(IC + "standing"), None))
               if str(o) == "BLOCKED" and (s, RDF.type, URIRef(IC + "Residual")) in graph]
    assert blocked and all((s, URIRef(IC + "blockedReason"), None) in graph for s in blocked)


# ---------------------------------------------------------------------------
# 9. Drift guards
# ---------------------------------------------------------------------------

def test_every_ea_term_used_exists_in_the_enterprise_architecture_pack_ontology() -> None:
    ea_pack = Graph().parse(PACKS_EA, format="turtle")
    known = {str(t) for triple in ea_pack for t in triple if isinstance(t, URIRef)}
    used: set[str] = set()
    for path in [*GATES, *QUERY_FILES, *TEMPLATE_FILES]:
        used |= set(re.findall(r"\bea:([A-Za-z][A-Za-z0-9]*)", strip_hash_comments(path.read_text(encoding="utf-8"))))
    assert used, "the gates must consume ea: terms"
    missing = sorted(name for name in used if S.EA + name not in known)
    assert not missing, f"ea: terms absent from enterprise-architecture-pack/ontology.ttl: {missing}"


PACKS_EA = S.PACKS / "enterprise-architecture-pack" / "ontology.ttl"


def test_togaf_anchor_and_ea_namespace_match_their_owners() -> None:
    togaf_owner = Graph().parse(S.PACKS / "togaf-adm-pack" / "ontology.ttl", format="turtle")
    assert dict(togaf_owner.namespaces())["togaf"] == URIRef(S.TOGAF)
    ea_owner = Graph().parse(PACKS_EA, format="turtle")
    assert dict(ea_owner.namespaces())["ea"] == URIRef(S.EA)
    for path in [*GATES, *QUERY_FILES]:
        text = path.read_text(encoding="utf-8")
        assert f"PREFIX ea: <{S.EA}>" in text, path.name
        assert f"PREFIX ic: <{IC}>" in text, path.name
        assert "PREFIX eap:" not in text


def test_ic_prefix_is_not_redeclared_for_foreign_vocabulary() -> None:
    ontology = S.ONTOLOGY.read_text(encoding="utf-8")
    assert "@prefix ea:" not in ontology and "@prefix eap:" not in ontology and "enterprise-architecture" not in ontology.replace(
        "enterprise-architecture vocabulary", "").replace("enterprise-architecture-pack", "")


# ---------------------------------------------------------------------------
# 10. Branch-binding lint
# ---------------------------------------------------------------------------

def test_every_union_branch_binds_subject_first() -> None:
    seen = 0
    for path in GATES:
        for branch in S.union_branches(path.read_text(encoding="utf-8")):
            seen += 1
            if S.first_pattern_binds_subject(branch):
                continue
            # the one lawful exception: a branch that opens with the R_CORE classifier block
            # (it cannot bind ?subject first) and binds ?subject explicitly afterwards
            assert branch.startswith("?closure a ic:IndustryClosure") and "AS ?subject" in branch, \
                f"{path.name}: {branch[:80]!r}"
    assert seen > 50


def test_lint_rejects_a_branch_that_does_not_bind_subject_first() -> None:
    source = "SELECT ?subject ?reason WHERE { { ?x a ?y . ?subject a ?z BIND('a' AS ?reason) } UNION { ?subject a ?y BIND('b' AS ?reason) } }"
    branches = S.union_branches(source)
    assert [S.first_pattern_binds_subject(b) for b in branches] == [False, True]


# ---------------------------------------------------------------------------
# 11-12. Catalog
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def catalog_raw() -> bytes:
    return S.catalog_bytes()


def test_catalog_lists_the_pack_deterministically(catalog_raw: bytes) -> None:
    assert S.catalog_bytes() == catalog_raw
    entry = S.catalog_entries(catalog_raw)["industry-closure-ledger-pack"]
    assert entry["profile"] == "project"
    assert entry["native_gates"] == len(EXPECTED_STEMS)
    assert entry["templates"] == len(TEMPLATE_FILES)
    assert entry["readiness"]["gates"] and entry["readiness"]["witnesses"]
    assert entry["digest"].startswith("sha256:")
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from marketplace import PACK_CLASSES
    finally:
        sys.path.remove(str(ROOT / "scripts"))

    assert entry["pack_class"] == PACK_CLASSES.get("industry-closure-ledger-pack")
    assert PACK_CLASSES.get("industry-closure-ledger-pack", "KernelPack") == "KernelPack"


def test_catalog_binding_marks_a_mismatched_bound_sbb_stale(catalog_raw: bytes) -> None:
    entries = S.catalog_entries(catalog_raw)
    current = entries["industry-closure-ledger-pack"]["digest"]
    graph = S.merged(Graph(), f"""{PFX}
ex:sbbCurrent a ea:SolutionBuildingBlock ; ic:marketplacePack "industry-closure-ledger-pack" ; ic:packDigest "{current}" .
ex:sbbDrift a ea:SolutionBuildingBlock ; ic:marketplacePack "industry-closure-ledger-pack" ; ic:packDigest "{digest('drifted')}" .
ex:sbbGhost a ea:SolutionBuildingBlock ; ic:marketplacePack "no-such-pack" ; ic:packDigest "{digest('ghost')}" .
ex:sbbUnbound a ea:SolutionBuildingBlock .
""")
    bound = S.bound_sbbs(graph)
    assert [local(s) for s, _, _ in bound] == ["sbbCurrent", "sbbDrift", "sbbGhost"]
    status = {local(s): S.binding_status(p, d, entries) for s, p, d in bound}
    assert status == {
        "sbbCurrent": ("LIVE", ""),
        "sbbDrift": ("STALE", "PACK_DIGEST_MISMATCH"),
        "sbbGhost": ("STALE", "PACK_NOT_IN_CATALOG"),
    }


# ---------------------------------------------------------------------------
# 13. Adversarial-review regressions (each pins a defect a reviewer reproduced)
# ---------------------------------------------------------------------------

def mutated(graph: Graph, *, remove: "list[tuple[str, str, object]]" = (), add: str = "") -> Graph:
    """A copy of ``graph`` with the given triples removed and Turtle added."""
    out = S.merged(graph)
    for s, p, o in remove:
        out.remove((URIRef(s), URIRef(p), o))
    if add:
        S.parse_into(out, f"{PFX}\n{add}")
    return out


def stage6_current() -> Graph:
    """Stage 6 with the FALSIFIED evidence removed: the evidence is current and VERIFIED again."""
    graph = stage_world(6)
    for triple in list(graph.triples((URIRef(EX + "evAF"), None, None))):
        graph.remove(triple)
    return graph


def carried(graph: Graph) -> "list[tuple[str, str, str]]":
    return [(r["source"], r["state"], r["staleBecause"]) for r in S.query_rows(graph, Q20)]


CARRIED_REEVALUATION = {
    "contract_revoked": ({"remove": [(EX + "kA", IC + "approvalStatus", URIRef(IC + "APPROVED"))],
                          "add": "ex:kA ic:approvalStatus ic:REJECTED ."}, "DEFICIT_CONTRACT"),
    "sbb_no_longer_qualified": ({"remove": [(EX + "sbbA", S.EA + "hasStanding", URIRef(S.EA + "QUALIFIED"))],
                                 "add": "ex:sbbA ea:hasStanding ea:CANDIDATE ."}, "DEFICIT_QUALIFICATION"),
    "abb_realizes_another_capability": ({"remove": [(EX + "abbA", S.EA + "realizesCapability", URIRef(EX + "capA"))],
                                         "add": 'ex:capZ a ea:Capability ; ic:capabilityKey "CAP-Z" ; ic:groundedIn ex:srcA . ex:abbA ea:realizesCapability ex:capZ .'},
                                        "DEFICIT_ABB"),
    "requirement_needs_do": ({"add": "ex:reqA ic:needsDoAuthority true ."}, "DEFICIT_AUTHORITY"),
}


def test_the_carried_baseline_is_live_while_the_chain_still_holds() -> None:
    graph = stage6_current()
    assert classes(graph) == {}
    assert carried(graph) == [("carried", "LIVE", "")]


@pytest.mark.parametrize("name", sorted(CARRIED_REEVALUATION))
def test_a_carried_coverage_is_re_marked_stale_when_the_chain_it_rests_on_breaks(name: str) -> None:
    edit, expected = CARRIED_REEVALUATION[name]
    graph = mutated(stage6_current(), **edit)
    # the residual reports the deficit, and the candidate snapshot agrees with it instead of asserting LIVE
    assert classes(graph) == {"REQ-A--CAP-A": expected}
    assert carried(graph) == [("carried", "STALE", expected)]
    text = next_snapshot(graph)
    assert f'ic:staleBecause "{expected}"' in text and "ic:coverageState ic:LIVE" not in text


def test_a_carried_coverage_stays_live_when_its_requirement_is_only_declared_out_of_scope() -> None:
    graph = mutated(stage6_current(), remove=[(EX + "reqA", IC + "disposition", URIRef(IC + "IN_SCOPE"))],
                    add="ex:reqA ic:disposition ic:OUT_OF_SCOPE ; ic:scopeJustification \"Moved out of scope on purpose.\" .")
    assert classes(graph) == {}
    assert carried(graph) == [("carried", "LIVE", "")]


def test_a_retired_coverage_is_not_carried_forward() -> None:
    graph = mutated(stage6_current(), add=f"""
<{EX}retire/cov> a ic:Retirement ; ic:retires ex:covAs1 ; ic:receiptDigest "{digest('retire-cov')}" ;
    ic:retirementReason "The capability was withdrawn from the synthetic scope." .
""")
    assert S.query_rows(graph, Q20) == []
    # without the retirement the same coverage is carried
    assert len(S.query_rows(stage6_current(), Q20)) == 1


def test_a_retirement_without_a_receipt_or_reason_does_not_remove_a_carried_coverage() -> None:
    graph = mutated(stage6_current(), add=f"""
<{EX}retire/cov> a ic:Retirement ; ic:retires ex:covAs1 ; ic:retirementReason "No receipt." .
""")
    assert len(S.query_rows(graph, Q20)) == 1


NEEDS_DO_FORMS = {
    "true_boolean": ("true", False),
    "string_true": ('"true"', True),
    "string_TRUE": ('"TRUE"', True),
    "string_one": ('"1"', True),
    "integer_one": ("1", True),
    "string_false": ('"false"', True),
    "iri": ("ex:yes", True),
    "false_boolean": ("false", False),
}


@pytest.mark.parametrize("name", sorted(NEEDS_DO_FORMS))
def test_a_do_need_that_is_not_a_literal_boolean_false_never_reads_as_covered(name: str) -> None:
    literal, _ = NEEDS_DO_FORMS[name]
    graph = mutated(stage_world(5), add=f"ex:reqA ic:needsDoAuthority {literal} .")
    got = classes(graph)
    if name == "false_boolean":
        assert got == {}, "only a typed boolean false lifts the DO fence"
    else:
        assert got == {"REQ-A--CAP-A": "DEFICIT_AUTHORITY"}
    standing = {r["standing"] for r in S.query_rows(graph, Q10)}
    assert standing <= {"BLOCKED"}


@pytest.mark.parametrize("name", sorted(NEEDS_DO_FORMS))
def test_a_non_boolean_do_need_is_refused_by_the_requirement_gate(name: str) -> None:
    literal, _ = NEEDS_DO_FORMS[name]
    graph = mutated(stage_world(5), add=f"ex:reqA ic:needsDoAuthority {literal} .")
    reasons = S.gate_reasons(graph, gate("020_requirement_identity"))
    if name in {"true_boolean", "false_boolean"}:
        assert "REFUSED:IC_NEEDS_DO_MALFORMED" not in reasons
    else:
        assert "REFUSED:IC_NEEDS_DO_MALFORMED" in reasons


def test_a_string_do_need_leaves_the_residual_ledger_visibly_unrecorded() -> None:
    graph = mutated(stage_world(5), add='ex:reqA ic:needsDoAuthority "true" .')
    assert S.gate_rows(graph, gate("055_frontier_recorded")) == []          # not covered, so no frontier to record
    assert {r for _, r in S.gate_rows(graph, gate("060_residual_ledger"))} == {"REFUSED:IC_RESIDUAL_UNRECORDED"}


@pytest.mark.parametrize("literal,refused", [("true", True), ('"true"', True), ('"1"', True), ("1", True), ('"false"', True),
                                              ("ex:granted", True), ("false", False)])
def test_a_do_grant_in_any_form_but_a_typed_false_is_forbidden(literal: str, refused: bool) -> None:
    graph = mutated(Graph(), add=f"ex:thing ic:grantsDoAuthority {literal} .")
    reasons = S.gate_reasons(graph, gate("080_authority_fence"))
    assert ("REFUSED:IC_AUTHORITY_DO_FORBIDDEN" in reasons) is refused


def test_a_closure_with_two_heads_is_refused_and_does_not_duplicate_frontier_rows() -> None:
    graph = mutated(stage_world(5), add="ex:snapB a ic:ClosureSnapshot ; ic:snapshotOf ex:closure ; ic:epoch 0 .")
    assert {r for _, r in S.gate_rows(graph, gate("030_snapshot_identity"))} == {
        "REFUSED:IC_SNAPSHOT_MULTIPLE_HEADS", "REFUSED:IC_SNAPSHOT_EPOCH_DUPLICATE"}
    # heads at different epochs are also two heads (the second is an orphan as well)
    other = mutated(stage_world(5), add="ex:snapB a ic:ClosureSnapshot ; ic:snapshotOf ex:closure ; ic:epoch 3 .")
    assert "REFUSED:IC_SNAPSHOT_MULTIPLE_HEADS" in S.gate_reasons(other, gate("030_snapshot_identity"))


def test_a_single_head_chain_is_not_refused_as_multi_headed() -> None:
    assert S.gate_rows(stage_world(6), gate("030_snapshot_identity")) == []


def test_a_second_work_order_for_one_residual_is_refused_even_with_a_different_id() -> None:
    pass_world = S.world(PACK / "witnesses" / "pass" / "100_sjira_workorder.ttl")
    graph = mutated(pass_world, add="""
ex:woresAsecond a ic:WorkOrder ; ic:workOrderId "SJ-REQ-A--CAP-A-second" ; ic:forResidual ex:resA ; ic:deltaCode "ARCHITECTURE_DELTA" ;
    ic:acceptance "Acceptance text." ; ic:falsifier "Falsified if the condition already holds." ;
    ic:standing "UNKNOWN" ; ic:authorityClaim "NONE" .
""")
    rows = S.gate_rows(graph, gate("100_sjira_workorder"))
    assert {r for _, r in rows} == {"REFUSED:IC_WORKORDER_DUPLICATE_FOR_RESIDUAL"}
    assert [local(s) for s, _ in rows] == ["woresA"]


def test_two_open_residuals_for_one_requirement_and_capability_are_refused() -> None:
    graph = S.world(PACK / "witnesses" / "pass" / "060_residual_ledger.ttl")
    assert S.gate_rows(graph, gate("060_residual_ledger")) == []
    doubled = mutated(graph, add="""
ex:resAagain a ic:Residual ; ic:residualKey "REQ-A--CAP-A-again" ; ic:residualOf ex:reqA ; ic:forCapabilityKey "CAP-A" ;
    ic:deficitClass ic:DEFICIT_ABB ; ic:feedbackTarget ic:UPSTREAM_ARCHITECTURE ; ic:status "OPEN" ; ic:standing "UNKNOWN" ; ic:authorityClaim "NONE" .
""")
    assert "REFUSED:IC_RESIDUAL_DUPLICATE_KEY" in S.gate_reasons(doubled, gate("060_residual_ledger"))


def test_a_residual_cannot_claim_a_standing_stronger_than_unknown_or_blocked() -> None:
    graph = S.world(PACK / "witnesses" / "pass" / "070_deficit_feedback.ttl")
    assert S.gate_rows(graph, gate("070_deficit_feedback")) == []
    promoted = mutated(graph, remove=[(EX + "resA", IC + "standing", Literal("UNKNOWN"))], add='ex:resA ic:standing "ALIVE" .')
    assert {r for _, r in S.gate_rows(promoted, gate("070_deficit_feedback"))} == {"REFUSED:IC_RESIDUAL_STANDING_PROMOTED"}


def alive_world() -> Graph:
    return S.world(PACK / "witnesses" / "pass" / "090_standing_evidence.ttl")


def test_alive_requires_a_live_coverage_with_no_current_falsification_and_its_own_evidence() -> None:
    graph = alive_world()
    assert S.gate_rows(graph, gate("090_standing_evidence")) == []
    stale = mutated(graph, remove=[(EX + "covAlive", IC + "coverageState", URIRef(IC + "LIVE"))],
                    add='ex:covAlive ic:coverageState ic:STALE ; ic:staleBecause "EVIDENCE_NOT_CURRENT" .')
    assert "REFUSED:IC_STANDING_ALIVE_NOT_LIVE" in S.gate_reasons(stale, gate("090_standing_evidence"))
    sbb = next(graph.objects(URIRef(EX + "covAlive"), URIRef(IC + "bySBB")))
    subject = next(graph.objects(sbb, URIRef(S.EA + "exactSubject")))
    falsified = mutated(graph, add=f"""
ex:evAfalse a ic:ExecutionEvidence ; ic:evidenceFor <{sbb}> ; ic:evidenceSubject "{subject}" ; ic:outcome ic:FALSIFIED ;
    ic:receiptDigest "{digest('false-receipt')}" ; ic:producedBy ex:agentBuilder ; ic:verifiedBy ex:agentVerifier ; ic:evidenceKind ic:OBSERVED .
""")
    assert "REFUSED:IC_STANDING_ALIVE_FALSIFIED" in S.gate_reasons(falsified, gate("090_standing_evidence"))
    foreign = mutated(graph, add=f"""
ex:sbbElsewhere a ea:SolutionBuildingBlock ; ea:exactSubject "{digest('elsewhere')}" .
ex:covAlive ic:bySBB ex:sbbElsewhere .
""", remove=[(EX + "covAlive", IC + "bySBB", sbb)])
    assert "REFUSED:IC_STANDING_EVIDENCE_FOREIGN" in S.gate_reasons(foreign, gate("090_standing_evidence"))


def test_an_sbb_with_two_exact_subjects_has_no_current_subject_and_is_refused() -> None:
    graph = mutated(stage_world(5), add=f'ex:sbbA ea:exactSubject "sha256:{"a" * 64}" .')
    assert classes(graph) == {}, "the classifier alone is existential over the pinned subjects"
    rows = S.gate_rows(graph, gate("050_coverage_chain"))
    assert [(local(s), r) for s, r in rows] == [("sbbA", "REFUSED:IC_SBB_SUBJECT_AMBIGUOUS")]


def test_a_receipt_digest_that_is_not_sha256_hex_is_no_retirement_receipt() -> None:
    base = admitted_stage5()
    cov = coverage_iri(base)
    graph = S.merged(base, SNAP2, f"""{PFX}
<{EX}retire/1> a ic:Retirement ; ic:retires <{cov}> ; ic:receiptDigest "x" ; ic:retirementReason "Malformed digest." .
""")
    assert "REFUSED:IC_RETIREMENT_DIGEST_MALFORMED" in S.gate_reasons(graph, gate("040_closure_monotonicity"))


def test_a_capability_grounded_in_a_source_outside_its_closure_is_an_ontology_deficit() -> None:
    graph = mutated(stage_world(5), remove=[(EX + "closure", IC + "usesSource", URIRef(EX + "srcA"))])
    assert classes(graph) == {"REQ-A--CAP-A": "DEFICIT_ONTOLOGY"}


def test_a_requirement_in_an_undeclared_closure_is_refused_by_gate_020() -> None:
    graph = mutated(stage_world(5), add=f"""
ex:reqLost a ic:Requirement ; ic:requirementId "REQ-LOST" ; ic:statement "A synthetic requirement aimed at nowhere." ;
    ic:inClosure <{EX}closure/missing> ; ic:disposition ic:IN_SCOPE ; ic:derivedFrom ex:srcA .
""")
    assert [(local(s), r) for s, r in S.gate_rows(graph, gate("020_requirement_identity"))] == [
        ("reqLost", "REFUSED:IC_REQUIREMENT_CLOSURE_UNDECLARED")]


HOSTILE_BASE_IRIS = [
    "https://example.invalid/bad base/",      # whitespace
    'https://example.invalid/x">/',            # a quote and an angle bracket would break out of <...> and "..."
    "https://example.invalid/x>y/",
    "http://example.invalid/plain/",           # not https
    "https://example.invalid/no-trailing-slash",
]


@pytest.mark.parametrize("base", HOSTILE_BASE_IRIS)
def test_a_hostile_base_iri_is_refused_before_it_can_be_spliced_into_generated_turtle(base: str) -> None:
    graph = stage_world(0)
    graph.remove((URIRef(EX + "closure"), URIRef(IC + "baseIri"), None))
    graph.add((URIRef(EX + "closure"), URIRef(IC + "baseIri"), Literal(base)))
    reasons = S.gate_reasons(graph, gate("030_snapshot_identity"))
    assert "REFUSED:IC_CLOSURE_BASEIRI_INVALID" in reasons
    # the templates do not escape: the gate is the only fence, so the splice is verbatim and must never be reached
    rendered = S.render(TEMPLATES / "residual-ledger.ttl.tera", S.query_rows(graph, Q10))
    assert base in rendered


def test_a_clean_base_iri_passes_the_closure_identity_gate() -> None:
    assert S.gate_rows(stage_world(0), gate("030_snapshot_identity")) == []


# ---------------------------------------------------------------------------
# 14. The one court this environment cannot run: real ggen manufacture and replay
# ---------------------------------------------------------------------------

def _ggen_binary() -> "str | None":
    import shutil

    return os.environ.get("GGEN_BIN") or shutil.which("ggen")


@pytest.mark.skipif(_ggen_binary() is None, reason="ggen not installed (set GGEN_BIN): manufacture and replay are BLOCKED:ggen_binary_unavailable")
@pytest.mark.parametrize("name", ["industry-closure-ledger-pack", "enterprise-operating-model-pack", "industry-closure-retail-lending-profile-pack"])
def test_real_ggen_manufactures_and_replays_the_pack(name: str, tmp_path: Path) -> None:
    import subprocess

    report = tmp_path / "qualification.json"
    done = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "qualify_packs.py"), "--ggen", _ggen_binary(), "--pack", name, "--report", str(report)],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )
    assert done.returncode == 0, done.stderr[-2000:]
    record = json.loads(report.read_text(encoding="utf-8"))["packs"][0]
    assert record["name"] == name and record["status"] == "ALIVE", record
