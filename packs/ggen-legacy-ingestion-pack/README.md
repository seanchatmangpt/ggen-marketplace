# ggen-legacy-ingestion-pack

Fortune 5 ingestion compiler contract for the `ggen-legacy` frontend.

The pack lifts `dslmodel`'s reader-family pattern into an evidence-bounded observer registry while preserving the `ggen-legacy` architecture boundary: observation is not admission, admission is not actuation, and registry coverage is not decoder execution standing.

## Registry

`registry-a.tsv` + `registry-b.tsv` are the deterministic ordered registry distribution governed by `ontology.ttl` and independently checked by `gates/verify_registry.py`:

- 24 format families
- 511 concrete formats
- 62 read-only live observation surfaces
- 83 Fortune 5 controls
- 10 stages
- 690 ordered obligations

Formats span structured text/RDF, modern and legacy languages, formal/planning languages, builds/packages, API/IDL/MCP, relational/columnar/scientific data, documents/office/notebooks, process/OCEL/XES, enterprise architecture, IaC/cloud/Kubernetes, CI/CD/SDLC, observability/network, IAM/security/SBOM/provenance/compliance, binaries/bytecode/archives, mainframe/IBM i/SAP/Salesforce/ServiceNow, collaboration/PIM, AI/ML/design, industrial/IoT, geospatial/media, generated artifacts, and unknown opaque inputs.

Live surfaces cover VCS, databases, APIs, Kubernetes, AWS/Azure/GCP, Terraform schemas, runtime state, CI, ticketing/CMDB, IAM, observability, enterprise SaaS, network/service discovery, artifact stores, secret-store metadata, and collaboration systems.

## Fortune 5 admission law

The registry encodes exact-source/digest identity, no-silent-drop and opaque preservation, bounded archive expansion, parser resource limits, sandbox/default-deny/no-auto-exec, secret/PII fencing, tenant/residency/legal-hold controls, deterministic normalization, provenance DAGs, read-only live observation, pagination closure, checkpoint/resume, receipt chains, independent replay, supply-chain identity, least privilege, and BRCE-gated consequential extension.

The ingestion stages remain separate:

`DETECTED → IDENTIFIED → HASHED → DECODED → PARSED → NORMALIZED → OBSERVED → MAPPED → ADMITTED`

`QUARANTINED` preserves evidence. `UNSUPPORTED` is visible topology, never absence.

## Verify

```bash
python3 gates/verify_registry.py
```

A successful run reports `ALIVE` only for the exact registry contract. Individual decoders/connectors remain `UNKNOWN`, `UNSUPPORTED`, `BLOCKED`, or separately `ALIVE` based on observed execution. No Fortune 5 production deployment or certification is claimed by this pack.
