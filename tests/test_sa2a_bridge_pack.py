"""Chicago-style court for sa2a-bridge-pack (GGMKT-26922-03).

Real collaborators only: the pack's real ontology.ttl loaded through rdflib,
the pack's real 8 SPARQL gates executed against it (all fail-closed: 0 rows on
the admitted graph, >=1 row on an unlawful mutation), and a real byte-drift
cmp against the xaas consumer's vendored copy when that checkout sits beside
this repo. No mocks.

Fail-witness law: every gate must be a real tripwire. For each gate this court
constructs the minimal unlawful mutation in memory and proves the gate fires.
A gate that cannot fail is vacuous and refuses this pack.

SHA binding: the pack's source tree must keep hashing to the exact
source_sha256 that the pinned ggen (marketplace.toml [ggen].version, v26.8.11)
qualification recorded for this court -- computed with the same
marketplace.fingerprint_paths the qualification runner itself uses. Any byte
change to the pack re-opens the court and the receipt must be re-cut.
"""
from __future__ import annotations

import filecmp
import sys
from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import marketplace  # noqa: E402  (repo-owned, zero-dependency)

from qualify_packs import pack_source_fingerprint  # noqa: E402

PACK = ROOT / "packs" / "sa2a-bridge-pack"
GATES = sorted((PACK / "gates").glob("*.rq"))
# xaas vendors this pack byte-for-byte under priv/sa2a_bridge (GGMKT-26922-03).
# The operator's fixed checkout is the exact subject this court names; the
# sibling checkout layout is the portable fallback.
_XAAS_CANDIDATES = (Path("/Users/sac/xaas"), ROOT.parent / "xaas")
XAAS = next((p for p in _XAAS_CANDIDATES if p.is_dir()), _XAAS_CANDIDATES[0])
VENDORED = XAAS / "priv" / "sa2a_bridge"

S2B = "https://ggen.dev/ontology/sa2a-bridge#"
EMA = "http://seanchatmangpt.github.io/packs/elixir-mcp-a2a#"
RDF_TYPE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

# The receipt this court was cut against: pinned ggen v26.8.11,
# scripts/qualify_packs_r18.py --scope all (shard 3 of 4), subject head
# recorded in receipts/v26.9.22/GGMKT-26922-03.json.
RECEIPTED_SOURCE_SHA256 = "635819b628af28be5f401a949fa7dec11288e1cb980c82242663a73b1d8f0b94"
RECEIPTED_GGEN_VERSION = "26.8.11"

# Autofde-lab commit that added the sa2a_* BEAM-port ops (the pack's own
# raise10 "exact supplier identity binding" -- gate 060 checks the shape,
# this constant pins the value the pack documents in README.md).
EXPECTED_SOURCE_SHA = "b70331aa2b6aae839daef34b25d34b428094efec"

if len(GATES) != 8:
    pytest.fail(f"sa2a-bridge-pack must expose exactly 8 gates, found {len(GATES)}")

GATE_BY_STEM = {gate.stem: gate for gate in GATES}


def load_ontology() -> Graph:
    graph = Graph()
    graph.parse(PACK / "ontology.ttl", format="turtle")
    return graph


def run_gate(graph: Graph, gate: Path) -> list:
    return list(graph.query(gate.read_text(encoding="utf-8")))


class TestOntologyIsReal:
    def test_loads_and_has_five_edge_specs(self) -> None:
        graph = load_ontology()
        assert len(graph) > 100
        edge_class = URIRef(f"{S2B}EdgeSpec")
        edge_specs = [s for s in graph.subjects(RDF_TYPE, edge_class)]
        assert len(edge_specs) == 5

    def test_supplier_identity_binding_is_the_documented_autofde_commit(self) -> None:
        graph = load_ontology()
        bridge = URIRef(f"{S2B}bridge")
        source_shas = [str(o) for o in graph.objects(bridge, URIRef(f"{S2B}sourceSha"))]
        assert source_shas == [EXPECTED_SOURCE_SHA]


class TestAllGatesPassOnAdmittedOntology:
    @pytest.mark.parametrize("gate_path", sorted(GATE_BY_STEM.values()), ids=lambda p: p.stem)
    def test_gate_returns_zero_rows(self, gate_path: Path) -> None:
        rows = run_gate(load_ontology(), gate_path)
        assert rows == [], f"{gate_path.stem} fired on the admitted ontology: {rows}"


class TestFailWitnesses:
    """Each gate must fire on the minimal unlawful mutation (fail witness)."""

    def witness(self, stem: str) -> Graph:
        graph = load_ontology()
        edge40 = URIRef(f"{S2B}edge40")
        edge50 = URIRef(f"{S2B}edge50")
        bridge = URIRef(f"{S2B}bridge")
        create10 = URIRef(f"{S2B}create10")
        if stem == "010_exactly_one_do":
            graph.add((edge50, RDF_TYPE, URIRef(f"{S2B}EdgeSpec")))
            graph.add((edge50, URIRef(f"{S2B}doBoundary"), Literal(True)))
        elif stem == "020_do_is_port_do_only":
            graph.remove((edge40, URIRef(f"{S2B}authority"), Literal("PORT_DO_ONLY")))
            graph.add((edge40, URIRef(f"{S2B}authority"), Literal("AMBIENT")))
        elif stem == "030_errc_complete":
            graph.remove((create10, URIRef(f"{S2B}category"), Literal("CREATE")))
        elif stem == "040_no_ambient_command_policy":
            graph.add((bridge, URIRef(f"{S2B}ambientCommandPolicy"), Literal(True)))
        elif stem == "050_port_do_requires_recovery":
            graph.remove((edge40, URIRef(f"{S2B}recoveryRequired"), Literal(True)))
        elif stem == "060_exact_supplier_identity":
            graph.remove((bridge, URIRef(f"{S2B}sourceSha"), Literal(EXPECTED_SOURCE_SHA)))
            graph.add((bridge, URIRef(f"{S2B}sourceSha"), Literal("not-a-git-sha")))
        elif stem == "070_consequential_requires_authority":
            bad = URIRef(f"{S2B}capUnlawful")
            graph.add((bad, RDF_TYPE, URIRef(f"{EMA}Capability")))
            graph.add((bad, URIRef(f"{EMA}mutationScope"), Literal("consequential")))
            graph.add((bad, URIRef(f"{EMA}requiresAuthority"), Literal(False)))
        elif stem == "080_exposed_via_closed_vocab":
            bad = URIRef(f"{S2B}capUnlawfulVocab")
            graph.add((bad, RDF_TYPE, URIRef(f"{EMA}Capability")))
            graph.add((bad, URIRef(f"{EMA}exposedVia"), Literal("cli")))
        else:  # pragma: no cover - corpus is pinned to 8 gates above
            pytest.fail(f"no fail witness defined for {stem}")
        return graph

    @pytest.mark.parametrize("gate_path", sorted(GATE_BY_STEM.values()), ids=lambda p: p.stem)
    def test_gate_fires_on_unlawful_mutation(self, gate_path: Path) -> None:
        rows = run_gate(self.witness(gate_path.stem), gate_path)
        assert rows, f"{gate_path.stem} is vacuous: no fail witness makes it fire"


class TestXaasVendoredCopyByteDrift:
    """GGMKT-26922-03: the xaas consumer vendors this pack byte-for-byte.

    Skipped when the sibling xaas checkout is absent (e.g. hosted CI); the
    local exact-head court run performs it for real and its receipt records
    the subject SHA.
    """

    @staticmethod
    def assert_identical(pack_file: Path, vendored_file: Path) -> None:
        assert pack_file.exists(), f"missing pack file {pack_file}"
        assert vendored_file.exists(), f"xaas vendored copy missing: {vendored_file}"
        assert filecmp.cmp(pack_file, vendored_file, shallow=False), (
            f"BYTE DRIFT: {pack_file} != {vendored_file} -- edit the owning pack and re-vendor, never the projection"
        )

    @pytest.mark.skipif(not VENDORED.is_dir(), reason="sibling xaas checkout not present")
    def test_ggen_igniter_queries_are_byte_identical(self) -> None:
        for name in ("contract.rq", "edges.rq", "mcp_descriptor.rq"):
            self.assert_identical(PACK / "ggen_igniter" / "queries" / name, VENDORED / "queries" / name)

    @pytest.mark.skipif(not VENDORED.is_dir(), reason="sibling xaas checkout not present")
    def test_ontology_is_byte_identical(self) -> None:
        self.assert_identical(PACK / "ontology.ttl", VENDORED / "ontology" / "ontology.ttl")

    @pytest.mark.skipif(not VENDORED.is_dir(), reason="sibling xaas checkout not present")
    def test_ggen_igniter_templates_are_byte_identical(self) -> None:
        for name in (
            "sa2a_bridge_contract.ex.eex",
            "sa2a_bridge_edges.ex.eex",
            "sa2a_mcp_descriptor.ex.eex",
        ):
            self.assert_identical(PACK / "ggen_igniter" / "templates" / name, VENDORED / "templates" / name)


class TestReceiptBinding:
    """The court's receipt binds this exact pack tree and the pinned ggen."""

    def test_source_tree_hashes_to_the_pinned_qualification_receipt(self) -> None:
        admitted = [p for p in marketplace.require_admitted() if p.name == "sa2a-bridge-pack"]
        assert len(admitted) == 1, "sa2a-bridge-pack must be exactly once admitted"
        assert pack_source_fingerprint(admitted[0]) == RECEIPTED_SOURCE_SHA256, (
            "sa2a-bridge-pack source drifted from the pinned-qualification receipt "
            f"({RECEIPTED_SOURCE_SHA256}); re-run the pinned ggen qualification and re-cut the receipt"
        )

    def test_receipted_ggen_version_still_is_the_marketplace_pin(self) -> None:
        text = (ROOT / "marketplace.toml").read_text(encoding="utf-8")
        assert f'version = "v{RECEIPTED_GGEN_VERSION}"' in text, (
            "marketplace.toml [ggen].version moved past the receipted ggen; re-run the court"
        )
