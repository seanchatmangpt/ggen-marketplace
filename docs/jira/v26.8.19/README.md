# v26.8.19 Pack Portfolio Consolidation Milestone

Standing ceiling: **PARTIAL_ALIVE**. Tickets 01-03 are implemented and independently re-verified (real code, real commands, real output — see their Outcome/commit history). `scripts/consolidation_court.py` went through two real corrections: v1→v2 (raw triple diffing couldn't see cross-namespace vocabulary overlap; fixed by adding a namespace-stripped class/predicate diff) and, on 2026-09-14, **v2→v3** (the namespace-stripped diff was itself inflated by generic RDF/RDFS/OWL/XSD meta-vocabulary — `Class`, `Property`, `domain`, `range`, `label`, `comment` — that any two hand-authored `ontology.ttl` files share regardless of real domain overlap; confirmed by direct measurement on a wasm4pm pair where 6 of 7 "shared" terms were exactly this generic set). Re-run against all 9 families under v3: **3 `ADMITTED`, 6 `PARTIAL`, 0 `REFUTED`** — one family (`repo-lifecycle`) downgraded from ADMITTED once its one non-real-overlap pair was correctly excluded, and every remaining PARTIAL family's real shared-pair count dropped substantially (e.g. `wasm4pm` 18/28 → 6/28, `release-lifecycle` 16/28 → 5/28). **No pack has been merged, moved, or deleted anywhere in this milestone** — every ADMITTED/PARTIAL verdict is explicitly a *candidate* for a follow-up physical-merge ticket, not a completed merge; ticket 03's own item 4 (real consumer-boundary check against a live ggen runtime) has not been run and physically merging without it would violate every family ticket's own acceptance criteria. All 9 real, v3 court reports are committed under `families/*-court-report.json`.

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
| `03-TICKET-consolidation-court-methodology.md` | **DONE.** `scripts/consolidation_court.py` v3 (corrected methodology, twice), real, deterministic, run against all 9 real families | — |
| `05-TICKET-tcps-family-consolidation.md` | **PARTIAL (v3).** 10/15 pairs share real (non-generic) vocabulary — was 12/15 under v2. Merge NOT started (needs ticket-03 item 4). | Court run against 03 |
| `06-TICKET-wasm4pm-family-consolidation.md` | **PARTIAL (v3).** 6/28 pairs share real vocabulary — was 18/28 under v2 (12 of the 18 were generic-vocabulary false positives). Merge NOT started (needs ticket-03 item 4). | Court run against 03 |
| `07-TICKET-fortune5-ea-family-consolidation.md` | **PARTIAL (v3).** 20/36 pairs share real vocabulary — was 29/36 under v2. Merge NOT started (needs ticket-03 item 4). | Court run against 03 |
| `08-TICKET-release-lifecycle-family-consolidation.md` | **PARTIAL (v3).** 5/28 pairs share real vocabulary — was 16/28 under v2 (11 of the 16 were generic-vocabulary false positives). Merge NOT started (needs ticket-03 item 4). | Court run against 03 |
| `09-TICKET-repo-lifecycle-family-consolidation.md` | **PARTIAL (v3), downgraded from ADMITTED under v2.** 9/10 pairs share real vocabulary; `dogfood-lifecycle-pack__repo-load-path-pack` shared zero real terms once generic vocabulary was excluded (was counted ADMITTED under v2 purely on generic overlap). Merge NOT started. | Court run against 03 |
| `10-TICKET-mcp-protocol-family-consolidation.md` | **PARTIAL (v3).** 4/10 pairs share real vocabulary — was 5/10 under v2. Merge NOT started (needs ticket-03 item 4). | Court run against 03 |
| `11-TICKET-ui-projection-kernel-family-consolidation.md` | **ADMITTED (v3, unchanged)** in all 3 render-target groups (shadcn 36/36, deckgl 3/3, react/remotion 3/3) — the only 3 families whose ADMITTED verdict survives real (non-generic) vocabulary exclusion. Merge NOT started (needs ticket-03 item 4). | Court run against 03 |

## What was corrected from the raw audit before drafting these tickets

- Pack count corrected from 142 to the actual on-disk **143**.
- Two on-disk packs entirely missing from the raw audit's family taxonomy are noted (`castle-pack`, `castle-board-pack`) but not assigned a ticket in this milestone — no consolidation claim was made about them to correct.
- One on-disk pack (`otel-weaver-ocel-pack`) belonging to the OBSERVABILITY family was missing from the raw audit's family list; noted in `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` but not given its own ticket since no specific claim about it was made to verify.
- The raw audit's "disposition counts" (13/20/64/38/3/3/1) are explicitly not restated as authoritative anywhere in this milestone — they were computed against the miscounted 142-pack inventory and are noted as a rough historical estimate only.
- Every other pack name cited in the raw audit resolved to a real directory; none were dropped for non-existence.

## Explicit standing ceiling

Read every ticket in this directory as `PARTIAL_ALIVE`. All 3 gating tickets (01/02/03) are implemented and independently re-verified. All 7 family tickets (05-11, 9 court runs across 9 family definitions) have real, committed, reproducible v3 court reports.

**v1 → v2 correction, stated plainly:** the court's first real run (v1) returned `REFUTED` for every single family — a suspicious, undifferentiated result that turned out to be a bug, not a finding. v1 diffed ontologies as raw `(s, p, o)` triples; every pack in this repo mints its own RDF namespace (`tcps-core-pack` uses `<.../tcps-core#>`, `tcps-cli-pack` uses `<.../tcps-cli#>`, etc.) and embeds pack-specific instance data (literal source text) as part of its ontology — so raw triple equality gave `common=0` between any two packs, including ones sharing a real, obvious class/predicate vocabulary (`Module`, `name`, `order`, `dependsOnModule`, confirmed by direct inspection of `tcps-core-pack` and `tcps-cli-pack`'s `ontology.ttl`). v1's blanket REFUTED was a methodology defect being reported as a portfolio finding. v2 added a namespace-stripped vocabulary diff (class/predicate local names) as the primary, verdict-driving signal.

**v2 → v3 correction (2026-09-14), stated equally plainly:** v2's own vocabulary diff had the same class of bug one level down. Direct measurement on `wasm4pm-algorithms-pack`/`wasm4pm-breed-provenance-pack` (a v2 PARTIAL-contributing pair with `vocabulary_diff.common=7`) showed 6 of those 7 "shared" terms were `Class`, `Property`, `comment`, `domain`, `label`, `range` — standard RDF/RDFS/OWL meta-vocabulary every hand-authored `ontology.ttl` uses to declare its OWN unrelated classes/properties, not evidence of real domain overlap. Any two valid `ontology.ttl` files in this repo would show `common > 0` under v2 for this reason alone. v3 adds a `GENERIC_VOCAB` exclusion set (full list in `scripts/consolidation_court.py`'s module comment: RDF/RDFS/OWL/XSD class and predicate meta-vocabulary) before computing `vocabulary_diff`/`vocabulary_shared`, re-run against all 9 families:

| Verdict | Count (v2 → v3) | Families |
|---|---|---|
| `ADMITTED` | 4 → **3** | `ui-shadcn`, `ui-deckgl`, `ui-react-remotion` (`repo-lifecycle` downgraded) |
| `PARTIAL` | 5 → **6** | `tcps`, `wasm4pm`, `fortune5-ea`, `release-lifecycle`, `mcp-protocol`, `repo-lifecycle` |
| `REFUTED` | 0 → 0 | — |

Every PARTIAL family's real shared-pair count dropped substantially once generic vocabulary stopped inflating it: `wasm4pm` 18/28→6/28, `release-lifecycle` 16/28→5/28, `fortune5-ea` 29/36→20/36, `tcps` 12/15→10/15, `mcp-protocol` 5/10→4/10. `repo-lifecycle` moved from ADMITTED (10/10) to PARTIAL (9/10): its one non-overlapping pair, `dogfood-lifecycle-pack__repo-load-path-pack`, shared zero real vocabulary once the generic terms were excluded — independently, a separate real-content readiness review of this family the same day recommended dropping `dogfood-lifecycle-pack` for the same underlying reason (a self-contained PROV-O ontology unrelated to the other four members), confirming the finding from two independent angles. The 3 UI families' ADMITTED verdicts are unchanged and now materially stronger evidence: their real (non-generic) vocabulary overlap holds for every pair, not just their generic-inflated overlap.

**Consumer-boundary BEFORE baseline (ticket 03 item 4, partial):** a real, installed `ggen` 26.8.18 binary was used to run `ggen sync run` against 4 families' kernel-candidate packs from real, isolated `/tmp/court-consumer-<family>` projects (`[packs]` path reference, per `docs/how-to/consume-a-pack.md`), captured while those 4 were still ADMITTED under v2. All 4 generated successfully and deterministically (replayed twice, identical `graph_hash_hex` both times):

| Family | Kernel candidate | Files generated | Deterministic on replay | v3 verdict |
|---|---|---|---|---|
| `repo-lifecycle` | `repo-as-found-pack` | 4 | yes | PARTIAL (downgraded; `repo-as-found-pack` itself was not the pair that lost overlap — this baseline's real evidence still holds for `repo-as-found-pack`'s own generation, but the family's blanket ADMITTED no longer holds) |
| `ui-shadcn` | `ai-chatbot-shadcn-pack` | 6 | yes | ADMITTED (unchanged) |
| `ui-deckgl` | `mfact-ui-deckgl-pack` | 5 | yes | ADMITTED (unchanged) |
| `ui-react-remotion` | `phage-wars-3-react-pack` | 7 | yes | ADMITTED (unchanged) |

Raw evidence: `docs/jira/v26.8.19/families/consumer-boundary/<family>-before.json`. This is the **BEFORE** half of item 4 only — real proof each kernel candidate actually generates today. There is no **AFTER** state, because no kernel-split pack has been physically created for any family yet.

**No pack anywhere in the marketplace was merged, moved, or deleted by this milestone**, despite 3 real ADMITTED verdicts and 4 real BEFORE baselines. That is deliberate, not incomplete: physically creating a new kernel pack and repointing members without the AFTER half of item 4 (generating from the *proposed* split and diffing against BEFORE) would itself be the process violation each ticket's Falsifiers section warns against — a BEFORE baseline alone does not prove a split preserves output.

**What is and isn't finished:** the court methodology now exists, is correct (caught and fixed two of its own defects via direct evidence inspection, not assumption, across v1→v2→v3), is deterministic, and has been run against every family this milestone proposed. A real BEFORE consumer-generation baseline exists for the 4 families that were ADMITTED under v2, captured with the real `ggen` binary, not simulated. That work is genuinely done. What remains real, unstarted follow-up work: (1) physically authoring each kernel pack's ontology/template split for the 3 families still ADMITTED under v3, generating the AFTER state, and diffing it against the BEFORE baselines captured here; (2) for the 6 PARTIAL families, deciding per-pair whether to re-scope membership (drop the pairs/packs that don't share real vocabulary) before any merge is even proposed. Neither is a court-run or evidence-capture task, and neither is claimed as done here.

If a future family is proposed for consolidation, or the ADMITTED families above are picked up for their physical-merge phase, re-run `scripts/consolidation_court.py` (v3) against `families/<name>.toml` — the machinery is real, reusable, and its verdict rule is documented in the script's own module docstring.

## See Also

- `../../../CLAUDE.md` — marketplace architecture, pack profile derivation, control-plane admission doctrine
- `../../../AGENTS.md` — authoritative source hierarchy and discipline list
- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — full methodology and evidence this milestone is built on
