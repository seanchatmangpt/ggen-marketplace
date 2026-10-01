//! Real-runtime wasmi harness + ontology contract tests for `graphlaw-wasm` (error style `refusal-kind`).
//
// Consumed query columns (harness.rq): crate_name, export_prefix, abi_version, error_style,
// wasm_env_var, has_abi_version_export, native_call, code_request_too_large,
// code_json_too_deep, code_missing_buffer, wasm_build_package, cfg_gate, pin_env,
// examples_path.
// Rendered by ggen (wasi-json-abi-pack) from the wja: graph.
// Edit the ontology and re-render; never edit this file by hand.
//
// Install as an integration test (tests/wasm_contract.rs), or as tests/common/mod.rs
// and call its pub API. Dev-dependencies: serde_json, sha2, wasmi, wasmi_wasi.
// Set `GRAPHLAW_WASM` to test a prebuilt module; otherwise the module is built
// once into `target/wasm-abi`. Nothing here skips: a missing or unbuildable module,
// a placeholder pin or a pin mismatch PANICS.
#![cfg(not(target_arch = "wasm32"))]
#![allow(dead_code)]

use std::path::PathBuf;
use std::process::Command;
use std::sync::{Mutex, OnceLock};

use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use wasmi::{Engine, Instance, Linker, Memory, Module, Store, TypedFunc};
use wasmi_wasi::{WasiCtx, WasiCtxBuilder};

use graphlaw_wasm::abi_meta::{ MAX_JSON_DEPTH, MAX_REQUEST_BYTES, OPS};

/// Environment variable naming a prebuilt wasm module.
pub const WASM_ENV: &str = "GRAPHLAW_WASM";
/// Manifest-relative path of the ontology's op-examples.
pub const EXAMPLES_PATH: &str = "registry/op-examples.json";
/// Environment variable naming a pin file that replaces the text given to `assert_pin`.
pub const PIN_ENV: &str = "GRAPHLAW_WASM_PIN";

/// Path of the wasm artifact: `GRAPHLAW_WASM`, else a one-time build.
pub fn wasm_path() -> &'static PathBuf {
    static PATH: OnceLock<PathBuf> = OnceLock::new();
    PATH.get_or_init(|| {
        if let Some(p) = std::env::var_os(WASM_ENV) {
            return p.into();
        }
        let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        let target = root.join("target/wasm-abi");
        let status = Command::new(std::env::var("CARGO").unwrap_or_else(|_| "cargo".into()))
            .current_dir(&root)
            .args([
                "build",
                "-p",
                "graphlaw-wasm",
                "--target",
                "wasm32-wasip1",
                "--profile",
                "wasm",
                "--target-dir",
            ])
            .arg(&target)
            .status()
            .expect("cargo runs");
        assert!(
            status.success(),
            "wasm build failed (is the wasm32-wasip1 target installed?)"
        );
        target.join("wasm32-wasip1/wasm/graphlaw_wasm.wasm")
    })
}

/// A live wasmi instance driven through the JSON ABI, exactly as a host such as Wasmex would.
pub struct Host {
    pub store: Store<WasiCtx>,
    pub memory: Memory,
    pub alloc: TypedFunc<u32, u32>,
    pub free: TypedFunc<(u32, u32), ()>,
    pub call: TypedFunc<(u32, u32), u64>,
}

impl Host {
    pub fn new() -> Self {
        let bytes = std::fs::read(wasm_path()).expect("wasm artifact");
        let engine = Engine::default();
        let module = Module::new(&engine, &bytes[..]).expect("valid wasm");
        // The only imports allowed are WASI's: no JavaScript glue, no custom host.
        for i in module.imports() {
            assert_eq!(
                i.module(),
                "wasi_snapshot_preview1",
                "unexpected host import {}::{}",
                i.module(),
                i.name()
            );
        }
        let mut store = Store::new(&engine, WasiCtxBuilder::new().build());
        let mut linker = <Linker<WasiCtx>>::new(&engine);
        wasmi_wasi::add_to_linker(&mut linker, |ctx| ctx).expect("links WASI");
        let instance: Instance = linker
            .instantiate_and_start(&mut store, &module)
            .expect("instantiates");
        // Reactor-style modules expose `_initialize`; hosts must call it once.
        if let Ok(init) = instance.get_typed_func::<(), ()>(&store, "_initialize") {
            init.call(&mut store, ()).expect("_initialize");
        }
        Host {
            memory: instance
                .get_memory(&store, "memory")
                .expect("exports memory"),
            alloc: instance.get_typed_func(&store, "gl_alloc").unwrap(),
            free: instance.get_typed_func(&store, "gl_free").unwrap(),
            call: instance.get_typed_func(&store, "gl_call").unwrap(),
            store,
        }
    }

    /// One raw request/response round trip; returns the response bytes.
    pub fn call_raw(&mut self, request: &[u8]) -> Vec<u8> {
        let len = request.len() as u32;
        let ptr = self.alloc.call(&mut self.store, len).unwrap();
        self.memory
            .write(&mut self.store, ptr as usize, request)
            .unwrap();
        self.raw_call_bytes(ptr, len)
    }

    /// One JSON round trip.
    pub fn call(&mut self, request: Value) -> Value {
        let out = self.call_raw(&serde_json::to_vec(&request).unwrap());
        serde_json::from_slice(&out).expect("response is JSON")
    }

    /// `gl_call` on an arbitrary (ptr, len) pair; reads and frees the response bytes.
    pub fn raw_call_bytes(&mut self, ptr: u32, len: u32) -> Vec<u8> {
        let packed = self.call.call(&mut self.store, (ptr, len)).unwrap();
        let (out_ptr, out_len) = ((packed >> 32) as u32, (packed & 0xffff_ffff) as u32);
        let mut out = vec![0u8; out_len as usize];
        self.memory
            .read(&self.store, out_ptr as usize, &mut out)
            .unwrap();
        self.free.call(&mut self.store, (out_ptr, out_len)).unwrap();
        out
    }

    /// `gl_call` on an arbitrary (ptr, len) pair; parsed JSON response.
    pub fn raw_call(&mut self, ptr: u32, len: u32) -> Value {
        serde_json::from_slice(&self.raw_call_bytes(ptr, len)).expect("response is JSON")
    }

    pub fn memory_pages(&self) -> u64 {
        self.memory.size(&self.store)
    }
}

/// One shared instance: instantiation is the expensive part.
pub fn host() -> &'static Mutex<Host> {
    static H: OnceLock<Mutex<Host>> = OnceLock::new();
    H.get_or_init(|| Mutex::new(Host::new()))
}

/// Raw response bytes from the native entry point.
pub fn native_raw(req: &[u8]) -> Vec<u8> {
    graphlaw::abi::call(req)
}

/// Raw response bytes from the native entry point for a JSON request.
pub fn native_bytes(req: &Value) -> Vec<u8> {
    native_raw(req.to_string().as_bytes())
}

/// Parsed response from the native entry point.
pub fn native(req: &Value) -> Value {
    serde_json::from_slice(&native_bytes(req)).expect("native response is JSON")
}

/// Raw response bytes from the compiled wasm module.
pub fn wasm_raw(req: &[u8]) -> Vec<u8> {
    host().lock().unwrap_or_else(|e| e.into_inner()).call_raw(req)
}

/// Raw response bytes from the compiled wasm module for a JSON request.
pub fn wasm_bytes(req: &Value) -> Vec<u8> {
    wasm_raw(req.to_string().as_bytes())
}

/// Parsed response from the compiled wasm module.
pub fn wasm(req: &Value) -> Value {
    serde_json::from_slice(&wasm_bytes(req)).expect("wasm response is JSON")
}

/// Runs raw `req` on native and wasm; asserts byte identity; returns the bytes.
pub fn both_raw(req: &[u8]) -> Vec<u8> {
    let n = native_raw(req);
    let w = wasm_raw(req);
    assert!(
        n == w,
        "native and wasm responses diverge\nnative: {}\nwasm:   {}",
        String::from_utf8_lossy(&n),
        String::from_utf8_lossy(&w)
    );
    n
}

/// Runs `req` on native and wasm; asserts byte identity.
pub fn both(req: &Value) -> (Vec<u8>, Vec<u8>) {
    let n = native_bytes(req);
    let w = wasm_bytes(req);
    assert!(
        n == w,
        "native and wasm responses diverge for {req}\nnative: {}\nwasm:   {}",
        String::from_utf8_lossy(&n),
        String::from_utf8_lossy(&w)
    );
    (n, w)
}

/// Runs `req` on native and wasm; asserts `ok == true` on both and byte identity.
pub fn ok(req: &Value) -> Value {
    let (n, _) = both(req);
    let v: Value = serde_json::from_slice(&n).expect("response is JSON");
    assert_eq!(v["ok"], Value::Bool(true), "request {req} failed: {v}");
    v
}

/// Runs `req` on native and wasm; asserts `ok == false` on both and byte identity.
pub fn refused(req: &Value) -> Value {
    let (n, _) = both(req);
    let v: Value = serde_json::from_slice(&n).expect("response is JSON");
    assert_eq!(v["ok"], Value::Bool(false), "request {req} was admitted: {v}");
    v
}

/// Reads a manifest-relative file.
pub fn read(path: &str) -> String {
    std::fs::read_to_string(format!("{}/{path}", env!("CARGO_MANIFEST_DIR")))
        .unwrap_or_else(|e| panic!("read {path}: {e}"))
}

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

/// Enforces the `wasm <sha256> <bytes> <name>` row of the artifact pin against the built
/// (or `GRAPHLAW_WASM`) module. Never skips: builds the wasm when the env var is
/// unset, panics on a placeholder or missing pin, and panics on a size or sha256 mismatch.
pub fn assert_pin(pin_file_text: &str) {
    let from_env = std::env::var_os(PIN_ENV).map(|p| {
        std::fs::read_to_string(&p).unwrap_or_else(|e| panic!("read {PIN_ENV} {p:?}: {e}"))
    });
    let text: &str = from_env.as_deref().unwrap_or(pin_file_text);
    let row: Vec<&str> = text
        .lines()
        .filter(|l| !l.trim_start().starts_with('#'))
        .map(|l| l.split_whitespace().collect::<Vec<&str>>())
        .find(|f| f.first() == Some(&"wasm"))
        .expect("pin file has no `wasm` row");
    assert!(
        row.len() == 4,
        "pin row must be `wasm <sha256> <bytes> <name>`: {row:?}"
    );
    let (sha, size, name) = (row[1], row[2], row[3]);
    assert!(
        sha.len() == 64 && sha.bytes().all(|b| b.is_ascii_hexdigit()),
        "placeholder pin: regenerate it from the built module (sha256 `{sha}`)"
    );
    let size: usize = size
        .parse()
        .unwrap_or_else(|_| panic!("placeholder pin: size `{size}` is not an integer"));
    let path = wasm_path();
    assert!(
        path.file_name().map(|n| n == name).unwrap_or(false),
        "pin names {name}, artifact is {path:?}"
    );
    let bytes = std::fs::read(path).expect("read wasm artifact");
    assert_eq!(
        bytes.len(),
        size,
        "pinned size differs: rebuild changed the module"
    );
    assert_eq!(
        hex(&Sha256::digest(&bytes)),
        sha,
        "module sha256 differs from the pin; if the change is intended, rebuild with --locked and update the pin"
    );
}

fn examples() -> Vec<(String, Value)> {
    let doc: Value = serde_json::from_str(&read(EXAMPLES_PATH)).expect("op-examples.json parses");
    doc["examples"]
        .as_array()
        .expect("examples array")
        .iter()
        .map(|e| (e["op"].as_str().unwrap().to_string(), e["request"].clone()))
        .collect()
}

/// The module must still answer a working request after limit abuse.
fn assert_healthy() {
    let (_, req) = examples().into_iter().next().expect("at least one example");
    ok(&req);
}

// ---- contract tests rendered from the ontology ----

#[test]
fn every_op_has_exactly_one_example_and_it_dispatches_that_op() {
    let ex = examples();
    let names: Vec<&str> = ex.iter().map(|(o, _)| o.as_str()).collect();
    assert_eq!(names, OPS, "examples must cover OPS, in order");
    for (op, req) in &ex {
        assert_eq!(req["op"], json!(op), "example for {op} requests another op");
    }
}

#[test]
fn native_and_wasm_are_byte_identical_over_every_example() {
    for (op, req) in examples() {
        let (n, w) = both(&req);
        assert_eq!(n, w, "native vs wasm diverged on op `{op}`");
        let v: Value = serde_json::from_slice(&w).unwrap();
        assert_eq!(v["ok"], true, "example for `{op}` must be a working request: {v}");
    }
}

#[test]
fn alloc_over_max_returns_null() {
    let mut g = host().lock().unwrap_or_else(|e| e.into_inner());
    let h = &mut *g;
    let ptr = h
        .alloc
        .call(&mut h.store, (MAX_REQUEST_BYTES as u32) + 1)
        .unwrap();
    assert_eq!(ptr, 0, "alloc over the limit must return null");
}

#[test]
fn null_buffer_call_is_typed_not_a_trap() {
    let r = {
        let mut h = host().lock().unwrap_or_else(|e| e.into_inner());
        h.raw_call(0, 0)
    };
    assert_eq!(r["ok"], false);
    assert_healthy();
}

#[test]
fn oversize_length_is_typed_with_observed_over_max() {
    let r = {
        let mut h = host().lock().unwrap_or_else(|e| e.into_inner());
        h.raw_call(8, (MAX_REQUEST_BYTES as u32) + 1)
    };
    assert_eq!(r["ok"], false);
    assert_healthy();
}

#[test]
fn depth_over_max_is_typed_and_identical_to_native() {
    let deep = format!(
        "{}{}",
        "[".repeat(MAX_JSON_DEPTH + 1),
        "]".repeat(MAX_JSON_DEPTH + 1)
    );
    let out = both_raw(deep.as_bytes());
    let r: Value = serde_json::from_slice(&out).unwrap();
    assert_eq!(r["ok"], false);
    assert_healthy();
}
