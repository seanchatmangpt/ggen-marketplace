# ggen-marketplace LinkedIn RevOps Strategy

## Standing and claim ceiling

`ggen-marketplace` owns reusable ontology-backed manufacturing packs. For the LinkedIn RevOps program its role is **CONSTRUCT / PACK AUTHORITY**, not live LinkedIn publication, CRM actuation, or sales decision authority.

The strategy is to encode the recurring semantics and projections once and manufacture consumer-specific artifacts for `linkedin-public-canon`, `revops`, BusinessOS, GoHighLevel bridges, process-intelligence, wasm4pm, and the Chatman ecosystem composition root.

## Proposed pack

Canonical package identity:

```text
ggen-linkedin-revops-pack
```

The pack should model the portable revenue ontology and generate bounded consumer artifacts without making any vendor the semantic source of truth.

## Canonical graph

Core classes/roles:

```text
Person
Account
Campaign
ContentAsset
EvidenceClaim
PublicationIntent
PublicationEvent
Signal
Assessment
Problem
Capability
Opportunity
Experiment
Outcome
Receipt
QualificationState
```

Core transitions:

```text
ContentConstructed
PublicationObserved
LeadCaptured
AssessmentCompleted
MQLAdmitted
SQLAdmitted
POVProposed
POVAccepted
POVExecuted
OutcomeVerified
CustomerWon
ExpansionObserved
```

Prefer public semantics such as PROV-O, DCTERMS, DCAT where applicable, FOAF/ORG for people/organizations, SKOS for controlled vocabularies, ODRL for policy where useful, SHACL for constraints, and OCEL-compatible event/object semantics. Private terms should cover only genuine uncovered concepts.

## Projections

The pack should be capable of manufacturing:

| Consumer | Projection |
|---|---|
| linkedin-public-canon | publication-registry schema + campaign asset metadata |
| revops | assessment/scoring schema + handoff envelope |
| BusinessOS | CRM/account/opportunity mapping |
| GHL bridge | vendor field/resource mapping |
| process-intelligence | reference process + conformance fixtures |
| wasm4pm | OCEL fixture/schema + analytical profile |
| chatman-ecosystem | capability/standing/relationship catalog entries |

Generated artifacts are consequences of the pack and must not become second hand-edited sources of truth.

## Challenger Sale model

Encode the commercial teaching model explicitly:

```text
Teach
-> Tailor
-> TakeControl
-> DiagnoseProblem
-> DefineConsequence
-> EstablishAuthorityPath
-> DefineFalsifiableOutcome
-> ProposePOV
```

A `SQLAdmitted` shape should require the bounded subject/problem, pain, consequence, authority path, and falsifiable outcome. Engagement alone must not satisfy the shape.

## August 31 campaign profile

Provide a `10k_august_2026` example/fixture showing:

```yaml
source: linkedin
campaign: 10k_august_2026
asset: software_manufacturing_readiness_index
teaching_thesis: synchronization_tax
cta: readiness_assessment
```

The fixture should demonstrate projection across publication, lead capture, CRM, process evidence, and revenue attribution without containing real PII or credentials.

## Authority law

The pack may manufacture `PublicationIntent`, `CRMMutationIntent`, `OutboundMessageIntent`, or `MeetingIntent`. It may not grant DO authority.

```text
pack generation != LinkedIn authority
pack generation != CRM authority
pack generation != customer authority
```

Consumer runtimes must bind exact subject, intent digest, scope, authority identity, consequence, and receipt where consequential execution occurs.

## Admission gates

Required pack gates should include:

- stable IDs for Campaign, ContentAsset, Account, Opportunity, Experiment and Outcome;
- provenance for quantitative EvidenceClaims;
- no `SQLAdmitted` without required qualification evidence;
- no `CustomerWon` without an observed commercial outcome;
- no revenue attribution without Campaign/ContentAsset lineage;
- no publication event inferred from a draft or intent;
- no secrets/PII in example receipts;
- deterministic projection/replay for fixtures.

## Next admitted increments

1. Create `packs/ggen-linkedin-revops-pack/` with manifest and canonical RDF ontology.
2. Add SHACL qualification, attribution, and authority shapes.
3. Add the August 31 synthetic campaign fixture.
4. Add projections for publication registry, generic RevOps handoff, BusinessOS CRM and GHL mapping.
5. Add OCEL/process-intelligence projections for funnel discovery and conformance.
6. Add independent pack verifier and deterministic two-pass generation test.
7. Add the pack to marketplace catalog/validation only after it satisfies repository pack admission.

## Falsifiers

The pack should be refused if it duplicates public ontology unnecessarily, embeds vendor semantics into the canonical graph, grants actuation authority, cannot reproduce projections deterministically, or allows commercial stage promotion without evidence.

The pack succeeds when one admitted semantic change can update every RevOps projection without manual synchronization.
