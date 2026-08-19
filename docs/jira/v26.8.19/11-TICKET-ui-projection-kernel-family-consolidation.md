# 11 Ticket UI Projection Kernel Family Consolidation

Standing: PARTIAL_ALIVE. **BLOCKED on ticket 03** — no physical merge until a family-consolidation proof exists for this family. This is the largest family in the milestone by member count; treat the court run here as the highest-effort item among the family tickets.

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

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — UI/application projection family entry
- `03-TICKET-consolidation-court-methodology.md`
- `02-TICKET-pack-class-taxonomy.md`
