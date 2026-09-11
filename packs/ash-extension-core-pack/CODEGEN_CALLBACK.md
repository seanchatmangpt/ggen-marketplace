# Ash codegen callback projection

`ash-extension-core-pack` accepts two optional consumer RDF facts on an `aex:AshExtensionSpec`:

- `aex:codegenTask` — exact Mix task name invoked by `Ash.Extension.codegen/1`.
- `aex:codegenName` — optional human-readable extension name used by `mix ash.codegen`; it is admitted only when `aex:codegenTask` exists.

The pack echoes these facts into the generated extension. It does not synthesize a task name from the package name and it does not grant the generated task authority beyond the normal Ash `mix ash.codegen` callback boundary.

Until the vocabulary declaration is folded into the monolithic `ontology.ttl`, these predicates are operationally admitted by `gates/040_codegen_callback_contract.rq` and consumed by `templates/extension.ex.tmpl`. RDF itself does not require prior property declaration; this file makes the temporary vocabulary-extension boundary explicit rather than hiding it.
