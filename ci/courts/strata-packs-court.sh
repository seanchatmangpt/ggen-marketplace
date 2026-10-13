#!/usr/bin/env bash
# Court strata-packs-court -- bounded qualification of the strata pack family
# via scripts/qualify_packs_r18.py. Pure verification; no network, no mutation.
# Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

: "${GGEN_BIN:?GGEN_BIN required}"

echo "::group::strata-packs-court: qualify strata packs"
(
set -e
python3 scripts/qualify_packs_r18.py \
  --ggen "$GGEN_BIN" \
  --pack strata-cas-pack \
  --pack strata-pn64-pack \
  --pack strata-protocol-pack \
  --pack strata-signer-pack \
  --pack strata-stratus-pack \
  --pack strata-temprun-pack \
  --pack strata-valve-pack \
  --scope all \
  --timeout-seconds 15 \
  --workers 4 \
  --report "${RUNNER_TEMP:-/tmp}/strata-qualification.json"
)
echo "::endgroup::"

echo "::group::strata-packs-court: report json sanity"
(
set -e
python3 -m json.tool "${RUNNER_TEMP:-/tmp}/strata-qualification.json" > /dev/null
)
echo "::endgroup::"
