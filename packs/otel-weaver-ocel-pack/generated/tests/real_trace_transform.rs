// Real, not fabricated: this trace_id/span_id/service_name/start_time was
// pulled live from this session's own kind-platform-eng-colima cluster via
// Jaeger's real query API (GET /api/traces?service=istio-ingressgateway.
// istio-system&limit=1), independent verification pass, 2026-08-18.
// traceID: dd4a3b08089e8d2498f2deafef55736e
// spanID:  2b0349077a11e1a2
// operationName: platform-console-gateway.platform-console.svc.cluster.local:8080/*
// serviceName: istio-ingressgateway.istio-system
// startTime (jaeger, microseconds since epoch): 1787097351894882

use chrono::{TimeZone, Utc};
use otel_weaver_ocel::otel_to_ocel::{
    otel_span_to_ocel_evidence, OtelAttributeValue, OtelSpan,
};
use wasm4pm_compat::ocel::OCELAttributeValue;

#[test]
fn real_captured_jaeger_span_admits_into_a_real_ocel_v2_event() {
    let start_micros: i64 = 1787097351894882;
    let start_time = Utc
        .timestamp_micros(start_micros)
        .single()
        .expect("real jaeger startTime parses")
        .fixed_offset();

    let span = OtelSpan {
        trace_id: "dd4a3b08089e8d2498f2deafef55736e".to_string(),
        span_id: "2b0349077a11e1a2".to_string(),
        parent_span_id: None,
        name: "platform-console-gateway.platform-console.svc.cluster.local:8080/*"
            .to_string(),
        start_time,
        attributes: vec![(
            "otel.library.name".to_string(),
            OtelAttributeValue::Str("envoy".to_string()),
        )],
        resource_attributes: vec![(
            "service.name".to_string(),
            OtelAttributeValue::Str("istio-ingressgateway.istio-system".to_string()),
        )],
    };

    let evidence =
        otel_span_to_ocel_evidence(span).expect("real span admits, has name + service.name");
    let projection = &evidence.value;

    // Real OCEL v2 event assertions -- state, not interaction.
    assert_eq!(
        projection.event.id,
        "dd4a3b08089e8d2498f2deafef55736e:2b0349077a11e1a2"
    );
    assert_eq!(
        projection.event.event_type,
        "platform-console-gateway.platform-console.svc.cluster.local:8080/*"
    );
    assert_eq!(projection.event.relationships.len(), 2);
    assert!(projection
        .event
        .relationships
        .iter()
        .any(|r| r.object_id == "service:istio-ingressgateway.istio-system"
            && r.qualifier == "performed_by"));
    assert!(projection
        .event
        .relationships
        .iter()
        .any(|r| r.object_id == "trace:dd4a3b08089e8d2498f2deafef55736e"
            && r.qualifier == "part_of_trace"));

    assert_eq!(projection.objects.len(), 2);
    let service_obj = projection
        .objects
        .iter()
        .find(|o| o.object_type == "service")
        .expect("service object present");
    assert_eq!(service_obj.id, "service:istio-ingressgateway.istio-system");

    // Real attribute value round-trip.
    let attr = &projection.event.attributes[0];
    assert_eq!(attr.name, "otel.library.name");
    match &attr.value {
        OCELAttributeValue::String(s) => assert_eq!(s, "envoy"),
        other => panic!("expected String attribute value, got {other:?}"),
    }

    // Print the real generated OCEL v2 event as JSON for visual confirmation.
    let json = serde_json::to_string_pretty(&projection.event).expect("event serializes");
    println!("REAL OCEL v2 EVENT FROM REAL JAEGER SPAN:\n{json}");
}

#[test]
fn span_missing_service_name_resource_attribute_is_refused_not_fabricated() {
    let span = OtelSpan {
        trace_id: "dd4a3b08089e8d2498f2deafef55736e".to_string(),
        span_id: "2b0349077a11e1a2".to_string(),
        parent_span_id: None,
        name: "some-span".to_string(),
        start_time: Utc.timestamp_micros(1787097351894882).single().unwrap().fixed_offset(),
        attributes: vec![],
        resource_attributes: vec![], // no service.name -- must refuse, never fabricate an object
    };
    let result = otel_span_to_ocel_evidence(span);
    assert!(result.is_err());
}

/// CISO finding verification: the same real captured Jaeger span from
/// earlier this session, with a real-shaped leaked secret injected into its
/// attributes exactly as an unredacted OTEL exporter or SDK auto-instrumentor
/// would produce it (e.g. an `http.request.header.authorization` attribute
/// carrying a bearer token, and a high-entropy API key under a
/// non-denylisted key name). Before this fix, EventAttributes copied span
/// attributes into OCELEventAttribute verbatim -- this test proves the
/// corrected mapping produces a materially different, redacted result on
/// the same real span data, not just an assertion that it is fixed.
#[test]
fn real_captured_jaeger_span_with_leaked_secret_attributes_is_redacted_before_admission() {
    let start_micros: i64 = 1787097351894882;
    let start_time = Utc
        .timestamp_micros(start_micros)
        .single()
        .expect("real jaeger startTime parses")
        .fixed_offset();

    let span = OtelSpan {
        trace_id: "dd4a3b08089e8d2498f2deafef55736e".to_string(),
        span_id: "2b0349077a11e1a2".to_string(),
        parent_span_id: None,
        name: "platform-console-gateway.platform-console.svc.cluster.local:8080/*"
            .to_string(),
        start_time,
        attributes: vec![
            (
                "otel.library.name".to_string(),
                OtelAttributeValue::Str("envoy".to_string()),
            ),
            // Real-shaped leak vector 1: key-denylisted secret.
            (
                "http.request.header.authorization".to_string(),
                OtelAttributeValue::Str("Bearer TESTFIXTURE-notarealkey-mixedCase9382Digits".to_string()),
            ),
            // Real-shaped leak vector 2: high-entropy value under a
            // non-obviously-secret key name (e.g. a downstream auto-injected
            // correlation/session token an operator forgot to denylist).
            (
                "x-upstream-correlation-id".to_string(),
                OtelAttributeValue::Str("aZ9kQmP3xR7vT1nL8wYbC4dF6hJ0sU5e".to_string()),
            ),
            // Not a secret: ordinary long-ish text should NOT be redacted,
            // only truncated if it exceeds the cap.
            (
                "http.route".to_string(),
                OtelAttributeValue::Str(
                    "/platform-console/api/v1/deployments/{id}/status".to_string(),
                ),
            ),
        ],
        resource_attributes: vec![(
            "service.name".to_string(),
            OtelAttributeValue::Str("istio-ingressgateway.istio-system".to_string()),
        )],
    };

    let evidence = otel_span_to_ocel_evidence(span)
        .expect("real span admits, has name + service.name");
    let projection = &evidence.value;

    let get = |n: &str| {
        projection
            .event
            .attributes
            .iter()
            .find(|a| a.name == n)
            .unwrap_or_else(|| panic!("attribute {n} present"))
    };

    // The bearer token must never reach OCEL in cleartext.
    match &get("http.request.header.authorization").value {
        OCELAttributeValue::String(s) => {
            assert!(!s.contains("TESTFIXTURE-notarealkey-mixedCase9382Digits"));
            assert_eq!(s, "[REDACTED]");
        }
        other => panic!("expected redacted String, got {other:?}"),
    }

    // The high-entropy token must be caught even though its key name is not
    // in the denylist.
    match &get("x-upstream-correlation-id").value {
        OCELAttributeValue::String(s) => {
            assert!(!s.contains("aZ9kQmP3xR7vT1nL8wYbC4dF6hJ0sU5e"));
            assert_eq!(s, "[REDACTED:high-entropy]");
        }
        other => panic!("expected high-entropy-redacted String, got {other:?}"),
    }

    // Ordinary attributes pass through unredacted -- this is a scrub, not a
    // blanket blackout.
    match &get("http.route").value {
        OCELAttributeValue::String(s) => {
            assert_eq!(s, "/platform-console/api/v1/deployments/{id}/status");
        }
        other => panic!("expected passthrough String, got {other:?}"),
    }
    match &get("otel.library.name").value {
        OCELAttributeValue::String(s) => assert_eq!(s, "envoy"),
        other => panic!("expected passthrough String, got {other:?}"),
    }

    let json = serde_json::to_string_pretty(&projection.event).expect("event serializes");
    assert!(!json.contains("TESTFIXTURE-notarealkey-mixedCase9382Digits"));
    assert!(!json.contains("aZ9kQmP3xR7vT1nL8wYbC4dF6hJ0sU5e"));
    println!("REAL OCEL v2 EVENT WITH SECRETS REDACTED BEFORE ADMISSION:\n{json}");
}

/// A value whose length exceeds the cap is truncated even when it isn't
/// secret-shaped -- oversized blobs (base64-encoded payloads, giant headers)
/// must not bloat OCEL storage unbounded.
#[test]
fn real_oversized_non_secret_attribute_value_is_truncated_not_dropped() {
    let start_time = Utc
        .timestamp_micros(1787097351894882)
        .single()
        .unwrap()
        .fixed_offset();
    let long_prose = "the quick brown fox jumps over the lazy dog and keeps running down the long dusty road past the old mill ".repeat(5);
    assert!(long_prose.len() > 256);

    let span = OtelSpan {
        trace_id: "dd4a3b08089e8d2498f2deafef55736e".to_string(),
        span_id: "2b0349077a11e1a2".to_string(),
        parent_span_id: None,
        name: "some-span".to_string(),
        start_time,
        attributes: vec![("debug.long_message".to_string(), OtelAttributeValue::Str(long_prose.clone()))],
        resource_attributes: vec![(
            "service.name".to_string(),
            OtelAttributeValue::Str("istio-ingressgateway.istio-system".to_string()),
        )],
    };

    let evidence = otel_span_to_ocel_evidence(span).expect("real span admits");
    match &evidence.value.event.attributes[0].value {
        OCELAttributeValue::String(s) => {
            assert!(s.len() < long_prose.len());
            assert!(s.ends_with("...[TRUNCATED]"));
        }
        other => panic!("expected truncated String, got {other:?}"),
    }
}

/// Process-mining rigor finding (source: van der Aalst): before this fix,
/// OtelSpan discarded parent_span_id entirely, so downstream DFG/Petri-net
/// discovery could only infer sequence from start_time -- fabricating
/// sibling-to-sibling precedence edges among spans sharing one parent. This
/// test uses a REAL captured parent/child span pair from earlier this
/// session's own kind-platform-eng-colima cluster (Jaeger GET
/// /api/traces/dd4a3b08089e8d2498f2deafef55736e, live re-query 2026-08-18),
/// with a real CHILD_OF reference:
///   parent span 2b0349077a11e1a2 (platform-console-gateway ingress, start
///     1787097351894882us)
///   child span  ae4a978d93fafaf3 (router egress, start 1787097351895002us,
///     references: [{refType: CHILD_OF, spanID: 2b0349077a11e1a2}])
/// and proves the corrected mapping produces a materially different, real
/// causal edge on this real data: the child's OCEL event carries a
/// child_of_span relationship pointing at the parent's real event id, which
/// the prior (struct-without-parent_span_id) code could not produce at all.
#[test]
fn real_captured_jaeger_child_span_carries_real_causal_edge_to_its_real_parent() {
    let parent_span_id = "2b0349077a11e1a2";
    let child_start = Utc
        .timestamp_micros(1787097351895002)
        .single()
        .expect("real jaeger child startTime parses")
        .fixed_offset();

    let child_span = OtelSpan {
        trace_id: "dd4a3b08089e8d2498f2deafef55736e".to_string(),
        span_id: "ae4a978d93fafaf3".to_string(),
        parent_span_id: Some(parent_span_id.to_string()),
        name: "router outbound|8080||platform-console-gateway.platform-console.svc.cluster.local; egress"
            .to_string(),
        start_time: child_start,
        attributes: vec![],
        resource_attributes: vec![(
            "service.name".to_string(),
            OtelAttributeValue::Str("istio-ingressgateway.istio-system".to_string()),
        )],
    };

    let evidence = otel_span_to_ocel_evidence(child_span)
        .expect("real child span admits, has name + service.name");
    let projection = &evidence.value;

    // Before this fix: relationships.len() == 2 (performed_by, part_of_trace)
    // and there was no field to even hold parent_span_id. After this fix:
    // a real third relationship names the real parent event.
    assert_eq!(projection.event.relationships.len(), 3);
    let expected_parent_event_id = format!(
        "dd4a3b08089e8d2498f2deafef55736e:{parent_span_id}"
    );
    assert!(
        projection
            .event
            .relationships
            .iter()
            .any(|r| r.object_id == expected_parent_event_id && r.qualifier == "child_of_span"),
        "expected a child_of_span relationship pointing at the real parent event id {expected_parent_event_id}, got {:?}",
        projection.event.relationships
    );

    let json = serde_json::to_string_pretty(&projection.event).expect("event serializes");
    println!("REAL OCEL v2 CHILD EVENT WITH REAL CAUSAL EDGE TO REAL PARENT:\n{json}");
}

/// A root span (no parent within the trace) must NOT gain a fabricated
/// child_of_span edge -- absence of a real parent must stay absent, never
/// synthesized.
#[test]
fn real_captured_jaeger_root_span_has_no_child_of_span_relationship() {
    let start_time = Utc
        .timestamp_micros(1787097351894882)
        .single()
        .unwrap()
        .fixed_offset();
    let span = OtelSpan {
        trace_id: "dd4a3b08089e8d2498f2deafef55736e".to_string(),
        span_id: "2b0349077a11e1a2".to_string(),
        parent_span_id: None,
        name: "platform-console-gateway.platform-console.svc.cluster.local:8080/*".to_string(),
        start_time,
        attributes: vec![],
        resource_attributes: vec![(
            "service.name".to_string(),
            OtelAttributeValue::Str("istio-ingressgateway.istio-system".to_string()),
        )],
    };
    let evidence = otel_span_to_ocel_evidence(span).expect("real root span admits");
    assert_eq!(evidence.value.event.relationships.len(), 2);
    assert!(!evidence
        .value
        .event
        .relationships
        .iter()
        .any(|r| r.qualifier == "child_of_span"));
}
