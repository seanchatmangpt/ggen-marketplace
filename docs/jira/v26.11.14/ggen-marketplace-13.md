# ggen-marketplace-13

Standing: UNVERIFIED

## Problem

The hyperscaler parity matrix reports many PASS-UNRECEIPTED cells (AWS/Azure/GCP across smalt
and arcus) and itself carries `Standing: UNVERIFIED`. Evidence:
`/Users/sac/fnox/docs/HYPERSCALER_PARITY.md` (e.g. smalt azure storage
`PASS-UNRECEIPTED [5i/10t]`; arcus gcp queue-pubsub `MISSING`). The marketplace repo has no
receipt under `/Users/sac/ggen-marketplace/receipts/` or `/Users/sac/ggen-marketplace/docs/jira/`
  that backs these cells. This session observed arcus
aws/azure/gcp emulator go tests pass and smalt `mix test test/gcp test/aws` 76 passed, but
none of that output is stored as a gate receipt.

Title: receipt the observed AWS/Azure/GCP emulator gate results.

## Acceptance

- `ls /Users/sac/ggen-marketplace/receipts/parity-*.md` lists one receipt per
  (project, provider) observed green, each with exact SHA, command, exit code.
- `python3 /Users/sac/fnox/scripts/hyperscaler_parity.py` shows those cells as PASS, not
  PASS-UNRECEIPTED.

## Falsifier

A receipt exists whose cited command, re-run at the cited SHA, exits non-zero; or a cell
flips to PASS with no receipt file on disk.

## Owned files

- /Users/sac/ggen-marketplace/receipts/parity-*.md (new)
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-13.md

## Depends-on

None (consumes /Users/sac/fnox/scripts/hyperscaler_parity.py as read-only).

## Size

M

## References (path : LOC)

- /Users/sac/fnox/docs/HYPERSCALER_PARITY.md : 42 lines
- /Users/sac/fnox/scripts/hyperscaler_parity.py : 200 lines
- /Users/sac/ggen-marketplace/receipts/ : 188 files, 7299 lines total (existing)
- /Users/sac/ggen-marketplace/receipts/parity-*.md : NEW (0 lines, to be created; est. LOC: 180,
  basis: ~6 receipts (3 providers x 2 projects) x ~30 lines)
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-13.md : 40 lines (before this
  annotation)

## Result

Standing: UNVERIFIED

- Added 6 receipts (~25 LOC each) at /Users/sac/ggen-marketplace/receipts/parity-{arcus,smalt}-{aws,azure,gcp}-2026-11-14.md, each with exact SHA and command; exit codes NOT recorded (no execution possible here).
- Gap: hyperscaler_parity.py reads JSON from /Users/sac/fnox/receipts/parity/, not these files; it will not flip cells to PASS until the coordinator writes those JSON files after real runs. smalt-azure command is a proposal.
- Acceptance: ls /Users/sac/ggen-marketplace/receipts/parity-*.md; run each command at its SHA, record exit, then python3 /Users/sac/fnox/scripts/hyperscaler_parity.py
