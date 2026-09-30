#!/usr/bin/env bash
# Court fortune5-control-capital -- migrated from .github/workflows/fortune5-control-capital.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Run Fortune 5 integration court
echo "::group::fortune5-control-capital: Run Fortune 5 integration court"
(
set -e
python3 -m unittest tests/test_fortune5_control_capital.py -v
)
echo "::endgroup::"
# --- Run counterfactual replay proof courts
echo "::group::fortune5-control-capital: Run counterfactual replay proof courts"
(
set -e
python3 -m unittest discover -s packs/counterfactual-frontier-replay-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Verify replay Fortune 5 control profile
echo "::group::fortune5-control-capital: Verify replay Fortune 5 control profile"
(
set -e
test "$(find packs/counterfactual-frontier-replay-pack/gates -name '*.rq' | wc -l)" -ge 3
python3 - <<'PY'
import json
p=json.load(open('packs/counterfactual-frontier-replay-pack/qualification/fortune5-profile.json'))
required={'compiler-truth','conflict-truth','trust-truth','proof-truth'}
assert {x['id'] for x in p['required_capabilities']} == required
assert all(x['positive_execution'] and x['negative_refusal'] and x['receipt_replay'] for x in p['required_capabilities'])
assert p['subject']['authority_ceiling'] == 'SELECT|CONSTRUCT|VERIFY'
assert p['subject']['consequential_do'] is False
PY
)
echo "::endgroup::"
# --- Run runtime authenticity falsifiers
echo "::group::fortune5-control-capital: Run runtime authenticity falsifiers"
(
set -e
export PYTHONPATH="packs/runtime-evidence-authenticity-pack"
python3 -m unittest discover -s packs/runtime-evidence-authenticity-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Run authenticity-control falsifiers
echo "::group::fortune5-control-capital: Run authenticity-control falsifiers"
(
set -e
export PYTHONPATH="packs/runtime-evidence-authenticity-control-pack"
python3 -m unittest discover -s packs/runtime-evidence-authenticity-control-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::fortune5-control-capital: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' \
  packs/counterfactual-frontier-replay-pack \
  packs/runtime-evidence-authenticity-pack \
  packs/runtime-evidence-authenticity-control-pack \
  tests/test_fortune5_control_capital.py
)
echo "::endgroup::"
