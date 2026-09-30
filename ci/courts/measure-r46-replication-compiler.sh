#!/usr/bin/env bash
# Court measure-r46-replication-compiler -- migrated from .github/workflows/measure-r46-replication-compiler.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Run permanent R46 court
echo "::group::measure-r46-replication-compiler: Run permanent R46 court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r46_replication_compiler.py
)
echo "::endgroup::"
# --- Parse and execute R46 ordinal-slot SPARQL family
echo "::group::measure-r46-replication-compiler: Parse and execute R46 ordinal-slot SPARQL family"
(
set -e
python3 - <<'PY'
from pathlib import Path
from rdflib import Graph
root=Path('packs/epistemic-sensor-factory-pack')
g=Graph(); g.parse(root/'ontology.ttl'); g.parse(root/'fixtures/r46-live-replication.ttl')
qs=[]
for p in sorted((root/'queries').glob('*.rq')):
    if p.name[:3].isdigit() and 186 <= int(p.name[:3]) <= 235:
        list(g.query(p.read_text())); qs.append(p.name)
slots={int(name[:3]) for name in qs}
assert slots == set(range(186,236)), sorted(set(range(186,236)) - slots)
print('R46 ordinal slots covered:', len(slots), 'slot queries executed:', len(qs))
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r46-replication-compiler: Refuse ambient consequential actuation"
(
set -e
! grep -R -E "actuationPerformed[[:space:]]+true|consequential_do[\"'][[:space:]]*:[[:space:]]*true" packs/epistemic-sensor-factory-pack/fixtures packs/epistemic-sensor-factory-pack/templates
)
echo "::endgroup::"
