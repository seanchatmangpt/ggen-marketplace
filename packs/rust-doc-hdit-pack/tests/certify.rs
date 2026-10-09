//! Chicago-style certify integration tests: run the real `doc-hdit`
//! binary end to end (subprocess, temp files, no mocks) and assert on
//! the emitted receipt chain state.

use std::path::PathBuf;
use std::process::Command;

fn bin() -> &'static str {
    env!("CARGO_BIN_EXE_doc-hdit")
}

fn temp_dir(tag: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!("doc-hdit-certify-it-{}-{}", tag, std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    d
}

fn pass_inputs() -> String {
    // Grounded fixture: every claim matches a code-surface fact.
    serde_json::json!({
        "modules": [{
            "name": "engine",
            "items": [
                {"kind": "fn", "ident": "ignite", "signature": "ignite(fuel: Fuel) -> Spark"},
                {"kind": "struct", "ident": "Piston", "signature": "Piston { bore: u32 }"}
            ]
        }],
        "claims": [
            {"id": "c0", "subject": "fn", "predicate": "ignite", "object": "ignite(fuel: Fuel) -> Spark"},
            {"id": "c1", "subject": "struct", "predicate": "Piston", "object": "Piston { bore: u32 }"}
        ]
    })
    .to_string()
}

fn fail_inputs() -> String {
    // Phantom claim the code surface cannot ground.
    serde_json::json!({
        "modules": [{
            "name": "engine",
            "items": [
                {"kind": "fn", "ident": "ignite", "signature": "ignite(fuel: Fuel) -> Spark"}
            ]
        }],
        "claims": [
            {"id": "c0", "subject": "fn", "predicate": "ignite", "object": "ignite(fuel: Fuel) -> Spark"},
            {"id": "c1", "subject": "fn", "predicate": "teleport", "object": "teleport(warp: Warp)"}
        ]
    })
    .to_string()
}

fn run(args: &[&str]) -> (i32, String, String) {
    let out = Command::new(bin()).args(args).output().expect("spawn doc-hdit");
    (
        out.status.code().unwrap_or(-1),
        String::from_utf8_lossy(&out.stdout).into_owned(),
        String::from_utf8_lossy(&out.stderr).into_owned(),
    )
}

#[test]
fn certify_pass_mints_chained_receipt() {
    let dir = temp_dir("pass");
    let inputs = dir.join("inputs.json");
    let chain = dir.join("receipts.jsonl");
    std::fs::write(&inputs, pass_inputs()).unwrap();

    let (code, stdout, stderr) = run(&["certify", inputs.to_str().unwrap(), "--chain", chain.to_str().unwrap()]);
    assert_eq!(code, 0, "stdout={}\nstderr={}", stdout, stderr);

    let receipt: serde_json::Value =
        serde_json::from_str(stdout.lines().next().unwrap()).expect("first stdout line is receipt JSON");
    assert_eq!(receipt["verdict"], "ACCEPTED");
    assert_eq!(receipt["parent"], "", "genesis receipt has empty parent");
    assert!(receipt["subject"].as_str().unwrap().len() == 64, "BLAKE3 hex subject");
    assert!(receipt["gates"]["S_coverage"].is_number());
    assert_eq!(
        receipt["extractor"], "",
        "unpinned certify still emits the extractor field (empty identity)"
    );
    assert!(receipt["thresholds"]["S_coverage_min"].is_number());
    let hash1 = receipt["hash"].as_str().unwrap().to_string();

    // Chain file has exactly one line; hash recomputes from fields.
    let chain_text = std::fs::read_to_string(&chain).unwrap();
    assert_eq!(chain_text.lines().count(), 1);
    let mut fields = receipt.clone();
    let claimed = fields
        .as_object_mut()
        .unwrap()
        .remove("hash")
        .expect("receipt carries hash");
    assert_eq!(
        doc_hdit::certify::chain_hash(&fields),
        claimed,
        "receipt hash must bind all receipt fields"
    );

    // Second certify appends and links to the first hash.
    let (code, stdout, _) = run(&["certify", inputs.to_str().unwrap(), "--chain", chain.to_str().unwrap()]);
    assert_eq!(code, 0);
    let r2: serde_json::Value = serde_json::from_str(stdout.lines().next().unwrap()).unwrap();
    assert_eq!(r2["parent"], json_str(&hash1), "child parent = previous hash");
    assert_ne!(r2["hash"], receipt["hash"]);
    assert_eq!(std::fs::read_to_string(&chain).unwrap().lines().count(), 2);

    let _ = std::fs::remove_dir_all(&dir);
}

#[test]
fn certify_fail_refuses_without_receipt() {
    let dir = temp_dir("fail");
    let inputs = dir.join("inputs.json");
    let chain = dir.join("receipts.jsonl");
    std::fs::write(&inputs, fail_inputs()).unwrap();
    // Strict court: Phi_halluc_max below what the phantom claim produces.
    let court = dir.join("strict.court");
    std::fs::write(&court, "Phi_halluc_max = 0.0000001\n").unwrap();

    let (code, stdout, stderr) = run(&[
        "certify",
        inputs.to_str().unwrap(),
        court.to_str().unwrap(),
        "--chain",
        chain.to_str().unwrap(),
    ]);
    assert_ne!(code, 0, "certify must fail closed; stdout={}", stdout);
    assert!(
        stderr.contains("REFUSED:DOC_HDIT_CERTIFY"),
        "expected typed refusal, got: {}",
        stderr
    );
    assert!(!chain.exists(), "no receipt may be minted on refusal");
    let _ = std::fs::remove_dir_all(&dir);
}

fn json_str(s: &str) -> String {
    s.to_string()
}

#[test]
fn certify_pins_extractor_and_refuses_drift_typed() {
    let dir = temp_dir("ext");
    let inputs = dir.join("inputs.json");
    let chain = dir.join("receipts.jsonl");
    let ext_a = dir.join("extractor_a.py");
    let ext_b = dir.join("extractor_b.py");
    std::fs::write(&inputs, pass_inputs()).unwrap();
    std::fs::write(&ext_a, "# extractor v1\n").unwrap();
    std::fs::write(&ext_b, "# extractor v2 (drifted)\n").unwrap();

    // 1. Pinned certify embeds the identity into the receipt, bound by hash.
    let (code, stdout, stderr) = run(&[
        "certify", inputs.to_str().unwrap(), "--chain", chain.to_str().unwrap(),
        "--extractor", ext_a.to_str().unwrap(),
    ]);
    assert_eq!(code, 0, "stdout={}\nstderr={}", stdout, stderr);
    let r1: serde_json::Value = serde_json::from_str(stdout.lines().next().unwrap()).unwrap();
    let id_a = doc_hdit::certify::extractor_identity(&ext_a).unwrap();
    assert_eq!(r1["extractor"], id_a.as_str(), "receipt embeds extractor BLAKE3");
    let mut fields = r1.clone();
    let claimed = fields.as_object_mut().unwrap().remove("hash").unwrap();
    assert_eq!(
        doc_hdit::certify::chain_hash(&fields),
        claimed,
        "hash must bind the extractor field"
    );

    // 2. Replay with the SAME extractor: ACCEPTED, appended.
    let (code, stdout, stderr) = run(&[
        "certify", inputs.to_str().unwrap(), "--chain", chain.to_str().unwrap(),
        "--extractor", ext_a.to_str().unwrap(),
    ]);
    assert_eq!(code, 0, "matching replay must pass; stderr={}", stderr);
    let r2: serde_json::Value = serde_json::from_str(stdout.lines().next().unwrap()).unwrap();
    assert_eq!(r2["extractor"], r1["extractor"]);

    // 3. Replay with a DRIFTED extractor: typed refusal, no receipt minted.
    let lines_before = std::fs::read_to_string(&chain).unwrap().lines().count();
    let (code, stdout, stderr) = run(&[
        "certify", inputs.to_str().unwrap(), "--chain", chain.to_str().unwrap(),
        "--extractor", ext_b.to_str().unwrap(),
    ]);
    assert_ne!(code, 0, "drifted extractor must refuse; stdout={}", stdout);
    assert!(
        stderr.contains("REFUSED:EXTRACTOR_MISMATCH"),
        "expected typed extractor refusal, got: {}",
        stderr
    );
    assert_eq!(
        std::fs::read_to_string(&chain).unwrap().lines().count(),
        lines_before,
        "no receipt minted on extractor mismatch"
    );

    // 4. --force-rebaseline acknowledges the drift and mints a NEW receipt
    //    under the new identity.
    let (code, stdout, stderr) = run(&[
        "certify", inputs.to_str().unwrap(), "--chain", chain.to_str().unwrap(),
        "--extractor", ext_b.to_str().unwrap(), "--force-rebaseline",
    ]);
    assert_eq!(code, 0, "force-rebaseline must mint; stderr={}", stderr);
    let r3: serde_json::Value = serde_json::from_str(stdout.lines().next().unwrap()).unwrap();
    let id_b = doc_hdit::certify::extractor_identity(&ext_b).unwrap();
    assert_eq!(r3["extractor"], id_b.as_str(), "new baseline carries new identity");
    assert_ne!(r3["extractor"], r1["extractor"]);
    assert_eq!(r3["parent"], r2["hash"], "rebaseline chains onto the old tip");

    let _ = std::fs::remove_dir_all(&dir);
}

#[test]
fn certify_legacy_chain_without_extractor_is_grandfathered() {
    let dir = temp_dir("legacy");
    let inputs = dir.join("inputs.json");
    let chain = dir.join("receipts.jsonl");
    let ext = dir.join("extractor.py");
    std::fs::write(&inputs, pass_inputs()).unwrap();
    std::fs::write(&ext, "# extractor v1\n").unwrap();
    // Legacy chain: one receipt with no extractor field.
    let legacy = serde_json::json!({
        "gates": {"S_coverage": 1.0}, "hash": "deadbeef", "parent": "",
        "subject": "s", "verdict": "ACCEPTED"
    });
    use std::io::Write;
    let mut f = std::fs::File::create(&chain).unwrap();
    writeln!(f, "{}", legacy).unwrap();
    drop(f);

    let (code, stdout, stderr) = run(&[
        "certify", inputs.to_str().unwrap(), "--chain", chain.to_str().unwrap(),
        "--extractor", ext.to_str().unwrap(),
    ]);
    assert_eq!(code, 0, "legacy chain must stay valid; stderr={}", stderr);
    let r: serde_json::Value = serde_json::from_str(stdout.lines().next().unwrap()).unwrap();
    assert_eq!(r["parent"], "deadbeef", "appended onto the legacy tip");

    let _ = std::fs::remove_dir_all(&dir);
}
