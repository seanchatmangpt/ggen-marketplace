#!/usr/bin/env bash
# Court measure-generation-capability -- migrated from .github/workflows/measure-generation-capability.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Verify generation capability surface
echo "::group::measure-generation-capability: Verify generation capability surface"
(
set -e
test -f packs/dfcm-maximalist-court-pack/generation-capability.ttl
count=$(find packs/dfcm-maximalist-court-pack/queries -maxdepth 1 -name 'generation-capability-*.rq' | wc -l)
test "$count" -ge 30
grep -q 'GenerationCapabilityObservation' packs/dfcm-maximalist-court-pack/generation-capability.ttl
grep -Rqs 'capabilityActuationPerformed false' packs/dfcm-maximalist-court-pack/queries/generation-capability-*.rq
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-generation-capability: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/dfcm-maximalist-court-pack/generation-capability.ttl packs/dfcm-maximalist-court-pack/queries/generation-capability-*.rq
)
echo "::endgroup::"
