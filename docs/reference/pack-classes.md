# Pack Classes

Seven portfolio-role labels applied to individual packs, orthogonal to `Pack.profile`'s
generation-shape derivation (`project`/`projection`/`semantic` in `scripts/marketplace.py`).
Where `Pack.profile` answers "what does this pack generate from," pack class answers "what
role does this pack play in the portfolio."

Class assignment is a portfolio-organization label only. It does not alter `ggen sync run`
output for any consumer, and it is not wired into `build_pack_archive()`, `catalog_record()`'s
`digest`/`size_bytes`/`ontology_fingerprint_sha256`, or any other generation-affecting
computation — it is informational metadata surfaced via the `pack_class` field on the catalog
record. The field is optional and nullable: only packs whose file contents have actually been
checked are seeded in `PACK_CLASSES` (`scripts/marketplace.py`); every other pack is
deliberately unclassified (`null`) rather than guess-classified.

## The seven classes

| Class | Role |
|---|---|
| `KernelPack` | Owns a canonical ontology other packs project from; no domain-specific product surface. |
| `CapabilityPack` | A legitimate, independently-owned capability module — real domain truth, not a mere profile of a kernel. |
| `ProfilePack` | A parameterized projection of a `KernelPack`'s ontology into one target (render stack, language, platform). |
| `WorldPack` | Owns falsifiers/authority ceilings for one simulated or game-like domain (e.g. gym/world packs) — deliberately not merged with sibling worlds. |
| `CompatibilityPack` | Kept on disk solely to preserve resolution for existing consumers of a retired pack. |
| `EvidencePack` | Owns receipt/standing/assurance semantics (SHACL, affidavit, certification evidence). |
| `ReleaseControlPack` | Owns release/CI/publication state-machine semantics. |

## Worked examples

These are the only packs whose file contents were actually checked as of this milestone
(`docs/jira/v26.8.19/00-PACK-PORTFOLIO-MATURITY-AUDIT.md`), so they are the only ones seeded
in `PACK_CLASSES`:

- `clap-noun-verb-pack` — `CompatibilityPack`. Retired from normal discovery per
  `docs/jira/v26.8.19/01-TICKET-retire-clap-noun-verb-legacy.md`; kept on disk only so
  path-pinned consumers keep resolving.
- `clap-noun-verb-schema-pack`, `clap-noun-verb-crate-pack`, `clap-noun-verb-routing-pack`,
  `clap-noun-verb-behavior-pack`, `clap-noun-verb-boundary-pack`,
  `clap-noun-verb-verification-pack` — `ProfilePack`. The six successor packs named by
  `clap-noun-verb-pack`'s own deprecation text; each projects a target-specific facet of the
  retired pack's ontology.
- `pack-authoring-pack` — `KernelPack`. Owns the canonical pack-authoring ontology other packs
  project from.
- `pack-maturity-pack` — `EvidencePack`. Owns maturity/standing evidence semantics.
- `wasm4pm-pack` — `CapabilityPack`. An independently-owned WASM-for-project-management
  capability, not a profile of another pack's kernel.

## See Also

- `docs/jira/v26.8.19/02-TICKET-pack-class-taxonomy.md` — the ticket this doc satisfies
- `docs/jira/v26.8.19/01-TICKET-retire-clap-noun-verb-legacy.md` — the deprecation this doc's
  `CompatibilityPack` example is grounded in
- `docs/reference/pack-contract.md` — the structural `Pack.profile` axis this taxonomy sits
  alongside
