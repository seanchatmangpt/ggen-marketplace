#!/usr/bin/env bash
# Court measure-r72-temporal-truth -- migrated from .github/workflows/measure-r72-temporal-truth.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Parse RDF and all SPARQL sensors
echo "::group::measure-r72-temporal-truth: Parse RDF and all SPARQL sensors"
(
set -e
python - <<'PY'
from pathlib import Path
from rdflib import Graph
from rdflib.plugins.sparql.parser import parseQuery
root = Path('packs/temporal-truth-observability-pack')
Graph().parse(root/'ontology.ttl', format='turtle')
queries = sorted((root/'queries').glob('*.rq'))
assert len(queries) == 48, len(queries)
for q in queries:
    parseQuery(q.read_text())
print(f'R72_ALIVE sensors={len(queries)}')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r72-temporal-truth: Refuse ambient consequential actuation"
(
set -e
! grep -R -E 'kubectl apply|terraform apply|aws .*create|gcloud .*create|az .*create' packs/temporal-truth-observability-pack
)
echo "::endgroup::"
