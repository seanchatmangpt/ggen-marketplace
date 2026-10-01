# Reference: enterprise operating model contract

Exact contract of `enterprise-operating-model-pack` (CapabilityPack). It models an enterprise operating-model decision, the foundation for execution that decision requires, four maturity stages, an engagement model, the order and artifact kinds of the architecture development method (ADM), and value-stream anchoring. It manufactures strategy-derived requirements and pending-approval building-block skeletons for [industry-closure-ledger-pack](industry-closure-contract.md).

This page is a reference. For learning see [Generate an industry closure](../tutorials/generate-an-industry-closure.md); for tasks see [Add an industry to a closure](../how-to/add-an-industry-to-closure.md); for rationale and what is interpretation versus source see [Industry closure as architecture strategy](../explanation/industry-closure-as-architecture-strategy.md).

Where this page and a source file differ, the source wins and this page is repaired. No ggen release, commit, digest or timeout value is recorded here.

## Scope, authority and non-goals

- Gates and queries SELECT; templates CONSTRUCT candidate Turtle. No DO individual, class or property is declared in this namespace, and gate `080_authority_fence.rq` refuses a DO ceiling, claim or grant.
- Authority literals are `NONE`, `OBSERVE`, `SELECT`, `CONSTRUCT`. Generated contract skeletons claim `NONE` and standing `UNKNOWN`.
- Non-goals: the pack does not prove strategic fit, decomposition adequacy, native runtime success, external observations or customer outcomes. It does not own ADM phase identity, operating-model identity, maturity-stage identity or engagement-mechanism identity (those are owned by `togaf-adm-pack`), the building-block and contract vocabulary (owned by `enterprise-architecture-pack`), or the standing ladder (owned by [Standing](standing.md)).
- It does not merge or edit similarly named packs. Hollow labels elsewhere in the marketplace that mention an operating model are not equivalent to this pack and are not changed.

## Notation join with togaf-adm-pack

Identity of phases, operating models, stages and engagement mechanisms stays in `togaf-adm-pack`. This pack restates only the `skos:notation` join keys it needs. A repository test compares the sets and fails on drift.

| Family | Notations restated here | Where identity lives |
|---|---|---|
| Operating models | `OM-DIVERSIFICATION`, `OM-COORDINATION`, `OM-REPLICATION`, `OM-UNIFICATION` | `togaf-adm-pack` |
| Maturity stages | `MAT-1-BUSINESS-SILOS`, `MAT-2-STANDARDIZED-TECHNOLOGY`, `MAT-3-OPTIMIZED-CORE`, `MAT-4-BUSINESS-MODULARITY` | `togaf-adm-pack` |
| ADM phases | `ADM-PRELIM`, `ADM-PHASE-A` through `ADM-PHASE-H`, `ADM-REQ-MGMT` | `togaf-adm-pack` |
| Engagement mechanisms | referenced by the `ENG-` notation prefix in instance data only (for example `ENG-ARCH-REVIEW-BOARD`, `ENG-PROJECT-FUNDING-GATE`, `ENG-COMPLIANCE-REVIEW`) | `togaf-adm-pack` |

What this pack adds on top of that identity: the axes of each operating model, the ordinal of each stage, the order of the phases and the artifact kinds each phase requires. `togaf-adm-pack` holds none of these as data.

## Vocabulary

Generated from the declarations in `packs/enterprise-operating-model-pack/ontology.ttl`. The source states each meaning; the notes after the tables add the closed individuals.

### Classes

| Term | Meaning |
|---|---|
| `eom:AdmEngagement` | One run of the architecture development method, for example one architecture project. Phase records belong to an engagement. |
| `eom:AdmPhase` | One phase of the architecture development method. Identity is the skos:notation join key shared with togaf-adm-pack. Phase order and artifact requirements are owned here because that pack holds them only as comments. |
| `eom:Artifact` | A concrete work product of a given eom:ArtifactKind. |
| `eom:ArtifactKind` | A generic, paraphrased kind of architecture work product. A stable superset, not an edition-exact catalogue. |
| `eom:CapabilityRole` | The explicit exemption vocabulary for capabilities that sit outside a value stream. |
| `eom:ComplianceCriterion` | A criterion an architecture contract skeleton carries, chosen from the operating-model axes by the generated skeleton template. |
| `eom:CoreBusinessProcess` | A process the enterprise relies on daily. Carries eom:standardVariant to say whether one enterprise-wide variant is used. |
| `eom:Dispensation` | A time-bounded, owned exemption from architecture review for a work package. |
| `eom:EngagementModel` | How enterprise-level governance, project-level governance and a linking mechanism fit together. Not an ADM run: see eom:AdmEngagement. |
| `eom:EnterpriseCapability` | Marker for a capability individual in an enterprise. Instance data types it alongside ea:Capability or togaf:Capability. It scopes gate 070 so that unrelated capabilities in a consumer graph are never refused. |
| `eom:FoundationForExecution` | The core processes, shared data and linking automation an enterprise must have to run its chosen operating model. |
| `eom:Level` | LOW or HIGH on either operating-model axis. |
| `eom:LinkingAutomation` | Automation that links processes and data. Must be realized by an architecture building block. |
| `eom:MaturityStage` | One of four ordered architecture maturity stages. Identity is the skos:notation join key shared with togaf-adm-pack. |
| `eom:ModularComponent` | A plug-and-play business component. Required by maturity stage 4 (business modularity). |
| `eom:OperatingModel` | One of four positions on the integration x standardization plane. Identity is the skos:notation join key shared with togaf-adm-pack. |
| `eom:OperatingModelDecision` | A recorded choice, for one strategy, of an operating model with its axes, foundation, engagement model, claimed maturity stage, and the industry closure it targets. |
| `eom:PhaseRecord` | The status of one ADM phase within one engagement, with the artifacts it produced. |
| `eom:RequirementsReview` | A review of requirements against an achieved phase. The requirements-management phase is continuous and needs none. |
| `eom:SharedDataDomain` | A data domain with a named owner role. eom:enterpriseScope says whether it is shared across the whole enterprise. |
| `eom:StageEvidence` | A receipted record that a decision has evidenced one maturity stage. A stage claim needs evidence for itself and every lower stage. |
| `eom:ValueStream` | An ordered flow of stages through which the enterprise delivers value. |
| `eom:ValueStreamStage` | One stage of a value stream. It enables capabilities, which anchors them to delivered value. |

### Object properties

| Term | Domain | Range | Meaning |
|---|---|---|---|
| `eom:artifactKind` | `eom:Artifact` | `eom:ArtifactKind` |  |
| `eom:atStage` | `eom:OperatingModelDecision` | `eom:MaturityStage` | The maturity stage the enterprise claims. Gate 040 requires receipted evidence for it and every lower stage. |
| `eom:capabilityRole` | any | `eom:CapabilityRole` | Explicit exemption from value-stream anchoring. |
| `eom:chosenModel` | `eom:OperatingModelDecision` | `eom:OperatingModel` | Exactly one operating model must be chosen. |
| `eom:complianceCriterion` | any | `eom:ComplianceCriterion` | Emitted on contract skeletons by the skeleton template. Chosen from the axes, not from the model name. |
| `eom:dispensation` | any | `eom:Dispensation` | An owned, expiring exemption used instead of a review. |
| `eom:enablesCapability` | `eom:ValueStreamStage` | any | The capability this stage depends on. Anchors the capability to delivered value. |
| `eom:enterpriseGovernance` | `eom:EngagementModel` | any | Enterprise-level mechanism. Must be a concept whose skos:notation starts with ENG- (join to togaf-adm-pack). |
| `eom:forDecision` | `eom:StageEvidence` | `eom:OperatingModelDecision` |  |
| `eom:forStage` | `eom:StageEvidence` | `eom:MaturityStage` |  |
| `eom:forStrategy` | `eom:OperatingModelDecision` | any | The ea:Strategy the decision answers. |
| `eom:hasCoreProcess` | `eom:FoundationForExecution` | `eom:CoreBusinessProcess` |  |
| `eom:hasEngagementModel` | `eom:OperatingModelDecision` | `eom:EngagementModel` |  |
| `eom:hasFoundation` | `eom:OperatingModelDecision` | `eom:FoundationForExecution` |  |
| `eom:hasLinkingAutomation` | `eom:FoundationForExecution` | `eom:LinkingAutomation` |  |
| `eom:hasModularComponent` | `eom:FoundationForExecution` | `eom:ModularComponent` |  |
| `eom:hasSharedData` | `eom:FoundationForExecution` | `eom:SharedDataDomain` |  |
| `eom:hasStage` | `eom:ValueStream` | `eom:ValueStreamStage` |  |
| `eom:integrationLevel` | any | `eom:Level` | Integration axis level of an operating model or a decision. |
| `eom:linkingMechanism` | `eom:EngagementModel` | any | Mechanism that links project and enterprise levels. Must be a concept whose skos:notation starts with ENG- (join to togaf-adm-pack). |
| `eom:ofEngagement` | `eom:PhaseRecord` | `eom:AdmEngagement` |  |
| `eom:ofEnterprise` | any | any | Names the enterprise a strategy, work package or capability belongs to. It is the jurisdiction marker: gates refuse only subjects that carry it (or an eom type). |
| `eom:ownedBy` | `eom:SharedDataDomain` | any | The org:Role that owns the data domain. |
| `eom:owner` | `eom:Dispensation` | any |  |
| `eom:phase` | `eom:PhaseRecord` | `eom:AdmPhase` |  |
| `eom:precedes` | `eom:AdmPhase` | `eom:AdmPhase` | Immediate predecessor relation of the ADM chain. A cycle is refused by gate 060. |
| `eom:produced` | `eom:PhaseRecord` | `eom:Artifact` |  |
| `eom:projectGovernance` | `eom:EngagementModel` | any | Project-level mechanism. Must be a concept whose skos:notation starts with ENG- (join to togaf-adm-pack). |
| `eom:realizedByABB` | `eom:LinkingAutomation` | any | The ea:ArchitectureBuildingBlock that realizes the linking automation. |
| `eom:reqMgmtReview` | `eom:PhaseRecord` | `eom:RequirementsReview` |  |
| `eom:requiresArtifactKind` | `eom:AdmPhase` | `eom:ArtifactKind` | A kind of artifact an engagement must have produced before the phase can be ACHIEVED. |
| `eom:reviewedBy` | any | any | Architecture review of a togaf:WorkPackage in an enterprise. |
| `eom:standardizationLevel` | any | `eom:Level` | Standardization axis level of an operating model or a decision. |
| `eom:supportsCapability` | any | any | Links a foundation element to the capability it supports. In a closure pipeline the capability must carry ic:capabilityKey. |
| `eom:targetClosure` | `eom:OperatingModelDecision` | any | IRI of the ic:IndustryClosure that generated requirements join. |

### Datatype properties

| Term | Domain | Range | Meaning |
|---|---|---|---|
| `eom:authorityCeiling` | any | any | Plain literal NONE, OBSERVE, SELECT or CONSTRUCT. DO is not representable (gate 080). |
| `eom:authorityClaim` | any | any | Plain literal. Generated artifacts claim NONE. DO is not representable (gate 080). |
| `eom:decisionKey` | `eom:OperatingModelDecision` | `string` | Safe key (letters, digits, dot, underscore, hyphen) used to mint requirement identifiers. Checked by gate 010. |
| `eom:elementKey` | any | `string` | Safe key of a foundation element. Used to mint requirement identifiers. Checked by gate 020. |
| `eom:enterpriseScope` | `eom:SharedDataDomain` | `boolean` | True when the data domain is shared across the whole enterprise. |
| `eom:expires` | `eom:Dispensation` | any | Expiry date of a dispensation. A dispensation without owner and expiry is refused. |
| `eom:levelCode` | `eom:Level` | `string` | LOW or HIGH, as a plain literal. Used by generation queries. |
| `eom:receiptDigest` | `eom:StageEvidence` | `string` | Plain literal of the form sha256:<64 lowercase hex>. A malformed digest does not count as evidence. |
| `eom:stageOrdinal` | `eom:MaturityStage` | `integer` | Position 1..4 of a maturity stage. Owned here: togaf-adm-pack orders stages by notation only. |
| `eom:standardVariant` | `eom:CoreBusinessProcess` | `boolean` | True when a single enterprise-wide variant of the process is used. |
| `eom:status` | `eom:PhaseRecord` | `string` | One of the plain literals NOT_STARTED, IN_PROGRESS, ACHIEVED. |
| `eom:targetBaseIri` | `eom:OperatingModelDecision` | `string` | Plain string equal to the target closure's ic:baseIri. Mints requirement and skeleton IRIs. |


### Axis levels and operating models (individuals)

| Individual | Type | Axes or code |
|---|---|---|
| `eom:LOW`, `eom:HIGH` | `eom:Level` | `eom:levelCode` is `LOW` or `HIGH` |
| `eom:Diversification` | `eom:OperatingModel` | notation `OM-DIVERSIFICATION` |
| `eom:Coordination` | `eom:OperatingModel` | notation `OM-COORDINATION` |
| `eom:Replication` | `eom:OperatingModel` | notation `OM-REPLICATION` |
| `eom:Unification` | `eom:OperatingModel` | notation `OM-UNIFICATION` |

### Axes truth table

Each operating model sits at one corner of the integration by standardization plane, and the four models cover the four corners exactly once.

| Operating model | Integration | Standardization | Foundation it demands (gate 030 interpretation) |
|---|---|---|---|
| `eom:Diversification` | `eom:LOW` | `eom:LOW` | no enterprise-scope shared data, no standard process variants |
| `eom:Coordination` | `eom:HIGH` | `eom:LOW` | enterprise-scope shared data, no standard process variants |
| `eom:Replication` | `eom:LOW` | `eom:HIGH` | standard process variants, no enterprise-scope shared data |
| `eom:Unification` | `eom:HIGH` | `eom:HIGH` | standard process variants and enterprise-scope shared data |

Axis obligations follow the decision's axes, not its model name. A decision whose chosen model disagrees with its stated axes is refused by gate 010.

### Foundation for execution

A decision links one `eom:FoundationForExecution` through `eom:hasFoundation`. The foundation has at least one core process (`eom:hasCoreProcess`), at least one shared data domain (`eom:hasSharedData`) and at least one linking automation (`eom:hasLinkingAutomation`). A stage-4 claim also needs a modular component (`eom:hasModularComponent`). Every process, data domain or linking automation carries a safe `eom:elementKey` and an `eom:supportsCapability` link to a capability that carries an industry-closure capability key. A shared data domain names an owning role. A linking automation is realized by an architecture building block.

### Maturity stages (individuals)

| Individual | Notation | Ordinal | Additional prerequisite (gate 040 interpretation) |
|---|---|---|---|
| `eom:StageBusinessSilos` | `MAT-1-BUSINESS-SILOS` | 1 | none |
| `eom:StageStandardizedTechnology` | `MAT-2-STANDARDIZED-TECHNOLOGY` | 2 | the foundation has a linking automation |
| `eom:StageOptimizedCore` | `MAT-3-OPTIMIZED-CORE` | 3 | every core process is a standard variant |
| `eom:StageBusinessModularity` | `MAT-4-BUSINESS-MODULARITY` | 4 | the foundation has a modular component |

A claim at stage n needs a receipted `eom:StageEvidence` for stage n and for every lower stage. Receipt digests are `sha256:` plus 64 lowercase hex.

### Engagement model

An `eom:EngagementModel` has an enterprise-level mechanism (`eom:enterpriseGovernance`), a project-level mechanism (`eom:projectGovernance`) and a linking mechanism (`eom:linkingMechanism`), each of which joins to an `ENG-` notation. A decision links one through `eom:hasEngagementModel`. A work package of an enterprise is reviewed (`eom:reviewedBy`) or carries an `eom:Dispensation` that has an owner and an expiry.

### Capability role, compliance criteria (individuals)

| Individual | Type | Meaning |
|---|---|---|
| `eom:ENABLING` | `eom:CapabilityRole` | explicit exemption of a capability from value-stream anchoring |
| `eom:StandardProcessVariant` | `eom:ComplianceCriterion` | emitted on a skeleton contract when standardization is HIGH |
| `eom:SharedDataContract` | `eom:ComplianceCriterion` | emitted on a skeleton contract when integration is HIGH |

### ADM phase order and artifact kinds

`eom:precedes` forms the chain from preliminary through A to H. Requirements management is continuous and sits outside the chain. Artifact kinds are generic paraphrased kinds, a stable superset, not an edition-exact list.

| Phase individual | Notation | Precedes | Required artifact kinds |
|---|---|---|---|
| `eom:AdmPrelim` | `ADM-PRELIM` | `eom:AdmPhaseA` | `eom:KindArchitecturePrinciples`, `eom:KindGovernanceModel` |
| `eom:AdmPhaseA` | `ADM-PHASE-A` | `eom:AdmPhaseB` | `eom:KindArchitectureVision`, `eom:KindStakeholderMap` |
| `eom:AdmPhaseB` | `ADM-PHASE-B` | `eom:AdmPhaseC` | `eom:KindBusinessArchitecture` |
| `eom:AdmPhaseC` | `ADM-PHASE-C` | `eom:AdmPhaseD` | `eom:KindInformationSystemsArchitecture` |
| `eom:AdmPhaseD` | `ADM-PHASE-D` | `eom:AdmPhaseE` | `eom:KindTechnologyArchitecture` |
| `eom:AdmPhaseE` | `ADM-PHASE-E` | `eom:AdmPhaseF` | `eom:KindOpportunitiesAndSolutions` |
| `eom:AdmPhaseF` | `ADM-PHASE-F` | `eom:AdmPhaseG` | `eom:KindMigrationPlan` |
| `eom:AdmPhaseG` | `ADM-PHASE-G` | `eom:AdmPhaseH` | `eom:KindComplianceAssessment` |
| `eom:AdmPhaseH` | `ADM-PHASE-H` | none | `eom:KindChangeRecord` |
| `eom:AdmReqMgmt` | `ADM-REQ-MGMT` | outside the chain | `eom:KindRequirementsRegister` |

A phase record in status `ACHIEVED` needs every artifact kind its phase requires, its predecessor phase `ACHIEVED` in the same engagement, and a requirements-management review (except for the requirements-management phase itself). Valid statuses are `NOT_STARTED`, `IN_PROGRESS` and `ACHIEVED`.

## Gates

The gate contract is the one stated in [Industry closure contract](industry-closure-contract.md): one `SELECT ?subject ?reason`, zero rows pass, any row a typed refusal, `ORDER BY ?subject ?reason`, stems of gates and witnesses corresponding exactly, and the same three enforcement layers (stem court, executing rdflib court, real-ggen qualification). The rdflib court requires the fail witness's reason set to equal the declared codes of the gate, so every code below has an executing negative witness.

Jurisdiction guard: gates act on eom-typed subjects, on `ea:Strategy` individuals that carry `eom:ofEnterprise` or that an `eom:OperatingModelDecision` answers, and on work packages of an enterprise. A foreign `ea:Strategy` that has neither is not refused; that is the one place where omitting `eom:ofEnterprise` leaves a strategy outside the gates, so a consumer must state it.

Flagged interpretation gates: `030_axis_obligations.rq` and `040_maturity_progression.rq` encode modelling interpretations, not rules quoted from any source. A consumer that disagrees with them should not use them as evidence of anything beyond internal consistency of its own decision.

| Gate | Code | Trigger |
|---|---|---|
| `010_operating_model_decision.rq` | `REFUSED:EOM_DECISION_NO_STRATEGY` | a decision answers no `ea:Strategy` |
| | `REFUSED:EOM_OM_CHOICE_MISSING` | a decision chooses no operating model |
| | `REFUSED:EOM_OM_CHOICE_AMBIGUOUS` | a decision chooses two models |
| | `REFUSED:EOM_OM_AXES_MISSING` | a decision lacks an integration or a standardization level |
| | `REFUSED:EOM_OM_AXES_INCONSISTENT` | the decision's axes differ from its chosen model's axes |
| | `REFUSED:EOM_STRATEGY_NO_OPMODEL` | a strategy of an enterprise has no decision |
| | `REFUSED:EOM_STRATEGY_NO_ENTERPRISE` | a strategy that a decision answers names no enterprise |
| | `REFUSED:EOM_PROVENANCE_MISSING` | a decision has no source |
| | `REFUSED:EOM_DECISION_KEY_UNSAFE` | the decision key is absent or not `^[A-Za-z0-9._-]+$` |
| | `REFUSED:EOM_DECISION_TARGET_INVALID` | the target closure is absent, or the target base IRI is absent or not an http(s) IRI ending in a slash or hash |
| `020_foundation_completeness.rq` | `REFUSED:EOM_FOUNDATION_NO_DECISION` | a foundation belongs to no decision |
| | `REFUSED:EOM_DECISION_NO_FOUNDATION` | a decision has no foundation |
| | `REFUSED:EOM_FOUNDATION_NO_PROCESS` | a foundation has no core process |
| | `REFUSED:EOM_FOUNDATION_NO_SHARED_DATA` | a foundation has no shared data domain |
| | `REFUSED:EOM_FOUNDATION_NO_LINKING` | a foundation has no linking automation |
| | `REFUSED:EOM_ELEMENT_NO_CAPABILITY` | an element supports no capability |
| | `REFUSED:EOM_ELEMENT_CAPABILITY_UNKEYED` | the supported capability has no industry-closure capability key |
| | `REFUSED:EOM_ELEMENT_KEY_UNSAFE` | an element key is absent or unsafe |
| | `REFUSED:EOM_DATA_UNOWNED` | a shared data domain has no owning role |
| | `REFUSED:EOM_LINKING_NO_ABB` | a linking automation is realized by no architecture building block |
| `030_axis_obligations.rq` | `REFUSED:EOM_STANDARDIZATION_PROCESS_NOT_STANDARD` | HIGH standardization but a core process is not a standard variant |
| | `REFUSED:EOM_INTEGRATION_DATA_NOT_SHARED` | HIGH integration but a shared data domain is not enterprise scope |
| | `REFUSED:EOM_OVERINTEGRATION` | LOW integration but a shared data domain is enterprise scope |
| | `REFUSED:EOM_OVERSTANDARDIZATION` | LOW standardization but a core process is a standard variant |
| `040_maturity_progression.rq` | `REFUSED:EOM_MATURITY_UNEVIDENCED` | the claimed stage has no receipted stage evidence |
| | `REFUSED:EOM_MATURITY_SKIP` | a lower stage has no receipted stage evidence |
| | `REFUSED:EOM_MATURITY_STAGE2_NO_SHARED_INFRA` | stage 2 or higher without a linking automation |
| | `REFUSED:EOM_MATURITY_STAGE3_NOT_STANDARD_CORE` | stage 3 or higher with a core process that is not a standard variant |
| | `REFUSED:EOM_MATURITY_STAGE4_NO_MODULARITY` | stage 4 without a modular component |
| `050_engagement_model.rq` | `REFUSED:EOM_ENGAGEMENT_NO_ENTERPRISE_LEVEL` | no enterprise-level mechanism |
| | `REFUSED:EOM_ENGAGEMENT_NO_PROJECT_LEVEL` | no project-level mechanism |
| | `REFUSED:EOM_ENGAGEMENT_NO_LINKING` | no linking mechanism |
| | `REFUSED:EOM_ENGAGEMENT_MECHANISM_UNKNOWN` | a mechanism does not join to an `ENG-` notation |
| | `REFUSED:EOM_DECISION_NO_ENGAGEMENT` | a decision has no engagement model |
| | `REFUSED:EOM_WORKPACKAGE_UNREVIEWED` | a work package is neither reviewed nor covered by a typed `eom:Dispensation` that has an owner and an expiry |
| | `REFUSED:EOM_DISPENSATION_UNBOUNDED` | a dispensation lacks an owner or an expiry |
| `060_adm_phase_gate.rq` | `REFUSED:EOM_ADM_CYCLE` | the phase order reaches itself |
| | `REFUSED:EOM_ADM_ARTIFACT_MISSING` | an ACHIEVED record lacks a required artifact kind |
| | `REFUSED:EOM_ADM_PREDECESSOR_NOT_ACHIEVED` | an ACHIEVED record's predecessor is not ACHIEVED in the same engagement |
| | `REFUSED:EOM_ADM_REQMGMT_MISSING` | an ACHIEVED record has no requirements-management review; a phase with no notation is not exempt |
| | `REFUSED:EOM_ADM_STATUS_INVALID` | status is outside the three allowed values |
| | `REFUSED:EOM_ADM_RECORD_MALFORMED` | a record lacks phase, engagement or status |
| `070_value_stream_anchoring.rq` | `REFUSED:EOM_CAPABILITY_FLOATING` | an enterprise capability is in no value stream stage and is not ENABLING |
| | `REFUSED:EOM_VALUE_STREAM_EMPTY` | a value stream has no stage |
| `080_authority_fence.rq` | `REFUSED:EOM_AUTHORITY_DO_FORBIDDEN` | a DO ceiling, claim or class (as a literal or as the DO individual), a DO individual under any property, or a DO grant flag that is not a typed boolean false appears |
| | `REFUSED:EOM_AUTHORITY_CEILING_INVALID` | a ceiling is outside NONE, OBSERVE, SELECT, CONSTRUCT |

Known limit: maturity stage evidence (`eom:StageEvidence`) is a design-time record. Gate `040_maturity_progression.rq` checks that a receipt digest exists in the right shape for the claimed stage and every lower stage; it does not check who produced or verified it, nor whether it was observed. A maturity claim here is therefore a modelling claim, never an observed outcome.

## Input contract

`ontology/enterprise-input.ttl` ships empty. A consumer supplies Turtle only: an `ea:Strategy` carrying `eom:ofEnterprise`; an `eom:OperatingModelDecision` with its axes, chosen model, `eom:targetClosure` and `eom:targetBaseIri`; the foundation elements, whose `eom:supportsCapability` links point at industry capabilities (this is how an enterprise's core processes tie to a profile's capabilities); the engagement model and ADM phase records; and existing building blocks in `ea:` shape, so skeletons appear only where none exist. The target base IRI must equal the closure's base IRI on the merged graph. `qualification/project/ontology/enterprise-input.ttl` overlays the contract with a synthetic enterprise.

## Generated artifacts (pass 1 of the two-pass pipeline)

Both rules use `mode = "Overwrite"` and `skip_empty = false`, and write only under `generated/enterprise-operating-model/`. Queries return literals and `STR()` values only; templates use only `for`, `if` and plain interpolation, and a repository test asserts the templates never contain the token for an approved status.

| Rule | Query | Output | Authority | Standing |
|---|---|---|---|---|
| `eom-requirements` | `queries/10-requirements.rq` | `generated/enterprise-operating-model/architecture-requirements.ttl` | none claimed | requirements are inputs, not standing claims |
| `eom-abb-skeletons` | `queries/20-abb-skeletons.rq` | `generated/enterprise-operating-model/abb-skeletons.ttl` | `ic:authorityClaim` is `NONE` | `ic:standing` is `UNKNOWN` |

- `eom-requirements` emits one `ic:Requirement` per foundation element: id `REQ-<decision key>-<element key>`, `ic:IN_SCOPE`, `ic:requiresCapability` the supported capability, `ic:originAuthority` the strategy, `ic:inClosure` the target closure. The statement is built from keys and axis codes only; no free text from input is echoed.
- `eom-abb-skeletons` emits, per capability that no building block realizes, a candidate `ea:ArchitectureBuildingBlock` and an `ea:ArchitectureContract` with an `ea:AuthorityBoundary` at the construct ceiling, `ic:PENDING_HUMAN_APPROVAL`, authority claim `NONE`, and a compliance criterion chosen from the axes (HIGH standardization gives `eom:StandardProcessVariant`, HIGH integration gives `eom:SharedDataContract`).
- Fixed point: skeletons appear only where no building block exists. After a human merges them, the next run emits none.

The skeleton is never approved by generation. Approval needs a named human and a receipt, enforced by gate `080_authority_fence.rq` of the industry closure pack.

## Pack status

- Derived packaging profile: project (the pack ships `ggen.toml`). Class: CapabilityPack, see [Pack classes](pack-classes.md). `[pack]` in `pack.toml` holds only name, version and description.
- The dependency direction is this pack to `industry-closure-ledger-pack` (templates emit its vocabulary), never the reverse.
- Manufacture, execution and replay: `BLOCKED:ggen_binary_unavailable` in an environment without a ggen binary. The gates are proven under rdflib only; `eom:precedes` order uses a property path whose native-engine behaviour is unproven until a real ggen run. Nothing here is ALIVE and no Level-5 claim is made.
