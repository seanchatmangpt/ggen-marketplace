# 02 Ticket Pack Class Taxonomy

Standing: PARTIAL_ALIVE, **ADMISSION-REQUIRED**. This ticket introduces a classification vocabulary only. It does not move, merge, or delete a single pack, and must not be read as authorizing any of that — physical consolidation is gated separately by ticket 03.

## Quick reference

- Introduce seven pack classes: `KernelPack`, `CapabilityPack`, `ProfilePack`, `WorldPack`, `CompatibilityPack`, `EvidencePack`, `ReleaseControlPack`.
- Landing site: either a `pack_class` field recognized by `scripts/marketplace.py`'s `Pack` dataclass, or a companion taxonomy doc under `docs/reference/` — implementer's choice, acceptance criteria below decide which is acceptable.
- This is an ontology-level change: it must go through `star-toml`/admission the same way `marketplace.toml` does, per this repo's own control-plane doctrine — no shadow classification file that bypasses admission.

## Why this ticket exists

The portfolio audit's biggest structural finding (see `00-PACK-PORTFOLIO-MATURITY-AUDIT.md`) is that 143 on-disk pack directories are not 143 peer concepts. `scripts/marketplace.py`'s current `Pack.profile` already derives three structural profiles (`project`/`projection`/`semantic`) from directory contents — this ticket proposes a second, orthogonal classification axis for *portfolio role*, not generation shape.

## Proposed class definitions (draft, subject to admission review)

| Class | Role |
|---|---|
| `KernelPack` | Owns a canonical ontology other packs project from; no domain-specific product surface. |
| `CapabilityPack` | A legitimate, independently-owned capability module — real domain truth, not a mere profile of a kernel. |
| `ProfilePack` | A parameterized projection of a `KernelPack`'s ontology into one target (render stack, language, platform). |
| `WorldPack` | Owns falsifiers/authority ceilings for one simulated or game-like domain (e.g. gym/world packs) — deliberately not merged with sibling worlds. |
| `CompatibilityPack` | Kept on disk solely to preserve resolution for existing consumers of a retired pack (see ticket 01's pattern). |
| `EvidencePack` | Owns receipt/standing/assurance semantics (SHACL, affidavit, certification evidence). |
| `ReleaseControlPack` | Owns release/CI/publication state-machine semantics. |

These definitions are drafts for the admission process to accept, amend, or reject — this ticket is not itself the admission.

## Acceptance criteria

1. The seven classes are defined in exactly one authoritative location (either the `Pack` dataclass in `scripts/marketplace.py` as an enum/literal field, or a new `docs/reference/pack-classes.md` — not both, to avoid a second source of truth per this repo's own doctrine).
2. If landed in `scripts/marketplace.py`, the field is optional/nullable for existing packs (no pack.toml is broken by this change) and validated the same way other `[pack]` fields are (deny-unknown-values if an enum, per FM-PACK-003's admission discipline already established for `clap-noun-verb-pack`).
3. `python3 scripts/marketplace.py validate` and the catalog a/b/cmp determinism check both pass unchanged for every existing pack (no pack.toml edits are required by this ticket alone).
4. The taxonomy document/field explicitly states that class assignment is a portfolio-organization label, not a generation-behavior change — assigning a class to a pack must not alter `ggen sync run` output for any consumer.
5. At least the `clap-noun-verb-pack` family (from ticket 01) and the `pack-authoring-pack`/`pack-maturity-pack`/`wasm4pm-pack` families (verified-true in the audit) are used as the worked examples in the taxonomy doc, since those are the packs whose file contents were actually checked in this milestone.
6. This ticket's own PR does not merge, delete, or move any pack directory. A PR that does so under cover of this ticket fails review.

## Falsifiers

- If any existing pack fails `marketplace.py validate` after this lands, the taxonomy was not made backward-compatible — fix forward, do not force-classify every pack in the same PR.
- If class assignment changes catalog `sha256`/`download_url` computation for a pack whose content didn't change, the field was wired into the wrong part of `catalog_record()`.
- If a reviewer finds this ticket's PR also deletes or physically merges a pack, that is out of scope and must be split into a ticket-03-gated follow-up.

## See Also

- `../../reference/pack-classes.md` — the landed taxonomy doc satisfying this ticket
- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — origin of the seven-class proposal
- `03-TICKET-consolidation-court-methodology.md` — the gate any *physical* consolidation must pass, independent of this taxonomy
- `CLAUDE.md` — `Pack.profile` derivation this taxonomy sits alongside, and the marketplace control-plane admission doctrine (`star-toml`/`admit-config.sh`)
