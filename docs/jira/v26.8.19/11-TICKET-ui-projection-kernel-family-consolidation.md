# 11 Ticket UI Projection Kernel Family Consolidation

**v4 correction (2026-09-14, superseding the v3 correction below the same day):** a real physical kernel+profile-split *design* pass -- not another verdict check, an attempt to actually specify the kernel pack a builder would create -- found that all 3 render-target groups' v3 ADMITTED verdict was itself a false positive of the same shape v3 fixes for RDF/RDFS/OWL: their entire universally-shared vocabulary was `ggen-create`'s own marketplace-wide tooling scaffold (a `GenerationSubject` individual with 10 name-casing predicates), confirmed present in 26 of this marketplace's 318 packs including packs with zero relationship to UI/shadcn/deck.gl/React. `scripts/consolidation_court.py` v4 excludes this (`TOOLING_VOCAB_NAMESPACES`) the same way v3 excludes generic RDF vocabulary. Re-run under v4: **REFUTED in all 3 render-target groups (shadcn 0/36, deckgl 0/3, react/remotion 0/3) -- zero real, family-specific shared vocabulary in any group.** Separately, the same design pass found this repository has no live cross-pack ontology-import mechanism at all (`[ontology].imports` is intra-pack only; `extra_ontologies` is never populated anywhere in 318 packs) -- so even a group that did show real overlap could not yet be physically split via kernel-import composition. No kernel pack should be built for this family. See `../README.md`'s v3→v4 correction section for the full cross-family comparison and methodology.

**v3 correction (2026-09-14, superseded above the same day):** `scripts/consolidation_court.py` was corrected a second time (v2→v3) after direct measurement showed v2's "shared vocabulary" signal was inflated by generic RDF/RDFS/OWL/XSD meta-vocabulary (Class, Property, domain, range, label, comment, ...) that any two hand-authored `ontology.ttl` files share regardless of real domain overlap. Re-run under v3: ADMITTED, unchanged, in all 3 render-target groups (shadcn 36/36, deckgl 3/3, react/remotion 3/3) -- this verdict did NOT survive the v4 tooling-vocabulary check above.

Standing: PARTIAL_ALIVE — court run complete (v2 methodology). Real vocabulary-level correspondence found for at least one family; physical-merge phase NOT started (ticket 03 item 4, real consumer-boundary check against a live ggen runtime, has not been run).

## Quick reference

- Proposed shape: `ui-projection-kernel -> render profiles{shadcn, deckgl, react, remotion, chrome-extension} -> domain ABoxes{bitjob, kgc, mfact, observatory, trialbase, ...}`. Domain state should be RDF/world truth; UI is a reversible projection, not a new authority-bearing pack class.
- Member packs (real names, confirmed on disk), grouped by render target:
  - shadcn: `packs/ai-chatbot-shadcn-pack`, `packs/bitjob-chrome-ext-shadcn-pack`, `packs/dev-my-app-shadcn-pack`, `packs/jotp-benchmark-site-shadcn-pack`, `packs/kgc-4d-playground-shadcn-pack`, `packs/kgc-sidecar-dashboard-shadcn-pack`, `packs/nextjs-ai-sdk-ui-shadcn-pack`, `packs/optimus-shadcn-pack`, `packs/trialbase-dashboard-shadcn-pack`
  - deckgl: `packs/mfact-ui-deckgl-pack`, `packs/neako-web-deckgl-pack`, `packs/observatory-ui-deckgl-pack`
  - react/remotion/other: `packs/phage-wars-3-react-pack`, `packs/remotion-y6f9kf-react-pack`, `packs/cyberpunk-tv-platform`
- No `ui-projection-kernel` pack exists yet on disk; this family, unlike TCPS or Fortune5/EA, requires creating a new kernel from scratch if `ADMITTED`, not just re-pointing existing packs at an existing core.

## Scope

This is explicitly the second-biggest consolidation opportunity in the source audit and the riskiest to get wrong: 15 packs each currently own their own UI manufacturing surface. The audit's own framing — do not create independent UI authority per pack; domain state is RDF/world truth, UI is a reversible projection — is the hypothesis the court must test per pack, not assume.

Note `packs/cyberpunk-tv-platform` does not follow the `-pack` naming suffix used by every other pack in this family (and in the marketplace generally). Confirmed on disk: it does contain a `pack.toml`, so it is a conformant pack directory — the naming irregularity alone is worth flagging in the court report, but is not grounds to exclude it.

## Acceptance criteria

1. Court report groups the 15 (or 14, pending the `cyberpunk-tv-platform` check above) member packs by render-target profile (`shadcn`/`deckgl`/`react`/`remotion`/`chrome-extension`) via template correspondence, confirming or correcting the grouping given in Quick Reference.
2. For each render-target group, court report determines whether member packs share a genuine reversible-projection template grammar (candidate profile) or each hand-rolls incompatible UI logic (stays independent `CapabilityPack`).
3. Court report separately evaluates each pack's *domain* ontology (bitjob/kgc/mfact/observatory/trialbase/etc.) to confirm domain truth is not itself duplicated by the UI pack (i.e., the UI pack should consume, not re-derive, domain RDF that may already live in a separate non-UI pack) — flag any pack found to be manufacturing its own domain facts rather than projecting them.
4. If `ADMITTED` for a given render-target group, this ticket's physical-change phase creates `ui-projection-kernel` (new pack, `KernelPack` per ticket 02) and repoints that group's members as profiles — done incrementally per render-target group, not all 15 in one PR.
5. Real consumer generation output diffed before/after for at least one pack per render-target group that undergoes physical change.
6. `python3 scripts/marketplace.py validate` and catalog determinism pass after each incremental change.

## Falsifiers

- A single PR attempting to fold all 15 packs into one kernel at once, skipping the render-target grouping and per-group verification, violates criterion 4 and should be rejected regardless of court verdict.
- If the court finds a given pack's UI templates encode domain-specific business logic inseparable from render mechanics (e.g. `bitjob-chrome-ext-shadcn-pack` embeds bitjob-specific rules no other shadcn pack shares), that pack is excluded from the shadcn profile group and stays a standalone `CapabilityPack`, not forced into the kernel.
- (Removed: `packs/cyberpunk-tv-platform` was checked and does contain `pack.toml` — it stays in scope for this family, subject only to the naming-irregularity note above.)

## Outcome (court run complete, v2 methodology)

The consolidation court was re-run using `scripts/consolidation_court.py` **v2**. v1 (the original run) diffed ontologies as raw (s,p,o) triples and returned `REFUTED` for every family in this milestone (0/9 admitted) — that was found to be a methodology defect, not a real finding: every pack mints its own RDF namespace and embeds pack-specific instance data (literal source text, per-crate case names), so raw triple equality gives `common=0` even between packs that share a real class/predicate vocabulary. v2 adds a namespace-stripped **vocabulary** diff (class/predicate local names) as the verdict-driving signal, with the old instance-triple diff kept and reported but no longer determining the verdict — see `scripts/consolidation_court.py`'s module docstring for the full methodology correction.

| Family | Kernel candidate | Verdict | Vocabulary-shared | Instance-conflicting | Report |
|---|---|---|---|---|---|
| `ui-shadcn` | `ai-chatbot-shadcn-pack` | **ADMITTED** | 36/36 pairs share real vocabulary | 36/36 pairs instance-conflicting (expected, not a defect) | `docs/jira/v26.8.19/families/ui-shadcn-court-report.json` |
| `ui-deckgl` | `mfact-ui-deckgl-pack` | **ADMITTED** | 3/3 pairs share real vocabulary | 3/3 pairs instance-conflicting (expected, not a defect) | `docs/jira/v26.8.19/families/ui-deckgl-court-report.json` |
| `ui-react-remotion` | `phage-wars-3-react-pack` | **ADMITTED** | 3/3 pairs share real vocabulary | 3/3 pairs instance-conflicting (expected, not a defect) | `docs/jira/v26.8.19/families/ui-react-remotion-court-report.json` |

This is a genuine, differentiated finding — real shared vocabulary exists across most or all member-pack pairs, which v1's blanket-REFUTED result had obscured. **This does NOT authorize a physical merge yet.** Per `03-TICKET-consolidation-court-methodology.md`'s own acceptance criteria, item 4 (a real consumer project generated from the current pack vs. the proposed kernel+profile split, output diffed) is required before any physical change, and `consolidation_court.py` explicitly does not perform it (`consumer_boundary_check: null` in every report). This ticket's ADMITTED/PARTIAL verdict is therefore a genuine **candidate for a follow-up physical-merge ticket**, not a completed merge — the physical-change phase (kernel-pack creation, repointing members as profiles, real consumer diff) remains unscoped, un-started work, separate from this court-run ticket.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — UI/application projection family entry
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`

## Consumer-boundary check (ticket 03 item 4) — BEFORE baseline captured

Ran the real `ggen` 26.8.18 binary against this family's ADMITTED kernel candidate(s) from a real, isolated `/tmp/court-consumer-<family>` consumer project (`[packs]` path reference, per `docs/how-to/consume-a-pack.md`). This is the **BEFORE** half of item 4's required check — proof the current, unmerged pack actually generates, successfully and deterministically:

| Family | Kernel candidate | Files generated | Graph hash | Deterministic on replay |
|---|---|---|---|---|
| `ui-shadcn` | `ai-chatbot-shadcn-pack` | 6 files | `1180a28962a45ea8...` | True |
| `ui-deckgl` | `mfact-ui-deckgl-pack` | 5 files | `1dc6e597614703db...` | True |
| `ui-react-remotion` | `phage-wars-3-react-pack` | 7 files | `9bdc3b0ba8fdaf14...` | True |

Raw evidence committed at `docs/jira/v26.8.19/families/consumer-boundary/<family>-before.json` (full file lists, full hashes). **This is not yet the full item-4 check**: there is no **AFTER** state, because no kernel-split pack has been created for this family — physically creating one is real, unstarted follow-up work, out of scope for this court-run/baseline-capture pass. Do not read this section as authorizing a physical merge.
