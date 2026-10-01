# How to triage an industry-closure residual

Use this procedure when a closure has a residual and you need to decide who acts on each row, record what changes, and keep the ledger honest. Exact contracts are in [Industry closure contract](../reference/industry-closure-contract.md). This page assumes you have a residual ledger from the packs (see [Generate an industry closure](../tutorials/generate-an-industry-closure.md)); the packs only propose changes and never perform them.

## 1. Read the ledger

Open `generated/industry-closure/residual-ledger.ttl` (or the feedback packet, `generated/industry-closure/feedback-packet.json`, which is flat JSON). For every residual note:

- the key, `<requirement id>--<capability key or UNMAPPED>`;
- the deficit class (the first failing link);
- the feedback target;
- the standing (UNKNOWN, or BLOCKED for authority).

Without a ggen binary, compute the same rows under rdflib by running `queries/10-residual.rq` over the ontology plus the consumer input; the tutorial shows how. Treat the ledger as a computed view: if it disagrees with the query, gate `060_residual_ledger.rq` refuses it, and the query is right.

Group by target, not by requirement. Each deficit class has exactly one target.

## 2. Route each class to its lane

| Class | Target | What to do | What counts as done |
|---|---|---|---|
| authority | `ic:UPSTREAM_AUTHORITY` | Nothing in this closure. Leave it open and `BLOCKED`. If you believe the need flag is wrong, correct the requirement, which is a human edit with a reason | the requirement no longer needs DO authority, or it remains blocked |
| ontology | `ic:UPSTREAM_KNOWLEDGE` | Map the requirement to a capability key, or admit another public source through the admission steps in [Add an industry to a closure](add-an-industry-to-closure.md) | the capability is grounded in an ADMITTED source |
| ABB | `ic:UPSTREAM_ARCHITECTURE` | Author an architecture building block that realizes the capability, or reuse an existing one. Merge the generated pending contract skeleton if it fits | an ABB realizes the capability |
| contract | `ic:UPSTREAM_ARCHITECTURE` | A named human reviews the skeleton and approves it, adding the approver and a receipt reference and an authority boundary | an APPROVED contract with approver, receipt and boundary governs the ABB |
| SBB | `ic:UPSTREAM_MARKETPLACE` | Survey the marketplace. Extend or compose an existing pack first. A new pack needs the class-closure justification in [Consolidate a pack family](consolidate-a-pack-family.md). Declare the SBB against the approved ABB | an SBB satisfies the ABB |
| qualification | `ic:UPSTREAM_QUALIFICATION` | Qualify the SBB through the real runtime and record the QUALIFIED standing with its pinned exact subject | the SBB is QUALIFIED with a pinned `sha256:` subject |
| evidence | `ic:UPSTREAM_QUALIFICATION` | Obtain execution evidence at the current exact subject from an independent verifier with a receipt | independent VERIFIED evidence at the current subject, none FALSIFIED |

Every change lands in the normal marketplace lanes by pull request and human adoption. PR CI stays read-only evidence and never rewrites source. A generated skeleton or work order is a candidate, never an approval.

For each OPEN residual there must be exactly one candidate work order (gate `100_sjira_workorder.rq`). The work order's acceptance and falsifier text come from the deficit class; read the falsifier first, because it tells you when the residual itself was wrong.

## 3. Record a receipted retirement (only when a capability should leave the ledger)

The ledger never shrinks silently. When a recorded coverage must go (its capability is withdrawn, or its ABB is replaced by a different ABB), add a retirement:

1. A retirement individual that retires the recorded coverage.
2. A non-blank reason.
3. A receipt digest in `sha256:` plus 64 lowercase hex.

Without all three, gate `040_closure_monotonicity.rq` refuses either the retirement or the next snapshot. Replacing the SBB under the same ABB needs no retirement: the identity of a coverage is the capability and its ABB.

## 4. Admit `closure-next`

After the factory change lands, re-run the pipeline. The chain now holds, the residual disappears by derivation rather than deletion, and `generated/industry-closure/closure-next.ttl` proposes the next snapshot: epoch plus one, superseding the head, with a coverage per carried or newly covered capability. Review it, then append it to the consumer's input.

Admission is by gates, not by trust. Run gates 030, 040, 050 and 055 and the residual and work-order gates 060 and 100 on the merged graph. A candidate coverage's standing is `UNKNOWN`; promoting it to a stronger standing is a separate act that gate 090 constrains.

## 5. Verify monotonicity

Before accepting the new snapshot, confirm all of these hold on the merged graph:

- the epoch is exactly the previous plus one with a single successor of the same closure (`030_snapshot_identity.rq`);
- every earlier (capability, ABB) pair is still recorded unless retired with a receipt (`040_closure_monotonicity.rq`);
- every LIVE head coverage still satisfies the full chain (`050_coverage_chain.rq`);
- every capability the chain calls covered is recorded LIVE in the head (`055_frontier_recorded.rq`).

## 6. Feed falsifying evidence back

When evidence at the SBB's current exact subject comes back FALSIFIED:

1. Record it as evidence with independent producer and verifier and a receipt. The evidence deficit reappears for that capability.
2. Re-mark the coverage STALE with a reason; do not delete it.
3. Make sure an OPEN residual exists for the requirement; otherwise gate `090_standing_evidence.rq` refuses the falsification as unfed.
4. Repair, re-qualify and obtain new VERIFIED evidence at the new current subject.

Evidence at a superseded subject is not joined, so success at another subject never repairs the current one.

## 7. Failure catalogue

When a gate refuses, find the code below and apply the repair. Re-run the gate under rdflib until it returns zero rows.

### Knowledge sources (`010_source_admission.rq`)

| Code | Repair |
|---|---|
| `REFUSED:IC_SOURCE_ADMISSION_INVALID` | set the admission to ADMITTED, EXCLUDED or UNKNOWN |
| `REFUSED:IC_SOURCE_PROVENANCE_MISSING` | add the missing source IRI, version, digest, licence boundary or locator, read from the vendored file |
| `REFUSED:IC_SOURCE_DIGEST_MALFORMED` | recompute with `sha256sum` and write `sha256:` plus 64 lowercase hex |
| `REFUSED:IC_SOURCE_NOT_VENDORED` | vendor the file under `ontologies/public/` and point the locator there |
| `REFUSED:IC_SOURCE_OUTSIDE_SCOPE` | move the source under the closure's bound path prefix, or widen the scope deliberately |
| `REFUSED:IC_SOURCE_EXCLUSION_UNREASONED` | add the exclusion reason |
| `REFUSED:IC_SOURCE_UNKNOWN_NO_FALSIFIER` | add a falsifier, or review and admit or exclude |

### Requirements (`020_requirement_identity.rq`)

| Code | Repair |
|---|---|
| `REFUSED:IC_REQUIREMENT_MALFORMED` | add the missing id, statement, disposition or closure |
| `REFUSED:IC_KEY_UNSAFE` | use only letters, digits, dot, underscore and hyphen |
| `REFUSED:IC_CAPABILITY_KEY_MISSING` | add a capability key to the required capability |
| `REFUSED:IC_REQUIREMENT_DISPOSITION_INVALID` | set IN_SCOPE or OUT_OF_SCOPE |
| `REFUSED:IC_REQUIREMENT_SILENT_DROP` | add a scope justification to the out-of-scope requirement, or put it back in scope |
| `REFUSED:IC_REQUIREMENT_DUPLICATE_ID` | give each requirement a unique id |
| `REFUSED:IC_REQUIREMENT_ORIGIN_UNADMITTED` | derive it from an ADMITTED source or an `ea:Strategy`; prose is not an origin |
| `REFUSED:IC_REQUIREMENT_CLOSURE_UNDECLARED` | declare the closure, or point the requirement at the closure it belongs to |
| `REFUSED:IC_NEEDS_DO_MALFORMED` | write the DO need as a boolean literal; any other value is read as a need and refused |

### Snapshots (`030_snapshot_identity.rq`)

| Code | Repair |
|---|---|
| `REFUSED:IC_CLOSURE_NO_SNAPSHOT` | add the epoch-0 snapshot |
| `REFUSED:IC_SNAPSHOT_EPOCH_MISSING` | add the epoch |
| `REFUSED:IC_SNAPSHOT_ORPHAN` | link the snapshot to its closure and, above epoch 0, to its predecessor |
| `REFUSED:IC_SNAPSHOT_EPOCH_SKIP` | make the epoch the predecessor's plus one |
| `REFUSED:IC_SNAPSHOT_FORK` | keep a single successor per snapshot |
| `REFUSED:IC_SNAPSHOT_CLOSURE_MISMATCH` | keep a chain within one closure |
| `REFUSED:IC_SNAPSHOT_MULTIPLE_HEADS` | keep one head: supersede one of the snapshots with the other, or remove the stray one |
| `REFUSED:IC_SNAPSHOT_EPOCH_DUPLICATE` | give each snapshot of a closure its own epoch |
| `REFUSED:IC_CLOSURE_BASEIRI_INVALID` | give the closure a plain `https` base IRI that ends in a slash and has no whitespace or quoting characters |

### Monotonicity (`040_closure_monotonicity.rq`)

| Code | Repair |
|---|---|
| `REFUSED:IC_CLOSURE_SHRINK` | carry the coverage into the next snapshot, or retire it with a receipt and reason |
| `REFUSED:IC_RETIREMENT_MALFORMED` | name the coverage the retirement retires |
| `REFUSED:IC_RETIREMENT_UNRECEIPTED` | add the receipt digest |
| `REFUSED:IC_RETIREMENT_UNREASONED` | add the reason |
| `REFUSED:IC_RETIREMENT_DIGEST_MALFORMED` | write the receipt digest as `sha256:` plus 64 lowercase hex |

### Coverage chain (`050_coverage_chain.rq`, `055_frontier_recorded.rq`)

| Code | Repair |
|---|---|
| `REFUSED:IC_COVERAGE_INCOMPLETE` | add the missing capability, ABB, SBB, snapshot or state |
| `REFUSED:IC_COVERAGE_STATE_INVALID` | use LIVE or STALE |
| `REFUSED:IC_COVERAGE_ABB_NOT_REALIZING` | cover only a capability the ABB realizes |
| `REFUSED:IC_COVERAGE_CONTRACT_NOT_APPROVED` | get the contract approved with boundary, or mark the coverage STALE with a reason |
| `REFUSED:IC_COVERAGE_SBB_MISMATCH` | bind an SBB that satisfies the coverage's ABB |
| `REFUSED:IC_COVERAGE_SBB_NOT_QUALIFIED` | qualify the SBB, or mark the coverage STALE with a reason |
| `REFUSED:IC_COVERAGE_SBB_UNPINNED` | pin the SBB's exact subject |
| `REFUSED:IC_SBB_SUBJECT_MALFORMED` | write the subject as `sha256:` plus 64 lowercase hex |
| `REFUSED:IC_COVERAGE_EVIDENCE_MISSING` | obtain independent VERIFIED evidence at the current subject, or mark STALE with a reason |
| `REFUSED:IC_COVERAGE_EVIDENCE_FALSIFIED` | mark the coverage STALE with a reason, repair and re-verify |
| `REFUSED:IC_COVERAGE_STALE_UNREASONED` | add the stale reason |
| `REFUSED:IC_SBB_SUBJECT_AMBIGUOUS` | keep one exact subject per SBB; a new subject is a new SBB version with its own evidence |
| `REFUSED:IC_FRONTIER_UNRECORDED` | admit `closure-next` so the head snapshot records the covered capability |

### Residual ledger and routing (`060_residual_ledger.rq`, `070_deficit_feedback.rq`)

| Code | Repair |
|---|---|
| `REFUSED:IC_RESIDUAL_UNRECORDED` | regenerate and merge the residual ledger |
| `REFUSED:IC_RESIDUAL_STALE_OR_MISCLASSIFIED` | regenerate the ledger; a recorded class that disagrees with the computed one is stale |
| `REFUSED:IC_RESIDUAL_ORPHAN` | remove a recorded residual whose requirement is out of scope or gone, or restore the requirement's scope |
| `REFUSED:IC_RESIDUAL_DUPLICATE_KEY` | keep one OPEN residual per key and per (requirement, capability) pair; regenerate the ledger |
| `REFUSED:IC_RESIDUAL_UNCLASSIFIED` | give the residual a deficit class |
| `REFUSED:IC_RESIDUAL_MULTICLASS` | keep exactly one class |
| `REFUSED:IC_RESIDUAL_NO_FEEDBACK` | add the feedback target of its class |
| `REFUSED:IC_FEEDBACK_MISROUTED` | use the target the class routes to |
| `REFUSED:IC_AUTHORITY_BLOCK_NOT_BLOCKED` | set the authority residual's standing to `BLOCKED` |
| `REFUSED:IC_AUTHORITY_BLOCK_UNREASONED` | add a blocked reason |
| `REFUSED:IC_RESIDUAL_STANDING_PROMOTED` | set the residual's standing to UNKNOWN or BLOCKED |

### Authority fence (`080_authority_fence.rq`)

| Code | Repair |
|---|---|
| `REFUSED:IC_AUTHORITY_DO_FORBIDDEN` | remove the DO ceiling, claim, class or grant flag (a grant flag is accepted only as a typed boolean false); DO is not representable here |
| `REFUSED:IC_AUTHORITY_CEILING_INVALID` | use NONE, OBSERVE, SELECT or CONSTRUCT |
| `REFUSED:IC_AUTHORITY_CLAIM_MISSING` | add an authority claim of `NONE` |
| `REFUSED:IC_AUTHORITY_CLAIM_NOT_NONE` | set the claim to `NONE` |
| `REFUSED:IC_CONTRACT_APPROVAL_UNATTRIBUTED` | have a named human add the approver and approval receipt, or set the status back to pending |

### Standing and evidence (`090_standing_evidence.rq`)

| Code | Repair |
|---|---|
| `REFUSED:IC_STANDING_INVALID` | use only the repository's standing vocabulary |
| `REFUSED:IC_STANDING_ALIVE_WITHOUT_EVIDENCE` | attach receipted, verified, independently attributed evidence, or lower the standing |
| `REFUSED:IC_STANDING_STALE_SUBJECT` | use evidence at the SBB's current subject, or lower the standing |
| `REFUSED:IC_STANDING_SYNTHETIC_ALIVE` | use OBSERVED evidence, or lower the standing; synthetic never supports ALIVE |
| `REFUSED:IC_STANDING_ALIVE_PACK_UNBOUND` | bind the SBB to a marketplace pack and its catalog digest, or lower the standing |
| `REFUSED:IC_STANDING_ALIVE_NOT_LIVE` | lower the standing, or restore the coverage to LIVE through re-verification |
| `REFUSED:IC_STANDING_ALIVE_FALSIFIED` | lower the standing; FALSIFIED evidence at the current subject rules ALIVE out |
| `REFUSED:IC_STANDING_EVIDENCE_FOREIGN` | cite evidence whose `ic:evidenceFor` is the coverage's own SBB |
| `REFUSED:IC_EVIDENCE_MALFORMED` | add the missing field or fix the receipt digest |
| `REFUSED:IC_EVIDENCE_NOT_INDEPENDENT` | have a different agent verify |
| `REFUSED:IC_EVIDENCE_FALSIFICATION_UNFED` | record the OPEN residual the falsification reopens |

### Work orders (`100_sjira_workorder.rq`)

| Code | Repair |
|---|---|
| `REFUSED:IC_WORKORDER_MISSING` | regenerate the work orders |
| `REFUSED:IC_WORKORDER_MALFORMED` | add the missing id, residual, delta code, acceptance, falsifier, standing or claim |
| `REFUSED:IC_WORKORDER_FALSIFIER_BLANK` | restore the falsifier from the deficit class |
| `REFUSED:IC_WORKORDER_DUPLICATE_ID` | keep a unique work order id |
| `REFUSED:IC_WORKORDER_DUPLICATE_FOR_RESIDUAL` | keep exactly one work order per residual; regenerate them rather than adding one by hand |
| `REFUSED:IC_WORKORDER_ORPHAN` | point the work order at a residual, or remove it |
| `REFUSED:IC_WORKORDER_DELTA_MISMATCH` | use the delta code of the residual's class |
| `REFUSED:IC_WORKORDER_STANDING_PROMOTED` | set the standing to UNKNOWN or BLOCKED |

### Profile grounding (profile pack gate `010_profile_grounding.rq`)

| Code | Repair |
|---|---|
| `REFUSED:LND_CAPABILITY_CONCEPT_NOT_PROVIDED` | ground the capability in a source that provides its concept, or change the concept |
| `REFUSED:LND_CAPABILITY_CONCEPT_MISSING` | name the concept the grounded capability denotes |
| `REFUSED:LND_REQUIREMENT_SOURCE_NOT_IN_CLOSURE` | add the source to the closure's used sources through admission, or derive from a used one |
| `REFUSED:LND_SOURCE_NOT_FIBO_LOAN` | admit only sources of the vendored loan-ontology family in that closure, or use another profile |

For the strategy side, see the code table in [Enterprise operating model contract](../reference/enterprise-operating-model-contract.md). A residual on a strategy-derived requirement names the unmanufactured foundation element of the operating-model decision.

## Boundaries

- Triage proposes changes. It grants no authority; a requirement that needs DO authority stays `BLOCKED`.
- Historical success at another subject is not current evidence.
- The packs prove the gates under rdflib and the bounded qualification boundary; they do not prove native runtime success or customer outcomes.
