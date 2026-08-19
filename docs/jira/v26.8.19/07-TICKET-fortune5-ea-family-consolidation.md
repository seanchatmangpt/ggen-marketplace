# 07 Ticket Fortune5 EA Family Consolidation

Standing: PARTIAL_ALIVE. **BLOCKED on ticket 03** — no physical merge until a family-consolidation proof exists for this family.

## Quick reference

- Proposed shape: `enterprise-architecture-core -> togaf-adm -> profiles{fortune5, github, chatman, self-play} -> concerns{required-capabilities, deployment-blocks, testing}`.
- Core candidate: `packs/fortune5-enterprise-architecture-pack` — **verified** to already contain `README.md`, `ontology.ttl`, `queries/010_architecture_surface.rq`, `shapes/fortune5-profile.shacl.ttl`, `gates/010_admission.rq`, `evidence/composition-contract.md` (checked directly, not inferred).
- Standard reference kept separate: `packs/togaf-adm-pack` (proposed `KEEP STANDARD`, not folded in — it likely represents the TOGAF ADM standard itself rather than a Fortune5-specific profile).
- Related/member packs (real names, confirmed on disk): `packs/fortune5-architecture-pack`, `packs/fortune5-deployment-blocks-pack`, `packs/fortune5-required-capabilities-pack`, `packs/fortune5-testing-bblock-pack`, `packs/enterprise-architecture-connection-pack`, `packs/gh-enterprise-architecture-pack`, `packs/chatman-togaf-closure-pack`, `packs/safe-ea-strategy-self-play-pack`

## Scope

`fortune5-enterprise-architecture-pack`'s file contents are independently verified to already resemble a mature core (ontology + queries + SHACL shapes + gates + evidence all present). Whether the other eight packs listed above are genuine profiles/concerns over that same ontology, or independent architecture authorities that happen to share vocabulary, is `INFERRED` and is exactly what ticket 03's court decides.

Note `packs/fortune5-architecture-pack` and `packs/fortune5-enterprise-architecture-pack` are two distinct, similarly-named directories on disk — the court run must explicitly resolve whether one is legacy/subset of the other (an overlap-review case, similar in kind to the `ggen-self-pack`/`ggen-self-host-pack` overlap noted elsewhere in the source audit) before proposing either as sole kernel.

## Acceptance criteria

1. Court report resolves the `fortune5-architecture-pack` vs `fortune5-enterprise-architecture-pack` naming overlap first — same-thing-different-name, superset/subset, or genuinely distinct — before any profile assignment is finalized.
2. Court report evaluates `fortune5-deployment-blocks-pack`, `fortune5-required-capabilities-pack`, `fortune5-testing-bblock-pack` as `concerns` (per the proposed shape) via query/template correspondence against the core.
3. Court report evaluates `enterprise-architecture-connection-pack`, `gh-enterprise-architecture-pack`, `chatman-togaf-closure-pack`, `safe-ea-strategy-self-play-pack` as candidate `profiles` (github/chatman/self-play framing) rather than assumed to fit that framing.
4. `togaf-adm-pack` is confirmed to remain standalone (standard reference, not a profile) unless the court's ontology diff shows otherwise.
5. Real consumer generation output is diffed before/after any physical change.
6. `python3 scripts/marketplace.py validate` and catalog determinism pass after any change.

## Falsifiers

- A merge proceeding without resolving the `fortune5-architecture-pack`/`fortune5-enterprise-architecture-pack` overlap first is invalid — this is the single highest-risk ambiguity in this family and must be closed before anything else.
- Any physical change lacking a cited `ADMITTED`/`PARTIAL` court report is a process violation.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — Fortune5/EA family entry and verified core-pack finding
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
