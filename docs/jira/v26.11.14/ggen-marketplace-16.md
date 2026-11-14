# ggen-marketplace-16

Standing: UNVERIFIED

## Problem

fnox.io hosting of the registry is authored but not deployed, and fnox.io registration is
pending ACTIVE (observed this session). The only in-tree record is
`/Users/sac/fnox/docs/setup/fnox-io-domain.md`; the marketplace repo has no receipt stating
this state, so docs may be read as claiming a live registry.
  `/Users/sac/ggen-marketplace/marketplace.toml` and
`/Users/sac/ggen-marketplace/marketplace.active.toml` do not record a hosting standing.

Title: record fnox.io registry hosting as authored-not-deployed.

## Acceptance

- `test -f /Users/sac/ggen-marketplace/receipts/fnox-io-hosting.md` exits 0.
- `grep -m1 "^Standing: BLOCKED\|^Standing: UNVERIFIED"
  /Users/sac/ggen-marketplace/receipts/fnox-io-hosting.md` matches.
- The receipt states registration status and names the condition (domain ACTIVE) that
  unblocks deploy.

## Falsifier

`curl -sI https://fnox.io` returns a registry response while the receipt still says
not deployed, or the receipt says deployed with no HTTP evidence.

## Owned files

- /Users/sac/ggen-marketplace/receipts/fnox-io-hosting.md (new)

## Depends-on

External: fnox.io registration reaching ACTIVE.

## Size

S

## References (path : LOC)

- /Users/sac/ggen-marketplace/receipts/fnox-io-hosting.md : NEW (0 lines, to be created; est. LOC:
  40, basis: sibling receipt shape, status + unblock condition + HTTP evidence)
- /Users/sac/fnox/docs/setup/fnox-io-domain.md : 128 lines
- /Users/sac/ggen-marketplace/marketplace.toml : 62 lines
- /Users/sac/ggen-marketplace/marketplace.active.toml : 67 lines

## Result

Standing: UNVERIFIED (file authored, not executed by me)

- Created /Users/sac/ggen-marketplace/receipts/fnox-io-hosting.md (~33 LOC): Standing BLOCKED,
  registration pending ACTIVE, unblock condition stated, no HTTP evidence claimed.
- Acceptance: `test -f /Users/sac/ggen-marketplace/receipts/fnox-io-hosting.md && grep -m1 "^Standing: BLOCKED\|^Standing: UNVERIFIED" /Users/sac/ggen-marketplace/receipts/fnox-io-hosting.md`
