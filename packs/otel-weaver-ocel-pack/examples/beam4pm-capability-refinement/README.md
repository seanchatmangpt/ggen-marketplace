# Example: `beam4pm.capability.id` event-type refinement

Marketplace-convention fixture pair for rule `EventActivityCapability`
(order 45, `templates/src/otel_to_ocel.rs.tmpl:284-294`): when a span's
(already-redacted) attributes carry a non-empty `beam4pm.capability.id`
value, the generated transformer uses it as `OCELEvent.event_type` in place
of the bare `span.name`.

This rule is intentionally **not** yet expressed as an `otelocel:MappingRule`
row in `ontology.ttl` -- it exists only as hand-written logic inside
`templates/src/otel_to_ocel.rs.tmpl`, outside the `queries/mapping-rules.rq`
projection loop. `queries/mapping-rules.rq`'s generic `SELECT * WHERE { ?rule
a otelocel:MappingRule ... }` will not surface this rule until (or unless) it
is promoted to a real ontology fact -- this fixture pins the rule's *current*
generated behavior so that promotion (or any future template edit) has a real
regression check instead of zero coverage.

## Input: `span.json`

A real-shaped OTLP span (attribute keys/values as `OtelSpan`/
`OtelAttributeValue` would carry them, not raw protobuf) whose attributes
carry `beam4pm.capability.id = "ingest.normalize.retry"` alongside the span's
own `name`, `"placeholder-span-name"` -- chosen deliberately unequal to the
capability id so the assertion cannot pass by accident if the refinement rule
is silently skipped.

## Expected output: `expected-ocel-event.json`

The `OCELEvent` fields this span must admit into, once passed through
`otel_span_to_ocel_evidence`. `event_type` is `"ingest.normalize.retry"` (the
capability id), not `"placeholder-span-name"` (the span name) -- this is the
one fact this fixture exists to pin.

## Verification

`generated/tests/beam4pm_capability_refinement.rs` loads this exact
fixture shape inline (Rust structs, not a JSON file, since
`generated/src/otel_to_ocel.rs`'s `OtelSpan` has no `Deserialize` impl) and
asserts the real transformer output against `expected-ocel-event.json`'s
values. Run with:

```bash
cd packs/otel-weaver-ocel-pack/generated
cargo test --test beam4pm_capability_refinement
```
