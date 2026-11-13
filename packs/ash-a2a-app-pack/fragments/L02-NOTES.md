# L02 relationships notes

Files: `ontology.d/L02-relationships.ttl`, `templates/L02_relationships.ex.tmpl`,
`gates/L02_010..040_*.rq`, `fixtures/L02-relationships.ttl`.

## Seam (coordinator)

One fragment module per resource that has `aap:relationship` or `aap:manage`, emitted at
`lib/<app_path>/<resource_file>_l02.ex` as `<ResourceModule>.Relationships`. Add to the resource
template's `use Ash.Resource` line:

    fragments: [{{ module_name }}.Relationships]

only for resources in that set. Fragments must be compiled first (Spark handles ordering via
module dependency). In the fixture: Ticket, Note, Tag, TicketTag.

Gaps in the shared template this lane relies on:

- Resource template emits no `relationships`; the fragment owns it. Do not add one.
- `many_to_many` needs the join resource's `belongs_to` pair; fixture join resource keeps a uuid
  `id` pk (gate 010 requires a pk). Composite join pk: set `aap:relPrimaryKey "true"` on both
  belongs_to and relax gate 010 for join resources.
- Skills targeting a manage action (e.g. `tag_ticket`) fail shared gate 020 because the action is
  in `aap:manage`, not `aap:action`. Coordinator: extend gate 020 with
  `UNION { ?resource aap:manage ?m . ?m aap:name ?an }` or add `aap:action` rows.
- Fragment actions are appended to base actions; manage action names must not collide
  (gate L02-040 checks).
- `public?` defaults to `true` in the template (A2A/RPC visibility); set `aap:relPublic "false"`.
- Domain must list both ends of every relationship (Ash verifies destination domain).

## DSL options modelled (deps/ash/lib/ash/resource/...)

- dsl.ex:237/269/301/336 entities has_one/has_many/many_to_many/belongs_to; args [:name,:destination]
- shared_options.ex: description:17, destination_attribute:21, source_attribute:32, public?:44,
  writable?:57, read_action:64, sort:95, no_attributes?:155
- belongs_to.ex: primary_key?:84, allow_nil?:90, define_attribute?:115, attribute_type:121
- many_to_many.ex: source_attribute_on_join_resource:75, destination_attribute_on_join_resource:80,
  through:85, join_relationship:89
- has_many.ex:84 / has_one.ex:83 `through` (path list, `aap:throughPath`), has_one allow_nil?:90
- dsl.ex:11 relationship `filter expr(...)` entity (multi-valued `aap:relFilter`)
- change/builtins.ex:296-305 `manage_relationship(arg, rel, opts)`: type, on_lookup, on_no_match,
  on_match, on_missing, use_identities; non-atomic so update gets `require_atomic?(false)`
  (change/manage_relationship.ex:44-49)

## Gates

010 dangling destination/through; 020 missing inverse (waive with `aap:noInverse "true"`);
030 shape (kind vocab, missing destination_attribute, join belongs_to pair, FK collision,
duplicate/attr-name collision); 040 manage_relationship validity.

## Known gaps

`validate_destination_attribute?`, `filterable?`, `sortable?`, `default_sort`, `manual`,
`not_found_message`, `violation_message`, `relationship_context`, `temporal_keys`,
`authorize_read_with`, `attribute_writable?`, `attribute_public?`, `attribute_always_select?`,
`from_many?`, `could_be_related_at_creation?`, `domain`, `read_action_arguments`;
`manage_relationship` `value_is_key`, `meta`, `ignore?`, `error_path`; inline
`manage_relationship` on base actions (only fragment-owned actions); `aggregates`/`calculations`
over relationships; `identities` (has_one uniqueness).
Unexercised: nothing compiled or run (no Bash).
