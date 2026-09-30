#!/usr/bin/env bash
# Court measure-r68-run-closure -- migrated from .github/workflows/measure-r68-run-closure.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Run R68 permanent court
echo "::group::measure-r68-run-closure: Run R68 permanent court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/qualification/test_r68_run_closure.py
)
echo "::endgroup::"
# --- Parse RDF and execute R68 sensors
echo "::group::measure-r68-run-closure: Parse RDF and execute R68 sensors"
(
set -e
python3 - <<'PY'
from pathlib import Path
from rdflib import Graph
root=Path('packs/epistemic-sensor-factory-pack')
g=Graph()
g.parse(root/'ontology.r68-run-closure-observability.ttl', format='turtle')
g.parse(root/'fixtures/r68-run-closure.ttl', format='turtle')
qs=sorted((root/'queries').glob('20[0-4][0-9]_r68_*.rq'))+sorted((root/'queries').glob('2050_r68_*.rq'))
assert len(qs)==50, len(qs)
for q in qs:
    list(g.query(q.read_text()))
print(f'R68 SPARQL PASS {len(qs)}/50')
PY
)
echo "::endgroup::"
