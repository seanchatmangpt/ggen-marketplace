# Reference: graphlaw rust, wasm, beam/elixir pipeline

> [!WARNING]
> `wasi-json-abi-pack` is **DEPRECATED** (lifecycle state recorded in `lifecycle.toml`). Its capabilities are consolidated into [`packs/rust-wasi-wasmex-pack`](../../../packs/rust-wasi-wasmex-pack/) — migrate generator wiring there.


The marketplace represents `~/graphlaw` (release v26.9.29, pinned at
`0bb0df2a93293af5447bbe22f2a38eb645204f4c`) through four packs, one per hop of the
rust > wasm > beam/elixir path. Each pack projects consequences from RDF; none executes graphlaw
or grants DO authority.

## Hops

| hop | pack | input graph | projection | gate court |
|---|---|---|---|---|
| rust crate ABI to wasm module | `wasi-json-abi-pack` | `qualification/graphlaw-consumer.ttl`, `qualification/graphlaw-ops.ttl` | `generated/graphlaw/` (ABI metadata, capability registry, op examples, cargo stack and profile, artifact pins, guards, test harness) | gates 010-090, 9 cases |
| wasm module to qualified runtime | `qri-qualification-profile-pack` | `ontology/examples/graphlaw-contract.ttl` | WIT, ABI ledger, Rust adapter, wasmex BEAM host | 10 gates |
| registry to Elixir capability surface | `graphlaw-ash-capability-pack` | graphlaw `registry/capability-registry.json` as RDF | behaviour, registry, per-op modules, result structs, docs, surface test | see the pack's `gate-court.toml` |
| evidence | `chicago-graphlaw-court-pack` | `cases/*.ttl` | Chicago-style Rust court tests over `graphlaw::abi::call` | gates and witnesses per pack |

Gate counts are read from each pack's `gate-court.toml`, which is the canonical source; this table
does not restate them for packs that are under active change.

## graphlaw facts carried by `wasi-json-abi-pack`

| fact | value | graph |
|---|---|---|
| module target | `wasm32-wasip1` | `ggen-graphlaw.toml`, `cargo-config.toml` |
| exports | `gl_alloc`, `gl_free`, `gl_call`; no `gl_abi_version` (`wja:hasAbiVersionExport false`) | `graphlaw-ops.ttl` |
| ops | 14, `capabilities` .. `policy`, ordered by `wja:opOrder` | `graphlaw-consumer.ttl` |
| host imports | 7 under `wasi_snapshot_preview1`: `random_get`, `environ_get`, `environ_sizes_get`, `clock_time_get`, `fd_write`, `proc_exit`, `sched_yield` | `graphlaw-ops.ttl` (`wja:WasiImport`) |
| limits | request 16,777,216 bytes; JSON depth 64; stack 16,777,216 bytes | `graphlaw-consumer.ttl` |
| error style | `refusal-kind` (`NotSemanticContent`, `Ambiguous`, `EngineRejected`, `Unsupported`, `ResourceLimit`) | `graphlaw-consumer.ttl` |
| release pins | wasm sha256 and bytes; registry and surface sha256 | `graphlaw-ops.ttl`, rendered to `generated/graphlaw/ARTIFACTS.sha256` |

The 7 imports were read from the import section of a locally built `graphlaw_wasm.wasm`; the pins
are the values in graphlaw `registry/ARTIFACTS.sha256` at the pinned SHA. A pin is a recorded
value, not a live check of any wasm file. `tests/test_wasi_json_abi_graphlaw.py` compares limits,
op names and pins against `git show <pinned SHA>:registry/...` of the graphlaw checkout.

## Gates added for the graphlaw specimen

| gate | refuses |
|---|---|
| `080_wasi_import_closure` | a `wja:WasiImport` whose module is not `wasi_snapshot_preview1`, has no module, or has no name |
| `090_artifact_pin_shape` | `wasmSha256`, `registrySha256`, `surfaceSha256` that are not 64-char lowercase hex; non-positive `wasmBytes` |

Each has a same-stem pass and fail witness under `packs/wasi-json-abi-pack/witnesses/`.

## Handwritten residue

`packs/wasi-json-abi-pack/HANDWRITTEN-graphlaw.md` lists what stays hand-written in graphlaw's
`wasm/src/lib.rs` (engine admission caps, the refusal-kind envelope, op bodies, and the module
wiring), each as `UNSUPPORTED(generator-capability)`. The outstanding-allocation accounting
(`wja:maxOutstandingBytes`, `wja:bufferStyle "vec"`, no `gl_abi_version`) is generated:
`ggen-graphlaw.toml` has an `ffi` rule and `generated/graphlaw/ffi.rs` is differentially tested
against the hand-written `lib.rs` for `wasm32-wasip1` (same exports, same `wasm_abi` results).

## Verification

```bash
python3 scripts/marketplace.py check wasi-json-abi-pack
python3 scripts/check_gate_witness_courts.py
python3 -m pytest tests/test_wasi_json_abi_graphlaw.py
# re-render the graphlaw projection in a scratch copy (ggen reads only ./ggen.toml)
cp ggen-graphlaw.toml ggen.toml && ggen sync run
```

## Standing

Marketplace boundary only: deterministic render, gate and witness courts, structural check. No
exact-SHA run of the wasm module is evidenced here, and no BEAM consumer receipt. See
[standing](standing.md) and [the explanation](../explanation/rust-wasm-beam-pipeline.md).

## See Also

- [How to represent a Rust ABI crate](../how-to/represent-a-rust-abi-crate.md)
- [GraphLaw Ash capability pack](graphlaw-ash-capability-pack.md)
- [QRI host profile](qri-host-profile.md)
