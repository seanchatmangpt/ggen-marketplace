# v26.8.19 Pack Portfolio Consolidation Milestone

Standing ceiling: **PARTIAL_ALIVE**. Tickets 01-03 are implemented and independently re-verified (real code, real commands, real output — see their Outcome/commit history). `scripts/consolidation_court.py` was corrected to **v2** after its first (v1) run against all 9 real families returned a blanket `REFUTED` (0/9 admitted) that turned out to be a methodology defect — raw (s,p,o) triple diffing can never find overlap between packs that (correctly) use their own RDF namespace, even when they share real vocabulary. v2 adds a namespace-stripped class/predicate diff as the verdict-driving signal. Re-run against all 9 families under v2: **4 `ADMITTED`, 5 `PARTIAL`, 0 `REFUTED`** — a genuine, differentiated result. **No pack has been merged, moved, or deleted anywhere in this milestone** — every ADMITTED/PARTIAL verdict is explicitly a *candidate* for a follow-up physical-merge ticket, not a completed merge; ticket 03's own item 4 (real consumer-boundary check against a live ggen runtime) has not been run and physically merging without it would violate every family ticket's own acceptance criteria. All 9 real, v2 court reports are committed under `families/*-court-report.json`.

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
| `03-TICKET-consolidation-court-methodology.md` | **DONE.** `scripts/consolidation_court.py` v2 (corrected methodology), real, deterministic, run against all 9 real families | — |
| `05-TICKET-tcps-family-consolidation.md` | **PARTIAL.** 12/15 pairs share real vocabulary. Merge NOT started (needs ticket-03 item 4). | Court run against 03 |
| `06-TICKET-wasm4pm-family-consolidation.md` | **PARTIAL.** 18/28 pairs share real vocabulary. Merge NOT started (needs ticket-03 item 4). | Court run against 03 |
| `07-TICKET-fortune5-ea-family-consolidation.md` | **PARTIAL.** 29/36 pairs share real vocabulary. Merge NOT started (needs ticket-03 item 4). | Court run against 03 |
| `08-TICKET-release-lifecycle-family-consolidation.md` | **PARTIAL.** 16/28 pairs share real vocabulary. Merge NOT started (needs ticket-03 item 4). | Court run against 03 |
| `09-TICKET-repo-lifecycle-family-consolidation.md` | **ADMITTED.** 10/10 pairs share real vocabulary. Merge NOT started (needs ticket-03 item 4). | Court run against 03 |
| `10-TICKET-mcp-protocol-family-consolidation.md` | **PARTIAL.** 5/10 pairs share real vocabulary. Merge NOT started (needs ticket-03 item 4). | Court run against 03 |
| `11-TICKET-ui-projection-kernel-family-consolidation.md` | **ADMITTED** in all 3 render-target groups (shadcn 36/36, deckgl 3/3, react/remotion 3/3). Merge NOT started (needs ticket-03 item 4). | Court run against 03 |

## What was corrected from the raw audit before drafting these tickets

- Pack count corrected from 142 to the actual on-disk **143**.
- Two on-disk packs entirely missing from the raw audit's family taxonomy are noted (`castle-pack`, `castle-board-pack`) but not assigned a ticket in this milestone — no consolidation claim was made about them to correct.
- One on-disk pack (`otel-weaver-ocel-pack`) belonging to the OBSERVABILITY family was missing from the raw audit's family list; noted in `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` but not given its own ticket since no specific claim about it was made to verify.
- The raw audit's "disposition counts" (13/20/64/38/3/3/1) are explicitly not restated as authoritative anywhere in this milestone — they were computed against the miscounted 142-pack inventory and are noted as a rough historical estimate only.
- Every other pack name cited in the raw audit resolved to a real directory; none were dropped for non-existence.

## Explicit standing ceiling

Read every ticket in this directory as `PARTIAL_ALIVE`. All 3 gating tickets (01/02/03) are implemented and independently re-verified. All 7 family tickets (05-11, 9 court runs across 9 family definitions) have real, committed, reproducible v2 court reports.

**v1 → v2 correction, stated plainly:** the court's first real run (v1) returned `REFUTED` for every single family — a suspicious, undifferentiated result that turned out to be a bug, not a finding. v1 diffed ontologies as raw `(s, p, o)` triples; every pack in this repo mints its own RDF namespace (`tcps-core-pack` uses `<.../tcps-core#>`, `tcps-cli-pack` uses `<.../tcps-cli#>`, etc.) and embeds pack-specific instance data (literal source text) as part of its ontology — so raw triple equality gave `common=0` between any two packs, including ones sharing a real, obvious class/predicate vocabulary (`Module`, `name`, `order`, `dependsOnModule`, confirmed by direct inspection of `tcps-core-pack` and `tcps-cli-pack`'s `ontology.ttl`). v1's blanket REFUTED was a methodology defect being reported as a portfolio finding. v2 adds a namespace-stripped vocabulary diff (class/predicate local names) as the primary, verdict-driving signal, keeps the old instance-triple diff as reported-but-non-authoritative context, and was re-run against all 9 families:

| Verdict | Count | Families |
|---|---|---|
| `ADMITTED` | 4 | `repo-lifecycle`, `ui-shadcn`, `ui-deckgl`, `ui-react-remotion` |
| `PARTIAL` | 5 | `tcps`, `wasm4pm`, `fortune5-ea`, `release-lifecycle`, `mcp-protocol` |
| `REFUTED` | 0 | — |

**Consumer-boundary BEFORE baseline (ticket 03 item 4, partial):** a real, installed `ggen` 26.8.18 binary was used to run `ggen sync run` against all 4 ADMITTED families' kernel-candidate packs from real, isolated `/tmp/court-consumer-<family>` projects (`[packs]` path reference, per `docs/how-to/consume-a-pack.md`). All 4 generated successfully and deterministically (replayed twice, identical `graph_hash_hex` both times):

| Family | Kernel candidate | Files generated | Deterministic on replay |
|---|---|---|---|
| `repo-lifecycle` | `repo-as-found-pack` | 4 | yes |
| `ui-shadcn` | `ai-chatbot-shadcn-pack` | 6 | yes |
| `ui-deckgl` | `mfact-ui-deckgl-pack` | 5 | yes |
| `ui-react-remotion` | `phage-wars-3-react-pack` | 7 | yes |

Raw evidence: `docs/jira/v26.8.19/families/consumer-boundary/<family>-before.json`. This is the **BEFORE** half of item 4 only — real proof each ADMITTED family's kernel candidate actually generates today. There is no **AFTER** state, because no kernel-split pack has been physically created for any family yet.

**No pack anywhere in the marketplace was merged, moved, or deleted by this milestone**, despite 4 real ADMITTED verdicts and 4 real BEFORE baselines. That is deliberate, not incomplete: physically creating a new kernel pack and repointing members without the AFTER half of item 4 (generating from the *proposed* split and diffing against BEFORE) would itself be the process violation each ticket's Falsifiers section warns against — a BEFORE baseline alone does not prove a split preserves output.

**What is and isn't finished:** the court methodology now exists, is correct (caught and fixed its own v1 defect via direct evidence inspection, not assumption), is deterministic, and has been run against every family this milestone proposed. A real BEFORE consumer-generation baseline now exists for all 4 ADMITTED families, captured with the real `ggen` binary, not simulated. That work is genuinely done. What remains real, unstarted follow-up work: physically authoring each kernel pack's ontology/template split, generating the AFTER state, and diffing it against the BEFORE baselines captured here — a design and implementation task in its own right, not a court-run or evidence-capture task, and is not claimed as done here.

If a future family is proposed for consolidation, or the ADMITTED families above are picked up for their physical-merge phase, re-run `scripts/consolidation_court.py` (v2) against `families/<name>.toml` — the machinery is real, reusable, and its verdict rule is documented in the script's own module docstring.

## See Also

- `../../../CLAUDE.md` — marketplace architecture, pack profile derivation, control-plane admission doctrine
- `../../../AGENTS.md` — authoritative source hierarchy and discipline list
- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — full methodology and evidence this milestone is built on
