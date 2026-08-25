#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
QUERIES = sorted((ROOT / "queries").glob("*.rq"))

# The pack is cumulative across independently-qualified MEASURE generations.
# R43 owns 001..050. Later generations may append disjoint, monotone ranges;
# historical qualification must not require globally contiguous numbering.
assert len(QUERIES) >= 50, f"expected at least 50 semantic sensors, got {len(QUERIES)}"
seen = set()
numbered = []
for path in QUERIES:
    match = re.match(r"^(\d{3})_", path.name)
    assert match, f"sensor lacks numeric identity: {path.name}"
    number = int(match.group(1))
    assert number not in seen, f"duplicate sensor identity: {number:03d}"
    seen.add(number)
    numbered.append(number)
    text = path.read_text()
    assert "SELECT" in text.upper(), path
    assert "DELETE" not in text.upper(), path
    assert "INSERT" not in text.upper(), path
    assert "LOAD " not in text.upper(), path

assert set(range(1, 51)) <= seen, "R43 baseline sensors 001..050 must remain immutable and complete"
assert numbered == sorted(numbered), "sensor identities must remain monotone"

ontology = (ROOT / "ontology.ttl").read_text()
for public in ("www.w3.org/ns/prov#", "www.w3.org/ns/dqv#", "www.w3.org/ns/dcat#", "www.w3.org/ns/odrl/2/", "purl.org/dc/terms/"):
    assert public in ontology, public

manifest = (ROOT / "ggen.toml").read_text()
assert "[[generation.rules]]" in manifest
assert "generated/replication-epistemic-observability/" in manifest
for template in ("standing-report.json.tera", "multiplier-report.json.tera"):
    text = (ROOT / "templates" / template).read_text()
    assert '"actuation_performed":false' in text

multiplier_query = (ROOT / "queries" / "050_1000x_shortfall.rq").read_text()
assert "ORDER BY ?run" in multiplier_query, "strict ggen generation requires deterministic multiplier ordering"

fixture = (ROOT / "fixtures" / "r43-reference.ttl").read_text()
assert "4bd157843a983f1e8151dcf589dc7e49dc28e37f" in fixture
assert "a2e0eca7516df44738a7b41b2c4e7498d00ef919" in fixture
assert re.search(r"reo:seedObservations\s+2", fixture)
assert re.search(r"reo:actionableOpportunities\s+8", fixture)
print(f"replication epistemic observability contract: PASS sensors={len(QUERIES)} r43=50")
