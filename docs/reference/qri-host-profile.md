# Reference: qri-host-profile

Reference for `qri:HostProfile`, the optional host-layer parameter block of a
`qri:CapabilityContract` in `qri-qualification-profile-pack`. Sources: `ontology.ttl`
(declarations), `shapes/qri.shacl.ttl` (`qri:HostProfileShape`), `gates/080_abi_family_closed.rq`,
`queries/50-54`, and `ggen-beam-host.toml`.

## Attachment

A contract points at one profile with `qri:hostProfile` (domain `qri:CapabilityContract`, range
`qri:HostProfile`, at most one per contract by shape). A contract without a profile projects
exactly as before through queries 10-40; queries 50-54 match only contracts that have one.
Every property below is optional.

```turtle
gl:contract a qri:CapabilityContract ;
    qri:abiSymbolPrefix "gl" ;
    qri:hostProfile gl:host .

gl:host a qri:HostProfile ;
    qri:outMode "packed_u64" ; qri:lenType "u32" ; qri:freeSymbol "gl_free" .
```

## Scalar properties

Format per entry: range; closed values; default when absent. "none" means the query binds an
empty string. Query 50 supplies the defaults.

ABI family (closed sets are enforced by SHACL and by gate 080):

- `qri:lenType` : string; `u32` | `usize`; default `u32`.
- `qri:outMode` : string; `packed_u64` | `out_param` | `len_prefix`; default `packed_u64`.
- `qri:errorCollapse` : string; `single_key_inspect` | `any_key_raw` | `ok_flag_refusal` |
  `flat_code` | `refusal_kind`; no default; not read by queries 50-54.
- `qri:freeSymbol` : string; open; default `<abiSymbolPrefix>_free`.
- `qri:freeArity` : integer; open; default 1 (ptr), 2 means (ptr,len); not read by 50-54.
- `qri:allocZeroPolicy` : string; open; default `refuse-resource_limit`.
- `qri:reqConsumed` : boolean; guest frees the request buffer itself; default `true`.
- `qri:outLenWidth` : integer; open; none; not read by 50-54.
- `qri:ptrMask` : string; hex mask such as `0xFFFFFFFF`; none; not read by 50-54.
- `qri:errorEnvelope` : string; open; none; not read by 50-54.
- `qri:requestCap` : integer; request size cap in bytes; default 0.

Artifact location and pin:

- `qri:pathEnv` : string; env var naming the wasm path; none.
- `qri:manifestRel` : string; manifest path relative to the app; none.
- `qri:wasmRel` : string; wasm path relative to the app; none.
- `qri:manifestSchema` : string; manifest schema id; none.
- `qri:pinFormat` : string; open (example `sha256-hex`); none.

Naming of generated Elixir modules:

- `qri:otpApp` : string; none.
- `qri:moduleRoot` : string; none.
- `qri:taskModuleRoot` : string; none.
- `qri:handleNoun` : string; default `engine`.
- `qri:taxonomyNamespace` : string; none.
- `qri:refusalModule` : string; none.
- `qri:telemetryRoot` : string; none.
- `qri:engineId` : string; none.

Envelope keys and probe:

- `qri:okKey` : string; default `ok`.
- `qri:opKey` : string; default `op`.
- `qri:probeOp` : string; none.
- `qri:probeExpectKey` : string; none.
- `qri:initExport` : string; export called at init; surfaced by query 53 as kind `init`.

Pool and timeouts:

- `qri:poolStrategy` : string; open; default `single`.
- `qri:poolSize` : integer; default 1.
- `qri:poolSizeSource` : string; computed size such as `schedulers_online`; wins over
  `qri:poolSize`; none.
- `qri:timeoutCheapMs` : integer; none; not read by 50-54.
- `qri:timeoutHeavyMs` : integer; none; not read by 50-54.

## Multi-valued properties

- `qri:recycleOn` : string, repeatable; refusal or trap codes after which the instance is
  recycled. Read by query 54 (`prefix`, `code`, `order`). Emission order comes from optional
  `qri:recycleRule` nodes (`qri:RecycleRule` with `qri:recycleCode`, `qri:recycleOrder` integer);
  unranked codes follow, ordered by code. Gate `100` refuses a rule naming a code not in `recycleOn`.
- `qri:hostLimit` : `qri:HostLimit`, repeatable. Each limit carries `qri:limitName` (string),
  `qri:limitDefault` (integer) and `qri:limitOrder` (integer), plus optional `qri:limitZeroOk`
  (boolean, default false: 0 is a real bound; `wasm_config.ex` then resolves it with
  `&1 >= min_limit(key)` and lists the key in `@zero_ok`) and `qri:limitZeroMeaning` (string,
  required by gate `090` when `limitZeroOk` is true). Read by query 51
  (`prefix`, `name`, `default`, `order`, `zero_ok`, `zero_meaning`), ordered by `limitOrder` then
  `limitName`.
- `qri:docExampleOp` : string on the profile; operation shown in the `Host.request/3` `@doc`
  example (`%{"op" => "law", ...}`); default elided (`%{"op" => ...}`). Read by query 50
  (`doc_example_op`).

## Contract-level companions

Read together with the profile by queries 52 and 53, but declared on the contract:

- `qri:wasiImport` -> `qri:WasiImport` with `qri:importName`, `qri:importParams`,
  `qri:importResults` (comma-separated value types). Query 52; params and results default to
  empty.
- `qri:requiredExport` and `qri:optionalExport` : strings. Query 53 emits kind `required` or
  `optional`; `qri:initExport` emits kind `init`.

## Queries

- `queries/50-profile.rq` : one row per profile with every scalar, defaults applied above.
- `queries/51-limits.rq` : `prefix`, `name`, `default`, `order`, `zero_ok`, `zero_meaning`.
- `queries/52-imports.rq` : `prefix`, `name`, `params`, `results`.
- `queries/53-exports.rq` : `prefix`, `name`, `kind`.
- `queries/54-recycle.rq` : `prefix`, `code`, `order`.

All five order by `?prefix` first, so output is deterministic.

## Admission

- SHACL `qri:HostProfileShape` enforces datatypes, `maxCount 1` on scalars, and the closed sets
  for `lenType`, `outMode`, `errorCollapse`.
- Gates `090_zero_ok_declares_meaning` and `100_recycle_rule_names_declared_code` refuse a
  zero-ok limit without declared zero semantics and an orphan recycle order row.
- Gate `080_abi_family_closed` returns a row with verdict `UNSUPPORTED` for an `outMode`,
  `errorCollapse` or `lenType` value outside its closed set.

## Usage in ggen-beam-host.toml

`ggen` reads only `./ggen.toml`, so a consumer copies `ggen-beam-host.toml` to `ggen.toml` in a
scratch copy of the pack and runs `ggen sync run`.

```toml
[project]
name = "qri-beam-host"

[ontology]
source = "ontology.ttl"
imports = ["ontology/examples/ash-graphlaw-contract.ttl"]

[templates]
dir = "templates/beam-host"
```

Templates under `templates/beam-host` (`abi`, `engine_load`, `host`, `pool`, `vendor_task`,
`verify_task`, `wasm_config`) embed queries 50-54 verbatim and render one hand-written
`ash_graphlaw` module each. The default `ggen.toml` does not import a host-profile contract.

## Standing

Marketplace boundary only. A host profile is a parameter block for generated BEAM host source; it
carries no authority and a profile's existence is not evidence that a host loads a module. See
[standing](standing.md).

## Verification

```bash
python3 -m pytest packs/qri-qualification-profile-pack/tests -q
python3 scripts/check_gate_witness_courts.py
```

## See Also

- [QRI qualification profile](qri-profile.md)
- [Why QRI is a thin waist](../explanation/qri-thin-waist.md)
- [Qualify a realization](../how-to/qualify-a-realization.md)
- [First QRI substitution](../tutorials/qri-first-substitution.md)
- Pack sources: `packs/qri-qualification-profile-pack/README.md`, `ontology.ttl`,
  `shapes/qri.shacl.ttl`, `ontology/examples/ash-graphlaw-contract.ttl`
