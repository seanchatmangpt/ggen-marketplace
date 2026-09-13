# Reference: `ash_*` Ecosystem Mapping

This reference documents the mapping between the 8 reusable `ash_*` Elixir/Hex packages and the canonical packs/patterns in `ggen-marketplace`.

---

## 1. Architectural Topology

```text
ggen-marketplace (reusable pack source, ontologies, patterns)
    ↓
ash_* (reusable Ash / Elixir machinery)
    ↓
XaaS (canonical Ash platform, institutional Postgres, sole DO crown)
    ↑
ZOELA (ZOE product / tenant projection)
```

**Ecosystem Invariants**:
- `ash_*` MUST NOT depend on `ZOELA`.
- `ash_*` provides reusable, un-opinionated Ash Framework extensions and compilers.
- Consequential execution (`DO`) remains behind the repository's admitted boundary (e.g. BRCE / Reactor).

---

## 2. Package-to-Pack Mapping Matrix

| Repository | Current Version | Primary Capability | Admitted Marketplace Packs |
|---|---|---|---|
| **`ash_a2a`** | `26.9.12` | Projects public Ash actions into A2A protocol skills & AgentCards. Zero-config capability discovery. | [`elixir-mcp-a2a-pack`](file:///Users/sac/ggen-marketplace/packs/elixir-mcp-a2a-pack), [`experience-projection-pack`](file:///Users/sac/ggen-marketplace/packs/experience-projection-pack) |
| **`ash_ex4pm`** | `26.9.10` | Automatic OCEL 2.0 event emission for Ash resources via `ex4pm`. | [`ash-ocel-revops-surface-factory-pack`](file:///Users/sac/ggen-marketplace/packs/ash-ocel-revops-surface-factory-pack), [`ash-runtime-integration-contract-pack`](file:///Users/sac/ggen-marketplace/packs/ash-runtime-integration-contract-pack) |
| **`ash_expo`** | `0.1.0-dev` | Connects Ash resources to React Native / Expo with offline policy & client adapters. | [`supabase-pack`](file:///Users/sac/ggen-marketplace/packs/supabase-pack), [`dfcm-dd-ui-pack`](file:///Users/sac/ggen-marketplace/packs/dfcm-dd-ui-pack) |
| **`ash_kudzu`** | `0.1.0` | SHACL admission gate validating resource ontologies fail-closed before compilation. | [`autofde-semantic-registry-pack`](file:///Users/sac/ggen-marketplace/packs/autofde-semantic-registry-pack), [`planning-policy-pack`](file:///Users/sac/ggen-marketplace/packs/planning-policy-pack) |
| **`ash_planning_center`** | `26.9.10` | Ash resources over Planning Center Online; OpenAPI-to-Turtle generator. | [`domain-capability-pack`](file:///Users/sac/ggen-marketplace/packs/domain-capability-pack), [`protocol-integration-pack`](file:///Users/sac/ggen-marketplace/packs/protocol-integration-pack) |
| **`ash_pplan`** | `26.9.7` | P-PLAN & PROV-O control plane; FOND policy validation; Reactor continuations. | [`planning-policy-pack`](file:///Users/sac/ggen-marketplace/packs/planning-policy-pack), [`fond-hddl-mx-loop`](file:///Users/sac/ggen-marketplace/patterns/fond-hddl-mx-loop), [`consequence-ir-pack`](file:///Users/sac/ggen-marketplace/packs/consequence-ir-pack) |
| **`ash_r2rml`** | `26.9.12` | W3C R2RML semantic mapping compiler; OBDA virtual SPARQL-to-SQL over Ash reads. | [`ash-r2rml-paas-pack`](file:///Users/sac/ggen-marketplace/packs/ash-r2rml-paas-pack), [`ash-r2rml-reactor-paas-pack`](file:///Users/sac/ggen-marketplace/packs/ash-r2rml-reactor-paas-pack), [`ash-extension-starter-pack`](file:///Users/sac/ggen-marketplace/packs/ash-extension-starter-pack) |
| **`ash_surface`** | `0.1.0` | Manifest-first consumer surfaces; emits vanilla `.mjs` + JSDoc + Zod. | [`experience-projection-pack`](file:///Users/sac/ggen-marketplace/packs/experience-projection-pack), [`deterministic-dynamic-ui-pack`](file:///Users/sac/ggen-marketplace/packs/deterministic-dynamic-ui-pack) |

---

## 3. Tooling and Generation Boundaries

1. **`mix ggen_igniter.sync` (Elixir)**:
   - Used by `ash_planning_center`, `ash_pplan`, `ash_a2a`, and `ash_ex4pm`.
   - Reads Turtle ontologies and SPARQL queries to generate Ash resources and extensions.
2. **`ggen sync run` (Rust CLI)**:
   - Driven by `ggen.toml` files in `ash_r2rml`, `ash_pplan`, and `ash_surface`.
   - Projects Tera/`.tmpl` templates into compiling Elixir/EEx artifacts.
