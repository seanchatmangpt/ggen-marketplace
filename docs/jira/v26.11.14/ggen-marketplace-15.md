# ggen-marketplace-15

Standing: UNVERIFIED

## Problem

Pack standing is almost entirely unrecorded. `/Users/sac/ggen-marketplace/packs/` holds 358 packs;
  only two carry a
`STANDING.md` (`packs/azure-terraform-pack/STANDING.md`,
`packs/ma-case-study-pack/STANDING.md`) and six carry `/Users/sac/ggen-marketplace/receipts/`. The
  cloud-dialect packs
`azure-terraform-pack` and `gcp-marketplace-saas-pack` (no STANDING.md, only
`/Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/docs/REAL_API_ALIGNMENT.md`) have no
  standing line; no aws-dialect, fibo, or parity pack
exists under `/Users/sac/ggen-marketplace/packs/` (checked by listing). Consumers cannot tell what
  is verified.

Title: add Standing records for the azure and gcp dialect packs.

## Acceptance

- `test -f /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/STANDING.md` exits 0.
- `grep -m1 "^Standing:"
  /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/STANDING.md
  /Users/sac/ggen-marketplace/packs/azure-terraform-pack/STANDING.md` prints
  a value from the closed standing vocabulary for both.

## Falsifier

A Standing value is ALIVE or PASS without a cited command, exit code, and SHA in the file.

## Owned files

- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/STANDING.md (new)
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/STANDING.md (Standing line only)

## Depends-on

ggen-marketplace-13.

## Size

S

## References (path : LOC)

- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/STANDING.md : NEW (0 lines, to be
  created; est. LOC: 100, basis: azure-terraform-pack/STANDING.md is 142,
  ma-case-study-pack/STANDING.md is 125; shorter pack)
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/STANDING.md : 142 lines
- /Users/sac/ggen-marketplace/packs/ma-case-study-pack/STANDING.md : 125 lines
- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/docs/REAL_API_ALIGNMENT.md : 63 lines

## Result

Standing: UNVERIFIED

- gcp-marketplace-saas-pack/STANDING.md already existed (59 LOC, `Standing: UNVERIFIED`); unchanged.
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/STANDING.md: inserted `Standing: UNVERIFIED`
  after the H1 (+2 LOC). No ALIVE/PASS claimed (no observed execution).
- Acceptance: `test -f /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/STANDING.md && grep -m1 "^Standing:" /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/STANDING.md /Users/sac/ggen-marketplace/packs/azure-terraform-pack/STANDING.md`
