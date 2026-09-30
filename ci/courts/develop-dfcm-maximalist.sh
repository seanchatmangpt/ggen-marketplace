#!/usr/bin/env bash
# Court develop-dfcm-maximalist -- migrated from .github/workflows/develop-dfcm-maximalist.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile reusable gates
echo "::group::develop-dfcm-maximalist: Compile reusable gates"
(
set -e
python3 -m compileall -q packs/dfcm-develop-maximalist-pack/gates
)
echo "::endgroup::"
# --- Refuse ambient DO
echo "::group::develop-dfcm-maximalist: Refuse ambient DO"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/dfcm-develop-maximalist-pack/gates
)
echo "::endgroup::"
