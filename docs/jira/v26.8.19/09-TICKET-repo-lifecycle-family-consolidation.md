# 09 Ticket Repo Lifecycle Family Consolidation

Standing: PARTIAL_ALIVE. **BLOCKED on ticket 03** — no physical merge until a family-consolidation proof exists for this family.

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

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — repository lifecycle family entry
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
