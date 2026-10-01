# observation-capability-pack

Evidence-first qualified capability contracts for the **observation and telemetry family**,
written for a capability-resolution engine (ash_pplan v26.9.30) to resolve against. Namespace
`ocap:` = `https://ggen.dev/ontology/observation-capability#` (pinned in
`docs/jira/v26.9.30/RESOLUTIONS.md`).

## Identity

- Semantic source: `ontology.ttl`. Pack v0.1.0. `[pack]` carries name/version/description only
  (FM-PACK-003); no `shapes.ttl` (FM-PACK-012); gates are violation-row SELECTs (FM-PACK-013);
  every gate ends in `ORDER BY` (E0013).
- Pinned capability identities (dotted ID via `rdfs:label` AND `dcterms:identifier`; the corpus
  joins on the literal in the consumer resolver, not in-tree):
  `Observation.Tap`, `Observation.Sample`, `Telemetry.Emit`.
- Minted sibling (same family namespace, recorded here): `Observation.Flush` (drain buffered
  observations to an evidence sink; consequential through a consequential sink). No other
  family's namespace was touched.

## Evidence-first law

Every realization of an observation capability (`ocap:ObservationCapability`) MUST state its
`ocap:evidenceRequirement` — the receipt or observation record that proves the observation
happened — and names the record kinds it yields via `ocap:produces`. A tap that cannot produce
evidence is REFUSED by gate 040 in two shapes: no evidence requirement at all
(observation-without-evidence) or `ocap:evidenceCapable false` declared outright
(evidence-incapable-realization).

Evidence record kinds (each anchored to public EARL via `rdfs:seeAlso earl:Assertion`, with the
EARL mapping stated on the kind): `ocel2EventLine`, `receiptChainEntry`,
`telemetryMeasurement`, `sampleDatapoint`, `earlAssertion`.

## EARL composition (public vocabulary before custom)

Verification semantics reuse W3C EARL (`http://www.w3.org/ns/earl#`): an evidence record must
be re-expressible as an `earl:Assertion` whose `earl:subject` is the observed surface and whose
`earl:result`/`earl:outcome` (passed / failed / not-tested) is the verification verdict.
Recorded failed edge: EARL carries NO delivery-semantics, authority, or realization vocabulary,
so `ocap:` extends EARL rather than misusing it — the extension terms live in this family's
namespace only.

## CAPABILITY != IMPLEMENTATION

Realizations named here:

| capability | realizations (provider coordinate) | evidence produced |
|---|---|---|
| Observation.Tap | `zcode-cli` src/ocel-tap.ts; `xaas` ocel_ash_emitter.ex; `telemetry (hex)` :telemetry.attach/4 | OCEL 2.0 line + receipt-chain entry; OCEL 2.0 line; telemetry measurement |
| Observation.Sample | `telemetry_poller (hex)` periodic measures | sample datapoint per tick |
| Telemetry.Emit | `telemetry (hex)` :telemetry.execute/3; `xaas` ocel_ndjson.ex append path | telemetry measurement; OCEL 2.0 line |
| Observation.Flush | EARL-assertion commit to an audit evidence sink (vocabulary coordinate) | earlAssertion + commit receipt |

Provider-coordinate honesty: `zcode-cli` src/ocel-tap.ts, `xaas`
lib/xaas/telemetry/ocel_ndjson.ex, and `xaas` lib/xaas/telemetry/ocel_ash_emitter.ex were
**confirmed by direct read 2026-09-30**; `telemetry`, `telemetry_poller`, and the EARL
vocabulary coordinate are cited **without local inspection claims**. A version number is never
the capability identity.

## Delivery semantics and authority

Delivery semantics are declared per capability: `atLeastOnce` (bus tap), `atMostOnce`
(synchronous telemetry dispatch; handlerCrash/handlerNotAttached are typed failures),
`exactlyOnce` (position-keyed flush), `sampleMayDrop` (sampling fidelity bound, declared —
never silent).

ProviderAvailable != Authorized mirrors the sibling event-state pack: `Telemetry.Emit` and
`Observation.Flush` are consequential **through their sink** (`ocap:consequentialSink` on the
stream individual). The worked instance keeps the counterfactual alive: the same
`Telemetry.Emit` capability is admitted without authority onto the non-consequential
`runtime-telemetry` stream and refused without authority onto `audit-evidence`. Invariants
encoded: Plan != Execution, Policy != Authority, ProviderAvailable != Authorized, Projection !=
Source, Generated != Admitted.

## Gates and their witnessed refusals (anti-vacuity)

Refusal SELECTs — any returned row refuses. Each gate's firing negative fixture lives in
`qualification/fixtures/` and is executed for real (rdflib SPARQL) by
`tests/test_observation_capability_pack.py`:

| gate | refuses | firing negative fixture |
|---|---|---|
| `gates/010_capability_requires_realization.rq` | capability with no realization | `negative-capability-without-realization.ttl` (Observation.Aggregate) |
| `gates/020_realization_requires_qualification.rq` | realization with no qualification condition | `negative-realization-without-qualification.ttl` |
| `gates/030_delivery_semantics_required.rq` | capability without deliverySemantics | `negative-delivery-semantics-missing.ttl` (Telemetry.Batch) |
| `gates/040_observation_requires_evidence.rq` | observation realization without evidence requirement (shape A) / evidence-incapable realization (shape B) | `negative-observation-without-evidence.ttl` (blind tap); `negative-evidence-incapable-tap.ttl` |
| `gates/050_consequential_requires_authority.rq` | consequential-sink emit with no bound authority | `negative-authority-unbound-consequential-sink.ttl` (providerAvailable true, still refused) |

`positive-conforming-instance.ttl` (exactly-once `Observation.Profile` on a non-consequential
stream) must stay silent under every gate, alone and unioned with the ontology.

## Ladder (REUSE -> COMPOSE -> EXTEND -> INVENT) and failed edges

- REUSE: `qce:` lifecycle canonical (`rdfs:seeAlso qce:CapabilityVersion` /
  `qce:QualifiedCapability`); public `prov:`/`dcterms:`/`skos:`/`earl:`; public EARL for
  verification semantics (see failed edge above).
- COMPOSE attempt, recorded failed edge: `packs/process-intelligence-pack` (`pi:`) models
  event-log FACTS, not capability contracts (no Capability/Realization/delivery/
  evidence-requirement structure), and its graph is not in this pack's qualification union, so
  gates cannot join on it. The OCEL realizations here produce records consumable by `pi:`
  downstream (mapping noted on the record kinds), with `pi:` untouched.
- COMPOSE attempts, recorded failed edges: `control-plane-causality-observability-pack`
  (`cpc:`), `temporal-truth-observability-pack` (`mem:`), `run-protocol-observability-pack`
  (`rpo:`) are observability-FACT vocabularies; none expresses capability contracts or
  evidence-requirement law. Their receipt/observation FACTS are the downstream consumers of
  this pack's observation records, not competing vocabularies.
- EXTEND/INVENT: this family pack is the wave-charter extension of `qce:` — the evidence-first
  contract shape `qce:` deliberately does not carry.

## Evidence boundary

Marketplace admission and real-ggen qualification only. Nothing here executes; holding a
capability contract confers zero authority. Standing: see the final lane report.
