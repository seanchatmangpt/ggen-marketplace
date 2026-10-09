//! Content-hash vectorize cache: replay stored hypervectors instead of
//! re-encoding an unchanged claims corpus.
//!
//! Cache key = BLAKE3 of the canonical JSON serialization of the claims
//! array. A hit skips `encode_doc`; a mismatch (edited claims) produces a
//! different key and recomputes. Off by default: enabled only when
//! `--cache <dir>` is passed (or `$DOC_HDIT_CACHE`/`$XDG_CACHE_HOME` is set).

use super::Hv;
use std::fs;
use std::io;
use std::path::PathBuf;

/// BLAKE3 hex digest of the serialized claims array.
pub fn claims_corpus_key(claims: &[crate::Claim]) -> String {
    let bytes = serde_json::to_vec(claims).expect("serialize claims for cache key");
    let mut hasher = blake3::Hasher::new();
    hasher.update(&bytes);
    hasher.finalize().to_hex().to_string()
}

/// Resolve the cache directory: `--cache` flag wins, then `$DOC_HDIT_CACHE`,
/// then `$XDG_CACHE_HOME/doc-hdit`. `None` = caching off (the default).
pub fn resolve_cache_dir(flag: Option<&str>) -> Option<PathBuf> {
    if let Some(d) = flag {
        return Some(PathBuf::from(d));
    }
    if let Ok(d) = std::env::var("DOC_HDIT_CACHE") {
        if !d.is_empty() {
            return Some(PathBuf::from(d));
        }
    }
    std::env::var("XDG_CACHE_HOME")
        .ok()
        .filter(|d| !d.is_empty())
        .map(|d| PathBuf::from(d).join("doc-hdit"))
}

fn cache_file(dir: &PathBuf, key: &str) -> PathBuf {
    dir.join(format!("vectorize-{}.json", key))
}

/// Load the cached `H_doc` vector for this corpus key, if present and
/// well-formed. Any read/parse/shape error is a miss, never a failure.
pub fn load_h_doc(dir: &PathBuf, key: &str) -> Option<Hv> {
    let bytes = fs::read(cache_file(dir, key)).ok()?;
    let v: Hv = serde_json::from_slice(&bytes).ok()?;
    if v.len() != crate::DIM {
        return None;
    }
    Some(v)
}

/// Store the `H_doc` vector for this corpus key. Best-effort: a write
/// failure is reported on stderr but never changes the audit outcome.
pub fn store_h_doc(dir: &PathBuf, key: &str, v: &Hv) -> io::Result<()> {
    fs::create_dir_all(dir)?;
    let bytes = serde_json::to_vec(v)?;
    fs::write(cache_file(dir, key), bytes)
}

/// Content key for the downstream vectorization results: BLAKE3 over the
/// serialized claims, code modules, external-dep allowlist, and directory
/// list — everything the per-claim projections and phantom ranking derive
/// from. Any edit to any input changes the key and forces a recompute.
pub fn derived_key(
    claims: &[crate::Claim],
    modules: &[crate::CodeModule],
    external: &[String],
    directories: &[String],
) -> String {
    let mut hasher = blake3::Hasher::new();
    for part in [
        serde_json::to_vec(claims).expect("serialize claims"),
        serde_json::to_vec(modules).expect("serialize modules"),
        serde_json::to_vec(external).expect("serialize external"),
        serde_json::to_vec(directories).expect("serialize directories"),
    ] {
        let len = (part.len() as u64).to_le_bytes();
        hasher.update(&len);
        hasher.update(&part);
    }
    hasher.finalize().to_hex().to_string()
}

/// Downstream bulk vectorization results (per-claim projection passes),
/// replayable when the input corpus is unchanged.
#[derive(serde::Serialize, serde::Deserialize)]
pub struct DerivedVectors {
    /// bundle of binarized per-claim projections onto the public code basis.
    pub p_code_pub: Hv,
    /// Same, onto the raw (full-surface) code basis.
    pub p_code_raw: Hv,
    /// (claim_index, vsa_alignment, grounded), sorted worst first.
    pub ranked: Vec<(usize, f64, bool)>,
}

/// Load the cached derived vectorization results, if present and well-formed.
pub fn load_derived(dir: &PathBuf, key: &str) -> Option<DerivedVectors> {
    let bytes = fs::read(cache_file2(dir, "derived", key)).ok()?;
    serde_json::from_slice(&bytes).ok()
}

/// Store the derived vectorization results. Best-effort.
pub fn store_derived(dir: &PathBuf, key: &str, d: &DerivedVectors) -> io::Result<()> {
    fs::create_dir_all(dir)?;
    let bytes = serde_json::to_vec(d)?;
    fs::write(cache_file2(dir, "derived", key), bytes)
}

fn cache_file2(dir: &PathBuf, prefix: &str, key: &str) -> PathBuf {
    dir.join(format!("{}-{}.json", prefix, key))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Claim;

    fn claim(id: &str) -> Claim {
        Claim {
            id: id.to_string(),
            subject: "s".into(),
            predicate: "p".into(),
            object: "o".into(),
        }
    }

    #[test]
    fn key_is_deterministic_and_content_sensitive() {
        let a = claims_corpus_key(&[claim("1"), claim("2")]);
        let b = claims_corpus_key(&[claim("1"), claim("2")]);
        let c = claims_corpus_key(&[claim("1"), claim("3")]);
        assert_eq!(a, b);
        assert_ne!(a, c);
        assert_eq!(a.len(), 64); // blake3 hex
    }

    #[test]
    fn store_then_load_roundtrips() {
        let dir = std::env::temp_dir().join(format!("doc-hdit-cache-test-{}", std::process::id()));
        let key = claims_corpus_key(&[claim("x")]);
        let v: Hv = (0..crate::DIM).map(|i| if i % 2 == 0 { 1 } else { -1 }).collect();
        store_h_doc(&dir, &key, &v).expect("store");
        let loaded = load_h_doc(&dir, &key).expect("hit");
        assert_eq!(loaded, v);
        // Edited corpus (different key) misses.
        assert!(load_h_doc(&dir, &claims_corpus_key(&[claim("y")])).is_none());
        std::fs::remove_dir_all(&dir).ok();
    }
}
