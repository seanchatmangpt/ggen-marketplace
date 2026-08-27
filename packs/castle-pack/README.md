# castle-pack

Ontology-first semantic authority for CASTLE.

The pack projects admitted architecture/goal bindings into `src/generated.rs` and `docs/GENERATED_ARCHITECTURE.md`, the executable Fortune-5 readiness profile into `src/fortune5_generated.rs` and `docs/FORTUNE5_REQUIREMENTS.md`, and the federated security identity graph into `src/security_sources_generated.rs`, `src/security_tools_generated.rs`, and `src/security_core_generated.rs`. Runtime algorithms remain consumer consequences; this pack owns the component inventory, authority boundaries, prohibited-goal priorities, readiness control semantics, and reusable security-source/tool topology.

Canonical flow:

`GOAL -> DfCM inverse construction -> dependency CONSTRUCT -> planner ensemble -> POWL v2 -> bounded GymAct -> OCEL v2 -> cryptographic receipt -> replay/invariant compilation`.

Fortune-5 admission adds 40 deterministic controls covering authority separation, isolation, supply chain, replay compatibility, observability, resilience, availability/SLOs, data policy, scale, determinism, evidence, typed refusal, change/rollback, air-gapped CONSTRUCT, adversarial coverage, quota headroom, and explicit owned-or-authorized execution scope.

Each readiness requirement is represented in RDF as a `castle:Fortune5Requirement` with a metric, comparator, target, category, authority, description, and deterministic order. ggen projects those facts into the consumer evaluator. Missing evidence is not success: the CASTLE runtime maps missing evidence to `UNKNOWN`, failed or invalid evidence to `REFUSED`, and complete receipted satisfaction to `ALIVE`.

## Federated security universe

`security-universe.ttl` preserves external framework/ontology identities, version policy, machine surface, and the 22-source Fortune-5 security core. `security-tools.ttl` preserves cloud/security-tool integration topology. These files do **not** vendor normative control text and do **not** claim certification. Registry presence means only that CASTLE can identify an authority or evidence bridge.

The pack gate fails closed if a source/tool row is incomplete, source/tool IDs collide, the Fortune-5 security core is not exactly 22 identities, or any tool claims direct CASTLE actuation authority. Native policy engines and enforcers therefore remain external evidence/enforcement surfaces behind the consumer's admission boundary.

The Fortune-5 profile is an internal executable readiness gate, not an assertion of external certification. Stricter profiles may raise thresholds; weakening a target requires a new versioned semantic source and receipt.

Planner and CONSTRUCT outputs are candidates only. GymAct execution is constrained to explicit owned/authorized test envelopes. Consequential defensive actuation remains BRCE receipt-bound.
