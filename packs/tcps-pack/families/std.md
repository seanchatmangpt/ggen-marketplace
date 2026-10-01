# tcps-pack (std module)

Absorbed verbatim from `tcps-std-pack` v0.1.0: receipt persistence
(受領証を保存する / 受領証を文字列化する) and environment observation (実行環境)
for 豊田コード生産方式, std-dependent, depends on tcps-core. Namespace verbatim:
`tcps_std:` = `http://seanchatmangpt.github.io/packs/tcps-std#`.

- Ontology: `ontology/std.ttl` — `LibModule` (forbid(unsafe_code) persistence +
  実行環境), `CargoManifest`, adversarial persistence case individuals
  (`pscValidRoot`, `pscRootBlockedByFile`).
- Templates: `std_lib_rs.tmpl` (→ `crates/tcps-std/src/lib.rs`;
  family-prefixed), `std_cargo_toml.tmpl` (→ `crates/tcps-std/Cargo.toml`;
  family-prefixed), `persistence_sabotage_proof.rs.tmpl` (→
  `crates/tcps-std/tests/tcps_std_persistence_sabotage_proof.rs`).
- Gates: `std_010_required.rq` (Modules must HAVE sourceText),
  `std_030_value_constraints.rq` (present sourceText must be non-empty).
