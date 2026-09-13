# ADR-0003: Ecosystem Topology and Platform Boundary: XaaS and ZOELA

## Status
Accepted

## Context
Initial iterations modeled ZOELA as a standalone Ash application that owned its own domain resources, local planning logic, ground-network semantics, and execution authority. However, evidence and architectural synthesis confirmed:
$$\boxed{\text{ZOELA is not an Ash application}}$$
It is a **ZOE-specific product/tenant projection over XaaS**, while XaaS is the canonical multi-tenant Ash platform, system of record, execution engine, and sole consequential DO crown.

## Decision
Establish the immutable unidirectional ecosystem topology:

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

1. **`ggen-marketplace` Role**:
   - Canonical corpus of reusable pack source and marketplace discovery.
   - Supplies foundational RDF vocabularies, templates, and fail-closed gates to both XaaS and ZOELA.
   - Zero application-specific composition logic belongs here.

2. **`XaaS` Role**:
   - The sole Ash runtime and institutional Postgres system of record.
   - Houses the FOND/HDDL planner runtime (strictly capped at `SELECT` / `CONSTRUCT`).
   - Houses generic ground-network, PPCX, purpose/disclosure, and A2A machine coordination primitives.
   - The **only** consequential DO crown via FrontierEvidence and BRCE/Reactor.

3. **`ZOELA` Role**:
   - A tenant product projection over XaaS.
   - Owns ZOE institutional ontology, Kingdom Capability semantics, Planning Center adapter, and church UX.
   - Employs zero hand-written Ash resources and has zero direct execution authority over backend records.
   - Generic semantics discovered in ZOELA prototypes (e.g. `src/lib/groundNetwork.ts`) graduate into marketplace ontologies and are manufactured into XaaS Ash resources via `ggen_igniter`.

## Pack Allocation Rules
- **XaaS Consumes**:
  - `xaas-public-ontology-profile` (public ontology profile)
  - `consequence-ir-pack` (consequence IR & BRCE authority laws)
  - `planning-policy-pack` (FOND/HDDL task decomposition; `SELECT != DO`)
  - `elixir-mcp-a2a-pack` (Elixir MCP router & A2A agent generation)
  - `ash-extension-starter-pack` (Reactor step graphs & receipted actions)
  - `ash-r2rml-reactor-paas-pack` & `ash-reactor-domain-error-contract-pack` (PaaS orchestration & error contracts)
  - `ash-runtime-integration-contract-pack` & `ash-ocel-revops-surface-factory-pack` (OCEL & RevOps audit)
  - `domain-capability-pack` (capability allowlists & count gates)
  - `dfcm-explore-candidate-factory-pack` (reversible candidate courts)
  - `runtime-evidence-authenticity-pack` (authentic runtime evidence)

- **ZOELA Consumes**:
  - `experience-projection-pack` (MX/HX capability projection)
  - `dfcm-dd-ui-pack` & `deterministic-dynamic-ui-pack` (reversible dynamic UI presentation)
  - `shadcn-ui-primitives-pack` (presentation primitives)
  - `supabase-pack` (transitional client RLS gates during Postgres migration)
  - `evidence-standing-pack` (standing badges & UI receipts)

- **Shared Cross-Repo Vocabulary**:
  - `domain-capability-pack` & `receipt-provenance-unification-pack`

## Consequences
- Single Ash execution runtime across the entire ecosystem (hosted in XaaS).
- Server machinery in ZOELA decreases toward zero ($\text{ZOELA-specific server machinery} \rightarrow 0$).
- All generic ground-network, PPCX, and planning primitives are maintained once as platform capabilities.
