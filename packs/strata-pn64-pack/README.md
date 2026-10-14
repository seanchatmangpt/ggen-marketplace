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

## Resolved: stale VERB_COUNT assertion

The template's self-test hardcodes `assert_eq!(VERB_COUNT, 6)` while the
ontology (widened in 33f6705/0dba165 to `DaoAckDelegation` 2048/0) projects
25 verbs, so the generated test failed on a fresh projection. Resolved
2026-10-14: the test now renders `assert_eq!(VERB_COUNT, {{ results | length }})`
and the `TRANSITIONS` array length is likewise projected. Two six-net
deadlock fixtures (which the ungated opcode-12 `DivisionOfAssembly` made
vacuous over `TRANSITIONS`) now court `has_deadlock_excluding` on explicit
local six-net tables. All 7 generated tests pass.

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only. Projected ABI constants are not a verified Petri-net execution engine on any runtime.
