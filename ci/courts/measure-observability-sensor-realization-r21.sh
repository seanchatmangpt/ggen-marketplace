#!/usr/bin/env bash
# Court measure-observability-sensor-realization-r21 -- migrated from .github/workflows/measure-observability-sensor-realization-r21.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Verify R21 sensor-realization surface
echo "::group::measure-observability-sensor-realization-r21: Verify R21 sensor-realization surface"
(
set -e
test -f packs/ggen-project-boundary-pack/gates/10-observability-sensor-realization.rq
test -f packs/ggen-project-boundary-pack/queries/r21-sensor-realization-frontier.rq
test -f packs/ggen-project-boundary-pack/templates/observability-sensor-realization.json.tera
test -f packs/ggen-project-boundary-pack/templates/observability-sensor-realization-court.py.tera
count=$(find packs/ggen-project-boundary-pack/queries -maxdepth 1 -name 'r21-*.rq' | wc -l)
test "$count" -ge 36
grep -q 'SensorRealizationRun' packs/ggen-project-boundary-pack/ontology.ttl
grep -q 'SensorPrecisionMetric' packs/ggen-project-boundary-pack/ontology.ttl
grep -q 'SensorRecallMetric' packs/ggen-project-boundary-pack/ontology.ttl
grep -q 'DiscoveryMultiplierMetric' packs/ggen-project-boundary-pack/ontology.ttl
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-observability-sensor-realization-r21: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/ggen-project-boundary-pack/templates/observability-sensor-realization* packs/ggen-project-boundary-pack/queries/r21-*.rq
)
echo "::endgroup::"
