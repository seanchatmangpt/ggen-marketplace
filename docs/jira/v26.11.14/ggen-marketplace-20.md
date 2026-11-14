# ggen-marketplace-20

Standing: UNVERIFIED

Title: Cost and ops budget gate for pack consumers on fnox hosting

## Problem

fnox hosting is authored with budget Terraform
(`/Users/sac/fnox/infra/gcp/budget/variables.tf` modified, uncommitted) but nothing
ties pack consumers (`/Users/sac/ggen-marketplace/docs/pack-consumer-contract.md`) to a cost or ops
  ceiling.
Observed pre-existing failures that a hosted registry would inherit: arcus
`gcp_emulator`/`sdlc` tests (HCL_UNSUPPORTED, nil deref at `sdlc_test.go:153`), and the
fnox e2e test fixes are not yet receipted.

## Acceptance

- Command: `grep -n "budget" /Users/sac/ggen-marketplace/docs/pack-consumer-contract.md`
- Expected: >= 1 match naming a ceiling and a gate command; a receipt in
  `/Users/sac/ggen-marketplace/receipts/` records the arcus failures as pre-existing.

## Falsifier

A consumer exceeding the stated ceiling is admitted by the gate.

## Owned files

- `/Users/sac/ggen-marketplace/docs/pack-consumer-contract.md`
- `/Users/sac/ggen-marketplace/receipts/`

## Depends-on

- ggen-marketplace-18

## Size

M

## References (path : LOC)

- /Users/sac/ggen-marketplace/docs/pack-consumer-contract.md : 153 lines
- /Users/sac/ggen-marketplace/receipts/ : 188 files, 7299 lines total (arcus pre-existing-failure
  receipt NEW, est. LOC: 40, basis: 2 failures + SHA/command/exit)
- /Users/sac/fnox/infra/gcp/budget/variables.tf : 38 lines

## Result

Standing: UNVERIFIED (no execution observed)
Files: /Users/sac/ggen-marketplace/docs/pack-consumer-contract.md (+~13 LOC budget section),
/Users/sac/ggen-marketplace/receipts/arcus-preexisting-failures-2026-11-14.md (new, ~22 LOC).
Acceptance: `grep -n "budget" /Users/sac/ggen-marketplace/docs/pack-consumer-contract.md`
