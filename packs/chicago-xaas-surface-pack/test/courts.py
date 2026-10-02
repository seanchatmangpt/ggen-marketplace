#!/usr/bin/env python3
"""Gate + JSON court library for chicago-xaas-surface-pack (L3 lane, v26.10.1).

SPARQL gates: ASK true = violation (typed REFUSED_CHICAGO_* refusal per gate comment).
JSON courts:  target the RESOLUTIONS R2 machine schema and R3 executive schema.

Real output only - no skips, no acceptance mocks. rdflib is the only dependency.
"""
import hashlib
import json
import pathlib
import re

from rdflib import Graph

PACK_ROOT = pathlib.Path(__file__).resolve().parent.parent
GATES_DIR = PACK_ROOT / "gates"
FIXTURES = PACK_ROOT / "test" / "fixtures"
WITNESS_PASS = FIXTURES / "witnesses" / "pass"
WITNESS_FAIL = FIXTURES / "witnesses" / "fail"
DEFAULT_CORPUS = FIXTURES / "corpus"
SOURCE_DIR = PACK_ROOT / "source"  # L2's vendored graphs (may be absent during the run)
RENDERED_CANONICAL = FIXTURES / "rendered" / "canonical"
RENDERED_REPLAY = FIXTURES / "rendered" / "replay"

# ---- pinned contract constants (RESOLUTIONS R2/R3/R4/R8 + lane contract) ----

EXACT_SUBJECT = "urn:chicago:agentic-payment:purchase-001"
GENERATOR_IDENTITY = "ggen-marketplace/chicago-xaas-surface-pack@26.10.1"
PROJECTION_TYPES = ("machine", "verification", "executive", "replay")
REQUIRED_LAYER_IDS = (
    "sjira", "graphlaw", "sa2a", "pplan", "xaas",
    "ex4pm", "beam4pm", "affidavit", "ashsurface", "marketplace",
)
SUCCESSOR_LAYER_IDS = ("wasm4pm", "castle")
BOUNDARY_CLASSES = ("Core", "LastMile", "Successor")
STANDING_VOCAB = ("UNKNOWN", "PARTIAL_ALIVE", "ALIVE", "BLOCKED", "BUILD_BROKEN", "UNSUPPORTED")
REFUSAL_ATOMS = (
    "above_delegated_limit", "wrong_principal", "delegation_expired",
    "provider_unavailable", "unknown_after_dispatch", "missing_evidence",
    "stale_subject", "policy_drift", "authority_none",
)
CASE_IDS = tuple(f"CHI-CASE-{n:03d}" for n in range(1, 11))
POSITIVE_CASE = "CHI-CASE-001"
# pinned layer table: contract slug -> (source graph layer IRI local, identifier, repository,
# capabilityId, boundaryClass, evidenceHorizon) - from docs/sjira/v26.10.1/goal.ttl
LAYER_TABLE = {
    "sjira":       ("layer-sjira",       "CHI-101-SJIRA",       "seanchatmangpt/ggen_igniter",     "sjira:goal-graph",           "Core",     "ADMITTED_SEMANTIC_SOURCE"),
    "graphlaw":    ("layer-graphlaw",    "CHI-102-GRAPHLAW",    "seanchatmangpt/ash_graphlaw",     "graphlaw:semantic-admission", "Core",     "ADMISSION_EVIDENCE"),
    "sa2a":        ("layer-sa2a",        "CHI-103-SA2A",        "seanchatmangpt/ash_a2a",          "sa2a:capability-route",      "Core",     "CAPABILITY_AND_AUTHORITY_EVIDENCE"),
    "pplan":       ("layer-pplan",       "CHI-104-PPLAN",       "seanchatmangpt/ash_pplan",        "ash_pplan:plan",             "Core",     "PLAN_AND_POLICY_EVIDENCE"),
    "xaas":        ("layer-xaas",        "CHI-105-XAAS",        "seanchatmangpt/xaas",             "xaas:runtime",               "Core",     "EXECUTED_VERIFIED"),
    "ex4pm":       ("layer-ocel",        "CHI-106-OCEL",        "seanchatmangpt/ash_ex4pm",        "ex4pm:ocel",                 "Core",     "OBSERVED_PROCESS_EVIDENCE"),
    "beam4pm":     ("layer-beam4pm",     "CHI-107-BEAM4PM",     "seanchatmangpt/beam4pm",          "beam4pm:conformance",        "Core",     "PROCESS_CONFORMANCE_EVIDENCE"),
    "affidavit":   ("layer-affidavit",   "CHI-108-AFFIDAVIT",   "seanchatmangpt/ash_affidavit",    "affidavit:standing",         "Core",     "CRYPTOGRAPHIC_EVIDENCE"),
    "ashsurface":  ("layer-surface",     "CHI-109-SURFACE",     "seanchatmangpt/ash_surface",      "ash_surface:projection",     "LastMile", "FAITHFUL_HUMAN_PROJECTION"),
    "marketplace": ("layer-marketplace", "CHI-110-MARKETPLACE", "seanchatmangpt/ggen-marketplace", "ggen_marketplace:render",    "LastMile", "DETERMINISTIC_MANUFACTURE"),
}
REQUIRED_CAPABILITY_IDS = tuple(LAYER_TABLE[slug][3] for slug in REQUIRED_LAYER_IDS)
SUCCESSOR_CAPABILITY_IDS = ("wasm4pm:qri", "castle:consequence")
# pinned case -> refusal atom (R4 typed refusal values; CHI-CASE-001 is the positive path)
CASE_REFUSALS = {
    "CHI-CASE-002": "above_delegated_limit",
    "CHI-CASE-003": "wrong_principal",
    "CHI-CASE-004": "delegation_expired",
    "CHI-CASE-005": "provider_unavailable",
    "CHI-CASE-006": "unknown_after_dispatch",
    "CHI-CASE-007": "missing_evidence",
    "CHI-CASE-008": "stale_subject",
    "CHI-CASE-009": "policy_drift",
    "CHI-CASE-010": "authority_none",
}

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


# ---- SPARQL gate machinery ----

def load_graph(*paths):
    graph = Graph()
    for path in paths:
        graph.parse(str(path), format="turtle")
    return graph


def gates():
    return sorted(GATES_DIR.glob("*.rq"))


def gate_violation(graph, gate_path):
    return bool(graph.query(gate_path.read_text()).askAnswer)


def corpus_inputs(explicit=None):
    """Corpus resolution: explicit args -> L2 vendored source/*.ttl -> default fixture corpus."""
    if explicit:
        return [pathlib.Path(p) for p in explicit]
    if SOURCE_DIR.is_dir() and sorted(SOURCE_DIR.glob("*.ttl")):
        return sorted(SOURCE_DIR.glob("*.ttl"))
    if DEFAULT_CORPUS.is_dir() and sorted(DEFAULT_CORPUS.glob("*.ttl")):
        return sorted(DEFAULT_CORPUS.glob("*.ttl"))
    return []


def run_witnesses():
    """Witnesses mode: every gate must stay clean on its pass witness and fire on its fail
    witness (same-stem). Anti-vacuity: a gate that never fires kills the run (exit 1)."""
    rows, bad = [], 0
    for gate in gates():
        stem = gate.stem
        pass_path, fail_path = WITNESS_PASS / f"{stem}.ttl", WITNESS_FAIL / f"{stem}.ttl"
        if not pass_path.is_file() or not fail_path.is_file():
            rows.append(f"witness {stem}: MISSING SAME-STEM WITNESS BAD")
            bad += 1
            continue
        vp = gate_violation(load_graph(pass_path), gate)
        vf = gate_violation(load_graph(fail_path), gate)
        ok = (not vp) and vf
        rows.append(
            f"witness {stem}: pass->{'VIOLATION' if vp else 'clean'} "
            f"fail->{'VIOLATION' if vf else 'clean'} {'OK' if ok else 'BAD'}"
        )
        bad += not ok
    rows.append("RESULT: " + ("REFUSED" if bad else "WITNESSES_OK") + f" ({bad} bad)")
    return rows, bad


def run_corpus(explicit=None):
    inputs = corpus_inputs(explicit)
    if not inputs:
        return ["corpus: NO INPUTS (no explicit files, pack source/ absent, no default corpus)"], 1
    graph = load_graph(*inputs)
    rows = [f"corpus inputs: {', '.join(str(i) for i in inputs)}"]
    bad = 0
    for gate in gates():
        violation = gate_violation(graph, gate)
        rows.append(f"gate {gate.stem}: {'VIOLATION' if violation else 'ok'}")
        bad += violation
    rows.append("RESULT: " + ("REFUSED" if bad else "ADMITTED") + f" ({bad} violations)")
    return rows, bad


# ---- JSON court machinery (R2/R3) ----

def load_json(path):
    return json.loads(pathlib.Path(path).read_text())


def header_errors(doc, expected_type=None, label=""):
    """R2 header law shared by all four projections."""
    errs = []
    tag = label or doc.get("projectionType", "?")
    if doc.get("generated") is not True:
        errs.append(f"{tag}: header generated must be true, got {doc.get('generated')!r}")
    if doc.get("authorityClaim") != "NONE":
        errs.append(f"{tag}: header authorityClaim must be 'NONE', got {doc.get('authorityClaim')!r}")
    if doc.get("subject") != EXACT_SUBJECT:
        errs.append(f"{tag}: header subject must be the exact literal, got {doc.get('subject')!r}")
    ptype = doc.get("projectionType")
    if ptype not in PROJECTION_TYPES:
        errs.append(f"{tag}: projectionType {ptype!r} outside vocabulary {PROJECTION_TYPES}")
    elif expected_type and ptype != expected_type:
        errs.append(f"{tag}: projectionType must be {expected_type!r}")
    digests = doc.get("sourceDigests")
    if not isinstance(digests, list) or not digests:
        errs.append(f"{tag}: sourceDigests must be a non-empty array")
    else:
        for entry in digests:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) \
                    or not HEX64.match(str(entry.get("sha256", ""))):
                errs.append(f"{tag}: bad sourceDigests entry {entry!r}")
    if doc.get("generatorIdentity") != GENERATOR_IDENTITY:
        errs.append(f"{tag}: generatorIdentity must be {GENERATOR_IDENTITY!r}, got {doc.get('generatorIdentity')!r}")
    return errs


def all_four_docs(rendered_dir):
    rendered_dir = pathlib.Path(rendered_dir)
    docs, errs = {}, []
    for ptype in PROJECTION_TYPES:
        path = rendered_dir / f"{ptype}.json"
        if not path.is_file():
            errs.append(f"missing projection doc: {path}")
            continue
        docs[ptype] = load_json(path)
    return docs, errs


def require(cond, errs, tag, message):
    if not cond:
        errs.append(f"{tag}: {message}")


def nonempty_str(value):
    return isinstance(value, str) and value.strip() != ""


def walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from walk_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk_strings(v)
