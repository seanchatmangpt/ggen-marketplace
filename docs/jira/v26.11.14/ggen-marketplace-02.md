# ggen-marketplace-02

Standing: UNVERIFIED

Title: gcp-marketplace-saas-pack gate and standing receipts

## Problem

`/Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/` ships
`gates/010_event_transitions.rq`,
`020_entitlement_states.rq`, `030_codegen.rq` and templates, but no `STANDING.md`, no
`instances/`, and no pack receipt (compare
`/Users/sac/ggen-marketplace/packs/azure-terraform-pack/STANDING.md`).
Mixed `.ex.tmpl` / `.eex` template suffixes are unexplained.
`/Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/docs/REAL_API_ALIGNMENT.md`
is the only claim surface and carries no observed gate output. The fnox parity matrix
(`/Users/sac/fnox/docs/HYPERSCALER_PARITY.md`) shows 23 PASS-UNRECEIPTED cells, the
same missing-receipt class.

## Acceptance

- `ls /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/STANDING.md` exists, with a
  `Standing:` line from
  the closed vocabulary and observed output of all three gates.
- A scratch consumer `ggen sync run` exits 0 and renders every template.
- Each gate returns a non-empty result on a mutated ontology (non-vacuity).

## Falsifier

A gate that returns identical output on a mutated ontology and the original.

## Owned files

- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/STANDING.md (new)
- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/gates/
- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/templates/

## Depends-on

None.

## Size

M

## References (path : LOC)

- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/STANDING.md : NEW (0 lines, to be
  created; est. LOC: ~100; basis: azure-terraform-pack/STANDING.md is 142 lines; smaller pack)
- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/gates/ : 3 files, 90 lines total
- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/templates/ : 5 files, 414 lines total
- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/ : 11 files, 777 lines total
- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/instances/ : NEW (0 lines, to be
  created; est. LOC: ~60; basis: assumed 1-2 instance .ttl files)
- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/docs/REAL_API_ALIGNMENT.md : 63 lines
- /Users/sac/ggen-marketplace/packs/azure-terraform-pack/STANDING.md : 142 lines
- /Users/sac/fnox/docs/HYPERSCALER_PARITY.md : 42 lines

## Result

Standing: UNVERIFIED (nothing executed; hook blocks ggen/build runs)

Files: /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/STANDING.md (new, ~70 LOC).
Gates and templates unchanged (gates already violation-polarity; suffix dialects documented).
instances/ not created (no grounded source).

Acceptance command: follow STANDING.md "Non-vacuity recipe" (gate on original = 0 rows, on each
mutation = non-empty) then scratch-consumer `ggen sync run` exit 0 rendering 5 templates.
