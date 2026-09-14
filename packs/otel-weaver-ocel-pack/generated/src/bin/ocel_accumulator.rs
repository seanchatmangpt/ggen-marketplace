// NOT GENERATED -- hand-written accumulator binary. First real caller of
// otel_to_ocel::otel_span_to_ocel_evidence().
//
// Receives OTLP spans via OTLP-HTTP/JSON (the Collector's `otlphttp` exporter
// with `encoding: json`, matching the plan's "simpler than gRPC" call and
// this crate's existing serde-first OTLP-shape convention -- no protobuf/
// prost dependency needed). Each span is admitted through the unmodified
// otel_span_to_ocel_evidence() admission door, then appended to an
// append-only OCEL v2 JSONL sidecar (one admitted OcelProjection per line),
// with object-ID deduplication so recurring service/trace objects (the
// plan's flagged highest-risk, no-precedent piece) are written once. The
// sidecar is periodically compacted into a canonical single-document
// OCEL v2 JSON (events[]/objects[]) via /compact.
//
// /discovery runs real process discovery (OC-DFG, one directly-follows
// graph per object type) over the compacted OCEL v2 JSON log by shelling
// out to wasm4pm-cli's real `wpm mining discover --algo ocdfg` subcommand
// (std::process::Command, real subprocess, never a fabricated result).
// That subcommand has no JSON output mode -- it prints a colored,
// human-readable table to stdout -- so the real stdout (ANSI codes
// stripped) is returned verbatim as the `raw` field; this is the actual
// output of the actual tool, not a reconstruction. Fails closed (503) if
// the compacted log doesn't exist yet, is empty, or the subprocess exits
// non-zero / fails to spawn.
//
// HTTP server: tiny_http (sync, blocking, no async runtime) -- the
// project carries no axum/actix precedent yet, and a single-threaded
// blocking loop is enough for this accumulator's traffic (a handful of
// spans/10s from the traffic-generator).

use chrono::{DateTime, FixedOffset, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::path::PathBuf;
use std::process::Command;
use std::sync::Mutex;

use otel_weaver_ocel::otel_to_ocel::{
    otel_span_to_ocel_evidence, OcelProjection, OtelAttributeValue, OtelSpan,
};
use wasm4pm_compat::ocel::{OCELObject, OCELType};

/// One line of the append-only sidecar: an admitted projection plus which
/// object ids in it were newly written vs already deduped (kept for a real,
/// inspectable audit trail of the dedup decision, not just the end state).
#[derive(Serialize, Deserialize, Debug, Clone)]
struct AccumulatorRecord {
    event: wasm4pm_compat::ocel::OCELEvent,
    /// Only objects not already seen by object id are recorded per-line;
    /// duplicates are dropped BEFORE the write, not filtered at compaction
    /// time, so the JSONL file itself never carries duplicate object ids.
    new_objects: Vec<OCELObject>,
}

struct AccumulatorState {
    jsonl_path: PathBuf,
    seen_object_ids: HashSet<String>,
    event_count: u64,
    object_count: u64,
    last_updated: Option<DateTime<Utc>>,
}

impl AccumulatorState {
    fn load_or_init(jsonl_path: PathBuf) -> std::io::Result<Self> {
        let mut seen_object_ids = HashSet::new();
        let mut event_count = 0u64;
        if jsonl_path.exists() {
            let f = File::open(&jsonl_path)?;
            for line in BufReader::new(f).lines() {
                let line = line?;
                if line.trim().is_empty() {
                    continue;
                }
                if let Ok(rec) = serde_json::from_str::<AccumulatorRecord>(&line) {
                    event_count += 1;
                    for obj in &rec.new_objects {
                        seen_object_ids.insert(obj.id.clone());
                    }
                }
            }
        }
        let object_count = seen_object_ids.len() as u64;
        Ok(Self {
            jsonl_path,
            seen_object_ids,
            event_count,
            object_count,
            last_updated: None,
        })
    }

    /// Appends one admitted projection, deduplicating objects by id against
    /// every object id ever seen (this is the flagged highest-risk logic:
    /// OcelProjection's service/trace objects recur across every span in
    /// the same trace/service, and otel_span_to_ocel_evidence was only ever
    /// exercised one span at a time -- nothing upstream dedupes).
    fn append(&mut self, projection: OcelProjection) -> std::io::Result<()> {
        let mut new_objects = Vec::new();
        for obj in projection.objects {
            if self.seen_object_ids.insert(obj.id.clone()) {
                new_objects.push(obj);
            }
        }
        let record = AccumulatorRecord {
            event: projection.event,
            new_objects,
        };
        let line = serde_json::to_string(&record).map_err(std::io::Error::other)?;
        let mut f = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.jsonl_path)?;
        writeln!(f, "{line}")?;
        f.flush()?;
        self.event_count += 1;
        self.object_count = self.seen_object_ids.len() as u64;
        self.last_updated = Some(Utc::now());
        Ok(())
    }

    /// Compacts the JSONL sidecar into a canonical single-document OCEL v2
    /// JSON (events[]/objects[]), per plan step C's stated engineering
    /// decision that true OCEL v2 JSON isn't naturally append-friendly.
    /// Reads the sidecar fresh from disk (not from in-memory state) so the
    /// compacted document is a real reflection of everything durably
    /// written, not just what this process instance appended.
    fn compact(&self, out_path: &PathBuf) -> std::io::Result<(usize, usize)> {
        let mut events = Vec::new();
        let mut objects = Vec::new();
        let mut object_ids = HashSet::new();
        if self.jsonl_path.exists() {
            let f = File::open(&self.jsonl_path)?;
            for line in BufReader::new(f).lines() {
                let line = line?;
                if line.trim().is_empty() {
                    continue;
                }
                let rec: AccumulatorRecord = serde_json::from_str(&line)?;
                events.push(rec.event);
                for obj in rec.new_objects {
                    if object_ids.insert(obj.id.clone()) {
                        objects.push(obj);
                    }
                }
            }
        }
        let event_types: Vec<OCELType> = {
            let mut names: Vec<String> = events
                .iter()
                .map(|e| e.event_type.clone())
                .collect::<HashSet<_>>()
                .into_iter()
                .collect();
            names.sort();
            names
                .into_iter()
                .map(|name| OCELType {
                    name,
                    attributes: vec![],
                })
                .collect()
        };
        let object_types: Vec<OCELType> = {
            let mut names: Vec<String> = objects
                .iter()
                .map(|o| o.object_type.clone())
                .collect::<HashSet<_>>()
                .into_iter()
                .collect();
            names.sort();
            names
                .into_iter()
                .map(|name| OCELType {
                    name,
                    attributes: vec![],
                })
                .collect()
        };
        let doc = wasm4pm_compat::ocel::OCEL {
            event_types,
            object_types,
            events: events.clone(),
            objects: objects.clone(),
        };
        let json = serde_json::to_string_pretty(&doc)?;
        std::fs::write(out_path, json)?;
        Ok((events.len(), objects.len()))
    }
}

/// Parses just enough of the OTLP-HTTP/JSON ExportTraceServiceRequest shape
/// (resourceSpans[].resource.attributes / scopeSpans[].spans[]) to build
/// this crate's OtelSpan -- deliberately narrow, matching the "minimal real
/// OTEL span shape this transformer consumes" scope already stated in
/// otel_to_ocel.rs, not a general-purpose OTLP proto decoder.
fn parse_otlp_json(body: &str) -> Vec<OtelSpan> {
    let root: serde_json::Value = match serde_json::from_str(body) {
        Ok(v) => v,
        Err(_) => return vec![],
    };
    let mut spans = Vec::new();
    let Some(resource_spans) = root.get("resourceSpans").and_then(|v| v.as_array()) else {
        return spans;
    };
    for rs in resource_spans {
        let resource_attributes = extract_attributes(rs.pointer("/resource/attributes"));
        let Some(scope_spans) = rs.get("scopeSpans").and_then(|v| v.as_array()) else {
            continue;
        };
        for ss in scope_spans {
            let Some(raw_spans) = ss.get("spans").and_then(|v| v.as_array()) else {
                continue;
            };
            for s in raw_spans {
                let trace_id = s.get("traceId").and_then(|v| v.as_str()).unwrap_or("").to_string();
                let span_id = s.get("spanId").and_then(|v| v.as_str()).unwrap_or("").to_string();
                let name = s.get("name").and_then(|v| v.as_str()).unwrap_or("").to_string();
                let parent_span_id = s
                    .get("parentSpanId")
                    .and_then(|v| v.as_str())
                    .filter(|v| !v.is_empty())
                    .map(|v| v.to_string());
                let start_nanos: i64 = s
                    .get("startTimeUnixNano")
                    .and_then(|v| v.as_str().map(|s| s.parse().ok()).unwrap_or_else(|| v.as_i64()))
                    .unwrap_or(0);
                let start_time = nanos_to_datetime(start_nanos);
                let attributes = extract_attributes(s.get("attributes"));
                spans.push(OtelSpan {
                    trace_id,
                    span_id,
                    parent_span_id,
                    name,
                    start_time,
                    attributes,
                    resource_attributes: resource_attributes.clone(),
                });
            }
        }
    }
    spans
}

fn nanos_to_datetime(nanos: i64) -> DateTime<FixedOffset> {
    let secs = nanos / 1_000_000_000;
    let subnanos = (nanos % 1_000_000_000) as u32;
    DateTime::from_timestamp(secs, subnanos)
        .unwrap_or_else(|| DateTime::from_timestamp(0, 0).unwrap())
        .with_timezone(&FixedOffset::east_opt(0).unwrap())
}

fn extract_attributes(v: Option<&serde_json::Value>) -> Vec<(String, OtelAttributeValue)> {
    let mut out = Vec::new();
    let Some(arr) = v.and_then(|v| v.as_array()) else {
        return out;
    };
    for kv in arr {
        let Some(key) = kv.get("key").and_then(|v| v.as_str()) else {
            continue;
        };
        let Some(val) = kv.get("value") else { continue };
        let parsed = if let Some(s) = val.get("stringValue").and_then(|v| v.as_str()) {
            OtelAttributeValue::Str(s.to_string())
        } else if let Some(i) = val
            .get("intValue")
            .and_then(|v| v.as_str().map(|s| s.parse().ok()).unwrap_or_else(|| v.as_i64()))
        {
            OtelAttributeValue::Int(i)
        } else if let Some(f) = val.get("doubleValue").and_then(|v| v.as_f64()) {
            OtelAttributeValue::Float(f)
        } else if let Some(b) = val.get("boolValue").and_then(|v| v.as_bool()) {
            OtelAttributeValue::Bool(b)
        } else {
            continue;
        };
        out.push((key.to_string(), parsed));
    }
    out
}

/// Strips ANSI SGR escape sequences (`\x1b[...m`) from `wpm`'s colored
/// table output so the returned `raw` string is plain text. Minimal,
/// hand-rolled (no `regex`/`strip-ansi-escapes` dependency in this crate's
/// Cargo.toml) -- only handles the CSI `ESC [ ... m` form `colored` emits,
/// which is all `wpm mining discover` produces.
fn strip_ansi(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    let mut chars = s.chars().peekable();
    while let Some(c) = chars.next() {
        if c == '\u{1b}' && chars.peek() == Some(&'[') {
            chars.next(); // consume '['
            for c2 in chars.by_ref() {
                if c2.is_ascii_alphabetic() {
                    break;
                }
            }
        } else {
            out.push(c);
        }
    }
    out
}

/// Result of a real `wpm mining discover --algo ocdfg` invocation.
enum DiscoveryOutcome {
    Ok { raw: String },
    Fail { reason: String },
}

/// Shells out to the real `wpm` binary (wasm4pm-cli) against the compacted
/// OCEL v2 JSON log at `log_path`, following this accumulator's existing
/// fail-closed conventions: a spawn failure, non-zero exit, or missing log
/// file all produce a `Fail` with a real diagnostic -- never a fabricated
/// `Ok`.
fn run_discovery(log_path: &PathBuf) -> DiscoveryOutcome {
    if !log_path.exists() {
        return DiscoveryOutcome::Fail {
            reason: format!(
                "compacted OCEL log not found at {:?} -- call POST /compact first",
                log_path
            ),
        };
    }
    let wpm_bin = std::env::var("WPM_BIN").unwrap_or_else(|_| "wpm".to_string());
    let output = match Command::new(&wpm_bin)
        .arg("mining")
        .arg("discover")
        .arg(log_path)
        .arg("--algo")
        .arg("ocdfg")
        .output()
    {
        Ok(o) => o,
        Err(e) => {
            eprintln!("discovery: failed to spawn {wpm_bin}: {e}");
            return DiscoveryOutcome::Fail {
                reason: format!("failed to spawn wasm4pm-cli ({wpm_bin}): {e}"),
            };
        }
    };
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();
        eprintln!(
            "discovery: wpm mining discover exited with {:?}: {}",
            output.status.code(),
            stderr.trim()
        );
        return DiscoveryOutcome::Fail {
            reason: format!(
                "wasm4pm-cli exited with {:?}: {}",
                output.status.code(),
                stderr.trim()
            ),
        };
    }
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    DiscoveryOutcome::Ok {
        raw: strip_ansi(&stdout),
    }
}

fn main() -> std::io::Result<()> {
    let bind_addr = std::env::var("OCEL_ACCUMULATOR_BIND").unwrap_or_else(|_| "0.0.0.0:4900".to_string());
    let data_dir = std::env::var("OCEL_ACCUMULATOR_DATA_DIR").unwrap_or_else(|_| "/data".to_string());
    std::fs::create_dir_all(&data_dir)?;
    let jsonl_path = PathBuf::from(&data_dir).join("ocel-log.jsonl");
    let compacted_path = PathBuf::from(&data_dir).join("ocel-log.json");

    let state = Mutex::new(AccumulatorState::load_or_init(jsonl_path)?);

    let server = tiny_http::Server::http(&bind_addr).map_err(std::io::Error::other)?;
    eprintln!("ocel_accumulator listening on {bind_addr}, data_dir={data_dir}");

    for mut request in server.incoming_requests() {
        let url = request.url().to_string();
        let method = request.method().clone();
        let respond = |request: tiny_http::Request, status: u16, body: String| {
            let header = tiny_http::Header::from_bytes(&b"Content-Type"[..], &b"application/json"[..]).unwrap();
            let response = tiny_http::Response::from_string(body)
                .with_status_code(status)
                .with_header(header);
            let _ = request.respond(response);
        };

        match (method, url.as_str()) {
            (tiny_http::Method::Post, "/v1/traces") => {
                let mut body = String::new();
                if request.as_reader().read_to_string(&mut body).is_err() {
                    respond(request, 400, r#"{"error":"read failed"}"#.to_string());
                    continue;
                }
                let spans = parse_otlp_json(&body);
                let mut admitted = 0usize;
                let mut refused = 0usize;
                {
                    let mut st = state.lock().unwrap();
                    for span in spans {
                        match otel_span_to_ocel_evidence(span) {
                            Ok(evidence) => {
                                let projection = evidence.into_inner();
                                if st.append(projection).is_ok() {
                                    admitted += 1;
                                } else {
                                    refused += 1;
                                }
                            }
                            Err(_) => refused += 1,
                        }
                    }
                }
                respond(
                    request,
                    200,
                    serde_json::json!({"admitted": admitted, "refused": refused}).to_string(),
                );
            }
            (tiny_http::Method::Get, "/status") => {
                let st = state.lock().unwrap();
                let body = serde_json::json!({
                    "eventCount": st.event_count,
                    "objectCount": st.object_count,
                    "lastUpdated": st.last_updated.map(|t| t.to_rfc3339()),
                })
                .to_string();
                respond(request, 200, body);
            }
            (tiny_http::Method::Get, "/discovery") => {
                match run_discovery(&compacted_path) {
                    DiscoveryOutcome::Ok { raw } => {
                        let body = serde_json::json!({"algorithm": "ocdfg", "raw": raw}).to_string();
                        respond(request, 200, body);
                    }
                    DiscoveryOutcome::Fail { reason } => {
                        let body = serde_json::json!({"error": reason}).to_string();
                        respond(request, 503, body);
                    }
                }
            }
            (tiny_http::Method::Post, "/compact") => {
                let st = state.lock().unwrap();
                match st.compact(&compacted_path) {
                    Ok((events, objects)) => respond(
                        request,
                        200,
                        serde_json::json!({"events": events, "objects": objects, "path": compacted_path}).to_string(),
                    ),
                    Err(e) => respond(request, 500, serde_json::json!({"error": e.to_string()}).to_string()),
                }
            }
            (tiny_http::Method::Get, "/healthz") => {
                respond(request, 200, r#"{"ok":true}"#.to_string());
            }
            _ => {
                respond(request, 404, r#"{"error":"not found"}"#.to_string());
            }
        }
    }
    Ok(())
}
