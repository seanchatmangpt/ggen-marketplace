//! Guard prelude for the `graphlaw-wasm` WASI JSON-ABI module (error style `refusal-kind`).
//
// Consumed query columns (guards.rq): crate_name, export_prefix, error_style,
// max_request_bytes, max_json_depth, code_request_too_large, code_json_too_deep,
// code_missing_buffer, code_internal.
// Rendered by ggen (wasi-json-abi-pack) from the wja: graph.
// Edit the ontology and re-render; never edit this file by hand.
//
// Limits: request 16777216 bytes, JSON depth 64 (see `crate::abi_meta`).
//
// Error style refusal-kind: the consumer owns a richer refusal envelope, so this file
// emits ONLY `json_depth` and the ordering helpers. The envelope (limit_response,
// missing_buffer_response, error body, encode) stays hand-written; it is recorded as
// a UNSUPPORTED(generator-capability) residue row in HANDWRITTEN.md.
#![allow(dead_code)]

use crate::abi_meta::{ERROR_CODES, OPS};

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
