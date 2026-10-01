# Reference: industry closure contract

Exact contract of `industry-closure-pack` (KernelPack) and of the profile gate in `industry-closure-retail-lending-profile-pack` (ProfilePack). This page is a reference: it states what the sources declare and does not teach or justify them. For the learning path see [Generate an industry closure](../tutorials/generate-an-industry-closure.md); for tasks see [Add an industry to a closure](../how-to/add-an-industry-to-closure.md) and [Triage an industry-closure residual](../how-to/triage-an-industry-closure-residual.md); for rationale see [Industry closure as architecture strategy](../explanation/industry-closure-as-architecture-strategy.md). The companion contract for strategy-derived requirements is [Enterprise operating model contract](enterprise-operating-model-contract.md).

Nothing on this page copies a ggen release, commit, platform asset, digest or timeout. The canonical sources are the pack files named below; where this page and a source differ, the source wins and this page is repaired.

## Scope and authority

- The pack SELECTs (queries and gates) and CONSTRUCTs (templates). It has no DO authority. No DO individual, class or property is declared in its namespace, and gate `080_authority_fence.rq` refuses one if a consumer supplies it.
- It does not prove a generated consumer, an external system, a benchmark, or any production actuation boundary. Marketplace qualification proves its bounded boundary only.
- The standing ladder is owned by [Standing](standing.md). This pack only restricts the literal values (gate `090_standing_evidence.rq`) and adds no vocabulary.

## Namespaces and the `ea:` hygiene rule

| Prefix | Namespace | Owner |
|---|---|---|
| `ic:` | `https://seanchatmangpt.github.io/packs/industry-closure-pack#` | this pack |
| `eom:` | `https://seanchatmangpt.github.io/packs/enterprise-operating-model-pack#` | [enterprise-operating-model-pack](enterprise-operating-model-contract.md) |
| `ea:` | `https://chatman.ai/ontology/enterprise-architecture#` | `enterprise-architecture-pack`, consumed by IRI only |
| `togaf:` | the anchor IRI declared in `togaf-adm-pack` | consumed by IRI only |

Hygiene rule: this pack never declares, re-types or prefix-declares an `ea:` or `togaf:` term in its ontology. Gates, queries and templates write the full IRI in a `PREFIX` line or in angle brackets and use only terms that exist in the owning ontology; a repository test binds every `ea:` local name used by a gate or query to `packs/enterprise-architecture-pack/ontology.ttl`. The consumed terms are `ea:Strategy`, `ea:Capability`, `ea:ArchitectureBuildingBlock`, `ea:SolutionBuildingBlock`, `ea:ArchitectureContract`, `ea:AuthorityBoundary`, `ea:realizesCapability`, `ea:governedByContract`, `ea:satisfiesABB`, `ea:hasStanding`, `ea:QUALIFIED`, `ea:exactSubject` and `ea:hasAuthorityBoundary`. A pack-local `eap:` vocabulary is not extended.

Jurisdiction guard: a gate acts on `ic:`-typed subjects or on `ea:` objects those subjects reference. It never refuses an unrelated `ea:` or `togaf:` subject in a consumer graph.

## Vocabulary

Generated from the declarations in `packs/industry-closure-pack/ontology.ttl`. Meanings are paraphrased in the source; read the source for the full text.

### Classes

| Term | Meaning |
|---|---|
| `ic:AdmissionState` | ADMITTED, EXCLUDED or UNKNOWN. |
| `ic:ApprovalStatus` | PENDING_HUMAN_APPROVAL, APPROVED or REJECTED, carried on architecture contracts. APPROVED requires approvedBy and approvalReceipt, which are human rights and never generated. |
| `ic:ClosureSnapshot` | One epoch of the coverage ledger of a closure. Epoch equals predecessor plus one, with a single successor per snapshot. |
| `ic:Coverage` | A recorded (capability, architecture building block) coverage in one snapshot. LIVE or STALE. The ABB is the identity of a coverage, so SBB substitution stays monotone. |
| `ic:CoverageState` | LIVE or STALE. STALE needs a stale reason and keeps the ledger monotone. |
| `ic:DeficitClass` | One of the seven first-failing-link classes of the residual. Each individual carries its own routing, delta code, acceptance text and falsifier text, so routing is data, not code. |
| `ic:EvidenceKind` | OBSERVED or SYNTHETIC. Synthetic evidence can never support ALIVE. |
| `ic:EvidenceOutcome` | VERIFIED, FALSIFIED or INCONCLUSIVE. |
| `ic:ExecutionEvidence` | An independently verified outcome for a solution building block at its current exact subject. Evidence at any other subject is never joined. |
| `ic:FeedbackTarget` | A typed upstream lane that a deficit class routes to. |
| `ic:IndustryClosure` | One bounded industry scope with its admitted knowledge sources, requirements and a chain of closure snapshots. |
| `ic:KnowledgeSource` | A public knowledge source. It enters the closure only through admission: ADMITTED, EXCLUDED with a reason, or UNKNOWN with a falsifier. |
| `ic:Requirement` | An atomic, paraphrased requirement with identity, a safe key, an explicit scope disposition and an admitted origin. Prose never originates a requirement. |
| `ic:Residual` | One recorded element of the residual for a (requirement, capability key) pair. Computed from the closure, never a second source of truth; gate 060 forces the recorded ledger to equal the computed residual. |
| `ic:Retirement` | A receipted, reasoned removal of a recorded coverage. The only lawful way a (capability, ABB) pair leaves the ledger. |
| `ic:ScopeDisposition` | IN_SCOPE or OUT_OF_SCOPE. Out of scope needs a scope justification; nothing leaves the residual silently. |
| `ic:WorkOrder` | A pure projection of one residual into a candidate sJira change record. Standing UNKNOWN or BLOCKED, authority claim NONE. |

### Object properties

| Term | Domain | Range | Meaning |
|---|---|---|---|
| `ic:admission` | `ic:KnowledgeSource` | `ic:AdmissionState` | Admission state of a knowledge source. |
| `ic:approvalStatus` | any | `ic:ApprovalStatus` | Approval status of an architecture contract. Generated skeletons carry PENDING_HUMAN_APPROVAL only. |
| `ic:approvedBy` | any | `Agent` | The human agent who approved a contract. Never generated. |
| `ic:byABB` | `ic:Coverage` | any | The architecture building block, the identity of the coverage. |
| `ic:bySBB` | `ic:Coverage` | any | The solution building block currently satisfying the ABB. |
| `ic:concept` | any | any | An IRI of a class, defined in an admitted source, that a capability individual denotes. |
| `ic:coverageState` | `ic:Coverage` | `ic:CoverageState` | LIVE or STALE. |
| `ic:coversCapability` | `ic:Coverage` | any | The capability a coverage records. |
| `ic:deficitClass` | `ic:Residual` | `ic:DeficitClass` | The exactly-one class of a residual (the first failing link). |
| `ic:derivedFrom` | `ic:Requirement` | `ic:KnowledgeSource` | Origin of a requirement in an ADMITTED knowledge source. |
| `ic:disposition` | `ic:Requirement` | `ic:ScopeDisposition` | Explicit scope disposition: IN_SCOPE or OUT_OF_SCOPE. |
| `ic:evidenceFor` | `ic:ExecutionEvidence` | any | The solution building block the evidence is about. |
| `ic:evidenceKind` | `ic:ExecutionEvidence` | `ic:EvidenceKind` | OBSERVED or SYNTHETIC. |
| `ic:evidencedBy` | `ic:Coverage` | `ic:ExecutionEvidence` | The execution evidence a coverage standing rests on. |
| `ic:feedbackTarget` | `ic:Residual` | `ic:FeedbackTarget` | The upstream target of a residual; must equal its class's routesTo. |
| `ic:forResidual` | `ic:WorkOrder` | `ic:Residual` | The residual a work order projects. |
| `ic:groundedIn` | any | `ic:KnowledgeSource` | A capability is grounded when it is grounded in an ADMITTED knowledge source (or grounded in a strategy). |
| `ic:groundedInStrategy` | any | any | A capability is grounded in a strategy individual of the enterprise-architecture vocabulary. |
| `ic:hasSnapshot` | `ic:IndustryClosure` | `ic:ClosureSnapshot` | Links a closure to a snapshot of its ledger. The head is the snapshot with no successor. |
| `ic:inClosure` | `ic:Requirement` | `ic:IndustryClosure` | The closure that owns the requirement. |
| `ic:inSnapshot` | `ic:Coverage` | `ic:ClosureSnapshot` | The snapshot a coverage is recorded in. |
| `ic:originAuthority` | `ic:Requirement` | any | Alternative origin of a requirement: a strategy individual of the enterprise-architecture vocabulary. |
| `ic:outcome` | `ic:ExecutionEvidence` | `ic:EvidenceOutcome` | VERIFIED, FALSIFIED or INCONCLUSIVE. |
| `ic:producedBy` | `ic:ExecutionEvidence` | any | The agent that produced the evidence. |
| `ic:providesConcept` | `ic:KnowledgeSource` | any | An IRI of a class that the admitted source defines. |
| `ic:requiresCapability` | `ic:Requirement` | any | The capability a requirement needs. The object is the capability individual; its identity is this link plus its capability key. |
| `ic:residualOf` | `ic:Residual` | `ic:Requirement` | The in-scope requirement the residual belongs to. |
| `ic:retires` | `ic:Retirement` | `ic:Coverage` | The recorded coverage a retirement removes. |
| `ic:routesTo` | `ic:DeficitClass` | `ic:FeedbackTarget` | The single upstream target a deficit class routes to. |
| `ic:snapshotOf` | `ic:ClosureSnapshot` | `ic:IndustryClosure` | The closure a snapshot belongs to. |
| `ic:sourceIri` | `ic:KnowledgeSource` | any | Version IRI of an ADMITTED source, read from the vendored file. |
| `ic:supersedes` | `ic:ClosureSnapshot` | `ic:ClosureSnapshot` | The immediate predecessor snapshot. |
| `ic:usesSource` | `ic:IndustryClosure` | `ic:KnowledgeSource` | Links a closure to a knowledge source it considered, in any admission state. |
| `ic:verifiedBy` | `ic:ExecutionEvidence` | any | The agent that verified the evidence. Must differ from the producer. |

### Datatype properties

| Term | Domain | Range | Meaning |
|---|---|---|---|
| `ic:acceptance` | `ic:WorkOrder` | `string` | Acceptance text of a work order, taken from its deficit class. |
| `ic:acceptanceText` | `ic:DeficitClass` | `string` | Paraphrased acceptance criterion copied into work orders. |
| `ic:approvalReceipt` | any | `string` | Receipt reference for a human approval. Never generated. |
| `ic:authorityCeiling` | any | any | Authority ceiling literal: NONE, OBSERVE, SELECT or CONSTRUCT. The consequential level is unrepresentable. |
| `ic:authorityClaim` | any | any | Authority claimed by a residual or work order. The only lawful value is NONE. |
| `ic:baseIri` | `ic:IndustryClosure` | `string` | Base IRI string from which generated residual, work-order and snapshot IRIs are minted. |
| `ic:blockedReason` | `ic:Residual` | `string` | Required reason on a residual routed to UPSTREAM_AUTHORITY. |
| `ic:boundPathPrefix` | `ic:IndustryClosure` | `string` | Vendored path prefix inside which every admitted source locator of the closure must lie. |
| `ic:capabilityKey` | any | `string` | Safe identity key of a capability individual, matching ^[A-Za-z0-9._-]+$. |
| `ic:deficitCode` | `ic:DeficitClass` | `string` | Local name of the deficit class as a literal; used to mint the class reference in generated rows. |
| `ic:deltaCode` | any | `string` | Typed delta kind requested of the factory. On a deficit class it is the source of truth; a work order must repeat its class's value. |
| `ic:epoch` | `ic:ClosureSnapshot` | `integer` | Epoch number. Epoch 0 is the empty ledger; each successor is predecessor plus one. |
| `ic:evidenceSubject` | `ic:ExecutionEvidence` | `string` | Exact subject digest the evidence was observed at. It counts only while it equals the SBB's current exact subject. |
| `ic:exclusionReason` | `ic:KnowledgeSource` | `string` | Why an EXCLUDED source is outside the closure. Required for EXCLUDED. |
| `ic:falsifier` | any | `string` | The condition that would prove the claim wrong. Required on an UNKNOWN knowledge source and on every work order; must not be blank. |
| `ic:falsifierText` | `ic:DeficitClass` | `string` | Paraphrased falsifier copied into work orders. |
| `ic:forCapabilityKey` | `ic:Residual` | `string` | Capability key of the residual, or UNMAPPED. |
| `ic:industryScope` | `ic:IndustryClosure` | `string` | Human-readable statement of the bounded industry scope. |
| `ic:licenseBoundary` | `ic:KnowledgeSource` | `string` | Statement of the licence terms under which the source is vendored and used. |
| `ic:marketplacePack` | any | `string` | Optional binding of a solution building block to a marketplace pack name. ALIVE requires it. |
| `ic:needsDoAuthority` | `ic:Requirement` | `boolean` | A NEED, never a grant. A requirement that needs consequential authority permanently classifies as DEFICIT_AUTHORITY with standing BLOCKED. The classifier fails closed: any value other than the typed literal boolean false reads as a need, and the requirement-identity gate (see the gate table) refuses a value that is not a boolean literal. |
| `ic:packDigest` | any | `string` | Optional catalog digest recorded for the bound pack. ALIVE requires it; a mismatch with the derived catalog marks the coverage STALE. |
| `ic:receiptDigest` | any | `string` | Receipt digest in the form sha256:<64 lowercase hex>. Required on a retirement and on execution evidence. |
| `ic:requirementId` | `ic:Requirement` | `string` | Safe identity key, matching ^[A-Za-z0-9._-]+$, unique across requirements. |
| `ic:residualKey` | `ic:Residual` | `string` | Requirement id, two hyphens, capability key or UNMAPPED. A plain literal everywhere. |
| `ic:retirementReason` | `ic:Retirement` | `string` | Required reason for a retirement. |
| `ic:scopeJustification` | `ic:Requirement` | `string` | Required reason for an OUT_OF_SCOPE requirement. |
| `ic:sourceDigest` | `ic:KnowledgeSource` | `string` | Pinned digest of the vendored source file, in the form sha256:<64 lowercase hex>. |
| `ic:sourceLocator` | `ic:KnowledgeSource` | `string` | Repository-relative path of the vendored source. Must start under ontologies/public/ and inside the closure's bound path prefix when ADMITTED. |
| `ic:sourceVersion` | `ic:KnowledgeSource` | `string` | Version string of an ADMITTED source, read from the vendored file. |
| `ic:staleBecause` | `ic:Coverage` | `string` | Required reason when a coverage is STALE. |
| `ic:standing` | any | any | Standing literal matching ^(UNKNOWN/PARTIAL_ALIVE/ALIVE/BLOCKED/BUILD_BROKEN/UNSUPPORTED/REFUSED:[A-Z0-9_]+)$. No new vocabulary. QUALIFIED is not ALIVE. |
| `ic:statement` | `ic:Requirement` | `string` | Paraphrased statement of the requirement. |
| `ic:status` | `ic:Residual` | `string` | Residual status literal. OPEN for every generated residual. |
| `ic:targetCode` | `ic:FeedbackTarget` | `string` | Local name of the feedback target as a literal. |
| `ic:workOrderId` | `ic:WorkOrder` | `string` | Unique identifier of a work order. |


### Closed value individuals

| Individual | Value set | Meaning |
|---|---|---|
| `ic:ADMITTED`, `ic:EXCLUDED`, `ic:UNKNOWN` | `ic:AdmissionState` | Source admission state. |
| `ic:IN_SCOPE`, `ic:OUT_OF_SCOPE` | `ic:ScopeDisposition` | Requirement scope disposition. |
| `ic:LIVE`, `ic:STALE` | `ic:CoverageState` | Coverage currentness. |
| `ic:VERIFIED`, `ic:FALSIFIED`, `ic:INCONCLUSIVE` | `ic:EvidenceOutcome` | Evidence outcome. |
| `ic:OBSERVED`, `ic:SYNTHETIC` | `ic:EvidenceKind` | Evidence kind. Synthetic never supports ALIVE. |
| `ic:PENDING_HUMAN_APPROVAL`, `ic:APPROVED`, `ic:REJECTED` | `ic:ApprovalStatus` | Contract approval status. |
| `ic:COVERED` | classifier sentinel | The whole chain holds. It is deliberately not a `ic:DeficitClass` and is never emitted as a deficit. |

## The chain operator and class precedence

The residual is derived, not stored. For an in-scope requirement `r` with capability `c`:

```text
Chain(c) := grounded(c)
          ∧ ABB realizes c
          ∧ APPROVED contract with an authority boundary governs that ABB
          ∧ SBB satisfies that ABB
          ∧ SBB is QUALIFIED with a pinned exactSubject
          ∧ independent VERIFIED evidence at the SBB's current exactSubject
            ∧ no FALSIFIED evidence at that subject

Δ := { (r, c) | r IN_SCOPE, needsDoAuthority(r) ∨ ¬Chain(c) }
```

Independence means the producer and the verifier of the evidence differ. Evidence recorded at any subject other than the SBB's current one is never joined.

Each element of Δ has exactly one class, the first failing link in this order:

| Order | Class | Fails when |
|---|---|---|
| 1 | `ic:DEFICIT_AUTHORITY` | the requirement carries `ic:needsDoAuthority true` (at every stage) |
| 2 | `ic:DEFICIT_ONTOLOGY` | the requirement maps to no capability, or the capability is grounded in no ADMITTED source and no strategy |
| 3 | `ic:DEFICIT_ABB` | no ABB realizes the capability |
| 4 | `ic:DEFICIT_CONTRACT` | no APPROVED contract with an authority boundary governs an ABB of the capability |
| 5 | `ic:DEFICIT_SBB` | no SBB satisfies an ABB under such a contract |
| 6 | `ic:DEFICIT_QUALIFICATION` | no such SBB is QUALIFIED with a pinned exactSubject |
| 7 | `ic:DEFICIT_EVIDENCE` | no independent VERIFIED evidence at the current subject, or FALSIFIED evidence exists at it |

The classifier is one block, delimited by `# BEGIN R_CORE` and `# END R_CORE`, that appears byte-identically (after whitespace normalisation) in `queries/10-residual.rq`, `queries/20-closure-frontier.rq`, `gates/055_frontier_recorded.rq` and `gates/060_residual_ledger.rq`. A repository test asserts the equality.

## Deficit classes: routing and delta codes

Routing is data on the `ic:DeficitClass` individuals, not code. `ic:acceptanceText` and `ic:falsifierText` on the class are copied into work orders.

| Class | `ic:routesTo` | `ic:deltaCode` | Factory change requested |
|---|---|---|---|
| `ic:DEFICIT_AUTHORITY` | `ic:UPSTREAM_AUTHORITY` | `AUTHORITY_BLOCK` | none inside this closure; standing `BLOCKED` |
| `ic:DEFICIT_ONTOLOGY` | `ic:UPSTREAM_KNOWLEDGE` | `ONTOLOGY_DELTA` | map the capability and admit a public source through gate 010 |
| `ic:DEFICIT_ABB` | `ic:UPSTREAM_ARCHITECTURE` | `ARCHITECTURE_DELTA` | author or reuse an ABB with a pending contract skeleton |
| `ic:DEFICIT_CONTRACT` | `ic:UPSTREAM_ARCHITECTURE` | `ARCHITECTURE_DELTA` | a named human approves the contract with receipt |
| `ic:DEFICIT_SBB` | `ic:UPSTREAM_MARKETPLACE` | `PACK_DELTA` | extend or compose an existing pack first; a new pack needs class-closure justification |
| `ic:DEFICIT_QUALIFICATION` | `ic:UPSTREAM_QUALIFICATION` | `QUALIFICATION_DELTA` | qualify the SBB and pin its exact subject |
| `ic:DEFICIT_EVIDENCE` | `ic:UPSTREAM_QUALIFICATION` | `COURT_DELTA` | independent evidence at the current exact subject |

Feedback targets: `ic:UPSTREAM_KNOWLEDGE`, `ic:UPSTREAM_ARCHITECTURE`, `ic:UPSTREAM_MARKETPLACE`, `ic:UPSTREAM_QUALIFICATION`, `ic:UPSTREAM_AUTHORITY`. A pack-delta request must follow [Consolidate a pack family](../how-to/consolidate-a-pack-family.md) and [Pack classes](pack-classes.md).

## Gates

Gate contract (both packs): each gate is one `SELECT ?subject ?reason`; zero rows is a pass and any row is a refusal with a typed `REFUSED:*` reason; every gate ends with `ORDER BY ?subject ?reason`. Every `UNION` branch binds `?subject` first, "missing property" is `OPTIONAL` plus `!BOUND`, and `NOT EXISTS` is used only with the outer variable bound. Stems of `gates/*.rq`, `witnesses/pass/*.ttl` and `witnesses/fail/*.ttl` correspond exactly.

### Enforcement layers

1. `gate-court.toml` and `scripts/check_gate_witness_courts.py` prove stem correspondence only.
2. The pytest courts run every gate under real rdflib against its witnesses. A pass witness returns zero rows; the fail witness's reason set must equal the declared `REFUSED:` literals of the gate, so a code that cannot fire fails the test.
3. `scripts/qualify_packs.py` with a real admitted ggen proves isolated manufacture and replay. Without a ggen binary this layer is `BLOCKED:ggen_binary_unavailable`.

Existence of a gate is never a claim of enforcement. The gates are proven under rdflib; native-engine behaviour of `EXISTS` inside `BIND` and of property paths is unproven until a real ggen run.

### Gate table

| Gate | Code | Trigger |
|---|---|---|
| `010_source_admission.rq` | `REFUSED:IC_SOURCE_ADMISSION_INVALID` | a knowledge source has no admission, or one outside ADMITTED, EXCLUDED, UNKNOWN |
| | `REFUSED:IC_SOURCE_PROVENANCE_MISSING` | an ADMITTED source lacks source IRI, version, digest, licence boundary or locator |
| | `REFUSED:IC_SOURCE_DIGEST_MALFORMED` | a source digest is not `sha256:` plus 64 lowercase hex |
| | `REFUSED:IC_SOURCE_NOT_VENDORED` | an ADMITTED locator does not start under `ontologies/public/` |
| | `REFUSED:IC_SOURCE_OUTSIDE_SCOPE` | an ADMITTED locator lies outside the closure's bound path prefix |
| | `REFUSED:IC_SOURCE_EXCLUSION_UNREASONED` | an EXCLUDED source has no exclusion reason |
| | `REFUSED:IC_SOURCE_UNKNOWN_NO_FALSIFIER` | an UNKNOWN source has no falsifier |
| `020_requirement_identity.rq` | `REFUSED:IC_REQUIREMENT_MALFORMED` | a requirement lacks id, statement, disposition or closure |
| | `REFUSED:IC_KEY_UNSAFE` | a requirement id or capability key does not match `^[A-Za-z0-9._-]+$` |
| | `REFUSED:IC_CAPABILITY_KEY_MISSING` | a capability required by a requirement has no capability key |
| | `REFUSED:IC_REQUIREMENT_DISPOSITION_INVALID` | disposition is neither IN_SCOPE nor OUT_OF_SCOPE |
| | `REFUSED:IC_REQUIREMENT_SILENT_DROP` | an OUT_OF_SCOPE requirement has no scope justification |
| | `REFUSED:IC_REQUIREMENT_DUPLICATE_ID` | two requirements share an id |
| | `REFUSED:IC_REQUIREMENT_ORIGIN_UNADMITTED` | an IN_SCOPE requirement derives from no ADMITTED source and no `ea:Strategy` origin authority |
| | `REFUSED:IC_REQUIREMENT_CLOSURE_UNDECLARED` | a requirement's closure is not a declared `ic:IndustryClosure`, so the requirement would silently drop out of the residual |
| | `REFUSED:IC_NEEDS_DO_MALFORMED` | `ic:needsDoAuthority` is not a literal of datatype `xsd:boolean` with a boolean lexical value |
| `030_snapshot_identity.rq` | `REFUSED:IC_CLOSURE_NO_SNAPSHOT` | a closure has no snapshot |
| | `REFUSED:IC_SNAPSHOT_EPOCH_MISSING` | a snapshot has no epoch |
| | `REFUSED:IC_SNAPSHOT_ORPHAN` | a snapshot with epoch above 0 has no predecessor, or belongs to no closure |
| | `REFUSED:IC_SNAPSHOT_EPOCH_SKIP` | epoch is not predecessor plus one |
| | `REFUSED:IC_SNAPSHOT_FORK` | two snapshots supersede the same predecessor |
| | `REFUSED:IC_SNAPSHOT_CLOSURE_MISMATCH` | a snapshot and its predecessor belong to different closures |
| | `REFUSED:IC_SNAPSHOT_MULTIPLE_HEADS` | a closure has two snapshots that have no successor |
| | `REFUSED:IC_SNAPSHOT_EPOCH_DUPLICATE` | two snapshots of one closure share an epoch |
| | `REFUSED:IC_CLOSURE_BASEIRI_INVALID` | a closure has no base IRI, or it is not a plain `https` IRI ending in a slash; whitespace, angle brackets, quotes, braces, bars, backslashes, carets and backticks are refused because the templates splice the base IRI unescaped |
| `040_closure_monotonicity.rq` | `REFUSED:IC_CLOSURE_SHRINK` | a (capability, ABB) coverage in snapshot t is absent from t+1 and no receipted, reasoned retirement names it |
| | `REFUSED:IC_RETIREMENT_MALFORMED` | a retirement retires nothing |
| | `REFUSED:IC_RETIREMENT_UNRECEIPTED` | a retirement has no receipt digest |
| | `REFUSED:IC_RETIREMENT_UNREASONED` | a retirement has no reason |
| | `REFUSED:IC_RETIREMENT_DIGEST_MALFORMED` | a retirement's receipt digest is not `sha256:` plus 64 lowercase hex |
| `050_coverage_chain.rq` | `REFUSED:IC_COVERAGE_INCOMPLETE` | a coverage lacks capability, ABB, SBB, snapshot or state |
| | `REFUSED:IC_COVERAGE_STATE_INVALID` | state is neither LIVE nor STALE |
| | `REFUSED:IC_COVERAGE_ABB_NOT_REALIZING` | the ABB does not realize the covered capability |
| | `REFUSED:IC_COVERAGE_CONTRACT_NOT_APPROVED` | a LIVE head coverage's ABB has no APPROVED contract with an authority boundary |
| | `REFUSED:IC_COVERAGE_SBB_MISMATCH` | the SBB does not satisfy the coverage's ABB |
| | `REFUSED:IC_COVERAGE_SBB_NOT_QUALIFIED` | a LIVE head coverage's SBB is not QUALIFIED |
| | `REFUSED:IC_COVERAGE_SBB_UNPINNED` | a LIVE head coverage's SBB has no exact subject |
| | `REFUSED:IC_SBB_SUBJECT_MALFORMED` | a covered SBB's exact subject is not `sha256:` plus 64 lowercase hex |
| | `REFUSED:IC_COVERAGE_EVIDENCE_MISSING` | a LIVE head coverage has no VERIFIED evidence at the SBB's current subject |
| | `REFUSED:IC_COVERAGE_EVIDENCE_FALSIFIED` | a LIVE head coverage has FALSIFIED evidence at the current subject |
| | `REFUSED:IC_COVERAGE_STALE_UNREASONED` | a STALE coverage has no stale reason |
| | `REFUSED:IC_SBB_SUBJECT_AMBIGUOUS` | an SBB that realizes a keyed capability carries two or more distinct exact subjects, so it has no single current subject |
| `055_frontier_recorded.rq` | `REFUSED:IC_FRONTIER_UNRECORDED` | the chain says a capability is covered but the head snapshot records no LIVE coverage of it |
| `060_residual_ledger.rq` | `REFUSED:IC_RESIDUAL_UNRECORDED` | a computed residual has no matching OPEN recorded residual |
| | `REFUSED:IC_RESIDUAL_STALE_OR_MISCLASSIFIED` | a recorded OPEN residual carries a class different from the computed one |
| | `REFUSED:IC_RESIDUAL_ORPHAN` | a recorded residual belongs to a requirement that is not IN_SCOPE |
| | `REFUSED:IC_RESIDUAL_DUPLICATE_KEY` | two OPEN residuals share a residual key, or share one (requirement, capability key) pair |
| `070_deficit_feedback.rq` | `REFUSED:IC_RESIDUAL_UNCLASSIFIED` | a residual has no deficit class |
| | `REFUSED:IC_RESIDUAL_MULTICLASS` | a residual has two classes |
| | `REFUSED:IC_RESIDUAL_NO_FEEDBACK` | a residual has no feedback target |
| | `REFUSED:IC_FEEDBACK_MISROUTED` | the target is not the one its class routes to |
| | `REFUSED:IC_AUTHORITY_BLOCK_NOT_BLOCKED` | an authority-routed residual is not standing `BLOCKED` |
| | `REFUSED:IC_AUTHORITY_BLOCK_UNREASONED` | an authority-routed residual has no blocked reason |
| | `REFUSED:IC_RESIDUAL_STANDING_PROMOTED` | a residual's standing is neither UNKNOWN nor BLOCKED |
| `080_authority_fence.rq` | `REFUSED:IC_AUTHORITY_DO_FORBIDDEN` | a DO ceiling, claim or class (as a literal or as the DO individual), a DO individual under any property, or a DO grant flag that is not a typed boolean false appears |
| | `REFUSED:IC_AUTHORITY_CEILING_INVALID` | a ceiling is outside NONE, OBSERVE, SELECT, CONSTRUCT |
| | `REFUSED:IC_AUTHORITY_CLAIM_MISSING` | a residual or work order has no authority claim |
| | `REFUSED:IC_AUTHORITY_CLAIM_NOT_NONE` | a residual or work order claims anything but NONE |
| | `REFUSED:IC_CONTRACT_APPROVAL_UNATTRIBUTED` | an APPROVED contract lacks a named approver or an approval receipt |
| `090_standing_evidence.rq` | `REFUSED:IC_STANDING_INVALID` | a standing literal is outside the closed vocabulary |
| | `REFUSED:IC_STANDING_ALIVE_WITHOUT_EVIDENCE` | an ALIVE coverage has no receipted, verified, independently attributed evidence |
| | `REFUSED:IC_STANDING_STALE_SUBJECT` | ALIVE evidence subject differs from the SBB's current exact subject |
| | `REFUSED:IC_STANDING_SYNTHETIC_ALIVE` | ALIVE rests on evidence that is not OBSERVED |
| | `REFUSED:IC_STANDING_ALIVE_PACK_UNBOUND` | ALIVE but the SBB has no marketplace pack or pack digest |
| | `REFUSED:IC_STANDING_ALIVE_NOT_LIVE` | ALIVE on a coverage whose state is not LIVE |
| | `REFUSED:IC_STANDING_ALIVE_FALSIFIED` | ALIVE on a head coverage whose SBB has FALSIFIED evidence at its current subject |
| | `REFUSED:IC_STANDING_EVIDENCE_FOREIGN` | the evidence an ALIVE coverage cites is not evidence for that coverage's own SBB |
| | `REFUSED:IC_EVIDENCE_MALFORMED` | evidence lacks a required field or its receipt digest is malformed |
| | `REFUSED:IC_EVIDENCE_NOT_INDEPENDENT` | producer and verifier are the same agent |
| | `REFUSED:IC_EVIDENCE_FALSIFICATION_UNFED` | FALSIFIED evidence at the current subject has no OPEN residual |
| `100_sjira_workorder.rq` | `REFUSED:IC_WORKORDER_MISSING` | an OPEN residual has no work order |
| | `REFUSED:IC_WORKORDER_MALFORMED` | a work order lacks id, residual, delta code, acceptance, falsifier, standing or authority claim |
| | `REFUSED:IC_WORKORDER_FALSIFIER_BLANK` | a work order's falsifier is blank |
| | `REFUSED:IC_WORKORDER_DUPLICATE_ID` | two work orders share an id |
| | `REFUSED:IC_WORKORDER_DUPLICATE_FOR_RESIDUAL` | two work orders project one residual, whatever their ids |
| | `REFUSED:IC_WORKORDER_ORPHAN` | a work order projects something that is not a residual |
| | `REFUSED:IC_WORKORDER_DELTA_MISMATCH` | the delta code differs from the residual's class |
| | `REFUSED:IC_WORKORDER_STANDING_PROMOTED` | a work order's standing is neither UNKNOWN nor BLOCKED |

Repairs for each code are catalogued in [Triage an industry-closure residual](../how-to/triage-an-industry-closure-residual.md).

### Profile gate (`industry-closure-retail-lending-profile-pack`)

`gates/010_profile_grounding.rq` is a ProfilePack gate over the kernel vocabulary. It is listed here because the profile is an ABox over this contract.

| Code | Trigger |
|---|---|
| `REFUSED:LND_CAPABILITY_CONCEPT_NOT_PROVIDED` | a capability is grounded in a source that does not provide the concept the capability denotes |
| `REFUSED:LND_CAPABILITY_CONCEPT_MISSING` | a capability is grounded in a source but names no concept, so concept provision cannot be checked |
| `REFUSED:LND_REQUIREMENT_SOURCE_NOT_IN_CLOSURE` | a requirement derives from a source its closure does not use |
| `REFUSED:LND_SOURCE_NOT_FIBO_LOAN` | a closure bound to the vendored loan-ontology path admits a source whose ontology IRI is outside that family |

## Input contract

A consumer supplies Turtle only.

- Industry side: `industry-closure-pack/ontology/industry-input.ttl` ships empty. A ProfilePack or the consumer supplies an `ic:IndustryClosure` with its base IRI, bound path prefix and scope; knowledge sources (ADMITTED, EXCLUDED, UNKNOWN); requirements; capability individuals; any known ABBs, contracts, SBBs and evidence in `ea:` shape; and snapshots, coverages and residuals.
- Enterprise side: [enterprise-operating-model-pack](enterprise-operating-model-contract.md) supplies strategy-derived requirements and skeletons as generated Turtle that the consumer appends to its imports.
- `qualification/project/ontology/industry-input.ttl` overlays the empty contract with synthetic data at the same relative path; synthetic data lives only under `qualification/` and `fixtures/`, never in `ontology.ttl`.

## Generated artifacts

The `ggen.toml` of the pack is pass 2 of a two-pass pipeline (pass 1 is the enterprise operating model pack). Every rule uses `mode = "Overwrite"` and `skip_empty = false`, so an empty residual still writes an empty ledger; this is the fixed point. All outputs are candidates.

| Rule | Query | Output | Authority | Standing |
|---|---|---|---|---|
| `residual-ledger` | `queries/10-residual.rq` | `generated/industry-closure/residual-ledger.ttl` | claim `NONE` | UNKNOWN, or BLOCKED for authority |
| `sjira-workorders` | `queries/10-residual.rq` | `generated/industry-closure/sjira-workorders.ttl` | claim `NONE` | UNKNOWN or BLOCKED |
| `closure-next` | `queries/20-closure-frontier.rq` | `generated/industry-closure/closure-next.ttl` | none claimed | `UNKNOWN` on every coverage it proposes |
| `feedback-packet` | `queries/10-residual.rq` | `generated/industry-closure/feedback-packet.json` | `doAuthority:false`, ceiling `NONE` | `UNKNOWN` |

- The ledger has one residual per (requirement, capability) in Δ, keyed `<requirement id>--<capability key or UNMAPPED>`, status `OPEN`.
- A work order is a pure projection of a residual: id `SJ-<residual key>`, delta code, acceptance and falsifier text taken from the deficit class. It is a candidate change record, not a file under `packs/`.
- `closure-next` proposes the next snapshot (epoch plus one, superseding the head). Every carried coverage is re-evaluated against the same chain the residual uses, per capability. It stays LIVE only while its capability is still covered and its own SBB has current independent VERIFIED evidence and no current FALSIFIED evidence. Otherwise it is re-marked STALE and kept, with the deficit class code as the stale reason (or `EVIDENCE_NOT_CURRENT` when the only fault is evidence). A coverage named by a receipted, reasoned retirement is not carried. A capability counts as needing DO when any IN_SCOPE requirement that requires it does; a requirement moved OUT_OF_SCOPE leaves the carried coverage LIVE. Admission is through gates 030, 040, 050 and 055 after a human appends it to input.
- The feedback packet is deterministic JSON with a flat `items` list sorted by key; each item carries work order id, requirement id, capability key, deficit class, delta code and target code, and the consumer groups by target.

What a run produces: strategy-derived requirements, candidate ABB and contract skeletons, the residual ledger, candidate work orders, the feedback packet and the candidate next snapshot. What it does not produce: packs, qualified SBBs, receipts, contract approvals, or any consequential action. Templates use only `for`, `if`, `loop.last` and plain interpolation, never contain the token for an approved status, never write outside `generated/<pack-scoped-dir>/`, and contain no ggen version, commit, digest or timeout literal; a repository test lints each of these.

## Standing and authority vocabularies

| Vocabulary | Allowed values | Enforced by |
|---|---|---|
| Authority ceiling | `NONE`, `OBSERVE`, `SELECT`, `CONSTRUCT` | gate `080_authority_fence.rq` |
| Authority claim of a residual or work order | `NONE` only | gate `080_authority_fence.rq` |
| Standing | `UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED`, `BUILD_BROKEN`, `UNSUPPORTED`, or typed `REFUSED:` plus upper-case code | gate `090_standing_evidence.rq` |
| Work order standing | `UNKNOWN` or `BLOCKED` | gate `100_sjira_workorder.rq` |

- `ea:QUALIFIED` is not ALIVE. A coverage may be called ALIVE only with independent, OBSERVED evidence at the SBB's current exact subject, and an SBB that carries `ic:marketplacePack` and `ic:packDigest`.
- Catalog binding is partial and explicit: a bound SBB whose recorded digest equals the digest in `python3 scripts/marketplace.py catalog --scope all` is current; a mismatch is a stale reason and the coverage must be marked STALE. No script computes the closure from the catalog.
- A requirement that needs DO authority is a need, never a grant: it classifies as `ic:DEFICIT_AUTHORITY` with standing `BLOCKED` forever. Consequential execution is a separately admitted path (BRCE where a consumer uses it) outside this pack.

## Ledger invariants

| Invariant | Gate |
|---|---|
| epoch is predecessor plus one, one successor per snapshot, same closure | `030_snapshot_identity.rq` |
| every recorded (capability, ABB) pair survives unless a receipted, reasoned retirement names it | `040_closure_monotonicity.rq` |
| every LIVE head coverage still satisfies the full chain | `050_coverage_chain.rq` |
| no covered capability is omitted from the head snapshot | `055_frontier_recorded.rq` |
| the recorded residual ledger equals the computed residual | `060_residual_ledger.rq` |

The ledger never shrinks. Currentness is re-earned: a regression keeps the coverage as STALE and the derived residual reappears.

### Known limits

- Falsified evidence is sticky. FALSIFIED evidence at an SBB's current exact subject keeps its capability in `DEFICIT_EVIDENCE` even beside VERIFIED evidence, and there is no evidence-supersession relation. The only recovery is a new exact subject (a new pinned SBB digest) with fresh VERIFIED evidence. The check covers every QUALIFIED SBB of any ABB that realizes the capability, which is over-strict and fails closed by design.
- An SBB has exactly one current exact subject; gate `050_coverage_chain.rq` refuses two.
- Gate `040_closure_monotonicity.rq` keys monotonicity on (capability, ABB). It does not constrain a coverage's state or SBB across snapshots; a LIVE coverage replaced by a STALE one is lawful if the stale reason is given.
- Grounding in an ADMITTED source counts only when the closure uses that source (`ic:usesSource`). An `ea:Strategy` accepted as an origin or grounding is taken as typed; this pack does not judge that strategy's own provenance.
- The classifier nests EXISTS inside BIND over variables bound earlier in the group. Its behaviour is shown under rdflib only. A native-engine run of the queries has never been made, so a divergence in unbound-variable or boolean handling there would not be caught here; that run is part of the real-ggen qualification and stays `BLOCKED:ggen_binary_unavailable` until it happens.

## Pack status

- Derived packaging profile: project (the pack ships `ggen.toml`). Class: KernelPack, see [Pack classes](pack-classes.md). `[pack]` in `pack.toml` holds only name, version and description.
- Not in the active marketplace configuration; visible under `python3 scripts/marketplace.py catalog --scope all`.
- Manufacture, execution and replay: `BLOCKED:ggen_binary_unavailable` in an environment without a ggen binary. Nothing here is ALIVE and no Level-5 claim is made; see [Level-5 maturity contract](level5-maturity-contract.md).
- The only input a real ggen would consume from this repository is the synthetic qualification overlay. The residual of the retail-lending profile is rdflib-only evidence: the profile has never been manufactured through ggen, and [Add an industry to a closure](../how-to/add-an-industry-to-closure.md) states how a consumer wires it in.
