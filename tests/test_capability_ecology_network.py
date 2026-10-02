"""Gate courts for packs/capability-ecology-pack (lane 2, v26.9.30 wave).

Every gate in gates/ is a violation-row SELECT evaluated (as in
qualification/verify.py) over the union of ontology.ttl and one fixture graph:

* the ontology's own eight capabilities are clean under every gate;
* qualification/fixtures/ncap_positive.ttl is clean under every gate;
* each negative fixture fires at least its named gate (anti-vacuity) and,
  stronger, exactly its own gate and no other;
* witnesses/{pass,fail}/<stem>.ttl are byte-identical copies of the fixtures
  (exact-stem court pairing, gate-court.toml);
* capability identities never carry provider coordinates
  (CAPABILITY != IMPLEMENTATION).
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tomllib
from functools import lru_cache
from pathlib import Path

import pytest
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "capability-ecology-pack"
GATES = PACK / "gates"
FIXTURES = PACK / "qualification" / "fixtures"
PASS = PACK / "witnesses" / "pass"
FAIL = PACK / "witnesses" / "fail"
NS = "https://ggen.dev/ontology/network-capability#"

EXPECTED_STEMS = [
    "ncap_010_capability_requires_realization",
    "ncap_020_realization_requires_qualification_conditions",
    "ncap_030_capability_requires_typed_failure_set",
    "ncap_040_consequential_requires_authority",
    "ncap_050_endpoint_resolution_precondition_required",
    "ncap_060_retry_semantics_declared",
]

PINNED_CAPABILITY_IDS = [
    "Http.Request", "Http.Get", "Http.Post", "Remote.Invoke", "Endpoint.Resolve",
]
# minted family siblings (provider-closed; recorded in README)
MINTED_SIBLING_IDS = ["Http.Put", "Http.Delete", "Http.Head"]

# capability -> >=1 realization dcterms:identifier (provider closure floor)
EXPECTED_REALIZATIONS = {
    "Http.Request": {"Reactor.Req.Dsl.Request"},
    "Http.Get": {"Reactor.Req.Dsl.Get"},
    "Http.Post": {"Reactor.Req.Dsl.Post"},
    "Http.Put": {"Reactor.Req.Dsl.Put"},
    "Http.Delete": {"Reactor.Req.Dsl.Delete"},
    "Http.Head": {"Reactor.Req.Dsl.Head"},
    "Remote.Invoke": {"Reactor.Req.Dsl.Post (Remote.Invoke qualification)"},
    "Endpoint.Resolve": {":inet.getaddr/2"},
}


def gate_stems() -> list[str]:
    return sorted(p.stem for p in GATES.glob("ncap_*.rq"))


@lru_cache(maxsize=None)
def gate_text(stem: str) -> str:
    return (GATES / f"{stem}.rq").read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def graph_for(rdf: Path) -> Graph:
    graph = Graph()
    graph.parse(PACK / "ontology/network.ttl", format="turtle")
    graph.parse(rdf, format="turtle")
    return graph


def rows(stem: str, rdf: Path) -> list:
    return list(graph_for(rdf).query(gate_text(stem)))


def test_gate_inventory_is_exactly_the_contract() -> None:
    assert gate_stems() == EXPECTED_STEMS


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_gate_shape(stem: str) -> None:
    text = gate_text(stem)
    assert text.startswith("# MESSAGE:"), "gate must open with a # MESSAGE: header"
    assert "ORDER BY" in text, "every SELECT needs ORDER BY (ggen E0013)"
    assert "INSERT" not in text and "DELETE" not in text and "CONSTRUCT" not in text, (
        "gates are refusal SELECTs only (FM-PACK-013)"
    )


def test_pinned_capability_ids_are_admitted() -> None:
    found = capability_ids()
    missing = [cid for cid in PINNED_CAPABILITY_IDS if cid not in found]
    assert not missing, f"pinned capability IDs missing from ontology: {missing}"


def test_minted_siblings_are_present_and_recorded() -> None:
    found = capability_ids()
    missing = [cid for cid in MINTED_SIBLING_IDS if cid not in found]
    assert not missing, f"minted siblings missing from ontology: {missing}"
    readme = (PACK / "families" / "network.md").read_text(encoding="utf-8")
    for cid in MINTED_SIBLING_IDS:
        assert cid in readme, f"minted sibling not recorded in README: {cid}"


def capability_ids() -> list[str]:
    return sorted(
        str(row.id) for row in graph_for(FIXTURES / "ncap_positive.ttl").query(
            f"PREFIX ncap: <{NS}> PREFIX dcterms: <http://purl.org/dc/terms/> "
            "SELECT ?id WHERE { ?cap a ncap:Capability ; dcterms:identifier ?id }"
        )
    )


def test_capability_ids_never_carry_provider_coordinates() -> None:
    for cid in capability_ids():
        assert "Reactor" not in cid and "reactor" not in cid and "/2" not in cid, (
            f"capability identity smells like an implementation: {cid}"
        )


def test_every_capability_resolves_to_expected_realization_closure() -> None:
    graph = graph_for(FIXTURES / "ncap_positive.ttl")
    found: dict[str, set[str]] = {}
    for row in graph.query(
        f"PREFIX ncap: <{NS}> PREFIX dcterms: <http://purl.org/dc/terms/> "
        "SELECT ?cid ?rid WHERE { "
        "?cap a ncap:Capability ; dcterms:identifier ?cid ; ncap:realizedBy ?r . "
        "?r dcterms:identifier ?rid }"
    ):
        found.setdefault(str(row.cid), set()).add(str(row.rid))
    for cid, expected in EXPECTED_REALIZATIONS.items():
        assert expected <= found.get(cid, set()), f"{cid}: missing realizations {expected - found.get(cid, set())}"


def test_every_realization_carries_provider_metadata() -> None:
    graph = graph_for(FIXTURES / "ncap_positive.ttl")
    bare = [
        str(row.rid) for row in graph.query(
            f"PREFIX ncap: <{NS}> PREFIX dcterms: <http://purl.org/dc/terms/> "
            "SELECT ?rid WHERE { "
            "?r a ncap:Realization ; dcterms:identifier ?rid . "
            "FILTER NOT EXISTS { ?r ncap:providerModule ?m } }"
        )
    ] + [
        str(row.rid) for row in graph.query(
            f"PREFIX ncap: <{NS}> PREFIX dcterms: <http://purl.org/dc/terms/> "
            "SELECT ?rid WHERE { "
            "?r a ncap:Realization ; dcterms:identifier ?rid . "
            "FILTER NOT EXISTS { ?r ncap:providerRepo ?p } }"
        )
    ]
    assert bare == [], f"realizations without provider metadata: {bare}"


def test_remote_invoke_requires_authority_in_contract() -> None:
    graph = graph_for(FIXTURES / "ncap_positive.ttl")
    unbound = [
        str(row.id) for row in graph.query(
            f"PREFIX ncap: <{NS}> PREFIX dcterms: <http://purl.org/dc/terms/> "
            "SELECT ?id WHERE { "
            "?cap a ncap:Capability ; dcterms:identifier ?id ; ncap:consequenceClass 'DO' . "
            "FILTER NOT EXISTS { ?cap ncap:requiresAuthority true } }"
        )
    ]
    assert unbound == [], f"DO capabilities without authority: {unbound}"


def test_ontology_instance_is_clean_under_every_gate() -> None:
    ontology = Graph()
    ontology.parse(PACK / "ontology/network.ttl", format="turtle")
    dirty = {
        stem: len(list(ontology.query(gate_text(stem))))
        for stem in EXPECTED_STEMS
    }
    assert not any(dirty.values()), f"ontology instance violates its own gates: {dirty}"


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_positive_fixture_yields_zero_rows(stem: str) -> None:
    found = rows(stem, FIXTURES / "ncap_positive.ttl")
    assert found == [], f"{stem}: positive fixture produced {len(found)} rows: {found[:3]}"


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_negative_fixture_fires_its_own_gate(stem: str) -> None:
    found = rows(stem, FIXTURES / f"negative-{stem}.ttl")
    assert len(found) >= 1, f"{stem}: negative fixture produced no rows (vacuous gate)"


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_negative_fixture_trips_only_its_own_gate(stem: str) -> None:
    witness = FIXTURES / f"negative-{stem}.ttl"
    fired = sorted(other for other in EXPECTED_STEMS if rows(other, witness))
    assert fired == [stem], f"{stem}: negative fixture tripped {fired}"


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_witnesses_are_exact_fixture_copies(stem: str) -> None:
    assert (PASS / f"{stem}.ttl").read_bytes() == (FIXTURES / "ncap_positive.ttl").read_bytes()
    assert (FAIL / f"{stem}.ttl").read_bytes() == (FIXTURES / f"negative-{stem}.ttl").read_bytes()


def test_gate_witness_court_structural_pairing() -> None:
    gates = set(gate_stems())
    assert gates == {p.stem for p in PASS.glob("ncap_*.ttl")}
    assert gates == {p.stem for p in FAIL.glob("ncap_*.ttl")}
    # Scoped to THIS pack: the repo-wide `check_gate_witness_courts.py --packs
    # packs/` sweep also courts sibling lanes' in-flight packs during the wave
    # and is coordinator-owned; here only this pack's pairing is asserted.
    spec = importlib.util.spec_from_file_location(
        "check_gate_witness_courts", ROOT / "scripts" / "check_gate_witness_courts.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    record = module.qualify(PACK)
    assert record["standing"] == "ALIVE"
    assert record["case_count"] >= len(gates)  # merged pack: one court, 59 cases


def test_verify_court_admits() -> None:
    completed = subprocess.run(
        [sys.executable, str(PACK / "qualification" / "verify.py")],
        capture_output=True, text=True, check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "ALIVE" in completed.stdout


def test_pack_manifest_conventions() -> None:
    manifest = tomllib.loads((PACK / "pack.toml").read_text(encoding="utf-8"))
    assert set(manifest) == {"pack"}
    assert manifest["pack"]["name"] == "capability-ecology-pack"
    assert manifest["pack"]["version"] == "26.9.0"
    assert manifest["pack"]["description"].strip()
    # FM-PACK-003: [pack] admits only name/version/description.


def test_readme_names_every_gate_firing_fixture() -> None:
    readme = (PACK / "families" / "network.md").read_text(encoding="utf-8")
    for stem in EXPECTED_STEMS:
        assert f"negative-{stem}.ttl" in readme, f"README must name the firing fixture for {stem}"


def test_readme_records_failed_edges() -> None:
    readme = (PACK / "families" / "network.md").read_text(encoding="utf-8")
    assert "## Failed edges" in readme
    for edge in ("reactor_http", "No endpoint-resolution step", "No public vocabulary"):
        assert edge.lower() in readme.lower(), f"failed edge not recorded: {edge}"
