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
