# strata-pn64-pack

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

PN64/OCEL64 dual-word ABI for Strata: one Petri-net transition per 64-bit word (marking/W-/W+/tid/flags fields) plus the six canonical RONR procedural transitions as pre/post place masks, projected as a Rust module of `pub const` values.

## Capability surface

```bash
$ ggen pack capabilities strata-pn64-pack
```

## Companion templates

The comment-only `templates/README.tmpl` companions are REQUIRED for consumers
on ggen older than 8bb154627 (pre-26.10.11): those builds resolve only
`templates/*.tmpl` (FM-PACK-005) and refuse `.tera`-only packs. Do not retire
them for pre-fix consumers; ggen >= 8bb154627 resolves `.tera` natively.

## Known defect: stale VERB_COUNT assertion

The template's self-test (`templates/pn64_masks.rs.tera:139`) hardcodes
`assert_eq!(VERB_COUNT, 6)` while the ontology projects 25 verbs
(`VERB_COUNT = {{ results | length }}` = 25 in `generated/pn64_masks.rs:17`),
so the generated test is stale and fails on a fresh projection. Fix belongs in
the template, not the generated file. Flagged by two lanes.

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only. Projected ABI constants are not a verified Petri-net execution engine on any runtime.
