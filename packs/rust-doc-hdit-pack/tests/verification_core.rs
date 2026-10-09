//! Chicago-style integration tests: real math, no mocks.

use doc_hdit::info_theory::entropy::{claim_grounded, mutual_information, q_density, shannon};
use doc_hdit::info_theory::{
    code_token_set, phi_exact, projection_residual, rank_phantoms, s_coverage, CodeBasis,
};
use doc_hdit::vsa::{basis, bind, bundle, cosine, permute, Hv};
use doc_hdit::{Claim, CodeModule};

fn claim(id: &str, s: &str, p: &str, o: &str) -> Claim {
    Claim {
        id: id.into(),
        subject: s.into(),
        predicate: p.into(),
        object: o.into(),
    }
}

#[test]
fn orthogonality_of_1000_random_basis_pairs() {
    let idents: Vec<String> = (0..2000).map(|i| format!("ortho-{}", i)).collect();
    let mut v1: Option<Hv> = None;
    let mut checked = 0;
    for (i, id) in idents.iter().enumerate() {
        let v = basis(id);
        if let Some(prev) = &v1 {
            let c = cosine(&prev, &v);
            assert!(
                c.abs() < 0.1,
                "pair {} cos={} outside orthogonality bound",
                checked,
                c
            );
            checked += 1;
            v1 = None;
        } else {
            v1 = Some(v);
            let _ = i;
        }
    }
    assert_eq!(checked, 1000);
}

#[test]
fn bind_distributes_over_bundle_tie_free() {
    let a = basis("dist-a");
    let b = basis("dist-b");
    // tie-free bundle input: b bundled with itself (sum = 2b, no zeros)
    let bc = bundle(&[b.clone(), b.clone()]);
    let lhs = bind(&a, &bc);
    let rhs = bundle(&[bind(&a, &b), bind(&a, &b)]);
    assert_eq!(lhs, rhs);
}

#[test]
fn permute_preserves_norm() {
    let v = basis("perm");
    for k in [0usize, 1, 7, 9999, 10_000, 12_345] {
        let p = permute(&v, k);
        let nv: i64 = v.iter().map(|x| x * x).sum();
        let np: i64 = p.iter().map(|x| x * x).sum();
        assert_eq!(nv, np);
        assert_eq!(nv, 10_000);
    }
}

/// Shared fixture: small code surface.
fn fixture_modules() -> Vec<CodeModule> {
    vec![CodeModule {
        name: "engine".to_string(),
        is_public: true,
        items: vec![
            doc_hdit::CodeItem {
                kind: "fn".into(),
                ident: "ignite".into(),
                signature: "ignite(fuel: Fuel) -> Spark".into(),
                is_public: true,
            },
            doc_hdit::CodeItem {
                kind: "struct".into(),
                ident: "Piston".into(),
                signature: "Piston { bore: u32 }".into(),
                is_public: true,
            },
            doc_hdit::CodeItem {
                kind: "fn".into(),
                ident: "exhaust".into(),
                signature: "exhaust(gas: Gas)".into(),
                is_public: true,
            },
            doc_hdit::CodeItem {
                kind: "trait".into(),
                ident: "Valved".into(),
                signature: "Valved: Send".into(),
                is_public: true,
            },
        ],
    }]
}

fn grounded_claims() -> Vec<Claim> {
    vec![
        claim("c0", "fn", "ignite", "ignite(fuel: Fuel) -> Spark"),
        claim("c1", "struct", "Piston", "Piston { bore: u32 }"),
        claim("c2", "fn", "exhaust", "exhaust(gas: Gas)"),
        claim("c3", "trait", "Valved", "Valved: Send"),
    ]
}

#[test]
fn planted_phantom_yields_positive_phi_and_top1_ranking() {
    let modules = fixture_modules();
    let mut claims = grounded_claims();
    // phantom: symbol absent from the code surface
    claims.push(claim("c4", "fn", "teleport", "teleport(warp: Warp)"));

    let tokens = code_token_set(&modules);
    let phi = phi_exact(&claims, &tokens);
    assert!(
        (phi - 0.2).abs() < 1e-12,
        "expected Phi = 1/5 = 0.2 for planted phantom, got {}",
        phi
    );

    let (_, codewords) = doc_hdit::vsa::encode::encode_code(&modules);
    let code_basis = CodeBasis::build(&codewords);
    let ranked = rank_phantoms(&claims, &tokens, &code_basis);
    assert_eq!(
        ranked[0].0, 4,
        "phantom claim index 4 must rank top-1; got {:?}",
        ranked
    );
    assert!(!ranked[0].2, "top-ranked claim must be ungrounded");
    assert!(ranked.last().map(|r| r.2).unwrap_or(false));

    // and the grounded baseline is exactly zero
    assert_eq!(phi_exact(&grounded_claims(), &tokens), 0.0);
}

#[test]
fn grounded_doc_yields_exact_zero_phi_and_q_density_one() {
    let modules = fixture_modules();
    let claims = grounded_claims();
    let tokens = code_token_set(&modules);
    let phi = phi_exact(&claims, &tokens);
    assert_eq!(phi, 0.0, "grounded doc must have Phi exactly 0");
    let q = q_density(&claims, &modules);
    assert!(
        (q - 1.0).abs() < 1e-12,
        "Q_density fully grounded = 1.0, got {}",
        q
    );
}

#[test]
fn phi_is_normalized_between_zero_and_one() {
    let modules = fixture_modules();
    let tokens = code_token_set(&modules);
    let mut claims = grounded_claims();
    for i in 0..10 {
        claims.push(claim(
            &format!("fake{}", i),
            "fn",
            "mentions",
            "no_such_symbol_x",
        ));
    }
    let phi = phi_exact(&claims, &tokens);
    assert!((0.0..=1.0).contains(&phi), "Phi out of [0,1]: {}", phi);
}

#[test]
fn claim_grounded_matches_object_not_subject() {
    let modules = fixture_modules();
    let tokens = code_token_set(&modules);
    // subject is a doc path; object is the symbol — must ground on object alone
    let c = claim("g0", "docs/engine.md#Usage", "mentions", "ignite");
    assert!(
        claim_grounded(&c, &tokens),
        "grounding must match the object symbol, not the doc-path subject"
    );
    let fake = claim(
        "g1",
        "docs/engine.md#Usage",
        "mentions",
        "zzz_totally_fake_symbol_zzz",
    );
    assert!(!claim_grounded(&fake, &tokens));
}

#[test]
fn qualified_and_aried_object_forms_ground() {
    let modules = fixture_modules();
    let tokens = code_token_set(&modules);
    for obj in [
        "ignite/1",        // arity form (Elixir)
        "Engine.ignite",   // qualified module form
        "Engine.ignite/1", // qualified + arity
        "engine::ignite",  // Rust path form
        "ignite()",        // call form
    ] {
        let c = claim("q", "docs/x.md#S", "mentions", obj);
        assert!(claim_grounded(&c, &tokens), "form '{}' must ground", obj);
    }
}

#[test]
fn coverage_similarity_separates_grounded_from_phantom() {
    let modules = fixture_modules();
    let (_, codewords) = doc_hdit::vsa::encode::encode_code(&modules);
    let code_basis = CodeBasis::build(&codewords);
    let g = grounded_claims();
    let s_grounded = s_coverage(&doc_hdit::vsa::encode::encode_doc(&g), &g, &code_basis);
    let mut phantom = grounded_claims();
    phantom.push(claim("c4", "fn", "teleport", "teleport(warp: Warp)"));
    let s_phantom = s_coverage(
        &doc_hdit::vsa::encode::encode_doc(&phantom),
        &phantom,
        &code_basis,
    );
    assert!(s_grounded > s_phantom, "{} vs {}", s_grounded, s_phantom);
}

#[test]
fn entropy_of_uniform_distribution_is_log2_n() {
    let tokens: Vec<&str> = (0..8).map(|i| match i {
        0 => "a", 1 => "b", 2 => "c", 3 => "d", 4 => "e", 5 => "f", 6 => "g", _ => "h",
    }).collect();
    let h = shannon(&tokens);
    assert!((h - 3.0).abs() < 1e-12);
}

#[test]
fn mutual_information_drops_for_ungrounded_claims() {
    let modules = fixture_modules();
    let grounded = grounded_claims();
    let mut phantom = grounded_claims();
    phantom.push(claim("c4", "fn", "teleport", "teleport(warp: Warp)"));

    let mi_grounded = mutual_information(&grounded, &modules);
    let mi_phantom = mutual_information(&phantom, &modules);
    // grounded: H(D)=log2(4)=2, H(D|C)=0 => I=2; phantom adds 1 bit surprisal / 5
    assert!((mi_grounded - 2.0).abs() < 1e-12);
    assert!((mi_phantom - (5f64.log2() - 0.2)).abs() < 1e-12);

    // density drops when the doc claims ungrounded symbols
    // (Q_density = grounded-claim fraction: fully grounded doc = 1.0)
    let q_grounded = q_density(&grounded, &modules);
    let q_phantom = q_density(&phantom, &modules);
    assert!((q_grounded - 1.0).abs() < 1e-12);
    assert!((q_phantom - 0.8).abs() < 1e-12); // 4 of 5 claims grounded
}

/// Real-corpus control (DOC-HDIT-PILOT replay): the planted-fake control
/// INSIDE the real ex4pm corpus. Requires /tmp/hdit/ex4pm.inputs.json from
/// the pilot replay; prints a SKIP note when the artifact is absent.
#[test]
fn real_corpus_fake_symbol_control() {
    let path = std::path::Path::new("/tmp/hdit/ex4pm.inputs.json");
    if !path.exists() {
        eprintln!("SKIP: /tmp/hdit/ex4pm.inputs.json absent (pilot replay not run)");
        return;
    }
    let raw = std::fs::read_to_string(path).expect("read ex4pm inputs");
    #[derive(serde::Deserialize)]
    struct Inputs {
        #[serde(default)]
        modules: Vec<CodeModule>,
        #[serde(default)]
        claims: Vec<Claim>,
    }
    let inputs: Inputs = serde_json::from_str(&raw).expect("parse ex4pm inputs");
    let n = inputs.claims.len();
    assert!(n > 100, "corpus too small: {}", n);
    let tokens = code_token_set(&inputs.modules);
    let baseline_phi = phi_exact(&inputs.claims, &tokens);

    // Inject the fake-symbol claim: Phi must move by exactly 1/(n+1) and the
    // fake must rank top-1 among ungrounded claims by the VSA near-miss signal.
    let mut injected = inputs.claims.clone();
    injected.push(claim(
        "zzz-control",
        "docs/x.md#Control",
        "mentions",
        "zzz_totally_fake_symbol_zzz",
    ));
    let phi_injected = phi_exact(&injected, &tokens);
    let expected = (baseline_phi * n as f64 + 1.0) / (n as f64 + 1.0);
    assert!(
        (phi_injected - expected).abs() < 1e-9,
        "Phi must move exactly one ungrounded claim under injection: {} -> {} (expected {})",
        baseline_phi,
        phi_injected,
        expected
    );

    // Separation is by the deterministic exact-match gate (set-based
    // formulation, DOC-HDIT-PILOT P0-2): the fake MUST land in the ungrounded
    // class, which is exactly what moves Phi by one claim. The VSA alignment
    // is a secondary near-miss ordering INSIDE the ungrounded class and
    // carries no grounded/ungrounded separation (pilot measurement) — it is
    // reported with the ranking, never gated on.
    let (_, codewords) = doc_hdit::vsa::encode::encode_code(&inputs.modules);
    let code_basis = CodeBasis::build(&codewords);
    let ranked = rank_phantoms(&injected, &tokens, &code_basis);
    let fake_entry = ranked.iter().find(|(i, _, _)| *i == n).expect("fake present");
    assert!(
        !fake_entry.2,
        "injected fake must be classified ungrounded by the exact-match gate"
    );
    let fake_align = fake_entry.1;
    let fake_rank = ranked
        .iter()
        .position(|(i, _, _)| *i == n)
        .expect("fake present")
        + 1;
    let ungrounded_count = ranked.iter().filter(|(_, _, g)| !*g).count();
    assert_eq!(
        ungrounded_count,
        (baseline_phi * n as f64).round() as usize + 1,
        "ungrounded class must be exactly the baseline misses plus the fake"
    );
    eprintln!(
        "control: n={} baseline_phi={:.4} phi_injected={:.4} ungrounded={} fake_rank={}/{} fake_align={:.4}",
        n + 1,
        baseline_phi,
        phi_injected,
        ungrounded_count,
        fake_rank,
        n + 1,
        fake_align
    );
}

// ------------------------------------------------- P2 scope + allowlist ---

#[test]
fn p2_public_scope_excludes_internal_items_from_public_surface() {
    let modules = vec![CodeModule {
        name: "engine".to_string(),
        is_public: true,
        items: vec![
            doc_hdit::CodeItem {
                kind: "fn".into(),
                ident: "ignite".into(),
                signature: "ignite(fuel: Fuel) -> Spark".into(),
                is_public: true,
            },
            doc_hdit::CodeItem {
                kind: "fn".into(),
                ident: "internal_helper".into(),
                signature: "internal_helper()".into(),
                is_public: false,
            },
        ],
    }];
    let public = doc_hdit::public_modules(&modules);
    assert_eq!(public.len(), 1);
    assert_eq!(public[0].items.len(), 1, "only the public item survives");
    assert_eq!(public[0].items[0].ident, "ignite");

    let public_tokens = code_token_set(&public);
    let internal_claim = claim(
        "int0",
        "docs/x.md#Internals",
        "mentions",
        "internal_helper",
    );
    assert!(
        !claim_grounded(&internal_claim, &public_tokens),
        "internal-only symbol must not ground against the public surface"
    );
    assert!(claim_grounded(&internal_claim, &code_token_set(&modules)));
}

#[test]
fn p2_external_documented_claims_are_classified_not_phantom() {
    let modules = fixture_modules();
    let tokens = code_token_set(&modules);
    let external = vec!["Ash.".to_string(), "Ecto.".to_string()];
    let ext = claim("e0", "docs/x.md#Deps", "mentions", "Ash.Reactor");
    let local = claim("g0", "docs/x.md#Deps", "mentions", "ignite");
    let phantom = claim("p0", "docs/x.md#Deps", "mentions", "zzz_fake_symbol_zzz");
    assert_eq!(
        doc_hdit::info_theory::claim_status(&ext, &tokens, &external),
        doc_hdit::info_theory::ClaimStatus::ExternalDocumented
    );
    assert_eq!(
        doc_hdit::info_theory::claim_status(&local, &tokens, &external),
        doc_hdit::info_theory::ClaimStatus::Grounded
    );
    assert_eq!(
        doc_hdit::info_theory::claim_status(&phantom, &tokens, &external),
        doc_hdit::info_theory::ClaimStatus::Phantom
    );

    let claims = vec![local, ext, phantom];
    // Phi: phantom only -> 1/3; Q: grounded + external -> 2/3
    assert!((doc_hdit::info_theory::phi_scoped(&claims, &tokens, &external) - 1.0 / 3.0).abs() < 1e-12);
    assert!(
        (doc_hdit::info_theory::q_density_scoped(&claims, &tokens, &external) - 2.0 / 3.0).abs() < 1e-12
    );
}

#[test]
fn p2_pre_p2_inputs_without_flags_load_full_surface() {
    // Pre-P2 code-surface JSON carries no is_public/known_external fields;
    // serde defaults must reconstruct the full public surface, not an empty one.
    let raw = r#"{"modules":[{"name":"engine","items":[{"kind":"fn","ident":"ignite","signature":"ignite()"}]}]}"#;
    let inputs: std::collections::BTreeMap<String, serde_json::Value> =
        serde_json::from_str(raw).expect("parse legacy inputs");
    let mods: Vec<CodeModule> =
        serde_json::from_value(inputs["modules"].clone()).expect("decode legacy modules");
    assert!(mods[0].is_public, "legacy module defaults to public");
    assert!(mods[0].items[0].is_public, "legacy item defaults to public");
    let public = doc_hdit::public_modules(&mods);
    assert_eq!(public.len(), 1);
    assert_eq!(public[0].items.len(), 1);
}

// ---------------------------------------------------- P3: set coverage ----

use doc_hdit::info_theory::{
    claim_token_set, is_prose_artifact, phi_scoped, q_density_scoped, s_coverage_set,
    s_coverage_set_report, ClaimStatus,
};

fn item(kind: &str, ident: &str, is_public: bool) -> doc_hdit::CodeItem {
    doc_hdit::CodeItem {
        kind: kind.into(),
        ident: ident.into(),
        signature: String::new(),
        is_public,
    }
}

#[test]
fn p3_set_coverage_exact_fractions() {
    let modules = fixture_modules(); // 4 public items in 1 module
    // No claims -> 0.0.
    assert_eq!(s_coverage_set(&modules, &[]), 0.0);
    // One claim covering `ignite` -> 1/4.
    let claims = vec![claim("c0", "doc", "mentions", "ignite")];
    assert!((s_coverage_set(&modules, &claims) - 0.25).abs() < 1e-12);
    // Two claims covering `ignite` + `Piston` -> 2/4 = 0.5.
    let claims = vec![
        claim("c0", "doc", "mentions", "ignite"),
        claim("c1", "doc", "mentions", "Piston"),
    ];
    assert!((s_coverage_set(&modules, &claims) - 0.5).abs() < 1e-12);
    // Duplicate claims must not inflate: same item twice is still 1/4.
    let claims = vec![
        claim("c0", "doc", "mentions", "ignite"),
        claim("c1", "doc", "mentions", "ignite/1"),
    ];
    assert!((s_coverage_set(&modules, &claims) - 0.25).abs() < 1e-12);
    // Qualified form covers too.
    let claims = vec![claim("c0", "doc", "mentions", "engine.ignite")];
    assert!((s_coverage_set(&modules, &claims) - 0.25).abs() < 1e-12);
}

#[test]
fn p3_prose_artifacts_classified_and_excluded() {
    // The two witnessed examples from the P2 receipt.
    assert!(is_prose_artifact("release/v26.8.23"));
    assert!(is_prose_artifact("stream/metrics.ex"));
    assert!(is_prose_artifact("1.2.3"));
    assert!(is_prose_artifact("v26.8.23"));
    assert!(is_prose_artifact("--mem-gb"));
    assert!(is_prose_artifact("stage/{id}.jsonl"));
    // Real symbols stay symbols.
    assert!(!is_prose_artifact("verify/0"));
    assert!(!is_prose_artifact("Ex4pm.OCEL.normalize/1"));
    assert!(!is_prose_artifact("s_coverage_set"));
    // Status classification.
    let modules = fixture_modules();
    let tokens = code_token_set(&modules);
    let claims = vec![
        claim("c0", "doc", "mentions", "release/v26.8.23"),
        claim("c1", "doc", "mentions", "stream/metrics.ex"),
        claim("c2", "doc", "mentions", "ignite"),
        claim("c3", "doc", "mentions", "zzz_absent_symbol_zzz"),
    ];
    assert_eq!(
        doc_hdit::info_theory::claim_status(&claims[0], &tokens, &[]),
        ClaimStatus::ProseArtifact
    );
    assert_eq!(
        doc_hdit::info_theory::claim_status(&claims[1], &tokens, &[]),
        ClaimStatus::ProseArtifact
    );
    // Phi excludes prose artifacts from numerator AND denominator:
    // 1 phantom / 2 scored claims = 0.5.
    assert!((phi_scoped(&claims, &tokens, &[]) - 0.5).abs() < 1e-12);
    // Q_density: 1 grounded / 2 scored = 0.5.
    assert!((q_density_scoped(&claims, &tokens, &[]) - 0.5).abs() < 1e-12);
}

#[test]
fn p3_coverage_monotone_in_claims() {
    let modules = fixture_modules();
    let c0 = vec![claim("c0", "doc", "mentions", "ignite")];
    let base = s_coverage_set(&modules, &c0);
    // Adding a claim covering a NEW public item strictly increases coverage.
    let c1 = vec![
        claim("c0", "doc", "mentions", "ignite"),
        claim("c1", "doc", "mentions", "exhaust"),
    ];
    let more = s_coverage_set(&modules, &c1);
    assert!(more > base, "coverage must strictly increase: {} !> {}", more, base);
    // Adding a claim covering an ALREADY covered item leaves it unchanged.
    let c2 = vec![
        claim("c0", "doc", "mentions", "ignite"),
        claim("c1", "doc", "mentions", "ignite/1"),
    ];
    assert_eq!(s_coverage_set(&modules, &c2), base);
    // Phantom/prose claims never raise coverage.
    let cj = vec![
        claim("c0", "doc", "mentions", "ignite"),
        claim("c1", "doc", "mentions", "zzz_absent_symbol_zzz"),
        claim("c2", "doc", "mentions", "release/v26.8.23"),
    ];
    assert_eq!(s_coverage_set(&modules, &cj), base);
}

#[test]
fn p3_public_scope_and_remediation_list() {
    // Private items are not in the denominator.
    let modules = vec![CodeModule {
        name: "engine".into(),
        is_public: true,
        items: vec![
            item("fn", "pub_thing", true),
            item("fn", "secret_thing", false),
        ],
    }];
    let claims = vec![claim("c0", "doc", "mentions", "pub_thing")];
    assert!((s_coverage_set(&modules, &claims) - 1.0).abs() < 1e-12);
    // Uncovered public items surface as the remediation list.
    let rep = s_coverage_set_report(&fixture_modules(), &[]);
    assert_eq!(rep.total, 4);
    assert_eq!(rep.covered, 0);
    assert_eq!(rep.coverage, 0.0);
    assert_eq!(rep.uncovered_modules.len(), 1);
    assert_eq!(rep.uncovered_modules[0], ("engine".to_string(), 4));
    // A claim mentioning a prose artifact does not cover anything.
    let claimed = claim_token_set(&vec![claim("c", "d", "m", "release/v26.8.23")]);
    assert!(!claimed.contains("release"));
    assert!(claimed.contains("release/v26.8.23"));
}

#[test]
fn p3_denominator_reconciliation_raw_vs_set_emitted() {
    // Backlog [59]: the audit previously emitted only the post-collapse set
    // denominator, so the raw-vs-set discrepancy was invisible. Both
    // denominators plus the collapsed delta must now be present.
    let modules = vec![
        CodeModule {
            name: "engine".into(),
            is_public: true,
            items: vec![
                item("fn", "ignite", true),
                item("fn", "exhaust", true),
            ],
        },
        // A non-public module whose public items survive in the raw
        // denominator but are collapsed out of the set denominator.
        CodeModule {
            name: "engine_internal".into(),
            is_public: false,
            items: vec![item("fn", "hidden_thing", true)],
        },
    ];
    let rep = s_coverage_set_report(&modules, &[]);
    assert_eq!(rep.total, 2, "set denominator: public items in public modules");
    assert_eq!(rep.total_raw, 3, "raw denominator: public items across ALL modules");
    assert_eq!(rep.collapsed_delta, rep.total_raw - rep.total);
    assert_eq!(rep.collapsed_delta, 1);
}

// --------------------------------- claim-grounding granularity variants ---

#[test]
fn call_wrapped_forms_unwrap_to_the_referent() {
    // Witnessed xaas offender: plug(XaasWeb.Plugs.AuthenticateOrg) — the
    // wrapped module path is the code-surface identifier.
    let v = doc_hdit::info_theory::symbol_variants("plug(XaasWeb.Plugs.AuthenticateOrg)");
    assert!(v.iter().any(|s| s == "XaasWeb.Plugs.AuthenticateOrg"));
    assert!(v.iter().any(|s| s == "AuthenticateOrg"));
    assert!(v.iter().any(|s| s == "plug"));
    // Nested call: Code.ensure_loaded?(Xaas.Chicago)
    let v = doc_hdit::info_theory::symbol_variants("Code.ensure_loaded?(Xaas.Chicago)");
    assert!(v.iter().any(|s| s == "Xaas.Chicago"));
    assert!(v.iter().any(|s| s == "Chicago"));
    // Unclosed call: Map.update(
    let v = doc_hdit::info_theory::symbol_variants("Map.update(");
    assert!(v.iter().any(|s| s == "Map.update"));
    // Spec arrow form (witnessed offender class): change/2 -> changeset.
    let v = doc_hdit::info_theory::symbol_variants("change/2 -> changeset");
    assert!(v.iter().any(|s| s == "change/2"));
    assert!(v.iter().any(|s| s == "change"));
    // Grounding end-to-end: plug(...) grounds against the wrapped module.
    let modules = vec![doc_hdit::CodeModule {
        name: "XaasWeb.Plugs.AuthenticateOrg".into(),
        is_public: true,
        items: vec![item("function", "call", true)],
    }];
    let tokens = code_token_set(&modules);
    let claims = vec![claim(
        "c0",
        "doc",
        "mentions",
        "plug(XaasWeb.Plugs.AuthenticateOrg)",
    )];
    assert_eq!(phi_scoped(&claims, &tokens, &[]), 0.0);
}

#[test]
fn route_paths_ground_against_router_extracted_items() {
    // Witnessed xaas offenders: execution/runs, execution/hooks/:event —
    // exact path membership against router-extracted items (kind "route").
    let router = doc_hdit::CodeModule {
        name: "XaasWeb.Router".into(),
        is_public: true,
        items: vec![
            item("route", "execution/runs", true),
            item("route", "execution/hooks/:event", true),
        ],
    };
    let tokens = code_token_set(&[router.clone()]);
    assert!(tokens.contains("execution/runs"));
    assert!(tokens.contains("execution/hooks/:event"));
    let claims = vec![
        claim("c0", "doc", "mentions", "execution/runs"),
        claim("c1", "doc", "mentions", "execution/hooks/:event"),
    ];
    assert_eq!(phi_scoped(&claims, &tokens, &[]), 0.0);
    assert!(!is_prose_artifact("execution/runs"));
    assert!(!is_prose_artifact("execution/hooks/:event"));
    // A route that was never extracted stays a phantom.
    let claims = vec![claim("c2", "doc", "mentions", "execution/nope")];
    assert_eq!(phi_scoped(&claims, &tokens, &[]), 1.0);
}

#[test]
fn trailing_slash_directory_refs_ground_by_dir_membership() {
    // Witnessed xaas offender class: receipts/engine_ops/ — grounds iff the
    // directory exists in the extractor's `directories` array (exact
    // membership; the CLI extends the token set with the dir list).
    assert!(!is_prose_artifact("receipts/engine_ops/"));
    // symbol_variants yields the slash-stripped directory path.
    let v = doc_hdit::info_theory::symbol_variants("receipts/engine_ops/");
    assert!(v.iter().any(|s| s == "receipts/engine_ops"));
    let mut tokens = code_token_set(&[]);
    tokens.insert("receipts/engine_ops".to_string());
    tokens.insert("receipts/engine_ops/".to_string());
    let grounded = vec![claim("c0", "doc", "mentions", "receipts/engine_ops/")];
    assert_eq!(phi_scoped(&grounded, &tokens, &[]), 0.0);
    // A directory that does not exist stays a phantom.
    let claims = vec![claim("c1", "doc", "mentions", "fixture/burn_in/")];
    assert_eq!(phi_scoped(&claims, &tokens, &[]), 1.0);
}

#[test]
fn reexport_aliases_ground_against_submodule_definitions() {
    // Backlog [56]: `pub use castle::*` at the crate root re-exports items
    // defined in a submodule; the code-surface index must admit the
    // re-exported alias names so a doc naming `castle::fn_name` (or a braced
    // alias like `PresentationAuthority`) grounds against the fn defined in
    // the submodule. Exact strings only — the alias universe comes from `use`
    // items the extractor emits from `pub use` declarations.
    let castle_fn = doc_hdit::CodeItem {
        kind: "function".into(),
        ident: "execute_powl_with_gym_act".into(),
        signature: "execute_powl_with_gym_act(&PowlProcess) -> Result<ReceiptedOcelLog>".into(),
        is_public: true,
    };
    let glob = doc_hdit::CodeItem {
        kind: "use".into(),
        ident: "castle::*".into(),
        signature: "castle::*".into(),
        is_public: true,
    };
    let braces = doc_hdit::CodeItem {
        kind: "use".into(),
        ident: "dd_ui::{DdUiRefusal, PresentationAuthority}".into(),
        signature: "dd_ui::{DdUiRefusal, PresentationAuthority}".into(),
        is_public: true,
    };
    let modules = vec![
        doc_hdit::CodeModule {
            name: "src/castle.rs".into(),
            is_public: true,
            items: vec![castle_fn],
        },
        doc_hdit::CodeModule {
            name: "src/lib.rs".into(),
            is_public: true,
            items: vec![glob, braces],
        },
    ];
    let tokens = code_token_set(&modules);
    // Module-qualified doc reference to a submodule fn grounds.
    let qualified = claim(
        "c0",
        "docs/payments/PAYMENTS.md#Lifecycle",
        "mentions",
        "castle::execute_powl_with_gym_act",
    );
    assert!(
        claim_grounded(&qualified, &tokens),
        "castle::fn_name must ground against the submodule fn"
    );
    // Braced re-export alias names ground.
    let alias_claim = claim("c1", "docs/x.md", "mentions", "PresentationAuthority");
    assert!(
        claim_grounded(&alias_claim, &tokens),
        "braced re-export alias must ground"
    );
    // A never-declared alias stays a phantom (no over-acceptance).
    let phantom = claim("c2", "docs/x.md", "mentions", "NotAnAlias");
    assert!(
        !claim_grounded(&phantom, &tokens),
        "undeclared alias must stay a phantom"
    );
    // A glob re-export adds no phantom-bearing tokens of its own: the glob
    // tail `*` never becomes a groundable symbol.
    let glob_only = vec![doc_hdit::CodeModule {
        name: "src/lib.rs".into(),
        is_public: true,
        items: vec![doc_hdit::CodeItem {
            kind: "use".into(),
            ident: "castle::*".into(),
            signature: "castle::*".into(),
            is_public: true,
        }],
    }];
    let glob_tokens = code_token_set(&glob_only);
    let star = claim("c3", "docs/x.md", "mentions", "*");
    assert!(
        !claim_grounded(&star, &glob_tokens),
        "glob tail must not become a groundable symbol"
    );
}
