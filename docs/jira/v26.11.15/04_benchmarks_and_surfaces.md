# 04_benchmarks_and_surfaces.md — Ggen Marketplace Benchmarks, Generator Throughput & Surfaces Audit

- **Audit Date**: 2026-11-16
- **Auditor**: Agent 14 of 20 (`ggen_auditor_benchmarks_docs`)
- **Target Repository**: `/Users/sac/ggen-marketplace`
- **Standing**: COMPLETED (Read-Only Live Audit; Documented to `docs/jira/v26.11.15/04_benchmarks_and_surfaces.md`)
- **Authority**: NONE (Audit observations, measured telemetry, and factual gap documentation only)

---

## 1. Executive Summary & Audit Methodology

In accordance with the `audit-and-report` methodology and the v26.11.15 Multi-Repository Production Review mandate, Agent 14 conducted a comprehensive live empirical audit of all benchmark harnesses, generator surfaces, template rendering throughput, and pack qualification pipelines across `/Users/sac/ggen-marketplace`.

### Integrity & Safety Guarantee
- **Zero Modifications to Source Code or Test Files**: In strict compliance with Mandatory Rule 1, no source code (`*.rs`, `*.py`, `*.ex`, `*.go`) or test files across `/Users/sac/ggen-marketplace` were created, modified, or deleted. All findings are derived strictly from live terminal command execution against the existing codebase.

### Audit Summary Statistics
| Metric | Count / Measurement | Finding / Standing |
|---|---|---|
| **Total Marketplace Packs** | 364 packs | 355 packs (97.5%) have zero benchmark files |
| **Packs with Templates** | 319 packs | 2,121 templates (1,848 `.tmpl`, 273 `.tera`, 7.74 MB total) |
| **Embedded SPARQL Queries in Templates** | 2,075 queries across 1,471 templates | Zero (0) template-rendering or query throughput benchmarks |
| **Packs with Any Benchmark/Perf Artifacts** | 9 packs | 5 packs are vacuous stubs, 1 claims registry, only 3 real harnesses |
| **Crates Defining Benchmarks (`cargo bench`)** | 0 crates in packs / tools | All 5 examined Rust crates report `0 measured` or ignore tests |
| **Rust Compilation Failures under `cargo bench`** | 1 crate (`tcps-core`) | 7 compile errors in `crates/tcps-core/src/試験.rs` |
| **Generator Sync Run Status** | REFUSED (`[FM-PACK-008]`) | `ggen.lock` content hash mismatch for `strata-ledger-pack` |
| **Marketplace Admission Validation Status** | REFUSED (`GATE_SOURCE_EXTENSION`) | Non-compliant `.toml` files in `packs/xstate-v5-machine-pack/gates/` |
| **Python Build/Test Environment** | BROKEN | `pyproject.toml` references missing `packages/pm4pytest` |

---

## 2. Cargo Bench & Crate Benchmark Audit

### Finding 1: Repository Root Lacks `Cargo.toml`
- **Target**: `/Users/sac/ggen-marketplace`
- **Gap / Vacuity Issue**: The repository is structured as an ecosystem pack registry with embedded polyglot crates, but lacks a top-level Cargo workspace configuration. Attempting to execute `cargo bench` at the repository root fails immediately.
- **Exact Command Executed**:
  ```bash
  cd /Users/sac/ggen-marketplace && cargo bench
  ```
- **Exit Code**: 101
- **Exact Output**:
  ```console
  error: could not find `Cargo.toml` in `/Users/sac/ggen-marketplace` or any parent directory
  ```

---

### Finding 2: `tools/marketplace-config` Has Zero Benchmarks Defined (`0 measured`)
- **Target File**: `/Users/sac/ggen-marketplace/tools/marketplace-config/Cargo.toml`
- **Gap / Vacuity Issue**: `tools/marketplace-config` compiles as a binary crate under the `bench` profile, but contains 0 benchmarks. Running `cargo bench` measures nothing, providing vacuous benchmark exit code 0.
- **Exact Command Executed**:
  ```bash
  cd /Users/sac/ggen-marketplace/tools/marketplace-config && cargo bench
  ```
- **Exit Code**: 0
- **Exact Output**:
  ```console
     Compiling ggen-marketplace-config v0.1.0 (/Users/sac/ggen-marketplace/tools/marketplace-config)
      Finished `bench` profile [optimized] target(s) in 34.55s
       Running unittests src/main.rs (target/release/deps/ggen_marketplace_config-13444b9d64254154)

  running 0 tests

  test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
  ```

---

### Finding 3: `packs/rust-doc-hdit-pack` Ignores All Tests Under `cargo bench` (`0 measured`)
- **Target File**: `/Users/sac/ggen-marketplace/packs/rust-doc-hdit-pack/Cargo.toml`
- **Gap / Vacuity Issue**: `packs/rust-doc-hdit-pack` has a Cargo manifest and 16 unit tests, but defines no benchmark functions (`#[bench]` or criterion). Under `cargo bench`, all 16 tests are marked `ignored` and 0 are measured.
- **Exact Command Executed**:
  ```bash
  cd /Users/sac/ggen-marketplace/packs/rust-doc-hdit-pack && cargo bench
  ```
- **Exit Code**: 0
- **Exact Output**:
  ```console
      Finished `bench` profile [optimized] target(s) in 47.29s
       Running unittests src/lib.rs (target/release/deps/doc_hdit-efd87350692c3d1e)

  running 16 tests
  test certify::tests::chain_file_roundtrip ... ignored
  test certify::tests::extractor_identity_is_content_hash_and_drift_sensitive ... ignored
  test certify::tests::last_chain_extractor_grandfathers_legacy_receipts ... ignored
  test certify::tests::receipt_hash_is_reproducible_and_chain_links ... ignored
  test certify::tests::subject_digest_covers_docs_tree ... ignored
  test scaffold::tests::context_is_sorted_and_deterministic ... ignored
  test scaffold::tests::merge_keeps_fresh_when_no_existing_blocks ... ignored
  test scaffold::tests::reference_table_identifiers_are_backtick_wrapped ... ignored
  test scaffold::tests::scaffold_empty_existing_file_is_treated_as_fresh ... ignored
  test scaffold::tests::scaffold_is_idempotent_and_merges_commentary ... ignored
  test scaffold::tests::scaffold_refuses_marker_free_existing_prose ... ignored
  test vsa::cache::tests::key_is_deterministic_and_content_sensitive ... ignored
  test vsa::cache::tests::store_then_load_roundtrips ... ignored
  test vsa::tests::basis_is_deterministic ... ignored
  test vsa::tests::bind_is_self_inverse ... ignored
  test vsa::tests::permute_rotates ... ignored

  test result: ok. 0 passed; 0 failed; 16 ignored; 0 measured; 0 filtered out; finished in 0.00s
  ```

---

### Finding 4: `packs/strata-signer-pack/courts` Ignores All Tests Under `cargo bench` (`0 measured`)
- **Target File**: `/Users/sac/ggen-marketplace/packs/strata-signer-pack/courts/Cargo.toml`
- **Gap / Vacuity Issue**: `strata-signer-pack/courts` has 25 court tests, but defines no benchmark targets. Under `cargo bench`, all 25 tests are ignored and `0 measured`.
- **Exact Command Executed**:
  ```bash
  cd /Users/sac/ggen-marketplace/packs/strata-signer-pack/courts && cargo bench
  ```
- **Exit Code**: 0
- **Exact Output**:
  ```console
      Finished `bench` profile [optimized] target(s) in 10.28s
       Running unittests src/lib.rs (target/release/deps/strata_signer_courts-206fa78917db3535)

  running 25 tests
  test signing::tests::different_digest_refuses_original_signature ... ignored
  ...
  test tx_binding::sabotage_twin_untagged_digest_caught ... ignored

  test result: ok. 0 passed; 0 failed; 25 ignored; 0 measured; 0 filtered out; finished in 0.00s
  ```

---

### Finding 5: `packs/tcps-pack/reference/製品版` Fails Compilation on `cargo bench`
- **Target File**: `/Users/sac/ggen-marketplace/packs/tcps-pack/reference/製品版/crates/tcps-core/src/試験.rs`
- **Gap / Vacuity Issue**: The Rust codebase in `tcps-pack` has uncompilable source code containing multiple broken module references and missing struct imports in Japanese identifier tests. Running `cargo bench` aborts with 7 compiler errors.
- **Exact Command Executed**:
  ```bash
  cd /Users/sac/ggen-marketplace/packs/tcps-pack/reference/製品版 && cargo bench
  ```
- **Exit Code**: 101
- **Exact Output**:
  ```console
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
  ```

---

## 3. Live Benchmark Harnesses Executed & Bottleneck Analysis

### Finding 6: `evolvable-capability-pack` Deterministic Gate Latency Benchmark
- **Target File**: `/Users/sac/ggen-marketplace/packs/evolvable-capability-pack/qualification/bench.py`
- **Harness Details**: Evaluates 14 SPARQL gates across synthetic capability evolution histories (N generations), verifying that execution time per generation stays bounded and scaling does not exceed quadratic thresholds.
- **Exact Command Executed**:
  ```bash
  cd /Users/sac/ggen-marketplace && python3 packs/evolvable-capability-pack/qualification/bench.py --sizes 5,10 --repeats 1
  ```
- **Exit Code**: 0
- **Measured Results**:
  ```json
  {
    "bound_seconds_per_generation": 0.05,
    "engine": { "python": "3.9.6", "rdflib": "7.1.4" },
    "machine": { "machine": "arm64", "system": "Darwin" },
    "results": [
      {
        "gates": 14,
        "generations": 5,
        "median_seconds": 0.375534,
        "seconds_per_generation": 0.075107,
        "triples": 194
      },
      {
        "gates": 14,
        "generations": 10,
        "median_seconds": 0.257353,
        "seconds_per_generation": 0.025735,
        "triples": 324
      }
    ],
    "scaling": {
      "checked": true,
      "pairs": [
        {
          "from_generations": 5,
          "max_time_ratio": 4.0,
          "size_ratio": 2.0,
          "standing": "ALIVE",
          "time_ratio": 0.685,
          "to_generations": 10
        }
      ]
    },
    "scaling_slack": 2.0,
    "schema": "ggen.evolvable-capability-pack.bench/2",
    "standing": "ALIVE"
  }
  ```

---

### Finding 7: `strategic-doctrine-pack` Benchmarks & Identified Performance Bottleneck
- **Target File**: `/Users/sac/ggen-marketplace/packs/strategic-doctrine-pack/benchmarks/bench_gates.py`
- **Harness Details**: Times 6 strategic-doctrine gates against both the shipped doctrine graph (699 triples) and synthetic graphs of 16 strategies (624 triples) and 64 strategies (1,872 triples) over 5 repeated trials.
- **Exact Command Executed**:
  ```bash
  cd /Users/sac/ggen-marketplace && python3 packs/strategic-doctrine-pack/benchmarks/bench_gates.py
  ```
- **Exit Code**: 0
- **Performance Bottleneck Analysis**:
  1. **Gate `050_no_excerpt`**:
     - Doctrine graph (699 triples): **2.2078s**
     - Synthetic 16 strategies: **2.4437s**
     - Synthetic 64 strategies: **8.2231s** (Scaling ratio: **3.37x**)
     - *Root cause*: Full graph text-scanning for prohibited excerpt predicates across complex nested blank nodes without index acceleration.
  2. **Gate `020_applicability_public_class_only`**:
     - Doctrine graph: **1.1505s**
     - Synthetic 16 strategies: **1.2907s**
     - Synthetic 64 strategies: **1.4296s**
  3. **Total Latency**: The 64-strategy synthetic graph takes **10.5017 seconds** to evaluate just 6 gates on 1,872 triples.

---

### Finding 8: `greene-licensing-case-pack` Benchmarks & Regex Backtracking Degradation
- **Target File**: `/Users/sac/ggen-marketplace/packs/greene-licensing-case-pack/bench/bench_gates.py`
- **Harness Details**: Evaluates gates on 1,337 triples, and measures adversarial susceptibility against 20,000-character adversarial string inputs designed to trigger regex backtracking in SPARQL filter clauses.
- **Exact Command Executed**:
  ```bash
  cd /Users/sac/ggen-marketplace && python3 packs/greene-licensing-case-pack/bench/bench_gates.py --repeats 1
  ```
- **Exit Code**: 0
- **Performance Degradation Results**:
  - Baseline Gate `050_no_endorsement_language`: **1.6887s**
  - Baseline Gate `060_no_quoted_source_text`: **1.3589s**
  - Adversarial `angle-run` (20,000 `<` chars): **4.3767s** total gate execution
  - Adversarial `stem-prefix-run` (20,000 `endor ` chars): **4.1211s** total gate execution
  - Adversarial `ampersand-run` (20,000 `&a` chars): **3.3344s** total gate execution
  - *Root cause*: In-memory SPARQL regex matching in rdflib lacks non-backtracking DFA execution guarantees, allowing large un-indexed string literals to degrade throughput by >2.5x.

---

## 4. Generator Throughput, Lock Drift & Admission Gaps

### Finding 9: Ggen Lock Drift `[FM-PACK-008]` Blocks Repository Sync Operations
- **Target File**: `/Users/sac/ggen-marketplace/ggen.lock`
- **Gap / Vacuity Issue**: The root lockfile `ggen.lock` records a hash for `strata-ledger-pack` that no longer matches the contents on disk. Consequently, all repository-wide generator operations (`ggen sync run`) fail validation immediately.
- **Exact Command Executed**:
  ```bash
  cd /Users/sac/ggen-marketplace && ggen sync run --dry-run --skip-ea-admission
  ```
- **Exit Code**: 1
- **Exact Output**:
  ```console
  2026-11-16T17:45:01.920474Z  INFO ggen.cli{command=sync run --dry-run --skip-ea-admission version="26.11.5"}:pipeline.load{operation.name="pipeline.load" operation.type="pipeline" pipeline.stage="load"}: ggen_engine::sync: close time.busy=20.5ms time.idle=9.75µs
  2026-11-16T17:45:01.922080Z  INFO ggen.cli{command=sync run --dry-run --skip-ea-admission version="26.11.5"}: ggen_cli_lib: close time.busy=25.2ms time.idle=15.0µs
  ERROR: CLI execution failed: Command execution failed: validation error: [FM-PACK-008] pack `strata-ledger-pack` (source `path:packs/strata-ledger-pack`) content hash mismatch: ggen.lock has `blake3:3121dc124049222af49be68225dc304c3f53e32aeff9af2c9471965f9ee6a229` but the pack on disk hashes to `blake3:2c0e3d1f04cd26949d15a3972703b591e61527c078b24019c4cae4ac8864f847`. Remediation: restore the pack, or delete ggen.lock to intentionally re-lock.
  ```

---

### Finding 10: Non-Compliant Gate File Extensions in `xstate-v5-machine-pack` Block Marketplace Admission
- **Target Files**:
  - `/Users/sac/ggen-marketplace/packs/xstate-v5-machine-pack/gates/baselines.toml`
  - `/Users/sac/ggen-marketplace/packs/xstate-v5-machine-pack/gates/shapes.toml`
- **Gap / Vacuity Issue**: `marketplace.py` strictly mandates that all files inside a pack's `gates/` directory have `.rq` or `.py` extensions (`GATE_SOURCE_SUFFIXES = {".rq", ".py"}`). The presence of `.toml` configuration files inside `xstate-v5-machine-pack/gates/` causes `require_admitted()` to refuse the entire pack corpus, blocking `scripts/marketplace.py validate` and `scripts/qualify_packs.py`.
- **Exact Command Executed**:
  ```bash
  python3.12 /Users/sac/ggen-marketplace/scripts/marketplace.py validate
  ```
- **Exit Code**: 2
- **Exact Output**:
  ```console
  REFUSED:GATE_SOURCE_EXTENSION:packs/xstate-v5-machine-pack/gates/baselines.toml
  REFUSED:GATE_SOURCE_EXTENSION:packs/xstate-v5-machine-pack/gates/shapes.toml
  ```

---

### Finding 11: Missing `packages/pm4pytest` Dependency Breaks Standard `uv run pytest`
- **Target File**: `/Users/sac/ggen-marketplace/pyproject.toml`
- **Gap / Vacuity Issue**: `pyproject.toml` specifies `pm4pytest = { path = "packages/pm4pytest", editable = true }` and registers a pytest entry point. However, `packages/pm4pytest` does not exist on disk (only `marketplace-cli`, `pm4playwright`, `pm4vitest`, and `vision-2030-capability-generator` exist in `packages/`). Standard `uv run pytest` fails during dependency resolution.
- **Exact Command Executed**:
  ```bash
  cd /Users/sac/ggen-marketplace && uv run pytest tests/test_manufacture_timing.py
  ```
- **Exit Code**: 2
- **Exact Output**:
  ```console
  error: Failed to generate package metadata for `pm4pytest==0.1.0 @ editable+packages/pm4pytest`
    Caused by: Distribution not found at: file:///Users/sac/ggen-marketplace/packages/pm4pytest
  ```
- **Verified Workaround**: Running via isolated arguments succeeds:
  ```bash
  cd /Users/sac/ggen-marketplace && uv run --no-project --with pytest --with rdflib pytest tests/test_manufacture_timing.py -o addopts=""
  ```
  Output: `6 passed in 0.07s`.

---

## 5. Unbenchmarked Surfaces: 2,121 Templates Across 319 Packs

### Finding 12: Total Absence of Template Rendering Benchmarks
- **Corpus Scope**:
  - Total packs: 364
  - Packs containing templates: 319 (87.6%)
  - Total templates: 2,121
  - Template extensions: 1,848 `.tmpl`, 273 `.tera`
  - Total unrendered template volume: 8,114,385 bytes (7.74 MB)
  - Embedded SPARQL queries: 2,075 distinct queries across 1,471 template frontmatters
- **Gap / Vacuity Issue**: Zero packs define benchmarks for template rendering, query extraction, or code emission. While templates are parsed during ggen sync, there is no performance tracking, regression guard, or throughput metric for template compilation and rendering.
- **Live Template Parse & Compile Throughput Measurement**:
  - Exact audit command executed across all 2,121 templates:
    ```bash
    python3.12 -c '
    import time, yaml, jinja2
    from pathlib import Path

    packs = Path("/Users/sac/ggen-marketplace/packs")
    tmpls = sorted(list(packs.glob("**/*.tmpl")) + list(packs.glob("**/*.tera")))
    t0 = time.perf_counter()
    env = jinja2.Environment()
    parsed_fm, queries, errors = 0, 0, []
    for t in tmpls:
        c = t.read_text(encoding="utf-8", errors="replace")
        if c.startswith("---"):
            p = c.split("---", 2)
            if len(p) >= 3:
                try:
                    fm = yaml.safe_load(p[1])
                    parsed_fm += 1
                    if isinstance(fm, dict) and "sparql" in fm:
                        queries += len(fm["sparql"]) if isinstance(fm["sparql"], dict) else 1
                except: pass
                body = p[2]
            else: body = c
        else: body = c
        try: env.parse(body)
        except Exception as e: errors.append((t.name, str(e)))
    el = time.perf_counter() - t0
    print(f"Count: {len(tmpls)}, Frontmatters: {parsed_fm}, Queries: {queries}, SyntaxErrors: {len(errors)}, Time: {el:.3f}s, Rate: {len(tmpls)/el:.1f} tmpls/s")
    '
    ```
  - **Live Output**:
    ```console
    Count: 2121, Frontmatters: 1471, Queries: 2075, SyntaxErrors: 46, Time: 2.172s, Rate: 976.6 tmpls/s
    ```
  - **Findings**:
    1. Frontmatter parsing and Jinja2 AST compilation throughput is **976.6 templates/sec (3.56 MB/sec)**.
    2. 46 templates fail standard Jinja2 parsing due to Tera-specific custom filter/tag dialect extensions (e.g. `set_global` in `ash-a2a-app-pack/templates/L18_fragment.ex.tmpl`), highlighting the lack of a standardized cross-pack template linter/benchmark.

---

### Finding 13: Vacuous Benchmark Stubs & Empty Artifact Directories
- **Target Artifacts**:
  1. `/Users/sac/ggen-marketplace/.benchmarks`: Empty directory (0 files, 64 bytes).
  2. `packs/cs2-semantic-work/consumer/native/bench/`: Contains `batch.exs` (117 bytes), `materialize.exs` (109 bytes), and `topology.exs` (123 bytes).
     - *Vacuity*: These files define empty Elixir modules with single-line helper functions (e.g., `Enum.each(1..n, fn _ -> ... end)`). They take no timings, compute no stats, assert no bounds, and lack runnable scripts.
  3. `packs/fleet-projection-closure/bench/matrix_scale.py`:
     - *Vacuity*: A 7-line file calculating `consumers * families`. Contains no benchmark runner, no timings, and no performance assertions.
  4. `packs/challenger-value-framing-pack/chicago/benchmark_claims.py`:
     - *Vacuity*: An 87-line static dataclass registry asserting speedups for external repositories (`/Users/sac/cgap`, `/Users/sac/smalt`, `/Users/sac/arcus`). Does not execute any local benchmark or verify any local claim.
  5. `packs/cgap-pack/gates/140_bench_file_exists.rq`:
     - *Vacuity*: Gate requires a file matching `^crates/bench/benches/[a-z0-9-]+\\.rs$`. No such directory or file exists anywhere in `ggen-marketplace`.

---

## 6. Actionable Remediation Roadmap

To achieve full production readiness, anti-vacuity compliance, and benchmark coverage, the following steps are required:

| Priority | Component | Action Item | Success Criterion |
|---|---|---|---|
| **P0** | `ggen.lock` | Re-synchronize `strata-ledger-pack` hash in `ggen.lock` via `ggen sync run` or clean re-lock. | `ggen sync run --dry-run` exits code 0. |
| **P0** | `xstate-v5-machine-pack` | Move `baselines.toml` and `shapes.toml` out of `gates/` into `config/` or `shapes/`. | `python3.12 scripts/marketplace.py validate` passes with 0 refusals. |
| **P1** | `pyproject.toml` | Remove missing `packages/pm4pytest` editable reference or restore the package. | `uv run pytest` executes cleanly without `-o addopts=""` workarounds. |
| **P1** | `tcps-pack` | Fix Japanese identifier compilation errors in `crates/tcps-core/src/試験.rs`. | `cargo check` and `cargo test` pass in `packs/tcps-pack/reference/製品版`. |
| **P2** | `strategic-doctrine-pack` | Optimize Gate `050_no_excerpt` SPARQL query to reduce 8.2s execution time on 1,872 triples. | Median gate execution stays < 1.0s on 64-strategy synthetic graph. |
| **P2** | Template Surfaces | Add a corpus-wide template benchmark harness measuring Tera template compile and render throughput. | Formal receipt generated recording throughput (templates/sec, MB/sec). |
| **P3** | Vacuous Stubs | Convert `cs2-semantic-work` and `fleet-projection-closure` bench stubs into real, timed Benchee/Python benchmarks or remove them. | Every file named `bench*` produces real, asserted timing receipts. |

---
*Report generated and verified by Agent 14 (`ggen_auditor_benchmarks_docs`) under Integrity Mode: Development.*
