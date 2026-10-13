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
# --scope all is REQUIRED: strata packs are deliberately outside
# marketplace.active.toml (E19 deferral, see docs/sjira/v26.10.8/STRATA-ACTIVATION-DEFERRAL.md);
# default --scope active would refuse ACTIVE_SCOPE_PACK_MISSING. --scope all + explicit
# --pack names is the lawful selection path. Do not "fix" to --scope active.
python3 scripts/qualify_packs_r18.py \
  --ggen "$GGEN_BIN" \
  --pack strata-audit-pack \
  --pack strata-cas-pack \
  --pack strata-chain-pack \
  --pack strata-consensus-pack \
  --pack strata-governance-pack \
  --pack strata-hash-pack \
  --pack strata-ledger-pack \
  --pack strata-net-pack \
  --pack strata-pn64-pack \
  --pack strata-protocol-pack \
  --pack strata-signer-pack \
  --pack strata-store-pack \
  --pack strata-stratus-pack \
  --pack strata-temprun-pack \
  --pack strata-tx-pack \
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
