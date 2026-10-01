# HANDWRITTEN-graphlaw.md — graphlaw-wasm residue ledger

Companion to `HANDWRITTEN.md` for the `graphlaw-wasm` consumer
(`qualification/graphlaw-consumer.ttl`). Enumerable facts (crate name, export prefix, ABI
version, request and depth limits, stack size, error style, ops, error codes, and the allocation
discipline: `wja:bufferStyle` vec, `wja:maxOutstandingBytes` 268435456, `wja:hasAbiVersionExport`
false, `wja:abiModulePath` graphlaw::abi) live in that graph. `generated/graphlaw/ffi.rs` is now
generated and replaces the body of `wasm/src/lib.rs` (the 256 MiB OUTSTANDING accounting, vec
buffers, no `gl_abi_version` export). Rows below are hand-written residue.

## Differential evidence (generated ffi.rs vs hand-written lib.rs)

`tests/test_wasi_json_abi_graphlaw.py::test_generated_ffi_matches_handwritten_lib_on_graphlaw_wasm_abi_suite`
builds graphlaw v26.9.29 (`0bb0df2a`, exact-SHA `git archive`) for wasm32-wasip1 twice in a scratch tree: once
with the hand-written `wasm/src/lib.rs`, once with `generated/graphlaw/{ffi,abi_meta}.rs` behind a
declarations-only `lib.rs`. Both artifacts export the same names (`gl_alloc`, `gl_free`, `gl_call`, `memory`)
and pass the same graphlaw `tests/wasm_abi.rs` suite under wasmi, including
`wasm_outstanding_allocation_cap_refuses_then_recovers_after_free`. The test skips with a `BLOCKED:` reason when
`ggen`, `cargo`/`rustup`, graphlaw at the pinned SHA, or the `wasm32-wasip1` target (as resolved by graphlaw's
`rust-toolchain.toml`) is absent. The pin is a release snapshot, not a live graphlaw tree.

| path | kind | standing | reason |
|---|---|---|---|
| `wasm/src/lib.rs` module wiring in graphlaw (`mod abi_meta; mod ffi;` plus the two generated files placed under `wasm/src/`) | consumer code | UNSUPPORTED(generator-capability) | the pack renders the shell and metadata but does not place files into the consumer crate or emit its `lib.rs`; graphlaw's checked-in `wasm/src/lib.rs` is still the hand-written original until graphlaw adopts the generated files (verified only in a scratch tree) |
| `MAX_PLAN_ACTIONS`, `MAX_ATOMS_PER_FIELD`, `MAX_POLICY_ENTRIES` and `plan_total_atoms` consts | consumer code | UNSUPPORTED(generator-capability) | engine admission caps are not `wja:` facts; the pack has no per-op cap vocabulary |
| refusal-kind error envelope (kind, dialect, engine; error codes NotSemanticContent, Ambiguous, EngineRejected, Unsupported, ResourceLimit) | consumer code | UNSUPPORTED(generator-capability) | `wja:errorStyle` = refusal-kind generates only `json_depth` and the ordering helper; the envelope is consumer-owned |
| op bodies (request decoding and engine dispatch behind each of the 14 `wja:Op` rows) | consumer code | UNSUPPORTED(generator-capability) | op semantics are not enumerable ontology facts; the generated dispatch table names the hand-written bodies |

## See Also

- [HANDWRITTEN.md](HANDWRITTEN.md)
