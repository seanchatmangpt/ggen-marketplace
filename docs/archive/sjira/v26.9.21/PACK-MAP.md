# Pack Map — v26.9.21 WD FA

## Reuse first

This map records the smallest marketplace composition currently supported by observed pack contracts.

### Platform law

- `ggen-platform-pack@26.9.12`
- `process-intelligence-pack@26.9.12`
- `protocol-integration-pack@26.9.13`
- `semantic-projection-pack@26.9.12`
- `evidence-standing-pack@26.9.12`
- `planning-policy-pack@26.9.12`
- `decision-optionality-pack@26.9.12`
- `experience-projection-pack@26.9.12`
- `state-transition-pack@26.9.12`
- `repository-lifecycle-pack@26.9.12`

### Projection/evidence machinery

- `shacl-projection-pack@0.1.0`
- `shacl-to-pydantic-pack@0.1.0`
- `ggen-ecosystem-ocel-pack@26.8.26+1`
- `autofde-lab-standing-vocabulary-pack@26.9.1`
- `autofde-semantic-registry-pack@1.0.0`
- `receipt-provenance-unification-pack@0.1.0`
- `evidence-lineage-independence-pack@0.1.0`
- `semantic-gate-witness-court-pack@26.8.27`
- `ontostar-mustar-powlv2-agent-pack@26.7.30` for POWL semantics only.

### UI prior art

- `nextjs-ai-sdk-pack`
- `nextjs-ai-sdk-ui-shadcn-pack@0.1.0`

These are not a direct fit for the requested frontend because the current marketplace files are TS/TSX-oriented and there are no paths named `zod` or `jsdoc` in the exact base tree.

## New candidate packs

### shacl-to-fastapi-pack

Purpose:
- generate FastAPI `APIRouter` surfaces;
- reuse generated Pydantic models;
- preserve canonical SHACL lineage;
- emit stable operation identifiers;
- separate queries/commands from domain semantics.

Falsifier:
- an existing marketplace pack is found that already generates equivalent FastAPI artifacts from the same canonical shapes.

### shacl-to-zod-jsdoc-pack

Purpose:
- generate Zod runtime schemas;
- generate JSDoc typedefs;
- support Next.js JavaScript without TypeScript;
- keep field identity aligned with canonical SHACL.

Falsifier:
- an existing pack is found that generates equivalent Zod/JSDoc artifacts from admitted semantic shapes.

### sa2a-fastapi-pack

Purpose:
- reuse `protocol-integration-pack` Capability/Protocol/Transport/Adapter semantics;
- generate Python/FastAPI SA2A agent/capability descriptors and request/result envelopes;
- bind producer/evidence/semantic/horizon/capability identities;
- default consequential capabilities to explicit authority requirements.

Falsifier:
- an existing Python-targeted A2A pack is found with equivalent capability semantics and FastAPI projection.

### wd-failure-analysis-pack

Purpose:
- contain the irreducible HDD FA overlay after public ontology reuse;
- define SHACL admission for exact subjects, evidence, applicability, exclusions, falsifiers, known/partial/unknown standing, diagnostic actions, dispositions, and corrective actions;
- provide synthetic positive/negative fixtures.

It must not duplicate:
- generic provenance;
- quantities/units;
- generic observation/sensor semantics;
- generic process/event semantics;
- generic planning/standing/receipt semantics already owned by marketplace/public ontologies.

## Downstream ownership

The following are application integrations, not reusable marketplace pack source unless a reusable abstraction emerges:

- PM4Py adapter and feature extraction in `autofde-lab`;
- POWL execution/representation adapter in `autofde-lab`;
- TPOT candidate-model search in `autofde-lab`;
- AutoFDE hypothesis/experiment policy in `autofde-lab`;
- Next.js WD FA workbench in the consumer application;
- live enterprise data adapters;
- live Jira mutation;
- production diagnostic DO.

This preserves the marketplace boundary: reusable manufacturing capital belongs here; consumer composition and application runtime do not.
