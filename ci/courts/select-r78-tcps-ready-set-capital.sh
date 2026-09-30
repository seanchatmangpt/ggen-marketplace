#!/usr/bin/env bash
# Court select-r78-tcps-ready-set-capital -- migrated from .github/workflows/select-r78-tcps-ready-set-capital.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R78 TCPS ready-set court
echo "::group::select-r78-tcps-ready-set-capital: Execute R78 TCPS ready-set court"
(
set -e
python -m pytest -q packs/portfolio-epistemic-observability-pack/tests/test_r78_tcps_ready_set_capital.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::select-r78-tcps-ready-set-capital: Refuse ambient consequential actuation"
(
set -e
! grep -R -nE 'consequentialDo[[:space:]]+true.*inAdmissibleSet[[:space:]]+true|actuationPerformed[[:space:]]+true' packs/portfolio-epistemic-observability-pack/ontology.r78-tcps-ready-set-capital.ttl packs/portfolio-epistemic-observability-pack/fixtures/r78-tcps-ready-set-capital.ttl
)
echo "::endgroup::"
