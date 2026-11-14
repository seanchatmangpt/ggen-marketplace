# ggen-marketplace-07 fibo pack and parity receipts

Standing: UNVERIFIED

## Problem

fnox has a FIBO surface (`/Users/sac/fnox/fibo/` with `map.rq`, `exhaustion_register.ttl`,
`CONTRACT.md`, `/Users/sac/ggen-marketplace/receipts/`) and `fibo/ggen.toml`, but `ls packs | grep
-i fibo` finds no
registry pack, so consumers cannot depend on it. `HYPERSCALER_PARITY.md` totals show
PASS-UNRECEIPTED 23 vs PASS 9: parity claims lack pack-level receipts.

## Acceptance

- `ls /Users/sac/ggen-marketplace/packs/fibo-pack/pack.toml` exists, ontology and query
  derived from `/Users/sac/fnox/fibo/map.rq` and `exhaustion_register.ttl`.
- A `/Users/sac/ggen-marketplace/receipts/` file per parity cell promoted from PASS-UNRECEIPTED,
  each with a Standing line.

## Falsifier

A pack receipt is cited for a cell while the underlying test (e.g. smalt test/aws) fails, or
the pack ships without a consumer contract naming fnox.

## Owned files

- /Users/sac/ggen-marketplace/packs/fibo-pack/** (new)
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-07.md

## Depends-on

ggen-marketplace-05, ggen-marketplace-06

## Size

M

## References (path : LOC)

- /Users/sac/fnox/fibo/map.rq : 19 lines
- /Users/sac/fnox/fibo/exhaustion_register.ttl : 81 lines
- /Users/sac/fnox/fibo/CONTRACT.md : 26 lines
- /Users/sac/fnox/fibo/ggen.toml : 24 lines
- /Users/sac/fnox/fibo/ : 66 files (receipts/ : 19 files)
- /Users/sac/fnox/docs/HYPERSCALER_PARITY.md : 42 lines
- /Users/sac/ggen-marketplace/packs/fibo-pack/ : NEW (0 lines, to be created; est. LOC: ~250;
  basis: map.rq+register+contract+toml total 150 lines, plus pack.toml and STANDING)
- /Users/sac/ggen-marketplace/receipts/ : NEW (0 lines, to be created; est. LOC: ~40 per promoted
  cell; basis: one receipt per PASS-UNRECEIPTED cell, up to 23)
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-07.md : 50 lines

## Result

Standing: UNVERIFIED

Files (new, /Users/sac/ggen-marketplace/packs/fibo-pack/): pack.toml, ggen.toml, STANDING,
CONSUMER_CONTRACT.md (names fnox), queries/map.rq, templates/fibo_map.py.tmpl,
ontology/walkthrough-fibo.ttl, ontology/exhaustion_register.ttl (copies of fnox sources).
Parity-cell receipts: BLOCKED (receipts/ not owned; underlying tests not observed passing).
Acceptance: ls /Users/sac/ggen-marketplace/packs/fibo-pack/pack.toml, then run the ggen sync in that dir.
