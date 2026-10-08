# Tutorial: graphlaw through rust, wasm and beam

> [!WARNING]
> `wasi-json-abi-pack` is **DEPRECATED** (lifecycle state recorded in `lifecycle.toml`). Its capabilities are consolidated into [`packs/rust-wasi-wasmex-pack`](../../packs/rust-wasi-wasmex-pack/) — migrate generator wiring there.


You will render graphlaw's wasm ABI projection from RDF, read what it carries, and watch a gate
refuse a broken import. It stops before DO: nothing here runs the graphlaw module.

## 1. Read the consumer facts

`packs/wasi-json-abi-pack/qualification/graphlaw-consumer.ttl` declares module `graphlaw-wasm`
(prefix `gl`, 14 ops, five refusal kinds) and `graphlaw-ops.ttl` adds per-op fields, the 7
`wasi_snapshot_preview1` imports and the release pins.

## 2. Run the court

```bash
python3 scripts/check_gate_witness_courts.py
python3 -m pytest tests/test_wasi_json_abi_graphlaw.py -q
```

The test renders the graphlaw profile with the real `ggen` in a scratch copy and compares it
byte-for-byte with `generated/graphlaw/`.

## 3. Read the projection

`generated/graphlaw/capability-registry.json` lists the 14 ops in order;
`generated/graphlaw/ARTIFACTS.sha256` holds the pins taken from graphlaw's own
`registry/ARTIFACTS.sha256` at the pinned release SHA.

## 4. Break it

Copy `witnesses/pass/080_wasi_import_closure.ttl` to a scratch file and change one
`wja:importModule` to `"env"`. From the pack directory run
`python3 runners/semantic_runner.py --gate gates/080_wasi_import_closure.rq --witness <scratch file> --expectation fail`:
gate 080 returns a row and the module is refused as not WASI-only.

## 5. Where it stops

The Elixir surface is `graphlaw-ash-capability-pack`, the qualified host is
`qri-qualification-profile-pack`; both are separate hops. This tutorial grants no authority and
establishes no exact-SHA run of the wasm module.

## See Also

[Reference: wasi-json-abi-pack](../reference/wasi-json-abi-pack.md) ·
[Reference: the graphlaw pipeline](../reference/graphlaw-rust-wasm-beam-pipeline.md) ·
[How to consume graphlaw through wasi-json-abi](../how-to/consume-graphlaw-through-wasi-json-abi.md)
