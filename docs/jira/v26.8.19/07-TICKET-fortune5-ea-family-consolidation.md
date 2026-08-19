# 07 Ticket Fortune5 EA Family Consolidation

Standing: PARTIAL_ALIVE — court run complete, CLOSED (no merge, per REFUTED falsifier).

## Quick reference

- Proposed shape: `enterprise-architecture-core -> togaf-adm -> profiles{fortune5, github, chatman, self-play} -> concerns{required-capabilities, deployment-blocks, testing}`.
- Core candidate: `packs/fortune5-enterprise-architecture-pack` — **verified** to already contain `README.md`, `ontology.ttl`, `queries/010_architecture_surface.rq`, `shapes/fortune5-profile.shacl.ttl`, `gates/010_admission.rq`, `evidence/composition-contract.md` (checked directly, not inferred).
- Standard reference kept separate: `packs/togaf-adm-pack` (proposed `KEEP STANDARD`, not folded in — it likely represents the TOGAF ADM standard itself rather than a Fortune5-specific profile).
- Related/member packs (real names, confirmed on disk): `packs/fortune5-architecture-pack`, `packs/fortune5-deployment-blocks-pack`, `packs/fortune5-required-capabilities-pack`, `packs/fortune5-testing-bblock-pack`, `packs/enterprise-architecture-connection-pack`, `packs/gh-enterprise-architecture-pack`, `packs/chatman-togaf-closure-pack`, `packs/safe-ea-strategy-self-play-pack`

## Scope

`fortune5-enterprise-architecture-pack`'s file contents are independently verified to already resemble a mature core (ontology + queries + SHACL shapes + gates + evidence all present). Whether the other eight packs listed above are genuine profiles/concerns over that same ontology, or independent architecture authorities that happen to share vocabulary, is `INFERRED` and is exactly what ticket 03's court decides.

Note `packs/fortune5-architecture-pack` and `packs/fortune5-enterprise-architecture-pack` are two distinct, similarly-named directories on disk — the court run must explicitly resolve whether one is legacy/subset of the other (an overlap-review case, similar in kind to the `ggen-self-pack`/`ggen-self-host-pack` overlap noted elsewhere in the source audit) before proposing either as sole kernel.

## Acceptance criteria

1. Court report resolves the `fortune5-architecture-pack` vs `fortune5-enterprise-architecture-pack` naming overlap first — same-thing-different-name, superset/subset, or genuinely distinct — before any profile assignment is finalized.
2. Court report evaluates `fortune5-deployment-blocks-pack`, `fortune5-required-capabilities-pack`, `fortune5-testing-bblock-pack` as `concerns` (per the proposed shape) via query/template correspondence against the core.
3. Court report evaluates `enterprise-architecture-connection-pack`, `gh-enterprise-architecture-pack`, `chatman-togaf-closure-pack`, `safe-ea-strategy-self-play-pack` as candidate `profiles` (github/chatman/self-play framing) rather than assumed to fit that framing.
4. `togaf-adm-pack` is confirmed to remain standalone (standard reference, not a profile) unless the court's ontology diff shows otherwise.
5. Real consumer generation output is diffed before/after any physical change.
6. `python3 scripts/marketplace.py validate` and catalog determinism pass after any change.

## Falsifiers

- A merge proceeding without resolving the `fortune5-architecture-pack`/`fortune5-enterprise-architecture-pack` overlap first is invalid — this is the single highest-risk ambiguity in this family and must be closed before anything else.
- Any physical change lacking a cited `ADMITTED`/`PARTIAL` court report is a process violation.

## Outcome (court run complete)

The consolidation court was run for real against this family:

```
$ python3 scripts/consolidation_court.py docs/jira/v26.8.19/families/fortune5-ea.toml > /tmp/court-fortune5-ea.toml.json; echo EXIT:$?
EXIT:0

$ python3 -m json.tool < /tmp/court-fortune5-ea.toml.json > /dev/null && echo VALID_JSON
VALID_JSON
```

- **Verdict: `REFUTED`**
- **Report: `docs/jira/v26.8.19/families/fortune5-ea-court-report.json`**
- **Diff result:** `ontology_conflicting_pairs = 36`, `total_pairs = 36` — all 36/36 evaluated pairs carry `ontology_conflict = true`, from
  `pairs.chatman-togaf-closure-pack__enterprise-architecture-connection-pack.ontology_conflict = true` through
  `pairs.gh-enterprise-architecture-pack__safe-ea-strategy-self-play-pack.ontology_conflict = true`.
- **Members evaluated:** `chatman-togaf-closure-pack`, `enterprise-architecture-connection-pack`, `fortune5-architecture-pack`,
  `fortune5-deployment-blocks-pack`, `fortune5-enterprise-architecture-pack`, `fortune5-required-capabilities-pack`,
  `fortune5-testing-bblock-pack`, `gh-enterprise-architecture-pack`, `safe-ea-strategy-self-play-pack`.

Per this ticket's own falsifiers: *"Any physical change lacking a cited `ADMITTED`/`PARTIAL` court report is a process violation."*
A `REFUTED` verdict is neither `ADMITTED` nor `PARTIAL`, so that falsifier forecloses any physical merge for this family — the
proposed `enterprise-architecture-core -> togaf-adm -> profiles{...} -> concerns{...}` shape is not supported by the real ontology
diff (every candidate pair conflicts). This closes the ticket's decision question without a merge: `REFUTED` is an acceptable
complete outcome under the ticket's own acceptance criteria, since acceptance criteria 1-4 required the court to resolve the
naming overlap and profile/concern assignments *before* any profile assignment or physical change — a `REFUTED` verdict resolves
that question in the negative (no valid consolidation shape exists) rather than leaving it open. No physical merge, pack directory
change, or `pack.toml` edit has been made to any of the nine member packs as part of this ticket. The
`fortune5-architecture-pack` vs `fortune5-enterprise-architecture-pack` naming-overlap question (acceptance criterion 1) is
subsumed by the `REFUTED` verdict: since all 36/36 pairs conflict, including this pair, no superset/subset or same-thing
relationship was found between them under the court's ontology diff.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — Fortune5/EA family entry and verified core-pack finding
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
