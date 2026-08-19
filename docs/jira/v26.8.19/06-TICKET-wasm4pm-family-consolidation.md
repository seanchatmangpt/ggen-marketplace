# 06 Ticket Wasm4pm Family Consolidation

Standing: PARTIAL_ALIVE. **BLOCKED on ticket 03** — no physical merge until a family-consolidation proof exists for this family.

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

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — wasm4pm family entry, including the verified `wasm4pm-pack` kernel-shape finding
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
