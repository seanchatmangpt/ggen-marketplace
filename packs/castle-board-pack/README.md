# castle-board-pack

`castle-board-pack` is the DfCM-derived Fortune-5 board admission extension for CASTLE.

It does **not** replace `castle-pack`. The base pack remains the stable 40-control Fortune-5 readiness profile. This pack contributes 49 stricter board controls and 10 prohibited board-failure goals. A board admission therefore requires:

```text
Base40(subject)
AND Board49(subject)
AND Base40(CASTLE)
AND Board49(CASTLE)
AND independent assurance
```

## DfCM derivation

The board profile starts from prohibited outcomes and derives the controls required to make each outcome inadmissible:

- `BoardEvidenceForgery` → signature, payload, parent-DAG, trust-root, revocation, and orphan checks.
- `BoardCastleSelfExemption` → CASTLE self-governance and independent verification.
- `BoardRootOfTrustCompromise` → key inventory, revocation, rollover, containment, signed privileged transitions, and crypto agility.
- `BoardCastleAvailabilityFailure` → explicit failure semantics, zero unreceipted degraded DO, partition testing, local capability verification, and causal recovery receipts.
- `BoardRiskPolicyDrift` → risk-appetite/policy traceability, control ownership, and bounded exceptions.
- `BoardMaterialityMiss` → deterministic classification, escalation, clocks, and receipted materiality decisions.
- `BoardAssuranceCapture` → independent design/effectiveness testing and evidence reproducibility.
- `BoardVendorLockIn` → offline verification and exportable receipts, trust roots, ontology, and policy history.
- `BoardFinancialControlBypass` → ICFR scope, key-control receipts, management-override receipts, and segregation of duties.
- `BoardEvidenceBlindness` → receipted board packages, end-to-end metric traceability, zero material REFUSED subjects, zero unresolved risk-appetite breaches, and independent board-package assurance.

Each generated board requirement carries `prov:wasDerivedFrom` to its prohibited goal. The ontology is semantic authority; generated TypeScript is a consumer projection.

## Generated projections

The pack generates:

- `src/board.generated.ts` — 49 board admission predicates.
- `src/board-goals.generated.ts` — 10 DfCM prohibited board-failure goals.

The consumer combines these with the base `castle-pack` projection rather than editing generated base outputs.

## Standing

The pack defines internal executable admission predicates. It does not assert external certification, audit opinion, regulatory compliance, or board approval by itself.