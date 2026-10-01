#!/usr/bin/env python3
"""Court B: enterprise-operating-model-pack under real rdflib, real files, no mocks.

Enforcement layers (existence of a gate is never claimed as enforcement):
  1. gate-court.toml + scripts/check_gate_witness_courts.py prove stem correspondence only.
  2. THIS module executes every gate under real rdflib against every witness. A pass
     witness returns zero rows and is not vacuous. A fail witness returns exactly the set
     of REFUSED:* codes parsed from the gate source, and every code is hit by a violator
     whose IRI names that code, so a code that cannot fire (or fires only by accident)
     fails here.
  3. scripts/qualify_packs.py with a real ggen proves manufacture and replay. No ggen
     binary exists in this environment: that layer is BLOCKED:ggen_binary_unavailable and
     nothing here claims it. Template rendering below uses a Jinja2 proxy restricted to
     the for/if/loop.last subset, which is PARTIAL evidence about the Tera templates.
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

import rdflib
from jinja2 import Environment, StrictUndefined
from rdflib import Literal, URIRef
from rdflib.namespace import RDF

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import marketplace  # noqa: E402
from check_gate_witness_courts import qualify as qualify_court  # noqa: E402

logging.getLogger("rdflib").setLevel(logging.ERROR)

PACK_NAME = "enterprise-operating-model-pack"
PACK = ROOT / "packs" / PACK_NAME
TOGAF_PACK = ROOT / "packs" / "togaf-adm-pack"
EA_PACK = ROOT / "packs" / "enterprise-architecture-pack"
IC_PACK = ROOT / "packs" / "industry-closure-pack"

EOM = "https://seanchatmangpt.github.io/packs/enterprise-operating-model-pack#"
IC = "https://seanchatmangpt.github.io/packs/industry-closure-pack#"
EA = "https://chatman.ai/ontology/enterprise-architecture#"
TOGAF = "http://www.semanticweb.org/ontologies/2020/4/OntologyTOGAFContentMetamodel.owl#"
SKOS_NOTATION = URIRef("http://www.w3.org/2004/02/skos/core#notation")

ONTOLOGY = PACK / "ontology.ttl"
INPUT_CONTRACT = PACK / "ontology" / "enterprise-input.ttl"
QUAL_INPUT = PACK / "qualification" / "project" / "ontology" / "enterprise-input.ttl"
GATES = sorted((PACK / "gates").glob("*.rq"))
CODE_RE = re.compile(r'"(REFUSED:[A-Z0-9_]+)"')

PFX = (
    f"PREFIX eom: <{EOM}> PREFIX ea: <{EA}> PREFIX togaf: <{TOGAF}> PREFIX org: <http://www.w3.org/ns/org#> "
    "PREFIX skos: <http://www.w3.org/2004/02/skos/core#> PREFIX dcterms: <http://purl.org/dc/terms/> "
)

# Vacuity guards: ASK queries over the pass witness alone. Each states the positive pattern a gate branch keys on, so
# a pass witness that merely contains the guarded type (and so exercises no branch condition) fails its guard.
GUARDS = {
    "010_operating_model_decision": [
        "ASK { ?d a eom:OperatingModelDecision ; eom:forStrategy ?s ; eom:chosenModel ?m ; eom:integrationLevel ?i ;"
        " eom:standardizationLevel ?l ; dcterms:source ?z . ?s a ea:Strategy ; eom:ofEnterprise ?e }",
    ],
    "020_foundation_completeness": [
        "ASK { ?d eom:hasFoundation ?f . ?f a eom:FoundationForExecution ; eom:hasCoreProcess ?p ; eom:hasSharedData ?s ;"
        " eom:hasLinkingAutomation ?l . ?p eom:elementKey ?k ; eom:supportsCapability ?c . ?s eom:ownedBy ?r . ?r a org:Role ."
        " ?l eom:realizedByABB ?a . ?a a ea:ArchitectureBuildingBlock }",
    ],
    "030_axis_obligations": [
        "ASK { ?d eom:standardizationLevel eom:HIGH ; eom:hasFoundation ?f . ?f eom:hasCoreProcess ?p . ?p eom:standardVariant true }",
        "ASK { ?d eom:integrationLevel eom:HIGH ; eom:hasFoundation ?f . ?f eom:hasSharedData ?s . ?s eom:enterpriseScope true }",
        "ASK { ?d eom:integrationLevel eom:LOW ; eom:hasFoundation ?f . ?f eom:hasSharedData ?s . ?s eom:enterpriseScope false }",
        "ASK { ?d eom:standardizationLevel eom:LOW ; eom:hasFoundation ?f . ?f eom:hasCoreProcess ?p . ?p eom:standardVariant false }",
    ],
    "040_maturity_progression": [
        "ASK { ?d eom:atStage eom:StageBusinessModularity ; eom:hasFoundation ?f . ?f eom:hasCoreProcess ?p ;"
        " eom:hasLinkingAutomation ?l ; eom:hasModularComponent ?m . ?p eom:standardVariant true ."
        " ?e a eom:StageEvidence ; eom:forDecision ?d ; eom:forStage eom:StageOptimizedCore ; eom:receiptDigest ?r }",
        "ASK { ?d eom:atStage eom:StageBusinessSilos . ?e a eom:StageEvidence ; eom:forDecision ?d ;"
        " eom:forStage eom:StageBusinessSilos ; eom:receiptDigest ?r }",
    ],
    "050_engagement_model": [
        "ASK { ?e a eom:EngagementModel ; eom:enterpriseGovernance ?g ; eom:projectGovernance ?p ; eom:linkingMechanism ?l . ?g skos:notation ?n }",
        "ASK { ?w a togaf:WorkPackage ; eom:ofEnterprise ?x ; eom:reviewedBy ?r }",
        "ASK { ?w a togaf:WorkPackage ; eom:dispensation ?d . ?d a eom:Dispensation ; eom:owner ?o ; eom:expires ?x }",
    ],
    "060_adm_phase_gate": [
        'ASK { ?r a eom:PhaseRecord ; eom:status "ACHIEVED" ; eom:phase ?p ; eom:ofEngagement ?e ; eom:produced ?a ; eom:reqMgmtReview ?v }',
        'ASK { ?r a eom:PhaseRecord ; eom:phase eom:AdmReqMgmt ; eom:status "ACHIEVED" }',
        'ASK { ?r a eom:PhaseRecord ; eom:phase eom:AdmPhaseA ; eom:status "ACHIEVED" . ?q a eom:PhaseRecord ; eom:phase eom:AdmPrelim ; eom:status "ACHIEVED" }',
    ],
    "070_value_stream_anchoring": [
        "ASK { ?s a eom:ValueStreamStage ; eom:enablesCapability ?c . ?c a eom:EnterpriseCapability }",
        "ASK { ?c a eom:EnterpriseCapability ; eom:capabilityRole eom:ENABLING }",
        "ASK { ?v a eom:ValueStream ; eom:hasStage ?s }",
    ],
    "080_authority_fence": [
        'ASK { ?x eom:authorityCeiling "CONSTRUCT" ; eom:authorityClaim "NONE" }',
        'ASK { ?x eom:authorityCeiling "SELECT" }',
    ],
}

# The complete (subject, code) row set of every fail witness, pinned by hand-reviewed pairs rather than derived from
# the violator's own name. A violator that stops firing, a code that fires on the wrong subject, or a collateral row
# all change this set. Subjects are local names under the witness namespace; codes omit the REFUSED: prefix.
EXPECTED_ROWS = {
    "010_operating_model_decision": {
        ("VIOL_EOM_DECISION_KEY_UNSAFE", "EOM_DECISION_KEY_UNSAFE"),
        ("VIOL_EOM_DECISION_KEY_UNSAFE_missing", "EOM_DECISION_KEY_UNSAFE"),
        ("VIOL_EOM_DECISION_NO_STRATEGY", "EOM_DECISION_NO_STRATEGY"),
        ("VIOL_EOM_DECISION_TARGET_INVALID", "EOM_DECISION_TARGET_INVALID"),
        ("VIOL_EOM_DECISION_TARGET_INVALID_no_closure", "EOM_DECISION_TARGET_INVALID"),
        ("VIOL_EOM_OM_AXES_INCONSISTENT", "EOM_OM_AXES_INCONSISTENT"),
        ("VIOL_EOM_OM_AXES_MISSING", "EOM_OM_AXES_MISSING"),
        ("VIOL_EOM_OM_CHOICE_AMBIGUOUS", "EOM_OM_AXES_INCONSISTENT"),
        ("VIOL_EOM_OM_CHOICE_AMBIGUOUS", "EOM_OM_CHOICE_AMBIGUOUS"),
        ("VIOL_EOM_OM_CHOICE_MISSING", "EOM_OM_CHOICE_MISSING"),
        ("VIOL_EOM_PROVENANCE_MISSING", "EOM_PROVENANCE_MISSING"),
        ("VIOL_EOM_STRATEGY_NO_ENTERPRISE", "EOM_STRATEGY_NO_ENTERPRISE"),
        ("VIOL_EOM_STRATEGY_NO_OPMODEL", "EOM_STRATEGY_NO_OPMODEL"),
    },
    "020_foundation_completeness": {
        ("VIOL_EOM_DATA_UNOWNED", "EOM_DATA_UNOWNED"),
        ("VIOL_EOM_DECISION_NO_FOUNDATION", "EOM_DECISION_NO_FOUNDATION"),
        ("VIOL_EOM_ELEMENT_CAPABILITY_UNKEYED", "EOM_ELEMENT_CAPABILITY_UNKEYED"),
        ("VIOL_EOM_ELEMENT_KEY_UNSAFE", "EOM_ELEMENT_KEY_UNSAFE"),
        ("VIOL_EOM_ELEMENT_KEY_UNSAFE_missing", "EOM_ELEMENT_KEY_UNSAFE"),
        ("VIOL_EOM_ELEMENT_NO_CAPABILITY", "EOM_ELEMENT_NO_CAPABILITY"),
        ("VIOL_EOM_FOUNDATION_NO_DECISION-foundation", "EOM_FOUNDATION_NO_DECISION"),
        ("VIOL_EOM_FOUNDATION_NO_LINKING", "EOM_FOUNDATION_NO_LINKING"),
        ("VIOL_EOM_FOUNDATION_NO_PROCESS", "EOM_FOUNDATION_NO_PROCESS"),
        ("VIOL_EOM_FOUNDATION_NO_SHARED_DATA", "EOM_FOUNDATION_NO_SHARED_DATA"),
        ("VIOL_EOM_LINKING_NO_ABB", "EOM_LINKING_NO_ABB"),
    },
    "030_axis_obligations": {
        ("VIOL_EOM_INTEGRATION_DATA_NOT_SHARED", "EOM_INTEGRATION_DATA_NOT_SHARED"),
        ("VIOL_EOM_OVERINTEGRATION", "EOM_OVERINTEGRATION"),
        ("VIOL_EOM_OVERSTANDARDIZATION", "EOM_OVERSTANDARDIZATION"),
        ("VIOL_EOM_STANDARDIZATION_PROCESS_NOT_STANDARD", "EOM_STANDARDIZATION_PROCESS_NOT_STANDARD"),
    },
    "040_maturity_progression": {
        ("VIOL_EOM_MATURITY_SKIP", "EOM_MATURITY_SKIP"),
        ("VIOL_EOM_MATURITY_SKIP_malformed", "EOM_MATURITY_SKIP"),
        ("VIOL_EOM_MATURITY_STAGE2_NO_SHARED_INFRA", "EOM_MATURITY_STAGE2_NO_SHARED_INFRA"),
        ("VIOL_EOM_MATURITY_STAGE3_NOT_STANDARD_CORE", "EOM_MATURITY_STAGE3_NOT_STANDARD_CORE"),
        ("VIOL_EOM_MATURITY_STAGE4_NO_MODULARITY", "EOM_MATURITY_STAGE4_NO_MODULARITY"),
        ("VIOL_EOM_MATURITY_UNEVIDENCED", "EOM_MATURITY_UNEVIDENCED"),
        ("VIOL_EOM_MATURITY_UNEVIDENCED_malformed", "EOM_MATURITY_UNEVIDENCED"),
    },
    "050_engagement_model": {
        ("VIOL_EOM_DECISION_NO_ENGAGEMENT", "EOM_DECISION_NO_ENGAGEMENT"),
        ("VIOL_EOM_DISPENSATION_UNBOUNDED", "EOM_DISPENSATION_UNBOUNDED"),
        ("VIOL_EOM_DISPENSATION_UNBOUNDED_no_owner", "EOM_DISPENSATION_UNBOUNDED"),
        ("VIOL_EOM_ENGAGEMENT_MECHANISM_UNKNOWN", "EOM_ENGAGEMENT_MECHANISM_UNKNOWN"),
        ("VIOL_EOM_ENGAGEMENT_MECHANISM_UNKNOWN_no_notation", "EOM_ENGAGEMENT_MECHANISM_UNKNOWN"),
        ("VIOL_EOM_ENGAGEMENT_NO_ENTERPRISE_LEVEL", "EOM_ENGAGEMENT_NO_ENTERPRISE_LEVEL"),
        ("VIOL_EOM_ENGAGEMENT_NO_LINKING", "EOM_ENGAGEMENT_NO_LINKING"),
        ("VIOL_EOM_ENGAGEMENT_NO_PROJECT_LEVEL", "EOM_ENGAGEMENT_NO_PROJECT_LEVEL"),
        ("VIOL_EOM_WORKPACKAGE_UNREVIEWED", "EOM_WORKPACKAGE_UNREVIEWED"),
        ("VIOL_EOM_WORKPACKAGE_UNREVIEWED_untyped_dispensation", "EOM_WORKPACKAGE_UNREVIEWED"),
    },
    "060_adm_phase_gate": {
        ("VIOL_EOM_ADM_ARTIFACT_MISSING", "EOM_ADM_ARTIFACT_MISSING"),
        ("VIOL_EOM_ADM_CYCLE", "EOM_ADM_CYCLE"),
        ("VIOL_EOM_ADM_PREDECESSOR_NOT_ACHIEVED", "EOM_ADM_PREDECESSOR_NOT_ACHIEVED"),
        ("VIOL_EOM_ADM_RECORD_MALFORMED", "EOM_ADM_RECORD_MALFORMED"),
        ("VIOL_EOM_ADM_RECORD_MALFORMED_no_engagement", "EOM_ADM_RECORD_MALFORMED"),
        ("VIOL_EOM_ADM_REQMGMT_MISSING", "EOM_ADM_REQMGMT_MISSING"),
        ("VIOL_EOM_ADM_REQMGMT_MISSING_no_notation", "EOM_ADM_REQMGMT_MISSING"),
        ("VIOL_EOM_ADM_STATUS_INVALID", "EOM_ADM_STATUS_INVALID"),
        ("VIOL_cycle-b", "EOM_ADM_CYCLE"),
    },
    "070_value_stream_anchoring": {
        ("VIOL_EOM_CAPABILITY_FLOATING", "EOM_CAPABILITY_FLOATING"),
        ("VIOL_EOM_CAPABILITY_FLOATING_no_enterprise", "EOM_CAPABILITY_FLOATING"),
        ("VIOL_EOM_VALUE_STREAM_EMPTY", "EOM_VALUE_STREAM_EMPTY"),
    },
    "080_authority_fence": {
        ("VIOL_EOM_AUTHORITY_CEILING_INVALID", "EOM_AUTHORITY_CEILING_INVALID"),
        ("VIOL_EOM_AUTHORITY_DO_FORBIDDEN", "EOM_AUTHORITY_CEILING_INVALID"),
        ("VIOL_EOM_AUTHORITY_DO_FORBIDDEN", "EOM_AUTHORITY_DO_FORBIDDEN"),
        ("VIOL_EOM_AUTHORITY_DO_FORBIDDEN_claim", "EOM_AUTHORITY_DO_FORBIDDEN"),
        ("VIOL_EOM_AUTHORITY_DO_FORBIDDEN_class", "EOM_AUTHORITY_DO_FORBIDDEN"),
        ("VIOL_EOM_AUTHORITY_DO_FORBIDDEN_grant", "EOM_AUTHORITY_DO_FORBIDDEN"),
        ("VIOL_EOM_AUTHORITY_DO_FORBIDDEN_grant_string", "EOM_AUTHORITY_DO_FORBIDDEN"),
        ("VIOL_EOM_AUTHORITY_DO_FORBIDDEN_iri", "EOM_AUTHORITY_DO_FORBIDDEN"),
    },
}


def load(*paths: Path) -> rdflib.Graph:
    graph = rdflib.Graph()
    for path in paths:
        graph.parse(path, format="turtle")
    return graph


def rows(graph: rdflib.Graph, query: str) -> list[tuple[str, str]]:
    return [(str(row[0]), str(row[1])) for row in graph.query(query)]


def reasons(graph: rdflib.Graph, gate: Path) -> set[str]:
    return {reason for _, reason in rows(graph, gate.read_text(encoding="utf-8"))}


def gate_path(stem: str) -> Path:
    return PACK / "gates" / f"{stem}.rq"


def declared_codes(gate: Path) -> set[str]:
    return set(CODE_RE.findall(gate.read_text(encoding="utf-8")))


def local(iri: str) -> str:
    return iri.rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def pack_text_files() -> list[Path]:
    return sorted(
        path
        for path in PACK.rglob("*")
        if path.is_file() and path.suffix in {".rq", ".ttl", ".tera", ".toml"}
    )


def notations(graph: rdflib.Graph) -> set[str]:
    return {str(o) for _, _, o in graph.triples((None, SKOS_NOTATION, None))}


def render(template: str, results: list[dict[str, str]]) -> str:
    env = Environment(undefined=StrictUndefined, keep_trailing_newline=True, autoescape=False)
    return env.from_string((PACK / "templates" / template).read_text(encoding="utf-8")).render(results=results)


def query_rows(graph: rdflib.Graph, query_file: str) -> list[dict[str, str]]:
    result = graph.query((PACK / "queries" / query_file).read_text(encoding="utf-8"))
    return [{str(v): str(row[v]) for v in result.vars if row[v] is not None} for row in result]


def gate_union_branches(source: str) -> list[str]:
    """Depth-2 groups of the WHERE body: the UNION branches of a gate."""
    lines = [line for line in source.splitlines() if not line.lstrip().startswith("#")]
    text = "\n".join(lines)
    text = re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)
    text = re.sub(r"<[^\s<>\"{}|^`\\]*>", "<>", text)
    start = text.index("{", text.index("WHERE"))
    depth = 0
    branches: list[str] = []
    current: list[str] = []
    for char in text[start:]:
        if char == "{":
            depth += 1
            if depth == 2:
                current = []
                continue
        elif char == "}":
            if depth == 2:
                branches.append("".join(current))
            depth -= 1
            continue
        if depth >= 2:
            current.append(char)
    return branches


def first_pattern(branch: str) -> str:
    match = re.search(r"\.(?:\s|$)", branch)
    return branch[: match.start()] if match else branch


class StructureTests(unittest.TestCase):
    def test_pack_toml_only_admitted_keys_and_identity(self) -> None:
        document = tomllib.loads((PACK / "pack.toml").read_text(encoding="utf-8"))
        self.assertEqual(set(document), {"pack"})
        self.assertEqual(set(document["pack"]), {"name", "version", "description"})
        self.assertEqual(document["pack"]["name"], PACK_NAME)
        self.assertRegex(document["pack"]["version"], r"^\d+\.\d+\.\d+$")
        self.assertTrue(document["pack"]["description"].strip())

    def test_marketplace_admits_the_pack_as_project_profile_outside_active_scope(self) -> None:
        packs = {pack.name: pack for pack in marketplace.require_admitted()}
        self.assertIn(PACK_NAME, packs)
        self.assertEqual(packs[PACK_NAME].profile, "project")
        self.assertEqual(len(packs[PACK_NAME].native_gates), 8)
        self.assertEqual(len(packs[PACK_NAME].templates), 2)
        active = {pack.name for pack in marketplace.scoped_packs("active")}
        self.assertNotIn(PACK_NAME, active)

    def test_no_symlinks_gates_only_rq_templates_only_tera(self) -> None:
        for path in PACK.rglob("*"):
            self.assertFalse(path.is_symlink(), path)
        self.assertEqual({p.suffix for p in (PACK / "gates").iterdir()}, {".rq"})
        self.assertEqual({p.suffixes[-1] for p in (PACK / "templates").iterdir()}, {".tera"})

    def test_gate_court_stems_correspond_exactly(self) -> None:
        record = qualify_court(PACK)
        self.assertEqual(record["case_count"], 8)
        self.assertEqual(record["standing"], "ALIVE")
        stems = {g.stem for g in GATES}
        self.assertEqual({p.stem for p in (PACK / "witnesses" / "pass").iterdir()}, stems)
        self.assertEqual({p.stem for p in (PACK / "witnesses" / "fail").iterdir()}, stems)
        self.assertEqual(stems, set(GUARDS))

    def test_all_turtle_parses(self) -> None:
        for path in sorted(PACK.rglob("*.ttl")):
            with self.subTest(path=path.relative_to(PACK).as_posix()):
                self.assertGreater(len(load(path)), 0 if path != INPUT_CONTRACT else -1)

    def test_input_contract_is_empty_and_overlay_shares_its_relative_path(self) -> None:
        self.assertEqual(len(load(INPUT_CONTRACT)), 0)
        self.assertGreater(len(load(QUAL_INPUT)), 0)
        self.assertEqual(
            QUAL_INPUT.relative_to(PACK / "qualification" / "project"),
            INPUT_CONTRACT.relative_to(PACK),
        )

    def test_ggen_toml_contract(self) -> None:
        config = tomllib.loads((PACK / "ggen.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["ontology"]["source"], "ontology.ttl")
        self.assertEqual(config["ontology"]["imports"], ["ontology/enterprise-input.ttl"])
        self.assertTrue((PACK / config["ontology"]["imports"][0]).is_file())
        self.assertEqual(config["generation"]["output_dir"], ".")
        rules = config["generation"]["rules"]
        self.assertEqual([r["name"] for r in rules], ["eom-requirements", "eom-abb-skeletons"])
        for rule in rules:
            self.assertTrue((PACK / rule["query"]["file"]).is_file())
            self.assertTrue((PACK / rule["template"]["file"]).is_file())
            self.assertTrue(rule["output_file"].startswith("generated/enterprise-operating-model/"), rule)
            self.assertIs(rule["skip_empty"], False)
            self.assertEqual(rule["mode"], "Overwrite")

    def test_catalog_lists_the_pack_with_a_permitted_class(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / "marketplace.py"), "catalog", "--scope", "all"],
            capture_output=True, text=True, check=True, cwd=ROOT,
        )
        entries = {e["name"]: e for e in json.loads(completed.stdout)["packs"]}
        entry = entries[PACK_NAME]
        self.assertEqual(entry["profile"], "project")
        # None until the integration lane assigns PACK_CLASSES; CapabilityPack afterwards.
        self.assertIn(entry["pack_class"], (None, "CapabilityPack"))


class GateCourtTests(unittest.TestCase):
    """Every gate under real rdflib, against every witness."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = load(ONTOLOGY)

    def test_every_gate_has_codes_and_a_deterministic_shape(self) -> None:
        seen: dict[str, str] = {}
        for gate in GATES:
            source = gate.read_text(encoding="utf-8")
            codes = declared_codes(gate)
            with self.subTest(gate=gate.name):
                self.assertTrue(codes)
                self.assertIn("SELECT ?subject ?reason WHERE", source)
                self.assertRegex(source, r"ORDER BY \?subject \?reason\s*$")
                self.assertNotIn("VALUES", source, "no VALUES inside gates")
                self.assertTrue(source.lstrip().startswith("# MESSAGE:"))
                for code in codes:
                    self.assertRegex(code, r"^REFUSED:EOM_[A-Z0-9_]+$")
                    self.assertIn(seen.setdefault(code, gate.name), {gate.name}, "a code belongs to exactly one gate")
        self.assertGreaterEqual(len(seen), 45)

    def test_pass_witnesses_return_zero_rows_and_are_not_vacuous(self) -> None:
        for gate in GATES:
            witness = PACK / "witnesses" / "pass" / f"{gate.stem}.ttl"
            with self.subTest(gate=gate.stem):
                world = load(witness)
                for guard in GUARDS[gate.stem]:
                    self.assertTrue(world.query(PFX + guard).askAnswer, f"vacuity guard: {guard}")
                combined = load(ONTOLOGY, witness)
                self.assertEqual(rows(combined, gate.read_text(encoding="utf-8")), [])

    def test_fail_witnesses_yield_exactly_the_pinned_subject_code_pairs(self) -> None:
        for gate in GATES:
            witness = PACK / "witnesses" / "fail" / f"{gate.stem}.ttl"
            declared = declared_codes(gate)
            with self.subTest(gate=gate.stem):
                result = rows(load(ONTOLOGY, witness), gate.read_text(encoding="utf-8"))
                self.assertEqual({reason for _, reason in result}, declared)
                got = {(local(subject), reason.removeprefix("REFUSED:")) for subject, reason in result}
                self.assertEqual(got, EXPECTED_ROWS[gate.stem])
                # every declared code is hit by at least one pinned pair
                self.assertEqual({code for _, code in EXPECTED_ROWS[gate.stem]}, {c.removeprefix("REFUSED:") for c in declared})

    def test_gate_output_is_deterministic(self) -> None:
        for gate in GATES:
            graph = load(ONTOLOGY, PACK / "witnesses" / "fail" / f"{gate.stem}.ttl")
            first = rows(graph, gate.read_text(encoding="utf-8"))
            self.assertEqual(first, rows(graph, gate.read_text(encoding="utf-8")))
            self.assertEqual(first, sorted(first))

    def test_ontology_alone_and_synthetic_enterprise_pass_every_gate(self) -> None:
        enterprise = load(ONTOLOGY, QUAL_INPUT)
        for gate in GATES:
            with self.subTest(gate=gate.stem):
                self.assertEqual(rows(self.ontology, gate.read_text(encoding="utf-8")), [])
                self.assertEqual(rows(enterprise, gate.read_text(encoding="utf-8")), [])

    def test_every_union_branch_binds_subject_in_its_first_pattern(self) -> None:
        for gate in GATES:
            source = gate.read_text(encoding="utf-8")
            branches = gate_union_branches(source)
            with self.subTest(gate=gate.stem):
                self.assertGreaterEqual(len(branches), 2)
                self.assertEqual(source.count("UNION"), len(branches) - 1)
                for branch in branches:
                    self.assertIn("?subject", first_pattern(branch), branch.strip()[:80])

    def test_jurisdiction_foreign_subjects_are_never_refused(self) -> None:
        foreign = rdflib.Graph()
        foreign.parse(data=f"""
            @prefix ea: <{EA}> .
            @prefix togaf: <{TOGAF}> .
            @prefix ex: <https://example.invalid/foreign/> .
            ex:strategy a ea:Strategy .
            ex:capability a ea:Capability , togaf:Capability .
            ex:abb a ea:ArchitectureBuildingBlock .
            ex:contract a ea:ArchitectureContract .
            ex:package a togaf:WorkPackage .
        """, format="turtle")
        graph = self.ontology + foreign
        for gate in GATES:
            with self.subTest(gate=gate.stem):
                self.assertEqual(rows(graph, gate.read_text(encoding="utf-8")), [])


def mutated(*, remove=(), add="") -> rdflib.Graph:
    """The synthetic enterprise (valid) with targeted edits, plus the pack ontology."""
    graph = load(ONTOLOGY, QUAL_INPUT)
    prefixes = f"""
        @prefix eom: <{EOM}> . @prefix ea: <{EA}> . @prefix ic: <{IC}> . @prefix togaf: <{TOGAF}> .
        @prefix skos: <http://www.w3.org/2004/02/skos/core#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        @prefix org: <http://www.w3.org/ns/org#> . @prefix dcterms: <http://purl.org/dc/terms/> .
        @prefix ex: <https://example.invalid/enterprise/acme/> .
    """
    for fragment in remove:
        victim = rdflib.Graph()
        victim.parse(data=prefixes + fragment, format="turtle")
        for triple in victim:
            graph.remove(triple)
    if add:
        graph.parse(data=prefixes + add, format="turtle")
    return graph


def only(graph: rdflib.Graph, stem: str) -> set[str]:
    return reasons(graph, gate_path(stem))


class AxisCourtTests(unittest.TestCase):
    def test_coordination_with_non_enterprise_shared_data_is_refused(self) -> None:
        graph = mutated(
            remove=["ex:decision eom:chosenModel eom:Unification ; eom:standardizationLevel eom:HIGH . ex:data-customer-master eom:enterpriseScope true ."],
            add="ex:decision eom:chosenModel eom:Coordination ; eom:standardizationLevel eom:LOW . "
                "ex:data-customer-master eom:enterpriseScope false . ex:process-order-to-cash eom:standardVariant false .",
        )
        # keep the decision otherwise consistent: Coordination = HIGH integration, LOW standardization
        graph.remove((URIRef("https://example.invalid/enterprise/acme/process-order-to-cash"), URIRef(EOM + "standardVariant"), Literal(True)))
        self.assertEqual(only(graph, "010_operating_model_decision"), set())
        self.assertEqual(only(graph, "030_axis_obligations"), {"REFUSED:EOM_INTEGRATION_DATA_NOT_SHARED"})

    def test_diversification_with_enterprise_scope_data_is_refused(self) -> None:
        graph = mutated(
            remove=["ex:decision eom:chosenModel eom:Unification ; eom:integrationLevel eom:HIGH ; eom:standardizationLevel eom:HIGH . "
                    "ex:process-order-to-cash eom:standardVariant true ."],
            add="ex:decision eom:chosenModel eom:Diversification ; eom:integrationLevel eom:LOW ; eom:standardizationLevel eom:LOW . "
                "ex:process-order-to-cash eom:standardVariant false .",
        )
        self.assertEqual(only(graph, "010_operating_model_decision"), set())
        self.assertEqual(only(graph, "030_axis_obligations"), {"REFUSED:EOM_OVERINTEGRATION"})

    def test_replication_with_a_non_standard_process_is_refused(self) -> None:
        graph = mutated(
            remove=["ex:decision eom:chosenModel eom:Unification ; eom:integrationLevel eom:HIGH . ex:data-customer-master eom:enterpriseScope true ."],
            add="ex:decision eom:chosenModel eom:Replication ; eom:integrationLevel eom:LOW . ex:data-customer-master eom:enterpriseScope false . "
                "ex:process-order-to-cash eom:standardVariant false .",
        )
        graph.remove((URIRef("https://example.invalid/enterprise/acme/process-order-to-cash"), URIRef(EOM + "standardVariant"), Literal(True)))
        self.assertEqual(only(graph, "010_operating_model_decision"), set())
        self.assertEqual(only(graph, "030_axis_obligations"), {"REFUSED:EOM_STANDARDIZATION_PROCESS_NOT_STANDARD"})

    def test_four_models_realise_all_four_axis_combinations_exactly_once(self) -> None:
        graph = load(ONTOLOGY)
        combos: dict[tuple[str, str], list[str]] = {}
        for model in graph.subjects(RDF.type, URIRef(EOM + "OperatingModel")):
            integ = graph.value(model, URIRef(EOM + "integrationLevel"))
            std = graph.value(model, URIRef(EOM + "standardizationLevel"))
            code = lambda level: str(graph.value(level, URIRef(EOM + "levelCode")))  # noqa: E731
            combos.setdefault((code(integ), code(std)), []).append(local(str(model)))
        self.assertEqual(
            sorted(combos),
            [("HIGH", "HIGH"), ("HIGH", "LOW"), ("LOW", "HIGH"), ("LOW", "LOW")],
        )
        self.assertTrue(all(len(v) == 1 for v in combos.values()), combos)
        self.assertEqual(combos[("HIGH", "HIGH")], ["Unification"])
        self.assertEqual(combos[("LOW", "LOW")], ["Diversification"])
        self.assertEqual(combos[("HIGH", "LOW")], ["Coordination"])
        self.assertEqual(combos[("LOW", "HIGH")], ["Replication"])


class MaturityCourtTests(unittest.TestCase):
    STAGE3 = (
        "ex:decision eom:atStage eom:StageOptimizedCore . "
        'ex:evidence-stage-3 a eom:StageEvidence ; eom:forDecision ex:decision ; eom:forStage eom:StageOptimizedCore ; '
        'eom:receiptDigest "sha256:' + "ab" * 32 + '" .'
    )

    def test_stage_three_without_a_standard_core_is_refused(self) -> None:
        graph = mutated(
            remove=["ex:decision eom:atStage eom:StageStandardizedTechnology ."],
            add=self.STAGE3 + " ex:process-order-to-cash eom:standardVariant false .",
        )
        graph.remove((URIRef("https://example.invalid/enterprise/acme/process-order-to-cash"), URIRef(EOM + "standardVariant"), Literal(True)))
        self.assertEqual(only(graph, "040_maturity_progression"), {"REFUSED:EOM_MATURITY_STAGE3_NOT_STANDARD_CORE"})

    def test_stage_three_with_a_standard_core_is_accepted(self) -> None:
        graph = mutated(remove=["ex:decision eom:atStage eom:StageStandardizedTechnology ."], add=self.STAGE3)
        self.assertEqual(only(graph, "040_maturity_progression"), set())

    def test_skipping_a_stage_is_refused(self) -> None:
        graph = mutated(
            remove=["ex:decision eom:atStage eom:StageStandardizedTechnology ."],
            add=self.STAGE3,
        )
        # drop the stage-1 evidence: the claim of stage 3 now skips stage 1
        for ev in list(graph.subjects(RDF.type, URIRef(EOM + "StageEvidence"))):
            if graph.value(ev, URIRef(EOM + "forStage")) == URIRef(EOM + "StageBusinessSilos"):
                graph.remove((ev, None, None))
        self.assertEqual(only(graph, "040_maturity_progression"), {"REFUSED:EOM_MATURITY_SKIP"})

    def test_stage_claim_with_no_evidence_for_itself_is_refused(self) -> None:
        graph = mutated(add="ex:decision eom:atStage eom:StageBusinessModularity .")
        self.assertIn("REFUSED:EOM_MATURITY_UNEVIDENCED", only(graph, "040_maturity_progression"))

    ACME = "https://example.invalid/enterprise/acme/"

    def stage_evidence(self, graph: rdflib.Graph, stage: str) -> URIRef:
        found = [ev for ev in graph.subjects(RDF.type, URIRef(EOM + "StageEvidence"))
                 if graph.value(ev, URIRef(EOM + "forStage")) == URIRef(EOM + stage)]
        self.assertEqual(len(found), 1, stage)
        return found[0]

    def set_digest(self, graph: rdflib.Graph, evidence: URIRef, value: str) -> None:
        graph.remove((evidence, URIRef(EOM + "receiptDigest"), None))
        graph.add((evidence, URIRef(EOM + "receiptDigest"), Literal(value)))

    def test_a_malformed_digest_on_the_claimed_stage_is_no_evidence(self) -> None:
        graph = mutated()
        self.set_digest(graph, self.stage_evidence(graph, "StageStandardizedTechnology"), "garbage")
        self.assertEqual(only(graph, "040_maturity_progression"), {"REFUSED:EOM_MATURITY_UNEVIDENCED"})

    def test_a_malformed_digest_on_a_lower_stage_is_no_evidence_so_the_claim_skips_it(self) -> None:
        graph = mutated()
        self.set_digest(graph, self.stage_evidence(graph, "StageBusinessSilos"), "sha256:abc")
        self.assertEqual(only(graph, "040_maturity_progression"), {"REFUSED:EOM_MATURITY_SKIP"})

    def test_a_well_formed_digest_on_every_stage_is_accepted(self) -> None:
        self.assertEqual(only(mutated(), "040_maturity_progression"), set())

    def test_stage_one_needs_no_linking_automation(self) -> None:
        # the stage-2 prerequisite (linking automation) must not leak down to a stage-1 claim
        graph = mutated(
            remove=["ex:decision eom:atStage eom:StageStandardizedTechnology ."],
            add="ex:decision eom:atStage eom:StageBusinessSilos .",
        )
        for link in list(graph.objects(URIRef(self.ACME + "foundation"), URIRef(EOM + "hasLinkingAutomation"))):
            graph.remove((URIRef(self.ACME + "foundation"), URIRef(EOM + "hasLinkingAutomation"), link))
        self.assertEqual(only(graph, "040_maturity_progression"), set())

    def test_stage_two_needs_no_standard_core_process(self) -> None:
        # the stage-3 prerequisite (a standard core) must not leak down to a stage-2 claim
        graph = mutated(add="ex:process-order-to-cash eom:standardVariant false .")
        graph.remove((URIRef(self.ACME + "process-order-to-cash"), URIRef(EOM + "standardVariant"), Literal(True)))
        self.assertEqual(only(graph, "040_maturity_progression"), set())

    def test_stage_two_without_linking_automation_is_refused(self) -> None:
        graph = mutated()
        for link in list(graph.objects(URIRef(self.ACME + "foundation"), URIRef(EOM + "hasLinkingAutomation"))):
            graph.remove((URIRef(self.ACME + "foundation"), URIRef(EOM + "hasLinkingAutomation"), link))
        self.assertEqual(only(graph, "040_maturity_progression"), {"REFUSED:EOM_MATURITY_STAGE2_NO_SHARED_INFRA"})

    def test_stage_ordinals_follow_the_notation_numbering(self) -> None:
        ours = load(ONTOLOGY)
        for stage in ours.subjects(RDF.type, URIRef(EOM + "MaturityStage")):
            notation = str(ours.value(stage, SKOS_NOTATION))
            ordinal = int(ours.value(stage, URIRef(EOM + "stageOrdinal")))
            self.assertEqual(int(notation.split("-")[1]), ordinal, notation)


class AdmCourtTests(unittest.TestCase):
    def test_missing_artifact_is_refused(self) -> None:
        graph = mutated(remove=["ex:record-prelim eom:produced ex:artifact-governance ."])
        self.assertEqual(only(graph, "060_adm_phase_gate"), {"REFUSED:EOM_ADM_ARTIFACT_MISSING"})

    def test_missing_predecessor_is_refused(self) -> None:
        graph = mutated(add=(
            "ex:record-c a eom:PhaseRecord ; eom:ofEngagement ex:adm-run ; eom:phase eom:AdmPhaseC ; eom:status \"ACHIEVED\" ; "
            "eom:produced ex:artifact-is ; eom:reqMgmtReview ex:review-prelim . "
            "ex:artifact-is a eom:Artifact ; eom:artifactKind eom:KindInformationSystemsArchitecture ."
        ))
        self.assertEqual(only(graph, "060_adm_phase_gate"), {"REFUSED:EOM_ADM_PREDECESSOR_NOT_ACHIEVED"})

    def test_missing_requirements_review_is_refused(self) -> None:
        graph = mutated(remove=["ex:record-prelim eom:reqMgmtReview ex:review-prelim ."])
        self.assertEqual(only(graph, "060_adm_phase_gate"), {"REFUSED:EOM_ADM_REQMGMT_MISSING"})

    def test_a_cycle_in_the_chain_is_refused(self) -> None:
        graph = mutated(add="eom:AdmPhaseA eom:precedes eom:AdmPrelim .")
        result = rows(graph, gate_path("060_adm_phase_gate").read_text(encoding="utf-8"))
        # the back edge also makes A a predecessor of PRELIM, which the achieved PRELIM record lacks
        self.assertEqual({reason for _, reason in result}, {"REFUSED:EOM_ADM_CYCLE", "REFUSED:EOM_ADM_PREDECESSOR_NOT_ACHIEVED"})
        self.assertEqual({local(s) for s, reason in result if reason == "REFUSED:EOM_ADM_CYCLE"}, {"AdmPrelim", "AdmPhaseA"})

    def test_requirements_management_needs_no_predecessor_or_review(self) -> None:
        graph = mutated(add=(
            "ex:record-rm a eom:PhaseRecord ; eom:ofEngagement ex:adm-run ; eom:phase eom:AdmReqMgmt ; eom:status \"ACHIEVED\" ; "
            "eom:produced ex:artifact-rm . ex:artifact-rm a eom:Artifact ; eom:artifactKind eom:KindRequirementsRegister ."
        ))
        self.assertEqual(only(graph, "060_adm_phase_gate"), set())


class JurisdictionAndGuardTests(unittest.TestCase):
    def test_strategy_without_enterprise_marker_is_not_refused_but_with_it_is(self) -> None:
        graph = mutated(add="ex:foreign-strategy a ea:Strategy .")
        self.assertEqual(only(graph, "010_operating_model_decision"), set())
        graph = mutated(add="ex:marked-strategy a ea:Strategy ; eom:ofEnterprise ex:enterprise .")
        self.assertEqual(only(graph, "010_operating_model_decision"), {"REFUSED:EOM_STRATEGY_NO_OPMODEL"})

    def test_work_package_without_enterprise_marker_is_not_refused_but_with_it_is(self) -> None:
        graph = mutated(add="ex:foreign-wp a togaf:WorkPackage .")
        self.assertEqual(only(graph, "050_engagement_model"), set())
        graph = mutated(add="ex:marked-wp a togaf:WorkPackage ; eom:ofEnterprise ex:enterprise .")
        self.assertEqual(only(graph, "050_engagement_model"), {"REFUSED:EOM_WORKPACKAGE_UNREVIEWED"})

    def test_unmarked_capability_is_not_refused_as_floating(self) -> None:
        graph = mutated(add="ex:foreign-cap a ea:Capability .")
        self.assertEqual(only(graph, "070_value_stream_anchoring"), set())
        graph = mutated(add="ex:lonely-cap a ea:Capability , eom:EnterpriseCapability ; eom:ofEnterprise ex:enterprise .")
        self.assertEqual(only(graph, "070_value_stream_anchoring"), {"REFUSED:EOM_CAPABILITY_FLOATING"})

    def test_do_is_not_representable_anywhere_in_the_ontology(self) -> None:
        graph = load(ONTOLOGY)
        for term in set(graph.subjects()) | set(graph.predicates()) | set(graph.objects()):
            if isinstance(term, URIRef) and str(term).startswith(EOM):
                self.assertNotRegex(local(str(term)), r"(?i)^(do|grantsDoAuthority|authorityClass)$")
        for _, _, obj in graph:
            if isinstance(obj, Literal):
                self.assertNotEqual(str(obj).upper(), "DO")

    def test_do_is_refused_by_the_authority_fence_on_a_real_decision(self) -> None:
        graph = mutated(add='ex:decision eom:authorityCeiling "DO" .')
        self.assertIn("REFUSED:EOM_AUTHORITY_DO_FORBIDDEN", only(graph, "080_authority_fence"))


class DriftTests(unittest.TestCase):
    """The notation join with togaf-adm-pack and IRI-only use of enterprise-architecture-pack."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.togaf = load(TOGAF_PACK / "ontology.ttl")
        cls.togaf_notations = notations(cls.togaf)
        cls.ours = load(ONTOLOGY)

    def test_operating_model_notations_equal_togaf(self) -> None:
        theirs = {n for n in self.togaf_notations if n.startswith("OM-")}
        mine = {n for n in notations(self.ours) if n.startswith("OM-")}
        self.assertEqual(mine, theirs)
        self.assertEqual(len(mine), 4)

    def test_maturity_notations_equal_togaf(self) -> None:
        theirs = {n for n in self.togaf_notations if n.startswith("MAT-")}
        mine = {n for n in notations(self.ours) if n.startswith("MAT-")}
        self.assertEqual(mine, theirs)
        self.assertEqual(len(mine), 4)

    def test_adm_notations_equal_togaf(self) -> None:
        theirs = {n for n in self.togaf_notations if n.startswith("ADM-") and n != "ADM-PHASES"}
        mine = {n for n in notations(self.ours) if n.startswith("ADM-")}
        self.assertEqual(mine, theirs)
        self.assertEqual(len(mine), 10)

    def test_precedes_visits_exactly_the_adm_phases_in_chain_order(self) -> None:
        phase_notation = {
            s: str(self.ours.value(s, SKOS_NOTATION))
            for s in self.ours.subjects(RDF.type, URIRef(EOM + "AdmPhase"))
        }
        precedes = URIRef(EOM + "precedes")
        visited = {s for s, _, o in self.ours.triples((None, precedes, None))} | {
            o for _, _, o in self.ours.triples((None, precedes, None))
        }
        self.assertEqual(
            {phase_notation[p] for p in visited},
            {n for n in self.togaf_notations if n.startswith("ADM-") and n not in {"ADM-PHASES", "ADM-REQ-MGMT"}},
        )
        # walk the chain from the phase with no predecessor
        successors = {s: o for s, _, o in self.ours.triples((None, precedes, None))}
        heads = [p for p in visited if p not in successors.values()]
        self.assertEqual(len(heads), 1)
        chain = [heads[0]]
        while chain[-1] in successors:
            chain.append(successors[chain[-1]])
        self.assertEqual(
            [phase_notation[p] for p in chain],
            ["ADM-PRELIM"] + [f"ADM-PHASE-{letter}" for letter in "ABCDEFGH"],
        )
        # requirements management is continuous: outside the chain
        reqmgmt = [p for p, n in phase_notation.items() if n == "ADM-REQ-MGMT"]
        self.assertEqual(len(reqmgmt), 1)
        self.assertNotIn(reqmgmt[0], visited)

    def test_every_phase_requires_at_least_one_artifact_kind(self) -> None:
        for phase in self.ours.subjects(RDF.type, URIRef(EOM + "AdmPhase")):
            self.assertTrue(list(self.ours.objects(phase, URIRef(EOM + "requiresArtifactKind"))), phase)

    def test_referenced_engagement_notations_exist_in_togaf(self) -> None:
        theirs = {n for n in self.togaf_notations if n.startswith("ENG-")}
        self.assertEqual(len(theirs), 3)
        referenced: set[str] = set()
        for path in pack_text_files():
            referenced |= set(re.findall(r'"(ENG-[A-Z][A-Z0-9-]*)"', path.read_text(encoding="utf-8")))
        self.assertTrue(referenced)
        self.assertLessEqual(referenced, theirs)
        # the ontology itself restates no ENG-* identity
        self.assertEqual({n for n in notations(self.ours) if n.startswith("ENG-")}, set())

    def test_togaf_anchor_iri_equals_the_one_in_togaf_adm_pack(self) -> None:
        declared = re.search(r"@prefix\s+togaf:\s+<([^>]+)>", (TOGAF_PACK / "ontology.ttl").read_text(encoding="utf-8"))
        self.assertEqual(declared.group(1), TOGAF)
        for path in pack_text_files():
            text = path.read_text(encoding="utf-8")
            for found in re.findall(r"(?:@prefix|PREFIX)\s+togaf:\s+<([^>]+)>", text):
                self.assertEqual(found, TOGAF, path)

    def test_togaf_local_names_used_exist_in_togaf_adm_pack(self) -> None:
        known = {local(str(t)) for t in set(self.togaf.subjects()) | set(self.togaf.objects()) if str(t).startswith(TOGAF)}
        used: set[str] = set()
        for path in pack_text_files():
            used |= set(re.findall(r"\btogaf:([A-Za-z][A-Za-z0-9_]*)", path.read_text(encoding="utf-8")))
        self.assertTrue(used)
        self.assertLessEqual(used, known)

    def test_ea_prefix_iri_and_local_names_exist_in_enterprise_architecture_pack(self) -> None:
        text = (EA_PACK / "ontology.ttl").read_text(encoding="utf-8")
        self.assertEqual(re.search(r"@prefix\s+ea:\s+<([^>]+)>", text).group(1), EA)
        graph = load(EA_PACK / "ontology.ttl")
        known = {
            local(str(t))
            for t in set(graph.subjects()) | set(graph.predicates()) | set(graph.objects())
            if str(t).startswith(EA)
        }
        used: set[str] = set()
        for path in pack_text_files():
            body = path.read_text(encoding="utf-8")
            for found in re.findall(r"(?:@prefix|PREFIX)\s+ea:\s+<([^>]+)>", body):
                self.assertEqual(found, EA, path)
            used |= set(re.findall(r"\bea:([A-Za-z][A-Za-z0-9_]*)", body))
        self.assertTrue(used)
        self.assertLessEqual(used, known, sorted(used - known))

    def test_ontology_declares_no_ea_or_togaf_prefix(self) -> None:
        text = ONTOLOGY.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"@prefix\s+(ea|eap|togaf):")

    def test_ic_terms_used_exist_in_the_industry_closure_ontology(self) -> None:
        ic = load(IC_PACK / "ontology.ttl")
        known = {local(str(t)) for t in set(ic.subjects()) | set(ic.predicates()) | set(ic.objects()) if str(t).startswith(IC)}
        used: set[str] = set()
        for path in pack_text_files():
            body = path.read_text(encoding="utf-8")
            used |= set(re.findall(r"\bic:([A-Za-z][A-Za-z0-9_]*)", body))
            used |= set(re.findall(re.escape(IC) + r"([A-Za-z][A-Za-z0-9_]*)", body))
        self.assertTrue(used)
        self.assertLessEqual(used, known, sorted(used - known))

    def test_eom_terms_used_by_gates_queries_templates_are_declared(self) -> None:
        known = {
            local(str(t)) for t in set(self.ours.subjects()) | set(self.ours.predicates()) | set(self.ours.objects())
            if str(t).startswith(EOM)
        }
        # deliberately undeclared names that gates reference only to refuse them
        refused_only = {"grantsDoAuthority", "authorityClass", "DO"}
        for path in [*GATES, *sorted((PACK / "queries").iterdir()), *sorted((PACK / "templates").iterdir())]:
            used = set(re.findall(r"\beom:([A-Za-z][A-Za-z0-9_]*)", path.read_text(encoding="utf-8")))
            with self.subTest(path=path.name):
                self.assertLessEqual(used - refused_only, known, sorted(used - refused_only - known))
        self.assertTrue(refused_only.isdisjoint(known))


class ReviewRegressionTests(unittest.TestCase):
    """Each case pins a gap an adversarial reviewer reproduced: a missing property must not switch a gate off."""

    def test_an_untyped_or_dangling_dispensation_does_not_exempt_a_work_package(self) -> None:
        graph = mutated(add="ex:wp-loose a togaf:WorkPackage ; eom:ofEnterprise ex:enterprise ; eom:dispensation ex:nothing-here .")
        self.assertEqual(only(graph, "050_engagement_model"), {"REFUSED:EOM_WORKPACKAGE_UNREVIEWED"})

    def test_a_typed_dispensation_without_owner_or_expiry_neither_exempts_nor_goes_unreported(self) -> None:
        graph = mutated(add="ex:wp-loose a togaf:WorkPackage ; eom:ofEnterprise ex:enterprise ; eom:dispensation ex:disp-bare . "
                            "ex:disp-bare a eom:Dispensation .")
        self.assertEqual(only(graph, "050_engagement_model"), {"REFUSED:EOM_WORKPACKAGE_UNREVIEWED", "REFUSED:EOM_DISPENSATION_UNBOUNDED"})

    def test_a_bounded_dispensation_still_exempts(self) -> None:
        graph = mutated(add='ex:wp-ok a togaf:WorkPackage ; eom:ofEnterprise ex:enterprise ; eom:dispensation ex:disp-good . '
                            'ex:disp-good a eom:Dispensation ; eom:owner ex:someone ; eom:expires "2031-01-01"^^xsd:date .')
        self.assertEqual(only(graph, "050_engagement_model"), set())

    def test_an_enterprise_capability_without_ofenterprise_is_still_checked_for_anchoring(self) -> None:
        graph = mutated(add='ex:cap-drifting a ea:Capability , eom:EnterpriseCapability ; ic:capabilityKey "CAP-DRIFTING" .')
        self.assertEqual(only(graph, "070_value_stream_anchoring"), {"REFUSED:EOM_CAPABILITY_FLOATING"})

    def test_a_strategy_a_decision_answers_must_name_its_enterprise(self) -> None:
        graph = mutated(add="ex:strategy-bare a ea:Strategy . ex:decision-bare a eom:OperatingModelDecision ; eom:forStrategy ex:strategy-bare .")
        self.assertIn("REFUSED:EOM_STRATEGY_NO_ENTERPRISE", only(graph, "010_operating_model_decision"))

    def test_an_unrelated_strategy_is_still_outside_jurisdiction(self) -> None:
        graph = mutated(add="ex:someone-elses-strategy a ea:Strategy .")
        self.assertNotIn("REFUSED:EOM_STRATEGY_NO_ENTERPRISE", only(graph, "010_operating_model_decision"))
        self.assertNotIn("REFUSED:EOM_STRATEGY_NO_OPMODEL", only(graph, "010_operating_model_decision"))

    def test_an_achieved_phase_without_a_notation_still_needs_its_requirements_review(self) -> None:
        graph = mutated(add="ex:phase-bare a eom:AdmPhase . ex:run-bare a eom:AdmEngagement . "
                            'ex:record-bare a eom:PhaseRecord ; eom:phase ex:phase-bare ; eom:ofEngagement ex:run-bare ; eom:status "ACHIEVED" .')
        self.assertEqual(only(graph, "060_adm_phase_gate"), {"REFUSED:EOM_ADM_REQMGMT_MISSING"})

    def test_do_is_refused_as_an_iri_as_a_class_and_as_a_non_false_grant(self) -> None:
        for fragment in (
            "ex:x eom:authorityClaim eom:DO .",
            "ex:x eom:authorityCeiling eom:DO .",
            'ex:x eom:authorityClass "do" .',
            "ex:x eom:grantsDoAuthority true .",
            'ex:x eom:grantsDoAuthority "true" .',
            "ex:x eom:grantsDoAuthority 1 .",
            "ex:x eom:someProperty eom:DO .",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn("REFUSED:EOM_AUTHORITY_DO_FORBIDDEN", only(mutated(add=fragment), "080_authority_fence"))

    def test_a_typed_false_grant_and_a_lawful_ceiling_are_not_refused(self) -> None:
        graph = mutated(add='ex:x eom:grantsDoAuthority false ; eom:authorityCeiling "CONSTRUCT" ; eom:authorityClaim "NONE" .')
        self.assertEqual(only(graph, "080_authority_fence"), set())


class GenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = load(ONTOLOGY, QUAL_INPUT)
        cls.requirements = query_rows(cls.graph, "10-requirements.rq")
        cls.skeleton_rows = query_rows(cls.graph, "20-abb-skeletons.rq")

    def test_queries_return_literals_only(self) -> None:
        for name in ("10-requirements.rq", "20-abb-skeletons.rq"):
            result = self.graph.query((PACK / "queries" / name).read_text(encoding="utf-8"))
            for row in result:
                for var in result.vars:
                    self.assertIsInstance(row[var], Literal, (name, var))

    def test_every_foundation_element_yields_one_requirement_row(self) -> None:
        self.assertEqual(len(self.requirements), 3)
        self.assertEqual(
            sorted(r["elementKey"] for r in self.requirements),
            ["customer-master", "integration-bus", "order-to-cash"],
        )
        self.assertEqual(self.requirements, sorted(self.requirements, key=lambda r: (r["decisionKey"], r["elementKey"], r["capabilityKey"])))

    def test_skeletons_only_for_capabilities_without_an_abb(self) -> None:
        self.assertEqual(sorted(r["capabilityKey"] for r in self.skeleton_rows), ["CAP-CUSTOMER-DATA", "CAP-ORDER-TO-CASH"])

    def test_requirements_render_to_the_ic_shape(self) -> None:
        out = render("architecture-requirements.ttl.tera", self.requirements)
        produced = rdflib.Graph()
        produced.parse(data=out, format="turtle")
        requirement = URIRef(IC + "Requirement")
        subjects = list(produced.subjects(RDF.type, requirement))
        self.assertEqual(len(subjects), 3)
        for s in subjects:
            for prop in ("requirementId", "statement", "inClosure", "disposition", "requiresCapability", "originAuthority"):
                self.assertEqual(len(list(produced.objects(s, URIRef(IC + prop)))), 1, (s, prop))
            self.assertEqual(produced.value(s, URIRef(IC + "disposition")), URIRef(IC + "IN_SCOPE"))
            self.assertRegex(str(produced.value(s, URIRef(IC + "requirementId"))), r"^[A-Za-z0-9._-]+$")
            self.assertEqual(produced.value(s, URIRef(IC + "inClosure")), URIRef("https://example.invalid/closure/acme"))
            self.assertEqual(
                produced.value(s, URIRef(IC + "originAuthority")),
                URIRef("https://example.invalid/enterprise/acme/strategy"),
            )
        self.assertEqual(len(produced), 3 * 7 + 0)

    def test_skeletons_are_pending_human_approval_with_no_authority(self) -> None:
        out = render("abb-skeletons.ttl.tera", self.skeleton_rows)
        produced = rdflib.Graph()
        produced.parse(data=out, format="turtle")
        contracts = list(produced.subjects(RDF.type, URIRef(EA + "ArchitectureContract")))
        abbs = list(produced.subjects(RDF.type, URIRef(EA + "ArchitectureBuildingBlock")))
        self.assertEqual(len(contracts), 2)
        self.assertEqual(len(abbs), 2)
        for contract in contracts:
            self.assertEqual(list(produced.objects(contract, URIRef(IC + "approvalStatus"))), [URIRef(IC + "PENDING_HUMAN_APPROVAL")])
            self.assertEqual([str(o) for o in produced.objects(contract, URIRef(IC + "authorityClaim"))], ["NONE"])
            self.assertEqual([str(o) for o in produced.objects(contract, URIRef(IC + "standing"))], ["UNKNOWN"])
            self.assertEqual(len(list(produced.objects(contract, URIRef(EA + "hasAuthorityBoundary")))), 1)
            criteria = {local(str(o)) for o in produced.objects(contract, URIRef(EOM + "complianceCriterion"))}
            self.assertEqual(criteria, {"StandardProcessVariant", "SharedDataContract"})
        for abb in abbs:
            self.assertEqual(len(list(produced.objects(abb, URIRef(EA + "realizesCapability")))), 1)
            self.assertEqual(len(list(produced.objects(abb, URIRef(EA + "governedByContract")))), 1)
        boundary = list(produced.subjects(RDF.type, URIRef(EA + "AuthorityBoundary")))
        self.assertEqual(len(boundary), 1)

    def test_compliance_criterion_follows_the_axes_not_the_model_name(self) -> None:
        base = {
            "decisionKey": "D", "capabilityKey": "CAP-X", "baseIri": "https://example.invalid/c/",
            "capabilityIri": "https://example.invalid/cap/x",
        }
        expectations = {
            ("HIGH", "HIGH"): {"StandardProcessVariant", "SharedDataContract"},
            ("LOW", "HIGH"): {"StandardProcessVariant"},   # integration LOW, standardization HIGH
            ("HIGH", "LOW"): {"SharedDataContract"},       # integration HIGH, standardization LOW
            ("LOW", "LOW"): set(),
        }
        for (integration, standardization), want in expectations.items():
            with self.subTest(integration=integration, standardization=standardization):
                out = render("abb-skeletons.ttl.tera", [{**base, "integration": integration, "standardization": standardization}])
                produced = rdflib.Graph()
                produced.parse(data=out, format="turtle")
                got = {local(str(o)) for o in produced.objects(None, URIRef(EOM + "complianceCriterion"))}
                self.assertEqual(got, want)

    def test_rendering_is_byte_deterministic_and_empty_input_is_valid_turtle(self) -> None:
        for template, data in (
            ("architecture-requirements.ttl.tera", self.requirements),
            ("abb-skeletons.ttl.tera", self.skeleton_rows),
        ):
            self.assertEqual(render(template, data), render(template, data))
            empty = render(template, [])
            rdflib.Graph().parse(data=empty, format="turtle")

    def test_fixed_point_after_a_human_merges_the_skeletons(self) -> None:
        skeletons = render("abb-skeletons.ttl.tera", self.skeleton_rows)
        requirements = render("architecture-requirements.ttl.tera", self.requirements)
        merged = rdflib.Graph()
        for path in (ONTOLOGY, QUAL_INPUT):
            merged.parse(path, format="turtle")
        merged.parse(data=skeletons, format="turtle")
        self.assertEqual(query_rows(merged, "20-abb-skeletons.rq"), [])
        self.assertEqual(render("abb-skeletons.ttl.tera", query_rows(merged, "20-abb-skeletons.rq")),
                         render("abb-skeletons.ttl.tera", []))
        self.assertEqual(render("architecture-requirements.ttl.tera", query_rows(merged, "10-requirements.rq")), requirements)
        # the merged world still satisfies every eom gate
        for gate in GATES:
            self.assertEqual(rows(merged, gate.read_text(encoding="utf-8")), [], gate.name)

    def test_an_unkeyed_capability_is_refused_by_the_gate_because_the_query_would_drop_it(self) -> None:
        graph = mutated(remove=['ex:cap-order-to-cash ic:capabilityKey "CAP-ORDER-TO-CASH" .'])
        self.assertEqual(only(graph, "020_foundation_completeness"), {"REFUSED:EOM_ELEMENT_CAPABILITY_UNKEYED"})
        self.assertEqual(len(query_rows(graph, "10-requirements.rq")), 2, "the silent drop the gate exists to prevent")

    def test_generated_triples_never_carry_do_or_approval(self) -> None:
        produced = rdflib.Graph()
        produced.parse(data=render("abb-skeletons.ttl.tera", self.skeleton_rows), format="turtle")
        produced.parse(data=render("architecture-requirements.ttl.tera", self.requirements), format="turtle")
        for s, p, o in produced:
            self.assertNotEqual(o, URIRef(IC + "APPROVED"))
            self.assertNotEqual(str(o).upper(), "DO")
            self.assertNotIn(local(str(p)), {"grantsDoAuthority", "authorityClass"})
            if local(str(p)) == "authorityClaim":
                self.assertEqual(str(o), "NONE")
            if local(str(p)) == "standing":
                self.assertEqual(str(o), "UNKNOWN")


class LintTests(unittest.TestCase):
    GENERATION_FILES = [
        *sorted((PACK / "templates").iterdir()),
        *sorted((PACK / "queries").iterdir()),
        PACK / "ggen.toml",
    ]

    def test_no_approved_token_in_templates_queries_or_project_file(self) -> None:
        for path in self.GENERATION_FILES:
            with self.subTest(path=path.name):
                self.assertNotRegex(path.read_text(encoding="utf-8"), r"(?i)approved")

    def test_no_authority_grant_and_only_none_claims_in_generation_files(self) -> None:
        for path in self.GENERATION_FILES:
            body = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotRegex(body, r"grantsDoAuthority\s+true")
                for claim in re.findall(r"authorityClaim\s+(\"[^\"]*\")", body):
                    self.assertEqual(claim, '"NONE"')
                for standing in re.findall(r"ic:standing\s+(\"[^\"]*\")", body):
                    self.assertIn(standing, {'"UNKNOWN"', '"BLOCKED"'})
                self.assertNotRegex(body, r"authorityCeiling\s+\"DO\"")

    def test_no_hardcoded_ggen_release_commit_or_digest(self) -> None:
        for path in self.GENERATION_FILES:
            body = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotRegex(body, r"\b[0-9a-f]{40}\b")
                self.assertNotRegex(body, r"sha256:[0-9a-f]{64}")
                self.assertNotRegex(body, r"(?i)ggen[ _-]?(version|release)")
                self.assertNotRegex(body, r"(?i)timeout|worker")

    def test_templates_use_only_the_for_if_loop_last_subset(self) -> None:
        allowed_stmt = [
            r"for row in results",
            r"endfor",
            r'if row\.[A-Za-z]+ == "[A-Z]+"',
            r"if loop\.last",
            r"endif",
        ]
        for path in sorted((PACK / "templates").iterdir()):
            body = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                for stmt in re.findall(r"\{%\s*(.*?)\s*%\}", body):
                    self.assertTrue(any(re.fullmatch(p, stmt) for p in allowed_stmt), stmt)
                for expr in re.findall(r"\{\{\s*(.*?)\s*\}\}", body):
                    self.assertRegex(expr, r"^row\.[A-Za-z]+$")
                self.assertNotIn("{#", body)

    def test_templates_write_nowhere_but_through_the_declared_rules(self) -> None:
        for path in sorted((PACK / "templates").iterdir()):
            self.assertNotRegex(path.read_text(encoding="utf-8"), r"(?m)^---\s*$", "no front matter or to: paths")

    def test_no_example_org_iris_and_synthetic_data_uses_example_invalid(self) -> None:
        for path in pack_text_files():
            if path.name == "gate-court.toml":
                continue
            body = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(PACK).as_posix()):
                self.assertNotIn("example.org", body)
        for kind in ("pass", "fail"):
            for witness in sorted((PACK / "witnesses" / kind).iterdir()):
                self.assertIn("https://example.invalid/", witness.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
