# gcp-marketplace-saas-pack Standing

Standing: UNVERIFIED

No gate or sync output was observed in this authoring lane (build/test execution is
coordinator-owned). Nothing below is a claim of execution; the Observed-output section is a
slot the coordinator fills from the real run.

## Claim table

| claim | standing | evidence |
|---|---|---|
| Gate 010 refuses empty/missing-eventType/dangling-resultingState events | UNVERIFIED | `gates/010_event_transitions.rq` authored; no run observed |
| Gate 020 refuses empty family, missing stateValue, duplicate stateValue | UNVERIFIED | `gates/020_entitlement_states.rq`; no run observed |
| Gate 030 refuses missing/ambiguous CodegenConfig moduleName | UNVERIFIED | `gates/030_codegen.rq`; no run observed |
| `ggen sync run` in a scratch consumer exits 0 and renders 5 templates | UNVERIFIED | not run |
| Real-API alignment (`docs/REAL_API_ALIGNMENT.md`) | UNVERIFIED | prose only, no gate output |

## Template suffixes

Templates: `gcp_config.ex.tmpl` (Tera: `{% for %}` / `{{ }}`), and four `.ex.eex` files
(`gcp_endpoint`, `gcp_error_view`, `gcp_router`, `gcp_validation`; EEx: `<% %>` with Elixir
`fn` helpers). The suffix names the template dialect of the body; frontmatter is identical
(`to:`, `sparql:`). Migrating `gcp_config` to EEx or the rest to Tera is not done.

## Gate polarity

Each gate is a violation query: any row is a refusal, zero rows is admission. Non-vacuity
means each gate returns rows on a mutated ontology.

## Non-vacuity recipe (coordinator runs; copy `ontology.ttl` to scratch, mutate, query)

| gate | mutation to scratch copy of `ontology.ttl` | expected rows |
|---|---|---|
| 010 | delete the `gcp:eventType` triple of `gcp:ev_active`; also point one `gcp:resultingState` at an undeclared IRI | `missing-eventType`, `dangling-resultingState` |
| 020 | remove every `a gcp:EntitlementState` typing (empty family); or give two states the same `gcp:stateValue` | `empty-state-family` / `duplicate-stateValue` |
| 030 | remove the `gcp:CodegenConfig` individual; or give it a second differing `gcp:moduleName` | `missing-codegen-config` / `ambiguous-moduleName` |

Run each gate against original (expect zero rows) and mutated (expect non-empty), e.g.
`python3 gates/run_gates.py --witnesses` from the pack dir (existing gate-court.toml + witnesses/{pass,fail}/ implement this court).
Falsifier: identical output on original and mutated.

## Acceptance (coordinator)

1. Non-vacuity table above: original empty, each mutation non-empty.
2. Scratch consumer: `ggen.toml` referencing this pack, `ggen sync run` exits 0, outputs:
   `test/support/marketplace/gcp/generated_config.ex`, `gcp_web_endpoint.ex`,
   `gcp_web_error_view.ex`, `gcp_web_router.ex`, `gcp_generated_validation.ex`.
3. Paste real outputs into the section below and promote Standing to a closed-vocabulary
   value the output supports.

## Observed output

(empty — UNVERIFIED)

## Not done

`instances/` not created: the ontology embeds its individuals (events, states, CodegenConfig)
in `ontology.ttl`; no second instance has a grounded source.
