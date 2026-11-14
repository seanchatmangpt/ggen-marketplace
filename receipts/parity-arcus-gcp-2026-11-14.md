# Parity Receipt: arcus gcp

Standing: UNVERIFIED

## Identity

- project: arcus (/Users/sac/arcus)
- provider: gcp
- SHA: 1a9bb0b330f605a7de1a96dbbae8d51f366562ec (read from .git main ref on 2026-11-14)
- ticket: ggen-marketplace-13

## Command

`cd /Users/sac/arcus && go test ./internal/gcp_emulator/...`

- exit code: NOT RECORDED (author lane cannot execute builds/tests)
- observation: operator session reported green (ticket ggen-marketplace-13); output not stored

## Consequence

Cells for arcus/gcp stay PASS-UNRECEIPTED in `hyperscaler_parity.py` until the coordinator
re-runs the command at the SHA above, records the exit code here, flips Standing to PASS, and
writes the matching JSON under `/Users/sac/fnox/receipts/parity/` (the script's receipt dir).

## Falsifier

Command exits non-zero at the cited SHA.
