#!/usr/bin/env bash
# Court enterprise-architecture-pack -- migrated from .github/workflows/enterprise-architecture-pack.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Positive exact-subject qualification
echo "::group::enterprise-architecture-pack: Positive exact-subject qualification"
(
set -e
python packs/enterprise-architecture-pack/gates/validate_enterprise_architecture.py \
  packs/enterprise-architecture-pack/fixtures/ea-graph.json
)
echo "::endgroup::"
# --- Authority-widening falsifier must be caught
echo "::group::enterprise-architecture-pack: Authority-widening falsifier must be caught"
(
set -e
python packs/enterprise-architecture-pack/gates/validate_enterprise_architecture.py \
  packs/enterprise-architecture-pack/fixtures/refused-authority.json \
  --expect-refusal AUTHORITY_WIDENING
)
echo "::endgroup::"
# --- Pack has no consequential authority declaration
echo "::group::enterprise-architecture-pack: Pack has no consequential authority declaration"
(
set -e
! grep -RniE 'grants_do_authority[[:space:]]*=[[:space:]]*true|authority[[:space:]]*=[[:space:]]*"DO"' \
  packs/enterprise-architecture-pack/pack.toml \
  packs/enterprise-architecture-pack/ggen.toml
)
echo "::endgroup::"
