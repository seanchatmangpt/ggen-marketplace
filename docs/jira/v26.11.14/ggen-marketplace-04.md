# ggen-marketplace-04

Standing: UNVERIFIED

Title: fnox.io registry hosting authored but undeployed and unreferenced

## Problem

fnox.io hosting of the registry is authored but not deployed, and registration is
pending ACTIVE (observed this session). `grep -rl fnox` over `*.md`, `*.toml`, `*.json`
in this repo returns no file, so `/Users/sac/ggen-marketplace/marketplace.toml` and
`/Users/sac/ggen-marketplace/marketplace.active.toml` carry
no fnox.io registry endpoint. The hosting artifacts live in `/Users/sac/fnox`
(`/Users/sac/fnox/infra/gcp/edge/`,
`/Users/sac/fnox/justfile.d/99-fnox-io.just`), untracked at session start.

## Acceptance

- `grep -n "fnox.io" /Users/sac/ggen-marketplace/marketplace.toml` returns the registry endpoint
  entry.
- `curl -sI https://fnox.io/` returns an HTTP status line, recorded in a receipt
  `/Users/sac/ggen-marketplace/receipts/fnox-io-hosting-<date>.md` with a `Standing:` line (PASS
only when the
  registration is ACTIVE; otherwise BLOCKED naming the pending state).

## Falsifier

A receipt claiming PASS while `curl` fails or the registration is not ACTIVE.

## Owned files

- /Users/sac/ggen-marketplace/marketplace.toml
- /Users/sac/ggen-marketplace/receipts/fnox-io-hosting-<date>.md (new)

## Depends-on

fnox.io registration reaching ACTIVE (external).

## Size

M

## References (path : LOC)

- /Users/sac/ggen-marketplace/marketplace.toml : 62 lines
- /Users/sac/ggen-marketplace/marketplace.active.toml : 67 lines
- /Users/sac/fnox/infra/gcp/edge/ : 4 files, 247 lines total (excl .terraform)
- /Users/sac/fnox/justfile.d/99-fnox-io.just : 30 lines
- /Users/sac/ggen-marketplace/receipts/fnox-io-hosting-<date>.md : NEW (0 lines, to be created;
  est. LOC: ~40; basis: typical receipt with SHA, URL, curl output)

## Result

Standing: PARTIAL (BLOCKED receipt; registration pending ACTIVE)

Files: /Users/sac/ggen-marketplace/marketplace.toml (+7 LOC),
/Users/sac/ggen-marketplace/receipts/fnox-io-hosting-2026-11-14.md (new, ~15 LOC)

Acceptance: `grep -n "fnox.io" /Users/sac/ggen-marketplace/marketplace.toml; curl -sI -m 10 https://fnox.io/; echo rc=$?`
