# HANDWRITTEN-graphlaw.md — graphlaw-wasm residue ledger

Companion to `HANDWRITTEN.md` for the `graphlaw-wasm` consumer
(`qualification/graphlaw-consumer.ttl`). Enumerable facts (crate name, export prefix, ABI
version, request and depth limits, stack size, error style, ops, error codes) live in that graph;
`ffi.rs` is not selected. Rows below are hand-written residue.

| path | kind | standing | reason |
|---|---|---|---|
| `wasm/src/lib.rs` OUTSTANDING counter and 256 MiB outstanding-allocation cap | consumer code | UNSUPPORTED(generator-capability) | needs a `wja:maxOutstandingBytes` fact and an accounted allocator template; neither exists in the pack |
| `MAX_PLAN_ACTIONS`, `MAX_ATOMS_PER_FIELD`, `MAX_POLICY_ENTRIES` and `plan_total_atoms` consts | consumer code | UNSUPPORTED(generator-capability) | engine admission caps are not `wja:` facts; the pack has no per-op cap vocabulary |
| refusal-kind error envelope (kind, dialect, engine; error codes NotSemanticContent, Ambiguous, EngineRejected, Unsupported, ResourceLimit) | consumer code | UNSUPPORTED(generator-capability) | `wja:errorStyle` = refusal-kind generates only `json_depth` and the ordering helper; the envelope is consumer-owned |
| op bodies (request decoding and engine dispatch behind each of the 14 `wja:Op` rows) | consumer code | UNSUPPORTED(generator-capability) | op semantics are not enumerable ontology facts; the generated dispatch table names the hand-written bodies |

## See Also

- [HANDWRITTEN.md](HANDWRITTEN.md)
