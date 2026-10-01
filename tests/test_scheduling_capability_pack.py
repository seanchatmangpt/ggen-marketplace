"""Lane 3, v26.9.30: execution falsifiers for scheduling-capability-pack.

Every test executes real SPARQL via rdflib against the pack's own graph —
rows are observed query results, never asserted shapes. The anti-vacuity
falsifier: every gate must fire on its fail witness and stay silent on its
pass witness; every missed-fire policy and timezone anchor stays inside its
closed vocabulary.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import rdflib

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "scheduling-capability-pack"
NS = rdflib.Namespace("https://ggen.dev/ontology/scheduling-capability#")
DCTERMS = rdflib.Namespace("http://purl.org/dc/terms/")

PINNED_IDS = {"Schedule.At", "Schedule.Cron", "Schedule.Delay"}
MINTED_IDS = {"Schedule.Interval"}
MISS_FIRE_POLICIES = {"catch_up", "skip", "drop"}
TIMEZONE_ANCHORS = {"none", "utc", "named-zone"}
TEMPORAL_KINDS = {"one-shot", "recurring"}


def load(graph_path: Path | None = None) -> rdflib.Graph:
    graph = rdflib.Graph()
    graph.parse(PACK / "ontology.ttl", format="turtle")
    if graph_path is not None:
        graph.parse(graph_path, format="turtle")
    return graph


def gates() -> dict[str, str]:
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted((PACK / "gates").glob("*.rq"))}


def test_court_runner_admits() -> None:
    result = subprocess.run(
        [sys.executable, str(PACK / "qualification" / "verify.py")],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("ADMITTED:scheduling-capability-pack")


def test_six_gates_present() -> None:
    assert sorted(gates()) == [
        "010_capability_requires_realization",
        "020_realization_requires_qualification",
        "030_missed_fire_policy_required",
        "040_consequential_requires_authority",
        "050_capability_identity_impl_free",
        "060_recurring_requires_timezone_anchoring",
    ]


def test_positive_fixture_keeps_every_gate_silent() -> None:
    graph = load(PACK / "qualification" / "fixtures" / "positive.ttl")
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


def test_temporal_vocabulary_stays_in_closed_sets() -> None:
    graph = load()
    for policy in graph.objects(None, NS.missedFirePolicy):
        assert str(policy) in MISS_FIRE_POLICIES, policy
    for anchor in graph.objects(None, NS.timezoneAnchoring):
        assert str(anchor) in TIMEZONE_ANCHORS, anchor
    for kind in graph.objects(None, NS.temporalKind):
        assert str(kind) in TEMPORAL_KINDS, kind


def test_recurring_capabilities_and_their_realizations_declare_anchors() -> None:
    graph = load()
    recurring = list(graph.subjects(NS.temporalKind, rdflib.Literal("recurring")))
    assert recurring, "no recurring capability in the base ontology"
    for cap in recurring:
        assert any(graph.objects(cap, NS.timezoneAnchoring)), cap
    for real in graph.subjects(NS.realizes, None):
        if any(t in recurring for t in graph.objects(real, NS.realizes)):
            assert any(graph.objects(real, NS.timezoneAnchoring)), real


def test_schedule_at_on_consequential_target_requires_authority() -> None:
    graph = load()
    at = graph.value(None, DCTERMS.identifier, rdflib.Literal("Schedule.At"))
    assert at is not None, "Schedule.At missing from the base ontology"
    assert str(next(graph.objects(at, NS.consequence))) == "DO"
    requirement = next(graph.objects(at, NS.authorityRequirement), None)
    assert requirement is not None, "Schedule.At must bind an authority requirement"
    assert "authority" in str(requirement).lower()


def test_realizations_declare_provider_metadata_and_conditions() -> None:
    graph = load()
    realizations = list(graph.subjects(rdflib.RDF.type, NS.CapabilityRealization))
    assert len(realizations) >= 3
    for real in realizations:
        assert any(graph.objects(real, NS.qualificationCondition)), real
        assert any(graph.objects(real, NS.missedFirePolicy)), real
        assert any(graph.objects(real, NS.providerMetadataBasis)), real


def test_no_capability_identity_names_an_implementation() -> None:
    graph = load()
    tokens = ("reactor", "oban", "quantum", "erlang", "elixir", "hex.pm")
    for identifier in graph.objects(None, DCTERMS.identifier):
        assert not any(token in str(identifier).lower() for token in tokens), identifier
