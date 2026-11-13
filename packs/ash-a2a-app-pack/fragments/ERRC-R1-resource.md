# ERRC-R1 resource.ex.tmpl fragments wiring

Standing: UNVERIFIED

## Files

- `templates/resource.ex.tmpl` (rewritten header, two new queries `frags`, `notifiers`)
- `fragments/ERRC-R1-resource.md`

## Query variables

- `frags`: `module_name frag_ord lane frag` (one row per resource x fragment, DISTINCT,
  ordered by module, lane ordinal). Tera: `my_frags | filter(attribute="module_name", ...)`;
  L09 presence via `filter(attribute="lane", value="L09")` (string compare, no numeric).
- `notifiers`: `module_name notifier` (second query, beyond "one": L11 seam requires
  `simple_notifiers:` in the `use` line).

## Trigger predicates (resource `?r`)

| Lane | Fragment emitted | Trigger |
|---|---|---|
| L01 | `.L01Attributes` | `aap:attrSpec` |
| L02 | `.Relationships` | `aap:relationship` or `aap:manage` |
| L03 | `.CalculationsL03` | `aap:calculation` |
| L04 | `Aggregates` (no dot) | `aap:aggregate` |
| L05 | `.L05` | `aap:identity` or `aap:validation` |
| L06 | `.L06` | `aap:l06Action` |
| L07 | `.L07Policies` | `aap:policy` (policyGroup/field policies alone do not emit) |
| L08 | `.TenancyL08` | `aap:multitenancy` with `aap:tenantStrategy` |
| L09 | `.DataLayer` | `aap:dataLayer` |
| L10 | `.L10` | `?i aap:interfaceOf ?r`, `aap:defineInterface`, `aap:interfaceDomain`, `aap:resourceInterfaceNamespace` |
| L11 | `.L11PubSub` | `aap:pubSub` with `aap:pubSubModule` |
| L12 | `.TypesL12` | `aap:typedAttribute` |
| L13 | `.StateMachine` | `aap:stateMachine` |
| L14 | `.L14Oban` | `aap:obTrigger` or `aap:obSchedule` |
| L15 | value of `aap:reactorFragment` | requires `aap:reactorFragment` + `aap:reactorFragmentFile` + `aap:reactorAction` (same as L15 template) |
| L17 | `.A2aL17` | `aap:skillSpec`, `authGate`, `leaseDurationMs`, `hookRef`, `semanticRequests`, `authorizer` |
| L18 | `.SparkL18` | `aap:sparkInstance` |
| notif | `simple_notifiers:` | `aap:notifier/aap:moduleName` or `aap:simpleNotifier` |

Each trigger mirrors that lane's own `resources`/`for_each` query so a listed fragment always
has an emitted file (drift risk: if a lane changes its trigger, change the matching branch).

## Dropped redundancy

- `data_layer: Ash.DataLayer.Ets` omitted when L09 fragment exists; kept otherwise.
- `extensions: [AshA2A]` kept always (legacy `a2a do` block needs it). No `authorizers:`,
  `AshStateMachine`, `AshOban` were ever on the use line; fragments (L07/L13/L14/L18) carry them.
- Minimal demo (legacy attribute/action/skill only): `frags` empty, output identical to before.
  Empty `attributes do end` / `actions do end` still emitted as before.

## Fragment module-name inconsistencies

- L04: `<Res>Aggregates` (no dot) vs every other lane's `<Res>.X`. Wired verbatim as emitted.
  Normalizing to `<Res>.AggregatesL04` requires editing `templates/L04_aggregates.ex.tmpl:51`
  and then the `CONCAT` in the L04 branch here.
- Unsuffixed, collision-prone names: L02 `.Relationships`, L09 `.DataLayer`, L13 `.StateMachine`
  (inconsistent with `...L03/L08/L12`-style suffixes; `.StateMachine` also near AshStateMachine
  naming). Files: `L02_relationships.ex.tmpl:69`, `L09_data_layer_fragment.ex.tmpl:67`,
  `L13_state_machine.tmpl:63`.
- Mixed suffix forms: `.L01Attributes`, `.L05`, `.L06`, `.L10`, `.L07Policies`, `.TenancyL08`,
  `.CalculationsL03`, `.TypesL12`, `.L11PubSub`, `.L14Oban`, `.SparkL18`, `.A2aL17`. All wired
  as emitted; no wiring bug, only naming drift.
- L15 fragment module is free text from `aap:reactorFragment` (no resource prefix guarantee).
- File-name drift: L14 `_l14_oban.ex`, L17 `_a2a_l17.ex` (harmless).

## Tera / ggen 26.11.5 risks

- `filter(attribute=..., value=...)` on rows (already used by this template; chained second filter
  on a filtered array for `l09`).
- `{% set x = ... | filter(...) -%}` then `x | length == 0` in `{% if %}`.
- `{% if %}` fragments inside a multi-line `use` argument list (whitespace/comma placement relies
  on inline `{% if %}...{% endif %}` without trim markers).
- SPARQL: large UNION with per-branch `BIND` after triples, `CONCAT(STR(..))`, `SELECT DISTINCT`
  over bound constants; `?frag_ord` is a string ("01".."18") so ORDER BY is lexical-correct.

## Residuals

- L07: base no longer declares `authorizers:`; ash_a2a verify_skills (`verify_skills.ex:488`)
  may not see fragment-contributed authorizers. L17 fragment also declares authorizers via
  `aap:authorizer`.
- L09: if Spark rejects `data_layer:` inside a fragment, fallback in `L09-NOTES.md` (emit
  `data_layer: <module>` in this template instead).
- L10 domain-side `use Ash.Domain ... fragments:` is outside this file (domain.ex.tmpl).
- Duplicate action/attribute names across legacy `aap:action`/`aap:attribute` and fragments are
  gated by lane gates, not here. Nothing run (no Bash).
