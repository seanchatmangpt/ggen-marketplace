//! Coverage similarity, projection residual (Phi), phantom ranking.

pub mod entropy;

use crate::vsa::{cosine, encode::encode_claim, Hv};
use crate::{Claim, CodeModule, DIM};

/// Code subspace basis: orthonormalized code codewords (Gram-Schmidt).
pub struct CodeBasis {
    basis: Vec<Vec<f64>>,
}

impl CodeBasis {
    /// Build the basis from code-surface codewords (module + item vectors).
    pub fn build(codewords: &[Hv]) -> CodeBasis {
        let mut basis: Vec<Vec<f64>> = Vec::with_capacity(codewords.len());
        for cw in codewords {
            let mut v: Vec<f64> = cw.iter().map(|&x| x as f64).collect();
            for b in &basis {
                let p: f64 = v.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
                for (x, y) in v.iter_mut().zip(b.iter()) {
                    *x -= p * y;
                }
            }
            let n = crate::vsa::norm(&v);
            if n > 1e-9 {
                for x in v.iter_mut() {
                    *x /= n;
                }
                basis.push(v);
            }
        }
        CodeBasis { basis }
    }

    /// Projection of a vector onto the code subspace.
    pub fn project(&self, v: &Hv) -> Vec<f64> {
        let mut out = vec![0.0; DIM];
        let vf: Vec<f64> = v.iter().map(|&x| x as f64).collect();
        for b in &self.basis {
            let c: f64 = vf.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
            for (o, y) in out.iter_mut().zip(b.iter()) {
                *o += c * y;
            }
        }
        out
    }

    /// Binarize a real-valued projection back to bipolar (ties by dim parity).
    pub fn binarize(v: &[f64]) -> Hv {
        v.iter()
            .enumerate()
            .map(|(j, &x)| match x.partial_cmp(&0.0) {
                Some(std::cmp::Ordering::Less) => -1,
                Some(std::cmp::Ordering::Greater) => 1,
                _ => {
                    if j.count_ones() & 1 == 0 {
                        1
                    } else {
                        -1
                    }
                }
            })
            .collect()
    }
}

/// S_coverage = cosine(H_doc, P_code(H_doc)): the fraction of the document
/// vector reproducible from the code surface. A fully grounded document
/// round-trips exactly (S = 1.0); phantom claims pull it toward 0.
pub fn s_coverage(h_doc: &Hv, claims: &[Claim], code_basis: &CodeBasis) -> f64 {
    let projected: Vec<Hv> = claims
        .iter()
        .map(|c| CodeBasis::binarize(&code_basis.project(&encode_claim(c))))
        .collect();
    let p_code = crate::vsa::bundle(&projected);
    cosine(h_doc, &p_code)
}

/// Projection residual through the encoder's bundling structure:
/// P_code(H_doc) = bundle over claims of binarize(project(claim_i)).
/// A claim already in the code subspace (grounded) round-trips exactly, so a
/// fully grounded document has Phi = 0. R = H_doc - P_code(H_doc);
/// Phi = ||R|| / ||H_doc|| (MAP L2 norms).
pub fn projection_residual(
    h_doc: &Hv,
    claims: &[Claim],
    code_basis: &CodeBasis,
) -> f64 {
    let projected: Vec<Hv> = claims
        .iter()
        .map(|c| {
            let p = code_basis.project(&encode_claim(c));
            CodeBasis::binarize(&p)
        })
        .collect();
    let p_code = crate::vsa::bundle(&projected);
    let mut res2 = 0.0f64;
    let mut tot2 = 0.0f64;
    for i in 0..DIM {
        let d = (h_doc[i] as f64) - (p_code[i] as f64);
        res2 += d * d;
        tot2 += (h_doc[i] as f64) * (h_doc[i] as f64);
    }
    if tot2 == 0.0 {
        0.0
    } else {
        res2.sqrt() / tot2.sqrt()
    }
}

/// Residual unbinding: rank claim indices by individual residual contribution —
/// ungrounded claims (exact-match core, deterministic) first, and within each
/// class by ascending VSA alignment against the code subspace (the secondary
/// near-miss similarity signal; low alignment = high residual contribution).
/// Returns (claim_index, vsa_alignment, grounded) sorted worst first.
pub fn rank_phantoms(
    claims: &[Claim],
    tokens: &std::collections::HashSet<String>,
    code_basis: &CodeBasis,
) -> Vec<(usize, f64, bool)> {
    let mut ranked: Vec<(usize, f64, bool)> = claims
        .iter()
        .enumerate()
        .map(|(i, c)| {
            let grounded = crate::info_theory::entropy::claim_grounded(c, tokens);
            let v = encode_claim(c);
            let p = CodeBasis::binarize(&code_basis.project(&v));
            let align = cosine(&v, &p);
            (i, align, grounded)
        })
        .collect();
    ranked.sort_by(|a, b| {
        a.2.cmp(&b.2)
            .then(a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal))
    });
    ranked
}

/// Strip a trailing arity suffix (`ident/2`), a trailing call pair
/// (`ident()`), and any leading module/path qualification
/// (`Foo.Bar::baz/1` -> `Foo.Bar::baz`, `baz`).
pub fn symbol_variants(sym: &str) -> Vec<String> {
    let mut out = vec![sym.to_string()];
    let base = sym.trim_end_matches("()").trim_end_matches('/');
    let base = if base.is_empty() { sym } else { base };
    out.push(base.to_string());
    // arity-stripped form: cut at the last '/' when what follows is digits
    if let Some(pos) = base.rfind('/') {
        let (head, tail) = base.split_at(pos);
        if !tail.is_empty() && tail[1..].chars().all(|c| c.is_ascii_digit()) {
            out.push(head.to_string());
            let q = head;
            out.push(q.rsplit('/').next().unwrap_or(q).to_string());
            if let Some(seg) = q.split('.').last() {
                out.push(seg.to_string());
            }
            if let Some(seg) = q.split("::").last() {
                out.push(seg.to_string());
            }
        }
    }
    out.push(base.rsplit('/').next().unwrap_or(base).to_string());
    if let Some(seg) = base.split('.').last() {
        out.push(seg.to_string());
    }
    if let Some(seg) = base.split("::").last() {
        out.push(seg.to_string());
    }
    out.into_iter()
        .filter(|s| !s.is_empty())
        .collect::<std::collections::HashSet<_>>()
        .into_iter()
        .collect()
}

/// Deterministic code-surface symbol set: module names (plus their file-stem
/// and path-tail variants) and every item ident/signature. Exact membership
/// over claim-object variants is the PRIMARY phantom gate; the VSA cosine is
/// only a secondary near-miss similarity signal.
pub fn code_token_set(modules: &[CodeModule]) -> std::collections::HashSet<String> {
    let mut set = std::collections::HashSet::new();
    for m in modules {
        set.extend(symbol_variants(&m.name));
        // file-stem variant for path-named modules (ferroplan scanner shape)
        let stem = m
            .name
            .rsplit('/')
            .next()
            .unwrap_or(&m.name)
            .trim_end_matches(".rs")
            .trim_end_matches(".ex")
            .trim_end_matches(".exs");
        set.extend(symbol_variants(stem));
        for it in &m.items {
            set.extend(symbol_variants(&it.ident));
            set.extend(symbol_variants(&it.signature));
        }
    }
    set
}

/// A claim is a phantom iff its OBJECT symbol is absent from the code surface
/// (exact-match core, deterministic). Phi = ungrounded_claims / total_claims;
/// bounded in [0, 1] by construction (v1's VSA projection residual could
/// exceed 1 and carried no real/phantom separation).
pub fn phi_exact(claims: &[Claim], tokens: &std::collections::HashSet<String>) -> f64 {
    if claims.is_empty() {
        return 0.0;
    }
    let ungrounded = claims
        .iter()
        .filter(|c| !crate::info_theory::entropy::claim_grounded(c, tokens))
        .count();
    ungrounded as f64 / claims.len() as f64
}

/// P2 external-deps allowance: a claim's object resolves against a documented
/// external dependency (`Ash.`, `Ecto.`, `serde_json::`, ...) rather than the
/// repo's code surface. Such claims are `external_documented`, not phantoms —
/// excluded from Phi and counted separately.
pub fn is_external_documented(object: &str, external: &[String]) -> bool {
    let obj = object.trim();
    external
        .iter()
        .any(|p| !p.is_empty() && obj.starts_with(p.as_str()))
}

/// Per-claim grounding status under the P2 scope rules.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ClaimStatus {
    /// Object matches the repo's code surface.
    Grounded,
    /// Object references a documented external dependency.
    ExternalDocumented,
    /// Object matches neither — a phantom.
    Phantom,
}

pub fn claim_status(
    claim: &Claim,
    tokens: &std::collections::HashSet<String>,
    external: &[String],
) -> ClaimStatus {
    if crate::info_theory::entropy::claim_grounded(claim, tokens) {
        return ClaimStatus::Grounded;
    }
    if is_external_documented(&claim.object, external) {
        return ClaimStatus::ExternalDocumented;
    }
    ClaimStatus::Phantom
}

/// Scoped Phi (P2): phantom_claims / total_claims. `external_documented`
/// claims are excluded from the phantom count (reported separately).
pub fn phi_scoped(
    claims: &[Claim],
    tokens: &std::collections::HashSet<String>,
    external: &[String],
) -> f64 {
    if claims.is_empty() {
        return 0.0;
    }
    let phantoms = claims
        .iter()
        .filter(|c| claim_status(c, tokens, external) == ClaimStatus::Phantom)
        .count();
    phantoms as f64 / claims.len() as f64
}

/// Scoped Q_density (P2): (grounded + external_documented) / total. A claim
/// referencing documented dep surface is verified information — it grounds
/// against the dependency's own docs, so it counts as density, not residue.
pub fn q_density_scoped(
    claims: &[Claim],
    tokens: &std::collections::HashSet<String>,
    external: &[String],
) -> f64 {
    if claims.is_empty() {
        return 0.0;
    }
    let ok = claims
        .iter()
        .filter(|c| claim_status(c, tokens, external) != ClaimStatus::Phantom)
        .count();
    ok as f64 / claims.len() as f64
}
