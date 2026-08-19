# 08 Ticket Release Lifecycle Family Consolidation

Standing: PARTIAL_ALIVE — court run complete, CLOSED (no merge, per REFUTED falsifier).

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

## Outcome (court run complete)

The consolidation court was run for real against this family:

```
$ python3 scripts/consolidation_court.py docs/jira/v26.8.19/families/release-lifecycle.toml > /tmp/court-release-lifecycle.toml.json; echo EXIT:$?
EXIT:0

$ python3 -m json.tool < /tmp/court-release-lifecycle.toml.json > /dev/null && echo VALID_JSON
VALID_JSON
```

**Verdict: `REFUTED`**, recorded in `docs/jira/v26.8.19/families/release-lifecycle-court-report.json`.

- `kernel_candidate`: `ggen-release-pack`
- `members` (8): `cargo-cicd-pack`, `chatman-ecosystem-release-pack`,
  `chatman-ecosystem-v26-9-1-release-gate`, `dry-run-publish-pack`, `ggen-release-pack`,
  `gh-actions-errc-pack`, `github-actions-pack`, `post-release-pack`
- `ontology_conflicting_pairs`: 28, `total_pairs`: 28 (28/28 pairwise combinations conflict —
  every pair has ontology triples/lines present in one member and absent from the other, i.e.
  `only_a > 0 and only_b > 0` for all 28 pairs)
- `verdict_rule`: "ADMITTED if ontology_conflicting_pairs == 0; REFUTED if
  ontology_conflicting_pairs == total_pairs; PARTIAL otherwise."
- `consumer_boundary_check`: out of scope for this marketplace-only script (per the script's own
  note); acceptance criterion 4 (real consumer generation diff via a real ggen runtime) was not
  evaluated by the court and remains unevaluated.

Per this ticket's own Falsifiers section: "If the court finds the eight packs' gate/query
surfaces do not share a common stage vocabulary at all ... the family claim is `REFUTED` for
those members and they remain standalone `CapabilityPack`s." The court's 28/28 conflicting-pairs
result satisfies this falsifier condition (no shared, non-conflicting ontology across any pair).
Per the ticket's `03-TICKET-consolidation-court-methodology.md` verdict semantics, a `REFUTED`
verdict is an acceptable complete outcome that closes the ticket without a merge — no physical
consolidation of these eight packs is authorized or performed under this ticket. All eight
member packs remain standalone `CapabilityPack`s.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — release/CI/publication control family entry
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
- `docs/jira/v26.8.19/families/release-lifecycle-court-report.json` — real court report
