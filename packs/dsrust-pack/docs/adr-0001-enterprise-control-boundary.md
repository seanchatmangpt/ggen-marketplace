# ADR-0001: Keep DsRust generation and enterprise runtime authority separate

- **Status:** Accepted for `dsrust-pack` 0.2
- **Decision owner:** Marketplace architecture
- **Scope:** `packs/dsrust-pack`
- **Source authority:** `seanchatmangpt/dsrust@f24adde08c1d8850e4d7079d019643bb40f905cb`

## Context

A DSPy-style generator can easily become an accidental control plane: ontology selects a model,
templates emit tool integrations, and generated applications obtain credentials and deployment
authority. At enterprise scale that would mix design authority, code manufacture, security
configuration, and production actuation in one component.

The marketplace already has a dedicated Fortune-5 architecture vocabulary. Duplicating it inside
DsRust would create two competing control models and guaranteed drift.

## Decision

`dsrust-pack` remains a construction-plane pack. It exposes an **optional enterprise binding adapter**
that points to an externally governed architecture asset and validates only the boundary facts this
pack can truthfully own:

- exact DsRust source identity;
- compatibility policy;
- construction-only authority;
- consumer ownership of runtime controls and data;
- receipt-gated promotion;
- pinned-source rollback;
- explicit compiler/runtime qualification standing;
- canonical enterprise architecture vocabulary reference.

The pack does **not** claim or configure enterprise identity, KMS, network, observability, SLO,
capacity, replication, data residency, or deployment policy. Those attach to the consuming runtime
asset through the enterprise architecture program.

## Consequences

Positive:

- separation of duties is mechanically visible;
- one Fortune-5 control vocabulary remains authoritative;
- portable DsRust users are not forced into enterprise policy;
- enterprise consumers receive a generated control matrix;
- unsupported or unproven standing remains explicit instead of being promoted by documentation.

Trade-off:

- `dsrust-pack` ALIVE does not mean a production runtime is ALIVE;
- consumers must add compiler/test/security/runtime receipts before actuation.

This is intentional. Conflating construction proof with runtime proof would be a stronger claim than
the available evidence supports.
