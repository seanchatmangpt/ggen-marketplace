#!/usr/bin/env bash
# xaas-ash-build-all.sh -- master runner. Executes all 5 real, verified parts
# of the XaaS Ash platform build in order. See README.md for full provenance
# and the honest command count (196 real core-project commands, 217 total
# including cross-cutting ecosystem installs -- see "On the 200+ command
# target" in README.md for why padding further would mean fabricating
# commands against a 44-capability ontology).
set -euo pipefail
cd "$(dirname "$0")"

echo "############################################"
echo "# Part 1: base domains/resources (52 mix commands)"
echo "############################################"
bash xaas-ash-build-base.sh

echo "############################################"
echo "# Part 2: ecosystem package installs (21 mix commands, cross-cutting)"
echo "############################################"
bash xaas-ash-build-ecosystem.sh

echo "############################################"
echo "# Part 3: per-resource extension upgrade (49 mix commands)"
echo "############################################"
bash xaas-ash-build-extend.sh

echo "############################################"
echo "# Part 4: per-resource change/validation modules (89 mix commands)"
echo "############################################"
bash xaas-ash-build-changes.sh

echo "############################################"
echo "# Part 5: project-wide finishing pass (6 mix commands)"
echo "############################################"
bash xaas-ash-build-finishing.sh

echo "############################################"
echo "# ALL PARTS COMPLETE -- 217 real mix commands run (196 core + 21 ecosystem)"
echo "############################################"
