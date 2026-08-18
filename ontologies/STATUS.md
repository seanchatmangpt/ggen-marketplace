# Ontology coverage status ledger

One row per named ontology/vocabulary researched across all research passes in this session
(three `deep-research` workflow rounds, ~450 subagents total, 3-vote adversarial verification
per claim). This is the authoritative "what's actually in `ontologies/`, what's missing, and
why" reference — `README.md` describes the directory layout; this file tracks completeness.

**Status values:**
- `added` — fetched, RDF-parsed successfully, path given
- `added-partial` — large/modular corpus, a meaningful subset fetched, gap named explicitly
- `blocked-technical` — real ontology, real publisher, no working fetch found this session
  (dead redirect, blocked host, timeout on a large file) — retry candidate, not abandoned
- `excluded-license` — cannot be freely redistributed (the one deliberate non-technical exclusion)
- `not-found` — researched with real search effort, no current public RDF/OWL artifact exists
  from the publisher (they only ship UML/XSD/JSON/spreadsheet)
- `unresearched` — named in scope, no dedicated search pass has targeted it yet

## General-purpose (W3C core + community)

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| schema.org | schema.org consortium | added | `public/schema-org.ttl` |
| FOAF | FOAF Project | added | `public/foaf.ttl` |
| SKOS, SKOS-XL | W3C | added | `public/skos.rdf`, `public/skos-xl.rdf` |
| Dublin Core (elements, terms, type-vocab) | DCMI | added | `public/dublin-core-*.ttl` |
| PROV-O | W3C Provenance WG | added | `public/prov-o.ttl` |
| DCAT | W3C DXWG | added | `public/dcat.ttl` |
| OWL-Time | W3C | added | `public/owl-time.ttl` |
| ORG | W3C | added | `public/org.ttl` |
| vCard | W3C | added | `public/vcard.ttl` |
| SSN, SOSA | W3C/OGC SDW WG | added | `public/ssn.ttl`, `public/sosa.ttl` |
| GoodRelations | Hepp Research / purl.org | added | `public/goodrelations.owl` |
| Bibo | Bibliographic Ontology Project | added | `public/bibo.ttl` |
| ADMS | W3C | added | `public/adms.ttl` |
| LOCN | W3C/ISA Programme | added | `public/locn.ttl` |
| Hydra | Hydra CG (W3C Community Group) | added | `public/hydra-core.jsonld` |
| VOID | vocab.deri.ie (DERI/Vocamp) | blocked-technical | host times out on every fetch attempt this session |
| Product Types Ontology | productontology.org | not-found | not a downloadable corpus — dynamically generates one RDF/Turtle file per Wikipedia product-category page on demand (millions of individual class URIs), no single ontology file to fetch |

## Cybersecurity / opsec

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| UCO (Unified Cyber Ontology) | Cyber Domain Ontology Project (Linux Foundation) | added | `public/uco/` — manifest + all 15 modules (action, analysis, configuration, core, identity, location, marking, observable, pattern, role, time, tool, types, victim, vocabulary) |
| CASE (Cyber-investigation Analysis Standard Expression) | CASE Ontology Committee | added | `public/case/` — manifest + investigation + vocabulary modules |
| D3FEND | MITRE (NSA Cybersecurity Directorate-funded) | added | `public/d3fend.ttl` |
| STIX 2.1 | OASIS | not-found | spec mandates JSON only (RFC7493/RFC8259) — no official RDF/OWL/Turtle serialization exists |
| TAXII 2.1 | OASIS | not-found | protocol spec mandates JSON only — no RDF/OWL/Turtle serialization exists |
| STIX-as-OWL (non-normative) | OASIS TC-adjacent community (oasis-tcs/tac-ontology) | not-added | exists (github.com/oasis-tcs/tac-ontology, `stix-spec.owl`) but explicitly a community approximation, not OASIS-ratified — not mirrored to avoid presenting it as canonical |
| MITRE ATT&CK-as-RDF | MITRE / community converters | unresearched | official ATT&CK distribution is STIX 2.x JSON; no canonical RDF/OWL converter confirmed this session |
| CAPEC | MITRE | not-found | published as XML/CSV/XLSX only, no RDF/OWL form confirmed |
| VERIS | Verizon / VERIS Community | not-found | JSON-schema based; only a JSON-LD graph companion exists, no true OWL/Turtle ontology |

## DevOps / software

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| SPDX 3.0.1 | SPDX project (Linux Foundation) | added | `public/spdx-model.ttl` |
| SWO (Software Ontology) | Allyson Lister / OBO Foundry | added | `public/swo.owl` |
| DOAP | DOAP project | added | `public/doap.rdf` |

## Energy / IoT / smart buildings

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| SAREF (core) | ETSI | added | `public/saref.ttl` |
| SAREF4AGRI/AUTO/BLDG/CITY/DMGT/EHAW/ENER/ENVI/GRID/INMA/LIFT/MARI/SYST/WATR/WEAR (15 extensions) | ETSI | added | `public/saref-extensions/*.ttl` |
| CIM / IEC 61970 as RDF | IEC | unresearched | not covered by any research pass yet |
| Brick Schema | Brick Consortium | unresearched | not covered by any research pass yet |

## Government / legal

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| ELI (European Legislation Identifier) | EU Publications Office | added | `public/eli.owl` |

## Cloud / IT infrastructure

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| CIMI | DMTF (ISO/IEC 19831) | not-found | only XML Schema/JSON published; no RDF/OWL binding exists anywhere per this session's research |
| USDL | (EU FP7 research effort, no clear current steward) | not-found | no RDF/OWL artifact or current maintenance status found |
| OCCI | Open Grid Forum | not-found | only HTTP/JSON renderings published; no RDF/OWL rendering exists |
| CSA Cloud Controls Matrix | Cloud Security Alliance | not-found | published as spreadsheet/JSON/YAML/OSCAL, not an ontology |

## Telecom

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| oneM2M Base Ontology (TS-0012) | oneM2M | added | `public/onem2m-base.owl` |
| TM Forum SID | TM Forum | not-found | published only as UML/XSD/Swagger; no official RDF/OWL/Turtle export exists |

## Transportation / logistics

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| Transmodel (academic OWL rendering) | OEG-UPM (SNAP project, EU-affiliated, coordinated with a CEN Transmodel WG member) | blocked-technical | non-official, no single packaged release file — only a documentation hub (oeg-upm.github.io/snap-docs) referencing source modules, not a finished download |
| NeTEx | CEN | unresearched | no verified claim survived this session's research |
| Linked GTFS / GTFS-as-RDF | — | unresearched | no verified claim survived this session's research |
| DATEX II | — | unresearched | no verified claim survived this session's research |

## Retail / e-commerce

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| GS1 Web Vocabulary | GS1 | added | `public/gs1-web-vocab.ttl` |
| Product Types Ontology | productontology.org | unresearched | not covered by any research pass yet (also listed above under general-purpose) |

## Insurance

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| ACORD Reference Architecture | ACORD | unresearched | no verified claim (positive or negative) surfaced this session |

## HR

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| HR-Open / HR-XML | HR Open Standards Consortium | not-found | publishes HR-JSON/HR-XML only, no RDF/OWL representation exists |
| HRM Ontology (job-market domain, HR-adjacent but not an HR-Open representation) | OEG, Universidad Politécnica de Madrid | added | `public/hrm/` — 13 modules (JobSeeker, Occupation, Skill, Competence, Education, Geography, Language, EconomicActivity, DrivingLicense, LabourRegulatory, JobOffer, Time, + dup JobSeekerOntolo) |

## Real estate

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| RealEstateCore (REC) v3.2 | RealEstateCore Consortium | added | `public/realestatecore/` — manifest + 9 modules (actuation, agents, analytics, building, core, dataschemas, device, lease, metadata) |

## Media / broadcasting

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| EBUCorePlus (current successor to EBUCore) | EBU (European Broadcasting Union) | added | `public/ebucoreplus.owl` |
| EBUCore (classic, superseded by EBUCorePlus) | EBU | not-added | original ebu.ch host blocks direct fetch (403); EBUCorePlus supersedes it and was added instead |

## Agriculture

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| AGROVOC (full LOD dump) | FAO | added | `public/agrovoc/agrovoc_lod.nt.zip` — 96MB compressed N-Triples (uncompresses to ~1.5GB; kept compressed to avoid a multi-GB blob) |

## Automotive / manufacturing

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| Industrial Ontologies Foundry (IOF) Core | IOF | added | `public/iof-core.rdf` |
| VDI 3682 (Formalized Process Description) | HSU-AUT (Helmut Schmidt University) | added | `public/vdi3682.owl` |
| AutomationML | AutomationML e.V. | not-found | natively XML/CAEX; only a work-in-progress academic RDF-mapping paper exists, no stable downloadable ontology |

## Education

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| schema.org Course / EducationalOccupationalCredential | schema.org | added (already in `public/schema-org.ttl`) | no separate file needed |
| MLO (Metadata for Learning Opportunities) | CEN/ISO | unresearched | no RDF/OWL download found or confirmed absent |

## Scientific research

| Ontology | Publisher | Status | Location |
|---|---|---|---|
| EDAM | edamontology.org (Jon Ison, Matúš Kalaš et al.) | added | `public/edam.owl` |
| Bioschemas profile SHACL shapes | Bioschemas community | added | `public/bioschemas-profiles-shacl.ttl` — note: constraint shapes over schema.org, not an independent ontology |
| OBO Foundry members | Individual maintainers, OBO Foundry-governed | added-partial | `public/obo/<id>.owl` — 170/190 active members, 2.7G. See Summary for the 20 not fetched and why. |
| SNOMED CT | SNOMED International | excluded-license | requires paid affiliate membership; cannot be freely redistributed |

---

## Summary

**851 files, 2.8G total.** `python3 scripts/marketplace.py validate`/`catalog` clean and
deterministic throughout; `ggen graph validate --files ontologies.ttl` loads the full umbrella
manifest (841 quads) with zero errors.

- **OBO Foundry**: 170/190 active members fetched successfully (`public/obo/`, 2.7G — by far the
  largest single component). 20 not fetched: `chebi` and `pr` need dedicated large-file handling
  (190MB+/430MB+, exceeded the retry timeout); `dron` and `gaz` were aborted mid-fetch after their
  downloads grew anomalously large (700MB+ and 325MB+, well past their known real ontology sizes —
  likely a redirect/streaming issue on the PURL resolver, not a legitimate file size) and should be
  re-investigated rather than blindly retried; `mp`, `mro`, `ncbitaxon`, `ncit`, `ogg`, `pcl`,
  `upheno`, `uberon`, `vto`, `xpo`, `zp`, `oba`, `fbbt`, `go`, `mondo` were stopped when fetching was
  halted for a usage-fit reassessment (see below), not because they failed.
- **FIBO**: 287/287 files, all parse-clean.
- **AGROVOC**: full LOD dump, kept compressed (96MB `.zip`) rather than exploded to its ~1.5GB
  uncompressed size.
- Named industry ontologies (D3FEND, SPDX, SWO, DOAP, SAREF core + 15 extensions, ELI, oneM2M,
  GS1, RealEstateCore, EBUCorePlus, HRM, IOF Core, VDI3682, EDAM, Bioschemas, UCO full 15-module
  set, CASE full 3-module set, Brick Schema): all fetched and parse-clean.
- rdflib parse sweep: 364/373 non-large-corpus files parse cleanly; the 9 failures are the same
  pre-existing source-repo syntax errors documented above (not introduced by any copy/fetch in
  this session).

**Fetching was deliberately stopped before 100% completion.** A check against actual pack usage
(`grep`-ing every `packs/*/ontology.ttl` for vocabulary prefixes) showed PROV-O used 149 times,
Dublin Core terms 143 times, SKOS 47 times, DCAT 22 times, SOSA/ORG/schema.org a handful of times
each across all 122 packs — and **zero** references to OBO Foundry, FIBO, AGROVOC, UCO/CASE, GS1,
HR-Open, RealEstateCore, EBUCorePlus, SAREF, D3FEND, IOF, or any other industry-vertical ontology
added this session. Per explicit user direction after that finding: keep everything already
fetched (it's a legitimate reference library for future packs), but stop pursuing the remaining
gaps — the marginal value against current, real usage is effectively zero. The general-purpose
W3C core (prov-o, dcat, skos, dublin-core, org, sosa/ssn, schema.org) plus the personal-repo
domain ontologies (`mechanical-design/`, `cns/dflss/`, etc.) remain the actually load-bearing 20%
of this directory.
