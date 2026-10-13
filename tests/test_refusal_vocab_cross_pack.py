"""Cross-pack court: refusal-vocabulary-pack ValveMapping crosswalk.

Explore finding #4 (L2xx wave): refusal-vocabulary-pack asserts ValveMapping
facts about strata-valve refusal classes. scripts/check_cross_pack_references.py
does NOT flag it, because the crosswalk objects stay inside the pack's own
`urn:refusal-vocabulary:` namespace (rv:vc-* local mirrors), never referencing
`https://strata.chatman.ai/ontology/valve#` IRIs directly. The pack-to-pack
correspondence is therefore carried only by the guard-atom strings
(rv:valveName / rv:valveAtom <-> valve:atom). This court makes that implicit
correspondence explicit and fail-closed over the rdflib union of both packs'
ontologies:

  1. every rv:ValveMapping carries rv:valveClass and rv:ashA2aClass;
  2. every rv:valveClass object is typed rv:ValveClass in the union;
  3. every rv:ashA2aClass object is typed rv:RefusalClass in the union;
  4. every mapped valve class is WITNESSED in the valve graph: there exists a
     strata-valve individual typed (subclass-closure of) valve:RefusalClass
     whose valve:atom equals the mapped class's rv:valveName or rv:valveAtom.

Fail-closed: zero mappings, a missing declaration, or an unparseable source
graph all fail the court.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
from rdflib import Graph, Literal, RDF, URIRef

ROOT = Path(__file__).resolve().parents[1]
RV_ONTOLOGY = ROOT / "packs" / "refusal-vocabulary-pack" / "ontology.ttl"
VALVE_ONTOLOGY = ROOT / "packs" / "strata-valve-pack" / "ontology.ttl"

RV = "urn:refusal-vocabulary:"
VALVE = "https://strata.chatman.ai/ontology/valve#"


def rv(p: str) -> URIRef:
    return URIRef(RV + p)


def valve(p: str) -> URIRef:
    return URIRef(VALVE + p)


def load_union(valve_text: str | None = None) -> Graph:
    """Parse both pack ontologies into one union graph. Any parse failure
    raises -- the court never treats an unparseable source as a pass."""
    g = Graph()
    g.parse(RV_ONTOLOGY.as_posix(), format="turtle")
    if valve_text is None:
        g.parse(VALVE_ONTOLOGY.as_posix(), format="turtle")
    else:
        g.parse(data=valve_text, format="turtle")
    return g


def refusal_class_closure(g: Graph) -> set[URIRef]:
    """valve:RefusalClass plus every class rdfs:subClassOf* it (computed over
    the union graph, one level of transitive closure via fixpoint)."""
    super_of: dict[URIRef, set[URIRef]] = {}
    for s, _, o in g.triples((None, URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"), None)):
        super_of.setdefault(s, set()).add(o)
    closure = {valve("RefusalClass")}
    frontier = list(closure)
    while frontier:
        cur = frontier.pop()
        for sub, supers in super_of.items():
            if cur in supers and sub not in closure:
                closure.add(sub)
                frontier.append(sub)
    return closure


def court(g: Graph) -> list[str]:
    """Return the list of court violations (empty == pass)."""
    violations: list[str] = []

    mappings = {}
    for m in g.subjects(RDF.type, rv("ValveMapping")):
        vc = g.value(m, rv("valveClass"))
        a2a = g.value(m, rv("ashA2aClass"))
        if vc is None or a2a is None:
            violations.append(f"mapping {m} missing valveClass or ashA2aClass")
            continue
        mappings[m] = (vc, a2a)

    if not mappings:
        violations.append("no rv:ValveMapping rows found -- fail-closed")

    witness_atoms: dict[str, set[str]] = {}
    for v in g.subjects(valve("atom"), None):
        atom = g.value(v, valve("atom"))
        if atom is None:
            continue
        types = set(g.objects(v, RDF.type))
        if types & refusal_class_closure(g):
            witness_atoms.setdefault(str(atom), set()).add(str(v))

    for m, (vc, a2a) in sorted(mappings.items(), key=lambda kv: str(kv[0])):
        if (vc, RDF.type, rv("ValveClass")) not in g:
            violations.append(f"{m}: valveClass {vc} not declared rv:ValveClass in union")
        if (a2a, RDF.type, rv("RefusalClass")) in g:
            pass
        elif (a2a, RDF.type, URIRef(RV + "AshA2aRefusalClass")) in g:
            pass  # tolerate either ash_a2a class parent in rv's vocabulary
        else:
            violations.append(f"{m}: ashA2aClass {a2a} not declared a refusal class in union")
        names = {str(x) for x in g.objects(vc, rv("valveName"))} | {
            str(x) for x in g.objects(vc, rv("valveAtom"))
        }
        if not names:
            violations.append(f"{m}: mapped valve class {vc} carries no rv:valveName/valveAtom")
            continue
        if not any(atom in witness_atoms for atom in names):
            violations.append(
                f"{m}: valve class {vc} (atoms {sorted(names)}) has no witness in the "
                "strata-valve graph: no valve:RefusalClass individual carries a matching valve:atom"
            )
    return violations


def test_court_passes_on_real_union():
    g = load_union()
    violations = court(g)
    assert violations == []
    # Floor: the crosswalk really has six rows (guards against a silently
    # empty graph reading as a vacuous pass).
    mappings = list(g.subjects(RDF.type, rv("ValveMapping")))
    assert len(mappings) == 6


def test_sabotage_drop_valve_class_declaration():
    """Drop the valve:MalformedFrameRefusal declaration (and its valve:atom)
    from the valve graph; the malformed-frame mapping must lose its witness
    and the court must fail."""
    original = VALVE_ONTOLOGY.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    out: list[str] = []
    skipping = False
    for line in lines:
        if line.startswith("valve:MalformedFrameRefusal a valve:RefusalClass"):
            skipping = True
            continue
        if skipping:
            if line.startswith(("valve:", "rdf:", "rdfs:", "@prefix")) or not line.startswith(
                ("    ", "\t")
            ):
                skipping = False
        if not skipping:
            out.append(line)
    sabotaged = "".join(out)
    assert "valve:MalformedFrameRefusal a valve:RefusalClass" not in sabotaged, (
        "sabotage failed to remove the class declaration"
    )
    g = load_union(valve_text=sabotaged)
    violations = court(g)
    assert any("vm-malformed-frame" in v and "no witness" in v for v in violations), violations


def test_sabotage_zero_mappings_fails_closed():
    g = load_union(valve_text=VALVE_ONTOLOGY.read_text(encoding="utf-8"))
    for m in list(g.subjects(RDF.type, rv("ValveMapping"))):
        g.remove((m, None, None))
    violations = court(g)
    assert any("fail-closed" in v for v in violations)


def test_inrepo_checker_does_not_flag_refusal_vocab():
    """Regression witness for Explore finding #4's resolution: the in-repo
    checker stays silent about refusal-vocabulary-pack because the crosswalk
    never references valve:-namespace IRIs. If a future crosswalk edit starts
    referencing valve: IRIs without a qualification/consumer.ttl stub, this
    assertion surfaces it."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_cross_pack_references as xref  # noqa: E402

    from marketplace import require_admitted  # noqa: E402

    packs = require_admitted()
    violations, _ = xref.find_violations([p for p in packs])
    offending = [v for v in violations if v.pack == "refusal-vocabulary-pack"]
    assert offending == [], (
        "refusal-vocabulary-pack now trips CROSS_PACK_REFERENCE_UNQUALIFIED; "
        f"add qualification/consumer.ttl stub(s): {offending}"
    )
