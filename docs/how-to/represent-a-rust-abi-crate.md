# How to represent a Rust ABI crate end to end

Goal: take a Rust crate exposing a JSON ABI over a WASI module and represent it through the
marketplace packs, using graphlaw as the worked specimen.

## Prerequisites

- `ggen` on `PATH`; Python 3.11.
- The crate checkout, its release SHA, and a built module at that SHA.

## Steps

### 1. Pin the subject

Record the crate's commit SHA and version. Read facts from `git show <sha>:path`, not the working
tree: a dirty checkout moves its own pins.

### 2. Write the wasm consumer graph

Under `packs/wasi-json-abi-pack/qualification/` add `<crate>-consumer.ttl` with one
`wja:WasmModule` (crate name, export prefix, `wja:abiVersion`, limits, stack size,
`wja:importsPolicy "wasi_snapshot_preview1"`, error style), its `wja:Op` rows with contiguous
`wja:opOrder`, and its `wja:ErrorCode` rows. Add `<crate>-ops.ttl` with per-op
`wja:requestFields`, `wja:responseFields`, `wja:exampleRequest`, the `wja:WasiImport` individuals
read from the module's import section, and the pin facts from the crate's artifact file.

### 3. Add the profile and render

Copy `ggen-graphlaw.toml` to `ggen-<crate>.toml`, point `source`/`imports` at the new graphs and
`output_file` at `generated/<crate>/`. Omit the `ffi` rule when the crate hand-writes its exports.
ggen reads only `./ggen.toml`, so render in a scratch copy:

```bash
cp ggen-<crate>.toml ggen.toml && ggen sync run
```

Copy the rendered `generated/<crate>/` back. Never edit generated files; change the graph and
re-render.

### 4. Record residue

Add `HANDWRITTEN-<crate>.md` listing hand-written code and why the generator cannot cover it, each
as `UNSUPPORTED(generator-capability)`.

### 5. Bind the later hops

Add a QRI contract under `qri-qualification-profile-pack/ontology/examples/` for the qualified
runtime and projection, and a registry consumer for `graphlaw-ash-capability-pack`-style typed
surfaces. Add Chicago court cases if the crate has a published corpus.

### 6. Run the gates

```bash
python3 scripts/marketplace.py check wasi-json-abi-pack
python3 scripts/check_gate_witness_courts.py
python3 -m pytest tests/test_wasi_json_abi_graphlaw.py   # copy and adapt for the new crate
python3 scripts/standing.py --check
python3 scripts/pack_capabilities.py --check
python3 scripts/marketplace.py catalog > /tmp/a.json && python3 scripts/marketplace.py catalog > /tmp/b.json && cmp /tmp/a.json /tmp/b.json
```

A new gate needs same-stem pass and fail witnesses and a `[[case]]` in `gate-court.toml`.

## Refusals

- `TEMPLATE_VARIABLE_MISSING` at render: an op lacks fields or an example; add them, nothing is
  defaulted.
- Gate 080 or 090 rows: fix the import or digest facts.
- Hand-written exports with no generator capability: record `UNSUPPORTED(generator-capability)`,
  do not mock execution into ALIVE.

## See Also

- [Reference: the pipeline](../reference/graphlaw-rust-wasm-beam-pipeline.md)
- [Why the pipeline is split](../explanation/rust-wasm-beam-pipeline.md)
- [Qualify a realization](qualify-a-realization.md)
