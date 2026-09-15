# 06 Ticket Wasm4pm Family Consolidation

**v3 correction (2026-09-14):** `scripts/consolidation_court.py` was corrected a second time (v2→v3) after direct measurement showed v2's "shared vocabulary" signal was inflated by generic RDF/RDFS/OWL/XSD meta-vocabulary (Class, Property, domain, range, label, comment, ...) that any two hand-authored `ontology.ttl` files share regardless of real domain overlap. Re-run under v3: **PARTIAL, 6/28 pairs share real vocabulary (was 18/28 under v2 -- 12 of those 18 pairs' overlap was purely generic RDF/RDFS/OWL boilerplate, e.g. Class/Property/domain/range/label/comment).** See `../README.md`'s v2→v3 correction section for the full cross-family comparison and methodology.

Standing: PARTIAL_ALIVE — court run complete (v2 methodology). Real vocabulary-level correspondence found for at least one family; physical-merge phase NOT started (ticket 03 item 4, real consumer-boundary check against a live ggen runtime, has not been run).

## Quick reference

- Kernel candidate: `packs/wasm4pm-pack` — **verified** to already have `ontology.ttl`, `gates/`, and `templates/` present (checked directly against the pack directory, not inferred).
- Capability-module members (real names, confirmed on disk): `packs/wasm4pm-algorithms-pack`, `packs/wasm4pm-breed-provenance-pack`, `packs/wasm4pm-cognition-pack`, `packs/wasm4pm-compat-pack`, `packs/wasm4pm-facts-pack`, `packs/wasm4pm-operator-applicability-pack`
- Profile member: `packs/wasm4pm-sandbox-pack`
- Product/use-case projection candidates (proposed to absorb as profiles, not peers): `packs/wasm4pm-interview-assist-pack`, `packs/wasm4pm-interview-site-pack`

## Scope

Unlike some families in this milestone, `wasm4pm-pack` itself is independently verified to already have the kernel shape (ontology + gates + templates present). What remains `INFERRED` is whether the six capability-module packs and two interview-product packs actually share/derive from `wasm4pm-pack`'s ontology, or merely share a naming prefix. This ticket does not claim that correspondence — it schedules the court run that would establish it.

## Acceptance criteria

1. Ticket 03's court run against this family produces a report confirming which of `wasm4pm-algorithms-pack`, `wasm4pm-breed-provenance-pack`, `wasm4pm-cognition-pack`, `wasm4pm-compat-pack`, `wasm4pm-facts-pack`, `wasm4pm-operator-applicability-pack` genuinely share ontology/query/template surface with `wasm4pm-pack`'s kernel, versus own real independent domain truth (in which case they stay `CapabilityPack`, not folded into the kernel).
2. `wasm4pm-sandbox-pack`'s role as a profile (not a capability module) is confirmed or corrected by the court's template/query diff.
3. `wasm4pm-interview-assist-pack` and `wasm4pm-interview-site-pack` are evaluated specifically for whether they are product-specific *projections* of `wasm4pm-pack` facts (supporting the "absorb as profile" proposal) or carry independent domain truth that should keep them as standalone `CapabilityPack`s — the court's consumer-boundary check (real generation output diff) is the deciding evidence, not naming similarity.
4. Any physical restructuring preserves a real consumer's generated output (before/after diff, per `CLAUDE.md` qualification discipline).
5. `python3 scripts/marketplace.py validate` and catalog determinism both pass after any change.

## Falsifiers

- A merge that folds any of the six capability packs into `wasm4pm-pack` without a cited `ADMITTED`/`PARTIAL` court report is a process violation.
- If the court finds `wasm4pm-interview-assist-pack`/`wasm4pm-interview-site-pack` have independent gates/domain rules not derivable from `wasm4pm-pack`'s ontology, the "absorb as profile" proposal is refuted for those two specifically — they stay standalone, and this ticket's scope narrows accordingly rather than failing outright.

## Outcome (court run complete, v2 methodology)

The consolidation court was re-run using `scripts/consolidation_court.py` **v2**. v1 (the original run) diffed ontologies as raw (s,p,o) triples and returned `REFUTED` for every family in this milestone (0/9 admitted) — that was found to be a methodology defect, not a real finding: every pack mints its own RDF namespace and embeds pack-specific instance data (literal source text, per-crate case names), so raw triple equality gives `common=0` even between packs that share a real class/predicate vocabulary. v2 adds a namespace-stripped **vocabulary** diff (class/predicate local names) as the verdict-driving signal, with the old instance-triple diff kept and reported but no longer determining the verdict — see `scripts/consolidation_court.py`'s module docstring for the full methodology correction.

| Family | Kernel candidate | Verdict | Vocabulary-shared | Instance-conflicting | Report |
|---|---|---|---|---|---|
| `wasm4pm` | `wasm4pm-pack` | **PARTIAL** | 18/28 pairs share real vocabulary | 28/28 pairs instance-conflicting (expected, not a defect) | `docs/jira/v26.8.19/families/wasm4pm-court-report.json` |

This is a genuine, differentiated finding — real shared vocabulary exists across most or all member-pack pairs, which v1's blanket-REFUTED result had obscured. **This does NOT authorize a physical merge yet.** Per `03-TICKET-consolidation-court-methodology.md`'s own acceptance criteria, item 4 (a real consumer project generated from the current pack vs. the proposed kernel+profile split, output diffed) is required before any physical change, and `consolidation_court.py` explicitly does not perform it (`consumer_boundary_check: null` in every report). This ticket's ADMITTED/PARTIAL verdict is therefore a genuine **candidate for a follow-up physical-merge ticket**, not a completed merge — the physical-change phase (kernel-pack creation, repointing members as profiles, real consumer diff) remains unscoped, un-started work, separate from this court-run ticket.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — wasm4pm family entry, including the verified `wasm4pm-pack` kernel-shape finding
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
