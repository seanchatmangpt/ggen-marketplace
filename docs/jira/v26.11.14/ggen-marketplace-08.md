# ggen-marketplace-08 fnox-io registry hosting deploy receipt

Standing: UNVERIFIED

## Problem

Hosting the registry at fnox.io is authored but not deployed, and fnox.io registration is
pending ACTIVE (observed this session). The registry has no receipt tying
`/Users/sac/ggen-marketplace/marketplace.toml` and
`/Users/sac/ggen-marketplace/marketplace.active.toml` to a served
endpoint, so `ggen` consumers cannot resolve packs from fnox.io. Authored hosting lives in
`/Users/sac/fnox/justfile.d/` and `/Users/sac/fnox/infra/gcp/edge`.

## Acceptance

- After registration is ACTIVE: `curl -fsS https://fnox.io/` returns 200 and a pack index
  whose pack count equals `ls /Users/sac/ggen-marketplace/packs | wc -l`.
- A receipt `/Users/sac/ggen-marketplace/receipts/fnox-io-hosting-<date>.md` records exact SHA,
  URL, and probe output.

## Falsifier

Index served from a stale SHA, or the receipt is written while the curl probe fails or the
registration status is not ACTIVE.

## Owned files

- /Users/sac/ggen-marketplace/receipts/fnox-io-hosting-*.md (new)
- /Users/sac/ggen-marketplace/marketplace.toml
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-08.md

## Depends-on

External: fnox.io registration ACTIVE; ggen-marketplace-07 optional

## Size

M

## References (path : LOC)

- /Users/sac/ggen-marketplace/marketplace.toml : 62 lines
- /Users/sac/ggen-marketplace/marketplace.active.toml : 67 lines
- /Users/sac/fnox/justfile.d/ : 36 files
- /Users/sac/fnox/justfile.d/99-fnox-io.just : 30 lines
- /Users/sac/fnox/infra/gcp/edge/ : 4 files, 247 lines total (excl .terraform)
- /Users/sac/ggen-marketplace/receipts/fnox-io-hosting-*.md : NEW (0 lines, to be created; est.
  LOC: ~40; basis: typical receipt with SHA, URL, probe output)
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-08.md : 49 lines

## Result

Standing: BLOCKED

- Observed this session: `ls /Users/sac/ggen-marketplace/packs | wc -l` = 361 at authoring (stale; 363 at re-audit, re-read at use time); `curl -sS -m 8 https://fnox.io/` http code 000 (no response).
- External dependency (fnox.io registration ACTIVE) is unmet, so no receipt `receipts/fnox-io-hosting-<date>.md` was written (writing one while the probe fails is the stated falsifier).
- Files changed: /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-08.md (+8 LOC). marketplace.toml not edited by this ticket (any working-tree modification is from another lane).
- Acceptance command (run after registration ACTIVE and deploy): `test "$(curl -fsS https://fnox.io/ | grep -c 'class="pack"'  # ASSUMPTION: adjust to real index markup after deploy)" = "$(ls /Users/sac/ggen-marketplace/packs | wc -l)"`, then write the receipt with `git -C /Users/sac/ggen-marketplace rev-parse HEAD`, URL, and probe output.

## Repair

W9-11: pack count marked stale (363 at re-audit); acceptance placeholder replaced by explicit assumption (BLOCKED until deploy); marketplace.toml claim attributed. Rerun: ls /Users/sac/ggen-marketplace/packs | wc -l
