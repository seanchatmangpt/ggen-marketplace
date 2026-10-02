# Ash codegen callback projection

Ported from `ash-extension-core-pack` (CODEGEN_CALLBACK.md + README.codegen-callback.md,
v26.9.30 consolidation lane 6) together with the capability itself: ontology terms,
gate (now `gates/090_codegen_callback_contract.rq`), and renderer.

`ash-extension-pack` declares two optional consumer RDF facts on an `aex:AshExtensionSpec` in its canonical `ontology.ttl`:

- `aex:codegenTask` — exact Mix task name invoked by `Ash.Extension.codegen/1`.
- `aex:codegenName` — optional human-readable extension name used by `mix ash.codegen`; it is admitted only when `aex:codegenTask` exists.

The pack echoes these facts into the generated extension. It does not synthesize a task name from the package name and it does not grant the generated task authority beyond the normal Ash `mix ash.codegen` callback boundary.

`gates/090_codegen_callback_contract.rq` refuses malformed task names and refuses `codegenName` without `codegenTask`; `templates/extension.ex.tmpl` consumes only the admitted predicates. The ontology, gate, and renderer therefore share one vocabulary rather than relying on an undeclared consumer-local extension.

Usage:

```turtle
@prefix aex: <http://seanchatmangpt.github.io/packs/ash-extension-core#> .

<#extension> a aex:AshExtensionSpec ;
  aex:codegenTask "my_extension.codegen" ;
  aex:codegenName "my_extension" .
```

When present, the generated Spark extension implements the optional `Ash.Extension.codegen/1` callback by re-enabling and running exactly the admitted Mix task. `codegenName` is display metadata only.

Support-subdir capability (ported in the same consolidation): an optional
`aex:supportSubdir` relative path places the generated support modules (Persist,
Verify, Info, Reactor pipeline) under `lib/<package>/<support_subdir>/` instead of
`lib/<package>/`, for consumers that already own a handwritten file at the
historical path. `gates/100_projection_isolation_contract.rq` refuses path escapes
and duplicate `aex:packageName` output ownership.
