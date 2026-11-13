# L13 notes: AshStateMachine on the A2A task lifecycle

## Coordinator seam

Add to the resource DSL header (resource.ex.tmpl, for resources having `aap:stateMachine`):

    fragments: [{{ module_name }}.StateMachine]

Emitted module: `lib/<app_path>/<resource_file>_l13.ex`
(`use Spark.Dsl.Fragment, of: Ash.Resource, extensions: [AshStateMachine]`; the `extensions:`
option on fragments is documented at deps/spark/lib/spark/dsl/fragment.ex:14). The host
resource keeps `extensions: [AshA2A]`. AshStateMachine auto-adds the `:state` atom attribute
(one_of all states, default = default_initial_state) when the resource lacks one
(transformers/add_state.ex:26-44), so the resource template needs no state attribute.

Actions named in transitions must exist on the resource (verifiers/verify_transition_actions.ex);
transitions are update actions, the initial one is a create.

## DSL options covered (file:line in deps/ash_state_machine/lib)

state_attribute ash_state_machine.ex:90; initial_states :95; default_initial_state :100;
extra_states :83; deprecated_states :76; transition action/from/to :29-46 (incl. `:*`
via aap:fromAny/toAny); transition_state change builtin_changes.ex:13 emitted as
`change(transition_state(:x), where: [action_is(:a)])` (aap:transitionTarget).

## Gates

010 unreachable (path `(^fromState/toState)+`, skipped when wildcards present),
020 undeclared states, 030 terminal with outgoing, 040 default not initial / no initial,
050 A2A vocabulary (task_lifecycle.ex:29,50) and terminal assertion.

## Known gaps

- `next_state` change (builtin_changes.ex:20), `AshStateMachine.Charts` flow chart output,
  and `possible_next_states` wiring into a2a skills are not modeled.
- `where: [action_is/1]` on a resource-level `changes` block is UNVERIFIED (no compile run).
- Two transitions of one action with different transitionTarget would stack conflicting
  changes; no gate yet.
- A2A `rejected`/`auth_required` producers are runtime-decided (task_lifecycle.ex:13-22);
  the pack only fixes legality, not which handler produces them.
- Template uses Tera `filter(attribute="target")` to detect presence; verify it treats
  unbound OPTIONAL as absent in ggen 26.11.5.
