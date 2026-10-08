# rust-wasi-wasmex-pack

Unified **Rust > WASM > Elixir** pipeline generator pack.

Coordinates both sides of the WebAssembly execution seam:
1. **Guest (Rust):**
   - Target: `wasm32-wasip1`
   - Cargo configuration (`.cargo/config.toml`) with stack size `4194304` (4 MiB)
   - Size-optimized profile `[profile.wasm]` (`opt-level = "s"`, `lto = true`, `codegen-units = 1`, `strip = true`, `panic = "abort"`)
   - Safe FFI linear-memory boundary (`<prefix>_alloc`, `<prefix>_call`, `<prefix>_free`)
   - Internal allocation accounting (`OUTSTANDING: AtomicUsize`) preventing linear memory overflow
   - Fail-closed error envelopes on guest failure instead of guest traps
2. **Host (Elixir):**
   - Direct execution via `Wasmex.Store.new`, `Wasmex.Module.compile`, `Wasmex.start_link`
   - Strict startup admission: authoritative SHA-256 binary digest verification
   - Import surface allowlist validation
   - Parameter unmarshalling for packed-u64 (`(out_ptr << 32) | out_len`)
   - Guaranteed cleanup in `try ... after` blocks
   - Fail-closed error normalization into typed `%Refusal{}` structs
   - Content-addressed manifest generation (`wasmex_host_manifest.json`)
3. **End-to-End Test Court:**
   - Parameterized test asserting round-trip execution, memory reclamation over 100 consecutive calls, malformed input rejection, and watchdog timeout handling.

## Queries

- `queries/registry.rq` — single-row aggregate of scalar module facts, consumed by
  `templates/abi/capability_registry.json.tmpl` (the `wasm-capability-registry` rule).
- `queries/artifacts.rq` — the lawful query for the `wasm-artifacts` rule
  (`templates/abi/artifacts.sha256.tmpl`). It projects the pin facts
  (`wja:wasmSha256`, `wja:wasmBytes`, `wja:registrySha256`, `wja:surfaceSha256`) that
  `registry.rq` cannot carry; each optional pin column binds `""` when the consumer
  graph carries no such fact, and the template then keeps its placeholder skeleton.

### Migration note (consumer `ggen.toml` rewiring required)

The `wasm-artifacts` rule's query is specified in each consumer's `ggen.toml`, so this
pack-side addition alone does not rewire existing consumers. On your next lawful
`ggen sync`, update the rule from

```toml
query = { pack = "rust-wasi-wasmex-pack", output = "queries", file = "registry.rq" }
```

to

```toml
query = { pack = "rust-wasi-wasmex-pack", output = "queries", file = "artifacts.rq" }
```

Consumers currently wiring `wasm-artifacts` to `registry.rq` (rendering placeholder
pins despite real pin facts in their graphs): `affidavit` (`ggen.toml`, `wasm-artifacts`
rule), `ferroplan` (`ggen.toml`, `wasm-artifacts` rule). `ash_graphlaw` consumes the
pack's gates but has no `wasm-artifacts` rule and requires no change.

## Precursor Pack Consolidation
This pack supersedes and deprecates:
- `wasi-json-abi-pack`
- `beam-wasmex-host-pack`
