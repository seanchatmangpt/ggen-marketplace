//! doc-hdit CLI: `vectorize` and `audit` subcommands.

use doc_hdit::info_theory::entropy::{mutual_information, q_density, shannon};
use doc_hdit::info_theory::{projection_residual, rank_phantoms, s_coverage, CodeBasis};
use doc_hdit::vsa::encode::{encode_code, encode_doc};
use doc_hdit::{Claim, CodeModule};
use std::collections::BTreeMap;

#[derive(serde::Deserialize)]
struct Inputs {
    #[serde(default)]
    modules: Vec<CodeModule>,
    #[serde(default)]
    claims: Vec<Claim>,
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
        eprintln!("usage: doc-hdit <vectorize|audit> <inputs.json> [court-file]");
        std::process::exit(2);
    }
    let cmd = args[1].as_str();
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

    let (_h_code, codewords) = encode_code(&inputs.modules);
    let h_doc = encode_doc(&inputs.claims);
    let code_basis = CodeBasis::build(&codewords);
    let sc = s_coverage(&h_doc, &inputs.claims, &code_basis);
    let phi = projection_residual(&h_doc, &inputs.claims, &code_basis);
    let ranked = rank_phantoms(&inputs.claims, &code_basis);
    let h_bits = shannon(
        &inputs
            .claims
            .iter()
            .flat_map(|c| [c.subject.as_str(), c.predicate.as_str(), c.object.as_str()])
            .collect::<Vec<_>>(),
    );
    let mi = mutual_information(&inputs.claims, &inputs.modules);
    let q = q_density(&inputs.claims, &inputs.modules);

    match cmd {
        "vectorize" => {
            let mut out: BTreeMap<&str, serde_json::Value> = BTreeMap::new();
            out.insert("s_coverage", serde_json::json!(sc));
            out.insert("phi", serde_json::json!(phi));
            out.insert("entropy_bits", serde_json::json!(h_bits));
            out.insert("mutual_information_bits", serde_json::json!(mi));
            out.insert("q_density", serde_json::json!(q));
            out.insert(
                "phantom_ranking",
                serde_json::json!(
                    ranked
                        .iter()
                        .map(|(i, a)| serde_json::json!({ "claim_index": i, "alignment": a }))
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
                            .take(3)
                            .map(|(i, _)| *i)
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
