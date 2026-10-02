# echo-wasm ABI

Generated companion to the capability registry (`registry/capability-registry.json`):
both are projections of the same `wja:` graph, rendered by ggen
(wasi-json-abi-pack). Regenerate; do not edit.

## Summary

- ABI version 1, wasm32 target (pointers and `usize` lower to `i32`).
- 5 core exports, 2 request/response algorithms, 1 replay companions.
- Imports policy: `none` (zero imports: the module is self-contained and imports nothing at all).
- Startup: WASI reactor (`_initialize`).

## Calling convention

1. `ptr = w4p_alloc_v1(len)`; write the UTF-8 JSON request into linear memory at `ptr`.
2. Call `w4p_call_v1(ptr, len, out_len_ptr)`; the response length is written through `out_len_ptr` and the response pointer is returned.
3. Read `out_len` bytes at `out_ptr` (UTF-8 JSON), then release with `w4p_free_v1(out_ptr, out_len)`.
4. Release the request buffer with `w4p_dealloc_v1(ptr, len)` (same `len` as
   `w4p_alloc_v1`). Reading an input never frees it; the host owns that release.

## Envelope
- Success: `{"result": <body>, "digest": "<16 lowercase hex chars>"}`
- Failure (unparsable request): `{"error": "<message>"}` — no digest.

## Digest and replay

- Digest: FNV-1a-64 over the result-body serialization bytes,
  formatted `{:016x}` (16 lowercase hex chars).
  Non-cryptographic in-WASM self-check; receipt identity hashing stays with the consumer.
- `<algo>_replay` exports re-execute the computation from the same request bytes and
  return 1 iff the recomputed response is non-empty; hosts compare the `digest` field
  of the original and recomputed responses. Computations are deterministic, so equal
  requests yield equal digests.

## Memory ownership

| Buffer | Produced by | Released by |
|---|---|---|
| request | `w4p_alloc_v1(len)` | host, `w4p_dealloc_v1(ptr, len)` |
| response | `w4p_call_v1` | host, `w4p_free_v1(ptr, out_len)` |

## Algorithms

echo, len

## Exports

| export | kind | params | result | source |
|---|---|---|---|---|
| `w4p_alloc_v1` | core | `(len: i32)` | i32 | - |
| `w4p_call_v1` | core | `(ptr: i32, len: i32, out_len: i32)` | i32 | - |
| `w4p_dealloc_v1` | core | `(ptr: i32, len: i32)` | - | - |
| `w4pm_echo_replay_v1` | replay | `(ptr: i32, len: i32)` | i32 | src/lib.rs |
| `w4pm_echo_v1` | request_response | `(ptr: i32, len: i32, out_len: i32)` | i32 | src/lib.rs |
| `w4pm_len_v1` | request_response | `(ptr: i32, len: i32, out_len: i32)` | i32 | src/lib.rs |
| `w4pm_module_version_v1` | core | `()` | i32 | - |
