# _UNIFIED_WASM_PACK_RECEIPT.md

## UNIFIED RUST > WASM > ELIXIR PACK RECEIPT

- **Repository Root:** `~/ggen-marketplace`
- **Commit SHA:** `e987f3717fead9b2f503a049bb39b49ae88b02d3`
- **Canonical Pack:** `packs/rust-wasi-wasmex-pack/`
- **Deprecated Precursors:**
  - `packs/wasi-json-abi-pack` (deprecated via `DEPRECATED.md`, documented in `CONSOLIDATION_MAP.md`)
  - `packs/beam-wasmex-host-pack` (deprecated via `DEPRECATED.md`, documented in `CONSOLIDATION_MAP.md`)

---

### 1. File Tree of `packs/rust-wasi-wasmex-pack/`

```
packs/rust-wasi-wasmex-pack/
├── README.md
├── pack.toml
├── ontology.ttl
├── shapes/
│   └── rww.shacl.ttl
├── fixtures/
│   └── probe_eval.ttl
├── gates/
└── templates/
    ├── guest/
    │   ├── Cargo.toml.tmpl
    │   ├── cargo_config.toml.tmpl
    │   └── ffi.rs.tmpl
    ├── host/
    │   ├── mix_deps.exs.tmpl
    │   ├── wasm_host.ex.tmpl
    │   └── wasmex_host_manifest.json.tmpl
    └── test/
        └── wasm_host_court.exs.tmpl
```

---

### 2. SHACL / Turtle Validation Status

- **Turtle Syntax:**
  ```
  rapper: Parsing URI file:///Users/sac/ggen-marketplace/packs/rust-wasi-wasmex-pack/ontology.ttl with parser turtle
  rapper: Parsing returned 67 triples (EXIT 0)
  ```
- **SHACL Conformance:**
  - Validated with `pyshacl` over `ontology.ttl` + `fixtures/probe_eval.ttl` against `shapes/rww.shacl.ttl`.
  - Result: `Conforms: True` (0 violations).

---

### 3. Verification Test Court Run

#### A. Guest Compilation & Export Inspection
- **Target:** `probe_eval_wasm` compiled with `cargo build --target wasm32-wasip1 --profile wasm`
- **Binary Size:** 78,698 bytes (`/tmp/probe_eval_test/target/wasm32-wasip1/wasm/probe_eval_wasm.wasm`)
- **Exported Symbols (Wasmtime Inspection):**
  - `memory`
  - `probe_eval_alloc`
  - `probe_eval_call`
  - `probe_eval_free`
- **Roundtrip Execution:**
  - Request: `{"test":"hello_wasm"}`
  - Response: `{"echo":{"test":"hello_wasm"},"ok":true}`
  - Deallocation verified with `probe_eval_free` without memory leaks.

#### B. Elixir Host Syntax & Compilation Check
- **Compiler:** Elixir 1.20.3 (Erlang/OTP 28)
- **Host Module:** `ProbeEval.Wasm.GeneratedHost`
- **Syntax / Bytecode Compilation:**
  - Compiled clean with `elixirc` into `.beam` files (`Elixir.ProbeEval.Wasm.GeneratedHost.beam`, `Elixir.ProbeEval.Wasm.GeneratedHost.Refusal.beam`).
  - Zero compilation errors.

---

### 4. Downstream Guidance
- `~/graphlaw`: Reference `rust-wasi-wasmex-pack` in `ggen.toml` to emit the guest FFI shell.
- `~/xaas`: Reference `rust-wasi-wasmex-pack` to emit `Wasmex` host modules and manifest records.
