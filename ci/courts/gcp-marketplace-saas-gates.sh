#!/usr/bin/env bash
# Court gcp-marketplace-saas-gates -- executes the pack's SPARQL gates + witnesses.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python3 packs/gcp-marketplace-saas-pack/gates/run_gates.py --witnesses
python3 scripts/check_gate_witness_courts.py
