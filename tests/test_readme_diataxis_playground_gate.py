"""PACK_FEEDBACK item 425 closure court (readme-diataxis-pack Playground gate).

Real collaborators only: the pack's real index.md.tmpl, its real frontmatter
SPARQL queries executed by rdflib against the pack's real qualification
fixture graph (qualification/consumer.ttl), and real renders of the real
template body.

(a) fixture graph (declares rdx:PlaygroundFile rows) -> Playground section present.
(b) same graph minus PlaygroundFile rows -> NO Playground section anywhere in
    the render. This is the item-425 defect shape: frozen-duckdb declared no
    playground rows and still got a permanent dead link in a GENERATED file.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml
from jinja2 import Environment
from rdflib import RDF, Graph

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "readme-diataxis-pack"
TMPL = PACK / "templates" / "index.md.tmpl"
FIXTURE = PACK / "qualification" / "consumer.ttl"
RDX = "https://seanchatmangpt.github.io/ggen-marketplace/readme-diataxis#"
PLAYGROUND_LINK = "[Playground](../playground/)"


def _parts() -> tuple[dict, str]:
    raw = TMPL.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    assert m, "index.md.tmpl must keep its frontmatter/body split"
    return yaml.safe_load(m.group(1)), m.group(2)


@pytest.fixture(scope="module")
def parts() -> tuple[dict, str]:
    return _parts()


def _fixture(with_playground: bool) -> Graph:
    full = Graph()
    full.parse(FIXTURE, format="turtle")
    if with_playground:
        return full
    stripped = Graph()
    pg_type = RDF.type
    playground_subjects = {
        s for s in full.subjects(RDF.type, None) if str(s).startswith("urn:readme-diataxis:playground:")
    }
    for s, p, o in full:
        # drop the rdx:PlaygroundFile typed rows and anything only reachable
        # through them (embedded playground-content literals stay out by
        # subject, not by string surgery on the graph)
        if s in playground_subjects:
            continue
        if pg_type == p and o in playground_subjects:
            continue
        stripped.add((s, p, o))
    return stripped


def _render(front: dict, body: str, g: Graph) -> str:
    env = Environment()
    return env.from_string(body).render(
        project=list(g.query(front["sparql"]["project"])),
        examples=list(g.query(front["sparql"]["examples"])),
        playground=list(g.query(front["sparql"]["playground"])),
    )


def test_template_declares_playground_query(parts):
    front, _ = parts
    assert "playground" in front["sparql"]
    assert "rdx:PlaygroundFile" in front["sparql"]["playground"]


def test_playground_section_present_with_declared_rows(parts):
    front, body = parts
    g = _fixture(with_playground=True)
    rows = list(g.query(front["sparql"]["playground"]))
    assert rows, "qualification fixture must declare PlaygroundFile rows"
    out = _render(front, body, g)
    assert PLAYGROUND_LINK in out


def test_playground_section_absent_without_rows(parts):
    front, body = parts
    g = _fixture(with_playground=False)
    assert list(g.query(front["sparql"]["project"])), "project rows must survive the strip"
    assert list(g.query(front["sparql"]["examples"])), "example rows must survive the strip"
    assert not list(g.query(front["sparql"]["playground"]))
    out = _render(front, body, g)
    assert PLAYGROUND_LINK not in out
    assert "playground" not in out.lower()


def test_playground_row_query_matches_gate_expectations(parts):
    # the gating query only admits rows that satisfy the pack's own required-
    # properties gate (relPath present) -- a declared-but-incomplete row does
    # not resurrect the section
    front, _ = parts
    g = Graph()
    g.parse(data="", format="turtle")
    g.parse(
        data=(
            "@prefix rdx: <" + RDX + "> .\n"
            "<urn:t:bad> a rdx:PlaygroundFile ; rdx:position 0 ."
        ),
        format="turtle",
    )
    rows = list(g.query(front["sparql"]["playground"]))
    assert rows == [] or all(r.relPath is not None for r in rows)
