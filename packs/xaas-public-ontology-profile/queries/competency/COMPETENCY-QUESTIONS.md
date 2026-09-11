# XaaS Competency Questions (CQ01–CQ20)

> Status: **NOT YET RUN**. These questions are stated so that any future `xaas:`-native term must
> point to a specific CQ it satisfies that no public term in `profile.ttl`'s composed ontologies
> could answer — per `gates/010_no_native_xaas_terms.rq`, which refuses native terms until this
> check exists. Each row below is a question, a current candidate public term (a hypothesis to
> test, not an asserted answer), and a real status.

| ID | Question | Candidate public term(s) (hypothesis, unproven) | Status |
|---|---|---|---|
| CQ01 | What service/capability is being offered? | `dcat:Resource`, `fno:Function` | UNCHECKED |
| CQ02 | What does it require and what does it provide? | `fno:Parameter`/`fno:Output` | UNCHECKED |
| CQ03 | Which implementations can realize it? | `fno:implementation` | UNCHECKED |
| CQ04 | Which implementation was selected? | `fno:Execution`, `prov:Activity` | UNCHECKED |
| CQ05 | What compute/network/storage topology realizes it? | none identified yet (NML/INDL not fetched) | UNCHECKED, likely gap |
| CQ06 | Which provider/region/zone/jurisdiction contains it? | GeoSPARQL (not fetched) | UNCHECKED, likely gap |
| CQ07 | Who owns, provides, operates, administers and consumes it? | `org:Organization`, `org:Role`, `org:membership` | UNCHECKED |
| CQ08 | What permission/prohibition/duty constrains it? | `odrl:Permission`/`Prohibition`/`Duty` | UNCHECKED |
| CQ09 | Who possesses actual authority to actuate it? | none proven — explicitly NOT `odrl:Permission` per `profile.ttl`'s own caveat | UNCHECKED, real open question |
| CQ10 | What observations demonstrate its current state? | `sosa:Observation` | UNCHECKED |
| CQ11 | What measurements, units, SLI/SLOs and quality claims apply? | `qudt:Quantity`/`qudt:Unit` | UNCHECKED |
| CQ12 | What plan was intended and what execution actually occurred? | `pplan:Plan`/`pplan:Step` → `prov:Activity` | UNCHECKED |
| CQ13 | What source/build/software artifacts resulted? | `spdx:Package`/`spdx:File` | UNCHECKED |
| CQ14 | What did it cost, in what unit, for what consumption? | GoodRelations + QUDT + FOCUS (FOCUS not RDF — MAP not admit) | UNCHECKED |
| CQ15 | What data/security/privacy/compliance obligations apply? | DPV, UCO (UCO present in `ontologies/public/uco/`, DPV not fetched) | UNCHECKED |
| CQ16 | What interface/property/action/event exposes the capability? | WoT Thing Description (not fetched) | UNCHECKED, likely gap |
| CQ17 | Which semantic fact caused which generated artifact fragment? | `prov:wasGeneratedBy`/`prov:used` | UNCHECKED |
| CQ18 | Which renderer/projector generated Terraform/Erlang/etc.? | `prov:Agent`/`prov:SoftwareAgent` | UNCHECKED |
| CQ19 | What receipt binds actuation to the admitted intent? | `prov:Entity` + SPDX + cryptographic identity (composition hypothesis, per the reframe doc) | UNCHECKED |
| CQ20 | Can that receipt be deterministically replayed and verified? | none identified yet | UNCHECKED, likely gap |

## Addendum: economic-agency competency questions (CQ21–CQ28, not yet incorporated)

A further reframe (recorded, not yet acted on): businesses should be modeled as **emergent,
receipted value-exchange loops over the ontology** — `B = (C, R, A, E, V, P)` (capabilities,
resources, authorities, exchanges, value/objectives, policies), closing through actuation
(`B_semantic --μ--> B_operational`) — not hand-designed institutions automated after the fact.
Under that framing, `BusinessType = Query(O*)` (e.g. "consulting firm" is a graph pattern:
`hasOffering → realizes ExpertCapability → delivery requires KnowledgeWork → consideration is
Fee`), not a template. This expands the competency-question set beyond infrastructure into
commerce/economic-agency domains:

| ID | Question | Candidate public term(s) (hypothesis, unproven) |
|---|---|---|
| CQ21 | What demand/need/intent triggers a candidate value loop? | none identified yet — real gap candidate |
| CQ22 | What offering/price/quote/order/transaction models the exchange? | `gr:Offering` (GoodRelations, already present), QUDT for price units |
| CQ23 | What contract/obligation/right/duty binds the parties? | `odrl:Duty`, FIBO (not fetched) |
| CQ24 | What accounting event (asset/liability/revenue/expense) results? | REA (Resource-Event-Agent, not fetched), FIBO |
| CQ25 | What jurisdiction/tax-nexus/taxable-event applies? | none identified yet — real gap candidate |
| CQ26 | What risk/exposure/control/residual-risk applies to the loop? | UCO (present), AIRO (not fetched, AI-risk specific) |
| CQ27 | Who legally/naturally bears authority to bind/mutate/transfer? | `org:Role`, ODRL — same CQ09 open question, economic-authority-scoped |
| CQ28 | Does the loop remain economically viable (positive unit economics) over observed cycles? | QUDT (quantities) + `prov:` (observation over time) — likely composition, unproven |

This addendum is recorded per the reframe; it has not been merged into the CQ01-CQ20 numbering or
run. `REA` (Resource-Event-Agent, the classical economic-exchange ontology) and `FIBO` (already
vendored at `ontologies/public/fibo/`, not yet checked against these questions) are the next real
fetch/check targets for this addendum, not GoodRelations/FIBO substitutes invented here.

## How this gets run (not yet done)

For each CQ: write a real SPARQL query against the composed profile graph (`profile.ttl` +
imported public ontologies), attempt to answer it using only the candidate public terms, and
record PASS (public terms answer it) / GAP (no public term answers it — only then is a native
`xaas:` term justified) / PARTIAL (answers part of the question). CQ05, CQ06, CQ16, CQ20 already
look like likely gaps given the ontologies not yet fetched (NML/INDL, GeoSPARQL, WoT TD) — but
"likely gap" is not the same as a run check, and is stated as a hypothesis here, not a conclusion.
