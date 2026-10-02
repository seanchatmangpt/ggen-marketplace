//! WebAssembly FFI shell for `echo-wasm`: the only `unsafe` in the crate.
//
// Consumed query columns (ffi.rq): crate_name, export_prefix, abi_version,
// max_request_bytes.
// Wire-convention columns (ffi.rq): return_convention, symbol_suffix,
// input_release_policy, abi_version_export_symbol.
// Rendered by ggen (wasi-json-abi-pack) from the wja: graph.
// Edit the ontology and re-render; never edit this file by hand.
//
// Protocol (ABI version 1, request limit 1048576 bytes; all
// integers are wasm `i32`/`i64`):
// 1. `w4p_alloc_v1(len) -> ptr`: host reserves `len` bytes and writes a UTF-8
//    JSON request there. Returns null when `len` exceeds the request limit.
// 2. `w4p_call_v1(ptr, len, out_len) -> out_ptr`: runs the request and reads the request buffer without freeing it (the host releases it
//    via `w4p_dealloc_v1`); the response
//    length is written through `out_len`.
// 3. host reads `out_len` bytes at `out_ptr` (UTF-8 JSON), then
//    `w4p_free_v1(out_ptr, out_len)`, and releases the request buffer with
//    `w4p_dealloc_v1(ptr, len)` (same `len` as alloc).
//
// A null request pointer or an oversize length never traps: the call returns a
// typed error response built by the safe core.
//
// Contract with the hand-written safe core (`crate::abi`):
//   pub fn call(request: &[u8]) -> Vec<u8>
//   pub fn limit_response(name: &str, observed: usize, max: usize) -> Vec<u8>
//   pub fn missing_buffer_response() -> Vec<u8>
// and with the generated `crate::abi_meta`: `ABI_VERSION: u32`,
// `MAX_REQUEST_BYTES: usize`.
//
// Allocation discipline: every buffer crossing the boundary is a `Box<[u8]>` of
// length `len.max(1)`, so `_free` / `_call` reconstruct the exact allocation.
#![allow(unsafe_code)]
#![deny(missing_docs)]
// Native builds only exercise the helpers through tests; the exports are wasm32-only.
#![cfg_attr(not(target_arch = "wasm32"), allow(dead_code))]

#[cfg(any(target_arch = "wasm32", test))]
use crate::abi_meta::ABI_VERSION;
use crate::abi_meta::MAX_REQUEST_BYTES;

/// Leak a boxed buffer to the host as a raw pointer.
fn into_raw(buf: Box<[u8]>) -> *mut u8 {
    Box::into_raw(buf) as *mut u8
}

/// Reclaim a buffer previously produced by [`into_raw`].
///
/// # Safety
/// `ptr` must come from this module and `len` must be the length that was
/// requested / returned for it; each pair may be reclaimed exactly once.
unsafe fn from_raw(ptr: *mut u8, len: u32) -> Box<[u8]> {
    let n = (len as usize).max(1);
    // SAFETY: caller guarantees ptr/len describe a live allocation of `n` bytes.
    unsafe { Box::from_raw(core::ptr::slice_from_raw_parts_mut(ptr, n)) }
}

/// Reserve `len` zeroed bytes; null when `len` exceeds the request limit.
pub fn alloc_buf(len: u32) -> *mut u8 {
    if len as usize > MAX_REQUEST_BYTES {
        return core::ptr::null_mut();
    }
    into_raw(vec![0u8; (len as usize).max(1)].into_boxed_slice())
}

/// Release a buffer pair handed out by this module (a request buffer from [`alloc_buf`] or a response buffer from a call).
///
/// # Safety
/// `ptr`/`len` must be exactly a pair previously handed out by this module.
pub unsafe fn free_buf(ptr: *mut u8, len: u32) {
    if !ptr.is_null() {
        // SAFETY: forwarded caller contract.
        drop(unsafe { from_raw(ptr, len) });
    }
}

/// Run one borrowed request buffer and return the JSON response bytes. The
/// host owns the input buffer, so this only reads through `ptr` and never
/// reconstructs or frees it. Null pointers and oversize lengths yield typed
/// error responses; releasing the input stays the host's job.
///
/// # Safety
/// `ptr`/`len` must describe a host-owned readable buffer of `len` bytes.
pub unsafe fn call_borrowed(ptr: *const u8, len: u32) -> Vec<u8> {
    let response = if ptr.is_null() {
        crate::abi::missing_buffer_response()
    } else if len as usize > MAX_REQUEST_BYTES {
        crate::abi::limit_response("request_bytes", len as usize, MAX_REQUEST_BYTES)
    } else {
        // SAFETY: caller guarantees `len` readable bytes behind `ptr`.
        let request = unsafe { core::slice::from_raw_parts(ptr, len as usize) };
        crate::abi::call(request)
    };
    if response.is_empty() {
        // Keep len >= 1 so the host's free reclaims the exact allocation.
        return b"{}".to_vec();
    }
    response
}

/// Hand a response to the host through the out-len pointer: the response
/// length is written through `out_len` and the response buffer pointer is
/// returned directly.
fn hand_response(response: Vec<u8>, out_len: *mut usize) -> *mut u8 {
    if !out_len.is_null() {
        // SAFETY: `out_len` is the host-supplied response-length pointer
        // required by the ABI contract.
        unsafe { *out_len = response.len() };
    }
    into_raw(response.into_boxed_slice())
}

/// ABI revision; see [`crate::abi_meta::ABI_VERSION`].
#[cfg(target_arch = "wasm32")]
#[unsafe(no_mangle)]
pub extern "C" fn w4pm_module_version_v1() -> u32 {
    ABI_VERSION
}

/// Reserve `len` bytes of linear memory for the host. Returns null (0) when
/// `len` exceeds the request limit; a following `w4p_call_v1` on that null
/// buffer yields a typed error response, never a trap.
#[cfg(target_arch = "wasm32")]
#[unsafe(no_mangle)]
pub extern "C" fn w4p_alloc_v1(len: u32) -> *mut u8 {
    alloc_buf(len)
}

/// Release a request buffer obtained from `w4p_alloc_v1`.
/// Reading an input never frees it: releasing request buffers is the host's job.
///
/// # Safety
/// `ptr`/`len` must be exactly a pair previously handed out by this module.
#[cfg(target_arch = "wasm32")]
#[unsafe(no_mangle)]
pub unsafe extern "C" fn w4p_dealloc_v1(ptr: *mut u8, len: u32) {
    // SAFETY: forwarded caller contract.
    unsafe { free_buf(ptr, len) }
}

/// Release a response buffer returned by `w4p_call_v1`.
///
/// # Safety
/// `ptr`/`len` must be exactly a pair previously handed out by this module.
#[cfg(target_arch = "wasm32")]
#[unsafe(no_mangle)]
pub unsafe extern "C" fn w4p_free_v1(ptr: *mut u8, len: u32) {
    // SAFETY: forwarded caller contract.
    unsafe { free_buf(ptr, len) }
}

/// Execute one JSON request; the response length is written through `out_len`
/// and the response buffer pointer is returned.
///
/// # Safety
/// `ptr`/`len` must describe a buffer from `w4p_alloc_v1` filled by the host;
/// `out_len` must be a writable `usize`.
#[cfg(target_arch = "wasm32")]
#[unsafe(no_mangle)]
pub unsafe extern "C" fn w4p_call_v1(ptr: *mut u8, len: u32, out_len: *mut usize) -> *mut u8 {
    // SAFETY: forwarded caller contract.
    hand_response(unsafe { call_borrowed(ptr, len) }, out_len)
}

#[cfg(all(test, not(target_arch = "wasm32")))]
mod tests {
    use super::*;

    #[test]
    fn alloc_over_limit_is_null() {
        assert!(alloc_buf((MAX_REQUEST_BYTES as u32).saturating_add(1)).is_null());
    }

    #[test]
    fn alloc_free_roundtrip_including_zero_len() {
        for len in [0u32, 1, 17] {
            let p = alloc_buf(len);
            assert!(!p.is_null());
            unsafe { free_buf(p, len) };
        }
    }

    #[test]
    fn null_and_oversize_call_are_typed_not_traps() {
        let a = unsafe { call_borrowed(core::ptr::null(), 0) };
        assert!(!a.is_empty());
        let b = unsafe { call_borrowed(core::ptr::dangling::<u8>(), (MAX_REQUEST_BYTES as u32).saturating_add(1)) };
        assert!(!b.is_empty());
    }

    #[test]
    fn abi_version_is_nonzero() {
        const { assert!(ABI_VERSION >= 1) };
    }
}
