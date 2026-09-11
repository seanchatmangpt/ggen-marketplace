# Ash codegen callback projection

`ash-extension-core-pack` declares two optional consumer RDF facts on an `aex:AshExtensionSpec` in its canonical `ontology.ttl`:

- `aex:codegenTask` — exact Mix task name invoked by `Ash.Extension.codegen/1`.
- `aex:codegenName` — optional human-readable extension name used by `mix ash.codegen`; it is admitted only when `aex:codegenTask` exists.

The pack echoes these facts into the generated extension. It does not synthesize a task name from the package name and it does not grant the generated task authority beyond the normal Ash `mix ash.codegen` callback boundary.

`gates/040_codegen_callback_contract.rq` refuses malformed task names and refuses `codegenName` without `codegenTask`; `templates/extension.ex.tmpl` consumes only the admitted predicates. The ontology, gate, and renderer therefore share one vocabulary rather than relying on an undeclared consumer-local extension.
