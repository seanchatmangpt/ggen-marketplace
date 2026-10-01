"""Court for industry-closure-retail-lending-profile-pack (ProfilePack, ABox only).

Real files, real rdflib, real SPARQL. Source digests are recomputed from the vendored files; versions,
IRIs and licences are read from them. The Jinja2 proxy is PARTIAL evidence about manufacture: real
ggen is unavailable here, so manufacture and execution stay BLOCKED:ggen_binary_unavailable.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path

import pytest
from rdflib import OWL, RDF, Graph, Namespace, URIRef

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ic_support as S  # noqa: E402

ROOT = S.ROOT
PACK = S.PACKS / "industry-closure-retail-lending-profile-pack"
KERNEL = S.PACK
ONTOLOGY = PACK / "ontology.ttl"
GOLDEN = PACK / "qualification" / "expected-residual.json"
GATE = PACK / "gates" / "010_profile_grounding.rq"
Q10 = KERNEL / "queries" / "10-residual.rq"
IC = Namespace(S.IC)
EA = Namespace(S.EA)
LND = Namespace("https://seanchatmangpt.github.io/packs/industry-closure-retail-lending-profile-pack#")
DCT = Namespace("http://purl.org/dc/terms/")
FIBO = "https://spec.edmcouncil.org/fibo/ontology/LOAN/"
KERNEL_STEMS = sorted(p.stem for p in (KERNEL / "gates").glob("*.rq"))


@pytest.fixture(scope="module")
def profile() -> Graph:
    g = Graph()
    g.parse(ONTOLOGY, format="turtle")
    return g


@pytest.fixture(scope="module")
def merged_world() -> Graph:
    return S.world(ONTOLOGY)


def sources(g: Graph, admission=None) -> list[URIRef]:
    out = []
    for s in g.subjects(RDF.type, IC.KnowledgeSource):
        if admission is None or (s, IC.admission, admission) in g:
            out.append(s)
    return sorted(out)


def vendored(g: Graph, src) -> Path:
    return ROOT / str(g.value(src, IC.sourceLocator))


def vendored_graph(path: Path) -> Graph:
    v = Graph()
    v.parse(path, format="xml")
    return v


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

def test_manifest_is_minimal_semantic_and_symlink_free() -> None:
    data = tomllib.loads((PACK / "pack.toml").read_text(encoding="utf-8"))
    assert set(data) == {"pack"}
    assert set(data["pack"]) == {"name", "version", "description"}
    assert data["pack"]["name"] == PACK.name
    assert re.fullmatch(r"\d+\.\d+\.\d+", data["pack"]["version"])
    assert data["pack"]["description"].strip()
    assert not (PACK / "ggen.toml").exists() and not (PACK / "templates").exists()
    assert not [p for p in PACK.rglob("*") if p.is_symlink()]
    assert all(p.suffix == ".rq" for p in (PACK / "gates").iterdir())


def test_profile_carries_no_building_blocks_coverage_evidence_or_receipts(profile: Graph) -> None:
    banned_types = [
        EA.ArchitectureBuildingBlock, EA.SolutionBuildingBlock, EA.ArchitectureContract, EA.ArchitectureReceipt,
        IC.Coverage, IC.Retirement, IC.ExecutionEvidence, IC.Residual, IC.WorkOrder,
    ]
    for t in banned_types:
        assert not list(profile.subjects(RDF.type, t)), t
    for p in (EA.realizesCapability, EA.satisfiesABB, EA.governedByContract, EA.hasStanding, EA.exactSubject,
              IC.evidenceFor, IC.bySBB, IC.byABB, IC.authorityClaim, IC.standing):
        assert not list(profile.subject_objects(p)), p


def test_one_closure_and_an_empty_epoch_zero_snapshot(profile: Graph) -> None:
    closures = list(profile.subjects(RDF.type, IC.IndustryClosure))
    assert closures == [LND.RetailLending]
    snaps = list(profile.subjects(RDF.type, IC.ClosureSnapshot))
    assert snaps == [LND.Snapshot0]
    assert int(profile.value(LND.Snapshot0, IC.epoch)) == 0
    assert (LND.Snapshot0, IC.supersedes, None) not in profile
    assert not list(profile.subjects(IC.inSnapshot, LND.Snapshot0))


# ---------------------------------------------------------------------------
# Vendored source pins, read from the actual files
# ---------------------------------------------------------------------------

def test_source_inventory_is_four_admitted_one_excluded_one_unknown(profile: Graph) -> None:
    assert len(sources(profile, IC.ADMITTED)) == 4
    assert len(sources(profile, IC.EXCLUDED)) == 1
    assert len(sources(profile, IC.UNKNOWN)) == 1
    assert len(sources(profile)) == 6


def test_every_source_digest_equals_sha256_of_its_vendored_file(profile: Graph) -> None:
    for src in sources(profile):
        path = vendored(profile, src)
        assert path.is_file() and not path.is_symlink(), path
        assert str(profile.value(src, IC.sourceDigest)) == "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(), src


def test_locators_lie_under_the_bound_path_prefix(profile: Graph) -> None:
    prefix = str(profile.value(LND.RetailLending, IC.boundPathPrefix))
    assert prefix == "ontologies/public/fibo/LOAN/"
    for src in sources(profile):
        assert str(profile.value(src, IC.sourceLocator)).startswith(prefix)
        assert set(profile.objects(LND.RetailLending, IC.usesSource)) == set(sources(profile))


def test_iri_version_and_licence_match_the_vendored_files(profile: Graph) -> None:
    for src in sources(profile):
        v = vendored_graph(vendored(profile, src))
        onto = next(v.subjects(RDF.type, OWL.Ontology))
        assert str(profile.value(src, IC.sourceIri)) == str(onto), src
        assert str(profile.value(src, IC.sourceVersion)) == str(v.value(onto, OWL.versionIRI)), src
        file_licence = str(v.value(onto, DCT.license))
        assert "opensource.org/licenses/MIT" in file_licence, src
        boundary = str(profile.value(src, IC.licenseBoundary))
        assert "MIT" in boundary and "opensource.org/licenses/MIT" in boundary, src
        if (src, IC.admission, IC.ADMITTED) in profile:
            # the copyright years named in the boundary text appear in the file's own notice
            for year_range in re.findall(r"\d{4}-\d{4}", boundary):
                assert year_range in file_licence, (src, year_range)


def test_every_provided_and_capability_concept_is_an_owl_class_in_its_admitted_source(profile: Graph) -> None:
    for src in sources(profile, IC.ADMITTED):
        v = vendored_graph(vendored(profile, src))
        concepts = set(profile.objects(src, IC.providesConcept))
        assert concepts, src
        for c in concepts:
            assert (c, RDF.type, OWL.Class) in v, (src, c)
            assert str(c).startswith(FIBO)
    for cap in profile.subjects(RDF.type, EA.Capability):
        src = profile.value(cap, IC.groundedIn)
        v = vendored_graph(vendored(profile, src))
        for c in profile.objects(cap, IC.concept):
            assert (c, RDF.type, OWL.Class) in v, (cap, c)
            assert (src, IC.providesConcept, c) in profile, (cap, c)
        assert (src, IC.admission, IC.ADMITTED) in profile


def test_excluded_has_a_reason_and_unknown_has_a_falsifier(profile: Graph) -> None:
    (excluded,) = sources(profile, IC.EXCLUDED)
    (unknown,) = sources(profile, IC.UNKNOWN)
    assert str(profile.value(excluded, IC.exclusionReason)).strip()
    assert str(profile.value(unknown, IC.falsifier)).strip()
    assert not list(profile.objects(excluded, IC.providesConcept))
    assert not list(profile.objects(unknown, IC.providesConcept))


# ---------------------------------------------------------------------------
# Requirements and golden residual
# ---------------------------------------------------------------------------

def test_requirements_are_atomic_identified_and_originate_in_admitted_sources(profile: Graph) -> None:
    reqs = sorted(profile.subjects(RDF.type, IC.Requirement))
    assert len(reqs) == 11
    ids = [str(profile.value(r, IC.requirementId)) for r in reqs]
    assert len(set(ids)) == len(ids)
    assert all(re.fullmatch(r"[A-Za-z0-9._-]+", i) for i in ids)
    for r in reqs:
        assert (r, IC.inClosure, LND.RetailLending) in profile
        assert len(str(profile.value(r, IC.statement)).split()) < 40  # one atomic paraphrase, not a pasted passage
        if (r, IC.disposition, IC.IN_SCOPE) in profile:
            assert (profile.value(r, IC.derivedFrom), IC.admission, IC.ADMITTED) in profile, r
    do_needing = [r for r in reqs if (r, IC.needsDoAuthority, None) in profile]
    assert do_needing == [LND.Req10]
    oos = list(profile.subjects(IC.disposition, IC.OUT_OF_SCOPE))
    assert oos == [LND.Req11] and str(profile.value(LND.Req11, IC.scopeJustification)).strip()


def test_no_do_vocabulary_and_no_authority_grant_in_the_profile(profile: Graph) -> None:
    text = ONTOLOGY.read_text(encoding="utf-8")
    assert "ic:DO" not in text and "grantsDoAuthority" not in text and "APPROVED" not in text
    assert not list(profile.triples((None, IC.authorityCeiling, None)))
    for _, o in profile.subject_objects(IC.needsDoAuthority):
        assert o.toPython() is True


def test_golden_residual_matches_the_kernel_query_over_kernel_plus_profile(merged_world: Graph) -> None:
    rows = S.query_rows(merged_world, Q10)
    assert S.rows_json(rows) == GOLDEN.read_text(encoding="utf-8")
    by = {r["rid"]: r for r in rows}
    in_scope_mapped = [r for i, r in by.items() if i != "LND-REQ-10"]
    assert len(in_scope_mapped) == 9
    assert all(r["classCode"] == "DEFICIT_ABB" and r["standing"] == "UNKNOWN" for r in in_scope_mapped)
    assert by["LND-REQ-10"]["classCode"] == "DEFICIT_AUTHORITY"
    assert by["LND-REQ-10"]["standing"] == "BLOCKED"
    assert "LND-REQ-11" not in by  # OUT_OF_SCOPE: absent from the residual, justified in the ontology


def test_consumer_wiring_rehearsal_feeds_the_profile_through_the_kernel_import_path(tmp_path: Path) -> None:
    """The documented consumer wiring: a scratch copy of the kernel with the profile's ontology.ttl placed at the
    kernel's input path. rdflib reads the kernel ggen.toml source and imports from that scratch consumer and runs every
    rule's query, so the wiring (paths, imports, query files) is exercised. It is a rehearsal of the manufacture input
    only: the real ggen run on this profile stays BLOCKED:ggen_binary_unavailable."""
    import shutil

    scratch = tmp_path / "consumer"
    shutil.copytree(KERNEL, scratch)
    assert (scratch / "ontology" / "industry-input.ttl").read_text(encoding="utf-8").count("a ic:") == 0, "ships empty"
    shutil.copyfile(ONTOLOGY, scratch / "ontology" / "industry-input.ttl")
    config = tomllib.loads((scratch / "ggen.toml").read_text(encoding="utf-8"))
    graph = Graph()
    for relative in [config["ontology"]["source"], *config["ontology"]["imports"]]:
        graph.parse(scratch / relative, format="turtle")
    produced = {}
    for rule in config["generation"]["rules"]:
        assert (scratch / rule["template"]["file"]).is_file()
        produced[rule["name"]] = S.query_rows(graph, scratch / rule["query"]["file"])
    assert S.rows_json(produced["residual-ledger"]) == GOLDEN.read_text(encoding="utf-8")
    assert produced["sjira-workorders"] == produced["feedback-packet"] == produced["residual-ledger"]
    assert produced["closure-next"] == [], "no building blocks, so nothing is covered and nothing is carried"


def test_residual_standings_are_never_alive() -> None:
    for row in json.loads(GOLDEN.read_text(encoding="utf-8")):
        assert row["standing"] in {"UNKNOWN", "BLOCKED"}


# ---------------------------------------------------------------------------
# Kernel gates over kernel plus profile
# ---------------------------------------------------------------------------

def completed_world(merged_world: Graph) -> Graph:
    rows = S.query_rows(merged_world, Q10)
    return S.merged(
        merged_world,
        S.render(KERNEL / "templates" / "residual-ledger.ttl.tera", rows),
        S.render(KERNEL / "templates" / "sjira-workorders.ttl.tera", rows),
    )


@pytest.mark.parametrize("stem", KERNEL_STEMS)
def test_kernel_gate_returns_zero_rows_over_kernel_plus_profile(merged_world: Graph, stem: str) -> None:
    rows = S.gate_rows(completed_world(merged_world), KERNEL / "gates" / f"{stem}.rq")
    assert rows == [], (stem, rows)


def test_without_the_recorded_residual_gate_060_refuses_every_row(merged_world: Graph) -> None:
    rows = S.gate_rows(merged_world, KERNEL / "gates" / "060_residual_ledger.rq")
    assert {reason for _, reason in rows} == {"REFUSED:IC_RESIDUAL_UNRECORDED"}
    assert len(rows) == 10


def test_jinja_proxy_second_render_of_the_ledger_is_byte_identical(merged_world: Graph) -> None:
    rows = S.query_rows(merged_world, Q10)
    a = S.render(KERNEL / "templates" / "residual-ledger.ttl.tera", rows)
    b = S.render(KERNEL / "templates" / "residual-ledger.ttl.tera", S.query_rows(merged_world, Q10))
    assert a == b
    assert 'ic:standing "ALIVE"' not in a and 'ic:authorityClaim "NONE"' in a


# ---------------------------------------------------------------------------
# Profile gate court: every declared code hit by an executing fail witness
# ---------------------------------------------------------------------------

def witness_graph(kind: str) -> Graph:
    return S.world(PACK / "witnesses" / kind / "010_profile_grounding.ttl")


def test_witness_stems_correspond_exactly() -> None:
    stems = {p.stem for p in (PACK / "gates").glob("*.rq")}
    assert stems == {p.stem for p in (PACK / "witnesses" / "pass").glob("*.ttl")}
    assert stems == {p.stem for p in (PACK / "witnesses" / "fail").glob("*.ttl")}
    assert stems == {"010_profile_grounding"}


def test_pass_witness_is_clean_and_not_vacuous() -> None:
    g = witness_graph("pass")
    assert S.gate_rows(g, GATE) == []
    for t in (IC.IndustryClosure, IC.KnowledgeSource, IC.Requirement, EA.Capability):
        assert list(g.subjects(RDF.type, t)), t


def test_fail_witness_reasons_equal_the_declared_codes() -> None:
    declared = S.declared_codes(GATE.read_text(encoding="utf-8"))
    assert declared == {
        "REFUSED:LND_CAPABILITY_CONCEPT_NOT_PROVIDED",
        "REFUSED:LND_CAPABILITY_CONCEPT_MISSING",
        "REFUSED:LND_REQUIREMENT_SOURCE_NOT_IN_CLOSURE",
        "REFUSED:LND_SOURCE_NOT_FIBO_LOAN",
    }
    assert S.gate_reasons(witness_graph("fail"), GATE) == declared


def test_each_code_is_hit_by_its_intended_violator() -> None:
    ex = "https://example.org/industry-closure-retail-lending-profile-pack/fail/"
    rows = set(S.gate_rows(witness_graph("fail"), GATE))
    assert rows == {
        (ex + "capBadConcept", "REFUSED:LND_CAPABILITY_CONCEPT_NOT_PROVIDED"),
        (ex + "capNoConcept", "REFUSED:LND_CAPABILITY_CONCEPT_MISSING"),
        (ex + "reqBadSource", "REFUSED:LND_REQUIREMENT_SOURCE_NOT_IN_CLOSURE"),
        (ex + "srcForeign", "REFUSED:LND_SOURCE_NOT_FIBO_LOAN"),
    }


def test_profile_ontology_passes_its_own_gate(merged_world: Graph) -> None:
    assert S.gate_rows(merged_world, GATE) == []


def test_every_union_branch_binds_subject_first() -> None:
    branches = S.union_branches(GATE.read_text(encoding="utf-8"))
    assert len(branches) == 4
    assert all(S.first_pattern_binds_subject(b) for b in branches)


def test_gate_is_deterministic_and_read_only(merged_world: Graph) -> None:
    before = len(merged_world)
    assert S.gate_rows(merged_world, GATE) == S.gate_rows(merged_world, GATE)
    assert len(merged_world) == before
    assert not re.search(r"\b(INSERT|DELETE|LOAD|CLEAR|DROP|CREATE)\b", GATE.read_text(encoding="utf-8"))


def test_a_tampered_digest_or_concept_is_caught_by_the_court(profile: Graph) -> None:
    tampered = Graph()
    for t in profile:
        tampered.add(t)
    src = LND.SrcLoans
    tampered.set((src, IC.sourceDigest, __import__("rdflib").Literal("sha256:" + "0" * 64)))
    assert str(tampered.value(src, IC.sourceDigest)) != "sha256:" + hashlib.sha256(vendored(profile, src).read_bytes()).hexdigest()
    g = S.merged(S.world(ONTOLOGY))
    g.add((LND.CapLoanIntake, IC.concept, URIRef(FIBO + "LoansGeneral/LoanApplications/NotAClass")))
    assert ("%sCapLoanIntake" % str(LND), "REFUSED:LND_CAPABILITY_CONCEPT_NOT_PROVIDED") in S.gate_rows(g, GATE)
