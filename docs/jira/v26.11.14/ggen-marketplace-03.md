# ggen-marketplace-03

Standing: UNVERIFIED

Title: AWS cloud dialect pack absent while parity claims AWS columns

## Problem

`ls packs | grep -i aws` matches nothing; the marketplace has `azure-terraform-pack` and
`gcp-marketplace-saas-pack` only. `/Users/sac/fnox/docs/HYPERSCALER_PARITY.md` carries
aws columns for smalt and arcus (e.g. smalt storage PASS, arcus storage
REGISTERED-DIVERGENCE KD-AW7) with no marketplace pack or receipt backing the AWS
dialect. Observed this session: arcus aws emulator go tests pass; smalt
`mix test test/gcp test/aws` 76 passed. Neither result is receipted in this repo.

## Acceptance

- `ls /Users/sac/ggen-marketplace/packs/aws-*/pack.toml` lists an AWS dialect pack with ontology
  and gates.
- `ls /Users/sac/ggen-marketplace/receipts/aws-parity-*.md` exists, citing exact SHAs and the
  observed arcus and
  smalt test counts, with a `Standing:` line.
- Every aws cell in the fnox parity matrix cites that receipt or a KD row.

## Falsifier

An aws PASS cell in the matrix whose cited receipt names no SHA or test output.

## Owned files

- /Users/sac/ggen-marketplace/packs/aws-*-pack/ (new)
- /Users/sac/ggen-marketplace/receipts/aws-parity-*.md (new)

## Depends-on

ggen-marketplace-01 (gate migration pattern).

## Size

L

## References (path : LOC)

- /Users/sac/fnox/docs/HYPERSCALER_PARITY.md : 42 lines
- /Users/sac/ggen-marketplace/packs/aws-*-pack/ : NEW (0 lines, to be created; est. LOC: ~400
  (ontology, gates, pack.toml, STANDING); basis: azure pack is 1649 lines incl. instances; AWS
  dialect pack scoped smaller)
- /Users/sac/ggen-marketplace/receipts/aws-parity-*.md : NEW (0 lines, to be created; est. LOC: ~60
  per receipt; basis: typical receipt with SHAs and test counts)
- /Users/sac/ggen-marketplace/packs/ : 359 entries (ls | wc -l)

## Result

Standing: UNVERIFIED

Files (new, all under /Users/sac/ggen-marketplace):
- packs/aws-cloud-dialect-pack/pack.toml (~10 LOC)
- packs/aws-cloud-dialect-pack/ontology.ttl (~70 LOC)
- packs/aws-cloud-dialect-pack/gates/010_cell_integrity.rq (~18 LOC)
- packs/aws-cloud-dialect-pack/gates/020_service_coverage.rq (~9 LOC)
- packs/aws-cloud-dialect-pack/STANDING.md (~9 LOC)
- receipts/aws-parity-2026-11-14.md (~35 LOC)

Not done: fnox matrix aws cells citing the receipt (generated file, not owned; the generator
scripts/hyperscaler_parity.py must emit the citation). Arcus test count unrecorded.

Acceptance: ls /Users/sac/ggen-marketplace/packs/aws-*/pack.toml /Users/sac/ggen-marketplace/receipts/aws-parity-*.md
then run the two gates over ontology.ttl and re-run the arcus and smalt aws tests to fill the receipt.
