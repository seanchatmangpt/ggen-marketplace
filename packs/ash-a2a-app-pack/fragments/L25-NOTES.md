# L25 notes: destroy actions

Coordinator seam. In `templates/resource.ex.tmpl` add to the `frags` query:

```sparql
{ ?r aap:l25Destroy ?x .
  BIND("25" AS ?frag_ord) BIND("L25" AS ?lane)
  BIND(".L25Destroy" AS ?suffix) }
```

Fragment file `lib/<appPath>/<resourceFile>_l25.ex` is emitted only for resources with
`aap:l25Destroy`. Action names must not duplicate `aap:action` / `aap:l06Action` names; the
resource template also renders `destroy` for `aap:action` rows (resource.ex.tmpl:206-213) without
accept/soft, so L25 destroys are separate entities.

## DSL options cited (deps/ash/lib/ash/resource/actions/)

- soft?, manual, require_atomic?: destroy.ex:67, 72, 87
- accept via create/update opts "for soft destroys": destroy.ex:112-115
- manual forces require_atomic? false: destroy.ex:120
- primary?: shared_options.ex:14; accept: shared_options.ex:52
- struct defaults (require_atomic? true by default): destroy.ex:16

## Gate L25_010 refuses

accept on non-soft/non-manual; soft without timestamp attribute; timestamp attribute not declared
(`aap:attribute` or `aap:attrSpec` with `aap:name`); soft+manual; two primary destroys.

## Known gaps

- Not modeled: atomic_upgrade?, atomic_upgrade_with, reject, require_attributes, multitenancy,
  arguments/changes beyond the timestamp stamp (use L06 for those).
- Soft destroy stamps via `set_attribute(&DateTime.utc_now/0)`; non-atomic, so
  `require_atomic?: true` with soft destroy is the author's responsibility
  (Ash raises at compile if the change lacks atomic support).
- Primary-uniqueness check covers L25 destroys only, not those from resource.ex.tmpl/L06.
- Fixture reuses `aap:attribute` edge with `aap:primaryKey`; `ex:Bad` has no domain, not renderable.
