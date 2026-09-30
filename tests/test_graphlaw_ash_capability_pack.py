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
    assert manifest["pack"]["version"] == "26.9.29"
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
