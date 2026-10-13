"""AIRo de-orphaning projection court (finding L185 R2).

The vendored AIRo ontology packs/ggen-platform-pack/ontology/airo.ttl is
hash-pinned by witness.ttl (tests/test_airo_pin_w687.py) but was orphaned:
nothing consumed it. It is now projected by the pack's ggen.toml rule
`airo-surface` into generated/airo_surface.rs (46 named AIRo classes, each
with label + comment), with a fail-closed gate
(gates/02-airo-surface-nonempty.gates) refusing a gutted graph. Sabotage
twins prove the refusal and the row-count expectation are non-vacuous.

Chicago style: real `ggen sync run` subprocess in a tmp copy, real rdflib,
no mocks.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "ggen-platform-pack"
AIRO_NS = "https://w3id.org/airo#"
OWL_CLASS = "http://www.w3.org/2002/07/owl#Class"
RDFS_COMMENT = "http://www.w3.org/2000/01/rdf-schema#comment"

rdflib = pytest.importorskip("rdflib")

EXPECTED_CLASS_COUNT = 46

# Stable, long-lived AIRo classes that must appear in the projected surface.
EXPECTED_CLASSES = (
    "AISystem",
    "Risk",
    "RiskConcept",
    "RiskControl",
    "RiskSource",
    "Hazard",
    "Consequence",
    "Impact",
)


def _ggen_binary() -> str:
    return os.environ.get("GGEN_BIN") or shutil.which("ggen") or "ggen"


def _copy_pack(dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    pack_copy = dest / "ggen-platform-pack"
    shutil.copytree(PACK, pack_copy)
    return pack_copy


def _sync(pack_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_ggen_binary(), "sync", "run"],
        cwd=pack_dir, capture_output=True, text=True, timeout=300,
    )


def _airo_class_facts() -> set:
    """rdflib-derived ground truth: (local, label, comment) per AIRo class."""
    g = rdflib.Graph()
    g.parse(PACK / "ontology" / "airo.ttl", format="turtle")
    out = set()
    for c in set(g.subjects(rdflib.RDF.type, rdflib.URIRef(OWL_CLASS))):
        if not (isinstance(c, rdflib.URIRef) and str(c).startswith(AIRO_NS)):
            continue
        label = str(next(g.objects(c, rdflib.RDFS.label), ""))
        comment = str(next(g.objects(c, rdflib.URIRef(RDFS_COMMENT)), ""))
        out.add((str(c).split("#")[-1], label, comment))
    return out


# ---------------------------------------------------------------------------
# Court 1: sync succeeds twice, byte-identical, and matches the working tree
# ---------------------------------------------------------------------------

def test_sync_twice_byte_identical_and_matches_working_tree():
    with tempfile.TemporaryDirectory() as td:
        copy = _copy_pack(Path(td) / "a")
        assert _sync(copy).returncode == 0
        gen1 = (copy / "generated" / "airo_surface.rs").read_bytes()
        assert _sync(copy).returncode == 0
        gen2 = (copy / "generated" / "airo_surface.rs").read_bytes()
        assert gen1 == gen2, "two fresh syncs must be byte-identical"
    committed = (PACK / "generated" / "airo_surface.rs").read_bytes()
    assert gen1 == committed, "fresh render must match working-tree copy"


# ---------------------------------------------------------------------------
# Court 2: content derived from the ontology (rdflib ground truth)
# ---------------------------------------------------------------------------

def test_generated_surface_matches_ontology_ground_truth():
    text = (PACK / "generated" / "airo_surface.rs").read_text()
    facts = _airo_class_facts()
    assert len(facts) == EXPECTED_CLASS_COUNT, len(facts)
    assert "AIRO_CLASS_COUNT: usize = 46" in text
    assert "// REFUSED" not in text, "real graph must not render REFUSED marker"
    for local, label, comment in sorted(facts):
        assert '"%s",' % local in text, local
        assert '"%s",' % label in text, label


def test_expected_stable_classes_present():
    text = (PACK / "generated" / "airo_surface.rs").read_text()
    for cls in EXPECTED_CLASSES:
        assert '"%s",' % cls in text, cls


# ---------------------------------------------------------------------------
# Court 3: fail-closed sabotage twins
# ---------------------------------------------------------------------------

def test_sabotage_gutted_graph_refuses(tmp_path):
    """A gutted AIRo graph must refuse: gate 02 returns a row, sync exits 1."""
    copy = _copy_pack(tmp_path / "sabotage")
    g = rdflib.Graph()
    g.parse(copy / "ontology" / "airo.ttl", format="turtle")
    for c in set(g.subjects(rdflib.RDF.type, rdflib.URIRef(OWL_CLASS))):
        if isinstance(c, rdflib.URIRef) and str(c).startswith(AIRO_NS):
            g.remove((c, rdflib.RDFS.label, None))
            g.remove((c, rdflib.URIRef(RDFS_COMMENT), None))
    g.serialize(destination=str(copy / "ontology" / "airo.ttl"), format="turtle")
    r = _sync(copy)
    assert r.returncode != 0, r.stdout + r.stderr
    assert "airo-graph-empty-refused" in (r.stdout + r.stderr), r.stdout[-400:]


def test_sabotage_row_count_mutation_is_caught(tmp_path):
    """Mutating the query row count expectation (drop one class's label so it
    leaves the surface) must change the rendered count — proving the count
    court is non-vacuous."""
    copy = _copy_pack(tmp_path / "countmut")
    g = rdflib.Graph()
    g.parse(copy / "ontology" / "airo.ttl", format="turtle")
    target = min(
        (c for c in set(g.subjects(rdflib.RDF.type, rdflib.URIRef(OWL_CLASS)))
         if isinstance(c, rdflib.URIRef) and str(c).startswith(AIRO_NS)),
        key=str,
    )
    g.remove((target, rdflib.RDFS.label, None))
    g.serialize(destination=str(copy / "ontology" / "airo.ttl"), format="turtle")
    r = _sync(copy)
    assert r.returncode == 0, r.stdout + r.stderr
    text = (copy / "generated" / "airo_surface.rs").read_text()
    assert "AIRO_CLASS_COUNT: usize = 45" in text, "sabotage render must show 45"
    assert "AIRO_CLASS_COUNT: usize = 46" not in text
