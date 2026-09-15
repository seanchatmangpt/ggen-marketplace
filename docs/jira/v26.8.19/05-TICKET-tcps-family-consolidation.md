# 05 Ticket TCPS Family Consolidation

Standing: PARTIAL_ALIVE — court run complete (v2 methodology). Real vocabulary-level correspondence found for at least one family; physical-merge phase NOT started (ticket 03 item 4, real consumer-boundary check against a live ggen runtime, has not been run).

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

## Outcome (court run complete, v2 methodology)

The consolidation court was re-run using `scripts/consolidation_court.py` **v2**. v1 (the original run) diffed ontologies as raw (s,p,o) triples and returned `REFUTED` for every family in this milestone (0/9 admitted) — that was found to be a methodology defect, not a real finding: every pack mints its own RDF namespace and embeds pack-specific instance data (literal source text, per-crate case names), so raw triple equality gives `common=0` even between packs that share a real class/predicate vocabulary. v2 adds a namespace-stripped **vocabulary** diff (class/predicate local names) as the verdict-driving signal, with the old instance-triple diff kept and reported but no longer determining the verdict — see `scripts/consolidation_court.py`'s module docstring for the full methodology correction.

| Family | Kernel candidate | Verdict | Vocabulary-shared | Instance-conflicting | Report |
|---|---|---|---|---|---|
| `tcps` | `tcps-core-pack` | **PARTIAL** | 12/15 pairs share real vocabulary | 15/15 pairs instance-conflicting (expected, not a defect) | `docs/jira/v26.8.19/families/tcps-court-report.json` |

This is a genuine, differentiated finding — real shared vocabulary exists across most or all member-pack pairs, which v1's blanket-REFUTED result had obscured. **This does NOT authorize a physical merge yet.** Per `03-TICKET-consolidation-court-methodology.md`'s own acceptance criteria, item 4 (a real consumer project generated from the current pack vs. the proposed kernel+profile split, output diffed) is required before any physical change, and `consolidation_court.py` explicitly does not perform it (`consumer_boundary_check: null` in every report). This ticket's ADMITTED/PARTIAL verdict is therefore a genuine **candidate for a follow-up physical-merge ticket**, not a completed merge — the physical-change phase (kernel-pack creation, repointing members as profiles, real consumer diff) remains unscoped, un-started work, separate from this court-run ticket.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — TCPS family entry
- `03-TICKET-consolidation-court-methodology.md` — the gating methodology this ticket depends on
- `02-TICKET-pack-class-taxonomy.md` — `tcps-core-pack` is a `KernelPack` candidate under that taxonomy once admitted
