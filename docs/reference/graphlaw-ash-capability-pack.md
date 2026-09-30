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
`gac:ResponseVariant`, `gac:CapabilityField`, `gac:Dialect`, `gac:LawStep`, `gac:OpBinding`.

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

## Witnesses

`witnesses/pass/<stem>.ttl` and `witnesses/fail/<stem>.ttl` exist for every gate stem (exact-stem
pairing, enforced by `scripts/check_gate_witness_courts.py` through `gate-court.toml`). The pass
witnesses are small self-consistent registries (two operations, one tagged). Each fail witness is
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
