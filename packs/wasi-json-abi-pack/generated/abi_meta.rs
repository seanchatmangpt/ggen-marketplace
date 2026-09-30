//! ABI metadata for the `echo-wasm` WASI JSON-ABI module.
//
// Consumed query columns (meta.rq): crate_name, export_prefix, abi_version,
// max_request_bytes, max_json_depth, ops, error_codes.
// Rendered by ggen (wasi-json-abi-pack) from the wja: graph.
// Edit the ontology and re-render; never edit this file by hand.
#![allow(dead_code)]

/// Name of the crate hosting the module.
pub const CRATE_NAME: &str = "echo-wasm";

/// Prefix of the exported symbols (`<prefix>_abi_version/_alloc/_free/_call`).
pub const EXPORT_PREFIX: &str = "ex";

/// Value returned by `<prefix>_abi_version`.
pub const ABI_VERSION: u32 = 1;

/// Upper bound on request size in bytes; alloc returns null above it.
pub const MAX_REQUEST_BYTES: usize = 1048576;

/// Upper bound on accepted JSON nesting depth.
pub const MAX_JSON_DEPTH: usize = 64;

/// Op table, ordered by `wja:opOrder`.
pub const OPS: &[&str] = &[
    "echo",
    "len",
];

/// Typed error codes, ordered by `wja:codeOrder`.
pub const ERROR_CODES: &[&str] = &[
    "BAD_JSON",
    "UNKNOWN_OP",
    "LIMIT_REQUEST_BYTES",
    "LIMIT_JSON_DEPTH",
    "NULL_INPUT",
    "INTERNAL",
];
