//! BLAKE3 chained gate receipts (`doc-hdit certify`), v1.
//!
//! Follows the osx-clnr affidavit receipt-chain pattern: an append-only
//! JSONL chain where each receipt's `parent` is the previous receipt's
//! `hash`, and `hash = blake3(canonical JSON of the receipt fields,
//! excluding `hash` itself)`. Full ed25519 witness signatures (affidavit
//! `receipts_certified`) are v2 scope and are NOT present in v1 receipts.

use serde_json::{json, Value};
use std::path::Path;

/// Domain-separation prefix for the receipt chain hash.
pub const CERTIFY_DOMAIN: &str = "doc-hdit-certify/v1";

/// One certified audit run. `verdict` is always ACCEPTED here; a failing
/// audit never reaches [`mint_receipt`] (the CLI exits REFUSED with no
/// receipt).
#[derive(Debug, Clone)]
pub struct GateOutcome {
    pub s_coverage: f64,
    pub phi_halluc: f64,
    pub q_density: f64,
}

#[derive(Debug, Clone)]
pub struct Thresholds {
    pub s_coverage_min: f64,
    pub phi_max: f64,
    pub q_density_min: f64,
}

/// BLAKE3 digest over the certified subject: the exact inputs.json bytes
/// plus (optionally) the rendered docs tree. Docs files are hashed in
/// sorted relative-path order so the digest is deterministic.
pub fn subject_digest(inputs_bytes: &[u8], docs_dir: Option<&Path>) -> std::io::Result<String> {
    let mut hasher = blake3::Hasher::new();
    hasher.update(b"doc-hdit/subject/v1|inputs|");
    hasher.update(inputs_bytes);
    if let Some(dir) = docs_dir {
        hasher.update(b"|docs|");
        let mut files: Vec<std::path::PathBuf> = Vec::new();
        collect_files(dir, &mut files)?;
        files.sort();
        for f in &files {
            let rel = f.strip_prefix(dir).unwrap_or(f).to_string_lossy();
            let bytes = std::fs::read(f)?;
            hasher.update(rel.as_bytes());
            hasher.update(b"\0");
            hasher.update(blake3::hash(&bytes).as_bytes());
        }
    }
    Ok(hasher.finalize().to_hex().to_string())
}

fn collect_files(dir: &Path, out: &mut Vec<std::path::PathBuf>) -> std::io::Result<()> {
    if !dir.exists() {
        return Ok(());
    }
    for entry in std::fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_dir() {
            collect_files(&path, out)?;
        } else {
            out.push(path);
        }
    }
    Ok(())
}

/// Extractor identity: BLAKE3 hex over the extractor source bytes. Certify
/// receipts natively bind the identity of the extractor that produced the
/// inputs (fleet law [150]: verdicts track extractor identity, not docs).
pub fn extractor_identity(path: &Path) -> std::io::Result<String> {
    let bytes = std::fs::read(path)?;
    Ok(blake3::hash(&bytes).to_hex().to_string())
}

/// The canonical hash input: every receipt field except `hash`, serialized
/// with serde_json's sorted-key canonical form.
pub fn chain_payload(
    subject: &str,
    parent: &str,
    gates: &GateOutcome,
    thresholds: &Thresholds,
    timestamp_secs: u64,
    extractor: &str,
) -> Value {
    json!({
        "extractor": extractor,
        "gates": {
            "Phi_halluc": gates.phi_halluc,
            "Q_density": gates.q_density,
            "S_coverage": gates.s_coverage,
        },
        "parent": parent,
        "subject": subject,
        "thresholds": {
            "Phi_halluc_max": thresholds.phi_max,
            "Q_density_min": thresholds.q_density_min,
            "S_coverage_min": thresholds.s_coverage_min,
        },
        "timestamp": timestamp_secs,
        "verdict": "ACCEPTED",
    })
}

/// BLAKE3 chain hash over the domain-separated canonical payload.
pub fn chain_hash(payload: &Value) -> String {
    blake3::hash(format!("{CERTIFY_DOMAIN}|{payload}").as_bytes())
        .to_hex()
        .to_string()
}

/// Mint one chained ACCEPTED receipt (including its `hash` field).
#[allow(clippy::too_many_arguments)]
pub fn mint_receipt(
    subject: &str,
    parent: &str,
    gates: &GateOutcome,
    thresholds: &Thresholds,
    timestamp_secs: u64,
    extractor: &str,
) -> Value {
    let payload = chain_payload(subject, parent, gates, thresholds, timestamp_secs, extractor);
    let hash = chain_hash(&payload);
    let mut receipt = payload;
    receipt["hash"] = json!(hash);
    receipt
}

/// Append one receipt line to the JSONL chain file. Returns the minted
/// receipt. `chain_path`'s parent directory is created if missing.
pub fn append_receipt(chain_path: &Path, receipt: &Value) -> std::io::Result<()> {
    if let Some(parent) = chain_path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    use std::io::Write;
    let mut f = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(chain_path)?;
    writeln!(f, "{receipt}")
}

/// Read the last receipt's `hash` from the JSONL chain ("" for genesis).
pub fn last_chain_hash(chain_path: &Path) -> std::io::Result<String> {
    match std::fs::read_to_string(chain_path) {
        Ok(text) => Ok(text
            .lines()
            .rev()
            .find(|l| !l.trim().is_empty())
            .and_then(|l| serde_json::from_str::<Value>(l).ok())
            .and_then(|v| v["hash"].as_str().map(str::to_string))
            .unwrap_or_default()),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(String::new()),
        Err(e) => Err(e),
    }
}

/// Read the last receipt's recorded extractor identity ("" when the chain is
/// empty OR the last receipt predates the extractor pin — such receipts are
/// grandfathered and never trigger [`super`]-level mismatch refusals).
pub fn last_chain_extractor(chain_path: &Path) -> std::io::Result<String> {
    match std::fs::read_to_string(chain_path) {
        Ok(text) => Ok(text
            .lines()
            .rev()
            .find(|l| !l.trim().is_empty())
            .and_then(|l| serde_json::from_str::<Value>(l).ok())
            .and_then(|v| v["extractor"].as_str().map(str::to_string))
            .unwrap_or_default()),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(String::new()),
        Err(e) => Err(e),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn gates() -> GateOutcome {
        GateOutcome {
            s_coverage: 0.95,
            phi_halluc: 0.0005,
            q_density: 0.7,
        }
    }

    fn thresholds() -> Thresholds {
        Thresholds {
            s_coverage_min: 0.90,
            phi_max: 0.001,
            q_density_min: 0.65,
        }
    }

    #[test]
    fn receipt_hash_is_reproducible_and_chain_links() {
        let r1 = mint_receipt("subj", "", &gates(), &thresholds(), 1_700_000_000, "ext-a");
        let r1_again = mint_receipt("subj", "", &gates(), &thresholds(), 1_700_000_000, "ext-a");
        assert_eq!(r1, r1_again, "same inputs must mint byte-identical receipt");
        assert_eq!(r1["extractor"], "ext-a", "receipt binds extractor identity");

        let r2 = mint_receipt("subj", r1["hash"].as_str().unwrap(), &gates(), &thresholds(), 1_700_000_001, "ext-a");
        assert_ne!(r1["hash"], r2["hash"]);
        assert_eq!(r2["parent"], r1["hash"], "child must link to parent hash");

        // Recompute the hash from the receipt's own fields.
        let mut fields = r2.clone();
        let claimed = fields
            .as_object_mut()
            .unwrap()
            .remove("hash")
            .expect("receipt carries hash");
        assert_eq!(chain_hash(&fields), claimed, "hash must bind all fields");
    }

    #[test]
    fn chain_file_roundtrip() {
        let dir = std::env::temp_dir().join(format!("doc-hdit-certify-test-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let chain = dir.join("receipts.jsonl");

        assert_eq!(last_chain_hash(&chain).unwrap(), "", "missing chain = genesis");
        let r1 = mint_receipt("s", "", &gates(), &thresholds(), 1, "ext-a");
        append_receipt(&chain, &r1).unwrap();
        let r2 = mint_receipt("s", &last_chain_hash(&chain).unwrap(), &gates(), &thresholds(), 2, "ext-a");
        append_receipt(&chain, &r2).unwrap();
        assert_eq!(last_chain_hash(&chain).unwrap(), r2["hash"]);

        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn subject_digest_covers_docs_tree() {
        let dir = std::env::temp_dir().join(format!("doc-hdit-subj-test-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(dir.join("sub")).unwrap();
        std::fs::write(dir.join("sub").join("b.md"), "hello").unwrap();
        std::fs::write(dir.join("a.md"), "world").unwrap();
        let d1 = subject_digest(b"{}", Some(&dir)).unwrap();
        let d2 = subject_digest(b"{}", Some(&dir)).unwrap();
        assert_eq!(d1, d2, "digest deterministic over same tree");
        std::fs::write(dir.join("a.md"), "tampered").unwrap();
        let d3 = subject_digest(b"{}", Some(&dir)).unwrap();
        assert_ne!(d1, d3, "tampered doc must change subject digest");
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn extractor_identity_is_content_hash_and_drift_sensitive() {
        let dir = std::env::temp_dir().join(format!("doc-hdit-ext-test-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let script = dir.join("extractor.py");
        std::fs::write(&script, "print('v1')\n").unwrap();
        let id1 = extractor_identity(&script).unwrap();
        std::fs::write(&script, "print('v2')\n").unwrap();
        let id2 = extractor_identity(&script).unwrap();
        assert_eq!(id1.len(), 64, "BLAKE3 hex");
        assert_ne!(id1, id2, "any extractor source change moves identity");
        assert!(extractor_identity(&dir.join("missing")).is_err());
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn last_chain_extractor_grandfathers_legacy_receipts() {
        let dir = std::env::temp_dir().join(format!("doc-hdit-ext-chain-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let chain = dir.join("receipts.jsonl");

        // Legacy receipt with no extractor field.
        let legacy = json!({"hash": "abc", "subject": "s", "verdict": "ACCEPTED"});
        append_receipt(&chain, &legacy).unwrap();
        assert_eq!(
            last_chain_extractor(&chain).unwrap(),
            "",
            "missing extractor field = grandfathered, empty identity"
        );

        // Pinned receipt: identity is readable back.
        let pinned = mint_receipt("s", "", &gates(), &thresholds(), 1, "ext-a");
        append_receipt(&chain, &pinned).unwrap();
        assert_eq!(last_chain_extractor(&chain).unwrap(), "ext-a");
        let _ = std::fs::remove_dir_all(&dir);
    }
}
