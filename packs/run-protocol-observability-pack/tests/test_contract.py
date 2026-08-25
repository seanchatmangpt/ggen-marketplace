from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
queries = sorted((ROOT / "queries").glob("*.rq"))
assert len(queries) == 50, len(queries)
assert (ROOT / "ontology.ttl").exists()
assert (ROOT / "fixtures/run-protocol.ttl").exists()
assert all("run-protocol-observability#" in q.read_text() for q in queries)
assert all("SELECT" in q.read_text() or "ASK" in q.read_text() for q in queries)
assert "BRCE_ONLY" in (ROOT / "ontology.ttl").read_text()
assert "actuationPerformed true" not in (ROOT / "fixtures/run-protocol.ttl").read_text()
print("R66 run-protocol contract: PASS (50 sensors)")
