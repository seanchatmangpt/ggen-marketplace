from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SCRIPT = SCRIPTS / "check_cross_pack_references.py"
spec = importlib.util.spec_from_file_location("check_cross_pack_references", SCRIPT)
assert spec is not None and spec.loader is not None
xref = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = xref
spec.loader.exec_module(xref)

_marketplace_spec = importlib.util.spec_from_file_location("marketplace", SCRIPTS / "marketplace.py")
assert _marketplace_spec is not None and _marketplace_spec.loader is not None
_marketplace = importlib.util.module_from_spec(_marketplace_spec)
sys.modules[_marketplace_spec.name] = _marketplace
_marketplace_spec.loader.exec_module(_marketplace)
Pack = _marketplace.Pack


def make_pack(tmp_path: Path, name: str, ontology_text: str, consumer_text: str | None = None) -> Pack:
    pack_dir = tmp_path / name
    pack_dir.mkdir()
    ontology_path = pack_dir / "ontology.ttl"
    ontology_path.write_text(ontology_text, encoding="utf-8")
    if consumer_text is not None:
        qual_dir = pack_dir / "qualification"
        qual_dir.mkdir()
        (qual_dir / "consumer.ttl").write_text(consumer_text, encoding="utf-8")
    return Pack(
        name=name,
        version="0.1.0",
        description="test",
        path=pack_dir,
        ontologies=(ontology_path,),
        templates=(),
        native_gates=(),
        verifier_gates=(),
    )


# --- strip_comments -------------------------------------------------------

def test_strip_comments_removes_trailing_comment():
    text = "ex:a ex:b ex:c . # a real comment\n"
    assert xref.strip_comments(text) == "ex:a ex:b ex:c . "


def test_strip_comments_preserves_hash_inside_iri():
    text = "@prefix ex: <http://example.org/ns#> .\n"
    assert xref.strip_comments(text) == text.rstrip("\n")


def test_strip_comments_preserves_hash_inside_string_literal():
    text = 'ex:a ex:label "not a # comment" .\n'
    assert xref.strip_comments(text) == text.rstrip("\n")


# --- tokenize_statements ---------------------------------------------------

def test_tokenize_statements_splits_on_top_level_dot():
    text = "ex:a ex:b ex:c .\nex:d ex:e ex:f ."
    stmts, skipped = xref.tokenize_statements(text)
    assert len(stmts) == 2
    assert skipped == 0


def test_tokenize_statements_does_not_split_on_decimal_point():
    text = "ex:a ex:weight 3.14 ."
    stmts, skipped = xref.tokenize_statements(text)
    assert len(stmts) == 1
    assert skipped == 0


def test_tokenize_statements_skips_blank_node_bearing_statement():
    # Each bracket character increments the skip counter independently (one
    # for `[`, one for `]`) -- the tokenizer drops the whole in-progress
    # statement per bracket encountered rather than parsing blank nodes.
    text = "ex:a ex:b [ ex:c ex:d ] .\nex:e ex:f ex:g ."
    stmts, skipped = xref.tokenize_statements(text)
    assert skipped == 2
    assert len(stmts) == 1


def test_tokenize_statements_flags_unterminated_trailing_content():
    text = "ex:a ex:b ex:c ."  # well-formed
    _, skipped = xref.tokenize_statements(text)
    assert skipped == 0
    text_bad = "ex:a ex:b ex:c"  # no closing dot
    _, skipped_bad = xref.tokenize_statements(text_bad)
    assert skipped_bad == 1


# --- resolve ----------------------------------------------------------------

def test_resolve_expands_known_curie():
    prefixes = {"ex": "http://example.org/ns#"}
    assert xref.resolve("ex:Widget", prefixes) == "http://example.org/ns#Widget"


def test_resolve_returns_none_for_unknown_prefix():
    assert xref.resolve("unknown:Widget", {}) is None


def test_resolve_returns_none_for_non_curie_token():
    assert xref.resolve('"a literal"', {"ex": "http://example.org/ns#"}) is None


# --- parse_ontology end-to-end ---------------------------------------------

def test_parse_ontology_extracts_statements_and_prefixes():
    text = """
    @prefix ex: <http://example.org/ns#> .
    ex:Alice a ex:Person ;
        ex:knows ex:Bob .
    """
    result = xref.parse_ontology(text)
    assert result.prefixes == {"ex": "http://example.org/ns#"}
    predicates = {stmt.predicate for stmt in result.statements}
    assert predicates == {"a", "ex:knows"}
    assert result.skipped == 0


# --- find_violations: the real defect this script exists to catch ---------

def test_find_violations_flags_unqualified_cross_pack_instance_reference(tmp_path):
    owner = make_pack(
        tmp_path,
        "owner-pack",
        """
        @prefix ex: <http://example.org/owner#> .
        ex:Widget42 a ex:Widget .
        """,
    )
    consumer = make_pack(
        tmp_path,
        "consumer-pack",
        """
        @prefix ex: <http://example.org/owner#> .
        @prefix c: <http://example.org/consumer#> .
        c:Job1 c:usesWidget ex:Widget42 .
        """,
    )
    violations, _ = xref.find_violations([owner, consumer])
    assert len(violations) == 1
    v = violations[0]
    assert v.pack == "consumer-pack"
    assert v.owner == "owner-pack"
    assert v.object_iri == "http://example.org/owner#Widget42"


def test_find_violations_allows_reference_backed_by_qualification_fixture(tmp_path):
    owner = make_pack(
        tmp_path,
        "owner-pack",
        """
        @prefix ex: <http://example.org/owner#> .
        ex:Widget42 a ex:Widget .
        """,
    )
    consumer = make_pack(
        tmp_path,
        "consumer-pack",
        """
        @prefix ex: <http://example.org/owner#> .
        @prefix c: <http://example.org/consumer#> .
        c:Job1 c:usesWidget ex:Widget42 .
        """,
        consumer_text="""
        @prefix ex: <http://example.org/owner#> .
        ex:Widget42 a ex:Widget .
        """,
    )
    violations, _ = xref.find_violations([owner, consumer])
    assert violations == []


def test_find_violations_ignores_vocabulary_class_or_property_reference(tmp_path):
    owner = make_pack(
        tmp_path,
        "owner-pack",
        """
        @prefix ex: <http://example.org/owner#> .
        ex:Widget a owl:Class .
        """,
    )
    consumer = make_pack(
        tmp_path,
        "consumer-pack",
        """
        @prefix ex: <http://example.org/owner#> .
        @prefix c: <http://example.org/consumer#> .
        c:Thing rdfs:subClassOf ex:Widget .
        """,
    )
    violations, _ = xref.find_violations([owner, consumer])
    assert violations == []


def test_find_violations_ignores_standard_vocabulary_namespace(tmp_path):
    consumer = make_pack(
        tmp_path,
        "consumer-pack",
        """
        @prefix c: <http://example.org/consumer#> .
        @prefix prov: <http://www.w3.org/ns/prov#> .
        c:Thing rdfs:subClassOf prov:Entity .
        """,
    )
    violations, _ = xref.find_violations([consumer])
    assert violations == []


def test_find_violations_ignores_namespace_typed_by_multiple_packs(tmp_path):
    a = make_pack(
        tmp_path,
        "pack-a",
        """
        @prefix shared: <http://example.org/shared#> .
        shared:Item1 a shared:Item .
        """,
    )
    b = make_pack(
        tmp_path,
        "pack-b",
        """
        @prefix shared: <http://example.org/shared#> .
        shared:Item2 a shared:Item .
        """,
    )
    c = make_pack(
        tmp_path,
        "pack-c",
        """
        @prefix shared: <http://example.org/shared#> .
        @prefix cc: <http://example.org/c#> .
        cc:Job cc:uses shared:Item1 .
        """,
    )
    violations, _ = xref.find_violations([a, b, c])
    assert violations == []
