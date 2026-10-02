# tcps-pack (wasm module)

Absorbed verbatim from `tcps-wasm-pack` v0.1.0: WebAssembly capability
boundary (版番号 / 正準選択 `extern "C"` exports) for 豊田コード生産方式,
depends on tcps-core; unsafe_code allowed at the FFI boundary only. Namespace
verbatim: `tcps_wasm:` = `http://seanchatmangpt.github.io/packs/tcps-wasm#`.

- Ontology: `ontology/wasm.ttl` — `LibModule` (`tcps_wasm_version_v1`,
  `tcps_wasm_select_canonical_v1`), `CargoManifest`.
- Templates: `wasm_lib_rs.tmpl` (→ `crates/tcps-wasm/src/lib.rs`;
  family-prefixed), `wasm_cargo_toml.tmpl` (→ `crates/tcps-wasm/Cargo.toml`;
  family-prefixed).
- Gates: `wasm_010_required.rq` (Module needs sourceText; Manifest needs
  manifestText), `wasm_030_value_constraints.rq` (present values non-empty).
