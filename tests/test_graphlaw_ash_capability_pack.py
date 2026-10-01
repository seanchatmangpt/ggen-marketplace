"""Gate courts for packs/graphlaw-ash-capability-pack.

Every gate in the pack's gates/ directory is a violation-row SELECT. Each gate is run with rdflib
against its exact-stem witnesses: the pass witness must yield zero rows, the fail witness at
least one row, and the fail witness must trip exactly its own gate and no other (a fail witness
that breaks several gates proves nothing about any one of them). No gate may hardcode the op
count; the expected count is read from gac:opCount in the graph.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tomllib
from functools import lru_cache
from pathlib import Path

import pytest
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "graphlaw-ash-capability-pack"
GATES = PACK / "gates"
PASS = PACK / "witnesses" / "pass"
FAIL = PACK / "witnesses" / "fail"
PACK_VERSION = "26.9.30"

EXPECTED_STEMS = [
    "010_registry_identity",
    "020_op_count_contract",
    "030_op_order_contract",
    "040_field_type_vocabulary",
    "050_response_variant_contract",
    "060_field_order_contract",
    "070_opbinding_reference_contract",
    "080_dialect_kind_contract",
    "090_law_step_ceiling_contract",
    "100_elixir_name_contract",
    "110_model_identity_contract",
    "120_model_field_contract",
    "130_model_reference_closure_contract",
    "140_model_enum_contract",
    "150_lease_receipt_required_fields_contract",
    "160_limit_scope_contract",
    "170_limit_completeness_contract",
    "180_coverage_complete",
]


def gate_stems() -> list[str]:
    return sorted(p.stem for p in GATES.glob("*.rq"))


@lru_cache(maxsize=None)
def gate_text(stem: str) -> str:
    return (GATES / f"{stem}.rq").read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def load(path: Path) -> Graph:
    graph = Graph()
    graph.parse(path, format="turtle")
    return graph


def rows(stem: str, witness: Path) -> list:
    return list(load(witness).query(gate_text(stem)))


def test_gate_inventory_is_exactly_the_contract() -> None:
    assert gate_stems() == EXPECTED_STEMS


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_gate_shape(stem: str) -> None:
    text = gate_text(stem)
    assert text.startswith("# MESSAGE:"), "gate must open with a # MESSAGE: header"
    assert re.search(r"^ORDER BY\b", text, re.M), "every SELECT needs ORDER BY"
    assert not re.search(r"\b14\b", text), "no gate may hardcode the op count"
    assert not re.search(r"https?://(?!seanchatmangpt\.github\.io/packs/|www\.w3\.org/)", text), (
        "gates make no network references"
    )


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_pass_witness_yields_zero_rows(stem: str) -> None:
    found = rows(stem, PASS / f"{stem}.ttl")
    assert found == [], f"{stem}: pass witness produced {len(found)} rows: {found[:3]}"


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_fail_witness_yields_rows(stem: str) -> None:
    found = rows(stem, FAIL / f"{stem}.ttl")
    assert len(found) >= 1, f"{stem}: fail witness produced no rows (vacuous gate)"


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_fail_witness_trips_only_its_own_gate(stem: str) -> None:
    witness = FAIL / f"{stem}.ttl"
    fired = sorted(other for other in EXPECTED_STEMS if rows(other, witness))
    assert fired == [stem], f"{stem}: fail witness tripped {fired}"


@pytest.mark.parametrize("stem", EXPECTED_STEMS)
def test_every_pass_witness_satisfies_every_gate(stem: str) -> None:
    witness = PASS / f"{stem}.ttl"
    fired = sorted(other for other in EXPECTED_STEMS if rows(other, witness))
    assert fired == [], f"{stem}: pass witness tripped {fired}"


def test_gate_witness_court_exact_stem_pairing() -> None:
    gates = set(gate_stems())
    assert gates == {p.stem for p in PASS.glob("*.ttl")}
    assert gates == {p.stem for p in FAIL.glob("*.ttl")}
    court = PACK / "gate-court.toml"
    if court.exists():
        spec = importlib.util.spec_from_file_location(
            "check_gate_witness_courts", ROOT / "scripts" / "check_gate_witness_courts.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        record = module.qualify(PACK)
        assert record["case_count"] == len(gates)
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_gate_witness_courts.py"), "--packs", str(ROOT / "packs")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_pack_manifest_conventions() -> None:
    manifest = tomllib.loads((PACK / "pack.toml").read_text(encoding="utf-8"))
    assert set(manifest) == {"pack"}
    assert manifest["pack"]["name"] == "graphlaw-ash-capability-pack"
    assert manifest["pack"]["version"] == PACK_VERSION
    assert manifest["pack"]["description"].strip()


def test_pack_ontology_carries_no_sample_individuals() -> None:
    ontology = PACK / "ontology.ttl"
    assert ontology.exists(), "pack ontology.ttl missing"
    graph = load(ontology)
    individuals = list(
        graph.query(
            """
            PREFIX gac: <http://seanchatmangpt.github.io/packs/graphlaw-ash-capability#>
            SELECT ?s WHERE { ?s a ?c . FILTER(STRSTARTS(STR(?s), "https://graphlaw.dev/registry#")) }
            ORDER BY ?s
            """
        )
    )
    assert individuals == []


def test_pack_version_is_26_9_30_everywhere() -> None:
    manifest = tomllib.loads((PACK / "pack.toml").read_text(encoding="utf-8"))
    assert manifest["pack"]["version"] == PACK_VERSION == "26.9.30"
    assert "26.9.30" in (PACK / "README.md").read_text(encoding="utf-8")


TYPED_MODELS = [
    "Lease",
    "SignedLease",
    "Receipt",
    "Attestation",
    "Plan",
    "Action",
    "PolicyEntry",
    "PolicyOutcome",
]

NEW_QUERIES = ["models", "model_fields", "model_enums"]
NEW_TEMPLATES = ["capability_model.ex.tmpl", "capability_enums.ex.tmpl", "capability_limits.ex.tmpl"]


def test_new_queries_and_templates_exist_with_order_by() -> None:
    for name in NEW_QUERIES:
        text = (PACK / "queries" / f"{name}.rq").read_text(encoding="utf-8")
        assert re.search(r"^ORDER BY\b", text, re.M), f"{name}.rq needs ORDER BY"
    for name in NEW_TEMPLATES:
        assert (PACK / "templates" / name).is_file(), name


def inline_queries(template: str) -> dict[str, str]:
    front = template.split("\n---\n", 1)[0]
    found: dict[str, list[str]] = {}
    current: str | None = None
    for line in front.splitlines():
        header = re.match(r"^  (\w+): \|$", line)
        if header:
            current = header.group(1)
            found[current] = []
        elif current is not None and (line.startswith("    ") or line == ""):
            found[current].append(line[4:] if line.startswith("    ") else "")
    return {name: "\n".join(body).rstrip("\n") for name, body in found.items()}


def test_every_inline_template_query_is_the_pack_query_file() -> None:
    """Sync: a template's inline query is byte-identical to queries/<name>.rq."""
    checked = 0
    for template in sorted((PACK / "templates").glob("*.tmpl")):
        for name, body in inline_queries(template.read_text(encoding="utf-8")).items():
            expected = (PACK / "queries" / f"{name}.rq").read_text(encoding="utf-8").rstrip("\n")
            assert body == expected, f"{template.name}: inline {name} differs from queries/{name}.rq"
            checked += 1
    assert checked > 0


def test_limits_query_is_identical_in_every_template_that_inlines_it() -> None:
    users = [
        t.name
        for t in sorted((PACK / "templates").glob("*.tmpl"))
        if "limits" in inline_queries(t.read_text(encoding="utf-8"))
    ]
    assert {"capability_index.md.tmpl", "capability_registry.ex.tmpl", "capability_limits.ex.tmpl"} <= set(users)


def render_models() -> list:
    graph = load(PASS / "110_model_identity_contract.ttl")
    return list((graph.query((PACK / "queries" / "models.rq").read_text(encoding="utf-8"))))


def test_model_query_is_deterministic_and_ordered() -> None:
    first = [tuple(map(str, row)) for row in render_models()]
    second = [tuple(map(str, row)) for row in render_models()]
    assert first == second
    assert [row[0] for row in first] == TYPED_MODELS
    assert [row[2] for row in first] == [
        "lease",
        "signed_lease",
        "receipt",
        "attestation",
        "plan",
        "action",
        "policy_entry",
        "policy_outcome",
    ]


def test_model_fields_and_enums_queries_cover_the_pass_witness() -> None:
    graph = load(PASS / "110_model_identity_contract.ttl")
    fields = list(graph.query((PACK / "queries" / "model_fields.rq").read_text(encoding="utf-8")))
    assert {str(r[0]) for r in fields} == set(TYPED_MODELS)
    enums = list(graph.query((PACK / "queries" / "model_enums.rq").read_text(encoding="utf-8")))
    assert [str(r[0]) for r in enums][:3] == ["Ceiling", "Ceiling", "Ceiling"]
    assert {str(r[0]) for r in enums} == {"Ceiling", "LeaseReason", "ReceiptReason", "PolicyRefusalKind"}


def test_limits_query_returns_scope_unit_and_source_for_every_limit() -> None:
    graph = load(PASS / "170_limit_completeness_contract.ttl")
    rows = list(graph.query((PACK / "queries" / "limits.rq").read_text(encoding="utf-8")))
    assert len(rows) == 15
    assert all(str(r[2]) and str(r[3]) and str(r[4]) for r in rows)
    assert {str(r[2]) for r in rows} == {"abi", "hooks", "n3", "plan", "wasm"}


def test_legacy_bare_limit_still_yields_empty_metadata() -> None:
    graph = Graph()
    graph.parse(
        data="""
        @prefix gac: <http://seanchatmangpt.github.io/packs/graphlaw-ash-capability#> .
        <urn:l:bare> a gac:Limit ; gac:limitName "max_x" ; gac:limitValue 1 .
        """,
        format="turtle",
    )
    [row] = list(graph.query((PACK / "queries" / "limits.rq").read_text(encoding="utf-8")))
    assert [str(v) for v in row] == ["max_x", "1", "", "", ""]


def test_ontology_declares_the_typed_model_vocabulary() -> None:
    graph = load(PACK / "ontology.ttl")
    declared = {str(s).rsplit("#", 1)[1] for s in graph.subjects()}
    for term in [
        "Model", "ModelField", "ModelEnum", "ModelEnumValue", "modelName", "modelOrder",
        "modelElixirModule", "modelRustPath", "modelDoc", "modelFieldOf", "modelFieldName",
        "modelFieldOrder", "modelFieldType", "modelFieldRequired", "modelFieldNullable",
        "modelFieldDoc", "enumOf", "enumValue", "enumOrder", "limitScope", "limitUnit",
        "limitSource", "limitCount",
    ]:
        assert term in declared, term
    assert "fieldOwner" in declared


def test_gate_150_is_inert_without_models_and_170_without_limit_count() -> None:
    legacy = load(PASS / "010_registry_identity.ttl")
    for stem in ("150_lease_receipt_required_fields_contract", "170_limit_completeness_contract"):
        assert list(legacy.query(gate_text(stem))) == []


def test_gate_160_ignores_bare_limits_but_refuses_partial_metadata() -> None:
    graph = Graph()
    graph.parse(
        data="""
        @prefix gac: <http://seanchatmangpt.github.io/packs/graphlaw-ash-capability#> .
        <urn:l:bare> a gac:Limit ; gac:limitName "max_x" ; gac:limitValue 1 .
        """,
        format="turtle",
    )
    assert list(graph.query(gate_text("160_limit_scope_contract"))) == []
    graph.parse(
        data="""
        @prefix gac: <http://seanchatmangpt.github.io/packs/graphlaw-ash-capability#> .
        <urn:l:half> a gac:Limit ; gac:limitName "max_y" ; gac:limitValue 2 ; gac:limitScope "n3" .
        """,
        format="turtle",
    )
    assert list(graph.query(gate_text("160_limit_scope_contract"))) != []


def test_docs_reference_lists_every_gate_stem() -> None:
    doc = (ROOT / "docs" / "reference" / "graphlaw-ash-capability-pack.md").read_text(encoding="utf-8")
    for stem in EXPECTED_STEMS:
        assert f"`{stem}`" in doc, stem
    for kind in ("signature verification", "lease authorize", "plan admit", "policy validation", "hook execution"):
        assert kind in doc
