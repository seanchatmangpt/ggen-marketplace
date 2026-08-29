# castle-paas-pack

Canonical ggen source for the CASTLE application platform built on Ash Framework, AshR2RML, Reactor, and public ontologies.

## Boundary

The pack does **not** replace CASTLE's Rust kernel. It manufactures the application/control plane around it:

`public ontology graph -> ggen -> Ash resource/action projection -> AshR2RML mapping IR -> R2RML/SHACL/OBDA -> Reactor workflows -> CASTLE kernel admission/BRCE -> receipts/replay`.

Ash owns resources, typed actions, relationships, policies, multitenancy, and API derivation. AshPostgres owns persistence. AshR2RML owns semantic correspondence and can emit deterministic ggen path/content bundles from compiled Ash resources. Reactor owns dependency resolution, concurrency, compensation, and saga rollback. The CASTLE kernel remains the only authority for exact-subject admission and consequential BRCE execution.

## Public ontology profile

Runtime semantics align to PROV-O, ODRL, DCAT, DCTERMS, SKOS, SOSA/SSN, QUDT, SHACL, RDF/RDFS/OWL and Schema.org. UCO and CASE are optional security-evidence vocabularies. `cp:*` exists only as generator metadata; it is not a competing enterprise domain ontology.

## PaaS resources

The source graph defines Organization, PlatformService, Subject, Observation, Admission, Plan, ExecutionIntent, Evidence, Receipt, Replay and Capability resources. ggen projects their module/table/public-class/tenancy/authority catalog. The consumer then defines the actual Ash resources and invokes `AshR2RML.Ggen.compile_ash_ttl_bundle/1` or `compile_api_bundle/2` to derive ontology, SHACL, R2RML and API consequences from the compiled Ash graph rather than maintaining parallel mappings.

## Reactor law

Seven workflow identities are generated: RegisterSubject, AdmitSubject, ConstructIntent, ExecuteIntent, QualifyEvidence, ReplayReceipt and PublishProjection. Exactly one may have `doBoundary=true`: ExecuteIntent, whose authority must be `BRCE_ONLY`.

Compensation is constrained: Reactor may undo local Ash persistence or manufacture another intent. It may not directly compensate an external side effect without crossing a fresh CASTLE admission + BRCE boundary and receiving a fresh receipt.

## Security/semantic projection fence

Semantic graphs contain identifiers, public classifications, evidence digests, standing, provenance and measured facts—not credentials or secret plaintext. Do not map secrets, tokens, private keys, decrypted AshCloak fields or soft-deleted records into OBDA/RDF projections. This fence is required because a semantic projection is a dissemination surface, not merely another database view.

## Acceptance

A consumer may claim the PaaS slice `ALIVE` only after:

1. pack gate returns zero violations;
2. real ggen manufacture runs twice with byte-identical consequences;
3. generated Ash resource graph compiles against the admitted Ash/AshPostgres/AshR2RML versions;
4. AshR2RML round-trip produces valid R2RML + SHACL and does not expose excluded fields;
5. Reactor refusal/rollback tests execute against the exact consumer head;
6. the CASTLE kernel adapter proves no command reaches DO without a valid BRCE prepare receipt;
7. an outcome receipt is persisted and replay-verified after observed execution.

Anything less is `PARTIAL_ALIVE`, `UNKNOWN`, `BLOCKED`, or typed `REFUSED_*` according to the missing transition.
