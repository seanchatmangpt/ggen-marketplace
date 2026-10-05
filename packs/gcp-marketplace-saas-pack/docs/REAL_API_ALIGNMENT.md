# gcp-marketplace-saas-pack — Real API Alignment (2026-10-03)

MP-gate honesty ledger, in the beam4pm-pro-entitlement-pack style: which
enums/shapes came from which Google document URL, what is generated, and what
stays BLOCKED until real Marketplace credentials exist.

## Verified sources (read 2026-10-03, not invented)

| Surface | Source URL | What was verified |
| --- | --- | --- |
| Entitlement states (8 values), Account states (3 values), resource fields | Live discovery doc: `https://cloudcommerceprocurement.googleapis.com/$discovery/rest?version=v1` (`Entitlement.State`, `Account.State`, Entitlement/Account schemas) | ENTITLEMENT_STATE_UNSPECIFIED, ENTITLEMENT_ACTIVATION_REQUESTED, ENTITLEMENT_ACTIVE, ENTITLEMENT_PENDING_CANCELLATION, ENTITLEMENT_CANCELLED, ENTITLEMENT_PENDING_PLAN_CHANGE, ENTITLEMENT_PENDING_PLAN_CHANGE_APPROVAL, ENTITLEMENT_SUSPENDED; ACCOUNT_STATE_UNSPECIFIED, ACCOUNT_ACTIVATION_REQUESTED (documented deprecated), ACCOUNT_ACTIVE |
| Lifecycle event types (13 admitted here), state transition table, Pub/Sub notification payload (eventId/eventType/providerId + account/entitlement {id, updateTime}) | `https://cloud.google.com/marketplace/docs/partners/integrated-saas/manage-entitlements` ("Manage customer entitlements for your SaaS product", last updated 2026-09-30 UTC per page footer) | Event types incl. ENTITLEMENT_CREATION_REQUESTED, ENTITLEMENT_OFFER_ACCEPTED, ENTITLEMENT_ACTIVE, ENTITLEMENT_PLAN_CHANGE_REQUESTED/CHANGED/CANCELLED, ENTITLEMENT_PENDING_CANCELLATION, ENTITLEMENT_CANCELLING, ENTITLEMENT_CANCELLATION_REVERTED, ENTITLEMENT_CANCELLED, ENTITLEMENT_RENEWED, ENTITLEMENT_OFFER_ENDED, ENTITLEMENT_DELETED; ACCOUNT_ACTIVE/ACCOUNT_DELETED for account tasks |
| Service Control report Operation | `https://docs.cloud.google.com/service-infrastructure/docs/service-control/reference/rest/v1/Operation` (+ services/report page) | operationId, operationName, consumerId (`project:PROJECT_ID`, `project_number:`, `api_key:` forms), startTime/endTime (RFC3339 Zulu), metricValueSets → MetricValueSet{metricName, metricValues[]} → MetricValue{int64Value, startTime, endTime}; duplicate-metric rejection constraint |
| Signup JWT claims | `x-gcp-marketplace-token` JWT, claims verified structurally; issuer constant taken from ash_a2a's hand-written `JwtValidator` (`https://www.googleapis.com/robot/v1/metadata/x509/cloud-commerce-partner@system.gserviceaccount.com`) | iss/sub/exp/aud structural checks only |

## Generated from ontology (ggen, oxigraph engine)

- `templates/gcp_validation.ex.eex` renders `gates/{010_event_transitions,
  020_entitlement_states,030_codegen}.rq` results into
  `<consumer module>.GeneratedValidation`: the 8-value state enum, the
  13-event transition table (empty resultingState = keep-current, still
  advances the watermark), watermark fold, Service Control payload builder,
  JWT structural checks.
- Semantics are beam4pm-proven (hand-designed-fold precedent), generated
  consumer-namespaced via the `gcp:CodegenConfig` individual.
- Consumer court:
  `/Users/sac/ash_pplan/test/marketplace_sim/gcp_contract_court_test.exs`
  (14 tests): lifecycle fold happy path / duplicate no-op / stale no-op /
  unknown-event-type refusal / anti-vacuity (empty fold != ACTIVE), report
  payload shape, JWT refusals, and byte-identical regeneration.

## BLOCKED (named, honest)

- **Seller account / Provider ID**: no real provider registration, so no live
  procurement events, no `usageReportingId`, no end-to-end marketplace run.
  Falsifier for unblocking: a real `providers/{id}` with an approved account
  and one live ENTITLEMENT_ACTIVE notification replayed through the fold.
- **Real Pub/Sub endpoint**: the notification ENVELOPE (eventId/eventType/
  providerId) is verified from the partner doc, but no subscription exists.
  The fold accepts plain maps, so an adapter for the base64 Pub/Sub push
  envelope is unwritten until a subscription can be pointed at a real URL.
- **JWT signature verification**: structural claim checks only; cryptographic
  verification against Google's public x509 keys requires JWKS fetch +
  key rotation handling, which is untestable without live tokens. Kept
  BLOCKED rather than faked.
- **Account-level events** (ACCOUNT_ACTIVE/ACCOUNT_DELETED): enumerated in
  the ontology (gcp:AccountState) but not folded into entitlement state —
  the documented transition table governs entitlements only.

## Deviations from Google's surface (disclosed)

- ENTITLEMENT_SUSPENDED is a reachable STATE but the partner doc lists no
  lifecycle eventType that sets it ("This is not yet supported" per the
  discovery doc) — the fold can represent the state but no generated event
  produces it.
- ENTITLEMENT_OFFER_ENDED / ENTITLEMENT_DELETED have no distinct state; they
  keep current status and advance the watermark (documented as commercial-
  term/tombstone facts).
- ENTITLEMENT_PENDING_PLAN_CHANGE (billing-cycle-completing plan change) is
  in the state enum and transition table, but no eventType maps directly to
  it — it is reached via Google's internal transition from
  ENTITLEMENT_PENDING_PLAN_CHANGE_APPROVAL, not by a partner-observable
  event. The fold's table mirrors the partner-observable events only.
