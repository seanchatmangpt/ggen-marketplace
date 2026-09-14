# ash-extension-starter-pack

**Superseded by [`../ash-extension-pack`](../ash-extension-pack).**

This pack is left on disk unmodified (not deleted, not edited) per
`../ash-extension-pack/pack.toml`'s own consolidation note, but all further
development happens in `ash-extension-pack`, not here.

## Why

`ash-extension-pack` consolidates `ash-extension-core-pack` and this pack into one
canonical pack after resolving two real conflicts between them (full detail in
[`../ash-extension-pack/pack.toml`](../ash-extension-pack/pack.toml)'s description):

1. **Competing `reactor_pipeline` templates targeting the same output path.** This
   pack's `templates/reactor_pipeline_dynamic.ex.tmpl` generates an arbitrary
   spec-declared step DAG from `aex:ReactorStep` rows. `ash-extension-core-pack`'s
   `templates/reactor_pipeline.ex.tmpl` hardcodes ash_r2rml's fixed five-step pipeline
   body and would write the same generated module path. `ash-extension-pack` resolved
   this in this pack's favor: this pack's dynamic, query-gated template is a strict
   generalization and is the sole winner carried into `ash-extension-pack`.
2. **The `aex:workflowReactor` vs `aex:generatesReceiptedAction` boundary.** This pack
   added `aex:generatesReceiptedAction` (idempotency-key-gated admission, a sealed
   receipt entity, deterministic replay) alongside core-pack's plain
   `aex:workflowReactor`. `ash-extension-pack`'s ontology comment block now states
   explicitly that these are independent, composable capabilities, not a hierarchy or
   mutual exclusion — resolving a boundary that was underspecified across this pack
   and `ash-extension-core-pack`.

Use `ash-extension-pack` for new work. See that pack's `pack.toml` for the full
consolidation rationale and current verification status.
