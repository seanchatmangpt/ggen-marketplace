# HANDWRITTEN.md — wasi-json-abi-pack ledger

Enumerable facts (module identity, export prefix, ABI version, limits, stack size,
imports policy, error style and limit codes, allocation discipline (`wja:bufferStyle`, `wja:maxOutstandingBytes`,
`wja:abiModulePath`, `wja:hasAbiVersionExport`), harness env/build/native-call facts, ops, error codes) live in `ontology.ttl` and consumer graphs; the
rendered projections are never hand-edited.

| path | kind | standing | reason |
|---|---|---|---|
| pack.toml, targets.toml, package.toml, ggen.toml | manifest | n/a (ggen-produced by definition) | pack admission and rule binding |
| ontology.ttl | ontology | n/a (ggen-produced by definition) | source graph |
| queries/*.rq | query | n/a (ggen-produced by definition) | SELECT projections over the ontology |
| templates/* | template | n/a (ggen-produced by definition) | render ontology facts |
| gates/*.rq (incl. 100_alloc_discipline_closed), gate-court.toml | gate | n/a (ggen-produced by definition) | admission gates over consumer graphs |
| witnesses/{pass,fail}/*.ttl | witness | n/a (ggen-produced by definition) | gate court evidence |
| runners/semantic_runner.py | runner | n/a (copied verbatim) | gate court runner |
| consumer op bodies (request decoding, domain logic behind each wja:Op) | consumer code | UNSUPPORTED(generator-capability) | domain semantics of an op are not enumerable ontology facts; the consumer hand-writes them and the generated dispatch table names them |
| consumer host glue (build scripts, CI wiring) | consumer code | UNSUPPORTED(generator-capability) | CI and build-script wiring is outside the projection; the wasmi test harness (`generated/tests_common.rs`) and guard prelude (`generated/guards.rs`) are now generated from the `wja:` facts |
| refusal-kind error envelope (`limit_response`, `missing_buffer_response`, error body, `encode` when `wja:errorStyle` = refusal-kind) | consumer code | UNSUPPORTED(generator-capability) | a consumer-owned refusal envelope (kind/dialect/engine) is not an enumerable flat-code table; `generated/guards.rs` emits only `json_depth` and the op/error-code ordering helpers for this style, and the harness asserts only `ok == false` for limit cases |
| the `abi_meta` import and safe-core path wiring in the consumer crate (`mod abi_meta;`, the module named by `wja:abiModulePath`) | consumer code | UNSUPPORTED(generator-capability) | the shell renders `use crate::abi_meta::*` and `<abiModulePath>::call`; declaring those modules in the consumer's `lib.rs` is outside the projection |
