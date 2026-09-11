# XaaS Public Ontology Profile — Batch 1 Provenance

Fetched live this session (2026-08-20) per the "profile public ontologies first, manufacture
`xaas:` terms only where a competency question proves a gap" architecture. Each row is a real,
retrieved artifact — HTTP 200, content verified as real RDF (not an error page) before being
committed. `PARTIAL_ALIVE` as public artifacts (real, retrieved, hash-pinned); `UNKNOWN` as XaaS
foundation until qualified (logical consistency, SHACL conformance, competency-question coverage
— none of that has been run yet, this is retrieval + pinning only).

| File | Canonical vocabulary | Source URL retrieved | SHA-256 | Publisher / status |
|---|---|---|---|---|
| `odrl22.ttl` | ODRL 2.2 (Open Digital Rights Language) | `https://www.w3.org/ns/odrl/2/ODRL22.ttl` | `7895765e80d86d1d0349d945a28b8a2479f03169572345080a5b3e561ef3145` | W3C Recommendation |
| `prof.ttl` | PROF (The Profiles Vocabulary) | `https://www.w3.org/ns/dx/prof/` (content-negotiated to Turtle) | `625f8ebed133ffd393d6a664455a0cf1cf1750907f8a016fb06f928db08636d` | W3C Recommendation |
| `qudt-schema.ttl` | QUDT 2.1 (Quantities, Units, Dimensions and Types) | `http://qudt.org/2.1/schema/qudt` | `25e9d4c127f5579b3fee083870fcbc38e0e01502f581b587c771a327b17210` | QUDT.org (community standard) |
| `togaf-content-metamodel.ttl` | TOGAF 9.2 Content Metamodel Ontology v2.0.0 | `https://raw.githubusercontent.com/cadmiumkitty/togaf-content-metamodel-ontology/master/OntologyTOGAFContentMetamodelV2.ttl` | `43b36076cd147b7100cad00fc6d4f229b191b2a456bf909d6cc20b61cffe3bd` | Independent (cadmiumkitty), OWL formalization of the real TOGAF 9.2 spec — not an Open Group-published artifact itself, flagged accordingly |
| `oslc-automation.ttl` | OSLC Automation Vocabulary | `https://raw.githubusercontent.com/oasis-tcs/oslc-domains/master/auto/automation-vocab.ttl` | `e429e2b8e7410b6f9a375bd072655836fdbfe63944667909da87208d700d035` | OASIS OSLC TC |
| `oslc-config-vocab.ttl` | OSLC Configuration Management v1.0 Vocabulary | `https://docs.oasis-open-projects.org/oslc-op/config/v1.0/os/config-vocab.ttl` | `e9942d4e45278455fcc714ed6ddbd5db23bf138fe2f556f6c760de216ca19a1` | OASIS Open (Apache-2.0 licensed, per file header) |
| `oslc-rm-vocab.ttl` | OSLC Requirements Management Vocabulary | `https://raw.githubusercontent.com/oasis-tcs/oslc-domains/master/rm/requirements-management-vocab.ttl` | `b5288f0d205288347eb505a3bf8d71347b16f69c684ed1e9c8b8453c43a594c` | OASIS OSLC TC |
| `p-plan.owl` | P-PLAN (Provenance of Plans) | `http://vocab.linkeddata.es/p-plan/p-plan.owl` | `b426b2b8471f41a337256d3248fc0f595be8bc83e3969ac27c1dc51f689c5b3` | Linked Data Spain / academic W3C-adjacent vocabulary, extends PROV-O |
| `fno.ttl` | FnO (The Function Ontology) | `https://github.com/IDLabResearch/function-ontology/raw/master/fno.ttl` | `2b3b512807d8ce5df5c15a7dac4751dff09c5af46731ccd8693ee24409f28c5` | IDLab (Ghent Univ. / imec) |

## What was attempted and not obtained this pass (disclosed, not silently dropped)

- **GeoSPARQL 1.1** (`geo.ttl`) — every URL tried this session 404'd (`raw.githubusercontent.com/
  opengeospatial/ogc-geosparql/{master,main}/geo.ttl`, the GitHub-Pages-served
  `geosparql11/geo.ttl`, the `schemas.opengis.net` path). The OGC repository's real file path
  needs to be re-located (likely renamed/moved since the search-engine-cached links were
  indexed) — real follow-on work, not abandoned.
- **CoCoOn** (Cloud Computing Ontology, cited by the user's ChatGPT-perspective message as
  `PARTIAL_ALIVE` and an important IaaS/PaaS/SaaS candidate) — not fetched this pass; the only
  located reference was a PDF paper (`users.cecs.anu.edu.au/~u5170295/papers/iswc-zhang-2019.pdf`),
  not a machine-readable OWL file with a stable public URL. Needs a real download-URL search
  before it can be pinned, not assumed absent.
- **NML, INDL, OMN** — cited by the same message as strong infrastructure-topology/federation
  candidates. Not fetched this pass (real academic/OGF artifacts with less certain stable-URL
  availability than the W3C/OASIS ones above) — flagged as the next real fetch target, not dropped.
- **DCAT 3, SOSA, OWL-Time, SPDX, PROV-O, ORG, SKOS, FOAF, GoodRelations, Dublin Core, Schema.org**
  — already present in `~/ggen-marketplace/ontologies/public/` from prior sessions, confirmed by
  directory listing before this batch started; not re-fetched.

## Not yet done (explicitly, per the profile-first architecture)

No qualification has been run: no logical-consistency check, no SHACL conformance check, no
namespace-collision check, no competency-question coverage test against
`ontology/platform-console-capabilities.ttl`'s 44 `ce:Capability` individuals. This batch is
retrieval + hash-pinning only — the `packs/xaas-public-ontology-profile/` pack (locks/, gates/,
queries/competency/) is the next real step, not yet built.
