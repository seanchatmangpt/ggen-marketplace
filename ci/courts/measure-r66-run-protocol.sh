#!/usr/bin/env bash
# Court measure-r66-run-protocol -- migrated from .github/workflows/measure-r66-run-protocol.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Run permanent contract court
echo "::group::measure-r66-run-protocol: Run permanent contract court"
(
set -e
python3 packs/run-protocol-observability-pack/tests/test_contract.py
)
echo "::endgroup::"
# --- Execute all 50 SPARQL sensors
echo "::group::measure-r66-run-protocol: Execute all 50 SPARQL sensors"
(
set -e
python3 - <<'PY'
from pathlib import Path
from rdflib import Graph
root=Path('packs/run-protocol-observability-pack')
g=Graph()
g.parse(root/'ontology.ttl', format='turtle')
g.parse(root/'fixtures/run-protocol.ttl', format='turtle')
qs=sorted((root/'queries').glob('*.rq'))
for q in qs:
    list(g.query(q.read_text()))
assert len(qs)==50
print('R66 SPARQL execution: PASS', len(qs))
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r66-run-protocol: Refuse ambient consequential actuation"
(
set -e
! grep -R -E "actuationPerformed[[:space:]]+true" packs/run-protocol-observability-pack/fixtures packs/run-protocol-observability-pack/templates packs/run-protocol-observability-pack/ontology.ttl
)
echo "::endgroup::"
