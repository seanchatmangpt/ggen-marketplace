#!/usr/bin/env bash
# Court implement-r46-replication-capital -- migrated from .github/workflows/implement-r46-replication-capital.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Guard bounded real-ggen qualification headroom
echo "::group::implement-r46-replication-capital: Guard bounded real-ggen qualification headroom"
(
set -e
python3 scripts/check_qualification_headroom.py
)
echo "::endgroup::"
# --- Execute exact R46 court tranche
echo "::group::implement-r46-replication-capital: Execute exact R46 court tranche"
(
set -eo pipefail
python3 - <<'PY'
from pathlib import Path
from rdflib import Graph
root = Path('packs/replication-epistemic-observability-pack')
graph = Graph()
graph.parse(root / 'ontology.ttl', format='turtle')
for fixture in sorted((root / 'fixtures').glob('*.ttl')):
    graph.parse(fixture, format='turtle')
queries = sorted((root / 'queries').glob('*.rq'))
tranche = [q for q in queries if 186 <= int(q.name.split('_', 1)[0]) <= 235]
assert len(tranche) == 50, len(tranche)
for query in tranche:
    graph.query(query.read_text())
print(f'R46_EXECUTED={len(tranche)}')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::implement-r46-replication-capital: Refuse ambient consequential actuation"
(
set -eo pipefail
! grep -RniE 'actuation_performed[[:space:]]*[=:][[:space:]]*true|consequential_do[[:space:]]*[=:][[:space:]]*true' \
  packs/replication-epistemic-observability-pack/ontology.ttl \
  packs/replication-epistemic-observability-pack/fixtures \
  packs/replication-epistemic-observability-pack/templates
)
echo "::endgroup::"
