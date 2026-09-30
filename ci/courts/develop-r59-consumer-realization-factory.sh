#!/usr/bin/env bash
# Court develop-r59-consumer-realization-factory -- migrated from .github/workflows/develop-r59-consumer-realization-factory.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Enforce sparse generation contract
echo "::group::develop-r59-consumer-realization-factory: Enforce sparse generation contract"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_sparse_generation_contract.py
)
echo "::endgroup::"
# --- Execute R59 realization factory court
echo "::group::develop-r59-consumer-realization-factory: Execute R59 realization factory court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r59_consumer_realization_factory.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::develop-r59-consumer-realization-factory: Refuse ambient consequential actuation"
(
set -eo pipefail
set -euo pipefail
! grep -R -nE 'kubectl apply|terraform apply|aws .*create|gcloud .*create|az .*create' \
  packs/epistemic-sensor-factory-pack/queries/9??_r59_*.rq \
  packs/epistemic-sensor-factory-pack/tests/run_r59_consumer_realization_factory.py
)
echo "::endgroup::"
