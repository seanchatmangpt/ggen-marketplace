# QRI qualification profile reference

Exact contract of `packs/qri-qualification-profile-pack` (namespace
`https://seanchatmangpt.github.io/packs/qri-qualification-profile-pack#`, prefix `qri:`).
Authority ceiling: NONE. Nothing here grants DO.

## Classes

| Class | Grounding | Role |
|---|---|---|
| `qri:Capability` | `skos:closeMatch sosa:Procedure` | stable capability identity |
| `qri:CapabilityContract` | `prov:Entity` | versioned, content-addressed contract |
| `qri:Realization` | `skos:closeMatch ssn:System` | an implementation that may fill the slot |
| `qri:RuntimeContext` | `prov:Entity` | host + authority policy + resource envelope |
| `qri:Invariant`, `qri:InvariantSet` | `prov:Entity` | executable boundary; kinds are a closed set |
| `qri:Qualification` / `QualificationReceipt` | `prov:Activity` / `prov:Entity` | evidence-producing transition |
| `qri:Admission`, `Execution`, `Replay` (+ receipts) | PROV | separate transitions, never merged |
| `qri:SubstitutionClaim` | `prov:Entity` | reified interchangeability over two receipts |
| `qri:SelectionPolicy` | `prov:Plan` | utility ordering over already-qualified candidates |

## Relations with a fixed domain

- `qri:qualifiesFor`, `qri:preservesInvariant`, `qri:qualificationResult`: domain
  `qri:QualificationReceipt` only, never `qri:Realization`.
- `qri:interchangeableUnder`: domain `qri:SubstitutionClaim`, range `qri:RuntimeContext`.
- There is no mutable `status`. `qri:derivedStanding` is an index regenerated from receipts.

## Gates (a returned row refuses)

| Gate | Refuses |
|---|---|
| `010_qualified_substitution` | claim whose receipts are not both Passed for one contract and the claimed context |
| `020_no_mutable_standing` | `qri:status` / `standing` / `qualified` / `admitted` flags |
| `030_authority_not_from_capability` | realization or receipt carrying `odrl:permission` or `qri:grantsAuthority` |
| `040_ambiguous_projection_unsupported` | field with no admitted wire type (`UNSUPPORTED`, never guessed) |
| `050_import_subset` | actual WASM import outside the contract's `qri:allowedImport` |
| `060_invariant_complete` | Passed receipt missing a required invariant |
| `070_typed_import_matches_allowed` | typed `qri:wasiImport` with no matching `qri:allowedImport` string |
| `080_abi_family_closed` | host profile selecting an ABI family outside the closed sets (`UNSUPPORTED(abi-family)`) |
| `090_zero_ok_declares_meaning` | `qri:limitZeroOk true` limit with no non-empty `qri:limitZeroMeaning` |
| `100_recycle_rule_names_declared_code` | `qri:recycleRule` ordering a code absent from the same profile's `qri:recycleOn` |

Every gate has same-stem `witnesses/pass` and `witnesses/fail` files; the fail witness must
produce at least one row.

## Projection (ggen, one rule per artifact)

| Output | Source query | Notes |
|---|---|---|
| `wit/refusal.wit`, `wit/capability.wit` | `40-refusals.rq`, `10-operations.rq` | WIT is the ABI ledger, not the semantic source |
| `abi.json` | `20-abi.rq` | symbols, allowed imports, required exports |
| `adapter/src/lib.rs`, `adapter/Cargo.toml` | `10-operations.rq` | `<prefix>_alloc/_free/_call`; domain logic stays hand-written |
| `beam/qri_host.ex` | `20-abi.rq` | wasmex host: digest pin, import/export admission, typed outcomes |

Outcomes are typed and never collapsed: `{:refused, code, detail}`, `{:trap, reason}`,
`{:unsupported, reason}`.

## Identity

`qualification/rdfc.py` hashes canonical N-Quads (URDNA2015, the algorithm standardized as
RDFC-1.0). Raw Turtle or JSON-LD text is never hashed.

## Standing boundary

The pack's reference court qualifies a native binary and a wasm32-wasip1 module hosted by the
generated wasmex host. The Component Model profile is emitted as WIT only; no component host is
exercised, so that profile is `PARTIAL_ALIVE`. SOSA 2023 alignment is a separate,
non-imported file because the 2023 edition is a Working Draft. This is not a Level-5 claim.

## See Also

[QRI thin waist](../explanation/qri-thin-waist.md) ·
[Qualify a realization](../how-to/qualify-a-realization.md) ·
[First QRI substitution](../tutorials/qri-first-substitution.md)
