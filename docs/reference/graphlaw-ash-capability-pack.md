# Reference: graphlaw-ash-capability-pack

`graphlaw-ash-capability-pack` projects a typed Elixir capability surface (behaviour, registry,
per-operation modules, API, lossless result structs, reference docs, pure surface test) from the
GraphLaw capability registry, schema `graphlaw.capability-registry/1`. The pack exposes what
GraphLaw already supports; it does not implement RDF, SPARQL, SHACL, ShEx, N3, Datalog,
entailment or planning semantics.

## Standing

`UNKNOWN` at the exact-SHA `ash_graphlaw` consumer boundary; `PARTIAL_ALIVE` at most at the
marketplace boundary. The gates and witnesses below establish structural admission of the
registry vocabulary. They do not execute any GraphLaw operation, and no consumer receipt exists,
so nothing here is `ALIVE`. See [standing](standing.md).

## Vocabulary

Namespace `gac: <http://seanchatmangpt.github.io/packs/graphlaw-ash-capability#>`. Registry
individuals use IRIs under `https://graphlaw.dev/registry#` and are supplied by the consumer, never
by the pack ontology. Classes checked by the gates: `gac:Registry`, `gac:Capability`,
`gac:ResponseVariant`, `gac:CapabilityField`, `gac:Dialect`, `gac:LawStep`, `gac:OpBinding`, and since 26.9.30 `gac:Model`, `gac:ModelField`,
`gac:ModelEnum`, `gac:ModelEnumValue` and the `gac:Limit` metadata (`gac:limitScope`,
`gac:limitUnit`, `gac:limitSource`, `gac:limitCount`).

## Gates

Each gate is a violation-row SPARQL SELECT under `packs/graphlaw-ash-capability-pack/gates/`
with a `# MESSAGE:` header and `ORDER BY`; zero rows admit, any row refuses. No gate hardcodes the
operation count: the expected count is read from `gac:opCount`.

| gate | contract |
|---|---|
| `010_registry_identity` | registry exists; schemaId exact; abiVersion integer >= 1; surfaceSha256 and registrySha256 match `^sha256:[0-9a-f]{64}$` |
| `020_op_count_contract` | opCount and dialectCount are integers equal to the counted capabilities and dialects; back-references resolve |
| `030_op_order_contract` | opOrder unique, integer, within 1..n (contiguous); opName unique |
| `040_field_type_vocabulary` | fieldType is in the closed 14-type vocabulary |
| `050_response_variant_contract` | every op has at least one variant, every variant at least one response field; tag and tag field consistent; tagged ops have at least two variants |
| `060_field_order_contract` | fields carry the required properties; side is closed; owner class matches side; order and name unique per owner and side |
| `070_opbinding_reference_contract` | every binding names a real op, at most one binding per op, typed legacy flag |
| `080_dialect_kind_contract` | dialect kind is `rdf` or `other`; orders unique; rdf dialects order before other dialects |
| `090_law_step_ceiling_contract` | law step ceiling is `observe`, `select`, `construct`, or absent |
| `100_elixir_name_contract` | op and field names match `^[a-z][a-z0-9_]*$`; no response field named `raw` |
| `110_model_identity_contract` | every `gac:Model` has modelName (UpperCamelCase), integer modelOrder >= 1, dotted-UpperCamelCase modelElixirModule and non-empty modelRustPath; all unique |
| `120_model_field_contract` | model fields carry owner, snake_case name (never `extra`), order, type, required, nullable and doc; type is in the closed vocabulary or `model:<Name>`, `list<model:<Name>>`, `enum:<Name>`; order and name unique per model |
| `130_model_reference_closure_contract` | modelFieldOf names a model; `model:`/`list<model:` types name an existing model; `enum:` types name an existing `gac:ModelEnum`; enum values point at an enum |
| `140_model_enum_contract` | every enum has a name, order and at least one value; values carry non-empty text and an order; order and text unique per enum |
| `150_lease_receipt_required_fields_contract` | only when any `gac:Model` exists: Lease, SignedLease, Receipt and Attestation exist with their required fields at the declared type and required flag |
| `160_limit_scope_contract` | limit names are snake_case; a limit that declares scope, unit or source declares all three, scope is `abi`/`hooks`/`n3`/`plan`/`wasm`, unit is `bytes`/`count`/`steps`/`firings`/`rounds`/`quads`; bare legacy limits stay clean |
| `170_limit_completeness_contract` | only when a registry declares `gac:limitCount`: it equals the number of `gac:Limit` individuals; every limit has a name and a non-negative integer value; names unique |
| `180_coverage_complete` | every op and native module has exactly one coverage row: GENERATED with artifact or UNSUPPORTED(generator-capability) with reason and note |

## Typed models

Declared by the registry (`models`, `model_enums`) and projected under `AshGraphLaw.Model`. Each
struct has one key per field plus `:extra`, so unknown wire keys survive a `from_map/1` /
`to_map/1` round trip; nested models decode through their own module. Enum lists are informational.

| model | Elixir module | engine type |
|---|---|---|
| `Lease` | `AshGraphLaw.Model.Lease` | `graphlaw::law::Lease` |
| `SignedLease` | `AshGraphLaw.Model.SignedLease` | `graphlaw::law::SignedLease` |
| `Receipt` | `AshGraphLaw.Model.Receipt` | `graphlaw::law::Receipt` |
| `Attestation` | `AshGraphLaw.Model.Attestation` | `graphlaw::attest::Attestation` |
| `Plan` | `AshGraphLaw.Model.Plan` | `graphlaw::plan::Plan` |
| `Action` | `AshGraphLaw.Model.Action` | `graphlaw::plan::Action` |
| `PolicyEntry` | `AshGraphLaw.Model.PolicyEntry` | `graphlaw::policy::Entry` |
| `PolicyOutcome` | `AshGraphLaw.Model.PolicyOutcome` | `graphlaw::policy::Outcome` |

Enums (`AshGraphLaw.Model.Enums`): `Ceiling`, `LeaseReason`, `ReceiptReason`, `PolicyRefusalKind`.

## Limit scopes

`AshGraphLaw.Capability.Limits` carries every limit with its scope, unit and enforcing source.

| scope | limits |
|---|---|
| `abi` | `max_atoms_per_field`, `max_json_depth`, `max_plan_actions`, `max_policy_entries`, `max_request_bytes` |
| `hooks` | `hooks_max_firings`, `hooks_max_rounds`, `hooks_max_state_quads` |
| `n3` | `n3_max_derived_facts`, `n3_max_iterations`, `n3_max_match_steps`, `n3_max_term_bytes`, `n3_max_total_bytes` |
| `plan` | `max_plan_total_atoms` |
| `wasm` | `max_outstanding_alloc_bytes` |

## UNSUPPORTED(generator-capability)

These GraphLaw behaviors have no generator in the pack and are ledgered, not generated:

- signature verification (`attest.rs` Ed25519 verification of attestations)
- lease authorize (`SignedLease::authorize`, clock and skew checks)
- plan admit (`plan.rs` admission of a candidate plan against the engine)
- policy validation (`policy.rs` FOND policy validation)
- hook execution (`hooks.rs` knowledge-hook firing)

## Witnesses

`witnesses/pass/<stem>.ttl` and `witnesses/fail/<stem>.ttl` exist for every gate stem (exact-stem
pairing, enforced by `scripts/check_gate_witness_courts.py` through `gate-court.toml`). The pass
witnesses are small self-consistent registries (two operations, one tagged; 110-170 also carry the typed models, enums and 15 scoped limits). Each fail witness is
the pass registry with one deliberate defect and trips exactly its own gate.

## Verification

```bash
python3 -m pytest tests/test_graphlaw_ash_capability_pack.py -q
python3 scripts/check_gate_witness_courts.py
python3 scripts/standing.py --check
python3 scripts/pack_capabilities.py --check
```

## See Also

- [standing](standing.md)
- [pack-catalog](pack-catalog.md)
- [pack-capabilities](pack-capabilities.md)
