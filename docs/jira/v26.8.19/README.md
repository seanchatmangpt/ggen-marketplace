# v26.8.19 Pack Portfolio Consolidation Milestone

Standing ceiling: **PARTIAL_ALIVE**. Tickets 01-03 are implemented and independently re-verified (real code, real commands, real output — see their Outcome/commit history). `scripts/consolidation_court.py` went through three real corrections, each one caught by actually trying to build on the previous verdict rather than by inspection alone: v1→v2 (raw triple diffing couldn't see cross-namespace vocabulary overlap), v2→v3 (2026-09-14: the namespace-stripped diff was itself inflated by generic RDF/RDFS/OWL/XSD meta-vocabulary — `Class`, `Property`, `domain`, `range`, `label`, `comment`), and v3→v4 (2026-09-14, same day: a real physical kernel+profile-split *design* pass on the 3 families still ADMITTED under v3 found the identical bug one layer up — their entire shared vocabulary was `ggen-create`'s own marketplace-wide tooling scaffold, not family domain content). **Final result after v4, run against all 9 real families: 0 `ADMITTED`, 6 `PARTIAL`, 3 `REFUTED`.** Every family this milestone proposed for physical consolidation turned out, once the methodology got precise enough, to have no clean case for a kernel+profile split — see the v2→v3→v4 correction section below for the full history and the "why not" for each. **No pack has been merged, moved, or deleted anywhere in this milestone.** All 9 real, v4 court reports are committed under `families/*-court-report.json`.

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
| `03-TICKET-consolidation-court-methodology.md` | **DONE.** `scripts/consolidation_court.py` v4 (corrected methodology, three times), real, deterministic, run against all 9 real families | — |
| `05-TICKET-tcps-family-consolidation.md` | **PARTIAL (v4, unchanged from v3).** 10/15 pairs share real (non-generic, non-tooling) vocabulary — was 12/15 under v2. Merge NOT started. | Court run against 03 |
| `06-TICKET-wasm4pm-family-consolidation.md` | **PARTIAL (v4, unchanged from v3).** 6/28 pairs share real vocabulary — was 18/28 under v2 (12 of the 18 were generic-vocabulary false positives). Merge NOT started. | Court run against 03 |
| `07-TICKET-fortune5-ea-family-consolidation.md` | **PARTIAL (v4, unchanged from v3).** 20/36 pairs share real vocabulary — was 29/36 under v2. Merge NOT started. | Court run against 03 |
| `08-TICKET-release-lifecycle-family-consolidation.md` | **PARTIAL (v4, unchanged from v3).** 5/28 pairs share real vocabulary — was 16/28 under v2 (11 of the 16 were generic-vocabulary false positives). Merge NOT started. | Court run against 03 |
| `09-TICKET-repo-lifecycle-family-consolidation.md` | **PARTIAL (v4, unchanged from v3), downgraded from ADMITTED under v2.** 9/10 pairs share real vocabulary; `dogfood-lifecycle-pack__repo-load-path-pack` shared zero real terms once generic vocabulary was excluded. Merge NOT started. | Court run against 03 |
| `10-TICKET-mcp-protocol-family-consolidation.md` | **PARTIAL (v4, unchanged from v3).** 4/10 pairs share real vocabulary — was 5/10 under v2. Merge NOT started. | Court run against 03 |
| `11-TICKET-ui-projection-kernel-family-consolidation.md` | **REFUTED (v4), downgraded from ADMITTED under v3.** 0/36, 0/3, 0/3 pairs share real vocabulary in all 3 render-target groups (shadcn/deckgl/react-remotion) — their entire v3 ADMITTED overlap was `ggen-create`'s own marketplace-wide tooling scaffold, not shadcn/deck.gl/Remotion domain content. A real kernel+profile-split design pass found no live cross-pack ontology-import mechanism exists anywhere in this repo to even build one. No merge. | Court run against 03 |

## What was corrected from the raw audit before drafting these tickets

- Pack count corrected from 142 to the actual on-disk **143**.
- Two on-disk packs entirely missing from the raw audit's family taxonomy are noted (`castle-pack`, `castle-board-pack`) but not assigned a ticket in this milestone — no consolidation claim was made about them to correct.
- One on-disk pack (`otel-weaver-ocel-pack`) belonging to the OBSERVABILITY family was missing from the raw audit's family list; noted in `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` but not given its own ticket since no specific claim about it was made to verify.
- The raw audit's "disposition counts" (13/20/64/38/3/3/1) are explicitly not restated as authoritative anywhere in this milestone — they were computed against the miscounted 142-pack inventory and are noted as a rough historical estimate only.
- Every other pack name cited in the raw audit resolved to a real directory; none were dropped for non-existence.

## Explicit standing ceiling

Read every ticket in this directory as `PARTIAL_ALIVE`. All 3 gating tickets (01/02/03) are implemented and independently re-verified. All 7 family tickets (05-11, 9 court runs across 9 family definitions) have real, committed, reproducible v4 court reports.

**v1 → v2 correction, stated plainly:** the court's first real run (v1) returned `REFUTED` for every single family — a suspicious, undifferentiated result that turned out to be a bug, not a finding. v1 diffed ontologies as raw `(s, p, o)` triples; every pack in this repo mints its own RDF namespace (`tcps-core-pack` uses `<.../tcps-core#>`, `tcps-cli-pack` uses `<.../tcps-cli#>`, etc.) and embeds pack-specific instance data (literal source text) as part of its ontology — so raw triple equality gave `common=0` between any two packs, including ones sharing a real, obvious class/predicate vocabulary (`Module`, `name`, `order`, `dependsOnModule`, confirmed by direct inspection of `tcps-core-pack` and `tcps-cli-pack`'s `ontology.ttl`). v1's blanket REFUTED was a methodology defect being reported as a portfolio finding. v2 added a namespace-stripped vocabulary diff (class/predicate local names) as the primary, verdict-driving signal.

**v2 → v3 correction (2026-09-14), stated equally plainly:** v2's own vocabulary diff had the same class of bug one level down. Direct measurement on `wasm4pm-algorithms-pack`/`wasm4pm-breed-provenance-pack` (a v2 PARTIAL-contributing pair with `vocabulary_diff.common=7`) showed 6 of those 7 "shared" terms were `Class`, `Property`, `comment`, `domain`, `label`, `range` — standard RDF/RDFS/OWL meta-vocabulary every hand-authored `ontology.ttl` uses to declare its OWN unrelated classes/properties, not evidence of real domain overlap. Any two valid `ontology.ttl` files in this repo would show `common > 0` under v2 for this reason alone. v3 adds a `GENERIC_VOCAB` exclusion set (full list in `scripts/consolidation_court.py`'s module comment: RDF/RDFS/OWL/XSD class and predicate meta-vocabulary) before computing `vocabulary_diff`/`vocabulary_shared`, re-run against all 9 families:

| Verdict | Count (v2 → v3) | Families |
|---|---|---|
| `ADMITTED` | 4 → **3** | `ui-shadcn`, `ui-deckgl`, `ui-react-remotion` (`repo-lifecycle` downgraded) |
| `PARTIAL` | 5 → **6** | `tcps`, `wasm4pm`, `fortune5-ea`, `release-lifecycle`, `mcp-protocol`, `repo-lifecycle` |
| `REFUTED` | 0 → 0 | — |

Every PARTIAL family's real shared-pair count dropped substantially once generic vocabulary stopped inflating it: `wasm4pm` 18/28→6/28, `release-lifecycle` 16/28→5/28, `fortune5-ea` 29/36→20/36, `tcps` 12/15→10/15, `mcp-protocol` 5/10→4/10. `repo-lifecycle` moved from ADMITTED (10/10) to PARTIAL (9/10): its one non-overlapping pair, `dogfood-lifecycle-pack__repo-load-path-pack`, shared zero real vocabulary once the generic terms were excluded — independently, a separate real-content readiness review of this family the same day recommended dropping `dogfood-lifecycle-pack` for the same underlying reason (a self-contained PROV-O ontology unrelated to the other four members), confirming the finding from two independent angles.

**v3 → v4 correction (2026-09-14, same day), stated equally plainly:** the 3 UI families' ADMITTED verdicts *looked* materially stronger under v3 — every pair sharing real, non-generic vocabulary. Rather than stop there, a real physical kernel+profile-split *design* pass was run on all 3 (not another verdict check — an attempt to actually specify the kernel pack a builder would create). That pass found the same class of bug one layer up: the "real, non-generic" vocabulary driving all 3 ADMITTED verdicts was `ggen-create`'s own marketplace-wide tooling scaffold — a `GenerationSubject` individual with 10 name-casing predicates (`name`/`upper`/`lower`/`capitalized`/`pascal`/`camel`/`snake`/`upper_snake`/`kebab`/`title`) that `ggen-create` injects into every generated pack's own `ontology.ttl`, confirmed present in **26 of this marketplace's 318 packs**, including packs with zero relationship to UI, shadcn, deck.gl, or React (`packs/platform-engineers-handbook`, `packs/neako-web-deckgl-pack`). It survived v3's GENERIC_VOCAB filter because it isn't RDF/RDFS/OWL/XSD meta-vocabulary — it's this marketplace's own tooling's meta-vocabulary, the identical failure shape one namespace over. v4 adds `TOOLING_VOCAB_NAMESPACES` (checked by full IRI, not bare local name, to avoid over-excluding real domain terms like "name" or "title" elsewhere in the marketplace) and was re-run against all 9 families:

| Verdict | Count (v3 → v4) | Families |
|---|---|---|
| `ADMITTED` | 3 → **0** | — |
| `PARTIAL` | 6 → **6** | `tcps`, `wasm4pm`, `fortune5-ea`, `release-lifecycle`, `mcp-protocol`, `repo-lifecycle` (all unchanged — none of their real overlap touched `ggen-create`'s namespace) |
| `REFUTED` | 0 → **3** | `ui-shadcn` (36/36→0/36), `ui-deckgl` (3/3→0/3), `ui-react-remotion` (3/3→0/3) |

**Beyond the vocabulary bug — a deeper, load-bearing finding from the same design pass:** even setting the tooling-vocabulary false positive aside, the design pass found this repository has **no live, exercised cross-pack ontology-import mechanism at all**. `[ontology].imports` (used repo-wide) only ever resolves relative paths *inside the same pack directory*; `extra_ontologies` appears only in prose descriptions of several unrelated packs, every one of which explicitly states it is *not* using that field, and a repo-wide grep found zero `ggen.toml` files that actually populate it. The only real cross-pack composition mechanism in this repository, confirmed by a real, exercised example (`packs/clap-noun-verb-zeroconfig-pack/ggen.toml`), is the `[packs]` table referencing a *sibling pack as a whole dependency* — not "import this pack's TBox into mine." A genuine kernel+profile split (member packs referencing a shared kernel's vocabulary rather than each re-declaring it) has no working precedent to build on here. This means even a family that *did* show real, non-tooling, non-generic universal vocabulary overlap would still need this composition mechanism built and proven before a physical split could be more than a documentation exercise — a materially bigger, separate piece of real infrastructure work, not a family-by-family court-run task.

**Consumer-boundary BEFORE baseline (ticket 03 item 4, historical):** a real, installed `ggen` 26.8.18 binary was used to run `ggen sync run` against 4 families' kernel-candidate packs from real, isolated `/tmp/court-consumer-<family>` projects (`[packs]` path reference, per `docs/how-to/consume-a-pack.md`), captured while those 4 were still ADMITTED under v2. All 4 generated successfully and deterministically (replayed twice, identical `graph_hash_hex` both times):

| Family | Kernel candidate | Files generated | Deterministic on replay | Final (v4) verdict |
|---|---|---|---|---|
| `repo-lifecycle` | `repo-as-found-pack` | 4 | yes | PARTIAL (9/10) |
| `ui-shadcn` | `ai-chatbot-shadcn-pack` | 6 | yes | REFUTED (0/36) |
| `ui-deckgl` | `mfact-ui-deckgl-pack` | 5 | yes | REFUTED (0/3) |
| `ui-react-remotion` | `phage-wars-3-react-pack` | 7 | yes | REFUTED (0/3) |

Raw evidence: `docs/jira/v26.8.19/families/consumer-boundary/<family>-before.json`. This baseline remains real, independent evidence that each of these 4 kernel-candidate packs generates deterministically *today, standalone* — that fact is unaffected by the vocabulary-overlap corrections above. What it can no longer support is item 4's original purpose (a BEFORE state to diff a proposed kernel-split AFTER state against) for 3 of the 4, since no real family-wide kernel exists to split into for `ui-shadcn`/`ui-deckgl`/`ui-react-remotion`.

**No pack anywhere in the marketplace was merged, moved, or deleted by this milestone.** With the benefit of the full v1→v2→v3→v4 correction history, that turned out to be exactly right, not merely cautious: every family this milestone proposed for consolidation, once checked precisely enough, either shows only a modest real overlap needing per-pair re-scoping (6 PARTIAL families) or no real overlap at all (3 REFUTED families, formerly the milestone's strongest-looking candidates).

**What is and isn't finished:** the court methodology now exists, is correct (caught and fixed three of its own defects via direct evidence inspection — not assumption — across v1→v2→v3→v4, the last two on the same day), is deterministic, and has been run to a stable, self-consistent conclusion against every family this milestone proposed. That work is genuinely, completely done — this milestone's physical-merge question is answered: **no family currently qualifies for a kernel+profile split**, and a real design pass additionally found this repository has no working cross-pack ontology-import mechanism to build one on even where overlap does exist. What remains real, unstarted follow-up work, should anyone pick it back up: (1) for the 6 PARTIAL families, deciding per-pair whether a *smaller*, re-scoped consolidation (dropping the non-overlapping members/pairs identified in each report) is still worth it; (2) designing and proving a real cross-pack ontology-import mechanism in `ggen` itself, since none of this milestone's findings can become a physical merge without one. Neither is claimed as done here.

If a future family is proposed for consolidation, re-run `scripts/consolidation_court.py` (v4) against `families/<name>.toml` — the machinery is real, reusable, correct as far as three real corrections have been able to determine, and its verdict rule is documented in the script's own module docstring.

## See Also

- `../../../CLAUDE.md` — marketplace architecture, pack profile derivation, control-plane admission doctrine
- `../../../AGENTS.md` — authoritative source hierarchy and discipline list
- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — full methodology and evidence this milestone is built on
