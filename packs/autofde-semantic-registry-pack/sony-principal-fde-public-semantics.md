# Sony Pictures Principal FDE public-semantics overlay

This overlay extends the generic AutoFDE semantic registry with the public semantic sources needed to ground the supplied Sony Pictures Entertainment Principal Forward Deployed Engineer role without embedding Sony-specific private domain facts into GymAct or AutoFDE-Lab.

## Media and rights-sensitive production

| Role surface | Public semantic authority |
|---|---|
| film/TV creative works, seasons, episodes, versions, participants, relationships | MovieLabs Creative Works Ontology; schema.org CreativeWork/Movie/TVSeries/MediaObject |
| production/post-production assets, compositions, versions, camera/audio/image/CG assets, participants, infrastructure | MovieLabs Ontology for Media Creation (OMC), current public docs v2.8 |
| broadcast/audiovisual metadata | EBUCore |
| editorial/media subject taxonomies and production roles | IPTC NewsCodes / Media Topics |
| rights, permissions, prohibitions, duties, constraints | W3C ODRL 2.2 |
| standardized public rights statements | RightsStatements.org vocabulary |
| Creative Commons permissions/license metadata | ccREL / Creative Commons namespace |
| preservation objects, events, agents and rights | PREMIS 3 OWL ontology |
| provenance and derivation | PROV-O |
| annotations and review notes | W3C Web Annotation Vocabulary |
| general descriptive metadata | Dublin Core Terms; schema.org |

MovieLabs is particularly important for SPE: MovieLabs states that OMC was co-developed with Sony Pictures Entertainment and other major studios and exists specifically to make media-production workflow software interoperable. Therefore it is a direct public industry ontology for the job's rights-sensitive media-production boundary rather than an analogy from generic cloud architecture.

## SDLC, Secure SDL, and AI-DLC are distinct

Do not collapse these terms:

- **SDLC**: lifecycle stages and software engineering evidence. Ground with ISO/IEC/IEEE lifecycle concepts where openly addressable, SWEBOK vocabularies where public, OpenAPI/AsyncAPI/API schemas, SPDX/CycloneDX/SLSA/in-toto, testing schemas, Git and CI/CD public models.
- **Secure Development Lifecycle / Secure SDLC**: NIST SSDF, OWASP SAMM, OWASP ASVS, NIST 800-53/OSCAL, CWE/CVE/CAPEC, SLSA, SPDX/CycloneDX, OPA/Rego policy surfaces.
- **AI-DLC**: no single mature public ontology is sufficient. It must be composed from software lifecycle + AI system + model/data provenance + evaluation + telemetry + risk/governance semantics. Public anchors include NIST AI RMF and GenAI Profile, SPDX 3 AI/Dataset profiles, ML Schema/Croissant where applicable, PROV-O/DCAT/DQV, OpenLineage, OpenTelemetry GenAI semantic conventions, model-card/dataset documentation schemas, and provider runtime API schemas. `AI-DLC` itself remains a local organizational practice label unless a public SPE/EIP definition is published.

## Full-stack application and platform surface

| Role surface | Public source family |
|---|---|
| backend HTTP APIs | OpenAPI |
| event-driven APIs | AsyncAPI + CloudEvents |
| RPC | Protocol Buffers descriptors + gRPC service descriptors |
| data schemas | JSON Schema, Avro, CSVW, R2RML/RML where semantic projection is required |
| software components/dependencies/builds | SPDX 3, CycloneDX, PURL, SLSA, in-toto |
| containers/images/runtime/distribution | OCI specifications |
| orchestration | Kubernetes API/OpenAPI + CRDs |
| infrastructure as code | Terraform provider schemas; CloudFormation, ARM/Bicep, GCP API schemas as provider authority |
| observability | OpenTelemetry Semantic Conventions, OpenMetrics, CloudEvents |
| service objectives | OpenSLO |
| software/service ownership | Backstage Catalog model; W3C ORG/PROV-O for semantic projection |

## Cloud provider authority

Cloud providers generally do not publish one OWL ontology. Treat their official type systems as authoritative schemas and project them into RDF explicitly:

- AWS: CloudFormation resource specification/resource-provider schemas, Smithy/API models, IAM policy grammar, ARN grammar.
- Azure: ARM resource-provider/type model, Bicep/ARM schemas, Azure REST API specifications, RBAC/Entra role schemas, Resource Graph types.
- GCP: API protobuf/service definitions, Cloud Asset Inventory asset/relationship/policy types, IAM policy model, organization-policy constraints, full-resource-name grammar.
- Terraform: `terraform providers schema -json` is an implementation vocabulary; it does not outrank the cloud-provider authority.

## AI/LLM runtime surface

The JD's RAG, agents, prompt architecture, evaluation, observability and guardrails require a federation rather than a fabricated single ontology:

- model/dataset/software identity and provenance: SPDX 3 AI/Dataset profiles + PROV-O + DCAT/DQV;
- datasets: Croissant/MLCommons plus DCAT/DQV/PROV;
- runtime events: OpenTelemetry GenAI semantic conventions + CloudEvents;
- lineage: OpenLineage;
- risk/governance: NIST AI RMF + GenAI Profile, OSCAL for control implementation/evidence, DPV for privacy and AI-related processing;
- policies/guardrails: ODRL, XACML/OPA/Rego models, SHACL admission constraints;
- provider-specific inference capability: Bedrock, Azure OpenAI, OpenAI, Anthropic public API schemas/specifications are implementation contracts, not ontologies;
- agents/tools: public protocol schemas may be projected, but protocol support does not itself prove agent capability.

## Enterprise/stakeholder surface

- organization, units, membership and roles: W3C ORG;
- people/agents: FOAF/schema.org/vCard RDF;
- capability/process/application/infrastructure relationships: ArchiMate exchange semantics + TOGAF content metamodel where publicly usable; BPMN/DMN/CMMN/BMM for processes, decisions, cases and motivation;
- provenance of stakeholder requests and decomposed plans: PROV-O;
- requirements and traceability: OSLC lifecycle-resource vocabularies plus project-specific instance data;
- project/product/platform ownership: schema.org + ORG + PROV-O + Backstage catalog projection.

## Governance and rights-sensitive data

- personal-data processing, purposes, roles, legal bases, technologies and risk: DPV and extensions;
- data usage policies: ODRL;
- controls/evidence: NIST OSCAL + 800-53 + CSF;
- threat/weakness/vulnerability: STIX 2.1, ATT&CK, D3FEND, CAPEC, CWE, CVE, CVSS;
- identity lifecycle and federation: SCIM, OAuth/OIDC, SAML, WebAuthn/FIDO, SPIFFE/SPIRE;
- access policy: XACML, NIST RBAC/NGAC plus provider IAM schemas;
- software supply-chain evidence: SPDX, CycloneDX, SLSA, in-toto, Sigstore bundles.

## Process and handoff

The engagement lifecycle `scope -> prototype -> production hardening -> handoff -> incumbent ownership -> reusable pattern -> platform backlog` should be represented as instance data over public process/provenance semantics, not encoded as a new private ontology:

- BPMN/POWL for process structure;
- OCEL/XES for execution evidence;
- PROV-O for derivation/responsibility;
- ORG for teams/roles;
- OSLC for lifecycle-resource relationships;
- SPDX/SLSA/in-toto for produced software/build evidence;
- DCAT/DQV/OpenLineage for produced data products;
- ArchiMate/TOGAF for architecture views and capability relationships.

The phrase **AI-DLC** and Sony-specific organizational names such as **EIP**, **Moveworks / Agentic Foundation**, internal handoff criteria, team-tier self-sufficiency, and internal platform backlog semantics remain **instance/local extension terms** unless an authoritative public machine-readable definition is discovered. They may be typed using public classes and relations, but must not be falsely promoted to public ontology terms.

## GymAct / AutoFDE-Lab consequence

GymAct should consume these sources as capability-space inputs; AutoFDE-Lab should compose them into enterprise missions. Neither repository should copy domain facts that are already present in public semantic authorities. Provider schemas and protocols are transformed into canonical graph projections with provenance, not asserted as equivalent OWL ontologies.
