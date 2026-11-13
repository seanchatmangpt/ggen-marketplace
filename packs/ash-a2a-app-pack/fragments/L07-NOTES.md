# L07 notes: Ash.Policy.Authorizer

Standing: UNVERIFIED

## Files

- ontology.d/L07-policy.ttl, templates/L07_policies.ex.tmpl, gates/L07_010..040_*.rq,
  fixtures/L07-policies.ttl.

## Seam (coordinator)

Template emits `lib/<app_path>/<resource_file>_l07.ex`, module `<ResourceModule>.L07Policies`,
a `Spark.Dsl.Fragment, of: Ash.Resource, authorizers: [Ash.Policy.Authorizer]` (authorizers is a
many-extension kind, deps/spark/lib/spark/dsl/fragment.ex:28-60). Add to the resource `use` in
resource.ex.tmpl, for resources having policies (fixture: Demo.Desk.Ticket):

    fragments: [Demo.Desk.Ticket.L07Policies]

Also add `authorizers: [Ash.Policy.Authorizer]` to the resource `use Ash.Resource` options if
`ash_a2a` verify_skills (lib/ash_a2a/verifiers/verify_skills.ex:488, refused_lease_required_no_authorizer)
does not see fragment-contributed authorizers; safe to declare in both places.
Resources with policies need the actor passed on agent calls; actor-less calls are forbidden.

## DSL options covered (authorizer.ex)

policy :140 (condition arg, description, access_type, error_message), bypass :278, policy_group :221,
authorize_if/forbid_if/authorize_unless/forbid_unless :72-138, policies.default_access_type :329,
field_policy :339 / field_policy_bypass :375 (fields, condition), field_policies.private_fields :446.
Checks: always, actor_present, action_type, action, actor_attribute_equals, accessing_from,
relates_to_actor_via (path via comma), expr (raw text in checkArg; used for `expr(...)`).

## Query variables

resources(module_name app_path resource_file default_access private_fields), groups(module_name
group_name kind arg arg2), policies(module_name policy_name ord group bypass kind arg arg2
access_type errmsg), checks(module_name policy_name ord check_type check_kind carg carg2),
field_policies(module_name fp_name ord fields bypass kind arg arg2), field_checks(module_name
fp_name ord check_type check_kind carg carg2).

## Known gaps

- `check` with custom Ash.Policy.Check modules (SimpleCheck/FilterCheck) and `{Mod, opts}` tuples not
  modeled (use kind fallthrough `kind(arg)` only).
- Policy conditions are single; compose with policy_group (group + condition become a list).
- Nested policy_group not modeled; ordering across groups vs ungrouped: groups emitted first.
- Fixture `ex:tId/tTitle` etc. omit `aap:Resource` fields beyond existing ontology; fixture uses blank-node checks
  whose checkOrder defines order. `expr` raw text is trusted (no escaping).
- `description("...")` uses policy name; embedded quotes unescaped.
- Gate 010/030 coverage matches condKind action/action_type/always only; group conditions are ignored.
- Tera macro `self::ref` and `containing` test unverified against ggen's Tera; coordinator build
  is the court. Fallback: inline per-kind if/elif.
- Policies on resources with `policy` but no `a2a` skills still emit; resources without any
  policy emit no file (query inner-joins aap:policy).
