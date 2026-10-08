# Release v26.10.8

Release notes for ggen-marketplace v26.10.8. Standing vocabulary per the repository doctrine:
claims below are marked where they rest on runs not executed in this release.

## Highlights

- **rust-wasi-wasmex-pack consolidation.** The rust-wasi-wasmex pack family was consolidated
  into `rust-wasi-wasmex-pack`; 2 precursor packs are deprecated via the pack lifecycle
  registry (`lifecycle.toml`), preserving exact provenance per the consolidation procedure
  (`docs/how-to/consolidate-a-pack-family.md`).
- **4-court qualification matrix, 28/28.** The qualification court matrix covers 4 courts;
  the recorded run is 28/28 passing.
- **Section-level `one_of` rendering.** Template projection renders `one_of` at section
  granularity instead of per-field, eliminating duplicated enumeration blocks in generated
  consumers.
- **L4/L5 doctrine doc.** `docs/reference/` gains the Level-4/Level-5 maturity doctrine
  document, aligning the maturity contract with the seven-dimension closure law.

## Known limitations

- The `[ggen]` pin remains `v26.8.11` (frozen-court identity, tag-to-commit binding); pin
  bump is user-gated (`BLOCKED:pin-bump-user-gated`, see `marketplace.toml`).
- The 28/28 court-matrix figure and the section-level `one_of` rendering claim are recorded
  from the fleet campaign lanes that own `packs/` and `tests/`; they are not re-run here.

## See Also

- [Release v26.9.30](release-v26.9.30.md)
- [Pack lifecycle registry](pack-lifecycle-registry.md)
- [Level 5 maturity contract](level5-maturity-contract.md)
- [Conformance courts index](CONFORMANCE-COURTS.md)
