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
/// per-claim cosine of the claim vector against the code subspace
/// (low alignment = high residual contribution = phantom suspect).
/// Returns indices sorted worst-alignment first, paired with alignment values.
pub fn rank_phantoms(claims: &[Claim], code_basis: &CodeBasis) -> Vec<(usize, f64)> {
    let mut ranked: Vec<(usize, f64)> = claims
        .iter()
        .enumerate()
        .map(|(i, c)| {
            let v = encode_claim(c);
            let p = CodeBasis::binarize(&code_basis.project(&v));
            let align = cosine(&v, &p);
            (i, align)
        })
        .collect();
    ranked.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal));
    ranked
}

/// Evaluate a single claim against a set of code modules (used by entropy grounding).
pub fn code_token_set(modules: &[CodeModule]) -> std::collections::HashSet<String> {
    let mut set = std::collections::HashSet::new();
    for m in modules {
        set.insert(m.name.clone());
        for it in &m.items {
            set.insert(it.kind.clone());
            set.insert(it.ident.clone());
            set.insert(it.signature.clone());
        }
    }
    set
}
