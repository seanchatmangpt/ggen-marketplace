# Test Suite Audit Report: ggen-marketplace (v26.11.15)

- **Audited Target**: `/Users/sac/ggen-marketplace`
- **Audit Agent**: Agent 12 of 20 (`ggen_auditor_tests`)
- **Evaluation Date**: 2026-11-16
- **Audit Standard**: Chicago-style real execution, fail-closed admission, anti-vacuity, epistemic envelope conformance
- **Scope**: Rust crates (`tools/`, `packs/`), Python pytest suites (`tests/`), Pack Verifiers (`packs/**/verify.py`), In-repo test harnesses & audit tools (`scripts/`)

---

## Executive Summary

A comprehensive, live audit of the test suites, verification harnesses, and Rust crates within `/Users/sac/ggen-marketplace` was executed. The repository enforces strict Chicago-style principles (zero synthetic mocks or stubs in active courts, requirement of real subprocesses and disk artifacts). However, the audit revealed **critical architectural and test suite blockers** that currently prevent clean CI execution and marketplace qualification.

### Key Audit Metrics
| Category | Evaluated | Passing / Conforming | Failing / Blocked | Standing |
|---|---|---|---|---|
| **Rust Crates (`Cargo.toml`)** | 10 crates in repo | 5 passing (108 tests) | 2 compile/dep failures, 2 zero-test crates, 1 root missing | **BUILD_BROKEN** |
| **Python Pytest Suite** | 137 files (2,282 tests) | 305 passing (batch 1), 86 (batch 2), 17 (batch 3) | 31 failures, 10 errors, 4 complete test suites skipped | **PARTIAL_ALIVE** |
| **Pack Verifiers (`verify.py`)** | 52 active verifiers | 49 passed | 3 failed (drift / hash refusal) | **PARTIAL_ALIVE** |
| **Config Admission (`star-toml`)** | `marketplace.toml` | 0 | 1 rejected (`[registry]` unknown field) | **REFUSED** |
| **Marketplace Validation (`marketplace.py`)** | Complete corpus | 0 | 1 rejected (`.toml` in `gates/`) | **REFUSED** |
| **Vacuity Audit (`audit_vacuity.py`)** | 27,745 files | N/A | 4,607 findings (1,004 errors, 3,603 warnings) | **REFUSED** |

---

## 1. Critical Repo-Level & Build Failure Findings

### Finding 1.1: Root-Level `cargo test` Execution Failure
- **Subject**: `/Users/sac/ggen-marketplace` (Repository Root)
- **Classification**: Missing Workspace Root Configuration
- **Gap / Issue**: Executing `cargo test` directly at the repository root fails immediately because no root `Cargo.toml` or Cargo workspace exists. Rust crates are scattered across `tools/` and `packs/` without a workspace manifest uniting them.
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace && cargo test
  ```
- **Command Output**:
  ```text
  error: could not find `Cargo.toml` in `/Users/sac/ggen-marketplace` or any parent directory
  [exit 101]
  ```

---

### Finding 1.2: `tcps-core` Test Suite Fails to Compile with 7 Type Errors
- **Subject**: `packs/tcps-pack/reference/製品版/crates/tcps-core/src/試験.rs`
- **Classification**: Compiler Error in Test Module
- **Gap / Issue**: The test module `試験.rs` in `tcps-core` references non-existent constructors (`新規`, `空`) and uses module identifiers where struct types are expected (`受領証`, `工程能力`). The test binary fails compilation, leaving the crate completely unverified.
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace/packs/tcps-pack/reference/製品版 && cargo test
  ```
- **Command Output**:
  ```text
     Compiling tcps-core v26.7.19 (/Users/sac/ggen-marketplace/packs/tcps-pack/reference/製品版/crates/tcps-core)
  error[E0425]: cannot find function `新規` in module `標準作業`
    --> crates/tcps-core/src/試験.rs:99:30
     |
  99 |     let mut 旧標準 = 標準作業::<4>::新規(100, 有無::無い, 1, 60, 1);
     |                                     ^^^^ not found in `標準作業`

  error[E0425]: cannot find function `新規` in module `標準作業`
     --> crates/tcps-core/src/試験.rs:100:26
      |
  100 |     let 新標準 = 標準作業::<4>::新規(101, 有無::有る(100), 1, 55, 1);
      |                                 ^^^^ not found in `標準作業`

  error[E0425]: cannot find function `新規` in module `五回なぜ`
     --> crates/tcps-core/src/試験.rs:128:24
      |
  128 |     let mut 分析 = 五回なぜ::新規();
      |                              ^^^^ not found in `五回なぜ`

  error[E0573]: expected type, found module `受領証`
     --> crates/tcps-core/src/試験.rs:324:24
      |
  324 |     ) -> 成否<(Self::成果, 受領証), Self::失敗> {
      |                            ^^^^^^ not a type

  error[E0574]: expected struct, variant or union type, found module `受領証`
     --> crates/tcps-core/src/試験.rs:330:13
      |
  330 |             受領証 {
      |             ^^^^^^ not a struct, variant or union type

  error[E0425]: cannot find function `空` in module `価値流`
     --> crates/tcps-core/src/試験.rs:388:28
      |
  388 |     let mut 流れ = 価値流::<4>::空();
      |                                 ^^ not found in `価値流`

  error[E0574]: expected struct, variant or union type, found module `工程能力`
     --> crates/tcps-core/src/試験.rs:395:14
      |
  395 |     let 能力 = 工程能力 { 最大数量: 8, 最小周期: 50, 最大候補数: 4 };
      |                ^^^^^^^^ not a struct, variant or union type

  error: could not compile `tcps-core` (lib test) due to 7 previous errors
  [exit 101]
  ```

---

### Finding 1.3: `chatman-receipt-harness` Fails Missing Dependency
- **Subject**: `packs/chatman-ecosystem-release-pack/qualification/chatman-harness/Cargo.toml`
- **Classification**: Broken Relative Path Dependency
- **Gap / Issue**: `chatman-receipt-harness` declares a local path dependency `ecosystem-core = { path = "../crates/ecosystem-core" }`. That directory is absent in the repository checkout, causing cargo to fail during source resolution.
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace/packs/chatman-ecosystem-release-pack/qualification/chatman-harness && cargo test
  ```
- **Command Output**:
  ```text
  error: failed to get `ecosystem-core` as a dependency of package `chatman-receipt-harness v0.0.0 (/Users/sac/ggen-marketplace/packs/chatman-ecosystem-release-pack/qualification/chatman-harness)`

  Caused by:
    failed to load source for dependency `ecosystem-core`

  Caused by:
    unable to update /Users/sac/ggen-marketplace/packs/chatman-ecosystem-release-pack/qualification/crates/ecosystem-core

  Caused by:
    failed to read `/Users/sac/ggen-marketplace/packs/chatman-ecosystem-release-pack/qualification/crates/ecosystem-core/Cargo.toml`

  Caused by:
    No such file or directory (os error 2)
  [exit 101]
  ```

---

### Finding 1.4: Vacuous Zero-Test Rust Crates
- **Subject**:
  1. `tools/marketplace-config` (`tools/marketplace-config/src/main.rs`)
  2. `packs/xstate-v5-machine-pack/tools/render_test` (`packs/xstate-v5-machine-pack/tools/render_test/src/main.rs`)
- **Classification**: Vacuous Passes / Zero Tests
- **Gap / Issue**: Both crates compile cleanly and exit `cargo test` with status code 0, but execute **0 tests**. They provide false positive pass signals in build loops.
- **Exact Commands & Outputs**:
  ```bash
  cd /Users/sac/ggen-marketplace/tools/marketplace-config && cargo test
  # Output:
  # running 0 tests
  # test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

  cd /Users/sac/ggen-marketplace/packs/xstate-v5-machine-pack/tools/render_test && cargo test
  # Output:
  # running 0 tests
  # test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
  ```

---

## 2. Marketplace Gate & Validation Failures

### Finding 2.1: `marketplace.py validate` Refuses Valid Pack Corpus due to Unadmitted Gate Extension
- **Subject**:
  - `packs/xstate-v5-machine-pack/gates/baselines.toml`
  - `packs/xstate-v5-machine-pack/gates/shapes.toml`
  - `scripts/marketplace.py:42` (`GATE_SOURCE_SUFFIXES`)
- **Classification**: Architectural Rule Violation / Pipeline Blocker
- **Gap / Issue**: `scripts/marketplace.py` enforces `GATE_SOURCE_SUFFIXES = frozenset({".rq", ".py", ".sh"})`. Placing `.toml` files in `packs/xstate-v5-machine-pack/gates/` triggers a fail-closed refusal `REFUSED:GATE_SOURCE_EXTENSION`. Because `marketplace.require_admitted()` evaluates the entire repository, this single issue breaks:
  1. `scripts/marketplace.py validate`
  2. `scripts/qualify_packs.py` (all shards)
  3. `ggen_marketplace.cli` (`ggmkt search`, `ggmkt info`, `ggmkt list`)
  4. Integration courts importing `marketplace.require_admitted()`
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace && /usr/local/bin/python3.11 scripts/marketplace.py validate
  ```
- **Command Output**:
  ```text
  REFUSED:GATE_SOURCE_EXTENSION:packs/xstate-v5-machine-pack/gates/baselines.toml
  REFUSED:GATE_SOURCE_EXTENSION:packs/xstate-v5-machine-pack/gates/shapes.toml
  [exit 2]
  ```

---

### Finding 2.2: CLI Test Suite `test_typer_cli.py` 75% Failure Rate
- **Subject**: `tests/test_typer_cli.py`
- **Classification**: Functional CLI Test Failure
- **Gap / Issue**: 3 out of 4 tests (`test_cli_search_a2a`, `test_cli_info`, `test_cli_list`) fail with exit code 2 because the CLI invokes `marketplace.require_admitted()`, which crashes on the `.toml` files in `xstate-v5-machine-pack/gates/`.
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace && /opt/homebrew/bin/pytest tests/test_typer_cli.py
  ```
- **Command Output**:
  ```text
  FAILED tests/test_typer_cli.py::test_cli_search_a2a - assert 2 == 0
  FAILED tests/test_typer_cli.py::test_cli_info - assert 2 == 0
  FAILED tests/test_typer_cli.py::test_cli_list - assert 2 == 0
  3 failed, 1 passed in 4.50s
  ```

---

### Finding 2.3: Config Admission Refuses `marketplace.toml` (`[registry]` schema mismatch)
- **Subject**: `marketplace.toml` line 67 vs `tools/marketplace-config/src/main.rs:16`
- **Classification**: Configuration Schema Drift / Fail-Closed Admission Blocker
- **Gap / Issue**: `marketplace.toml` introduced `[registry.fnox_io]`. However, `tools/marketplace-config/src/main.rs` does not declare a `registry` field in `MarketplaceConfig`. Because `star-toml` strictly refuses unknown fields, running `scripts/admit-config.sh` refuses admission.
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace && bash scripts/admit-config.sh marketplace.toml /tmp/admitted.json
  ```
- **Command Output**:
  ```text
  REFUSED:MARKETPLACE_CONFIG_NOT_ADMITTED:1 validation error
  registry
    unknown field: `registry` (got: `registry`) [unknown_field]
  [exit 2]
  ```

---

## 3. Test Suite Divergence with Upstream `ggen` CLI v26.11.5

### Finding 3.1: EA Admission Gate `[FM-LAW-015]` Breakage Across Sync Courts
- **Subject**:
  - `tests/test_aaif_deployment_court.py`
  - `tests/test_aaif_vanilla_pack_court.py`
  - `tests/test_aaif_wrap_autofde_lab.py`
  - `tests/test_cas_chain_composition.py`
  - `tests/test_conference_provisioning_court.py`
- **Classification**: Toolchain / Protocol Version Divergence
- **Gap / Issue**: The ambient `ggen` CLI version is `26.11.5`. Upstream introduced `[FM-LAW-015] EA admission gate`: every `ggen sync run` must either supply `ea.graph.json` or pass `--skip-ea-admission`. While `scripts/qualify_packs.py` was updated to pass `--skip-ea-admission`, the Python test courts were not updated. Consequently, all tests invoking `ggen sync run` fail.
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace && /opt/homebrew/bin/pytest -v tests/test_aaif_deployment_court.py -k "TestHappyPathKindRail or TestIdempotentRedeploy"
  ```
- **Command Output**:
  ```text
  FAILED tests/test_aaif_deployment_court.py::TestHappyPathKindRail::test_happy_path_kind_rail
  E AssertionError: REFUSED:GGEN_SYNC_FAILED:exit 1:
  E ERROR: CLI execution failed: Command execution failed: validation error: [FM-LAW-015] EA admission gate: `/Users/sac/.cache/tmp/.../solution-acme/ea.graph.json` is absent and no admission opt-out was given. Every sync must either admit its candidate SBBs against an EA graph or explicitly skip with `--skip-ea-admission`. Remediation: add ea.graph.json, or pass --skip-ea-admission to run without architecture admission.
  ```

---

## 4. Missing Dependencies & Skipped Test Suites

### Finding 4.1: Missing `packages/pm4pytest` Dependency and Skipped Courts
- **Subject**:
  - `pyproject.toml:50` (`pm4pytest = { path = "packages/pm4pytest", editable = true }`)
  - `tests/test_aaif_enterprise_court.py`
  - `tests/test_rust_wasi_wasmex_court.py`
  - `tests/test_ggmkt_pm4pytest_court.py`
  - `tests/test_ggmkt_pm4pytest_precision_court.py`
- **Classification**: Missing Repository Package / Skipped Enterprise Test Courts
- **Gap / Issue**: `packages/pm4pytest` does not exist in `packages/`.
  - `uv run` refuses to generate package metadata (`Caused by: Distribution not found at: file:///Users/sac/ggen-marketplace/packages/pm4pytest`).
  - Four entire test suites use `pytest.importorskip("pm4pytest")` and are completely skipped.
  - In `test_ggmkt_pm4pytest_court.py:137`, the test additionally hardcodes an absolute subprocess call to `.venv/bin/pm4pytest`, which is also missing.
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace && /opt/homebrew/bin/pytest tests/test_aaif_enterprise_court.py
  ```
- **Command Output**:
  ```text
  collected 0 items / 1 skipped
  ============================== 1 skipped in 0.04s ==============================
  [exit 5]
  ```

---

## 5. Pack Verifiers (`verify.py`) Audit

52 active `verify.py` scripts across `packs/` were executed live under Python 3.11 with genuine `rdflib` and SHACL execution.
- **Passed**: 49 verifiers passed with 0 rows on constraint violation queries.
- **Refused / Failed**: 3 verifiers failed due to hash drift between live code and pinned receipts:

### Finding 5.1: `strata-protocol-pack` Valve Hash Mismatch
- **Subject**: `packs/strata-protocol-pack/verify.py`
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace/packs/strata-protocol-pack && /usr/local/bin/python3.11 verify.py
  ```
- **Command Output**:
  ```text
  PASS 010_header_layout.rq: 0 rows
  PASS 020_refusal_receipt_len.rq: 0 rows
  PASS 030_refusal_taxonomy_closure.rq: 0 rows
  REFUSED: live valve refusals.ex hash 685b554f681b1f1bfb9f4f346ed77d45673b23fede0f87c2117e6fb75e7c0249 != pin de7bd39b05b4cc78a6356cc84286301fc1b424c7bb592582ebbc3ca792740335
  [exit 1]
  ```

### Finding 5.2: `strata-signer-pack` Witness Drift
- **Subject**: `packs/strata-signer-pack/verify.py`
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace/packs/strata-signer-pack && /usr/local/bin/python3.11 verify.py
  ```
- **Command Output**:
  ```text
  REFUSED: witness hash drift (witness=1134b20cd0d6283376722ecc1c98da1c3b79223d42725fb4995131fce42706c7 receipt=aa4296b88c5639a716d6c7c9abb72940adaf4eb12cbad1d94166351567cb6b37)
  [exit 1]
  ```

### Finding 5.3: `strata-temprun-pack` Witness Drift
- **Subject**: `packs/strata-temprun-pack/verify.py`
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace/packs/strata-temprun-pack && /usr/local/bin/python3.11 verify.py
  ```
- **Command Output**:
  ```text
  REFUSED: witness hash drift (witness=e025425b032a0fffbd40568478028dd3067cbcab2aea75dec5964e41f8330e09 receipt=3314b2122c1ae988c9e64588a3f94051e2b2a6c94c4a688a5c25a007a2f46b0f)
  [exit 1]
  ```

---

## 6. Assertion Strength & Vacuity Audit

### Finding 6.1: Vacuous "No-Raise" Tests with Zero Verifications
- **Subject**: `tests/test_aaif_deployment_court.py`
  - `test_plain_config_without_kind_passes` (line 789)
  - `test_happy_path_namespace_passes` (line 798)
  - `test_pack_runtime_state_artifacts_excluded_check_passes` (line 936)
- **Classification**: Vacuous Assertion / Missing State Verification
- **Gap / Issue**: These test functions call deployment validator functions (`deploy.check_namespace_scope`, `deploy.check_lock_digests`) with only a `# no raise` comment. They do not assert return values, inspect side effects, or check mutation resistance. If the called function is a no-op or returns early, the test passes vacously.

### Finding 6.2: Disabled Pass/Fail Witness Checks in `workflow-corpus-pack`
- **Subject**: `packs/workflow-corpus-pack/gate-court.toml:23`
- **Classification**: Weakened Gate Verification Contract
- **Gap / Issue**: The court contract explicitly disables witness verification:
  ```toml
  require_pass = false
  require_fail = false
  ```
  The comments state this was an intentional bypass due to concurrent multi-lane editing, but it structurally weakens the gate-witness court to a no-op at the structural qualification layer.

### Finding 6.3: Static Repository Vacuity Report
- **Subject**: `scripts/audit_vacuity.py`
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace && /usr/local/bin/python3.12 scripts/audit_vacuity.py
  ```
- **Command Output Metrics**:
  - **Standing**: `REFUSED`
  - **Total Findings**: 4,607
  - **Error Severity**: 1,004
  - **Warning Severity**: 3,603
  - **Rust Unimplemented Macros**: 32 occurrences
  - **Rust Todo Macros**: 11 occurrences
  - **Python Swallowed Exceptions**: 2 occurrences (`pass` in broad `except Exception`)
  - **Python Empty Functions**: 8 occurrences

---

## 7. Documentation vs Reality Drift

### Finding 7.1: Pack Census Canary Drift
- **Subject**: `tests/test_capabilities_and_census.py::test_generated_docs_match_scripts`
- **Classification**: Documentation Drift / Test Failure
- **Gap / Issue**: `docs/reference/pack-capabilities.md` records 364 packs, while `pack_capabilities.py --markdown` outputs 327 packs. The canary test fails because generated documentation was not updated in sync with repository pack additions/retirements.
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace && /opt/homebrew/bin/pytest tests/test_capabilities_and_census.py -k test_generated_docs_match_scripts
  ```
- **Command Output**:
  ```text
  FAILED tests/test_capabilities_and_census.py::test_generated_docs_match_scripts
  E AssertionError: assert '# Pack capab...low-map.md)\n' == '# Pack capab...low-map.md)\n'
  E   - | packs | 364 |
  E   + | packs | 327 |
  ```

---

## 8. Passing Crates & Strong Verification Witness Reference

The audit confirmed that several Rust crates exhibit exemplary verification rigor:
1. **`packs/strata-signer-pack/courts`**:
   - 25 passed tests in 0.13s.
   - Rigorously validates ML-DSA-65 post-quantum signing, domain separation tag verification, and intentional `SabotageTwin` refusal (anti-vacuity).
2. **`packs/rust-doc-hdit-pack`**:
   - 44 passed tests across unit, integration, and certification harnesses.
   - Verifies vector symbolic architectures (VSA), bundle tie-freedom, information entropy bounds, and tamper-evident receipt chaining.
3. **`packs/strata-ledger-pack/courts-compile`**:
   - 11 unit tests and 1 `trybuild` compile-fail test passed.
   - Proves state transitions, conservation law invariants under random property generation, and compile-time prevention of private field bypass.
4. **`packs/mfact-pack/reference/mfact-core`**:
   - 19 passed tests covering manifest validation, blake3 genesis folds, and receipt engine determinism.

---

## Actionable Remediation Plan

1. **Gate Suffix Repair**:
   - Move or rename `baselines.toml` and `shapes.toml` out of `packs/xstate-v5-machine-pack/gates/` (or update `GATE_SOURCE_SUFFIXES` in `scripts/marketplace.py` if `.toml` gate declarations are lawful).
2. **`marketplace.toml` Schema Alignment**:
   - Update `tools/marketplace-config/src/main.rs` to include `registry: Option<RegistryConfig>` in `MarketplaceConfig` so `scripts/admit-config.sh` admits cleanly.
3. **Rust Compilation Fix**:
   - Repair the 7 compile errors in `packs/tcps-pack/reference/製品版/crates/tcps-core/src/試験.rs` by correctly importing and typing `受領証` and `工程能力`.
4. **Toolchain Sync `--skip-ea-admission`**:
   - Update `_deploy` and subprocess invocations in `test_aaif_deployment_court.py`, `test_aaif_vanilla_pack_court.py`, `test_aaif_wrap_autofde_lab.py`, and `test_cas_chain_composition.py` to pass `--skip-ea-admission` when invoking `ggen sync run`.
5. **Restore `packages/pm4pytest`**:
   - Vendor or symlink `pm4pytest` into `packages/pm4pytest` so that `uv run` and enterprise test courts (`test_aaif_enterprise_court.py`) can execute rather than skip.
6. **Re-seal Pack Verifier Hashes**:
   - Update receipt hashes in `packs/strata-protocol-pack/`, `packs/strata-signer-pack/`, and `packs/strata-temprun-pack/` to match live admitted sources.
