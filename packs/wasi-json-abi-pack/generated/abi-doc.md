# echo-wasm ABI

Generated companion to the capability registry (`registry/capability-registry.json`):
both are projections of the same `wja:` graph, rendered by ggen
(wasi-json-abi-pack). Regenerate; do not edit.

## Summary

- ABI version 1, wasm32 target (pointers and `usize` lower to `i32`).
- 4 core exports plus one dispatch entry (`ex_call`) serving 2 ops.
- Imports policy: `wasi_snapshot_preview1`.
- Startup: default `cdylib` command startup.

## Calling convention

1. `ptr = ex_alloc(len)`; write the UTF-8 JSON request into linear memory at `ptr`.
2. Call `ex_call(ptr, len)`; the packed `u64` result encodes `(out_ptr << 32) | out_len`.
3. Read `out_len` bytes at `out_ptr` (UTF-8 JSON), then release with `ex_free(out_ptr, out_len)`.

## Envelope
- Success: `{"ok": true, ...}` with the op's response fields.
- Failure: `{"ok": false, "error": {"code": <code>, "message": ...}}` with string
  codes drawn from the module's error table.

## Memory ownership

| Buffer | Produced by | Released by |
|---|---|---|
| request | `ex_alloc(len)` | the module, inside `ex_call` |
| response | `ex_call` | host, `ex_free(ptr, out_len)` |

## Algorithms

echo, len

## Exports

| export | kind | params | result | source |
|---|---|---|---|---|
| `ex_abi_version` | core | `()` | i32 | - |
| `ex_alloc` | core | `(len: i32)` | i32 | - |
| `ex_call` | core | `(ptr: i32, len: i32)` | i64 | - |
