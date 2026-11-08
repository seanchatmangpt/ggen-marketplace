# Z5b — Render Test Court (xstate-v5-machine-pack)

Standing: PASS

## Engine choice

Rust `tera` 1.x via a standalone cargo bin — no Rust workspace exists in
ggen-marketplace, so the bin lives as its own crate at
`packs/xstate-v5-machine-pack/tools/render_test/` (Cargo.toml + src/main.rs).
Node tera-syntax engines were not evaluated further: cargo 1.97.0 is installed
and tera is the reference implementation of the syntax S2 authored in, so a
compatible-engine approximation was unnecessary. Disclosed: crate builds its
own dep tree from crates.io.

## Census of prior lane work

tools/ contained ONLY `construct_gate.py` (S3). No `render_test.*`, no scratch
files — the killed prior lane left zero partial work on disk.

## Method

`tools/render_test/` renders BOTH pack templates with the documented test var
surface (`tools/render_test/test_vars.json`: machine_label/name/id,
transition_count, context_fields, stash_fields, events, guards, actions,
actors with todo_arm, states with invoke/transitions/excluded/children,
initial_state, parallel; smoke: scenarios with provide_actors/send_steps/
expected_value).

## Gate 1 — render (exit 0 both)

```
cargo run --release -- <pack> test_vars.json /tmp/z5b_render2
RENDERED machine.tera.tmpl -> /tmp/z5b_render2/machine.ts (6139 bytes)
RENDERED smoke.tera.tmpl -> /tmp/z5b_render2/smoke.ts (3235 bytes)
render_test: exit 0 (both templates rendered)
```

## Gate 2 — construct (tools/construct_gate.py)

```
python3 tools/construct_gate.py \
  --machine-file /tmp/z5b_render2/machine.ts \
  --xstate-resolve /Users/sac/srve/servengine-frontend/node_modules/xstate
machine.ts ProviderOnboardingMachine OK initial="editing"
Tally: 1/1 construct OK   # exit 0
```

## Template defects the render exposed (all fixed)

1. `machine.tera.tmpl` context fields rendered `statusstring;` — missing
   `: ` separator between `field.name` and `field.type_expr`. Fixed.
2. `machine.tera.tmpl` actions params rendered `assign((, context) =>` when
   `uses_context=true, uses_event=false` — unconditional comma separator.
   Fixed to the guards' conditional-separator pattern, and param order aligned
   to xstate's `(context, event)` signature (was `(event, context)`).
3. `smoke.tera.tmpl` emitted `createActor(M, { input }, { actors })` — a third
   argument; xstate v5 `createActor` takes (machine, options) and actors ride
   INSIDE the options object. Fixed: actors merged into the options object.
4. `smoke.tera.tmpl` duplicated `fromPromise` import (two xstate import
   lines). Fixed to one.

## Files touched (lane-owned)

- `packs/xstate-v5-machine-pack/tools/render_test/Cargo.toml` (new)
- `packs/xstate-v5-machine-pack/tools/render_test/src/main.rs` (new)
- `packs/xstate-v5-machine-pack/tools/render_test/test_vars.json` (new)
- `packs/xstate-v5-machine-pack/tools/render_test/RECEIPT.md` (new)
- `packs/xstate-v5-machine-pack/templates/machine.tera.tmpl` (fixes 1-2)
- `packs/xstate-v5-machine-pack/templates/smoke.tera.tmpl` (fixes 3-4)
