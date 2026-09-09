#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
ontology = (root / "ontology.ttl").read_text()
ggen = (root / "ggen.toml").read_text()
fixture = (root / "fixtures/r53-closed-loop-consumer-assimilation.ttl").read_text()
errors = []

def admit(name, ok):
    print(f"{name}={'PASS' if ok else 'FAIL'}")
    if not ok:
        errors.append(name)

admit("PUBLIC_PROV", "http://www.w3.org/ns/prov#" in ontology)
admit("PUBLIC_DQV", "http://www.w3.org/ns/dqv#" in ontology)
admit("PUBLIC_DCAT", "http://www.w3.org/ns/dcat#" in ontology)
admit("PUBLIC_ODRL", "http://www.w3.org/ns/odrl/2/" in ontology)
admit("CLOSED_LOOP_COMPILER", "ClosedLoopAssimilationCompiler" in ontology)
admit("ASSIMILATION_RULE", 'name = "closed-loop-assimilation-plan"' in ggen)
admit("NEXT_WAVE_RULE", 'name = "next-wave-plan"' in ggen)
admit("NO_GENERATED_EDITING_SURFACE", "generated/epistemic-sensor-factory" in ggen)
admit("GGEN_QUALIFIED_HEAD", "e7bc695976bba37d1abf73a266da1b2267ca2a1d" in fixture)
admit("GGEN_MERGE", "a9967f98df05f7a1f0c54376b2a35508bacb935d" in fixture)
admit("GGEN_DEFAULT_CONTAINS", "ddfa602bfbab57b7ed5150f61b0acac7a41e3020" in fixture)
admit("NO_AMBIENT_DO", "esf:actuationPerformed false" in fixture and "esf:noAmbientDo true" in fixture)
queries = [p for p in (root / "queries").glob("*.rq") if re.match(r"(?:45[1-9]|4[6-9][0-9]|500)_", p.name)]
admit("FIFTY_SENSORS", len(queries) == 50)
if errors:
    raise SystemExit("REFUSED[R53_CLOSED_LOOP_CONTRACT]=" + ",".join(errors))
print("R53_CLOSED_LOOP_CONTRACT=ALIVE")
