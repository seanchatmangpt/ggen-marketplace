#!/usr/bin/env bash
# Court measure-r45-epistemic-sensor-factory -- migrated from .github/workflows/measure-r45-epistemic-sensor-factory.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Qualify sensor factory contract
echo "::group::measure-r45-epistemic-sensor-factory: Qualify sensor factory contract"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_contract.py
)
echo "::endgroup::"
# --- Qualify R45 sensor-family contract
echo "::group::measure-r45-epistemic-sensor-factory: Qualify R45 sensor-family contract"
(
set -e
python3 packs/replication-epistemic-observability-pack/scripts/r45_consumer_replication_court.py
)
echo "::endgroup::"
# --- Qualify R46 replication compiler contract
echo "::group::measure-r45-epistemic-sensor-factory: Qualify R46 replication compiler contract"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r46_replication_compiler.py
)
echo "::endgroup::"
# --- Parse and execute bounded R45 and R46 SPARQL tranches
echo "::group::measure-r45-epistemic-sensor-factory: Parse and execute bounded R45 and R46 SPARQL tranches"
(
set -e
python3 - <<'PY'
from pathlib import Path
from rdflib import Graph
from rdflib.plugins.sparql.processor import prepareQuery
Graph().parse('packs/epistemic-sensor-factory-pack/ontology.ttl', format='turtle')
q45=Path('packs/replication-epistemic-observability-pack/queries')
r45=sorted(p for p in q45.glob('*.rq') if p.name.split('_')[0].isdigit() and 86 <= int(p.name.split('_')[0]) <= 135)
assert len(r45)==50, len(r45)
for p in r45: prepareQuery(p.read_text())
root=Path('packs/epistemic-sensor-factory-pack')
g=Graph(); g.parse(root/'ontology.ttl'); g.parse(root/'fixtures/r46-live-replication.ttl')
r46=sorted(p for p in (root/'queries').glob('*.rq') if p.name[:3].isdigit() and 186 <= int(p.name[:3]) <= 235)
slots={int(p.name[:3]) for p in r46}
assert slots == set(range(186,236)), sorted(set(range(186,236)) - slots)
for p in r46: list(g.query(p.read_text()))
print(f'R45_PARSE_PASS={len(r45)} R46_SLOT_COVERAGE={len(slots)} R46_EXECUTION_PASS={len(r46)}')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r45-epistemic-sensor-factory: Refuse ambient consequential actuation"
(
set -e
python3 packs/replication-epistemic-observability-pack/scripts/r45_consumer_replication_court.py
grep -q 'odrl:prohibition \[ odrl:action odrl:execute \]' packs/epistemic-sensor-factory-pack/ontology.ttl
! grep -R -E 'actuationPerformed[[:space:]]+true|consequential_do.*true' packs/epistemic-sensor-factory-pack/fixtures packs/epistemic-sensor-factory-pack/templates
)
echo "::endgroup::"
