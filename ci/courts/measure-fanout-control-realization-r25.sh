#!/usr/bin/env bash
# Court measure-fanout-control-realization-r25 -- migrated from .github/workflows/measure-fanout-control-realization-r25.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Run permanent fanout controller courts
echo "::group::measure-fanout-control-realization-r25: Run permanent fanout controller courts"
(
set -e
python3 -m unittest discover -s packs/fanout-realization-controller-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Verify R25 measurement surface
echo "::group::measure-fanout-control-realization-r25: Verify R25 measurement surface"
(
set -e
test "$(find packs/fanout-realization-controller-pack/queries -name 'r25-*.rq' | wc -l)" -eq 40
test -f packs/fanout-realization-controller-pack/gates/03-control-realization-r25.rq
test -f packs/fanout-realization-controller-pack/control-realization-r25.ttl
test -f packs/fanout-realization-controller-pack/control-realization-r25-ledger.jsonl
grep -q 'fanout-control-realization-report-r25' packs/fanout-realization-controller-pack/ggen.toml
grep -q 'fanout-control-realization-court-r25' packs/fanout-realization-controller-pack/ggen.toml
grep -q 'http://www.w3.org/ns/dqv#' packs/fanout-realization-controller-pack/ontology.ttl
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-fanout-control-realization-r25: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|httpx\.(post|put|patch|delete)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/fanout-realization-controller-pack/tests packs/fanout-realization-controller-pack/templates
)
echo "::endgroup::"
