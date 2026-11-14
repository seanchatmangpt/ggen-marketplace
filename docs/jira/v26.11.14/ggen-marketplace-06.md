# ggen-marketplace-06 gcp-terraform-pack from fnox infra

Standing: UNVERIFIED

## Problem

GCP has only `/Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack` (commerce procurement
surface); no pack
generates the GCP Terraform dialect. The fnox repo carries hand-written modules at
`/Users/sac/fnox/infra/gcp/{iam,iap,edge,budget,cloudrun,gpu}` (uncommitted modifications and
untracked `.terraform/` dirs in git status). The arcus gcp_emulator has a pre-existing failure
(HCL_UNSUPPORTED) observed this session, so the dialect boundary is undocumented in the registry.

## Acceptance

- `ls /Users/sac/ggen-marketplace/packs/gcp-terraform-pack/pack.toml` exists with ontology
  facts for the six fnox modules, templates, and a gate listing unsupported HCL constructs.
- Scratch-consumer `ggen sync run` output diffed against
  `/Users/sac/fnox/infra/gcp/iam/main.tf` shows zero semantic differences or each difference
  is a registered divergence row.

## Falsifier

A construct arcus rejects with HCL_UNSUPPORTED is emitted by the pack without a divergence
row, or `.terraform/` artifacts are shipped inside the pack.

## Owned files

- /Users/sac/ggen-marketplace/packs/gcp-terraform-pack/** (new)
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-06.md

## Depends-on

ggen-marketplace-05 (shared dialect gate shape)

## Size

L

## References (path : LOC)

- /Users/sac/fnox/infra/gcp/iam/main.tf : 186 lines
- /Users/sac/fnox/infra/gcp/iam/ : 4 files, 294 lines total
- /Users/sac/fnox/infra/gcp/iap/ : 4 files, 226 lines total
- /Users/sac/fnox/infra/gcp/edge/ : 4 files, 247 lines total
- /Users/sac/fnox/infra/gcp/budget/ : 3 files, 119 lines total
- /Users/sac/fnox/infra/gcp/cloudrun/ : 4 files, 264 lines total
- /Users/sac/fnox/infra/gcp/gpu/ : 5 files, 341 lines total
  (counts exclude .terraform/ and .terraform.lock.hcl)
- /Users/sac/ggen-marketplace/packs/gcp-terraform-pack/ : NEW (0 lines, to be created; est. LOC:
  ~1000; basis: six fnox modules total 1491 lines of module files; pack templates+ontology+gate)
- /Users/sac/ggen-marketplace/docs/jira/v26.11.14/ggen-marketplace-06.md : 52 lines

## Result

Standing: UNVERIFIED (authored; nothing executed)

Files (all under /Users/sac/ggen-marketplace/packs/gcp-terraform-pack/): pack.toml, ontology.ttl
(~95 LOC; iam fully modelled, other five modules inventory-only), templates/iam_main.tf.tera,
templates/iam_preamble.tf.tera, gates/010_iam_resources.rq, gates/020_unsupported_hcl.rq,
docs/DIVERGENCES.md, STANDING.md. Divergence rows D-01..D-04, U-01..U-06 registered; iap/edge/
budget/cloudrun/gpu bodies are PARTIAL (D-04). No ggen manifest wired; sync output not diffed.

Acceptance: `ls /Users/sac/ggen-marketplace/packs/gcp-terraform-pack/pack.toml` then scratch
consumer `ggen sync run` and diff against /Users/sac/fnox/infra/gcp/iam/main.tf.
