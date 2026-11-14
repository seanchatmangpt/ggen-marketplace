# Azure and AWS Parity Cells Receipt 2026-11-14

Standing: UNVERIFIED

## Subject

PASS-UNRECEIPTED cells in `/Users/sac/fnox/docs/HYPERSCALER_PARITY.md` for the azure and aws
columns (smalt and arcus rows). Gate: `python3 /Users/sac/fnox/scripts/hyperscaler_parity.py --check`.

## Observed

- The gate reads receipts only from `/Users/sac/fnox/receipts/parity/<repo>-<cloud>-<service>.json`
  with `"standing":"PASS"`. A markdown receipt here does not move any cell.
- Pack evidence: `packs/azure-terraform-pack`, `packs/typer-azure-pack`. No AWS terraform pack
  exists (only `azure-terraform-pack` and `gh-terraform-pack`); aws cells cite
  `receipts/aws-parity-2026-11-14.md` (PARTIAL).
- No gate or test command was executed by this lane (build/test hooks blocked).

## Not claimed

No cell is marked PASS by this receipt. Moving a cell requires the coordinator to run the
arcus/smalt test suites, then write the fnox JSON receipt citing this file.

## Falsifier

A cell is PASS while its cited receipt is absent or predates its test file.

## Replay

`python3 /Users/sac/fnox/scripts/hyperscaler_parity.py --check` (expect exit 1 until JSON receipts
land for the remaining PASS-UNRECEIPTED cells).

## See Also

- `receipts/aws-parity-2026-11-14.md`
- `packs/azure-terraform-pack/STANDING.md`
