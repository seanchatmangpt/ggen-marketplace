# ADR-0005: AshSurface MX Consumer Surface Projection for ZOELA

## Status
Accepted

## Context
Initial iterations of `ash_surface` (`0.1.0` / JS runtime `0.2.0`) projected Ash actions as simple tuples: `(Action + Profile + Transport)`. While effective for transport selection and basic invocation receipts, this is insufficient for Machine Experience (MX) consumer applications like ZOELA.

ZOELA contains substantial duplicate client code (handwritten FOND/HDDL candidate checking, Supabase/Drizzle domain authority, handwritten Zod schemas). To eliminate this duplication and enforce:
$$\boxed{\text{XaaS/Ash} \longrightarrow \text{AshSurface}_{MX} \longrightarrow \text{ZOELA}}$$
`ash_surface` must upgrade to **`v26.9.13 — MX Consumer Surface`**, backed by marketplace-canonical ontologies and contracts.

## Decision
1. **CalVer Binding**:
   Align `ash_surface`, its surface contracts, and JS runtime to **`v26.9.13`**.

2. **First-Class Action Authority**:
   Every Surface action explicitly declares its authority boundary (`OBSERVE | SELECT | CONSTRUCT | DO`), `hasDOAuthority false` (for SELECT/CONSTRUCT), pre/post state transitions, and typed refusal schemas.

3. **Observation Projection ($ObservationProjection(W_t)$)**:
   Formal snapshot representation of world state from XaaS/Ash, feeding the planner with exact subject, state digest, and standing.

4. **FOND/HDDL Planning Episode Projection**:
   AshSurface surfaces planning candidate results (`VALID_STRONG | VALID_STRONG_CYCLIC | REFUSED`) without reimplementing the planner engine.

5. **MX Composed Receipt Envelope**:
   Composes transport disposition receipts with backend domain consequence receipts:
   $$\boxed{TransportReceipt \neq ConsequenceReceipt}$$

6. **Unknown-After-Dispatch Reconciliation**:
   Closes the offline/mobile timeout boundary safely:
   $$Timeout \not\Rightarrow NonExecution$$
   Commands in `TRANSPORT_OUTCOME_UNKNOWN` are reconciled via `reconcile(commandId)` with zero re-actuation retry.

7. **Server-to-Client Event Projection**:
   Realtime PubSub/Phoenix Channel event streaming carrying sequence numbers, state digests, and receipt references.

8. **Generated Zod & JSDoc Contracts**:
   `AshManifest` $\rightarrow$ `ggen/AshSurface` $\rightarrow$ complete executable client descriptors without handwritten schemas in ZOELA.

9. **ZOELA Code Reduction**:
   ZOELA becomes strictly: $\boxed{\text{ZOELA} = \text{MobileProjection}(\text{XaaS/Ash})}$. Handwritten FOND/HDDL, domain mutation code, and validation schemas in ZOELA are deleted.

## Consequences
- `ggen-marketplace` defines the canonical contracts in `patterns/fond-hddl-mx-loop/contracts/surface_mx.ttl` and `mx_receipt.ttl`.
- `packs/experience-projection-pack` enforces the `020_mx_authority_ceiling.rq` gate.
- `ash_surface` has an authoritative specification to implement its `v26.9.13` release.
