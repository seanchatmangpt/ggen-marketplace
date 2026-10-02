# tcps-pack (ffi module)

Absorbed verbatim from `tcps-ffi-pack` v0.1.0: TCPS FFI crate (`tcps-ffi`) —
stable C ABI over tcps-core; RDF spec (LibModule/HeaderFile/CargoManifest
individuals with verbatim `sourceText`) + SHACL shapes + Rust/C templates for
`src/lib.rs`, `include/tcps.h`, and `Cargo.toml`. Namespace verbatim:
`tcps_ffi:` = `http://seanchatmangpt.github.io/packs/tcps-ffi#`.

- Ontology: `ontology/ffi.ttl` — `LibRsModule`, `TcpsHeaderFile`,
  `CargoManifestFile` (dependsOn `LibRsModule`).
- Templates: `ffi_lib_rs.tmpl` (→ `crates/tcps-ffi/src/lib.rs`; family-prefixed),
  `ffi_cargo_toml.tmpl` (→ `crates/tcps-ffi/Cargo.toml`; family-prefixed),
  `tcps_h.tmpl` (→ `crates/tcps-ffi/include/tcps.h`).
- Gates: `ffi_010_required.rq` (typed individuals must HAVE sourceText),
  `ffi_030_value_constraints.rq` (present sourceText must be non-empty),
  `ffi_040_depends_on_declared.rq` (dependency targets must be named).
- Reference note: the pack's 3 vendored `reference/製品版` files were
  byte-identical members of the canonical snapshot now at
  `reference/製品版/` (crates/tcps-ffi/Cargo.toml, crates/tcps-ffi/src/lib.rs,
  include/tcps.h) — dropped with the absorption, attested by the canonical
  snapshot and its own internal SOURCE_MANIFEST.sha256.
