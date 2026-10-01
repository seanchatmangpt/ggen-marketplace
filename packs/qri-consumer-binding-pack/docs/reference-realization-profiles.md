# Reference realization profiles

Non-normative. SRFC-001 is technology-independent; the technology named here lives only in this
pack. A profile is selected by `qcb:profileId` on the binding's `qcb:RealizationProfile`
(admitted set: gate 140). Authority ceiling NONE in every profile: the pin is identity, never
authorization.

## Projection types (`qcb:requestedProjection`, closed set, gate 150)

| value | emitted (under `generated/`) |
|---|---|
| `host` | `beam-wasmex`: `beam-host/*.ex` and `MANIFEST.json`; `node-wasi`: `node-wasi/host.mjs` |
| `op-names` | `contract.json` (operation names only; typed fields are UNSUPPORTED(projection)) |
| `tests` | `tests/authority_boundary_test.exs` (beam-wasmex) or `node-wasi/authority-boundary.test.mjs` (node-wasi) |
| always | `artifact-pin.json`, `projection-receipt.json` |

## beam-wasmex

Reuses the `qri-qualification-profile-pack` beam-host templates through the `[packs]` path
dependency in `ggen.toml`; the contract's `qri:hostProfile` carries the host knobs. The seven
rendered host files and `MANIFEST.json` equal the committed `ash_affidavit` files byte for byte.

## node-wasi

`ggen-node-wasi.toml` (no `[packs]`). The generated host uses `node:fs`, `node:crypto` and
`node:wasi` only: it verifies size and sha256 against the pin before compiling, refuses imports
outside the contract's `qri:allowedImport` set, checks required exports and the ABI version, and
returns typed refusals (`wasm_digest_mismatch`, `wasm_invalid`, `abi_failure`, ...).
`node host.mjs --check <wasm>` exits 0 on a pinned module and 3 with a typed JSON refusal otherwise.

## Consuming

    python3.11 runners/consume.py --binding qualification/consumer.ttl --out <dir>

Gates run first; any row prints a typed refusal (`code`, `class`, `broken_term`, `gate`) and writes
nothing. Otherwise ggen runs twice in a scratch capsule (the second pass renders the receipt from the
digests of the first), the passes are compared, and `generated/`-relative files are written to `<dir>`.

## Committed generated trees

`generated/` is the projection of `qualification/consumer.ttl` (profile `beam-wasmex`, the Elixir host
in `ash_affidavit`). `generated/profiles/node-wasi/` is the projection of
`qualification/consumer-node-wasi.ttl` (profile `node-wasi`). Each is reproduced by one
`consume.py --binding <binding> --out <dir>` run and compared byte for byte with the committed tree by
`test_c8_generated_tree_in_pack_equals_fresh_consume` (beam-wasmex) and
`test_c8_node_wasi_generated_tree_equals_fresh_consume` (node-wasi). Both trees carry their own
`projection-receipt.json`, whose `pack_content_digest` changes whenever a pack source changes, so a source
edit without regeneration fails both courts.

## Refusal transport and detail shape

`consume.py` prints one JSON object on stdout. REFUSED and UNSUPPORTED are separable at the transport
without reading the code: top-level key `refused` with exit status 2, or top-level key `unsupported` with
exit status 7 (UNSUPPORTED is not REFUSED; SRFC-001 R40). Both objects also carry `also`, the sorted list of
other `gate:code` rows that fired. The detail record has the same keys for both:
`broken_term`, `class`, `code`, `gate`, `standing_literal`. Runner-side codes add keys:
`CONTRACT_DIGEST_MISMATCH` adds `declared` and `computed`; `SHAPE_NONCONFORMANT` adds `violations`
(sorted `component`/`focus`/`path` records); their `gate` is `consume` and `shacl`. A refusal at any of
these steps leaves `--out` untouched. Detail shape parity between hosts: both generated hosts refuse with a `Refusal` carrying a stable `code`,
a `class` placed by one closed code-to-class table, a message and a detail map (node-wasi: a `Refusal` error
class, `host.mjs`; beam-wasmex: `{:error, %Refusal{}}`); `node host.mjs --check` prints the same fields as
JSON with `authority: "NONE"`. These host-layer codes are a closed set distinct from the generation-time
vocabulary of `qcb:generation-refusals`; a host code outside its table is `unsupported`, never refused, and
neither set is reported under the other's name. Exit status 3 (unparseable binding, pyshacl missing) is a structural error, not a typed refusal.

## Pin records

| record | schema id | owner | role |
|---|---|---|---|
| producer pin | `affidavit.wasm-pin/1` | affidavit (`affidavit-wasm/registry/artifact-pin.json`) | identity of one built module plus build, ops, imports, exports |
| consumer pin | `qcb.artifact-pin/1` | this pack (`generated/artifact-pin.json`) | the binding's `qcb:ArtifactPin` rendered as a record |

Mapping producer record to ConsumerBinding pin: `sha256` to `qcb:checksum` (`spdx:Checksum`,
`spdx:checksumAlgorithm_sha256`, `spdx:checksumValue`); `bytes` to `dcat:byteSize`; `registry_sha256` to
`qcb:registrySha256`; `abi_version` to `qcb:abiVersion`. Producer-only fields (`build`, `ops`, `imports`,
`exports`, `crate`, `name`) are not part of the consumer pin. The consumer states the pin; the court
`test_producer_and_consumer_pin_records_have_distinct_schema_ids` observes that the two schema ids differ
and that the four mapped values agree.

## Relation to affidavit-consumer-pack

`affidavit-consumer-pack` generates its own TypeScript and Python hosts from `wja:` facts; this
pack's node-wasi host adds the pin, ceiling, import-surface and closed-refusal semantics from the
binding. The packs are siblings, not successor and predecessor. See
`relation-to-affidavit-consumer-pack.md` for the composition probe and court C10.
