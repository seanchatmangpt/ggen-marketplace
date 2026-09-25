# HANDWRITTEN.md — provider-extinction-contract-pack

The pack IS the authored surface (法面): every file below is hand-authored RDF
or hand-authored gate SPARQL, manufactured once, so consumers never hand-write
a provider-neutral execution contract again. No generated files ship; nothing
here is a projection of another source, so there is no reconciliation manifest.

| path | what | why hand-authored (once) | date |
|---|---|---|---|
| pack.toml | pack admission record + explicit NOT-claimed authority boundary | pack authorship is the marketplace's lawful write surface | 2026-09-25 |
| ontology.ttl | ExecutionRequest/ExecutionProvider/ExecutionReceipt contract classes (prov-anchored), 12-field receipt vocabulary, routing facts (providerId/enabled), extinction invariant, dogfood request/provider/receipt triple for ALOOP-ZCODE-DOGFOOD-001 lane 5 | one-time ontology authorship; `pec:` minted only after the failed-edge record against prov / OCEL 2.0 / dcterms / oslc_cm (recorded in-file) | 2026-09-25 |
| gates/010_no_provider_identity_in_workorder.rq | violation-row gate: provider names are unlawful in WorkOrder/AuthorityGrant/AcceptanceCriterion semantic literals (title/description); minted identifiers exempt (recorded failed edge in the gate header) | gate authorship is pack authorship; fires via FM-PACK-013 in consumers | 2026-09-25 |
| gates/020_routing_totality.rq | violation-row gate: every executable capability resolves to >= 1 enabled provider (capabilityId left-segment join) | same | 2026-09-25 |
| gates/030_receipt_shape.rq | violation-row gate: ExecutionReceipt carries all 12 contract fields | same | 2026-09-25 |
| qualification/fixtures/pos_consumer_clean.ttl | conforming consumer graph (consumer namespace) — all gates 0 rows | anti-vacuity positive half | 2026-09-25 |
| qualification/fixtures/neg_provider_in_workorder.ttl | provider-name leak in identity + acceptance — gate 010 fires | anti-vacuity negative half (mutating input must be refused) | 2026-09-25 |
| qualification/fixtures/neg_unroutable_capability.ttl | disabled-provider capability + segment-less capabilityId — gate 020 fires | same | 2026-09-25 |
| qualification/fixtures/neg_incomplete_receipt.ttl | receipt missing 3 contract fields — gate 030 fires 3 rows | same | 2026-09-25 |
| templates/provider_contract_summary.json.tmpl | projects provider routing table + all three gate verdicts to generated/provider_contract_summary.json in a consumer sync | pack ships >= 1 template (FM-PACK-005, witnessed by real ggen sync); the render is the consumer-facing projection of the gates | 2026-09-25 |

Ledger position: zero 産面 bytes. No consumer repo was touched by authoring
this pack. The dogfood individuals name episode ALOOP-ZCODE-DOGFOOD-001 as
data, not as authority. NOT claimed (see pack.toml): actuation authority,
provider selection policy, cancellation execution, provider-specific payload
validation.
