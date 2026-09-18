"""RFC-GPACK-001 valid-corpus falsifiers (Appendix D ``valid/*``, ticket T02).

Every normative claim the positive corpus implements carries a falsifier in
this file (RFC §96). The guards are pure functions returning violation
lists; each has a sabotage twin (§79: "deleting or disabling the guard
SHOULD cause the falsifier to survive") proving the guard can actually
fire -- a guard that cannot fail is vacuous.

Real execution throughout: TOML via stdlib ``tomllib``, Turtle + SPARQL via
``rdflib`` (pinned ``rdflib==7.1.4`` in CI workflows that need an RDF
stack, e.g. compose-r86-forced-top25-qualification-capsule.yml). Rows below
are observed query results, never asserted shapes.

Out of scope here (wave 2 / Appendix E crown): running the Rust ``ggen``
or ``ggen_igniter`` engines against these fixtures. The single-variable
Tera substitution witness below is a binding-level consequence check, not
an engine render.
"""

from __future__ import annotations

import json
import re
import shutil
import tomllib
from pathlib import Path

import pytest
import rdflib
from rdflib.plugins.parsers.notation3 import BadSyntax

ROOT = Path(__file__).resolve().parents[1]
SPEC_PACK = ROOT / "packs" / "ggen-pack-spec-pack"
POSITIVE = SPEC_PACK / "qualification" / "positive"

GP = rdflib.Namespace("https://ggen.dev/ns/pack#")

FIXTURES = (
    "minimal-portable-pack",
    "two-semantic-dependencies",
    "portable-tera-fanout",
    "consumer-alias",
)

SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)

# ---------------------------------------------------------------------------
# RFC-GPACK-001 §91 "Minimal Portable Example" — canonical bytes, verbatim
# from the RFC's fenced blocks (each block's trailing newline included).
# The minimal-portable-pack fixture must be byte-faithful to these.
# ---------------------------------------------------------------------------

RFC91_TOML = "\n".join(
    [
        "[pack]",
        'name = "hello-pack"',
        'version = "1.0.0"',
        'description = "Portable hello-world semantic projection."',
    ]
) + "\n"

RFC91_TTL = "\n".join(
    [
        "@prefix gp: <https://ggen.dev/ns/pack#> .",
        "@prefix ex: <https://example.org/hello#> .",
        "",
        "<urn:ggen:pack:hello-pack>",
        "    a gp:Pack ;",
        '    gp:name "hello-pack" ;',
        '    gp:version "1.0.0" ;',
        "    gp:profile gp:Portable1 ;",
        "    gp:renderer gp:Tera1 ;",
        "    gp:authorityCeiling gp:Construct .",
        "",
        "ex:Hello",
        '    ex:message "Hello from admitted RDF." .',
    ]
) + "\n"

RFC91_MESSAGE_RQ = "\n".join(
    [
        "PREFIX ex: <https://example.org/hello#>",
        "",
        "SELECT ?message",
        "WHERE {",
        "  ex:Hello ex:message ?message .",
        "}",
    ]
) + "\n"

RFC91_GATE_RQ = "\n".join(
    [
        "PREFIX ex: <https://example.org/hello#>",
        "",
        "SELECT ?subject",
        "WHERE {",
        "  BIND(ex:Hello AS ?subject)",
        "  FILTER NOT EXISTS {",
        "    ex:Hello ex:message ?message .",
        "  }",
        "}",
    ]
) + "\n"

RFC91_TEMPLATE = "{{ message }}\n"

RFC91_EXPECTED = "Hello from admitted RDF.\n"

RFC91_FILES: dict[str, str] = {
    "pack.toml": RFC91_TOML,
    "ontology.ttl": RFC91_TTL,
    "queries/message.rq": RFC91_MESSAGE_RQ,
    "gates/010_required.rq": RFC91_GATE_RQ,
    "templates/hello.txt.tera": RFC91_TEMPLATE,
    "expected/hello.txt": RFC91_EXPECTED,
}


# ---------------------------------------------------------------------------
# Guards (pure functions -> violation lists; empty list = guard passes)
# ---------------------------------------------------------------------------


def strict_manifest_violations(text: str) -> list[str]:
    """RFC §7.1: [pack] admits ONLY name (non-empty), version (SemVer),
    description (non-empty); the manifest has no other top-level tables."""
    bad: list[str] = []
    try:
        doc = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return [f"TOML_UNPARSEABLE:{exc}"]
    extra_tables = sorted(set(doc) - {"pack"})
    if extra_tables:
        bad.append(f"MANIFEST_EXTRA_TABLE:{','.join(extra_tables)}")
    table = doc.get("pack")
    if not isinstance(table, dict):
        return bad + ["MANIFEST_PACK_TABLE_MISSING"]
    extra_keys = sorted(set(table) - {"name", "version", "description"})
    if extra_keys:
        bad.append(f"MANIFEST_UNKNOWN_KEY:{','.join(extra_keys)}")
    for key in ("name", "version", "description"):
        if key not in table:
            bad.append(f"MANIFEST_MISSING_KEY:{key}")
        elif not (isinstance(table[key], str) and table[key].strip()):
            bad.append(f"MANIFEST_EMPTY_KEY:{key}")
    if "version" in table and not SEMVER_RE.match(str(table["version"])):
        bad.append(f"MANIFEST_VERSION_NOT_SEMVER:{table['version']!r}")
    return bad


def rfc91_drift(fixture_dir: Path) -> dict[str, str]:
    """RFC §91 byte-faithfulness: each canonical file matches the RFC's
    bytes exactly. Returns per-file drift reports; empty dict = faithful."""
    drift: dict[str, str] = {}
    for rel, canonical in RFC91_FILES.items():
        path = fixture_dir / rel
        if not path.is_file():
            drift[rel] = "FILE_MISSING"
            continue
        actual = path.read_bytes().decode("utf-8")
        if actual != canonical:
            drift[rel] = f"BYTES_DIFFER (expected {len(canonical)}, got {len(actual)})"
    extra = sorted(
        str(p.relative_to(fixture_dir))
        for p in fixture_dir.rglob("*")
        if p.is_file() and str(p.relative_to(fixture_dir)) not in RFC91_FILES
    )
    if extra:
        drift["<extra-files>"] = ",".join(extra)
    return drift


def self_description_violations(graph: rdflib.Graph, manifest_text: str) -> list[str]:
    """RFC §8 + §10: the graph self-describes the pack with
    gp:profile gp:Portable1 and gp:authorityCeiling gp:Construct, and the
    graph's gp:name equals the manifest [pack].name (identity
    correspondence Project(I_S) == I_B)."""
    bad: list[str] = []
    name = str(tomllib.loads(manifest_text)["pack"]["name"])
    subjects = list(graph.subjects(GP.name, rdflib.Literal(name)))
    if not subjects:
        return [f"GRAPH_NAME_MISSING:{name}"]
    for subject in subjects:
        profiles = list(graph.objects(subject, GP.profile))
        if rdflib.URIRef(str(GP.Portable1)) not in profiles:
            bad.append(f"PROFILE_NOT_PORTABLE1:{subject}:{profiles}")
        ceilings = list(graph.objects(subject, GP.authorityCeiling))
        if rdflib.URIRef(str(GP.Construct)) not in ceilings:
            bad.append(f"CEILING_NOT_CONSTRUCT:{subject}:{ceilings}")
    return bad


def dependency_scope_violations(graph: rdflib.Graph, fixture_dir: Path) -> list[str]:
    """RFC §26/§27/§73: exactly two gp:PackRequirement individuals; each has
    exactly one gp:requiresPack and exactly one gp:dependencyScope whose
    value is exactly "SEMANTICS" (§55 token form); no LAW/PROJECTION scopes
    anywhere; each dependee resolves to an inline deps/<name> dir that is
    semantic-only (no templates/)."""
    bad: list[str] = []
    requirements = sorted(graph.subjects(rdflib.RDF.type, GP.PackRequirement), key=str)
    if len(requirements) != 2:
        bad.append(f"REQUIREMENT_COUNT:{len(requirements)}")
    seen_deps: list[str] = []
    for req in requirements:
        deps = [str(o) for o in graph.objects(req, GP.requiresPack)]
        if len(deps) != 1:
            bad.append(f"REQUIREMENT_DEP_CARDINALITY:{req}:{deps}")
            continue
        seen_deps.append(deps[0])
        scopes = [str(o) for o in graph.objects(req, GP.dependencyScope)]
        if scopes != ["SEMANTICS"]:
            bad.append(f"SCOPE_NOT_EXACTLY_SEMANTICS:{req}:{scopes}")
    for dep_iri in sorted(set(seen_deps)):
        dep_name = dep_iri.rsplit(":", 1)[-1]
        dep_dir = fixture_dir / "deps" / dep_name
        if not (dep_dir / "pack.toml").is_file():
            bad.append(f"DEP_DIR_MISSING:{dep_name}")
            continue
        if (dep_dir / "templates").exists():
            bad.append(f"DEP_NOT_SEMANTIC_ONLY:{dep_name}")
    for token in ("LAW", "PROJECTION"):
        hits = [
            str(s)
            for s, o in graph.subject_objects(GP.dependencyScope)
            if str(o) == token
        ]
        if hits:
            bad.append(f"FORBIDDEN_SCOPE_TOKEN:{token}:{hits}")
    return bad


def fanout_order_violations(
    query_text: str, graph: rdflib.Graph, expected_targets: list[str]
) -> list[str]:
    """RFC §25 + §22: the projection query establishes order via ORDER BY;
    executing it yields the pinned deterministic target set, derived by
    substituting each binding row into the template's frontmatter `to:`
    pattern."""
    bad: list[str] = []
    if not re.search(r"\bORDER\s+BY\b", query_text):
        bad.append("ORDER_BY_MISSING")
    rows = [
        (str(row.name), int(row.rank)) for row in graph.query(query_text)
    ]
    if not rows:
        return bad + ["FANOUT_NO_ROWS"]
    derived = [f"generated/{rank}-{name}.txt" for name, rank in rows]
    if derived != expected_targets:
        bad.append(f"TARGET_ORDER_MISMATCH:{derived}!={expected_targets}")
    return bad


def alias_violations(fixture_dir: Path) -> list[str]:
    """RFC §9: the consumer config assigns alias "payments" to the canonical
    acme-payments-pack; the receipt fields preserve BOTH identities, and the
    alias does not overwrite the canonical name."""
    bad: list[str] = []
    manifest = tomllib.loads((fixture_dir / "pack.toml").read_text(encoding="utf-8"))
    canonical = str(manifest["pack"]["name"])
    consumer = tomllib.loads(
        (fixture_dir / "consumer.toml").read_text(encoding="utf-8")
    )
    packs = consumer.get("packs")
    if not isinstance(packs, dict) or "payments" not in packs:
        return bad + [f"ALIAS_MISSING:payments:{sorted(packs or {})}"]
    path = str(packs["payments"].get("path", ""))
    if not path.endswith(canonical):
        bad.append(f"ALIAS_PATH_NOT_CANONICAL:{path}!~{canonical}")
    receipt = json.loads(
        (fixture_dir / "expected" / "receipt.json").read_text(encoding="utf-8")
    )
    if receipt.get("consumer_alias") != "payments":
        bad.append(f"RECEIPT_ALIAS_NOT_PRESERVED:{receipt.get('consumer_alias')!r}")
    if receipt.get("canonical_name") != canonical:
        bad.append(f"RECEIPT_CANONICAL_NOT_PRESERVED:{receipt.get('canonical_name')!r}")
    if receipt.get("consumer_alias") == receipt.get("canonical_name"):
        bad.append("RECEIPT_ALIAS_OVERWRITES_CANONICAL")
    return bad


def load_graph(path: Path) -> rdflib.Graph:
    graph = rdflib.Graph()
    graph.parse(path, format="turtle")
    return graph


# ---------------------------------------------------------------------------
# The real corpus passes every guard (positive witnesses, real execution)
# ---------------------------------------------------------------------------


class TestValidCorpusPasses:
    def test_every_fixture_manifest_is_strict_71(self) -> None:
        for fixture in FIXTURES:
            text = (POSITIVE / fixture / "pack.toml").read_text(encoding="utf-8")
            assert strict_manifest_violations(text) == [], fixture

    def test_every_corpus_turtle_parses_for_real(self) -> None:
        ttl_files = sorted(POSITIVE.rglob("*.ttl"))
        assert len(ttl_files) == 6  # 4 fixtures, two-semantic has 2 dependees
        for path in ttl_files:
            graph = load_graph(path)
            assert len(graph) > 0, path

    def test_every_fixture_self_describes_portable1_construct(self) -> None:
        for fixture in FIXTURES:
            graph = load_graph(POSITIVE / fixture / "ontology.ttl")
            manifest = (POSITIVE / fixture / "pack.toml").read_text(encoding="utf-8")
            assert self_description_violations(graph, manifest) == [], fixture

    def test_minimal_portable_pack_is_byte_faithful_to_rfc_91(self) -> None:
        drift = rfc91_drift(POSITIVE / "minimal-portable-pack")
        assert drift == {}, drift

    def test_minimal_query_and_gate_execute_with_expected_consequence(self) -> None:
        fixture = POSITIVE / "minimal-portable-pack"
        graph = load_graph(fixture / "ontology.ttl")
        rows = list(graph.query((fixture / "queries/message.rq").read_text(encoding="utf-8")))
        assert [str(r.message) for r in rows] == ["Hello from admitted RDF."]
        # §14: SELECT gate violation == RowCount > 0; the corpus gate passes.
        gate_rows = list(graph.query((fixture / "gates/010_required.rq").read_text(encoding="utf-8")))
        assert len(gate_rows) == 0
        # Binding-level consequence: `{{ message }}` over the observed
        # binding reproduces the §91 expected bytes exactly.
        rendered = RFC91_TEMPLATE.replace("{{ message }}", str(rows[0].message))
        assert rendered == (fixture / "expected/hello.txt").read_bytes().decode("utf-8")

    def test_two_semantic_dependencies_declare_exactly_semantics(self) -> None:
        fixture = POSITIVE / "two-semantic-dependencies"
        graph = load_graph(fixture / "ontology.ttl")
        assert dependency_scope_violations(graph, fixture) == []

    def test_portable_tera_fanout_has_order_by_and_pinned_targets(self) -> None:
        fixture = POSITIVE / "portable-tera-fanout"
        query = (fixture / "queries/modules.rq").read_text(encoding="utf-8")
        graph = load_graph(fixture / "ontology.ttl")
        expected = (fixture / "expected/targets.txt").read_text(encoding="utf-8").splitlines()
        assert fanout_order_violations(query, graph, expected) == []
        template = (fixture / "templates/module.txt.tera").read_text(encoding="utf-8")
        assert "for_each: modules" in template
        assert "renderer: tera1" in template

    def test_consumer_alias_preserves_both_identities(self) -> None:
        assert alias_violations(POSITIVE / "consumer-alias") == []


# ---------------------------------------------------------------------------
# Sabotage twins (§79): each guard must FIRE under a targeted mutation.
# A guard whose twin observes no violation is vacuous and fails here.
# ---------------------------------------------------------------------------


class TestGuardsCanFire:
    def test_strict_manifest_guard_fires_on_unknown_key(self) -> None:
        poisoned = RFC91_TOML.replace(
            'description = "Portable hello-world semantic projection."\n',
            'description = "Portable hello-world semantic projection."\n'
            'author = "saboteur"\n',
        )
        violations = strict_manifest_violations(poisoned)
        assert any(v.startswith("MANIFEST_UNKNOWN_KEY") for v in violations), violations

    def test_rfc91_byte_guard_fires_on_single_byte_drift(self, tmp_path: Path) -> None:
        fixture = tmp_path / "minimal-portable-pack"
        shutil.copytree(POSITIVE / "minimal-portable-pack", fixture)
        ontology = fixture / "ontology.ttl"
        ontology.write_bytes(
            ontology.read_bytes().replace(b"1.0.0", b"1.0.1", 1)
        )
        drift = rfc91_drift(fixture)
        assert drift.get("ontology.ttl", "").startswith("BYTES_DIFFER"), drift

    def test_turtle_parse_guard_fires_on_broken_turtle(self) -> None:
        broken = RFC91_TTL.replace("gp:authorityCeiling gp:Construct .", "gp:authorityCeiling")
        with pytest.raises(BadSyntax):
            rdflib.Graph().parse(data=broken, format="turtle")

    def test_self_description_guard_fires_when_ceiling_dropped(self) -> None:
        stripped = RFC91_TTL.replace(
            "    gp:authorityCeiling gp:Construct .", "    ."
        )
        graph = rdflib.Graph()
        graph.parse(data=stripped, format="turtle")
        violations = self_description_violations(graph, RFC91_TOML)
        assert any(v.startswith("CEILING_NOT_CONSTRUCT") for v in violations), violations

    def test_dependency_scope_guard_fires_on_projection_scope(self) -> None:
        fixture = POSITIVE / "two-semantic-dependencies"
        graph = load_graph(fixture / "ontology.ttl")
        extra = """
@prefix gp: <https://ggen.dev/ns/pack#> .

<urn:ggen:pack:two-semantic-dependencies#requirement-gamma>
    a gp:PackRequirement ;
    gp:requiresPack <urn:ggen:pack:alpha-semantics-pack> ;
    gp:dependencyScope "PROJECTION" .
"""
        graph.parse(data=extra, format="turtle")
        violations = dependency_scope_violations(graph, fixture)
        assert any(v.startswith("SCOPE_NOT_EXACTLY_SEMANTICS") for v in violations), violations
        assert any(v.startswith("FORBIDDEN_SCOPE_TOKEN:PROJECTION") for v in violations), violations
        assert any(v.startswith("REQUIREMENT_COUNT") for v in violations), violations

    def test_fanout_order_guard_fires_without_order_by(self) -> None:
        fixture = POSITIVE / "portable-tera-fanout"
        query = (fixture / "queries/modules.rq").read_text(encoding="utf-8")
        graph = load_graph(fixture / "ontology.ttl")
        expected = (fixture / "expected/targets.txt").read_text(encoding="utf-8").splitlines()
        stripped = query.replace("ORDER BY ?rank\n", "")
        violations = fanout_order_violations(stripped, graph, expected)
        assert "ORDER_BY_MISSING" in violations, violations

    def test_minimal_gate_can_fire_when_data_violated(self) -> None:
        """§79 negative witness for the corpus's own gate: drop the
        ex:message triple and the SELECT gate must return a violation row
        (§14: violation == RowCount > 0)."""
        fixture = POSITIVE / "minimal-portable-pack"
        graph = load_graph(fixture / "ontology.ttl")
        graph.remove((None, rdflib.URIRef("https://example.org/hello#message"), None))
        gate_rows = list(graph.query((fixture / "gates/010_required.rq").read_text(encoding="utf-8")))
        assert len(gate_rows) == 1, gate_rows

    def test_alias_guard_fires_when_alias_overwrites_canonical(self, tmp_path: Path) -> None:
        fixture = tmp_path / "consumer-alias"
        shutil.copytree(POSITIVE / "consumer-alias", fixture)
        receipt_path = fixture / "expected" / "receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        del receipt["consumer_alias"]
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        violations = alias_violations(fixture)
        assert any(v.startswith("RECEIPT_ALIAS_NOT_PRESERVED") for v in violations), violations
