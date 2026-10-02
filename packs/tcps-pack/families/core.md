# tcps-pack (core module — the kernel)

Absorbed verbatim from `tcps-core-pack` v0.1.0 (the lifecycle-designated
"Kernel candidate for the 24-module no_std crate"; content anchors of this
consolidation). Namespace verbatim: `tcps:` =
`http://seanchatmangpt.github.io/packs/tcps-core#` — note this is a DIFFERENT
IRI space from the cli module's `tcps:` prefix (…/packs/tcps-cli#); disjoint
IRIs, no two-owner IRIs.

- Ontology: `ontology/core.ttl` — 24-module no_std module set (語彙, 原点,
  系譜, 品質, 標準作業, 自働化, かんばん, 必要時生産, 平準化, アンドン, 改善,
  受領証, …) with verbatim Rust `tcps:sourceText` literals.
- Templates: `core_lib_rs.tmpl` (→ `src/lib.rs`, family-prefixed: collided
  with ffi/std/wasm `lib.rs.tmpl`), `pokayoke_sabotage_proof.rs.tmpl` (→
  `tests/tcps_core_pokayoke_sabotage_proof.rs`), and the 26 Japanese-stem
  module templates (→ `src/<概念>.rs`) — names conserved verbatim.
- Gates: `core_010_dangling_reference.rq` (dependsOnModule targets must be
  declared), `core_020_referenced_module_name.rq` (referenced modules must be
  named) — translated from the pack's SHACL shapes.
- Vendored state: the canonical product snapshot `reference/製品版/` (132
  files) moved here from tcps-core-pack; `source-manifest.json` (43 ordered
  crate sources, hash-verified against the snapshot) moved with it. The older
  internal second snapshot `豊田コード生産方式_v26.7.19/` (40 files; 27
  byte-identical to 製品版, 13 unique to that revision) was retired — hashes
  and origin recorded in
  `reference/SOURCE_MANIFEST.retired-豊田コード生産方式_v26.7.19.sha256`.
