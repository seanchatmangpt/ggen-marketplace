# beam4pm-pro-entitlement-pack

Local, ggen-manufactured substrate for two beam4pm_pro MP-gate properties that are
genuinely testable without an external marketplace provider
(`docs/jira/v26.8.29/11-release-gates-receipts.md` in beam4pm):

- **MP3 Entitlement** — "beam4pm_pro receives/reconciles the provider's
  entitlement/order/agreement state idempotently."
- **MP6 Billing/metering** — "contract quantities/usage reconcile exactly;
  duplicate/reordered events do not double bill."

Schema-only pack (same contract as `beam4pm-pro-infra-pack`): reuses
`beam4pm-process-model-pack`'s `bpm:RecordType`/`bpm:Field` vocabulary verbatim and
ships **zero individuals of its own**. A consuming project mints its own
`entitlement_event` / `entitlement_state` / `usage_event` / `billing_reconciliation`
`bpm:RecordType` facts in its own `ontology.ttl`.

## Templates

- `templates/beam4pm_entitlement.{erl,ex}.tmpl` + `_test(s).{erl,exs}.tmpl` — struct/
  record generation (following `beam4pm_types.erl.tmpl`) plus a hand-designed
  `reconcile_entitlement/2` fold: applies an at-least-once, arbitrarily-reordered
  notification stream to one `entitlement_state` under a strict
  `(effective_at, event_id)` watermark. A replayed event or a stale out-of-order
  event is an exact no-op; a malformed `effective_at` or an empty `event_id` is a
  typed refusal (`validate_event_shape/1`), never silently dropped or applied.
- `templates/beam4pm_billing.{erl,ex}.tmpl` + `_test(s).{erl,exs}.tmpl` — struct/
  record generation plus a hand-designed `reconcile_billing`/`reconcile(events,
  entitlement_id, metric_name, {period_start, period_end})` fold: filters to one
  `(entitlement_id, metric_name)` partition **and** the caller-supplied half-open
  `[period_start, period_end)` window *before* deduplicating by `event_id` and
  summing. The period argument is what makes it impossible for the same event to
  be double-billed across two adjacent reconciliation calls.

## Real bugs found and fixed (2026-08-30)

Each fix below is independently checkable against the current code and its
regression test in this pack (`validate_event_shape/1`'s refusal tests;
`cross_period_double_bill_prevented_test` / the matching Elixir test), not
asserted from an unverifiable process description:

1. **MP3 severe**: an earlier revision validated only field *presence*, never
   format. A malformed `effective_at` (not a real ISO8601 string) sorted above
   any real timestamp under plain term order, permanently poisoning the
   watermark and silently dropping every subsequent real event with no error.
2. **MP3**: an event with `event_id: ""` and `effective_at: ""` collided with
   the initial state's own bottom sentinel watermark, so it was silently
   dropped even as the very first event for an entitlement.
3. **MP6 severe, a direct MP6 contract violation**: an earlier revision shipped
   `reconcile_billing/1` with no period argument at all, deriving
   `period_start`/`period_end` after the fact from each call's own input
   batch — silently dropping the exact anti-double-billing mechanism (an
   externally-supplied half-open period filter) the design mandated. A usage
   event landing on a period boundary (a realistic off-by-one query or
   at-least-once redelivery spanning a rollover) was counted in **both**
   periods' totals.

All three are fixed in the templates shipped here, with regression tests
(`validate_event_shape` refusal cases; `cross_period_double_bill_prevented_test`
/ `"cross-period double billing is prevented..."`) proving each fix, not just
asserting it.

## Standing

Both folds are verified against synthetic events only. MP3 and MP6 remain
`BLOCKED` on real Partner Procurement API access and a seller account — this
pack manufactures the adapters those gates will need and does not itself close
either gate. Named limits not solved here: the notification fold alone cannot
reach `ENTITLEMENT_SUSPENDED` (a reachable status with no corresponding event
type); `ENTITLEMENT_OFFER_ENDED`/`ENTITLEMENT_DELETED`'s downstream effects are
marked `UNVERIFIED` design choices requiring confirmation against the real API.
