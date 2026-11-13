# ERRC-R4-full-fixture

Standing: UNVERIFIED

Subject: `/Users/sac/ggen-marketplace/packs/ash-a2a-app-pack/fixtures/FULL-app.ttl`. One helpdesk
consumer graph (ETS data layer, no Repo, no database) built only from terms the lane fixtures and
`ontology.ttl` already use. Authored without Bash: no `ggen graph validate`, no `ggen sync`, no
SPARQL run. Every gate row below was evaluated by reading the gate against the fixture.

## Lanes exercised

| lane | exercised by |
|---|---|
| L01 | enum TicketStatus; Ticket attrSpec status/labels/timestamps/closed_at/api_token |
| L02 | Ticket notes/ticket_tags/tags/ticket_watchers/watchers/tasks; manage tag_ticket; Tag, TicketTag, Person, TicketWatcher, Org |
| L03 | Ticket display (concat); Note shout (expr + argument), label (module) |
| L04 | Ticket note_count, has_notes, latest_note, tag_labels |
| L05 | Ticket identity unique_title + 4 validations; Tag identity unique_label |
| L06 | Ticket close, touch, recent, count_open (+Run), stamp, assign; hook AuditClose |
| L07 | Ticket policy group, 5 policies, 2 field policies, authorizer |
| L08 | Ticket attribute multitenancy (global), org owner via L08 terms, mount, task store |
| L09 | ETS data layer on every resource (postgres/sqlite/mnesia arms not exercised) |
| L10 | domain config, 2 resource interfaces, calc interface, domain interface, mountOf |
| L11 | PubSub (close, escalate, destroy), PubSubServer, Notifier with A2ABridge |
| L12 | enum, newtype, typed_struct, embedded; Ticket typedAttribute requester/resolution |
| L13 | TicketTask 8-state A2A lifecycle |
| L14 | start_submitted trigger, nightly_triage schedule, 3 queues, ObanConfig, DeliveryWorker |
| L15 | Reactor TriageTicket (4 steps), ReactorAction triage, reactorSkill triage_ticket |
| L16 | workflow, 2 providers, pack, target, Ticket and TicketTask control planes |
| L17 | domain cards, skillSpecs, hookRefs, agent exec config, mount, endpoint, dispatch hooks |
| L18 | Helpdesk.Audit extension, watch entity, Ticket instance |
| L19 | `eaDeclare "true"` on the project |
| L20 | identity court, 4 policy cases, transition case, reactor case, plan case, shim court |

## Seam resolutions chosen

- L06 `watchers`: Ticket relationship `watchers` (many_to_many through TicketWatcher) added.
- Ticket tenant FK: declared once through L08 terms (`relName`, `relSourceAttribute`) only. A
  node carrying both L02 and L08 terms double-claims `org` and `org_id` in X_040 and X_100.
- Mount: one Mount node with `mountOf` Helpdesk (L10_030 requires it on every Mount), hung on
  Gateway via `aap:mount`, agent `forDomain` Helpdesk (L17_124 not triggered).
- No `pubType "create"` publication and no Delegate, so generated create tests need no PubSub
  process and no hand-owned delegate module.
- Hook refs sit on TicketTask (no skills there), so generated dispatch tests never reach
  `Helpdesk.Hooks`.
- Ticket multitenancy is `global? true`, so court calls without a tenant succeed.

## Per-gate table

| gate set | status | note |
|---|---|---|
| L01..L19 single-lane gates | satisfied by reading | shapes copied from lane fixtures |
| L20 gates | satisfied by reading | legacy actions only in cases; unique caseFile/shimName |
| X_010 module duplicate | satisfied | all moduleName values unique; derived suffixes distinct |
| X_020 output path | satisfied | all stems unique under appPath helpdesk |
| X_030 action clash | satisfied | Ticket: 3 legacy, 1 manage, 6 L06, 1 reactor, all distinct |
| X_040 field clash | satisfied | org / org_id claimed once (L08 terms only) |
| X_050 entity names | satisfied | skills, specNames, reactorSkill, policies all distinct |
| X_060 state attribute | satisfied | no `state` field declared on TicketTask |
| X_070 lease/authorizer | satisfied | Ticket has authorizer `Ash.Policy.Authorizer` |
| X_080 oban actions | satisfied | start, read, submit exist on TicketTask |
| X_090 notifier/transition | satisfied | close, escalate on Ticket; 8 via-actions on TicketTask |
| X_100 tenant attribute | satisfied | org_id claimed once; one multitenancy section |

## Residuals (not gate rows)

1. `templates/L08_domain_mounts.ex.tmpl` emits `mount(agent: <IRI>)` from an IRI-typed
   `?agent`; L17_124 forces `mountAgent` to be an `aap:Agent` IRI. Query must select moduleName.
2. MountsL08 and A2aL17 fragments both emit `transport do mount` for Gateway (duplicate mount).
3. The L10_030 vs L17_124 conflict passes only through the mountOf-vs-edge-domain split.
4. Oban runtime needs a hand-owned `Helpdesk.Repo` and application supervision; PubSubServer
   child, AshOban config and Endpoint child are not generated.
5. `Helpdesk.Hooks`, `Helpdesk.Support.CommandHandler` are hand-owned; no template emits them.
6. Create actions on Ticket require `org_id`; generated create properties supply values only
   if the L20 template draws UUIDs for accepted FK attributes (UNVERIFIED).
7. Unexercised: L09 postgres/sqlite/mnesia, L11 Delegate, L12 union, L08 context strategy.
8. Not run: Turtle parse, `ggen graph validate`, sync, compile, courts.

## Coordinator

Run `ggen graph validate` on the pack with FULL-app.ttl, then the pack sync, then each gate;
any returned row is a refusal and this table is wrong for that row.
