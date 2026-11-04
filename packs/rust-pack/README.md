# rust-pack

Canonical RDF graph for ontology-driven Rust systems manufacturing: multi-crate
Cargo workspaces, `#![no_std]` + `alloc` kernels, RFC 430 naming discipline,
UCG safety proofs, 64-byte aligned SIMD buffer slots, unwind-guarded C ABI
shells. Generated consequences are projections of THIS graph — change the
graph, re-run `ggen sync`, never hand-edit generated output.

Authority: [docs/PRD.md](docs/PRD.md) (product) and
[docs/ARD.md](docs/ARD.md) (architecture); conventions follow the exemplar
[../avec-pack](../avec-pack). Pack namespace IRI:
`https://seanchatmangpt.github.io/packs/rust-pack#`; vocabulary prefix
`rust: <urn:ggen:rust:#>` (ARD.md:7).

## Layout

| path | content |
|---|---|
| `ontology.ttl` | the canonical graph — `urn:ggen:rust:#` vocabulary + pack namespace |
| `gates/010…050_*.rq` | 5 violation-row SELECTs, `ORDER BY`-deterministic |
| `witnesses/{pass,fail}/` | exact-stem witness pairs per gate — pass silent, fail fires |
| `gate-court.toml` | court config (`ggen.semantic-gate-witness-court/1`, exact-stem keys) |
| `templates/*.tmpl` | 5 Tera templates with disjoint output targets |
| `qualification/` | consumer specimen + receipt validator |
| `docs/PRD.md`, `docs/ARD.md` | product/architecture authority (unchanged this wave) |

## What the graph models

- **Workspaces and crates** — `rust:Workspace` with `rust:workspaceDependency`
  members, `rust:resolverVersion "2"`, edition 2021 default / 2024 permitted;
  `rust:Crate` individuals with `crateType`, `isNoStd`, `hasAlloc`, MSRV taken
  from the graph (`rust:msrv`), never hardcoded.
- **Item tree with RFC 430 naming** — `rust:Struct`/`rust:Enum` (UpperCamelCase)
  and `rust:Function`/`rust:Module` (snake_case), each carrying `rust:itemName`
  and linked to its owning crate via `rust:defines` (R1/R8 of RESOLUTIONS.md).
- **UCG safety proofs** — `rust:Function` `isUnsafe=true` must carry a
  non-empty `rust:safetyProof`; the fail-witness mutation drops it.
- **64-byte alignment invariant (avec parity)** — `rust:BufferSlot` with
  `rust:simdProfile` ("Arrow" / "SIMD" / "None") and `rust:byteAlignment`;
  non-None profiles must align at exactly 64 bytes (ARD §2.2).
- **Unwind-safe C ABI** — `rust:FfiExport` individuals with `rust:symbolName`
  and `rust:unwindProtection`; an `extern "C"` export without an unwind guard
  is refused.
- **Workspace inheritance discipline** — `rust:Crate rust:dependsOn
  rust:Dependency`; a dependency that is also a `rust:workspaceDependency`
  member must not carry a crate-local `rust:versionLiteral` (PRD.md:58-60).
- **Promises** — `p:Subject`/`p:Promise` court-facing individuals with
  `p:backedBy` edges, matching the house convention.

## Gates

Refusal gates 010–050; each has a pass witness (zero rows) and a fail witness
(≥1 row) at the exact stem.

| gate | refuses when |
|---|---|
| `010_api_naming` | an item's `itemName` violates RFC 430 naming for its class |
| `020_unsafe_safety_proof` | a `Function` has `isUnsafe=true` without `safetyProof` |
| `030_alignment_invariant` | a `BufferSlot` has `simdProfile != "None"` and `byteAlignment != 64` |
| `040_ffi_unwind_guard` | an `FfiExport` lacks `unwindProtection` |
| `050_workspace_inheritance` | a `dependsOn` target is a workspace dependency and the edge carries `versionLiteral` |

## Projections

| template | generated target |
|---|---|
| `templates/workspace_cargo_toml.tmpl` | `Cargo.toml` — resolver "2", workspace dependencies, member fan-out |
| `templates/crate_cargo_toml.tmpl` | `crates/<crate>/Cargo.toml` — edition, msrv from graph, no_std/alloc features |
| `templates/lib_rs.tmpl` | `crates/<crate>/src/lib.rs` — `#![no_std]` shell, `forbid(unsafe_code)`, module tree |
| `templates/c_abi_h.tmpl` | `inc/<crate>.h` — FfiExport projections to the workspace root |
| `templates/crate_court_test.tmpl` | `crates/<crate>/tests/<crate>_court.rs` — hand-transcribed + SPARQL-derived proof pair |

## Consumers

Pin the pack by path in your project's `ggen.toml`:

```toml
[packs]
rust-pack = { path = "../ggen-marketplace/packs/rust-pack" }
```

Replay (verify ladder §5 of RESOLUTIONS.md): `ggen sync run` twice in a
consumer project — sha256-identical generated tree, second run
`"written": []`.

## Standing

`UNKNOWN` as of 2026-10-30 (this wave is mid-flight): gates/, witnesses/,
ontology.ttl, and qualification/ land in concurrent lanes L6–L9; the manifest
files (this README, `pack.toml`, `gate-court.toml`) are authored. Standing
flips on the §5 verify ladder:

```text
$ python3 scripts/check_gate_witness_courts.py --packs packs   # rust-pack row
$ python3 scripts/marketplace.py check rust-pack               # exit 0
```

Baseline (pre-existing, not this wave's regression):
`REFUSED:ONTOLOGY_SOURCE_MISSING:rust-pack` until ontology.ttl lands.

## Evidence boundary

Marketplace admission + the exact-stem witness court + consumer replay only.
The pack never executes cargo; Miri and the compiled-layer Rust ladder are
consumer-side stages (`ACCEPTED-WARN:miri-nightly-consumer-side`,
`ACCEPTED-WARN:untestable-prose-requirement` rows in `qualification.toml`).
Grants no execution authority; BRCE remains the sole actuation boundary.

## See Also

- [Pack contract](../../docs/reference/pack-contract.md)
- [Pack classes](../../docs/reference/pack-classes.md)
- [avec-pack exemplar](../avec-pack/README.md)
- [RESOLUTIONS.md](RESOLUTIONS.md) — this wave's resolved contract
