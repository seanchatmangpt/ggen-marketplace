//! Guard prelude for the `echo-wasm` WASI JSON-ABI module (error style `flat-code`).
//
// Consumed query columns (guards.rq): crate_name, export_prefix, error_style,
// max_request_bytes, max_json_depth, code_request_too_large, code_json_too_deep,
// code_missing_buffer, code_internal.
// Rendered by ggen (wasi-json-abi-pack) from the wja: graph.
// Edit the ontology and re-render; never edit this file by hand.
//
// Limits: request 1048576 bytes, JSON depth 64 (see `crate::abi_meta`).
//
// Error style flat-code: `{"ok":false,"error":{"code","message",..}}`. The hand-written
// safe core re-exports this module (`pub use crate::guards::*;`) and supplies
// `call` / `dispatch`; `limit_response` and `missing_buffer_response` satisfy the
// contract of the generated FFI shell.
#![allow(dead_code)]

use crate::abi_meta::{ERROR_CODES, OPS};
use serde_json::{json, Value};

/// Maximum bracket nesting of a JSON text (string-aware, allocation-free).
pub fn json_depth(b: &[u8]) -> usize {
    let (mut depth, mut max, mut in_str, mut esc) = (0usize, 0usize, false, false);
    for &c in b {
        if in_str {
            if esc {
                esc = false;
            } else if c == b'\\' {
                esc = true;
            } else if c == b'"' {
                in_str = false;
            }
            continue;
        }
        match c {
            b'"' => in_str = true,
            b'[' | b'{' => {
                depth += 1;
                max = max.max(depth);
            }
            b']' | b'}' => depth = depth.saturating_sub(1),
            _ => {}
        }
    }
    max
}

/// Position of `name` in the op table (`wja:opOrder` order).
pub fn op_index(name: &str) -> Option<usize> {
    OPS.iter().position(|o| *o == name)
}

/// Position of `code` in the error-code table (`wja:codeOrder` order).
pub fn error_code_index(code: &str) -> Option<usize> {
    ERROR_CODES.iter().position(|c| *c == code)
}

/// A structured, host-readable failure.
#[derive(Debug, PartialEq, Eq)]
pub struct AbiError {
    /// Stable machine-readable code; always one of `ERROR_CODES`.
    pub code: &'static str,
    /// Human-readable explanation.
    pub message: String,
    /// Extra typed fields merged into the `error` object (limit failures).
    pub details: Option<Value>,
}

/// A plain failure with no extra fields.
pub fn err(code: &'static str, message: impl Into<String>) -> AbiError {
    AbiError {
        code,
        message: message.into(),
        details: None,
    }
}

/// A typed resource-limit failure: `LIMIT_REQUEST_BYTES` (bytes) or `LIMIT_JSON_DEPTH` (nesting).
pub fn limit(name: &str, observed: usize, max: usize) -> AbiError {
    let code = if name == "json_depth" {
        "LIMIT_JSON_DEPTH"
    } else {
        "LIMIT_REQUEST_BYTES"
    };
    AbiError {
        code,
        message: format!("resource limit `{name}` exceeded: {observed} > {max}"),
        details: Some(json!({"limit": name, "observed": observed, "max": max})),
    }
}

/// The `{"ok":false,"error":{..}}` body for a failure.
pub fn error_body(e: AbiError) -> Value {
    let mut error = json!({"code": e.code, "message": e.message});
    if let (Some(Value::Object(extra)), Some(map)) = (e.details, error.as_object_mut()) {
        map.extend(extra);
    }
    json!({"ok": false, "error": error})
}

/// Typed response for a request over a resource limit (used by the FFI shell).
pub fn limit_response(name: &str, observed: usize, max: usize) -> Vec<u8> {
    encode(error_body(limit(name, observed, max)))
}

/// Typed response for a call whose request buffer does not exist (`ex_alloc`
/// refused it, or it was never allocated).
pub fn missing_buffer_response() -> Vec<u8> {
    encode(error_body(err(
        "NULL_INPUT",
        "request buffer missing: ex_alloc refused or was never called",
    )))
}

/// Serialize a response; total (the fallback keeps the ABI total anyway).
pub fn encode(v: Value) -> Vec<u8> {
    serde_json::to_vec(&v).unwrap_or_else(|_| {
        br#"{"ok":false,"error":{"code":"INTERNAL","message":"encode"}}"#.to_vec()
    })
}
