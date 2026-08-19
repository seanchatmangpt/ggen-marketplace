# 05 Ticket TCPS Family Consolidation

Standing: PARTIAL_ALIVE — court run complete, CLOSED (no merge, per REFUTED falsifier).

## Quick reference

- Proposed shape: one TCPS core ontology with projections for `{cli, ffi, std, wasm, release}`.
- Kernel candidate: `packs/tcps-core-pack`
- Member packs (real names, all confirmed present on disk): `packs/tcps-cli-pack`, `packs/tcps-ffi-pack`, `packs/tcps-std-pack`, `packs/tcps-wasm-pack`, `packs/tcps-release-pack`
- Confidence basis: naming-convention cohesion (all six packs share the `tcps-` prefix and a one-word-per-target suffix pattern consistent with a kernel+profile split). This is a structural/naming observation, not a verified ontology-content match — the audit's own family-membership claim here is `INFERRED`, and this ticket does not upgrade it to verified; only ticket 03's court can do that.

## Scope

This ticket is the *plan*, not the merge. It records the proposed shape and acceptance criteria so that once ticket 03's court exists, running it against this family is a scoped, well-defined unit of work rather than a fresh investigation.

## Acceptance criteria

1. Ticket 03's consolidation court has been run against this family and produced a report at a stable path (e.g. `docs/jira/v26.8.19/reports/tcps-consolidation.json`).
2. The report's verdict is `ADMITTED` or `PARTIAL` (naming which members are excluded, if any) — a `REFUTED` verdict closes this ticket without a merge, and that is an acceptable, complete outcome.
3. If `ADMITTED`/`PARTIAL`: `tcps-core-pack` is confirmed (or amended) as the kernel, and each of `tcps-cli-pack`/`tcps-ffi-pack`/`tcps-std-pack`/`tcps-wasm-pack`/`tcps-release-pack` is confirmed as a parameterized profile over it, per the court's pairwise ontology/query/template diffs.
4. A real consumer project exercising `tcps-cli-pack` (or another admitted member) before and after any proposed physical restructuring produces identical generated output (per this repo's qualification discipline in `CLAUDE.md`).
5. `python3 scripts/marketplace.py validate` and the catalog determinism check both pass after any physical change.
6. No pack is deleted in this ticket's PR unless the court's report explicitly names it as fully subsumed by the kernel with zero unique surface — and even then, prefer retiring it from discovery (ticket 01's pattern) over an outright delete, consistent with this repo's fix-forward, provenance-preserving discipline.

## Falsifiers

- Any physical merge/delete landed under this ticket without a cited court report at the path from criterion 1 is a process violation — revert and redo through the court.
- If the court returns `REFUTED` (e.g. the five profile packs' ontologies conflict rather than converge), this ticket is done as "family claim not upheld" — do not re-attempt consolidation without new evidence.

## Outcome (court run complete)

`scripts/consolidation_court.py` was run for real against this family (`docs/jira/v26.8.19/families/tcps.toml`, kernel candidate `tcps-core-pack` + 5 members). Verdict: **`REFUTED`** — `ontology_conflicting_pairs: 15`, `total_pairs: 15` (all C(6,2)=15 pairwise combinations have ontology triples present in only one side). Report committed at `docs/jira/v26.8.19/families/tcps-court-report.json`, reproduced byte-for-byte on an independent re-run.

Per acceptance criterion 2 and the Falsifiers section above, this is an acceptable, complete outcome: "a `REFUTED` verdict closes this ticket without a merge." No pack was moved, merged, or deleted. `tcps-core-pack` and the five profile-candidate packs remain independent, unmerged packs.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — TCPS family entry
- `03-TICKET-consolidation-court-methodology.md` — the gating methodology this ticket depends on
- `02-TICKET-pack-class-taxonomy.md` — `tcps-core-pack` is a `KernelPack` candidate under that taxonomy once admitted
