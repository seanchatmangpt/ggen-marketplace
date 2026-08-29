# GCP Exact Conformance Pack

This pack is the ggen manufacturing projection for GymAct's GCP differential-conformance work. It does **not** implement a second GCP simulator and it does not assert that GCP is exact by construction.

## Contract

The admitted source families are represented as public semantic facts: Google Discovery REST documents, canonical `googleapis` proto/RPC definitions, Service Config, Cloud Asset Inventory, Audit Logs, IAM/policy behavior, quota/limit behavior, long-running-operation semantics, published human documentation, and receipted empirical observations.

GymAct owns runtime observation and paired real-GCP/simulator execution. This pack owns static manufacture from the admitted RDF graph and fail-closed graph gates. A consumer may publish a `dqv:QualityMeasurement` for `gcp:exactness-metric` only from differential evidence; the pack refuses a true exactness assertion without at least two distinct provenance sources.

## DfCM boundary

`SELECT` explores and queries the semantic graph. `CONSTRUCT` manufactures deterministic projections such as `src/gcp_contract_sources.rs`. This pack has no `DO` authority. Real GCP actuation stays behind GymAct/BRCE and produces receipts before exactness can advance.

The static source catalog deliberately preserves all ten required source families instead of collapsing them into a hand-written service list. A missing source family is topology loss and fails `010_contract_sources_complete.rq`.

## Gates

- `010_contract_sources_complete.rq` refuses deletion of any admitted contract-source family.
- `020_exactness_receipted.rq` refuses a true exactness measurement without paired provenance.
- `030_public_ontology_only.rq` refuses pack-owned OWL/RDFS classes or RDF/OWL properties; pack URNs are ABox identities only.

## Standing

The pack itself can qualify as a deterministic manufacturing projection without claiming live GCP equivalence. GCP standing remains `PARTIAL_ALIVE` until every admitted external contract unit has paired real/simulator execution evidence and the differential verifier reports no mismatch, gap, duplicate, refusal, block, unsupported unit, or unreceipted `ALIVE` claim.
