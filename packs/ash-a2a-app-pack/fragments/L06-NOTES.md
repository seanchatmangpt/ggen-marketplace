# L06 notes

Standing: UNVERIFIED

## Coordinator wiring

Add to the resource `use Ash.Resource` options in resource.ex.tmpl (only for resources that have
`aap:l06Action`; the generated module is `<ResourceModule>.L06` at
`lib/<appPath>/<resourceFile>_l06.ex`):

    fragments: [{{ module_name }}.L06]

Fragment compile order: fragment modules must compile before the resource; Elixir resolves this
through the compiler tracer. Fixture needs `Demo.Desk.Ticket` fragments: `[Demo.Desk.Ticket.L06]`.
Fixture `aap:accept ""` yields `accept([])`-less output (no accept line) - fine.
`ex:L06_assign` references `watchers` relationship absent from the fixture (compile gap, by design:
relationships lane owns it; drop that action when building without it).

## Templates (one output each)

- `templates/L06_fragment.ex.tmpl` (for_each resources) -> `lib/<app>/<res>_l06.ex`
- `templates/L06_hook.ex.tmpl` (for_each hooks) -> `lib/<app>/<hook_file>.ex`
- `templates/L06_run.ex.tmpl` (for_each runs) -> `lib/<app>/<run_file>.ex`

## DSL cited (deps under /Users/sac/ash_a2a/deps/ash/lib/ash/resource)

- primary?, transaction?, description, public?, touches_resources: actions/shared_options.ex:14,23,19,40,29
- require_atomic? update.ex:78 / destroy.ex:88; atomic_upgrade? update.ex:85
- generic action returns/constraints/allow_nil?/run: actions/action/action.ex:70-98
- argument name/type/allow_nil?/public?/default/constraints: actions/argument.ex:23-65
- set_attribute change/builtins.ex:156; set_new_attribute :267; atomic_update :247; atomic_set :206;
  increment :122; manage_relationship :305
- build preparation: preparation/builtins.ex:39 (filter/sort/limit modelled as build opts)
- change opts where/on/only_when_valid?: change/change.ex:32,39,59
- Change callback change/3: change/change.ex:316; Preparation prepare/3: preparation/preparation.ex:139
- hooks: changeset.ex:7378 before_action, :7441 before_transaction, :7530 after_action,
  :7666 after_transaction
- Implementation run/3: actions/action/implementation.ex:60

## Known gaps

- `atomic?` is not an action option in this Ash (it is the `atomic?/0` change callback);
  modelled as require_atomic?/atomic_upgrade? only.
- manage_relationship step defaults opts to `type: :append_and_remove`.
- L06 actions are separate from `aap:action`; a primary read in both would conflict. Names must
  be unique across both sets (no gate cross-checks this without shared ontology access).
- Hook bodies / run bodies are Elixir text in the graph (escape hatch, not typed).
- No validations, no `change where:` expression typing, no `before_action` option passing
  (`prepend?`), no read `pagination`/`get?`, no `manual` actions, no `reactor(...)` run form.
- Generic-action `argument` order in fragment is alphabetical (SPARQL order by name).
- Gates L06_020/L06_030 are unexecuted; verify at `ggen graph validate` (fixture should return 0 rows).
