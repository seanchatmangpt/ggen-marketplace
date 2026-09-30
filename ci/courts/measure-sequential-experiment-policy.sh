#!/usr/bin/env bash
# Court measure-sequential-experiment-policy -- migrated from .github/workflows/measure-sequential-experiment-policy.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Verify sequential measurement surface
echo "::group::measure-sequential-experiment-policy: Verify sequential measurement surface"
(
set -e
python3 - <<'PY'
from pathlib import Path
import re
q = sorted(Path('packs/dfcm-maximalist-court-pack/queries').glob('seq-*.rq'))
assert len(q) >= 32, len(q)
ontology = Path('packs/dfcm-maximalist-court-pack/ontology.ttl').read_text()
for term in ('ExperimentStep','sequenceId','stepIndex','predictedGain','realizedGain','policyDecision','actuationPerformed'):
    assert f'dmc:{term}' in ontology, term
for path in q:
    text = path.read_text()
    assert 'PREFIX dmc:' in text and ('SELECT' in text or 'ASK' in text), path
print(f'sequential_query_count={len(q)}')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-sequential-experiment-policy: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'curl |wget |requests\.(post|put|patch|delete)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/dfcm-maximalist-court-pack/queries/seq-*.rq
)
echo "::endgroup::"
