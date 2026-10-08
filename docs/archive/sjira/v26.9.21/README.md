# sJira v26.9.21 — WD Semantic Failure Analysis

## Subject

This subtree is the semantic work/evidence plan for implementing the Western Digital HDD failure-analysis case study from reusable `ggen-marketplace` capability packs.

The target application is:

```text
Next.js (JavaScript + JSDoc + Zod)
        ↓ HTTPS / JSON
FastAPI + Pydantic + SQLAlchemy
        ↓
sJira semantic WorkOrders
        ↓
SA2A capability adapters
        ↓
AutoFDE Lab / TPOT / PM4Py / POWL / OCEL 2.0
        ↓
evidence → verification → receipt → replay → MachineExperience
```

The working-backwards invariant is:

> Every solved failure should make the next equivalent failure cheaper to understand.

## Standing

- **Milestone**: `v26.9.21`
- **Repository**: `seanchatmangpt/ggen-marketplace`
- **Exact base**: `616e93d1e6f9566e4b5eb4e2c3d1400746786e50`
- **Status**: `CANDIDATE`
- **Authority ceiling**: `OBSERVE | SELECT | CONSTRUCT | VERIFY`
- **Consequential DO**: outside this repository and outside this milestone.
- **Evidence ceiling**: these files establish a work graph only. They do not establish that proposed packs, WD integrations, live Jira mutation, production SA2A peers, or runtime FA behavior exist.

## Chesterton / prior-art result

The marketplace already contains the horizontal architecture. The implementation should compose those packs before inventing new infrastructure.

### Canonical active topology to reuse

| Capability | Pack | Observed role |
|---|---|---|
| Platform front door | `ggen-platform-pack` | Declares the consolidated platform components |
| Process semantics | `process-intelligence-pack` | Event/Object/ProcessModel/Conformance/Drift |
| Protocol binding | `protocol-integration-pack` | Capability → protocol/transport adapter without semantic duplication |
| Projection law | `semantic-projection-pack` | Canonical semantic source → non-sovereign generated artifact |
| Evidence / standing | `evidence-standing-pack` | NoReceipt ⇒ NoStanding |
| Planning | `planning-policy-pack` | HDDL/FOND/world/role; SELECT ≠ DO |
| Candidate frontier | `decision-optionality-pack` | evidence requirements, falsifiers, reversible selection |
| Machine experience | `experience-projection-pack` | discoverable/composable/verifiable/replayable MX |
| Lifecycle | `state-transition-pack` | observed → selected → constructed → executed → verified |
| Release law | `repository-lifecycle-pack` | Source → Build → Verify → Release |

### Specialized packs to compose

| Capability | Pack | Disposition |
|---|---|---|
| SHACL projection law | `shacl-projection-pack@0.1.0` | REUSE |
| SHACL → Pydantic | `shacl-to-pydantic-pack@0.1.0` | REUSE with `shacl-projection-pack` |
| OCEL manufacture | `ggen-ecosystem-ocel-pack@26.8.26+1` | REUSE/EXTEND for HDD object/event types |
| POWL v2 semantics | `ontostar-mustar-powlv2-agent-pack@26.7.30` | REUSE semantics, not its full agent runtime |
| Standing vocabulary | `autofde-lab-standing-vocabulary-pack@26.9.1` | REUSE |
| Semantic source registry | `autofde-semantic-registry-pack@1.0.0` | REUSE for public ontology inventory/admission |
| Receipt contracts | `receipt-provenance-unification-pack@0.1.0` | REUSE |
| Negative witness court | `semantic-gate-witness-court-pack@26.8.27` | REUSE |
| Evidence independence | `evidence-lineage-independence-pack@0.1.0` | REUSE |
| Next.js prior art | `nextjs-ai-sdk-pack`, `nextjs-ai-sdk-ui-shadcn-pack` | REFERENCE/EXTEND only; current templates are TS/TSX-oriented |

## Confirmed gaps

The exact marketplace tree at the base contains no path named for `fastapi`, `zod`, or `jsdoc`. Therefore the following are explicit work items rather than assumed capabilities:

1. **`shacl-to-fastapi-pack`** — generate FastAPI router/request/response surfaces from admitted SHACL/Pydantic contracts.
2. **`shacl-to-zod-jsdoc-pack`** — generate runtime Zod schemas plus JSDoc typedefs for a no-TypeScript Next.js consumer.
3. **`sa2a-fastapi-pack`** — project `protocol-integration-pack` capability bindings into Python/FastAPI SA2A endpoints and envelopes.
4. **`wd-failure-analysis-pack`** — WD-specific domain overlay: Drive, FailureCase, Lot, Component, Supplier, BOMRevision, FirmwareRevision, ProductionLine, TestStation, TestRun, Rework, EvidenceArtifact, FailureMode, KnownIssue, DiagnosticAction, Disposition, CorrectiveAction, plus applicability/exclusion/falsifier shapes.

These are candidate names until implementation and qualification.

## sJira work streams

| ID | Work stream | Owner | Disposition |
|---|---|---|---|
| SJIRA-WDFA-001 | Compose canonical marketplace platform packs | ggen-marketplace | REUSE |
| SJIRA-WDFA-002 | Admit public ontology/source inventory | ggen-marketplace | REUSE/EXTEND |
| SJIRA-WDFA-003 | Create WD failure-analysis domain overlay | ggen-marketplace | BUILD |
| SJIRA-WDFA-004 | Define SHACL shapes for WorkOrder/domain state | ggen-marketplace | BUILD |
| SJIRA-WDFA-005 | Generate Pydantic models from SHACL | ggen-marketplace | REUSE |
| SJIRA-WDFA-006 | Manufacture FastAPI projection pack | ggen-marketplace | BUILD |
| SJIRA-WDFA-007 | Manufacture Zod + JSDoc projection pack | ggen-marketplace | BUILD |
| SJIRA-WDFA-008 | Manufacture Python SA2A/FastAPI projection pack | ggen-marketplace | BUILD |
| SJIRA-WDFA-009 | Manufacture OCEL 2.0 HDD object/event projection | ggen-marketplace | EXTEND |
| SJIRA-WDFA-010 | Integrate PM4Py process analysis | autofde-lab | DOWNSTREAM |
| SJIRA-WDFA-011 | Integrate POWL v2 process representation | autofde-lab | DOWNSTREAM |
| SJIRA-WDFA-012 | Integrate TPOT candidate-model search | autofde-lab | DOWNSTREAM |
| SJIRA-WDFA-013 | Integrate AutoFDE hypothesis/experiment selection | autofde-lab | DOWNSTREAM |
| SJIRA-WDFA-014 | Build sJira semantic WorkOrder projection | consumer + marketplace semantics | BUILD |
| SJIRA-WDFA-015 | Build Next.js FA workbench | consumer app | DOWNSTREAM |
| SJIRA-WDFA-016 | Bind receipts, provenance, and replay | marketplace + consumer | REUSE/EXTEND |
| SJIRA-WDFA-017 | Add known/partial/unknown negative controls | marketplace + autofde-lab | BUILD |
| SJIRA-WDFA-018 | Add evidence-lineage independence court | marketplace + consumer | REUSE |
| SJIRA-WDFA-019 | Close UNKNOWN → verified disposition → MachineExperience → KNOWN replay | cross-repo | BUILD |
| SJIRA-WDFA-020 | Demonstrate four-case synthetic FA court and UI | cross-repo | BUILD |

The dependency graph and acceptance predicates are in [WORKGRAPH.ttl](./WORKGRAPH.ttl). The executable evidence requirements are summarized in [ACCEPTANCE.md](./ACCEPTANCE.md).

## Phase-one execution order

```text
public ontology inventory
        ↓
WD domain overlay + SHACL
        ↓
SHACL → Pydantic
        ├──→ FastAPI
        └──→ Zod/JSDoc → Next.js
        ↓
OCEL 2.0 HDD world
        ↓
PM4Py → POWL
        ↓
deterministic feature manufacture
        ↓
TPOT candidate models
        ↓
AutoFDE hypothesis / discriminating experiment
        ↓
sJira WorkOrder
        ↓
bounded simulated diagnostic
        ↓
independent verification
        ↓
receipt / replay / MachineExperience
```

## Phase-one exclusions

The first vertical slice deliberately excludes:

- production HDD actuation;
- live Jira SaaS mutation;
- unrestricted text-to-SQL;
- autonomous destructive teardown;
- enterprise-wide corpus ingestion;
- perfect multimodal extraction from all historical PowerPoints;
- production ACL federation;
- replacement of Jira, Confluence, or manufacturing systems.

Those remain separate authorization/integration problems after the semantic and replay kernel is proven.
