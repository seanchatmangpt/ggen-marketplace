"""Strata pack corpus courts (lane L9, strata-hardening wave).

Five guards over the real packs/strata-*-pack tree -- no mocks, pure
``tomllib``/``rdflib`` execution:

1. every pack.toml parses and satisfies the self-IRI invariant
   (README.md:69: ``provides`` must contain ``urn:ggen:pack:<pack-id>``
   exactly);
2. isolation-qualification law: ``requires == []`` for every strata pack
   (``scripts/qualify_packs.py`` qualifies each pack in isolation with a
   single-pack ``[packs]`` capsule, so a cross-pack require can never
   resolve -- regression is the FM-PACK-018 failure class);
3. the composition relationship each consumer pack has with
   strata-protocol-pack is documented via a "Relationship note" comment
   in its pack.toml (documentation-only dependency, FM-PACK-014
   remediation);
4. intra-pack undeclared-class court (rdflib): every class IRI used as
   the object of ``a`` (``rdf:type``) within a strata ontology.ttl is
   either declared ``a rdfs:Class`` / ``owl:Class`` in the same file or
   lives in a foreign/standard namespace (rdf:/rdfs:/xsd:/owl: or
   ``https://strata.chatman.ai/ontology# (wire:/pdu: sub-namespaces)`` for valve's wire: references). Protocol,
   valve and pn64 were just fixed for this failure class; this pins it.
5. set-guard: exactly seven ``packs/strata-*-pack`` directories.

Guard 4 is a pure function with a sabotage twin (injected fake triple
set) proving it can actually fire -- a guard that cannot fail is vacuous.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import rdflib

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"

RDF = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = rdflib.Namespace("http://www.w3.org/2002/07/owl#")

STRATA_PACKS = sorted(
    p for p in PACKS.iterdir() if p.is_dir() and p.name.startswith("strata-")
    and p.name.endswith("-pack")
)

CONSUMER_PACKS = (
    "strata-cas-pack",
    "strata-signer-pack",
    "strata-temprun-pack",
    "strata-stratus-pack",
    "strata-pn64-pack",
)

# Namespaces whose class IRIs are foreign to the ontology file and exempt
# from the intra-pack declaration requirement (standard vocabularies plus
# the protocol wire vocabulary valve's ontology references).
FOREIGN_CLASS_NAMESPACES = (
    str(RDF),
    str(RDFS),
    "http://www.w3.org/2001/XMLSchema#",
    str(OWL),
    "https://strata.chatman.ai/ontology/wire#",  # protocol-owned wire: vocabulary, referenced cross-pack by valve
)

CLASS_DECLARATIONS = (RDFS.Class, OWL.Class)


# ---------------------------------------------------------------------------
# Guards (pure functions -> violation lists; empty list = guard passes)
# ---------------------------------------------------------------------------


def self_iri_violations(manifest: dict, name: str) -> list[str]:
    """Self-IRI invariant (README.md:69): [capabilities].provides contains
    exactly the pack's own ``urn:ggen:pack:<name>`` self-URN."""
    bad: list[str] = []
    caps = manifest.get("capabilities")
    if not isinstance(caps, dict):
        return [f"CAPABILITIES_TABLE_MISSING:{name}"]
    provides = caps.get("provides")
    if not isinstance(provides, list):
        return bad + [f"PROVIDES_NOT_LIST:{name}"]
    self_urn = f"urn:ggen:pack:{name}"
    if self_urn not in provides:
        bad.append(f"SELF_IRI_MISSING:{name}:{provides}")
    return bad


def requires_violations(manifest: dict, name: str) -> list[str]:
    """Isolation-qualification law: requires must be exactly [] for every
    strata pack (FM-PACK-018: a cross-pack require can never resolve in
    qualify_packs.py's single-pack capsule)."""
    caps = manifest.get("capabilities")
    if not isinstance(caps, dict):
        return [f"CAPABILITIES_TABLE_MISSING:{name}"]
    requires = caps.get("requires", [])  # absent key == empty (protocol/valve)
    if not isinstance(requires, list):
        return [f"REQUIRES_NOT_LIST:{name}"]
    if requires != []:
        return [f"REQUIRES_NOT_EMPTY:{name}:{requires}"]
    return []


def undeclared_class_violations(graph: rdflib.Graph) -> list[str]:
    """Intra-pack undeclared-class court: every class IRI used as the
    object of ``a`` must be declared ``a rdfs:Class``/``owl:Class`` in the
    same graph, or live in a foreign/standard namespace."""
    bad: list[str] = []
    declared = {
        s
        for s, o in graph.subject_objects(rdflib.RDF.type)
        if o in CLASS_DECLARATIONS
    }
    for subject, class_iri in graph.subject_objects(rdflib.RDF.type):
        if not isinstance(class_iri, rdflib.URIRef):
            continue
        if str(class_iri).startswith(FOREIGN_CLASS_NAMESPACES):
            continue
        if class_iri in declared:
            continue
        bad.append(f"UNDECLARED_CLASS:{subject}:{class_iri}")
    return sorted(bad)


def relationship_note_violations(text: str, name: str) -> list[str]:
    """Cross-pack relationship documentation: the consumer pack.toml
    carries a 'Relationship note' comment naming strata-protocol-pack."""
    if "Relationship note" not in text:
        return [f"RELATIONSHIP_NOTE_MISSING:{name}"]
    if "strata-protocol-pack" not in text:
        return [f"RELATIONSHIP_NOTE_OMITS_PROTOCOL_PACK:{name}"]
    return []


def load_manifest(pack_dir: Path) -> tuple[dict, str]:
    text = (pack_dir / "pack.toml").read_text(encoding="utf-8")
    return tomllib.loads(text), text


def load_graph(path: Path) -> rdflib.Graph:
    graph = rdflib.Graph()
    graph.parse(path, format="turtle")
    return graph


# ---------------------------------------------------------------------------
# Courts over the real corpus (positive witnesses, real execution)
# ---------------------------------------------------------------------------


class TestStrataCorpusCourts:
    def test_exactly_seven_strata_packs(self) -> None:
        # Set-guard: exactly 7 packs/strata-*-pack directories.
        assert len(STRATA_PACKS) == 7, [p.name for p in STRATA_PACKS]

    def test_every_pack_toml_parses_and_has_capabilities(self) -> None:
        for pack_dir in STRATA_PACKS:
            manifest, _ = load_manifest(pack_dir)
            # Reuse the self-IRI guard: it already fails when the
            # capabilities table is missing or provides is malformed.
            assert self_iri_violations(manifest, pack_dir.name) == [], (
                pack_dir.name
            )

    def test_every_pack_provides_exactly_its_self_urn(self) -> None:
        for pack_dir in STRATA_PACKS:
            manifest, _ = load_manifest(pack_dir)
            assert self_iri_violations(manifest, pack_dir.name) == [], (
                pack_dir.name
            )

    def test_every_pack_requires_nothing(self) -> None:
        for pack_dir in STRATA_PACKS:
            manifest, _ = load_manifest(pack_dir)
            assert requires_violations(manifest, pack_dir.name) == [], (
                pack_dir.name
            )

    def test_every_consumer_documents_relationship_note(self) -> None:
        for pack_name in CONSUMER_PACKS:
            _, text = load_manifest(PACKS / pack_name)
            assert relationship_note_violations(text, pack_name) == [], pack_name

    def test_every_strata_ontology_declares_its_used_classes(self) -> None:
        for pack_dir in STRATA_PACKS:
            graph = load_graph(pack_dir / "ontology.ttl")
            violations = undeclared_class_violations(graph)
            assert violations == [], (pack_dir.name, violations)


# ---------------------------------------------------------------------------
# Sabotage twin: the class-declaration guard must FIRE under an injected
# fake triple set. A guard that cannot fail is vacuous.
# ---------------------------------------------------------------------------


class TestClassDeclarationGuardCanFire:
    def test_undeclared_class_guard_fires_on_fake_triples(self) -> None:
        graph = rdflib.Graph()
        graph.parse(
            data=(
                "@prefix ex: <https://example.org/strata-sabotage#> .\n"
                "ex:Thing a ex:Undeclared ;\n"
                '    ex:label "sabotage individual" .\n'
            ),
            format="turtle",
        )
        violations = undeclared_class_violations(graph)
        assert violations, "guard must fire on an undeclared class"
        assert all(
            v.startswith("UNDECLARED_CLASS:") for v in violations
        ), violations

    def test_undeclared_class_guard_stays_silent_when_declared(self) -> None:
        graph = rdflib.Graph()
        graph.parse(
            data=(
                "@prefix ex: <https://example.org/strata-sabotage#> .\n"
                "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
                "ex:Thing a rdfs:Class .\n"
                "ex:Individual a ex:Thing .\n"
            ),
            format="turtle",
        )
        assert undeclared_class_violations(graph) == []

    def test_undeclared_class_guard_exempts_foreign_namespaces(self) -> None:
        graph = rdflib.Graph()
        graph.parse(
            data=(
                "@prefix ex: <https://example.org/strata-sabotage#> .\n"
                "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
                "@prefix wire: <https://strata.chatman.ai/ontology/wire#> .\n"
                "ex:Individual a rdfs:Class, wire:ForeignRef .\n"
            ),
            format="turtle",
        )
        assert undeclared_class_violations(graph) == []


# ---------------------------------------------------------------------------
# Sabotage twins: the self-IRI / requires / relationship-note guards must
# FIRE on synthetic broken fixtures and stay SILENT on the good case.
# ---------------------------------------------------------------------------


class TestSelfIriGuardCanFire:
    def test_self_iri_guard_fires_on_missing_self_urn(self) -> None:
        manifest = tomllib.loads(
            """
            [pack]
            name = "strata-sabotage-pack"

            [capabilities]
            provides = ["urn:ggen:pack:some-other-pack"]
            """
        )
        violations = self_iri_violations(manifest, "strata-sabotage-pack")
        assert violations == [
            "SELF_IRI_MISSING:strata-sabotage-pack:"
            "['urn:ggen:pack:some-other-pack']"
        ], violations

    def test_self_iri_guard_stays_silent_on_good_case(self) -> None:
        manifest = tomllib.loads(
            """
            [pack]
            name = "strata-sabotage-pack"

            [capabilities]
            provides = ["urn:ggen:pack:strata-sabotage-pack"]
            """
        )
        assert self_iri_violations(manifest, "strata-sabotage-pack") == []


class TestRequiresGuardCanFire:
    def test_requires_guard_fires_on_cross_pack_require(self) -> None:
        manifest = tomllib.loads(
            """
            [pack]
            name = "strata-sabotage-pack"

            [capabilities]
            provides = ["urn:ggen:pack:strata-sabotage-pack"]
            requires = ["strata-protocol-pack"]
            """
        )
        violations = requires_violations(manifest, "strata-sabotage-pack")
        assert violations == [
            "REQUIRES_NOT_EMPTY:strata-sabotage-pack:"
            "['strata-protocol-pack']"
        ], violations

    def test_requires_guard_stays_silent_on_empty_requires(self) -> None:
        manifest = tomllib.loads(
            """
            [pack]
            name = "strata-sabotage-pack"

            [capabilities]
            provides = ["urn:ggen:pack:strata-sabotage-pack"]
            """
        )
        assert requires_violations(manifest, "strata-sabotage-pack") == []


class TestRelationshipNoteGuardCanFire:
    def test_relationship_note_guard_fires_on_missing_note(self) -> None:
        text = "# strata-sabotage-pack: no relationship documented\n"
        violations = relationship_note_violations(text, "strata-sabotage-pack")
        assert violations == [
            "RELATIONSHIP_NOTE_MISSING:strata-sabotage-pack"
        ], violations

    def test_relationship_note_guard_fires_on_note_omitting_protocol(self) -> None:
        text = "# Relationship note: relates to strata-some-other-pack\n"
        violations = relationship_note_violations(text, "strata-sabotage-pack")
        assert violations == [
            "RELATIONSHIP_NOTE_OMITS_PROTOCOL_PACK:strata-sabotage-pack"
        ], violations

    def test_relationship_note_guard_stays_silent_on_good_case(self) -> None:
        text = "# Relationship note: consumes strata-protocol-pack wire types.\n"
        assert relationship_note_violations(text, "strata-sabotage-pack") == []
