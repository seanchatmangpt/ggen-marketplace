# L12 notes: custom Ash types

Standing: UNVERIFIED

## Seam

Add to each resource that has `aap:typedAttribute` facts (resource.ex.tmpl `use Ash.Resource`):

    fragments: [{{ module_name }}.TypesL12]

Fragment file: `lib/<appPath>/<resourceFile>_l12.ex`. Types compile before resources
(Elixir resolves module deps), but `Ash.Type.Enum`/NewType modules are referenced by name only.
Alternative if coordinator prefers: add `aap:typedAttribute` rows to resource.ex.tmpl directly.

## Vocab (ontology.d/L12-types.ttl)

CustomType (typeKind enum|newtype|typed_struct|embedded|union), TypeField, UnionMember,
TypedAttribute; props typeRef, isArray, allowNil, defaultValue, typeConstraints, enumValue,
subtypeOf, unionStorage/unionTag/unionTagValue, a2aExposed.

## DSL grammar cited

- NewType: deps/ash/lib/ash/type/new_type.ex:17,26,30,112-113 (subtype_of, constraints, lazy_init?)
- Enum: deps/ash/lib/ash/type/enum.ex:20,48 (`use Ash.Type.Enum, values: [...]`)
- TypedStruct: deps/ash/lib/ash/typed_struct.ex:17-24 (`typed_struct do field ... end`)
- Union: deps/ash/lib/ash/type/union.ex:18-64 (storage, types, tag, tag_value)
- Embedded: `use Ash.Resource, data_layer: :embedded`, `defaults [..., create: :*, update: :*]`
- A2A serializability: ash_a2a verify_skills.ex:47-59 (@known_unserializable),
  :522-536 (module-form primitives incl. Ash.Type.Struct serializable), :557-561 (custom module
  types => `{:unknown, _}` warn, not error). So generated enum/newtype/union/embedded types
  warn on A2A-exposed arguments; gate L12_010 errors only on the hard-unserializable list.

## Gates

- L12_010 unserializable leaf type (opt-out `aap:a2aExposed "false"`)
- L12_020 type well-formedness
- L12_030 exactly-one type source per field/member/attribute

## Known gaps

- Tera `filter(attribute=..)` string-equality on module_name assumed as in resource.ex.tmpl.
- Enum value descriptions/labels (`description/0`, `label/0` callbacks) not modelled.
- Custom hand-written Ash.Type callbacks (cast_input etc.), `Ash.Type.Struct` with `instance_of`
  constraints, union `:map_with_tag` tag-value literal escaping beyond Elixir term literals.
- Embedded resources: no calculations/validations/changes/identities; no per-field
  `allow_nil` for `create: :*` accept customization.
- Whether verify_skills warns can be silenced is not modelled; warns are unchanged.
- Fragment must be listed by coordinator; no skill-argument-level serializability join (gate 010
  is per-type, not per-skill-reachability).
