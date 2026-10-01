# Why graphlaw is represented as a rust, wasm, beam/elixir pipeline

graphlaw is a Rust crate whose public surface is a JSON ABI over one WASI module, consumed from
Elixir. The marketplace splits that path into hops so each hop owns one kind of truth and can be
refused independently.

## One source per fact

The Rust crate owns op semantics. The wasm module owns the calling convention: exports, linear
memory protocol, limits, imports. The BEAM side owns the host and the typed surface. A fact is
stated once, at the hop that owns it, and later hops project it:

- ops, order and limits are `wja:` facts in `wasi-json-abi-pack`, and the Elixir registry is
  projected from graphlaw's capability registry, not re-typed;
- host imports are enumerated individuals, so "WASI only" is a gate over data and not a sentence;
- digests are pins of a released artifact, bound to a graphlaw SHA, never to a working tree.

## Why not one pack

QRI is a thin waist: it qualifies interchangeable realizations and must not know graphlaw's op
list. The Ash capability pack must not know the wasm calling convention. Merging them would
duplicate whichever vocabulary changed first and make drift between hops invisible. Splitting
them lets a gate at one hop fail while the others still render.

## What stays hand-written

Semantics that are not enumerable facts remain hand-written: op bodies, the refusal envelope,
allocator accounting. They are recorded as `UNSUPPORTED(generator-capability)` residue, not
quietly omitted, so a later generator capability has a ledger to retire.

## What a green pipeline does not prove

Rendering and gates prove structure and determinism of the projections. They do not prove that the
wasm module runs, that its digest matches a built binary, or that a BEAM host loads it. Those need
an exact-SHA execution receipt at the consumer boundary. Generated text has no authority by
existing.

## See Also

- [Reference: the pipeline](../reference/graphlaw-rust-wasm-beam-pipeline.md)
- [How to represent a Rust ABI crate](../how-to/represent-a-rust-abi-crate.md)
- [Why QRI is a thin waist](qri-thin-waist.md)
