# tcps-pack (cli module)

Absorbed verbatim from `tcps-cli-pack` v0.1.0: Toyota Production System (TCPS)
CLI ontology — the `tcps-cli` crate (2 binaries: `tcps` main CLI, `tcps-bench`)
RDF spec + SHACL shapes + Rust bin templates for the 豊田コード生産方式 CLI.
Namespace verbatim: `tcps:` = `http://seanchatmangpt.github.io/packs/tcps-cli#`
(a different IRI space from the core module's `tcps:`).

- Ontology: `ontology/cli.ttl` — `CargoTomlModule`, `MainModule` (`src/main.rs`),
  `KijunModule` (`src/基準.rs`), CLI case individuals (`cliInspectSucceeds`,
  `cliVersionSucceeds`).
- Templates: `cli_cargo_toml.tmpl` (→ `crates/tcps-cli/Cargo.toml`;
  family-prefixed: collided with ffi/std/wasm `cargo_toml.tmpl`),
  `main_rs.tmpl` (→ `crates/tcps-cli/src/main.rs`), `kijun_rs.tmpl` (→
  `crates/tcps-cli/src/基準.rs`), `dispatch_sabotage_proof.rs.tmpl` (→
  `crates/tcps-cli/tests/tcps_cli_dispatch_sabotage_proof.rs`).
- Gate: `cli_010_depends_on_declared.rq` — every `tcps:dependsOnModule` target
  must be a declared, named `tcps:Module`.
