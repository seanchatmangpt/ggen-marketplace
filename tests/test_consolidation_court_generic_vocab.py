"""Real, Chicago-style regression tests for consolidation_court.py's v3 fix.

No mocks anywhere: every test parses real Turtle text through the real
`rdflib`-backed `rdf_vocabulary_set()` (or runs the real on-disk pack
ontologies already committed to this repo) and asserts on the real
returned set/verdict. See ~/.claude/rules/testing-chicago-style.md.

The bug this guards against: v2 of consolidation_court.py counted
standard RDF/RDFS/OWL/XSD meta-vocabulary (Class, Property, domain,
range, label, comment, ...) as "shared vocabulary" between two packs,
which is true of any two hand-authored ontology.ttl files in this repo
regardless of real domain overlap. v3 excludes GENERIC_VOCAB before
computing vocabulary_diff/vocabulary_shared. These tests would fail
against the pre-fix (v2) implementation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import consolidation_court as cc  # noqa: E402


def _write_ttl(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


# Two real, independently-authored TBox declarations (own classes/properties
# via standard RDFS/OWL machinery) with completely disjoint domain content --
# the exact shape that produced v2's false-positive "shared vocabulary".
ONTOLOGY_A = """\
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix fooa: <https://ggen.dev/ontology/fooa#> .

fooa:Widget a rdfs:Class ; rdfs:label "Widget" ; rdfs:comment "A widget." .
fooa:widgetName a owl:DatatypeProperty ;
    rdfs:domain fooa:Widget ;
    rdfs:range <http://www.w3.org/2001/XMLSchema#string> ;
    rdfs:label "widget name" .

fooa:example-widget a fooa:Widget ; fooa:widgetName "example" .
"""

ONTOLOGY_B = """\
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix foob: <https://ggen.dev/ontology/foob#> .

foob:Gadget a rdfs:Class ; rdfs:label "Gadget" ; rdfs:comment "A gadget." .
foob:gadgetPower a owl:DatatypeProperty ;
    rdfs:domain foob:Gadget ;
    rdfs:range <http://www.w3.org/2001/XMLSchema#integer> ;
    rdfs:label "gadget power" .

foob:example-gadget a foob:Gadget ; foob:gadgetPower 42 .
"""

# Same shape, but this time the two ontologies genuinely share a real,
# non-generic domain class/predicate under different namespaces (the case
# v2's fix was originally designed to catch, and v3 must not break).
ONTOLOGY_C = """\
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix fooc: <https://ggen.dev/ontology/fooc#> .

fooc:Module a rdfs:Class .
fooc:mod-one a fooc:Module ; fooc:dependsOnModule fooc:mod-two .
fooc:mod-two a fooc:Module .
"""

ONTOLOGY_D = """\
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix food: <https://ggen.dev/ontology/food#> .

food:Module a rdfs:Class .
food:cli-mod a food:Module ; food:dependsOnModule food:core-mod .
food:core-mod a food:Module .
"""


def test_generic_vocab_terms_are_excluded_from_rdf_vocabulary_set(tmp_path):
    path = _write_ttl(tmp_path, "a.ttl", ONTOLOGY_A)
    vocab = cc.rdf_vocabulary_set((path,))

    # Real domain terms are present.
    assert ("class", "Widget") in vocab
    assert ("predicate", "widgetName") in vocab

    # Generic RDF/RDFS/OWL/XSD meta-vocabulary is excluded, even though the
    # real Turtle content genuinely uses every one of these terms.
    for generic_class in ("Class", "Property"):
        assert ("class", generic_class) not in vocab
    for generic_predicate in ("domain", "range", "label", "comment", "type"):
        assert ("predicate", generic_predicate) not in vocab
    assert ("class", "string") not in vocab
    assert ("class", "integer") not in vocab


def test_two_unrelated_ontologies_no_longer_falsely_share_vocabulary(tmp_path):
    """The exact v2 bug: two ontologies with zero real domain overlap, both
    declaring their own classes/properties via standard RDFS/OWL, used to
    show vocabulary_shared=True purely from the shared meta-vocabulary.
    """
    path_a = _write_ttl(tmp_path, "a.ttl", ONTOLOGY_A)
    path_b = _write_ttl(tmp_path, "b.ttl", ONTOLOGY_B)

    vocab_a = cc.rdf_vocabulary_set((path_a,))
    vocab_b = cc.rdf_vocabulary_set((path_b,))
    common = vocab_a & vocab_b

    assert common == frozenset(), (
        f"expected zero real shared vocabulary between unrelated ontologies, got {common}"
    )


def test_genuinely_shared_domain_vocabulary_across_namespaces_still_detected(tmp_path):
    """v3 must not regress v2's original fix: two ontologies using
    different base namespaces for the SAME real domain vocabulary
    (Module/dependsOnModule) must still show real overlap.
    """
    path_c = _write_ttl(tmp_path, "c.ttl", ONTOLOGY_C)
    path_d = _write_ttl(tmp_path, "d.ttl", ONTOLOGY_D)

    vocab_c = cc.rdf_vocabulary_set((path_c,))
    vocab_d = cc.rdf_vocabulary_set((path_d,))
    common = vocab_c & vocab_d

    assert ("class", "Module") in common
    assert ("predicate", "dependsOnModule") in common
    # The generic rdfs:Class declaration triple must not itself count.
    assert ("class", "Class") not in common


def test_real_wasm4pm_pair_no_longer_shares_vocabulary_after_fix():
    """Regression test against the exact real pair that surfaced this bug:
    wasm4pm-algorithms-pack and wasm4pm-breed-provenance-pack showed
    vocabulary_diff.common=7 under v2, of which 6 were pure generic
    RDF/RDFS/OWL boilerplate (Class, Property, comment, domain, label,
    range). Only "category" was a real (if weak) shared predicate.
    """
    pack_a = REPO_ROOT / "packs" / "wasm4pm-algorithms-pack"
    pack_b = REPO_ROOT / "packs" / "wasm4pm-breed-provenance-pack"
    if not pack_a.is_dir() or not pack_b.is_dir():
        pytest.skip("wasm4pm-algorithms-pack/wasm4pm-breed-provenance-pack not present on disk")

    vocab_a = cc.rdf_vocabulary_set(cc.ontology_files(pack_a))
    vocab_b = cc.rdf_vocabulary_set(cc.ontology_files(pack_b))
    common = vocab_a & vocab_b

    # None of the 6 generic terms v2 counted survive the fix.
    for generic_term in ("Class", "Property", "comment", "domain", "label", "range"):
        assert ("predicate", generic_term) not in common
        assert ("class", generic_term) not in common

    # At most the one real, non-generic shared predicate remains.
    assert common <= frozenset({("predicate", "category")})


def test_generic_vocab_set_contains_no_duplicate_entries():
    """A real, simple sanity check on the constant itself: no accidental
    duplicate strings (which wouldn't break behavior via a Python set, but
    would indicate a copy-paste error worth catching)."""
    as_list = list(cc.GENERIC_VOCAB)
    assert len(as_list) == len(set(as_list))
    assert len(cc.GENERIC_VOCAB) > 20
