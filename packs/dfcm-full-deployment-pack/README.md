# DfCM Full Deployment Pack

**Design for Combinatorial Maximalism (DfCM)** maximizes the lawful reversible option graph before irreversible selection while preserving explicit authority boundaries.

This pack manufactures the DfCM control plane and a **Fortune 5 readiness evidence plane** from one canonical RDF graph. It does not grant ambient execution authority. `SELECT`, `CONSTRUCT`, and `DO` remain distinct; only BRCE may perform `DO`, and successful actuation must produce replay-verifiable receipts before the exact subject can earn `ALIVE`.

## Core DfCM closure

1. **Preserve** — retain reversible lawful candidates and treat a failed edge as topology, not graph failure.
2. **Fence** — carry the semantic quotient, exclusions, capability bounds, and Chesterton-style preservation obligations before removal.
3. **Calculus** — objects, morphisms, admission, closure, authority, actuation, receipt, replay, and standing are first-class.
4. **Exclusions** — ambient execution, unreceipted actuation, hook actuation, projection authority, and inspection-as-execution are forbidden.
5. **Falsifier** — every required component and enterprise control names its verifier and falsifier.
6. **Extension** — runtime adapters, Lean admission, mfact certificates, hooks, and enterprise controls extend the graph without bypassing authority.
7. **Operationalization** — ontology → SPARQL → ggen → runtime → BRCE → receipt → replay → standing.

## Fortune 5 readiness closure

The enterprise layer is **50 mandatory controls across 10 domains**, five controls per domain:

- governance and enterprise risk
- identity and access
- data and privacy
- platform and tenancy
- software supply chain
- delivery and change
- reliability and resilience
- observability and security operations
- finance and vendor management
- compliance and assurance

Every control binds:

`domain × criticality × accountable role × evidence kind × framework reference × evidence freshness × verifier × falsifier`

The core external reference profile is intentionally conservative: NIST CSF 2.0 for enterprise cybersecurity-risk outcomes, NIST SP 800-53 Rev. 5 release 5.2.0 for control coverage, and the final NIST SSDF 1.1 for secure software development. Workload-specific frameworks such as PCI DSS, FedRAMP, HIPAA, SOX, GDPR, or ISO certification are adapters, not implied claims.

### Readiness is not certification

`FORTUNE5_ALIVE` means the generated verifier observed complete, fresh, exact-subject evidence for the internal 50-control readiness contract. It **does not** assert SOC 2, ISO 27001, PCI DSS, FedRAMP, or any other external certification. The `certification-claim-fence` control refuses unreceipted certification claims.

## Generated enterprise artifacts

`ggen sync` additionally manufactures:

- `consumer/dfcm/enterprise/fortune5-controls.json` — canonical machine-readable control inventory
- `consumer/dfcm/enterprise/FORTUNE5_READINESS.md` — executive/control-owner projection
- `consumer/dfcm/enterprise/fortune5-deployment.toml` — deployment and proof contract
- `consumer/dfcm/enterprise/evidence.schema.json` — evidence snapshot schema
- `consumer/dfcm/enterprise/verify_fortune5.py` — fail-closed exact-subject readiness verifier

Generated outputs are projections and must not become editing surfaces. `ontology/dfcm.ttl` remains canonical.

## Verification

```sh
ggen sync
python consumer/dfcm/verify_dfcm.py
python consumer/dfcm/enterprise/verify_fortune5.py --self-test
python consumer/dfcm/enterprise/verify_fortune5.py \
  --subject <exact-subject> \
  --evidence <evidence-snapshot.json>
```

The self-test establishes **`VERIFIER_ALIVE`**, not production-subject standing. A real subject receives `ALIVE` only from its own complete evidence snapshot.

The Lean artifact is an admission boundary, not a claim that Lean executed during generation. The mfact boundary remains the release-certificate boundary over ontology, admission, runtime receipt, replay, standing, and enterprise-control evidence.
