#!/usr/bin/env bash
# Court aaif-deployment -- pay-before-manufacture deployer court.
# Runs tests/test_aaif_deployment_court.py: refusal ladder, live-sim kind rail,
# paid-delivery receipt chain, byte-identical replay. Pure verification from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
echo "::group::aaif-deployment: pytest court"
python3 -m pytest tests/test_aaif_deployment_court.py -q
echo "::endgroup::"
