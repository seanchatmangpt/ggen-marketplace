# Parity Receipt: smalt azure

Standing: UNVERIFIED

## Identity

- project: smalt (/Users/sac/smalt)
- provider: azure
- SHA: d22a1c80f625d970509162a257af0227d58b0fe4 (read from .git main ref on 2026-11-14)
- ticket: ggen-marketplace-13

## Command

`cd /Users/sac/smalt && mix test test/data_plane test/identity test/monitor`

- exit code: NOT RECORDED (author lane cannot execute builds/tests)
- observation: no green run observed this session; command is a proposal, include real azure test paths

## Consequence

Cells for smalt/azure stay PASS-UNRECEIPTED in `hyperscaler_parity.py` until the coordinator
re-runs the command at the SHA above, records the exit code here, flips Standing to PASS, and
writes the matching JSON under `/Users/sac/fnox/receipts/parity/` (the script's receipt dir).

## Falsifier

Command exits non-zero at the cited SHA.
