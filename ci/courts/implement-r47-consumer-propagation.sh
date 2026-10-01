#!/usr/bin/env bash
# Court implement-r47-consumer-propagation -- migrated from .github/workflows/implement-r47-consumer-propagation.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R47 consumer propagation courts
echo "::group::implement-r47-consumer-propagation: Execute R47 consumer propagation courts"
(
set -e
python3 - <<'PY'
from pathlib import Path
from rdflib import Graph
root=Path('packs/epistemic-sensor-factory-pack')
g=Graph(); g.parse(root/'ontology.ttl'); g.parse(root/'fixtures/r46-live-replication.ttl')
manifest=root/'queries/r47-consumer-propagation.manifest'
names=[line.strip() for line in manifest.read_text().splitlines() if line.strip()]
assert len(names)==50, len(names)
assert len(set(names))==50, 'duplicate semantic query identity'
qs=[root/'queries'/name for name in names]
missing=[str(p) for p in qs if not p.is_file()]
assert not missing, missing
for p in qs:
    list(g.query(p.read_text()))
print(f'R47_CONSUMER_PROPAGATION_PASS={len(qs)}')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::implement-r47-consumer-propagation: Refuse ambient consequential actuation"
(
set -e
! grep -R -E 'actuationPerformed[[:space:]]+true|consequential_do.*true' packs/epistemic-sensor-factory-pack/fixtures packs/epistemic-sensor-factory-pack/templates
)
echo "::endgroup::"
