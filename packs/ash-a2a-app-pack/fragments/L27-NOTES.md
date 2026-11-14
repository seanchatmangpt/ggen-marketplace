# L27 dispatch test notes

Standing: UNVERIFIED

`templates/L27_dispatch_test.exs.tmpl` emits `test/<agent_file>_dispatch_test.exs` per agent.

## Dispatcher contract used

- `AshA2A.Dispatcher.dispatch(skill_name, %Message{}, resource_or_domain, history, auth_identity, opts)`
  at `/Users/sac/ash_a2a/lib/ash_a2a/dispatcher.ex:164-171`.
- Input read from the first `Part.Data` (`fetch_input/1`, dispatcher.ex:655-663).
- `:read` runs `Ash.Query.for_read |> Ash.read` (dispatcher.ex:789-799) with `authorize?: true`
  and a nil actor (`build_opts/2`, dispatcher.ex:761-773).
- List replies are `{:reply, [%Part.Data{data: %{results: rows}}]}` (`wrap_for_part_data/1`,
  dispatcher.ex:1174-1176); rows are public-attribute maps with atom keys (`encode_result/1`,
  dispatcher.ex:1142-1146).

## Selection and skip rules

READ skill = legacy `aap:Skill` whose `aap:ofAction` names an `aap:Action` with
`aap:actionType "read"` on the same resource. L17 `aap:skillSpec` skills are not covered.

Skipped with `@tag skip: "L27-SKIP ..."` (visible in ExUnit output):

- `aap:leaseRequired "true"` (CapabilityRelease guard, dispatcher.ex:321-322).
- `aap:consequence` other than `observe` (sole-DO and kernel fence, dispatcher.ex:332-334).
- resource has any `aap:policy` (nil actor under `authorize?: true`, dispatcher.ex:768).

## Record setup

First `aap:Action` of type create on the resource is called with `Ash.create(authorize?: false)`.
Sample values by `aap:ashType`: string, integer, boolean, float, uuid; other accepted types are
omitted. Asserts the created primary key appears in the reply, plus each string attribute value.
No create action: reply shape only.
