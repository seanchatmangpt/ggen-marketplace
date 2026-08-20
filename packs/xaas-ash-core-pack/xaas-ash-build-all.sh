#!/usr/bin/env bash
# xaas-ash-build-all.sh -- master runner. Executes all 3 real, verified parts
# of the XaaS Ash platform build in order. See README.md for the full
# provenance and the honest count (120 real "mix" commands, not 200+ -- see
# "On the 200+ command target" in README.md for why padding further would
# mean fabricating commands against a 44-capability ontology).
set -euo pipefail
cd "$(dirname "$0")"

echo "############################################"
echo "# Part 1: base domains/resources (52 mix commands)"
echo "############################################"
bash xaas-ash-build-base.sh

echo "############################################"
echo "# Part 2: ecosystem package installs (19 mix commands)"
echo "############################################"
bash xaas-ash-build-ecosystem.sh

echo "############################################"
echo "# Part 3: per-resource extension upgrade (49 mix commands)"
echo "############################################"
bash xaas-ash-build-extend.sh

echo "############################################"
echo "# ALL PARTS COMPLETE -- 120 real mix commands run"
echo "############################################"
