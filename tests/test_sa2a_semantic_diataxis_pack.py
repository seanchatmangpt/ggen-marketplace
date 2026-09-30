"""Chicago court for sa2a-semantic-diataxis-pack.

Real collaborators: the pack's real ontology.ttl through rdflib and its real
SPARQL gates. A gate returning rows is a violation. The admitted graph must
yield zero rows everywhere; each adversarial mutation must trip its named gate.
The real-sync case runs only when a ggen binary is on PATH (never mocked).
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "sa2a-semantic-diataxis-pack"
SD = Namespace("https://ggen.dev/ontology/sa2a-semantic-diataxis#")
GATES = {g.stem: g.read_text() for g in sorted((PACK / "gates").glob("*.rq"))}
HEX = "0" * 39 + "1"


def graph() -> Graph:
    g = Graph()
    g.parse(PACK / "ontology.ttl", format="turtle")
    return g


def rows(g: Graph, stem: str) -> int:
    return len(list(g.query(GATES[stem])))


def test_nine_gates_admit_the_source():
    assert len(GATES) == 9
    g = graph()
    assert {s: rows(g, s) for s in GATES} == {s: 0 for s in GATES}


def test_semantic_equivalence_unclaimed_and_authority_none():
    g = graph()
    c = SD.DefaultContract
    assert str(g.value(c, SD.semanticEquivalence)) == "UNCLAIMED"
    assert str(g.value(c, SD.authority)) == "NONE"


def test_pack_toml_and_ggen_toml_admit():
    import tomllib
    tomllib.loads((PACK / "pack.toml").read_text())
    cfg = tomllib.loads((PACK / "ggen.toml").read_text())
    assert len(cfg["generation"]["rules"]) == 7
    for gate in cfg["validation"]["gates"]:
        assert (PACK / gate).is_file()


def _doc(g, name, quadrant="reference", out=None, rev=HEX, standing="UNKNOWN", auth="NONE"):
    d = SD[name]
    g.add((d, RDF.type, SD.Document))
    for p, o in [(SD.title, "t"), (SD.quadrant, quadrant), (SD.outputId, out or name),
                 (SD.subjectRevision, rev), (SD.authority, auth), (SD.standing, standing)]:
        g.add((d, p, Literal(o)))
    g.add((d, SD.capability, SD.AgentAdmission))
    return d


def _step(g, d, name, order=1, consequential=False):
    s = SD[name]
    g.add((d, SD.hasStep, s))
    g.add((s, SD.order, Literal(order)))
    g.add((s, SD.action, Literal("a")))
    g.add((s, SD.consequential, Literal(consequential)))
    return s


def test_missing_required_field_refused():
    g = graph(); g.remove((SD.ReferenceContract, SD.title, None))
    assert rows(g, "010_required_fields")


def test_multi_valued_or_unknown_quadrant_refused():
    g = graph(); g.add((SD.ReferenceContract, SD.quadrant, Literal("tutorial")))
    assert rows(g, "020_single_quadrant")
    g = graph(); _doc(g, "X", quadrant="blog")
    assert rows(g, "020_single_quadrant")


def test_howto_without_steps_refused():
    g = graph(); _doc(g, "X", quadrant="how-to")
    assert rows(g, "030_complete_procedures")


def test_ambiguous_procedure_refused():
    g = graph(); d = _doc(g, "X", quadrant="how-to")
    _step(g, d, "S1", 1); _step(g, d, "S2", 1)
    assert rows(g, "030_complete_procedures")


def test_document_cannot_self_grant_authority():
    g = graph(); _doc(g, "X", auth="DO")
    assert rows(g, "040_authority_separation")


def test_consequential_step_requires_external_authority():
    g = graph(); d = _doc(g, "X", quadrant="how-to")
    _step(g, d, "S1", 1, consequential=True)
    assert rows(g, "040_authority_separation")


def test_mutable_revision_refused():
    g = graph(); _doc(g, "X", rev="main")
    assert rows(g, "050_exact_identity")


def test_alive_without_evidence_refused():
    g = graph(); _doc(g, "X", standing="ALIVE")
    assert rows(g, "060_standing_evidence")
    g = graph(); _doc(g, "Y", standing="FANTASTIC")
    assert rows(g, "060_standing_evidence")


def test_unknown_extension_must_be_unsupported():
    g = graph(); x = SD.Ext1
    g.add((x, RDF.type, SD.Extension)); g.add((SD.ReferenceContract, SD.extension, x))
    assert rows(g, "070_unsupported_extensions")
    g.add((x, SD.standing, Literal("UNSUPPORTED")))
    assert not rows(g, "070_unsupported_extensions")


def test_untyped_or_dangling_link_refused():
    g = graph(); g.remove((SD.LinkHowToToTutorial, SD.linkType, None))
    assert rows(g, "080_typed_links")
    g = graph(); g.set((SD.LinkHowToToTutorial, SD.to, SD.Nowhere))
    assert rows(g, "080_typed_links")


def test_duplicate_output_identity_refused():
    g = graph(); _doc(g, "X", out="reference/contract-fields")
    assert rows(g, "090_output_uniqueness")


@pytest.mark.skipif(shutil.which("ggen") is None, reason="ggen runtime not installed; real sync not exercised")
def test_real_sync_is_idempotent(tmp_path):
    work = tmp_path / "pack"
    shutil.copytree(PACK, work)
    def sync():
        return subprocess.run(["ggen", "sync", "run"], cwd=work, capture_output=True, text=True)
    first = sync(); assert first.returncode == 0, first.stderr
    snap = {p.relative_to(work): p.read_bytes() for p in (work / "consumer").rglob("*") if p.is_file()}
    assert snap
    second = sync(); assert second.returncode == 0, second.stderr
    assert snap == {p.relative_to(work): p.read_bytes() for p in (work / "consumer").rglob("*") if p.is_file()}
