# 07 Ticket Fortune5 EA Family Consolidation

Standing: PARTIAL_ALIVE — court run complete (v2 methodology). Real vocabulary-level correspondence found for at least one family; physical-merge phase NOT started (ticket 03 item 4, real consumer-boundary check against a live ggen runtime, has not been run).

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

## Outcome (court run complete, v2 methodology)

The consolidation court was re-run using `scripts/consolidation_court.py` **v2**. v1 (the original run) diffed ontologies as raw (s,p,o) triples and returned `REFUTED` for every family in this milestone (0/9 admitted) — that was found to be a methodology defect, not a real finding: every pack mints its own RDF namespace and embeds pack-specific instance data (literal source text, per-crate case names), so raw triple equality gives `common=0` even between packs that share a real class/predicate vocabulary. v2 adds a namespace-stripped **vocabulary** diff (class/predicate local names) as the verdict-driving signal, with the old instance-triple diff kept and reported but no longer determining the verdict — see `scripts/consolidation_court.py`'s module docstring for the full methodology correction.

| Family | Kernel candidate | Verdict | Vocabulary-shared | Instance-conflicting | Report |
|---|---|---|---|---|---|
| `fortune5-ea` | `fortune5-enterprise-architecture-pack` | **PARTIAL** | 29/36 pairs share real vocabulary | 36/36 pairs instance-conflicting (expected, not a defect) | `docs/jira/v26.8.19/families/fortune5-ea-court-report.json` |

This is a genuine, differentiated finding — real shared vocabulary exists across most or all member-pack pairs, which v1's blanket-REFUTED result had obscured. **This does NOT authorize a physical merge yet.** Per `03-TICKET-consolidation-court-methodology.md`'s own acceptance criteria, item 4 (a real consumer project generated from the current pack vs. the proposed kernel+profile split, output diffed) is required before any physical change, and `consolidation_court.py` explicitly does not perform it (`consumer_boundary_check: null` in every report). This ticket's ADMITTED/PARTIAL verdict is therefore a genuine **candidate for a follow-up physical-merge ticket**, not a completed merge — the physical-change phase (kernel-pack creation, repointing members as profiles, real consumer diff) remains unscoped, un-started work, separate from this court-run ticket.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — Fortune5/EA family entry and verified core-pack finding
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
