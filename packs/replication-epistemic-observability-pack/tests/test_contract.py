#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
QUERIES = sorted((ROOT / "queries").glob("*.rq"))

# This pack is cumulative: later MEASURE generations append independently
# qualified sensor families rather than replacing the original R43 fifty.
assert len(QUERIES) >= 50, f"expected at least 50 semantic sensors, got {len(QUERIES)}"
expected = [f"{i:03d}_" for i in range(1, len(QUERIES) + 1)]
for prefix, path in zip(expected, QUERIES, strict=True):
    assert path.name.startswith(prefix), (prefix, path.name)
    text = path.read_text()
    assert "SELECT" in text.upper(), path
    assert "DELETE" not in text.upper(), path
    assert "INSERT" not in text.upper(), path
    assert "LOAD " not in text.upper(), path

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
print(f"replication epistemic observability contract: PASS sensors={len(QUERIES)}")
