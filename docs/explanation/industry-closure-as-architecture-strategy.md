# Industry closure as architecture strategy

This page explains why three packs exist for turning public industry knowledge and enterprise strategy into measured, routable software gaps, and where their claims stop. It is explanation: it gives rationale, fences and exclusions. Exact contracts are in [Industry closure contract](../reference/industry-closure-contract.md) and [Enterprise operating model contract](../reference/enterprise-operating-model-contract.md). To learn by doing, follow [Generate an industry closure](../tutorials/generate-an-industry-closure.md).

All descriptions of external frameworks here are paraphrases of ideas, not quotations. The packs state their own modelling choices and mark which are interpretation (see "Interpretation versus source").

## The chain being modelled

```text
Public knowledge
  → Industry closure
  → Requirement
  → sJira (work order)
  → Marketplace
  → ggen
  → Qualified software
```

Read left to right, each arrow is a transition that either holds or leaves a visible gap:

1. **Public knowledge → industry closure.** A public ontology does not simply "apply" to an industry. It is admitted into one bounded scope: pinned by digest, licensed, vendored inside the repository, and inside that scope's path boundary. A source can instead be excluded with a reason, or left UNKNOWN with a falsifier. Admission is the only door.
2. **Industry closure → requirement.** A requirement is atomic, paraphrased, has a safe key and an explicit scope disposition, and has an admitted origin: an admitted source, or an enterprise strategy. Prose alone never originates one.
3. **Requirement → sJira.** Each unmet requirement becomes a candidate change record that carries its own acceptance text and a falsifier. The record is a projection of the gap, not a second source of truth.
4. **sJira → marketplace → ggen → qualified software.** The change lands in the ordinary marketplace lanes by pull request and human adoption. Only after a pack is qualified at an exact subject and independently verified does the requirement count as met.

The packs own the measuring of the gap and the typed routing of it. They do not own the work on the far side of each arrow.

## Why the gap is computed, not stored

Call the set of in-scope requirements R and the derived closure Cl, the set of capabilities for which a full chain holds. The residual is R minus Cl, with one extra rule: a requirement that needs consequential authority is in the residual no matter what else exists.

A stored list of "open gaps" would be a second source of truth. It would drift the moment a building block was approved or a qualification regressed, and nobody would know which copy to believe. So the pack derives the residual by query from the same graph the facts live in, and gate `060_residual_ledger.rq` forces any recorded ledger to equal the computed one. A recorded row is therefore a cache that is checked, never an authority that is trusted.

The chain a capability must satisfy has a fixed order, and the first failing link names the deficit:

| First failing link | Deficit | What it asks of the factory |
|---|---|---|
| the requirement needs consequential authority | authority | nothing, it stays blocked |
| no mapped, grounded capability | ontology | admit knowledge, or map the capability |
| no architecture building block | ABB | author or reuse one |
| no approved contract | contract | a named human decides |
| no solution building block | SBB | supply one from the marketplace |
| not qualified at a pinned subject | qualification | qualify through the real runtime |
| no independent evidence at the current subject | evidence | verify independently |

"First failing link" gives every gap exactly one class, so every gap has exactly one upstream target, and routing can be data on the class rather than logic in code. The seven-class table is the reference; the idea is that a deficit tells you which lane owns the next move.

## Why the ledger is monotone while currentness is re-earned

Two things are easy to confuse. One is the history of what the enterprise has once closed. The other is whether that closure is still true today.

- The **ledger** of snapshots and coverages only grows. A recorded coverage leaves it only through a receipted, reasoned retirement. This protects against silent loss of closure: an edit that quietly drops a covered capability is refused.
- **Currentness** is derived each time. If an SBB's exact subject changes, or evidence at the current subject is falsified, the derived residual reappears and the coverage is marked STALE, not deleted. The enterprise did close it once, it is not closed now, and both facts remain visible.

A swap of one qualified, evidenced SBB for another on the same ABB leaves the ledger intact because the identity of a coverage is the capability and its ABB, not the SBB. That is why a replaced implementation is growth or neutral, never shrinkage. Historical success at another subject is not evidence for the current one: evidence at a superseded subject is simply never joined.

## Strategy as the origin of requirements

The industry side answers what the world of an industry demands. The enterprise side answers what this enterprise has decided to be. The second needs its own semantics, and `enterprise-operating-model-pack` supplies them.

The core idea paraphrased: an enterprise chooses how integrated its business units are and how standardized their processes are. Two axes, two levels each, give four operating models:

| Model | Integration | Standardization | Plain meaning |
|---|---|---|---|
| Diversification | low | low | units run independently with their own processes |
| Coordination | high | low | units share data and still keep their own processes |
| Replication | low | high | units stay independent and run the same standard processes |
| Unification | high | high | one integrated enterprise on common processes and data |

The decision matters because it selects the **foundation for execution**: the core processes, shared data and linking automation the enterprise must actually have to run that model. Each foundation element supports a capability, so each one yields a requirement whose origin is a strategy rather than prose. That is what makes requirements derive from strategy.

The packs also model four **maturity stages** (silos, standardized technology, optimized core, modular business) as an ordered ladder, and an **engagement model** that joins enterprise-level governance, project-level governance and a linking mechanism. The stage gate refuses a maturity claim that skips a lower stage or lacks the foundation that stage presupposes. An enterprise therefore cannot claim a stage that its closure cannot evidence.

When a residual arises on a strategy-derived requirement, it names the unmanufactured foundation element. That is the strategic meaning of a technical deficit: this part of the chosen operating model has no qualified software behind it.

## The architecture development method as gates

The architecture development method (ADM) is modelled as an ordered cycle of phases from preparation through vision, business, information systems, technology, opportunities, migration planning, implementation governance and change management, with requirements management continuous across all of them.

The packs treat it as ontology plus gates, not as a diagram. Order is data (a predecessor chain). Each phase requires generic artifact kinds. A phase record may only be marked achieved if its artifacts exist, its predecessor was achieved in the same engagement, and a requirements review was recorded. Accepting a phase is thus a refusal-capable transition, not a status field anyone can set.

The ADM is also where the semantic seam to the existing `togaf-adm-pack` sits. Identity of phases is owned there; this pack joins by notation and adds the data that pack holds only as comments.

## Interpretation versus source

Not every statement in these packs has the same standing.

- **Source-shaped**: identity keys that join to `togaf-adm-pack` by notation, and the pinned public knowledge sources, which are digests of vendored files.
- **Interpretation**: the axis obligations (high standardization implies standard process variants, high integration implies enterprise-scope data, and the converse prohibitions), the maturity prerequisites per stage, the generic artifact kinds, and the choice to anchor capabilities to value streams. These are modelling choices a thoughtful consumer might disagree with. The relevant gates are flagged as interpretation in the reference and refusing under them proves only internal consistency of a decision with this model.

If a future need contradicts an interpretation, the repair is to change the interpretation in the canonical Turtle, gate and witness, not to patch generated output.

## Feedback loop

One turn from t to t+1:

1. Requirements enter with an admitted origin.
2. The residual is measured. The recorded ledger must equal it.
3. Each gap routes to its lane. Knowledge, architecture, marketplace, qualification and authority are five distinct upstream targets.
4. The factory change happens in the normal lanes by pull request and human adoption. This repository only proposes it; it does not perform it, and pull-request CI stays read-only evidence.
5. A re-run finds the chain holding. The residual disappears by derivation, not deletion, and the capability enters the frontier. A candidate next snapshot is proposed, and the consumer admits it by appending it to input.
6. The next snapshot must contain every earlier coverage unless retired with a receipt.
7. Execution evidence feeds back. Falsified evidence at the current subject reopens the evidence deficit, marks the coverage STALE, and is refused if it has no open residual to land in.

For an SBB gap the loop asks first to extend or compose an existing pack, and only second for a new one with class-closure justification. That follows the repository's rule of preferring class closure over proliferation; see [Class closure and consolidation](class-closure-and-consolidation.md) and [Pack classes](../reference/pack-classes.md).

## Authority fence

The repository keeps SELECT, CONSTRUCT and DO separate. Queries and gates select. Templates construct candidate Turtle and JSON. DO is not representable: no such ceiling, claim, class or grant can be expressed without a gate refusing it.

Three practical consequences:

- A requirement such as "disburse funds autonomously" is a recorded need, never a grant. It classifies as the authority deficit and stays blocked in this closure forever. Closing it needs a separately admitted consequential path outside these packs, and where a consumer uses BRCE that path remains BRCE.
- A generated contract skeleton is pending human approval. Approval needs a named human and a receipt, which are human acts that no template emits and a test enforces by checking templates never contain the approved token.
- Every generated residual, work order and skeleton claims no authority and a standing of unknown, or blocked for an authority gap.

Existence of a powerful artifact grants no authority. See [Security and authority](security-and-authority.md).

## Honest standing

The standing vocabulary is the repository's own and nothing is added: unknown, partial alive, alive, blocked, build broken, unsupported and typed refusals. The pack adds two guards on top.

- **Qualified is not alive.** QUALIFIED on a solution building block is a necessary link of the chain. A capability is covered only with independent verified evidence at the block's current exact subject. A coverage may be called alive only with observed, not synthetic, evidence and a block bound to a catalog pack entry.
- **Synthetic is not observed.** The fixtures that demonstrate closure use synthetic evidence. They prove the calculus behaves; they prove nothing about any real software.

For this change, the standing by dimension is partial for semantic source, admission, authority fence and composition, because Turtle parses and every gate executes against witnesses under rdflib, and unknown (or `BLOCKED:ggen_binary_unavailable` where no ggen exists) for manufacture, execution and receipt or replay. Nothing is alive and no Level-5 claim is made. The seven-dimension definition is in [Level-5 maturity contract](../reference/level5-maturity-contract.md) and the vocabulary in [Standing](../reference/standing.md).

## What the packs do not prove

- **Strategic fit.** Choosing an operating model is a human decision. The pack checks that the foundation is consistent with the stated axes, not that the axes were the right choice.
- **Decomposition adequacy.** That requirements and capabilities cover an industry well is a judgement the closure records, not one it makes.
- **Native runtime success.** Gates are proven with rdflib. How a real ggen engine treats existence checks inside bindings and property paths stays unproven until a real run on the exact subject.
- **Customer outcomes.** Closed requirements are about software readiness, not whether anyone benefited.
- **A real SBB.** The real industry profile ships no building blocks, so its starting closure is empty and its residual is honest: abb deficits and one blocked authority row.

## Non-equivalence of similarly named packs

Several packs share words with these. Similar names are not equivalence proof.

- `togaf-adm-pack` holds phase, model, stage and mechanism identity as a projection pack. It is consumed by notation and not edited.
- `enterprise-architecture-pack` owns the building block, contract and exact-subject vocabulary. It is consumed by IRI and not edited.
- `chatman-togaf-closure-pack` closes a per-project lifecycle. It is a different closure from industry closure and is not merged.
- Hollow operating-model labels elsewhere in the marketplace are cited as non-equivalent and are not changed.

## Why three packs and no edits

- A kernel owns the calculus because it is shared by every industry and by the enterprise-architecture family. Per-industry knowledge is data in a profile, not a new kernel.
- A capability pack owns the operating-model delta because its content is useful to consumers that never compute closure, and because the existing ADM pack models these concepts in a form that cannot be extended across files. The dependency runs from it to the kernel, never back.
- One profile pack proves the shape on a real, pinned industry. A second profile would be a sibling of the same shape. An umbrella is not warranted until at least two profiles exist.
- No existing pack is edited: each has its own maturity evidence, which an edit would invalidate, and the seam to them is a notation or IRI join guarded by a drift test.
- The sJira projection is folded into the kernel because nothing else consumes it yet. If a second ticket consumer appears, splitting it is justified; until then a third pack with a single dependency would be proliferation.

For the discipline behind these choices see [Class closure and consolidation](class-closure-and-consolidation.md), [Pack classes](../reference/pack-classes.md), and the procedure in [Consolidate a pack family](../how-to/consolidate-a-pack-family.md).
