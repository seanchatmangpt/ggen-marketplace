# 08 Ticket Release Lifecycle Family Consolidation

Standing: PARTIAL_ALIVE. **BLOCKED on ticket 03** — no physical merge until a family-consolidation proof exists for this family.

## Quick reference

- Proposed shape: one `release-lifecycle-pack` ontology with stages `PREPARE -> VERIFY -> DRY_RUN -> RELEASE_INTENT -> RELEASE -> POST_RELEASE`, with projections for ggen/chatman/cargo/GitHub targets.
- Member packs (real names, confirmed on disk): `packs/ggen-release-pack`, `packs/chatman-ecosystem-release-pack`, `packs/chatman-ecosystem-v26-9-1-release-gate`, `packs/dry-run-publish-pack`, `packs/post-release-pack`, `packs/cargo-cicd-pack`, `packs/github-actions-pack`, `packs/gh-actions-errc-pack`
- No single existing pack has been independently verified as already possessing the full proposed stage-machine ontology; this ticket schedules discovery of a kernel candidate as part of the court run, not a predetermined one.

## Scope

This family is the least individually-verified of the high-confidence groups in this milestone — no member pack's file contents were checked directly during the verification pass that seeded this milestone (only the family's naming cohesion was observed). The court run for this family must therefore also determine which member, if any, is the best kernel candidate, rather than assuming one.

Note `packs/chatman-ecosystem-v26-9-1-release-gate` is version-pinned in its own name (`v26-9-1`), which is a signal worth resolving explicitly: is it a `ReleaseControlPack` instance parameterized by version, or a one-off gate that should stay outside any kernel? The court's query/gate correspondence check should answer this directly.

## Acceptance criteria

1. Court report identifies a kernel candidate (or concludes none of the eight yet qualifies, in which case a new core pack may need to be proposed as a separate follow-up, out of scope for this ticket).
2. Court report evaluates each of the eight member packs against the proposed six-stage lifecycle vocabulary (`PREPARE/VERIFY/DRY_RUN/RELEASE_INTENT/RELEASE/POST_RELEASE`), naming which stage(s) each pack's gates/queries actually correspond to.
3. `chatman-ecosystem-v26-9-1-release-gate`'s version-pinning question (parameterized instance vs. standalone one-off) is explicitly resolved.
4. Real consumer generation output is diffed before/after any physical change for at least one release-flow-consuming project.
5. `python3 scripts/marketplace.py validate` and catalog determinism pass after any change.

## Falsifiers

- Any physical change made under this ticket without a cited court report is a process violation.
- If the court finds the eight packs' gate/query surfaces do not share a common stage vocabulary at all (e.g. `cargo-cicd-pack` and `github-actions-pack` encode CI mechanics with no release-stage semantics in common with `ggen-release-pack`), the family claim is `REFUTED` for those members and they remain standalone `CapabilityPack`s.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — release/CI/publication control family entry
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
