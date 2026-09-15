"""Real, Chicago-style regression tests for consolidation_court.py's v4 fix.

No mocks anywhere: every test parses real Turtle text through the real
`rdflib`-backed `rdf_vocabulary_set()` (or runs the real, on-disk
ui-shadcn/ui-deckgl/ui-react-remotion court definitions already committed
to this repo) and asserts on the real returned set/verdict. See
~/.claude/rules/testing-chicago-style.md.

The bug this guards against: the 3 UI families (ui-shadcn, ui-deckgl,
ui-react-remotion) were all verdict=ADMITTED under v3 -- every pair
shared real, non-generic-RDF vocabulary. A real physical kernel+profile-
split design pass found that entire shared vocabulary was `ggen-create`'s
own marketplace-wide tooling scaffold (a GenerationSubject individual
with 10 name-casing predicates), injected into generated packs
regardless of domain, and present in 26 of this marketplace's 318 packs.
v4 excludes TOOLING_VOCAB_NAMESPACES (checked by full IRI, not bare local
name) before computing vocabulary_diff/vocabulary_shared. These tests
would fail against the pre-fix (v3) implementation.
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


# Two real, independently-authored ontologies that each embed ggen-create's
# real scaffold triples (byte-identical to what ggen-create actually
# generates -- see e.g. packs/ai-chatbot-shadcn-pack/ontology.ttl) plus
# their own, genuinely disjoint domain content.
ONTOLOGY_WITH_SCAFFOLD_A = """\
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix gc: <https://ggen.io/ontology/ggen-create#> .
@prefix faketoola: <https://ggen.dev/ontology/faketoola#> .

gc:gc_subject_a a gc:GenerationSubject ;
    gc:name "Button" ;
    gc:upper "BUTTON" ;
    gc:lower "button" ;
    gc:capitalized "Button" ;
    gc:pascal "Button" ;
    gc:camel "button" ;
    gc:snake "button" ;
    gc:upper_snake "BUTTON" ;
    gc:kebab "button" ;
    gc:title "Button" .

faketoola:MyRealDomainThing a rdf:Property .
faketoola:example-a a faketoola:MyRealDomainThing .
"""

ONTOLOGY_WITH_SCAFFOLD_B = """\
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix gc: <https://ggen.io/ontology/ggen-create#> .
@prefix faketoolb: <https://ggen.dev/ontology/faketoolb#> .

gc:gc_subject_b a gc:GenerationSubject ;
    gc:name "chat" ;
    gc:upper "CHAT" ;
    gc:lower "chat" ;
    gc:capitalized "Chat" ;
    gc:pascal "Chat" ;
    gc:camel "chat" ;
    gc:snake "chat" ;
    gc:upper_snake "CHAT" ;
    gc:kebab "chat" ;
    gc:title "Chat" .

faketoolb:UnrelatedOtherThing a rdf:Property .
faketoolb:example-b a faketoolb:UnrelatedOtherThing .
"""


def test_ggen_create_scaffold_terms_are_excluded_from_rdf_vocabulary_set(tmp_path):
    path = _write_ttl(tmp_path, "a.ttl", ONTOLOGY_WITH_SCAFFOLD_A)
    vocab = cc.rdf_vocabulary_set((path,))

    # The real, non-scaffold domain term is present.
    assert ("class", "MyRealDomainThing") in vocab

    # ggen-create's own scaffold class/predicates are excluded, even though
    # the real Turtle content genuinely declares and uses every one of them.
    assert ("class", "GenerationSubject") not in vocab
    for scaffold_predicate in (
        "name", "upper", "lower", "capitalized", "pascal", "camel",
        "snake", "upper_snake", "kebab", "title",
    ):
        assert ("predicate", scaffold_predicate) not in vocab


def test_two_ontologies_sharing_only_ggen_create_scaffold_no_longer_share_vocabulary(tmp_path):
    """The exact v4 bug: two ontologies with genuinely disjoint domain
    content, both carrying ggen-create's own generic scaffold, used to
    show vocabulary_shared=True purely from the shared scaffold.
    """
    path_a = _write_ttl(tmp_path, "a.ttl", ONTOLOGY_WITH_SCAFFOLD_A)
    path_b = _write_ttl(tmp_path, "b.ttl", ONTOLOGY_WITH_SCAFFOLD_B)

    vocab_a = cc.rdf_vocabulary_set((path_a,))
    vocab_b = cc.rdf_vocabulary_set((path_b,))
    common = vocab_a & vocab_b

    assert common == frozenset(), (
        f"expected zero real shared vocabulary between disjoint-domain "
        f"ontologies that merely share ggen-create's scaffold, got {common}"
    )


def test_a_term_with_the_same_local_name_outside_tooling_namespace_is_not_excluded(tmp_path):
    """v4 must be namespace-scoped, not bare-local-name-scoped: a REAL
    domain predicate that happens to be spelled "name" under a pack's own
    namespace (not ggen-create's) must still be counted.
    """
    text = """\
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix realdomain: <https://ggen.dev/ontology/realdomain#> .

realdomain:Thing a rdf:Property .
realdomain:example a realdomain:Thing ; realdomain:name "not ggen-create's name" .
"""
    path = _write_ttl(tmp_path, "c.ttl", text)
    vocab = cc.rdf_vocabulary_set((path,))
    assert ("predicate", "name") in vocab


def test_real_ui_families_are_now_refuted_after_tooling_vocab_exclusion():
    """Regression test against the exact 3 real families that surfaced this
    bug: ui-shadcn, ui-deckgl, and ui-react-remotion were all verdict=
    ADMITTED under v3 (every pair shared vocabulary), driven entirely by
    ggen-create's scaffold. Under v4, none of the three should show any
    real shared vocabulary.
    """
    families = {
        "ui-shadcn": REPO_ROOT / "docs/jira/v26.8.19/families/ui-shadcn.toml",
        "ui-deckgl": REPO_ROOT / "docs/jira/v26.8.19/families/ui-deckgl.toml",
        "ui-react-remotion": REPO_ROOT / "docs/jira/v26.8.19/families/ui-react-remotion.toml",
    }
    for name, toml_path in families.items():
        if not toml_path.is_file():
            pytest.skip(f"{name} family definition not present on disk")

    for name, toml_path in families.items():
        _family_name, _kernel_candidate, member_names = cc.load_family(toml_path)
        members = [cc.load_member(member_name) for member_name in member_names]
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                vocab_a = cc.rdf_vocabulary_set(members[i].ontologies)
                vocab_b = cc.rdf_vocabulary_set(members[j].ontologies)
                common = vocab_a & vocab_b
                assert common == frozenset(), (
                    f"{name}: expected zero real shared vocabulary between "
                    f"{members[i].name} and {members[j].name} after "
                    f"TOOLING_VOCAB_NAMESPACES exclusion, got {common}"
                )


def test_tooling_vocab_namespaces_contains_the_ggen_create_namespace():
    assert "https://ggen.io/ontology/ggen-create#" in cc.TOOLING_VOCAB_NAMESPACES
