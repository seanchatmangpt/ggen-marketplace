# ash-extension-core-pack

**Superseded by [`../ash-extension-pack`](../ash-extension-pack).**

This pack is left on disk unmodified (not deleted, not edited) per
`../ash-extension-pack/pack.toml`'s own consolidation note, but all further
development happens in `ash-extension-pack`, not here.

## Why

`ash-extension-pack` consolidates this pack and `ash-extension-starter-pack` into one
canonical pack after resolving two real conflicts between them (full detail in
[`../ash-extension-pack/pack.toml`](../ash-extension-pack/pack.toml)'s description):

1. **Competing `reactor_pipeline` templates targeting the same output path.** This
   pack's `templates/reactor_pipeline.ex.tmpl` hardcodes ash_r2rml's fixed five-step
   pipeline body. `ash-extension-starter-pack`'s `templates/reactor_pipeline_dynamic.ex.tmpl`
   generates an arbitrary spec-declared step DAG from `aex:ReactorStep` rows and would
   write the same generated module path. `ash-extension-pack` resolved this by keeping
   only the starter-pack's dynamic, query-gated template going forward; this pack's
   fixed five-step template was retired and is NOT carried into `ash-extension-pack`.
2. **The `aex:workflowReactor` vs `aex:generatesReceiptedAction` boundary.** This pack
   only had `aex:workflowReactor` (a plain opt-in Reactor pipeline). The two are
   independent, composable capabilities, not a hierarchy — `ash-extension-pack`'s
   ontology comment block states this explicitly, resolving a boundary that was
   underspecified across this pack and `ash-extension-starter-pack`.

Use `ash-extension-pack` for new work. See that pack's `pack.toml` for the full
consolidation rationale and current verification status.
