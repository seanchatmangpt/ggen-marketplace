# ggen-marketplace-12 AWS/Azure/GCP parity receipts court

Standing: UNVERIFIED

## Problem

AWS and Azure parity claims lack receipts (observed this session: arcus emulator go tests
pass, smalt gcp/aws 76 passed; arcus gcp_emulator/sdlc failing HCL_UNSUPPORTED and nil deref
at sdlc_test.go:153). `/Users/sac/fnox/docs/HYPERSCALER_PARITY.md` is untracked. No pack in
`/Users/sac/ggen-marketplace/packs/` is an aws dialect pack, and no court maps parity cells to
  receipts.

## Acceptance

`python3 /Users/sac/ggen-marketplace/scripts/check_parity_receipts.py` exits 1 listing each
  aws/azure/gcp cell with no
receipt as MISSING, 0 only when every cell is pass or registered-divergence.

## Falsifier

A cell with no receipt is reported as pass.

## Owned files

`/Users/sac/ggen-marketplace/scripts/check_parity_receipts.py`,
`/Users/sac/ggen-marketplace/receipts/parity-receipts-index.md`

## Depends-on

ggen-marketplace-09, ggen-marketplace-10 (/Users/sac/ggen-marketplace/docs/jira/v26.11.14/)

## Size

L

## References (path : LOC)

- /Users/sac/ggen-marketplace/scripts/check_parity_receipts.py : NEW (0 lines, to be created; est.
  LOC: 120, basis: parse 42-line matrix + receipt lookup + exit logic)
- /Users/sac/ggen-marketplace/receipts/parity-receipts-index.md : NEW (0 lines, to be created; est.
  LOC: 40, basis: one row per parity cell, ~23 PASS-UNRECEIPTED + 9 PASS)
- /Users/sac/fnox/docs/HYPERSCALER_PARITY.md : 42 lines
- /Users/sac/fnox/scripts/hyperscaler_parity.py : 200 lines
- /Users/sac/ggen-marketplace/packs/ : pack dir (cited, no count owned)

## Result

Standing: UNVERIFIED (authored; one read-only run observed, see below)

Files:
- /Users/sac/ggen-marketplace/scripts/check_parity_receipts.py (~100 LOC)
- /Users/sac/ggen-marketplace/receipts/parity-receipts-index.md (~25 LOC)

Behavior: parses matrix cells; REGISTERED-DIVERGENCE with KD id passes; PASS passes only with an
index row whose receipt JSON exists with standing PASS; everything else (PASS-UNRECEIPTED,
MISSING, FAIL, unindexed PASS) prints MISSING and exits 1.

Acceptance command: `python3 /Users/sac/ggen-marketplace/scripts/check_parity_receipts.py`
(expected exit 1 while 27 cells lack receipts).

## Repair (W9-16)

Standing: UNVERIFIED (edited, not executed)
- Audit HIGH/MED fixed: parity court resolves KD ids against arcus/smalt registers
  (check_parity_receipts.py); arcus gap court requires UNIMPLEMENTED or NOT_FOUND "no such route"
  (observability_gap_test.go) and KD-GA6-1/2 rows refreshed; smalt KD-ARCUS-02 row reworded to
  observed facts. Coordinator reruns: the parity-receipts script, the arcus gcp_emulator Gap test, smalt sdk_coverage.
