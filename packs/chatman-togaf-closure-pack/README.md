# chatman-togaf-closure-pack

Semantic closure law for finishing Chatman Ecosystem projects at an enterprise-architecture lifecycle level rather than stopping at "code merged" or "artifact ALIVE".

This pack is **TOGAF-aligned**, not a copy of the TOGAF Standard. It encodes the lifecycle obligations discussed in the Chatman Ecosystem as RDF + native SPARQL refusal gates:

- target realization and architecture conformance;
- transition-architecture closure;
- replacement and sunset;
- retirement versus true decommission;
- consumer, access, data, runtime, and cost disposition;
- operations acceptance;
- registration of the target as the new baseline;
- continuing architecture-change watch;
- receipt-bound ERRC CREATE that must retire existing WIP;
- zero ambient DO authority.

## Core law

Evidence standing, project lifecycle, and asset lifecycle are orthogonal.

```text
EvidenceStanding: UNKNOWN | PARTIAL_ALIVE | ALIVE | BLOCKED | BUILD_BROKEN | UNSUPPORTED | REFUSED

ProjectLifecycle:
ARCHITECTING -> MIGRATION_PLANNED -> IMPLEMENTING -> CUTOVER
-> LEGACY_RETIREMENT -> CHANGE_GOVERNANCE -> CLOSED

AssetLifecycle:
PLANNED -> TRANSITION -> ACTIVE -> SUNSET_SCHEDULED
-> RETIRING -> RETIRED -> DECOMMISSIONED -> ARCHIVED
```

`ALIVE` therefore never means the enterprise project is closed.

A project may assert `tc:CLOSED` only when the pack's gates find no counterexample to the closure contract.

## Closure fixed point

For a closed project:

1. every target asset is `tc:ACTIVE`, has evidence standing `er:ALIVE`, is owned, has target-realization evidence, and has architecture-conformance evidence;
2. every transition architecture is `tc:TRANSITION_CLOSED` with closure evidence;
3. every displaced baseline asset has an explicit disposition;
4. a replacement disposition requires an admitted successor, a sunset date, and terminal asset state `tc:DECOMMISSIONED` or `tc:ARCHIVED`;
5. decommission controls explicitly cover consumer migration, writes, access, data, runtime, cost, evidence archive, and replacement completion;
6. every lifecycle obligation is terminal and evidence-backed;
7. operations has accepted ownership;
8. the realized target has been registered as the new baseline;
9. a continuing change watch has been registered;
10. no project carries `tc:DO` authority.

`tc:RETIRED` is intentionally insufficient for a replacement closure: it means the asset is no longer approved for normal use, but does not prove that infrastructure, credentials, data, spend, consumers, or retained evidence have been dispositioned.

## Explicit N/A

A decommission control may be `tc:NOT_APPLICABLE_WITH_EVIDENCE`. Omitting the control is not allowed. This keeps software-only, cloud, data, identity, contract, and repository projects on one closure calculus without inventing irrelevant work.

## ERRC integration

`tc:LifecycleObligation` is the enterprise WIP unit. It can carry:

- `tc:errcLane`;
- `tc:blockedDependents`;
- `tc:impactScore`;
- `tc:closesWip`.

The `tc:CREATE` lane is fail-closed: a CREATE obligation must name existing WIP it retires and must require a receipt. This prevents "CREATE" from becoming permission to manufacture speculative scope.

## Chatman Ecosystem examples

### anti-llm-cheat-lsp

A green WIP scanner release is target-realization evidence, not project closure. If it replaces older/manual WIP-discovery paths, closure additionally requires consumer migration, retirement/decommission of those paths, transition closure, operations ownership, baseline registration, and a change watch.

### ggen replacement

If `new-generator tc:replaces old-generator`, `new-generator` being ALIVE does not close the program. `old-generator` must be explicitly retained with decision evidence or replaced-and-decommissioned with the mandatory retirement controls terminal.

### generated closure evidence

Creating a receipt, archive bundle, baseline record, or conformance artifact is lawful `tc:CREATE` only when `tc:closesWip` identifies the existing closure gap it retires.

## Sources

- `ontology.ttl` — reusable lifecycle vocabulary and public-ontology alignment.
- `gates/*.rq` — fail-closed closure laws.
- `queries/closure_frontier.rq` — remaining enterprise WIP ordered by impact.
- `queries/retirement_frontier.rq` — displaced assets and their retirement/decommission status.
- `qualification/consumer.ttl` — positive, fully closed synthetic consumer used by marketplace qualification.

## Authority

The pack is SELECT/CONSTRUCT law. It does not merge pull requests, delete infrastructure, revoke credentials, destroy data, terminate contracts, publish releases, or otherwise actuate. DO remains external, independently admitted, and receipt-bound.
