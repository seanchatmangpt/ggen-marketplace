//! doc-hdit CLI: `scaffold`, `vectorize`, `audit` and `certify` subcommands.

use doc_hdit::info_theory::entropy::{mutual_information, shannon};
use doc_hdit::info_theory::{
    code_token_set, is_prose_artifact, phi_scoped, q_density_scoped, rank_phantoms,
    s_coverage_set_report, ClaimStatus, CodeBasis,
};
use doc_hdit::vsa::encode::{encode_code, encode_doc};
use doc_hdit::{public_modules, Claim, CodeModule};
use std::collections::BTreeMap;

#[derive(serde::Deserialize)]
struct Inputs {
    #[serde(default)]
    modules: Vec<CodeModule>,
    #[serde(default)]
    claims: Vec<Claim>,
    /// Module prefixes of documented external dependencies (P2 allowlist).
    #[serde(default)]
    known_external: Vec<String>,
    /// Repo directory paths from the extractor's code surface; a
    /// trailing-slash doc reference (`receipts/engine_ops/`) grounds by exact
    /// membership here — directory existence, never fuzzy.
    #[serde(default)]
    directories: Vec<String>,
    /// Repo file paths from the extractor's code surface; a `path_ref` claim
    /// (`planning/foo.hddl`, P1 [47]) grounds by exact membership here —
    /// file existence, never fuzzy.
    #[serde(default)]
    paths: Vec<String>,
}

/// Gate thresholds parsed from a court file
/// (lines of `key = value` or `key: value`; missing keys fall back to defaults).
struct Thresholds {
    s_coverage_min: f64,
    phi_max: f64,
    q_density_min: f64,
}

impl Default for Thresholds {
    fn default() -> Self {
        Thresholds {
            s_coverage_min: 0.30,
            phi_max: 0.20,
            q_density_min: 0.10,
        }
    }
}

fn parse_court(text: &str) -> Thresholds {
    let mut t = Thresholds::default();
    for line in text.lines() {
        let line = line.split('#').next().unwrap_or("").trim();
        let sep = if let Some(i) = line.find('=') {
            i
        } else if let Some(i) = line.find(':') {
            i
        } else {
            continue;
        };
        let key = line[..sep].trim().to_lowercase();
        let val: f64 = match line[sep + 1..].trim().parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        // Match by suffix so both canonical and court-file spellings
        // (S_coverage_min, Phi_halluc_max, Q_density_min) parse.
        if key.ends_with("s_coverage_min") || key == "coverage" {
            t.s_coverage_min = val;
        } else if (key.contains("phi") && key.ends_with("_max")) || key == "phantom" {
            t.phi_max = val;
        } else if key.ends_with("q_density_min") || key == "density" {
            t.q_density_min = val;
        }
    }
    t
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!(
            "usage: doc-hdit <vectorize|audit|certify> -- <inputs.json> [court-file]\n       doc-hdit scaffold --code <json> --templates <dir> --out <docsdir>\n       doc-hdit certify <inputs.json> [court-file] [--docs <dir>] [--chain <receipts.jsonl>]"
        );
        std::process::exit(2);
    }
    let cmd = args[1].as_str();
    if cmd == "scaffold" {
        let mut code = None;
        let mut templates = None;
        let mut out = None;
        let mut i = 2;
        while i < args.len() {
            match args[i].as_str() {
                "--code" => code = args.get(i + 1).cloned(),
                "--templates" => templates = args.get(i + 1).cloned(),
                "--out" => out = args.get(i + 1).cloned(),
                _ => {}
            }
            i += 2;
        }
        let (code, templates, out) = match (code, templates, out) {
            (Some(c), Some(t), Some(o)) => (c, t, o),
            _ => {
                eprintln!("usage: doc-hdit scaffold --code <json> --templates <dir> --out <docsdir>");
                std::process::exit(2);
            }
        };
        match doc_hdit::scaffold::scaffold_cli(&code, &templates, &out) {
            Ok(written) => {
                for w in &written {
                    println!("scaffolded {}", w.display());
                }
                println!(
                    "OK: scaffold rendered {} files into {}",
                    written.len(),
                    out
                );
            }
            Err(e) => {
                eprintln!("error: {}", e);
                std::process::exit(2);
            }
        }
        return;
    }
    let input_path = args.get(2).map(String::as_str).unwrap_or("");
    let raw = match std::fs::read_to_string(input_path) {
        Ok(r) => r,
        Err(e) => {
            eprintln!("error: cannot read {}: {}", input_path, e);
            std::process::exit(2);
        }
    };
    let inputs: Inputs = match serde_json::from_str(&raw) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("error: invalid JSON in {}: {}", input_path, e);
            std::process::exit(2);
        }
    };

    // P2 scope: S_coverage evaluates against the PUBLIC code surface only
    // (exported/pub/@doc'd items); the raw full-surface value is kept as
    // S_coverage_raw (report-only).
    let public = public_modules(&inputs.modules);
    let (_h_code_pub, codewords_pub) = encode_code(&public);
    let code_basis = CodeBasis::build(&codewords_pub);
    let (_h_code_raw, codewords_raw) = encode_code(&inputs.modules);
    let code_basis_raw = CodeBasis::build(&codewords_raw);
    // Content-hash vectorize cache (off by default): key = BLAKE3 of the
    // claims array; a hit replays the stored H_doc instead of re-encoding.
    let cache_flag = args
        .iter()
        .position(|a| a == "--cache")
        .and_then(|i| args.get(i + 1).map(String::as_str));
    let cache_dir = doc_hdit::vsa::cache::resolve_cache_dir(cache_flag);
    let h_doc = match &cache_dir {
        Some(dir) => {
            let key = doc_hdit::vsa::cache::claims_corpus_key(&inputs.claims);
            match doc_hdit::vsa::cache::load_h_doc(dir, &key) {
                Some(v) => {
                    eprintln!("cache: hit {}", &key[..16.min(key.len())]);
                    v
                }
                None => {
                    eprintln!("cache: miss {}", &key[..16.min(key.len())]);
                    let v = encode_doc(&inputs.claims);
                    if let Err(e) = doc_hdit::vsa::cache::store_h_doc(dir, &key, &v) {
                        eprintln!("cache: store failed: {}", e);
                    }
                    v
                }
            }
        }
        None => encode_doc(&inputs.claims),
    };
    // Deterministic exact-match phantom gate (primary); the VSA projection
    // residual stays as a secondary similarity signal (phi_vsa, report-only).
    // Directory refs ground by exact membership against the extractor's
    // `directories` array (both slash forms; symbol_variants strips the
    // trailing slash on the claim side).
    let mut tokens = code_token_set(&inputs.modules);
    for d in &inputs.directories {
        if d.is_empty() {
            continue;
        }
        tokens.insert(d.clone());
        tokens.insert(format!("{}/", d));
    }
    // P1 [47] path_ref grounding: file-path claims ground by exact membership
    // against the extractor's `paths` array — file existence, never fuzzy.
    for p in &inputs.paths {
        if !p.is_empty() {
            tokens.insert(p.clone());
        }
    }
    let external = &inputs.known_external;
    // P3: the GATED S_coverage is set coverage per the court's stated
    // definition; the VSA projection cosine stays as a report-only
    // semantic-similarity signal (s_coverage_vsa).
    let cov = s_coverage_set_report(&inputs.modules, &inputs.claims);
    let sc = cov.coverage;
    // Downstream per-claim vectorization (3 passes over every claim against
    // the code basis): cached by content hash of the full input surface, so
    // an unchanged corpus replays the stored vectors instead of re-encoding.
    let (sc_vsa, sc_raw, phi_vsa, ranked) = match &cache_dir
        .as_ref()
        .and_then(|dir| {
            let key = doc_hdit::vsa::cache::derived_key(
                &inputs.claims,
                &inputs.modules,
                external,
                &inputs.directories,
            );
            doc_hdit::vsa::cache::load_derived(dir, &key).map(|d| (dir.clone(), key, d))
        }) {
        Some((_, key, d)) => {
            eprintln!("cache: derived hit {}", &key[..16.min(key.len())]);
            (
                doc_hdit::vsa::cosine(&h_doc, &d.p_code_pub),
                doc_hdit::vsa::cosine(&h_doc, &d.p_code_raw),
                doc_hdit::info_theory::projection_residual_vectors(&h_doc, &d.p_code_raw),
                d.ranked.clone(),
            )
        }
        None => {
            // Single pass per code basis: the bundled projections feed both
            // the report values and the cache store.
            let p_code_pub =
                doc_hdit::info_theory::bundle_projections(&inputs.claims, &code_basis);
            let p_code_raw =
                doc_hdit::info_theory::bundle_projections(&inputs.claims, &code_basis_raw);
            let sc_vsa = doc_hdit::vsa::cosine(&h_doc, &p_code_pub);
            let sc_raw = doc_hdit::vsa::cosine(&h_doc, &p_code_raw);
            let phi_vsa = doc_hdit::info_theory::projection_residual_vectors(&h_doc, &p_code_raw);
            let ranked = rank_phantoms(&inputs.claims, &tokens, &code_basis);
            if let Some(dir) = &cache_dir {
                let key = doc_hdit::vsa::cache::derived_key(
                    &inputs.claims,
                    &inputs.modules,
                    external,
                    &inputs.directories,
                );
                let d = doc_hdit::vsa::cache::DerivedVectors {
                    p_code_pub,
                    p_code_raw,
                    ranked: ranked.clone(),
                };
                if let Err(e) = doc_hdit::vsa::cache::store_derived(dir, &key, &d) {
                    eprintln!("cache: store failed: {}", e);
                } else {
                    eprintln!("cache: derived stored {}", &key[..16.min(key.len())]);
                }
            }
            (sc_vsa, sc_raw, phi_vsa, ranked)
        }
    };
    // Deterministic exact-match phantom gate (primary); the VSA projection
    // residual stays as a secondary similarity signal (phi_vsa, report-only).
    // Directory refs ground by exact membership against the extractor's
    // `directories` array (both slash forms; symbol_variants strips the
    // trailing slash on the claim side).
    let phi = phi_scoped(&inputs.claims, &tokens, external);
    let external_documented = inputs
        .claims
        .iter()
        .filter(|c| ClaimStatus::ExternalDocumented == doc_hdit::info_theory::claim_status(c, &tokens, external))
        .count();
    let prose_artifacts = inputs
        .claims
        .iter()
        .filter(|c| is_prose_artifact(&c.object))
        .count();
    let h_bits = shannon(
        &inputs
            .claims
            .iter()
            .flat_map(|c| [c.subject.as_str(), c.predicate.as_str(), c.object.as_str()])
            .collect::<Vec<_>>(),
    );
    let mi = mutual_information(&inputs.claims, &inputs.modules);
    let q = q_density_scoped(&inputs.claims, &tokens, external);

    match cmd {
        "certify" => {
            let court_path = args.get(3).cloned().unwrap_or_default();
            let text = std::fs::read_to_string(&court_path).unwrap_or_default();
            let t = parse_court(&text);
            let gates = [
                ("S_coverage", sc, t.s_coverage_min, sc >= t.s_coverage_min),
                ("Phi_halluc", phi, t.phi_max, phi <= t.phi_max),
                ("Q_density", q, t.q_density_min, q >= t.q_density_min),
            ];
            let failures: Vec<&(&str, f64, f64, bool)> =
                gates.iter().filter(|g| !g.3).collect();
            if !failures.is_empty() {
                for (name, value, threshold, _) in failures {
                    eprintln!(
                        "REFUSED:DOC_HDIT_CERTIFY_GATE_FAIL:{} value={:.4} threshold={:.4}",
                        name, value, threshold
                    );
                }
                eprintln!("REFUSED:DOC_HDIT_CERTIFY:gate failure — no receipt minted");
                std::process::exit(1);
            }
            // Flag parsing after the gate pass (cheap refusal first).
            let mut docs_dir: Option<std::path::PathBuf> = None;
            let mut chain_path: Option<std::path::PathBuf> = None;
            let mut j = 2;
            while j < args.len() {
                match args[j].as_str() {
                    "--docs" => docs_dir = args.get(j + 1).map(std::path::PathBuf::from),
                    "--chain" => chain_path = args.get(j + 1).map(std::path::PathBuf::from),
                    _ => {}
                }
                j += 1;
            }
            let inputs_bytes = std::fs::read(input_path).unwrap_or_default();
            let subject = match doc_hdit::certify::subject_digest(&inputs_bytes, docs_dir.as_deref())
            {
                Ok(s) => s,
                Err(e) => {
                    eprintln!("REFUSED:DOC_HDIT_CERTIFY:subject digest failed: {}", e);
                    std::process::exit(1);
                }
            };
            let chain = chain_path.unwrap_or_else(|| {
                docs_dir
                    .clone()
                    .map(|d| d.join("doc-hdit.receipts.jsonl"))
                    .unwrap_or_else(|| std::path::PathBuf::from("doc-hdit.receipts.jsonl"))
            });
            let parent = doc_hdit::certify::last_chain_hash(&chain).unwrap_or_default();
            let ts = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0);
            let outcome = doc_hdit::certify::GateOutcome {
                s_coverage: sc,
                phi_halluc: phi,
                q_density: q,
            };
            let thresholds = doc_hdit::certify::Thresholds {
                s_coverage_min: t.s_coverage_min,
                phi_max: t.phi_max,
                q_density_min: t.q_density_min,
            };
            let receipt = doc_hdit::certify::mint_receipt(
                &subject,
                &parent,
                &outcome,
                &thresholds,
                ts,
            );
            if let Err(e) = doc_hdit::certify::append_receipt(&chain, &receipt) {
                eprintln!("REFUSED:DOC_HDIT_CERTIFY:cannot append to {}: {}", chain.display(), e);
                std::process::exit(1);
            }
            println!(
                "{}",
                serde_json::to_string(&receipt).expect("serialize receipt")
            );
            println!("OK: certified — receipt appended to {}", chain.display());
        }
        "vectorize" => {
            let mut out: BTreeMap<&str, serde_json::Value> = BTreeMap::new();
            out.insert("s_coverage", serde_json::json!(sc));
            out.insert("s_coverage_raw", serde_json::json!(sc_raw));
            out.insert("s_coverage_vsa", serde_json::json!(sc_vsa));
            out.insert(
                "s_coverage_report",
                serde_json::json!({
                    "covered": cov.covered,
                    "total": cov.total,
                    "uncovered_modules_top10": cov
                        .uncovered_modules
                        .iter()
                        .take(10)
                        .map(|(name, miss)| serde_json::json!({"module": name, "uncovered_items": miss}))
                        .collect::<Vec<_>>()
                }),
            );
            out.insert("prose_artifacts", serde_json::json!(prose_artifacts));
            out.insert("phi", serde_json::json!(phi));
            out.insert("external_documented", serde_json::json!(external_documented));
            out.insert("phi_vsa", serde_json::json!(phi_vsa));
            out.insert("entropy_bits", serde_json::json!(h_bits));
            out.insert("mutual_information_bits", serde_json::json!(mi));
            out.insert("q_density", serde_json::json!(q));
            out.insert(
                "phantom_ranking",
                serde_json::json!(
                    ranked
                        .iter()
                        .map(|(i, a, g)| {
                            serde_json::json!({
                                "claim_index": i, "alignment": a, "grounded": g
                            })
                        })
                        .collect::<Vec<_>>()
                ),
            );
            println!(
                "{}",
                serde_json::to_string_pretty(&out).expect("serialize metrics")
            );
        }
        "audit" => {
            let court_path = args.get(3).cloned().unwrap_or_default();
            let text = std::fs::read_to_string(&court_path).unwrap_or_default();
            let t = parse_court(&text);
            let mut violations = 0;
            // P2 landed: S_coverage gates over the public/documented surface;
            // the raw full-surface value stays report-only.
            println!("REPORT  coverage_raw value={:.4}", sc_raw);
            println!(
                "REPORT  coverage_vsa value={:.4} (VSA projection cosine, report-only)",
                sc_vsa
            );
            println!(
                "REPORT  prose_artifacts count={} (path/version/prose objects; excluded from Phi and Q)",
                prose_artifacts
            );
            println!(
                "REPORT  external_documented count={} (documented-dep references, excluded from Phi)",
                external_documented
            );
            let gates: [(&str, f64, f64, bool); 3] = [
                ("coverage", sc, t.s_coverage_min, sc >= t.s_coverage_min),
                ("phantom", phi, t.phi_max, phi <= t.phi_max),
                ("density", q, t.q_density_min, q >= t.q_density_min),
            ];
            for (gate, value, threshold, pass) in gates {
                if pass {
                    println!("PASS  {} value={:.4} threshold={:.4}", gate, value, threshold);
                } else {
                    violations += 1;
                    println!(
                        "FAIL  {} value={:.4} threshold={:.4} offending_claims={:?}",
                        gate,
                        value,
                        threshold,
                        ranked
                            .iter()
                            .filter(|(_, _, grounded)| !*grounded)
                            .take(3)
                            .map(|(i, _, _)| *i)
                            .collect::<Vec<_>>()
                    );
                }
            }
            if violations > 0 {
                std::process::exit(1);
            }
        }
        _ => {
            eprintln!("unknown subcommand: {}", cmd);
            std::process::exit(2);
        }
    }
}
