# v26.8.19 Pack Portfolio Consolidation Milestone

Standing ceiling: **PARTIAL_ALIVE**. Tickets 01-03 are implemented and independently re-verified (real code, real commands, real output — see their Outcome/commit history). Tickets 05-11's court runs are complete: **every one of the 8 proposed families (TCPS, wasm4pm, Fortune5/EA, release-lifecycle, repo-lifecycle, MCP-protocol, and the UI-projection-kernel family's 3 render-target groups) returned a real `REFUTED` verdict** from `scripts/consolidation_court.py` (every pairwise ontology diff conflicted — `ontology_conflicting_pairs == total_pairs` in all 8 reports). **No pack has been merged or deleted anywhere in this milestone** — REFUTED is each ticket's own defined acceptable-complete-outcome (see each ticket's Falsifiers section), not a shortcut around ticket 03's gate. All 8 real court reports are committed under `families/*-court-report.json`.

## Quick reference

This directory is a milestone-ticket exception to this repository's strict Diátaxis documentation structure (`docs/tutorials/`, `docs/how-to/`, `docs/reference/`, `docs/explanation/`), matching the convention already used for milestone tickets in sibling repos (e.g. `ggen-legacy/tickets/*.md`). Nothing here is a Diátaxis page and nothing here should be treated as one.

## Milestone summary

The pack-consolidation portfolio audit that seeded this milestone found that `ggen-marketplace`'s pack count (143 on disk, corrected from the source audit's "142") has crossed the point where adding more packs is the dominant maturity strategy — the next jump is class closure and consolidation of repeated projection grammars, not new pack creation. The audit is grounded in this repository's own source hierarchy (`pack.toml -> ontology.ttl -> templates -> gates`, real consumer boundary required for consequential claims) rather than treating "pack exists" as maturity.

One concrete, individually-verified finding anchors the milestone: `clap-noun-verb-pack` already self-declares deprecated in its own `pack.toml`, naming six real successor packs. Everything else — family groupings, proposed kernel/profile shapes, disposition counts — is `INFERRED`: a structural/naming observation, not a proven graph/query/template correspondence, and is documented as such throughout.

## Ticket index

| File | What it is | Depends on |
|---|---|---|
| `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` | Source-of-truth analysis: 7-axis maturity matrix, methodology, corrections to the raw audit's count/omissions | — |
| `01-TICKET-retire-clap-noun-verb-legacy.md` | **DONE.** `scripts/marketplace.py` catalog marks `clap-noun-verb-pack` deprecated with 6 real successors | — |
| `02-TICKET-pack-class-taxonomy.md` | **DONE.** 7-class taxonomy in `docs/reference/pack-classes.md` + `pack_class` catalog field (worked examples only) | — |
| `03-TICKET-consolidation-court-methodology.md` | **DONE.** `scripts/consolidation_court.py` real, deterministic, run 8 times against 8 real families | — |
| `05-TICKET-tcps-family-consolidation.md` | **CLOSED.** Court run: `REFUTED` (15/15 pairs conflict). No merge. | Court run against 03 |
| `06-TICKET-wasm4pm-family-consolidation.md` | **CLOSED.** Court run: `REFUTED` (28/28 pairs conflict). No merge. | Court run against 03 |
| `07-TICKET-fortune5-ea-family-consolidation.md` | **CLOSED.** Court run: `REFUTED` (36/36 pairs conflict). No merge. | Court run against 03 |
| `08-TICKET-release-lifecycle-family-consolidation.md` | **CLOSED.** Court run: `REFUTED` (28/28 pairs conflict). No merge. | Court run against 03 |
| `09-TICKET-repo-lifecycle-family-consolidation.md` | **CLOSED.** Court run: `REFUTED` (10/10 pairs conflict). No merge. | Court run against 03 |
| `10-TICKET-mcp-protocol-family-consolidation.md` | **CLOSED.** Court run: `REFUTED` (10/10 pairs conflict). No merge. | Court run against 03 |
| `11-TICKET-ui-projection-kernel-family-consolidation.md` | **CLOSED.** All 3 render-target groups (shadcn 36/36, deckgl 3/3, react/remotion 3/3) `REFUTED`. No merge, no new kernel pack created. | Court run against 03 |

## What was corrected from the raw audit before drafting these tickets

- Pack count corrected from 142 to the actual on-disk **143**.
- Two on-disk packs entirely missing from the raw audit's family taxonomy are noted (`castle-pack`, `castle-board-pack`) but not assigned a ticket in this milestone — no consolidation claim was made about them to correct.
- One on-disk pack (`otel-weaver-ocel-pack`) belonging to the OBSERVABILITY family was missing from the raw audit's family list; noted in `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` but not given its own ticket since no specific claim about it was made to verify.
- The raw audit's "disposition counts" (13/20/64/38/3/3/1) are explicitly not restated as authoritative anywhere in this milestone — they were computed against the miscounted 142-pack inventory and are noted as a rough historical estimate only.
- Every other pack name cited in the raw audit resolved to a real directory; none were dropped for non-existence.

## Explicit standing ceiling

Read every ticket in this directory as `PARTIAL_ALIVE`. All 3 gating tickets (01/02/03) are implemented and independently re-verified. All 7 family tickets (05-11, 9 court runs across 8 family definitions) have real, committed, reproducible court reports and are closed with `REFUTED` — consistent with each ticket's own stated acceptable-complete-outcome for that verdict. **No pack anywhere in the marketplace was merged, moved, or deleted by this milestone.** The court's own `verdict_rule` (`ADMITTED` only when `ontology_conflicting_pairs == 0`) is strict by design — every proposed family in this audit turned out to have genuine pack-specific ontology content that a naming-convention-only "family" grouping missed. That is a real, useful finding in itself: it falsifies the audit's INFERRED groupings rather than rubber-stamping them, and it means the marketplace's 143 packs remain, for now, exactly what they were before this milestone — no physical consolidation has occurred, and none is currently supported by evidence.

If a future family is proposed for consolidation, re-run `scripts/consolidation_court.py` against a new `families/<name>.toml` — the machinery is real and reusable, it is only this milestone's specific 8 candidate groupings that failed.

## See Also

- `../../../CLAUDE.md` — marketplace architecture, pack profile derivation, control-plane admission doctrine
- `../../../AGENTS.md` — authoritative source hierarchy and discipline list
- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — full methodology and evidence this milestone is built on
