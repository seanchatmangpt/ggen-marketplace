//! Hand-written reference domain for the `gl` core-WASM contract (the irreducible residue; the ABI
//! shim around it is generated). FNV-1a digest of the request with typed refusals.

/// Typed refusal response (a refusal is neither a trap nor an unsupported op).
pub fn refusal(code: &str) -> Vec<u8> {
    format!("{{\"refused\":\"{code}\"}}").into_bytes()
}

/// Deterministic observable: `{"ok":"<fnv1a64 hex>","len":n}` or a refusal.
pub fn call(request: &[u8]) -> Vec<u8> {
    if request.is_empty() {
        return refusal("malformed-input");
    }
    if request.starts_with(b"unsupported:") {
        return refusal("unsupported");
    }
    let mut h: u64 = 0xcbf2_9ce4_8422_2325;
    for b in request {
        h ^= u64::from(*b);
        h = h.wrapping_mul(0x0100_0000_01b3);
    }
    format!("{{\"ok\":\"{h:016x}\",\"len\":{}}}", request.len()).into_bytes()
}
