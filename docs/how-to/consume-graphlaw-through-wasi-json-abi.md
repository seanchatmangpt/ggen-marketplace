# How to consume graphlaw through wasi-json-abi

Goal: regenerate graphlaw's wasm ABI projection after the graphlaw subject or its pins change.

## Prerequisites

- `ggen` on `PATH`; Python 3.11 with `rdflib` and `pytest`.
- The graphlaw checkout at `~/graphlaw` and the release SHA you are pinning.

## Steps

1. Read ops, limits and pins at the SHA, not the working tree:
   `git -C ~/graphlaw show <sha>:registry/capability-registry.json` and
   `git -C ~/graphlaw show <sha>:registry/ARTIFACTS.sha256`.
2. Update `qualification/graphlaw-consumer.ttl` (module facts, ops, error codes) and
   `qualification/graphlaw-ops.ttl` (fields, examples, imports, pins). Imports come from the import
   section of the module built at that SHA.
3. Render in a scratch copy of the pack, then copy `generated/graphlaw/` back:
   ```bash
   cp ggen-graphlaw.toml ggen.toml && ggen sync run
   ```
4. Update `GRAPHLAW_SHA` in `tests/test_wasi_json_abi_graphlaw.py`.
5. Run the gates:
   ```bash
   python3 scripts/marketplace.py check wasi-json-abi-pack
   python3 scripts/check_gate_witness_courts.py
   python3 -m pytest tests/test_wasi_json_abi_graphlaw.py -q
   ```

## Refusals

- `REFUSED` by gate 080: an import outside `wasi_snapshot_preview1` or without a name.
- `REFUSED` by gate 090: a digest that is not 64-char lowercase hex.
- Render error `TEMPLATE_VARIABLE_MISSING` or zero rows: an op lacks `requestFields`,
  `responseFields` or `exampleRequest`; nothing is defaulted.
- A dirty graphlaw working tree has different pins than the release; use the SHA.

## See Also

[Reference: wasi-json-abi-pack](../reference/wasi-json-abi-pack.md) ·
[Tutorial: graphlaw through rust, wasm and beam](../tutorials/graphlaw-rust-wasm-beam.md) ·
[How to represent a Rust ABI crate](represent-a-rust-abi-crate.md)
