#!/usr/bin/env bash
# Court measure-observability-realization-r16 -- migrated from .github/workflows/measure-observability-realization-r16.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Verify realization measurement surface
echo "::group::measure-observability-realization-r16: Verify realization measurement surface"
(
set -e
test "$(find packs/ggen-project-boundary-pack/queries -name 'r16-realize-*.rq' | wc -l)" -eq 12
test "$(find packs/ggen-project-boundary-pack/fixtures -name 'r16-*.ttl' | wc -l)" -eq 1
grep -q 'MeasurementRun' packs/ggen-project-boundary-pack/observability-realization.ttl
grep -q 'NoveltyMetric' packs/ggen-project-boundary-pack/observability-realization.ttl
)
echo "::endgroup::"
# --- Verify realization receipt
echo "::group::measure-observability-realization-r16: Verify realization receipt"
(
set -e
python3 - <<'PY'
import hashlib,json
from pathlib import Path
p=Path('receipts/measure/2026-08-24-observability-realization-r16.json')
r=json.loads(p.read_text()); digest=r.pop('sha256')
assert hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest()==digest
assert r['contained'] is True
assert r['run_seed_count']==4 and r['run_opportunity_count']==12
assert r['run_novel_count']==12 and r['run_actionable_count']==12
assert r['run_relief_count']==0
assert r['authority']=='OBSERVE|VERIFY|CONSTRUCT'
assert r['consequential_do']=='BRCE_ONLY' and r['actuation_performed'] is False
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-observability-realization-r16: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/ggen-project-boundary-pack/observability-realization.ttl packs/ggen-project-boundary-pack/queries/r16-realize-*.rq packs/ggen-project-boundary-pack/fixtures/r16-*.ttl receipts/measure/2026-08-24-observability-realization-r16.json
)
echo "::endgroup::"
