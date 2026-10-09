#!/bin/sh
# check_pin_freshness.sh -- pin-stability law (R62) enforcement gate.
#
# Law: an extractor change and its PIN-ROTATION-LEDGER update are ATOMIC --
# they must land in the SAME commit. This gate fails fast (before the fleet
# courts semaphore/courts) whenever scripts/gen_doc_surface.py's sha256 is
# not the ledger's current-row hash, so a rotation can never land without
# its ledger row.
#
# Ledger is the single pin authority; sibling receipts use the stable
# ledger reference form. Overridable for probing:
#   PIN_LEDGER=<path> check_pin_freshness.sh
# Exit 0 iff the current-row hash matches the live extractor.
set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXTRACTOR="$REPO_ROOT/scripts/gen_doc_surface.py"
PIN_LEDGER="${PIN_LEDGER:-$REPO_ROOT/docs/sjira/v26.10.8/PIN-ROTATION-LEDGER.md}"

REPAIR_MSG="update the ledger's current row in the SAME commit as the extractor change"

[ -f "$EXTRACTOR" ] || { echo "check_pin_freshness: extractor missing: $EXTRACTOR" >&2; exit 1; }
[ -f "$PIN_LEDGER" ] || { echo "check_pin_freshness: ledger missing: $PIN_LEDGER" >&2; exit 1; }

LIVE_HASH="$(shasum -a 256 "$EXTRACTOR" | awk '{print $1}')"

# Current row = the ledger row that names the current pin; historical hops
# live under "## Lineage" bullets, the current row is the one the ledger
# calls "(current)". Match the 64-hex hash on that row.
# "Current row" = a ledger line that both marks itself current and carries
# the 64-hex sha256. Historical hop bullets lack "current" so cannot pass.
if grep -i "current" "$PIN_LEDGER" 2>/dev/null | grep -q "$LIVE_HASH"; then
  echo "check_pin_freshness: OK $LIVE_HASH (ledger current)"
  exit 0
fi

echo "check_pin_freshness: STALE PIN -- extractor sha256 $LIVE_HASH not found in ledger current row: $REPAIR_MSG" >&2
exit 1
