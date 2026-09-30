#!/usr/bin/env bash
# Court implement-r60-realization-qualification -- migrated from .github/workflows/implement-r60-realization-qualification.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Enforce upstream sparse-generation contract
echo "::group::implement-r60-realization-qualification: Enforce upstream sparse-generation contract"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_sparse_generation_contract.py
)
echo "::endgroup::"
# --- Execute R59 producer court
echo "::group::implement-r60-realization-qualification: Execute R59 producer court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r59_consumer_realization_factory.py
)
echo "::endgroup::"
# --- Execute all R60 qualification courts
echo "::group::implement-r60-realization-qualification: Execute all R60 qualification courts"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r60_realization_qualification.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::implement-r60-realization-qualification: Refuse ambient consequential actuation"
(
set -eo pipefail
set -euo pipefail
! grep -R -nE 'kubectl apply|terraform apply|aws .*create|gcloud .*create|az .*create' \
  packs/epistemic-sensor-factory-pack/queries/10??_r60_*.rq \
  packs/epistemic-sensor-factory-pack/queries/1100_r60_*.rq \
  packs/epistemic-sensor-factory-pack/tests/run_r60_realization_qualification.py
)
echo "::endgroup::"
