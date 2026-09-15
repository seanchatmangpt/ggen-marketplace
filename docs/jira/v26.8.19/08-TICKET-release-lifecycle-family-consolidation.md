# 08 Ticket Release Lifecycle Family Consolidation

**v3 correction (2026-09-14):** `scripts/consolidation_court.py` was corrected a second time (v2→v3) after direct measurement showed v2's "shared vocabulary" signal was inflated by generic RDF/RDFS/OWL/XSD meta-vocabulary (Class, Property, domain, range, label, comment, ...) that any two hand-authored `ontology.ttl` files share regardless of real domain overlap. Re-run under v3: **PARTIAL, 5/28 pairs share real vocabulary (was 16/28 under v2 -- 11 of those 16 pairs' overlap was purely generic RDF/RDFS/OWL boilerplate).** See `../README.md`'s v2→v3 correction section for the full cross-family comparison and methodology.

Standing: PARTIAL_ALIVE — court run complete (v2 methodology). Real vocabulary-level correspondence found for at least one family; physical-merge phase NOT started (ticket 03 item 4, real consumer-boundary check against a live ggen runtime, has not been run).

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

## Outcome (court run complete, v2 methodology)

The consolidation court was re-run using `scripts/consolidation_court.py` **v2**. v1 (the original run) diffed ontologies as raw (s,p,o) triples and returned `REFUTED` for every family in this milestone (0/9 admitted) — that was found to be a methodology defect, not a real finding: every pack mints its own RDF namespace and embeds pack-specific instance data (literal source text, per-crate case names), so raw triple equality gives `common=0` even between packs that share a real class/predicate vocabulary. v2 adds a namespace-stripped **vocabulary** diff (class/predicate local names) as the verdict-driving signal, with the old instance-triple diff kept and reported but no longer determining the verdict — see `scripts/consolidation_court.py`'s module docstring for the full methodology correction.

| Family | Kernel candidate | Verdict | Vocabulary-shared | Instance-conflicting | Report |
|---|---|---|---|---|---|
| `release-lifecycle` | `ggen-release-pack` | **PARTIAL** | 16/28 pairs share real vocabulary | 28/28 pairs instance-conflicting (expected, not a defect) | `docs/jira/v26.8.19/families/release-lifecycle-court-report.json` |

This is a genuine, differentiated finding — real shared vocabulary exists across most or all member-pack pairs, which v1's blanket-REFUTED result had obscured. **This does NOT authorize a physical merge yet.** Per `03-TICKET-consolidation-court-methodology.md`'s own acceptance criteria, item 4 (a real consumer project generated from the current pack vs. the proposed kernel+profile split, output diffed) is required before any physical change, and `consolidation_court.py` explicitly does not perform it (`consumer_boundary_check: null` in every report). This ticket's ADMITTED/PARTIAL verdict is therefore a genuine **candidate for a follow-up physical-merge ticket**, not a completed merge — the physical-change phase (kernel-pack creation, repointing members as profiles, real consumer diff) remains unscoped, un-started work, separate from this court-run ticket.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — release/CI/publication control family entry
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
- `docs/jira/v26.8.19/families/release-lifecycle-court-report.json` — real court report
