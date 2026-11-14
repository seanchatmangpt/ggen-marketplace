# L24 notes: read actions with get? / get_by

Coordinator seam. Add to the `frags` query in `templates/resource.ex.tmpl`:

```sparql
{ ?r aap:l24Read ?x . ?x aap:actionType "read"
  BIND("24" AS ?frag_ord) BIND("L24" AS ?lane) BIND(".L24Get" AS ?suffix) }
```

Fragment file: `lib/<appPath>/<resourceFile>_l24.ex`, module `<Module>.L24Get`.

## DSL cited (deps/ash/lib/ash/resource/actions/read.ex)

- `get?` boolean, default false: 70-76
- `get_by` wrap_list atom; sets get? true, adds argument + filter per field: 83-89

## Gates

- L24_010: get?/get_by on non-read action
- L24_020: get? read with no getByKey and no resolvable getIdentity
- L24_030: getByKey not an aap:attribute of the resource

## Known gaps

- aap:attrSpec (L01) attributes are not consulted by L24_030; only aap:attribute.
- Identity-derived keys come from GROUP_CONCAT; key order is engine-dependent.
- Multi-key get_by does not enforce identity uniqueness; unique-key proof is not modeled.
- Resource sharing an action name with a legacy aap:Action is not gated (duplicate action).
