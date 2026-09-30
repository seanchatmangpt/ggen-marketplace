#!/usr/bin/env bash
# Court measure-observability-amplifier-r15 -- migrated from .github/workflows/measure-observability-amplifier-r15.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Verify observability measurement surface
echo "::group::measure-observability-amplifier-r15: Verify observability measurement surface"
(
set -e
test "$(find packs/ggen-project-boundary-pack/queries -name 'r15-observe-*.rq' | wc -l)" -eq 40
test "$(find packs/ggen-project-boundary-pack/fixtures -name 'r15-*.ttl' | wc -l)" -eq 8
grep -q 'http://www.w3.org/ns/prov#' packs/ggen-project-boundary-pack/observability-amplifier.ttl
grep -q 'http://www.w3.org/ns/dqv#' packs/ggen-project-boundary-pack/observability-amplifier.ttl
grep -q 'FailureFanoutMetric' packs/ggen-project-boundary-pack/observability-amplifier.ttl
)
echo "::endgroup::"
# --- Verify innovation-capital receipt
echo "::group::measure-observability-amplifier-r15: Verify innovation-capital receipt"
(
set -e
python3 - <<'PY'
import hashlib, json
from pathlib import Path
p=Path('receipts/measure/2026-08-24-observability-amplifier-r15.json')
r=json.loads(p.read_text())
digest=r.pop('sha256')
raw=json.dumps(r,sort_keys=True,separators=(',',':'))
assert hashlib.sha256(raw.encode()).hexdigest()==digest
assert r['seed_observations']==4
assert r['actionable_opportunities']==12
assert r['discovery_multiplier']==3.0
assert r['query_count']==40 and r['fixture_count']==8
assert 'root-cause-fanout' in r['sensor_families']
assert r['authority']=='OBSERVE|VERIFY|CONSTRUCT'
assert r['consequential_do']=='BRCE_ONLY'
assert r['actuation_performed'] is False
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-observability-amplifier-r15: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/ggen-project-boundary-pack/observability-amplifier.ttl packs/ggen-project-boundary-pack/queries/r15-observe-*.rq packs/ggen-project-boundary-pack/fixtures/r15-*.ttl receipts/measure/2026-08-24-observability-amplifier-r15.json
)
echo "::endgroup::"
