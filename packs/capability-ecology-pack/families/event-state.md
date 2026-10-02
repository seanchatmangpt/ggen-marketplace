# capability-ecology-pack (event-state family)

Qualified capability contracts for the **event and observed-state family**, written for a
capability-resolution engine (ash_pplan v26.9.30) to resolve against. Namespace
`escap:` = `https://ggen.dev/ontology/event-state-capability#` (pinned in
`docs/jira/v26.9.30/RESOLUTIONS.md`).

## Identity

- Semantic source: `ontology.ttl`. Pack v0.1.0. `[pack]` carries name/version/description only
  (FM-PACK-003); no `shapes.ttl` (FM-PACK-012); gates are violation-row SELECTs (FM-PACK-013);
  every gate ends in `ORDER BY` (E0013).
- Pinned capability identities (dotted ID via `rdfs:label` AND `dcterms:identifier`; the corpus
  joins on the literal in the consumer resolver, not in-tree):
  `Event.Emit`, `Event.Subscribe`, `State.Observe`, `State.Query`.
- Minted siblings (same family namespace, recorded here): `Event.DeadLetter`,
  `State.Snapshot`. No other family's namespace was touched.

## CAPABILITY != IMPLEMENTATION

`escap:Capability` individuals are semantic identities. Provider packages appear only on
`escap:Realization` individuals with provider metadata (`escap:providerRepo`,
`escap:providerModule`, `escap:versionPinPolicy`), `>= 1` qualification condition, an evidence
requirement (state family), and — where the topic is consequential — a bound
`escap:authorityRequirement`. Realizations named here:

| capability | realizations (provider coordinate) |
|---|---|
| Event.Emit | `ash` Ash.Notifier -> Phoenix.PubSub notification; `telemetry (hex)` :telemetry.execute/3 |
| Event.Subscribe | `ash` pubsub subscription surface (Phoenix.PubSub.subscribe/2) |
| State.Observe | `telemetry_poller (hex)` periodic measures; `zcode-cli` src/ocel-tap.ts |
| State.Query | `otp` :ets.lookup/2; `ash` Ash.read/2 over an admitted read action |
| Event.DeadLetter | `ash` Ash.Notifier reroute to DLQ topic |
| State.Snapshot | `otp` :ets.tab2list/1 freeze |

Provider-coordinate honesty: `zcode-cli` src/ocel-tap.ts and the `xaas` OCEL emitter/sink
coordinates were **confirmed by direct read 2026-09-30**; `ash`, `telemetry`,
`telemetry_poller`, and `otp` coordinates are cited as public API surfaces **without local
inspection claims**. A version number is never the capability identity.

## Semantics admitted as graph facts

- Delivery (event family): `atLeastOnce` (duplicates possible, idempotent consumers),
  `exactlyOnce` (effect-once inside a declared dedupe window), `atMostOnce` (loss is a typed
  failure, never silent).
- Observation (state family): `monotonicObservedState` (observed state never regresses),
  `pointInTimeSnapshot`, `streamingTail`.
- Typed failures are individuals, not strings: duplicateDelivery, deliveryLoss,
  topicUnavailable, authorizationDenied, staleObservation, dedupeWindowExceeded,
  subscriberBackpressure.
- Each capability carries inputs, outputs, preconditions, postconditions, success outcome,
  typed failure outcomes, nondeterministic outcome set, evidence requirement, execution
  properties (durability / replay / isolation / concurrency).

## Authority: ProviderAvailable != Authorized

`State.Observe` is **non-consequential** (reading needs no authority). `Event.Emit` is
**consequential through its topic**: the topic individual carries
`escap:consequentialTopic true/false`, and the realization must carry an explicit
`escap:authorityRequirement` when emitting onto a consequential topic. `escap:providerAvailable
true` never discharges authority — gate 050 never reads that property. The worked instance
keeps the counterfactual alive: the same `Event.Emit` capability is admitted without authority
onto the non-consequential `runtime-metrics` topic and refused without authority onto
`order-lifecycle`.

Invariants encoded: Plan != Execution (a realization is an offer, not an execution), Policy !=
Authority, ProviderAvailable != Authorized, Projection != Source, Generated != Admitted.

## Gates and their witnessed refusals (anti-vacuity)

Refusal SELECTs — any returned row refuses. Each gate's firing negative fixture lives in
`qualification/fixtures/` and is executed for real (rdflib SPARQL) by
`tests/test_event_state_capability_pack.py`:

| gate | refuses | firing negative fixture |
|---|---|---|
| `gates/escap_010_capability_requires_realization.rq` | capability with no realization | `escap_negative-capability-without-realization.ttl` (Event.Throttle) |
| `gates/escap_020_realization_requires_qualification.rq` | realization with no qualification condition | `escap_negative-realization-without-qualification.ttl` |
| `gates/escap_030_delivery_semantics_required.rq` | event capability without deliverySemantics / state capability without observationSemantics | `escap_negative-delivery-semantics-missing.ttl` (Event.Broadcast) |
| `gates/escap_040_observation_requires_evidence.rq` | state-family realization without an evidence requirement | `escap_negative-observation-without-evidence.ttl` (blind observer) |
| `gates/escap_050_consequential_requires_authority.rq` | consequential-topic emit with no bound authority | `escap_negative-authority-unbound-consequential-topic.ttl` (providerAvailable true, still refused) |

`escap_positive-conforming-instance.ttl` (exactly-once `Event.Forward` onto a consequential topic
WITH bound authority) must stay silent under every gate, alone and unioned with the ontology.

## Ladder (REUSE -> COMPOSE -> EXTEND -> INVENT) and failed edges

- REUSE: `qce:` (qualified-capability-ecology-pack) is the canonical lifecycle
  (`rdfs:seeAlso qce:CapabilityVersion` / `qce:QualifiedCapability`); public
  `prov:`/`dcterms:`/`skos:`/`earl:`/`xsd:`; APS standing individuals remain the standing
  vocabulary.
- COMPOSE attempt, recorded failed edge: `packs/process-intelligence-pack` (`pi:`) models
  `pi:Event` as a process-mining event-log FACT (activity + object relations), not a capability
  (no delivery semantics, no realization/qualification/authority structure), and its graph is
  not part of this pack's qualification union, so no gate could join on it. Composed instead at
  the semantic-mapping level: the OCEL-tap realizations here produce `pi:Event`-shaped records
  downstream (noted in the realization comments), with `pi:` untouched.
- COMPOSE attempts, recorded failed edges: `control-plane-causality-observability-pack` (`cpc:`),
  `temporal-truth-observability-pack` (`mem:`), and `run-protocol-observability-pack` (`rpo:`)
  are observability-FACT vocabularies (runs, receipts, memory records as dqv measurements).
  None expresses a capability contract (no Capability/Realization/delivery-semantics/authority
  classes). Authority vocabulary reuses the OBSERVE/VERIFY distinction conceptually through the
  consequential/consequentialTopic split, not by import.
- EXTEND/INVENT: this family pack is the wave-charter extension of `qce:` — the contract shape
  (inputs/outcomes/semantics/realizations) `qce:` deliberately does not carry.

## Evidence boundary

Marketplace admission and real-ggen qualification only. Nothing here executes; holding a
capability contract confers zero authority. Standing: see the final lane report.
