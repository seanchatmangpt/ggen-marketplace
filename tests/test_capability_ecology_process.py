"""Lane 3, v26.9.30: execution falsifiers for process-capability-pack.

Every test executes real SPARQL via rdflib against the pack's own graph —
rows are observed query results, never asserted shapes. The anti-vacuity
falsifier: reverting (removing) a gate's negative fixture must be detectable,
and every gate must fire on its fail witness and stay silent on its pass
witness.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import rdflib

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "capability-ecology-pack"
NS = rdflib.Namespace("https://ggen.dev/ontology/process-capability#")
DCTERMS = rdflib.Namespace("http://purl.org/dc/terms/")

PINNED_IDS = {"Process.Spawn", "Process.Supervise", "Process.Signal", "Process.Link"}
MINTED_IDS = {"Process.Monitor", "Process.Unlink"}


def load(graph_path: Path | None = None) -> rdflib.Graph:
    graph = rdflib.Graph()
    graph.parse(PACK / "ontology/process.ttl", format="turtle")
    if graph_path is not None:
        graph.parse(graph_path, format="turtle")
    return graph


def gates() -> dict[str, str]:
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted((PACK / "gates").glob("pcap_*.rq"))}


def test_court_runner_admits() -> None:
    result = subprocess.run(
        [sys.executable, str(PACK / "qualification" / "verify.py")],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"standing": "ALIVE"' in result.stdout


def test_six_gates_present() -> None:
    assert sorted(gates()) == [
        "pcap_010_capability_requires_realization",
        "pcap_020_realization_requires_qualification",
        "pcap_030_supervision_semantics_required",
        "pcap_040_consequential_requires_authority",
        "pcap_050_capability_identity_impl_free",
        "pcap_060_admitted_requires_evidence",
    ]


def test_positive_fixture_keeps_every_gate_silent() -> None:
    graph = load(PACK / "qualification" / "fixtures" / "pcap_positive.ttl")
    for name, query in gates().items():
        rows = list(graph.query(query))
        assert rows == [], f"{name} fired on the positive fixture: {rows}"


def test_each_fail_witness_fires_its_gate_and_pass_witness_is_silent() -> None:
    for name, query in gates().items():
        silent = load(PACK / "witnesses" / "pass" / f"{name}.ttl")
        assert list(silent.query(query)) == [], f"{name} fired on its PASS witness"
        firing = load(PACK / "witnesses" / "fail" / f"{name}.ttl")
        assert len(list(firing.query(query))) >= 1, f"{name} did NOT fire on its FAIL witness (vacuous gate)"


def test_pinned_capability_ids_are_resolver_join_keys() -> None:
    graph = load()
    ids = {str(o) for o in graph.objects(None, DCTERMS.identifier)}
    assert PINNED_IDS <= ids, f"missing pinned ids: {sorted(PINNED_IDS - ids)}"
    assert MINTED_IDS <= ids, f"missing minted sibling ids: {sorted(MINTED_IDS - ids)}"


def test_no_capability_identity_names_an_implementation() -> None:
    graph = load()
    tokens = ("reactor", "oban", "quantum", "erlang", "elixir", "hex.pm")
    for identifier in graph.objects(None, DCTERMS.identifier):
        assert not any(token in str(identifier).lower() for token in tokens), identifier


def test_realizations_declare_provider_metadata_and_conditions() -> None:
    graph = load()
    realizations = list(graph.subjects(rdflib.RDF.type, NS.CapabilityRealization))
    assert len(realizations) >= 2
    for real in realizations:
        assert any(graph.objects(real, NS.qualificationCondition)), real
        assert any(graph.objects(real, NS.versionPinPolicy)), real
        assert any(graph.objects(real, NS.providerMetadataBasis)), real


def test_supervision_capability_and_realizations_declare_semantics() -> None:
    graph = load()
    supervised = list(
        graph.subjects(NS.capabilityFamily, rdflib.Literal("process-supervision"))
    )
    assert supervised, "no supervision-family capability in the base ontology"
    for cap in supervised:
        assert any(graph.objects(cap, NS.supervisionSemantics)), cap
    for real in graph.subjects(NS.realizes, None):
        targets = list(graph.objects(real, NS.realizes))
        if any(t in supervised for t in targets):
            assert any(graph.objects(real, NS.supervisionSemantics)), real


def test_do_capabilities_bind_authority_read_do_not() -> None:
    graph = load()
    for cap in graph.subjects(rdflib.RDF.type, NS.Capability):
        consequence = str(next(graph.objects(cap, NS.consequence)))
        if consequence == "DO":
            assert any(graph.objects(cap, NS.authorityRequirement)), cap
