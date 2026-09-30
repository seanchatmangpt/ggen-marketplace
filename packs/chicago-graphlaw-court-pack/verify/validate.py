#!/usr/bin/env python3
"""Pack gate runner.
  validate.py corpus [cases.ttl ...]   gates + SHACL + JSON-literal checks over ontology + cases
  validate.py witnesses                each gate: pass witness => no violation, fail witness => violation
Gates are SPARQL ASK: true = violation. Exit 0 only if everything holds. Real output, no skips."""
import json, pathlib, sys
from rdflib import Graph, Namespace, URIRef
from pyshacl import validate

ROOT = pathlib.Path(__file__).resolve().parent.parent
CC = Namespace("https://chicago.graphlaw.dev/court#")

def load(*files):
    g = Graph()
    for f in files:
        g.parse(str(f), format="turtle")
    return g

def gates():
    return sorted((ROOT / "gates").glob("*.rq"))

def violated(g, gate):
    return bool(g.query(gate.read_text()).askAnswer)

def json_checks(g):
    errs = []
    for p in ("request", "requestB", "expect", "expectB", "compare"):
        for s, o in g.subject_objects(CC[p]):
            try:
                v = json.loads(str(o))
            except Exception as e:
                errs.append(f"{s} cc:{p}: not JSON ({e})"); continue
            if "####\"" in str(o) or "\"####" in str(o):
                errs.append(f"{s} cc:{p}: contains raw-string delimiter")
            if p in ("expect", "expectB"):
                if not isinstance(v, list):
                    errs.append(f"{s} cc:{p}: not an array"); continue
                for a in v:
                    ptr = a.get("ptr") if isinstance(a, dict) else None
                    if not isinstance(ptr, str) or not (ptr == "" or ptr.startswith("/")):
                        errs.append(f"{s} cc:{p}: bad ptr {ptr!r}")
                    if not any(k in a for k in ("eq", "contains", "len", "absent")):
                        errs.append(f"{s} cc:{p}: no assertion form in {a}")
            if p == "compare":
                for c in v:
                    if c.get("rel") not in ("eq", "neq") or not str(c.get("a", "")).startswith("/") or not str(c.get("b", "")).startswith("/"):
                        errs.append(f"{s} cc:compare: bad entry {c}")
            if p in ("request", "requestB"):
                for step in (v if isinstance(v, list) else [v]):
                    if not isinstance(step, dict) or "op" not in step:
                        errs.append(f"{s} cc:{p}: step lacks op: {step!r}")
    return errs

def corpus(cases):
    ont = ROOT / "ontology.ttl"
    g = load(ont, *cases)
    bad = 0
    for gate in gates():
        v = violated(g, gate)
        print(f"gate {gate.stem}: {'VIOLATION' if v else 'ok'}")
        bad += v
    shapes = load(ROOT / "shapes.ttl")
    conforms, _, text = validate(g, shacl_graph=shapes, inference="rdfs", abort_on_first=False)
    print(f"shacl: {'conforms' if conforms else 'NONCONFORMANT'}")
    if not conforms:
        print(text); bad += 1
    errs = json_checks(g)
    for e in errs:
        print("json:", e)
    print(f"json literals: {'ok' if not errs else str(len(errs)) + ' errors'}")
    bad += len(errs)
    print("RESULT:", "REFUSED" if bad else "ADMITTED", f"({bad} problems)")
    return 1 if bad else 0

def witnesses():
    ont = ROOT / "ontology.ttl"
    bad = 0
    for gate in gates():
        p = load(ont, ROOT / "witnesses/pass" / f"{gate.stem}.ttl")
        f = load(ont, ROOT / "witnesses/fail" / f"{gate.stem}.ttl")
        vp, vf = violated(p, gate), violated(f, gate)
        ok = (not vp) and vf
        print(f"witness {gate.stem}: pass->{'violation' if vp else 'clean'} fail->{'violation' if vf else 'CLEAN'} {'OK' if ok else 'BAD'}")
        bad += not ok
    print("RESULT:", "REFUSED" if bad else "WITNESSES_OK", f"({bad} bad)")
    return 1 if bad else 0

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "corpus"
    if mode == "witnesses":
        sys.exit(witnesses())
    files = [pathlib.Path(a) for a in sys.argv[2:]] or sorted((ROOT / "cases").glob("*.ttl"))
    sys.exit(corpus(files))
