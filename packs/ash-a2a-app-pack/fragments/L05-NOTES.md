# L05 notes: identities and validations

Standing: UNVERIFIED

## Coordinator seam

Template `templates/L05_identities_validations.tmpl` emits, per resource that has any
`aap:identity` or `aap:validation`, `lib/<app_path>/<resource_file>_l05.ex` defining
`<module_name>.L05` (a `Spark.Dsl.Fragment` of `Ash.Resource`).

Add to the shared `resource.ex.tmpl` `use Ash.Resource` options, only for resources with L05 facts
(or unconditionally if the file is always generated; the resources query filters to those with facts):

    fragments: [{{ module_name }}.L05]

Demo: `fragments: [Demo.Desk.Ticket.L05]`.

Action-level validations are expressed as resource-level `validate ... where: [action_is(:name)]`
(`aap:forAction`), because the shared template owns the `actions do` block and fragments cannot
append to an existing action entity.

## DSL options modelled (deps/ash/lib/ash/resource)

- identity.ex:33-93: name, keys, where, nils_distinct?, eager_check?, eager_check_with,
  pre_check?, pre_check_with, description, field_names, message, all_tenants?
- validation.ex:145-186: validation, where, on, only_when_valid?, description, before_action?,
  always_atomic?; message passed through as opt.
- builtins.ex: present:282 absent:337 attributes_present:301 attributes_absent:375 match:253
  compare:239 numericality:233 one_of:22 string_length:193 attribute_equals:158
  attribute_does_not_equal:81 attribute_in:175 argument_equals:430 argument_does_not_equal:415
  argument_in:445 confirm:66 changing:52 action_is:143 (via aap:forAction);
  `raw` kind covers negate:93, is_valid, `{Module, opts}` custom validations.

## Gates

L05_identity_key_not_attribute, L05_identity_wellformed, L05_validation_wellformed,
L05_validation_attribute_not_attribute, L05_message_quotes.

## Known gaps

- Validation names order output (ORDER BY name); use numeric prefixes. The name is not emitted.
- byte_size:211 and the `where` negation helpers are only reachable via kind `raw`/`aap:where`.
- Identity `where` is a raw Elixir expr string; not validated.
- Key gate fails for attributes not declared as `aap:attribute` (e.g. relationship-generated ids).
- GROUP_CONCAT key order is unspecified (irrelevant to Ash semantics).
- Per-validation `message` is escaped by gate only (quotes forbidden), not by template.
- Action-scoped `validate` inside an action block (action-local `validate` entity) is unreachable
  until coordinator exposes an action fragment hook.
- Compile and ggen run not performed; Tera `filter(attribute=...)` on aggregated rows assumed
  to behave like the base resource.ex.tmpl usage.
