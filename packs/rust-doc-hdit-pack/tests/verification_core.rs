//! Chicago-style integration tests: real math, no mocks.

use doc_hdit::info_theory::entropy::{mutual_information, q_density, shannon};
use doc_hdit::info_theory::{projection_residual, rank_phantoms, s_coverage, CodeBasis};
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
        items: vec![
            doc_hdit::CodeItem {
                kind: "fn".into(),
                ident: "ignite".into(),
                signature: "ignite(fuel: Fuel) -> Spark".into(),
            },
            doc_hdit::CodeItem {
                kind: "struct".into(),
                ident: "Piston".into(),
                signature: "Piston { bore: u32 }".into(),
            },
            doc_hdit::CodeItem {
                kind: "fn".into(),
                ident: "exhaust".into(),
                signature: "exhaust(gas: Gas)".into(),
            },
            doc_hdit::CodeItem {
                kind: "trait".into(),
                ident: "Valved".into(),
                signature: "Valved: Send".into(),
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

    let (_h_code, codewords) = doc_hdit::vsa::encode::encode_code(&modules);
    let h_doc = doc_hdit::vsa::encode::encode_doc(&claims);
    let code_basis = CodeBasis::build(&codewords);

    let phi = projection_residual(&h_doc, &claims, &code_basis);
    assert!(phi > 0.0, "expected Phi > 0 for planted phantom, got {}", phi);

    let ranked = rank_phantoms(&claims, &code_basis);
    assert_eq!(
        ranked[0].0,
        4,
        "phantom claim index 4 must rank top-1; got {:?}",
        ranked
    );

    // and the grounded baseline is strictly cleaner
    let phi_grounded = {
        let gc = grounded_claims();
        let hd = doc_hdit::vsa::encode::encode_doc(&gc);
        projection_residual(&hd, &gc, &code_basis)
    };
    assert!(phi > phi_grounded);
}

#[test]
fn grounded_doc_yields_near_zero_phi() {
    let modules = fixture_modules();
    let claims = grounded_claims();
    let (_, codewords) = doc_hdit::vsa::encode::encode_code(&modules);
    let h_doc = doc_hdit::vsa::encode::encode_doc(&claims);
    let code_basis = CodeBasis::build(&codewords);
    let phi = projection_residual(&h_doc, &claims, &code_basis);
    assert!(
        phi < 1e-9,
        "grounded doc should have Phi ~ 0, got {}",
        phi
    );
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
    let q_grounded = q_density(&grounded, &modules);
    let q_phantom = q_density(&phantom, &modules);
    assert!((q_grounded - 0.5).abs() < 1e-12); // 2 bits / 4 claims
    assert!(q_phantom < q_grounded);
}
