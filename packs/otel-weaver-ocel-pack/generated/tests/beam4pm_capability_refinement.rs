// Closes the marketplace gap: no test/fixture exercised the
// `beam4pm.capability.id` event-type refinement rule (order 45,
// `EventActivityCapability`, `templates/src/otel_to_ocel.rs.tmpl:284-294`).
//
// Fixture pair lives at
// `examples/beam4pm-capability-refinement/{span.json,expected-ocel-event.json}`
// per the marketplace's own examples/ convention (see that directory's
// README.md). `OtelSpan` has no `Deserialize` impl, so the span is
// constructed here as the real typed struct with values matching
// `span.json` verbatim, and the assertions are pinned to
// `expected-ocel-event.json`'s values -- state-based, no mocking of any
// collaborator (the real `otel_span_to_ocel_evidence` transformer is
// exercised end to end).

use chrono::{TimeZone, Utc};
use otel_weaver_ocel::otel_to_ocel::{
    otel_span_to_ocel_evidence, OtelAttributeValue, OtelSpan,
};
use wasm4pm_compat::ocel::OCELAttributeValue;

#[test]
fn beam4pm_capability_id_refines_event_type_over_bare_span_name() {
    // Matches examples/beam4pm-capability-refinement/span.json exactly.
    let start_time = Utc
        .timestamp_nanos(1_787_200_000_000_000_000)
        .fixed_offset();

    let span = OtelSpan {
        trace_id: "aa11bb22cc33dd44ee55ff6600112233".to_string(),
        span_id: "0102030405060708".to_string(),
        parent_span_id: None,
        // Deliberately unequal to the capability id below, so this
        // assertion cannot pass by accident if the refinement rule is
        // silently skipped and event_type falls back to span.name.
        name: "placeholder-span-name".to_string(),
        start_time,
        attributes: vec![(
            "beam4pm.capability.id".to_string(),
            OtelAttributeValue::Str("ingest.normalize.retry".to_string()),
        )],
        resource_attributes: vec![(
            "service.name".to_string(),
            OtelAttributeValue::Str("beam4pm-ingest-worker".to_string()),
        )],
    };

    let evidence = otel_span_to_ocel_evidence(span)
        .expect("real span with name + service.name admits");
    let projection = &evidence.value;

    // Matches examples/beam4pm-capability-refinement/expected-ocel-event.json.
    assert_eq!(
        projection.event.id,
        "aa11bb22cc33dd44ee55ff6600112233:0102030405060708"
    );
    assert_eq!(
        projection.event.event_type, "ingest.normalize.retry",
        "event_type must be the beam4pm.capability.id attribute value, \
         not the bare span name, when that attribute is present and non-empty"
    );
    assert_ne!(
        projection.event.event_type, span_name_used_as_fallback_marker(),
        "regression guard: event_type must not silently fall back to span.name"
    );

    assert_eq!(projection.event.relationships.len(), 2);
    assert!(projection
        .event
        .relationships
        .iter()
        .any(|r| r.qualifier == "performed_by"));
    assert!(projection
        .event
        .relationships
        .iter()
        .any(|r| r.qualifier == "part_of_trace"));

    // The capability-id attribute itself is still preserved verbatim in
    // event attributes (redaction only scrubs secret-shaped values/keys;
    // this key/value is neither), independent of its use as event_type.
    let capability_attr = projection
        .event
        .attributes
        .iter()
        .find(|a| a.name == "beam4pm.capability.id")
        .expect("beam4pm.capability.id attribute preserved on the event");
    match &capability_attr.value {
        OCELAttributeValue::String(s) => assert_eq!(s, "ingest.normalize.retry"),
        other => panic!("expected string attribute value, got {other:?}"),
    }
}

fn span_name_used_as_fallback_marker() -> &'static str {
    "placeholder-span-name"
}
