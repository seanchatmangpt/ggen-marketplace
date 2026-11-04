
## kmip

PARTIAL_ALIVE. Authored /Users/sac/ggen-marketplace/packs/smalt-core-pack/ontology/kmip.ttl (21 triples, rdflib parse exit 0): minimal KMIP v1.4 mini-ontology at namespace http://docs.oasis-open.org/kmip/ns/v1.4# covering exactly the admission-shape surface — kmip:ManagedObject class, kmip:SecretData and kmip:SymmetricKey subclasses, and kmip:state as an xsd:string datatype property with the five State enumeration values (PreActive/Active/Deactivated/Compromised/Destroyed, KMIP v1.4 §3.1.2) documented in rdfs:comment including the SHACL-visible sh:in/sh:datatype/sh:maxCount expectation. Provenance header states derivation from OASIS KMIP v1.4 spec text and that the encoding is NOT an official OASIS artifact (no official RDF encoding exists). PARTIAL not ALIVE: the TTL parses and carries the full shape-consumed surface, but no shape/template yet validates against it via pyshacl and no ggen projection consumes it — both are other lanes/next step.

## dcterms
Vendored official DCMI Metadata Terms as `ontology/dcterms.ttl` (ALIVE). Source: `https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.rdf` (official RDF/XML, 128199 bytes, fetched 2026-10-30), converted RDF/XML -> Turtle via python3 rdflib `Graph.serialize(format="turtle")` (700 triples, round-trip parse-verified); PROVENANCE header prepended, body unmodified. Gate: rdflib parse exit 0 with 700 triples; `dcterms:identifier` and `dcterms:temporal` both declared as `rdf:Property` (8 triples each, verified via `g.triples`); grep confirms both declarations at lines 695/738. Terms required by shapes/ (dcterms:identifier, dcterms:temporal) are present; ggen.toml/shapes untouched (lane-exclusive file only).
## org
STATUS: PARTIAL. Vendored the official W3C ORG vocabulary verbatim from https://www.w3.org/ns/org.ttl (v0.8) into `ontology/org.ttl` behind a PROVENANCE header (upstream sha256 `3e01f89a17475a88f8b1606ca0fae04800d34dbbf93adc6db12dc30929848729`, fetched 2026-10-30). Gate passed: `python3 rdflib` parse exit 0 (748 triples) and grep confirms `org:OrganizationalUnit a owl:Class` declared. Divergence: the W3C vocabulary declares NO lowercase `org:organizationalUnit` property — only the class `org:OrganizationalUnit` (with `org:hasUnit`/`org:unitOf` as the unit-containment properties). Rather than invent a term inside a verbatim vendor file, the class is vendored as-is; any admission shape referencing `org:organizationalUnit` (lowercase) will not resolve against this ontology and needs either a rename to `org:OrganizationalUnit`/`org:hasUnit` or a local extension term outside this file. Evidence: rdflib parse exit 0, grep count 1 for the class declaration; upstream sha256 recorded above.

## rbac

`ontology/rbac.ttl` (lane V-RBAC, 2026-10-30) — minimal rbac: mini-ontology,
namespace `http://csrc.nist.gov/ns/rbac#`, projecting the NIST RBAC reference
model (INCITS 359-2012; FIPS 199-adjacent): classes Subject, Role, Permission,
Operation, Object; object properties role (Subject→Role), permission
(Role→Permission), operation (Permission→Operation), object
(Permission→Object). PROVENANCE: derived from the NIST RBAC model — NOT an
official NIST artifact, no W3C ratification (community encodings such as UMBC
ebiquity OWL-RBAC exist but no ratified W3C artifact). Standing: ALIVE —
evidence: `python3` rdflib 7.6.0 parse of
`/Users/sac/ggen-marketplace/packs/smalt-core-pack/ontology/rbac.ttl`
returned 39 triples, exit 0; 5 owl:Class and 4 owl:ObjectProperty terms
present.

## cimi

`ontology/cimi.ttl` vendors a minimal CIMI mini-ontology (namespace `http://schemas.dmtf.org/cimi/2/`) derived by lane V-CIMI from DMTF DSP0263 text — DMTF publishes no official RDF encoding, so this is a derived work, not an official DMTF artifact (declared in the file PROVENANCE header). Coverage is restricted to the smalt core surface: `cimi:Resource` with common attributes (`id`, `name`, `state`), the Volume family (`cimi:Volume`, `cimi:VolumeConfiguration`, `cimi:VolumeImage`, `cimi:VolumeTemplate`, plus referenced `cimi:Machine`), the `volumeConfig`/`volumeImage` reference properties, and the DSP0263 lifecycle `state` vocabulary as `cimi:State` individuals (CREATING, AVAILABLE, STARTING, STOPPED, STOPPING, DELETING, ERROR). Gate: rdflib parse exit 0 (76 triples, 2026-10-30).

## wac

`ontology/wac.ttl` vendors the official W3C Web Access Control (ACL) vocabulary verbatim (namespace `http://www.w3.org/ns/auth/acl#`), fetched from https://www.w3.org/ns/auth/acl via content negotiation (`Accept: text/turtle`) on 2026-10-30, SHA256 `7d555d5c4b11101e4e2bc583c7d8adb6ae35c8552fe406794f828bfa5014d1ce`, delimited by `# VERBATIM-BEGIN`/`# VERBATIM-END` under a PROVENANCE header. One marked LOCAL EXTENSION follows the verbatim block: `acl:Mode a rdfs:Class` — the W3C document defines no `acl:Mode` (modes are the classes Read/Write/Append/Control under `acl:Access`), so it is declared locally so shape references resolve, with removal instructions in-file. Coverage: all 9 terms needed by the shapes — `acl:Authorization`, `acl:agent`, `acl:accessTo`, `acl:mode`, `acl:Mode`, and mode classes `acl:Read`/`Write`/`Append`/`Control` — confirmed present as graph subjects. Gate: rdflib parse exit 0 (97 triples incl. provenance-stripped comments; 2026-10-30). Status: ALIVE.

## tosca

V-TOSCA lane (2026-10-30): vendored the SODALITE EU TOSCA OWL ontology (DUL-grounded, the established RDF encoding — OASIS TOSCA YAML 1.3 has no official RDF) VERBATIM into `ontology/tosca.ttl` from SODALITE-EU/semantic-models `ontology definitions/tosca-builtins.ttl` @master (retrieved 2026-10-30, Apache-2.0; verified byte-identical by diff except one added trailing newline, disclosed in the in-file PROVENANCE header). Appended a clearly-marked LOCAL EXTENSION block defining `tosca.capabilities.Container.Application`, `tosca.capabilities.Container.Runtime`, `tosca.nodes.Storage.ObjectStorage` and `tosca.relationships.ConnectsTo` — referenced by the operator's admission shapes but absent from the vendored artifact — derived from OASIS TOSCA Simple Profile 1.3 text, declared not-official-RDF. Gate: `python3 -c rdflib parse` exit 0, 1434 triples, all eight referenced terms present (Container.Application, Container.Runtime, nodes.Storage.ObjectStorage, relationships.ConnectsTo/HostedOn/DependsOn, nodes.Root, capabilities.Container). Status: ALIVE.

## security

V-SEC lane (2026-10-30): vendored the official W3C Security Vocabulary VERBATIM into `ontology/security.ttl` from https://w3id.org/security via content negotiation (`Accept: text/turtle`; direct-URL fetch confirmed 200 text/turtle), retrieved 2026-10-30, SHA256 `e446e484b2fd43df9cb2a2c69b735ffa245dfc12f1d9b9305a98ac5e376a9f70` (vocab dc:date 2025-04-11), delimited by `# VERBATIM-BEGIN`/`# VERBATIM-END` under a PROVENANCE header. Term finding: the current W3C vocabulary defines NO plain `sec:digest` datatype property — the only digest term is `sec:digestMultibase` (itself feature-at-risk); the legacy CCG/Web-Payments `sec:digest` (hex xsd:string) is absent. Following the wac.ttl precedent, a clearly-marked LOCAL EXTENSION block after the verbatim body declares `sec:digest a rdf:Property, owl:DatatypeProperty ; rdfs:range xsd:string` with in-file guidance that new work SHOULD use `sec:digestMultibase` and shapes should migrate; the extension is removable once shapes move. Gate: `python3` rdflib 7.x parse exit 0 (616 triples); `sec:digest` confirmed as owl:DatatypeProperty with range xsd:string and `sec:digestMultibase` present as graph subject (2026-10-30). Status: ALIVE.

## occi

ALIVE. Vendored OGF OCCI 1.2 as RDF at `ontology/occi.ttl` (parse gate: `python3 rdflib` exit 0, 163 triples, 2026-10-30). No official fetchable RDF/OWL rendering was reachable, so the file is hand-vendored with a PROVENANCE header: occiware/occi-schemas ships XML Schema only (schemas/http%3A%2F%2Fschemas.ogf.org%2Focci%2Fcore%23.xml), occiware/occi-wg contains LaTeX only (no .owl/.ttl in the tree), and schemas.ogf.org serves no OWL at its category scheme URIs. Content: core model per GFD.183 (Entity, Resource, Link, Category, Kind, Mixin, Action, Attribute + title/summary/attributes/applies/depends/source/target) and infrastructure per GFD.181 (compute/storage/network/storagelink/networkinterface kinds, their attribute sets, and start/stop/restart/online/offline/up/down/link actions). Canonical OCCI category scheme URIs (`http://schemas.ogf.org/occi/core#`, `.../infrastructure#`) preserved verbatim so scheme+term identifiers stay in-source.
