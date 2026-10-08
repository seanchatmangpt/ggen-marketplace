# Reference: wasi-json-abi-pack

> [!WARNING]
> `wasi-json-abi-pack` is **DEPRECATED** (lifecycle state recorded in `lifecycle.toml`). Its capabilities are consolidated into [`packs/rust-wasi-wasmex-pack`](../../packs/rust-wasi-wasmex-pack/) — migrate generator wiring there.


`packs/wasi-json-abi-pack` renders the host-facing shell of a WASI JSON-ABI module from an
ontology of `wja:WasmModule`, `wja:Op`, `wja:ErrorCode` and `wja:WasiImport`. Namespace
`https://ggen.dev/ontology/wasi-json-abi#`, prefix `wja:`. Authority NONE.

## Vocabulary

| term | domain | meaning |
|---|---|---|
| `wja:crateName`, `wja:exportPrefix`, `wja:abiVersion` | module | identity of the crate and its `<prefix>_alloc/_free/_call` exports |
| `wja:maxRequestBytes`, `wja:maxJsonDepth`, `wja:stackSizeBytes` | module | limits and stack size |
| `wja:importsPolicy` | module | must be `wasi_snapshot_preview1` |
| `wja:errorStyle` | module | closed set; `flat-code` and `refusal-kind` |
| `wja:hasOp`, `wja:opName`, `wja:opOrder`, `wja:requestFields`, `wja:responseFields`, `wja:exampleRequest` | op | ordered op table |
| `wja:hasErrorCode`, `wja:codeName`, `wja:codeOrder` | error code | ordered code table |
| `wja:hasWasiImport`, `wja:importModule`, `wja:importName` | import | enumerated host imports |
| `wja:wasmSha256`, `wja:wasmBytes`, `wja:registrySha256`, `wja:surfaceSha256` | module | release pins |
| `wja:wasmEnvVar`, `wja:wasmBuildPackage`, `wja:nativeCall`, `wja:hasAbiVersionExport`, `wja:cfgGate`, `wja:pinEnv`, `wja:examplesPath` | module | harness and guard parameters |

## Consumer graphs

| graph | profile | renders to |
|---|---|---|
| `qualification/consumer.ttl` (toy `echo-wasm`) | `ggen.toml` | `generated/` |
| `qualification/graphlaw-consumer.ttl` + `qualification/graphlaw-ops.ttl` (graphlaw v26.9.29) | `ggen-graphlaw.toml` | `generated/graphlaw/` |

ggen reads only `./ggen.toml`; render a non-default profile by copying it to `ggen.toml` in a
scratch copy of the pack and running `ggen sync run`.

## Projections

ABI metadata, capability registry, op examples, cargo config and profile fragments, an artifact
pin file, guards and a test harness. The `ffi` rule belongs to `ggen.toml` only; graphlaw
hand-writes its exports (see `HANDWRITTEN-graphlaw.md`).

## Gates

Violation-row SPARQL SELECTs under `packs/wasi-json-abi-pack/gates/`, each with same-stem
witnesses and a case in `gate-court.toml`, the canonical list. They cover module properties, op
and error-code order closure, export prefix, limits, import policy, error style, import closure
and pin shape.

## Standing

Marketplace boundary only: deterministic render and gate courts. Pins are recorded values, not
live checks of a binary. No exact-SHA execution of a rendered module is evidenced. See
[standing](standing.md).

## Verification

```bash
python3 scripts/marketplace.py check wasi-json-abi-pack
python3 scripts/check_gate_witness_courts.py
python3 -m pytest tests/test_wasi_json_abi_graphlaw.py -q
```

## See Also

- [Reference: the graphlaw pipeline](graphlaw-rust-wasm-beam-pipeline.md)
- [Tutorial: graphlaw through rust, wasm and beam](../tutorials/graphlaw-rust-wasm-beam.md)
- [How to consume graphlaw through wasi-json-abi](../how-to/consume-graphlaw-through-wasi-json-abi.md)
- [Why the pipeline is split](../explanation/rust-wasm-beam-pipeline.md)
