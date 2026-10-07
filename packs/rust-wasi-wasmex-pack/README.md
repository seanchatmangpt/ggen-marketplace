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

## Precursor Pack Consolidation
This pack supersedes and deprecates:
- `wasi-json-abi-pack`
- `beam-wasmex-host-pack`
