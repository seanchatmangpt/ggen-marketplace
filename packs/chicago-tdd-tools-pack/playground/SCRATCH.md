# Playground: add your own `ctt:CliBoundaryTest`

Edit this scratch file's companion, or copy its shape into a real consumer's
`domain.ttl`, then re-run `ggen sync run` to see a new generated `#[test]`
appear in `tests/chicago_tdd_tools_boundary.rs`.

## Try it

Add a new individual like this (grounded in a real binary you actually
build, e.g. a `[[bin]]` target in your own consumer crate):

```turtle
@prefix ctt: <http://seanchatmangpt.github.io/packs/chicago-tdd-tools#> .

ctt:my-tool-version
  a ctt:CliBoundaryTest ;
  ctt:testName "my_tool_version_emits_name" ;
  ctt:binary "my-tool" ;
  ctt:args "--version" ;
  ctt:expectExitCode 0 ;
  ctt:stdoutNeedle "my-tool" ;
  ctt:coversAxiom "my-tool --version exits 0 and prints its own name" .
```

Then:

```bash
ggen sync run
```

The new `#[test] fn my_tool_version_emits_name()` appears in
`tests/chicago_tdd_tools_boundary.rs`, dispatching through the generated
`run_boundary_spec` in `tests/chicago_tdd_tools_boundary_runtime.rs` —
which spawns your real `my-tool` binary via
`chicago_tdd_tools::cli_proof::CliHarness::cargo_bin("my-tool")`. No mocks:
if `my-tool` isn't on `PATH` or a `CARGO_BIN_EXE_*` target, the test fails
for real, the same way `CliHarness::cargo_bin`'s resolution order
(`/Users/sac/chicago-tdd-tools/src/cli_proof/harness.rs`) is documented to
behave.

## A different real chicago-tdd-tools primitive, for contrast

This pack's own generated code always wraps `CliHarness` through
`run_boundary_spec`. If instead your test needs to admit and validate a
*config file* rather than cross a CLI-binary boundary, the sibling real
primitive in the same repo is `config_test!`
(`/Users/sac/chicago-tdd-tools/src/core/macros/config_test.rs`), used like:

```rust
config_test!(test_default_config_admitted, AppConfig, r#"
    name = "app"
    workers = 4
"#, |config| { assert_eq!(config.workers, 4); });
```

That macro is what `star-toml-pack`'s generated module wires against
(`examples/star-toml/samples/*.toml` in the real chicago-tdd-tools repo).
This pack's `ctt:CliBoundaryTest` shape is deliberately narrower — process
boundary, not config admission — so a config-shaped test case does not
belong in this ontology; it belongs in `star-toml-pack`'s own
`stp:ConfigSection`/`stp:ConfigField` shape instead (see this marketplace's
real cross-pack composition proof in `MATURITY.md`, axis 7).
