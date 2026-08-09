#!/usr/bin/env python3
from pathlib import Path
import json, tomllib
from rdflib import Graph, Namespace, RDF
from rdflib.namespace import SKOS
ROOT = Path(__file__).resolve().parents[1]
V30 = Namespace("https://ggen.io/marketplace/vision2030#")
def fail(msg): raise SystemExit(f"REFUSED:VISION_2030_PACK_INVALID:{msg}")
for name in ("package.toml", "ggen.toml"):
    with (ROOT / name).open("rb") as fh: tomllib.load(fh)
g = Graph(); g.parse(ROOT / "ontology.ttl", format="turtle"); g.parse(ROOT / "shapes.ttl", format="turtle")
caps = sorted(set(g.subjects(RDF.type, V30.Capability)), key=str)
fams = set(g.subjects(RDF.type, V30.CapabilityFamily))
if len(caps) < 50: fail(f"expected >=50 capabilities, observed {len(caps)}")
if len(fams) < 10: fail(f"expected >=10 families, observed {len(fams)}")
for cap in caps:
    for pred in (SKOS.prefLabel, V30.family, V30.leverageScore, V30.requiredStanding, V30.cognitionValueDirection):
        if len(list(g.objects(cap, pred))) != 1: fail(f"{cap} missing/duplicate {pred}")
    family = next(g.objects(cap, V30.family)); score = int(next(g.objects(cap, V30.leverageScore)))
    if not 0 <= score <= 100: fail(f"score out of range: {cap}")
    if str(next(g.objects(cap, V30.cognitionValueDirection))) != "more-valuable-as-cognition-abundant": fail(f"post-AGI inversion failed: {cap}")
    for pred in (V30.problemEliminated, V30.primitiveRequirement, V30.ggenRole, V30.consequence2030):
        if not list(g.objects(family, pred)): fail(f"family default missing {pred}")
for template in (ROOT / "templates").glob("*.tera"):
    if "results" not in template.read_text(): fail(f"{template.name} does not consume query results")
scores = sorted((int(next(g.objects(c,V30.leverageScore))), str(next(g.objects(c,SKOS.prefLabel)))) for c in caps)[::-1]
print(json.dumps({"standing":"ALIVE","capabilities":len(caps),"families":len(fams),"crown_score":scores[0][0],"top_capabilities":[n for _,n in scores[:5]]}, sort_keys=True))
