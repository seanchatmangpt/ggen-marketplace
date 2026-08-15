# DfCM Full Deployment Pack

**Design for Combinatorial Maximalism (DfCM)** maximizes the lawful reversible option graph before irreversible selection while preserving explicit authority boundaries.

This pack manufactures a complete DfCM control-plane consumer from one canonical RDF graph. It does not grant ambient execution authority. `SELECT`, `CONSTRUCT`, and `DO` are distinct operations; only the BRCE boundary may perform `DO`, and every successful actuation produces a chained receipt that can be replay-verified before standing becomes `ALIVE`.

## Manufactured surfaces

1. **Preserve** — retain reversible lawful candidates and treat a failed edge as topology, not graph failure.
2. **Fence** — carry the semantic quotient, exclusions, capability bounds, and Chesterton-style preservation obligations before removal.
3. **Calculus** — objects, morphisms, admission, closure, authority, actuation, receipt, replay, and standing are first-class.
4. **Exclusions** — ambient execution, unreceipted actuation, hook actuation, projection authority, and inspection-as-execution are forbidden.
5. **Falsifier** — every required component names its verifier and falsifier.
6. **Extension** — runtime adapters, Lean admission, mfact certificates, and hooks extend the graph without bypassing authority.
7. **Operationalization** — ontology → SPARQL → ggen → generated runtime → BRCE → receipt → replay → standing.

The generated Python verifier executes the exact generated runtime against an in-memory consequence adapter. It proves positive execution plus named refusal, hook non-actuation, graph preservation after a failed edge, receipt-chain verification, and exact-subject `ALIVE` standing. The in-memory adapter is a verifier fixture only; production actuation must be supplied through the same `Actuator` protocol and BRCE boundary.

Generated outputs are projections and must not become editing surfaces. The RDF graph is canonical.

## Generation

```sh
ggen sync
python consumer/dfcm/verify_dfcm.py
```

Expected verifier standing: `ALIVE`.

The Lean artifact is an admission boundary, not a claim that Lean executed during generation. The mfact boundary is represented in the deployment manifest and must be certified by the downstream mfact verifier before release standing is promoted.
