# ERRC-R3-crosslane

Standing: UNVERIFIED (authored without running ggen; coordinator sync/validate is the court)

ERRC R3 (Reduce cross-lane collisions). Single-lane gates (`L01_020`, `L08_010`, `L14_010/020`,
`L17_105`, ...) each see one lane's edges. The `gates/X_*.rq` family sees the union of lanes and
returns one row per violation with a readable `?reason` column. Each gate is a plain SPARQL
SELECT; any returned row is a refusal. Every example below uses these prefixes:

    @prefix aap: <https://ggen.dev/ash-a2a-app#> .
    @prefix ex:  <https://example.org/demo#> .

Common base used by most examples:

    ex:dom a aap:Domain ; aap:moduleName "Demo.Domain" ; aap:appPath "demo" ;
      aap:domainFile "domain" .
    ex:res a aap:Resource ; aap:moduleName "Demo.Ticket" ; aap:inDomain ex:dom ;
      aap:resourceFile "ticket" .

## Gate index

| gate | collision caught | columns |
|---|---|---|
| X_010 | duplicate Elixir module name across lanes (incl. derived suffix modules) | module, claimants, reason |
| X_020 | two lanes emit the same output path | path, claimants, reason |
| X_030 | action name clash across action, manage, l06Action, reactorAction | resource, action, claimants, reason |
| X_040 | field name clash across attribute, attrSpec, typedAttribute, FK, calc, aggregate | resource, field, claimants, reason |
| X_050 | fragment entity names (identity/validation, policy, oban, skill) | resource, namespace, entity, claimants, reason |
| X_060 | L13 state attribute type or shadowing mismatch | resource, state_attribute, reason |
| X_070 | L07 policies vs L17 authorizer vs lease_required skills | resource, skill, reason |
| X_080 | L14 trigger/schedule action not declared by any lane | resource, entity, property, missing, reason |
| X_090 | L11 publication/bridge/delegate and L13 transition action not declared | resource, entity, property, missing, reason |
| X_100 | L08 tenant attribute missing, clashing, or duplicated multitenancy | resource, tenant_attr, reason |

## X_010 module name duplicate

Claims: `aap:moduleName` on any subject, `calcModule`, `actionImplModule`, `serverModule`,
`taskStoreModule`, `structModule`, `endpointModule`, `reactorFragment`, plus derived modules
(`<Res>.Relationships`, `.L01Attributes`, `.CalculationsL03`, `<Res>Aggregates`, `.L05`, `.L06`,
`.L07Policies`, `.TenancyL08`, `.DataLayer`, `.L11PubSub`, `.TypesL12`, `.StateMachine`, `.L14Oban`,
`.SparkL18`, `.A2aL17`, `.ControlPlaneL16`, `<Domain>.MountsL08`, `<Agent>.Configured`,
`<Endpoint>.Router`, `<Ext>.Persist/.Info/.Verify`, `<Reactor>.Steps.<impl>`). A derived
module only counts when its lane has data for the owner.

Minimal trigger (a hand-named L06 hook colliding with the derived `.L06` fragment):

    ex:res aap:l06Action ex:act .
    ex:hook a aap:L06Hook ; aap:moduleName "Demo.Ticket.L06" .

Second trigger (resource and enum sharing a name):

    ex:enum a aap:EnumType ; aap:moduleName "Demo.Ticket" .

## X_020 output path duplicate

Rebuilds each template `to:` path (`lib/<appPath>/<file>.ex`, lane suffixes `_l01`..`_l18`,
`_a2a_l17`, and the `types/ calculations/ reactors/ reactor_actions/ pplan/` families).
Not claimed: L15 step files (step name is template-derived), L10 `_l10` siblings, L09 config files.

Minimal trigger (enum file stem equals resource file stem):

    ex:enum a aap:EnumType ; aap:moduleName "Demo.Status" ; aap:inDomain ex:dom ;
      aap:enumFile "ticket" .

Second trigger (stem aliasing a lane sibling: resource `ticket` with attrSpec emits
`ticket_l01.ex`):

    ex:res aap:attrSpec ex:a1 .
    ex:other a aap:Resource ; aap:moduleName "Demo.Other" ; aap:inDomain ex:dom ;
      aap:resourceFile "ticket_l01" .

## X_030 action name clash

Per resource, `aap:name` over `aap:action | aap:manage | aap:l06Action | aap:reactorAction`.

    ex:res aap:action ex:a1 ; aap:l06Action ex:a2 .
    ex:a1 aap:name "close" ; aap:actionType "update" .
    ex:a2 aap:name "close" ; aap:actionType "update" .

Same shape with `aap:manage` or `aap:reactorAction` instead of `aap:l06Action`.

## X_040 field name clash

Claims: legacy `aap:attribute`, `attrSpec`, `typedAttribute`, L02 relationship `aap:name`,
L02 belongs_to FK (`aap:sourceAttribute`, default `<name>_id`, skipped when
`aap:defineAttribute "false"`), L08 `relName` and `relSourceAttribute`, L03 calculation,
L04 aggregate.

Minimal trigger (L02 belongs_to generates `org_id`, L01 also declares it):

    ex:res aap:relationship ex:rel ; aap:attrSpec ex:spec .
    ex:rel aap:name "org" ; aap:relKind "belongs_to" ; aap:destination ex:org .
    ex:spec aap:name "org_id" .

Second trigger (calc named like an attribute):

    ex:res aap:attribute ex:a ; aap:calculation ex:c .
    ex:a aap:name "title" ; aap:ashType "string" ; aap:primaryKey "false" .
    ex:c aap:name "title" ; aap:calcKind "expr" ; aap:ashType "string" .

## X_050 fragment entity name clash

Namespaces per resource: `identity/validation` (L05), `policy` (policy, policyGroup, fieldPolicy;
L07 joins checks by name), `oban` (trigger + schedule), `skill` (`aap:skill`, `aap:skillSpec` via
`aap:specName`, L15 `reactorSkill`).

Minimal trigger (identity and validation share a name):

    ex:res aap:identity ex:i ; aap:validation ex:v .
    ex:i aap:name "unique_slug" ; aap:identityKey "slug" .
    ex:v aap:name "unique_slug" ; aap:validationKind "present" .

Second trigger (policy and field policy share a name):

    ex:res aap:policy ex:p ; aap:fieldPolicy ex:fp .
    ex:p aap:name "admin" .
    ex:fp aap:name "admin" ; aap:fields "secret" .

## X_060 state machine attribute type

State attribute is `aap:stateAttribute` or `state`. AshStateMachine auto-adds it only when no
attribute of that name exists. Rows when a lane declares it with a non-atom `ashType`, a module that
is neither atom nor a declared enum/custom type, an array, a non-`attribute` kind, a typeRef to a
non-enum type, or when a calculation/aggregate/relationship takes the name.

Minimal trigger (state declared as string):

    ex:res aap:stateMachine ex:sm ; aap:attribute ex:a .
    ex:sm a aap:StateMachine .
    ex:a aap:name "state" ; aap:ashType "string" ; aap:primaryKey "false" .

## X_070 lease authorizer cross-lane

`verify_skills.ex:487` ignores fragment-contributed authorizers, so only `aap:authorizer` (L17)
satisfies `lease_required?`. Rows: (A) lease skill plus L07 policies, no `aap:authorizer`;
(B/B2) L15 `reactorSkill` lease with no `aap:authorizer` (L17_105 does not cover reactorSkill);
(C) L07 policies plus `aap:authorizer` that omits `Ash.Policy.Authorizer`.

Minimal trigger A:

    ex:res aap:skill ex:s ; aap:policy ex:p ; aap:action ex:a .
    ex:s aap:name "commit" ; aap:ofAction "commit" ; aap:description "d" ; aap:leaseRequired "true" .
    ex:p aap:name "open" .

Minimal trigger C:

    ex:res aap:policy ex:p ; aap:authorizer "My.Other.Authorizer" .
    ex:p aap:name "open" .

## X_080 oban action undeclared

Trigger refs (`obAction`, `obReadAction`, `obWorkerReadAction`, `obOnError`) and schedule refs
(`obAction`, `obReadAction`) must match a name in `aap:action | aap:manage | aap:l06Action |
aap:reactorAction`. Supersedes `L14_010/L14_020` for multi-lane resources.

    ex:res aap:obTrigger ex:t .
    ex:t aap:name "sweep" ; aap:obAction "expire" .

No action named `expire` in any lane, so one row. Declaring it as `aap:l06Action` clears it.

## X_090 notifier action undeclared

Refs: `aap:pubAction`, `aap:bridgeAction`, `aap:delegateAction`, and `aap:viaAction` (except `*`).
`aap:pubExcept` is a comma list and is not split (known gap).

    ex:res aap:pubSub ex:ps .
    ex:ps aap:publication ex:pub .
    ex:pub aap:pubAction "approve" ; aap:pubEvent "approved" .

Transition variant:

    ex:res aap:stateMachine ex:sm .
    ex:sm aap:smTransition ex:tr .
    ex:tr aap:viaAction "approve" .

## X_100 tenant attribute clash

Rows: `missing` (tenantAttribute declared by no lane, including L01 attrSpec, L12 typedAttribute,
L02 FK incl. default `<name>_id`), `clash` (more than one field claim on the name), and two
`aap:multitenancy` sections on one resource. Supersedes `L08_010` for multi-lane resources.

Minimal trigger (missing; adding `ex:res aap:attrSpec [ aap:name "org_id" ]` clears X_100):

    ex:res aap:multitenancy ex:mt .
    ex:mt aap:tenantStrategy "attribute" ; aap:tenantAttribute "org_id" .

Clash trigger (attribute plus L08 foreign key both define `org_id`):

    ex:res aap:multitenancy ex:mt ; aap:attrSpec ex:spec ; aap:relationship ex:rel .
    ex:mt aap:tenantStrategy "attribute" ; aap:tenantAttribute "org_id" .
    ex:spec aap:name "org_id" .
    ex:rel aap:relName "org" ; aap:relDestination "Demo.Org" ; aap:relSourceAttribute "org_id" .

## Overlap with single-lane gates

- `L01_020`: attrSpec vs legacy only; X_040 is the superset. Both stay.
- `L08_010`: false-fires when the tenant attribute comes from L01/L02; prefer X_100.
- `L14_010/020`: false-fire when the action comes from L02/L06/L15; prefer X_080.
- `L17_105`: leaves reactorSkill leases unchecked; X_070 closes that.

## Known gaps

- L10 `.L10`/`_l10` derived modules and paths, L09 config paths, and L15 step file names are not
  claimed in X_010/X_020.
- X_050 does not compare validation/identity names against attribute names.
- Boolean-like literals are compared via `STR(?x) = "true"` so plain and typed booleans both match.
- No engine run: variable-predicate `VALUES` rows and nested `GROUP_CONCAT` subqueries rely on
  ggen 26.11.5 SPARQL 1.1 support (UNVERIFIED).

## See Also

- `LANES.md`
- `fragments/L01-NOTES.md` through `fragments/L20-NOTES.md`
