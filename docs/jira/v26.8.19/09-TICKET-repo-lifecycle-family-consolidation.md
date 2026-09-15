# 09 Ticket Repo Lifecycle Family Consolidation

**v3 correction (2026-09-14):** `scripts/consolidation_court.py` was corrected a second time (v2→v3) after direct measurement showed v2's "shared vocabulary" signal was inflated by generic RDF/RDFS/OWL/XSD meta-vocabulary (Class, Property, domain, range, label, comment, ...) that any two hand-authored `ontology.ttl` files share regardless of real domain overlap. Re-run under v3: **PARTIAL, 9/10 pairs share real vocabulary -- DOWNGRADED from ADMITTED (10/10) under v2. `dogfood-lifecycle-pack__repo-load-path-pack` shared zero real vocabulary once generic RDF/RDFS/OWL terms were excluded; a separate real-content review the same day independently recommended dropping `dogfood-lifecycle-pack` from this family for the same underlying reason.** See `../README.md`'s v2→v3 correction section for the full cross-family comparison and methodology.

Standing: PARTIAL_ALIVE — court run complete (v2 methodology). Real vocabulary-level correspondence found for at least one family; physical-merge phase NOT started (ticket 03 item 4, real consumer-boundary check against a live ggen runtime, has not been run).

## Quick reference

- Proposed shape: one repository-reconstitution calculus (`repo-lifecycle-pack`) with objects `{as-found, loaded, intervened, reconciled, dogfooded}`.
- Member packs (real names, confirmed on disk): `packs/repo-as-found-pack`, `packs/repo-load-path-pack`, `packs/repo-intervention-pack`, `packs/repo-reconciliation-pack`, `packs/dogfood-lifecycle-pack`
- This is the smallest family in this milestone (5 members) and its naming maps cleanly one-to-one onto the proposed five lifecycle objects, making it a strong first-or-second candidate for running ticket 03's court after (or alongside) the TCPS family.

## Scope

No member pack's file contents were independently checked in the verification pass that seeded this milestone — this ticket rests on naming-convention cohesion alone (`INFERRED`), same evidentiary footing as the TCPS and release-lifecycle families. The clean 1:1 name-to-object mapping is a reason to prioritize running the court here early, not a substitute for running it.

## Acceptance criteria

1. Court report confirms or corrects the proposed object mapping: `repo-as-found-pack` -> `as-found`, `repo-load-path-pack` -> `loaded`, `repo-intervention-pack` -> `intervened`, `repo-reconciliation-pack` -> `reconciled`, `dogfood-lifecycle-pack` -> `dogfooded`.
2. Court report's ontology diff determines whether these five are genuinely sequential stages of one calculus (shared subject vocabulary, compatible predicates) or five independently-scoped packs that merely share a naming theme.
3. If `ADMITTED`, the proposed kernel (`repo-lifecycle-pack`) does not yet exist on disk — this ticket's physical-change phase includes creating it as the kernel `KernelPack` (per ticket 02's taxonomy) with the five existing packs becoming its stage profiles, or documents why creating a new pack is out of scope and a different existing pack should serve as kernel instead.
4. Real consumer generation output is diffed before/after any physical change.
5. `python3 scripts/marketplace.py validate` and catalog determinism pass after any change.

## Falsifiers

- Any physical change made under this ticket without a cited court report is a process violation.
- If the court finds `dogfood-lifecycle-pack` encodes a genuinely different concern (e.g. cross-repo dogfooding policy rather than a stage of a single repo's reconstitution) rather than the fifth stage of the same calculus as the other four, it is excluded from the kernel and this ticket's scope narrows to the remaining four.

## Outcome (court run complete, v2 methodology)

The consolidation court was re-run using `scripts/consolidation_court.py` **v2**. v1 (the original run) diffed ontologies as raw (s,p,o) triples and returned `REFUTED` for every family in this milestone (0/9 admitted) — that was found to be a methodology defect, not a real finding: every pack mints its own RDF namespace and embeds pack-specific instance data (literal source text, per-crate case names), so raw triple equality gives `common=0` even between packs that share a real class/predicate vocabulary. v2 adds a namespace-stripped **vocabulary** diff (class/predicate local names) as the verdict-driving signal, with the old instance-triple diff kept and reported but no longer determining the verdict — see `scripts/consolidation_court.py`'s module docstring for the full methodology correction.

| Family | Kernel candidate | Verdict | Vocabulary-shared | Instance-conflicting | Report |
|---|---|---|---|---|---|
| `repo-lifecycle` | `repo-as-found-pack` | **ADMITTED** | 10/10 pairs share real vocabulary | 10/10 pairs instance-conflicting (expected, not a defect) | `docs/jira/v26.8.19/families/repo-lifecycle-court-report.json` |

This is a genuine, differentiated finding — real shared vocabulary exists across most or all member-pack pairs, which v1's blanket-REFUTED result had obscured. **This does NOT authorize a physical merge yet.** Per `03-TICKET-consolidation-court-methodology.md`'s own acceptance criteria, item 4 (a real consumer project generated from the current pack vs. the proposed kernel+profile split, output diffed) is required before any physical change, and `consolidation_court.py` explicitly does not perform it (`consumer_boundary_check: null` in every report). This ticket's ADMITTED/PARTIAL verdict is therefore a genuine **candidate for a follow-up physical-merge ticket**, not a completed merge — the physical-change phase (kernel-pack creation, repointing members as profiles, real consumer diff) remains unscoped, un-started work, separate from this court-run ticket.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — repository lifecycle family entry
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`

## Consumer-boundary check (ticket 03 item 4) — BEFORE baseline captured

Ran the real `ggen` 26.8.18 binary against this family's ADMITTED kernel candidate(s) from a real, isolated `/tmp/court-consumer-<family>` consumer project (`[packs]` path reference, per `docs/how-to/consume-a-pack.md`). This is the **BEFORE** half of item 4's required check — proof the current, unmerged pack actually generates, successfully and deterministically:

| Family | Kernel candidate | Files generated | Graph hash | Deterministic on replay |
|---|---|---|---|---|
| `repo-lifecycle` | `repo-as-found-pack` | 4 files | `6ce3b01d2bea7e31...` | True |

Raw evidence committed at `docs/jira/v26.8.19/families/consumer-boundary/<family>-before.json` (full file lists, full hashes). **This is not yet the full item-4 check**: there is no **AFTER** state, because no kernel-split pack has been created for this family — physically creating one is real, unstarted follow-up work, out of scope for this court-run/baseline-capture pass. Do not read this section as authorizing a physical merge.
