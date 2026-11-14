# ggen-marketplace-05 aws-terraform-pack missing

Standing: UNVERIFIED

## Problem

The registry has `/Users/sac/ggen-marketplace/packs/azure-terraform-pack` but no AWS counterpart:
`ls packs | grep -i aws`
returns nothing (observed this session). AWS parity claims in
`/Users/sac/fnox/docs/HYPERSCALER_PARITY.md` show arcus aws serverless-run MISSING and
several arcus aws cells REGISTERED-DIVERGENCE (KD-AW7, KD-AW8, KD-AW9, KD-AW12). Observed this
session: arcus aws emulator go tests pass and smalt `mix test test/aws` passes, but no pack
projects AWS Terraform from ontology.

## Acceptance

- `ls /Users/sac/ggen-marketplace/packs/aws-terraform-pack/pack.toml` exists, with
  `ontology.ttl`, `templates/`, `gates/`, `STANDING.md` mirroring azure-terraform-pack layout.
- `ggen sync run` twice in a scratch consumer yields byte-identical `.tf` output and a valid
  `ggen receipt verify`.

## Falsifier

Edit the ontology instance (region or resource attribute) and regenerated `.tf` does not
change, or a hand-edited `.tf` still passes the gate.

## Owned files

- /Users/sac/ggen-marketplace/packs/aws-terraform-pack/** (new)
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-05.md

## Depends-on

none (pattern source: /Users/sac/ggen-marketplace/packs/azure-terraform-pack)

## Size

M

## References (path : LOC)

- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/pack.toml : 10 lines
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/ : 14 files, 1649 lines total (pattern
  source)
- /Users/sac/fnox/docs/HYPERSCALER_PARITY.md : 42 lines
- /Users/sac/ggen-marketplace/packs/aws-terraform-pack/ : NEW (0 lines, to be created; est. LOC:
  ~900; basis: roughly half of azure-terraform-pack 1649 lines (14 files))
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-05.md : 48 lines

## Result

Standing: UNVERIFIED (authored only, no execution observed)

Files (new, /Users/sac/ggen-marketplace/packs/aws-terraform-pack/): pack.toml, ontology.ttl,
STANDING.md, gates/010_task_group.rq, gates/020_container.rq, gates/030_orphan.rq,
templates/{main,providers,variables,outputs}.tf.tmpl (~400 LOC total; no tftest/PDDL).

Acceptance (coordinator): `ls packs/aws-terraform-pack/pack.toml`; in a scratch consumer run
`ggen sync run` twice, sha256 deploy/aws/fnox-runner/*.tf identical, then `ggen receipt verify`.
