# L21 notes: hddl_operator

Standing: UNVERIFIED

## Files

- ontology.d/L21-hddl-operator.ttl, gates/L21_010_one_operator_per_skill.rq,
  gates/L21_020_fact_args_declared.rq, templates/L21_operators.ex.tmpl,
  fixtures/L21-legal.ttl (0 gate rows expected), fixtures/L21-refusing.ttl (rows expected).

## DSL evidence (ash_a2a)

- dsl.ex:153-186 entity schema (parameters, preconditions, add_effects, delete_effects; fact
  `{atom, [atom]}`); dsl.ex:196 nested under `skill`.
- verifiers/verify_hddl_operators.ex:11 (one operator per skill), :35 refused_hddl_multiple_operators,
  :13-14,61 refused_hddl_fact_args.
- chicago/fixtures/brce.ex:130-149 usage; `extensions: [AshA2A]` at brce.ex:28.

## Seam (coordinator)

Template emits `lib/<app_path>/<resource_file>_l21.ex`, module `<ResourceModule>.L21Operators`
(`Spark.Dsl.Fragment, of: Ash.Resource, extensions: [AshA2A]`), for resources with a skill that has
an `aap:hddlOperator`. Add to resource `use`: `fragments: [Demo.Flow.Phase.L21Operators]`.

Collision risk: the fragment re-declares `skill :name, :action` (identifier :name, dsl.ex:195). If
resource.ex.tmpl also emits that skill, either suppress the skill in the main template when it has
`aap:hddlOperator`, or drop the skill header here and merge the `hddl_operator` block into the main
skill block. The fragment carries `consequence` (aap:consequence) for the skill it declares; other
skill options (description, arguments, leases from other lanes) are NOT carried -- prefer the
merge-into-main option if the skill has any.

Gates run as SELECT-any-row = refuse; the existing gate runner for L07 applies.

## Query variables

resources(module_name app_path resource_file), skills(module_name skill_name action_name
consequence), params(module_name skill_name pname ord), facts(module_name skill_name role fact_ord
predicate fact_key), fact_args(module_name fact_key aname ord).

## Known gaps

- Facts keyed by skill/role/predicate/order: two same-predicate facts in one role need distinct
  aap:factOrder, else their args merge (gate does not check).
- Arg order within a fact is aap:argOrder; blank nodes without it sort as 0.
- Tera `filter(attribute=..)` nested in `for` over a `set` inside inline loops, and the `role` array
  literal loop, are unverified against ggen's Tera; coordinator sync is the court.
- Fragment-contributed `a2a` section in a fragment with `extensions: [AshA2A]` is unverified.
- Skill names/predicates/params are emitted as atoms; gate 020 enforces snake_case only.
