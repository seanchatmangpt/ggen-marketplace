# Target Architecture: ggen-marketplace

## 1. Vision & Ecosystem Topology
Transform `ggen-marketplace` into an automated, federated semantic registry providing certified capability discovery and closed-loop execution patterns across distributed ecosystems:

```text
public ontologies / ggen-marketplace
            ↓
      ggen_igniter
            ↓
 ash_r2rml / ash_a2a / ash_pplan / beam4pm
            ↓
┌──────────────────────────────────────────┐
│                   XaaS                   │
│                                          │
│ canonical Ash resources + Postgres       │
│ FOND/HDDL planning                       │
│ SemanticIR / knowledge hooks             │
│ A2A capability projection                │
│ DurableServer / OTP continuity           │
│ PPCX / identity / disclosure             │
│ ground-network primitives                │
│ OCEL / receipts / replay                 │
│ BRCE / Reactor — ONLY DO CROWN           │
└──────────────────────────────────────────┘
            ↑
      tenant/product graph
            │
┌──────────────────────────────────────────┐
│                  ZOELA                   │
│                                          │
│ ZOE ontology                             │
│ Kingdom Capability semantics             │
│ Planning Center adapter                  │
│ church-specific policies                 │
│ ZOE Marketplace                          │
│ mobile/web UX                            │
│ local/offline projections where useful   │
└──────────────────────────────────────────┘
```

## 2. Core Architectural Roles
- **XaaS** is the platform, canonical Ash execution runtime, institutional Postgres system of record, and sole DO crown. It consumes generic capability, planning, consequence, and Ash PaaS packs.
- **ZOELA** is the tenant product projection over XaaS. It consumes experience projection, deterministic dynamic UI, and presentation packs.
- See [`docs/adr/ADR-0003-ecosystem-topology-and-composition-boundary.md`](file:///Users/sac/ggen-marketplace/docs/adr/ADR-0003-ecosystem-topology-and-composition-boundary.md) for the complete decision record and pack allocation matrix.

## 3. The Closed-Loop Pattern Catalog (CalVer & Compatibility)
The 12 consolidated capability packs define the underlying capability topology. Over this topology, `ggen-marketplace` introduces the **Pattern Catalog**:
$$\boxed{O_t \rightarrow \text{HDDL} \rightarrow \text{FOND} \rightarrow \text{SELECT} \rightarrow \text{CONSTRUCT} \rightarrow \text{BRCE} \rightarrow R_t \rightarrow \text{Replay} \rightarrow \text{MX} \rightarrow O_{t+1}}$$

- **Pattern**: `patterns/fond-hddl-mx-loop/` (`fond-hddl-mx-loop@v26.9.13`)
- **Domain #1**: `domains/repo-closure/` (`repo-closure@v26.9.13`)
- **CalVer Invariant**:
  $$\text{VersionIdentity} \neq \text{CompatibilitySemantics}$$
  CalVer records admission date ($v26.9.13$), while machine-readable RDF predicates (`compatibleWith`, `supersedes`, `requires`, `projects`, `conformsTo`, `breakingAgainst`) govern compatibility.
- **Promotion Invariant**: $\text{Experience} \neq \text{Authority}$. No MX-derived candidate enters exploitation without formal verification and admission into a new CalVer release.
- See [`docs/adr/ADR-0004-fond-hddl-mx-loop-pattern-and-calver.md`](file:///Users/sac/ggen-marketplace/docs/adr/ADR-0004-fond-hddl-mx-loop-pattern-and-calver.md).

## 4. Key Marketplace Target Capabilities
1. **Level-5 Pack Maturity**: Full formal verification, automated SHACL shape validation, and Diátaxis documentation coverage for all packs.
2. **Deterministic Registry Distribution**: Release distribution with cryptographic provenance and tamper-evident receipts.
3. **Option-Hypergraph Amplification (R15)**: Hypergraph querying over pack capabilities, dependencies, and composition paths.
4. **Automated Admission Pipeline**: Zero-trust CI admission combining `star-toml`, containerized ggen execution, and consumer generation tests.
