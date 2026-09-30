#!/usr/bin/env bash
# Court develop-r73-revalidation-manufacturing -- migrated from .github/workflows/develop-r73-revalidation-manufacturing.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute all R73 semantic courts
echo "::group::develop-r73-revalidation-manufacturing: Execute all R73 semantic courts"
(
set -e
python packs/revalidation-manufacturing-capital-pack/court.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::develop-r73-revalidation-manufacturing: Refuse ambient consequential actuation"
(
set -e
! grep -R -E 'kubectl apply|terraform apply|aws .*create|gcloud .*create|az .*create' packs/revalidation-manufacturing-capital-pack
)
echo "::endgroup::"
