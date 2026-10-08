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
}

/// S_coverage = cosine(H_doc, H_code).
pub fn s_coverage(h_doc: &Hv, h_code: &Hv) -> f64 {
    cosine(h_doc, h_code)
}

/// Projection residual: R = H_doc - P_code(H_doc);
/// Phi = ||R|| / ||H_doc|| (MAP L2 norms; ||H_doc|| = sqrt(D) for bipolar input).
pub fn projection_residual(h_doc: &Hv, code_basis: &CodeBasis) -> f64 {
    let p = code_basis.project(h_doc);
    let mut res2 = 0.0;
    let mut tot2 = 0.0;
    for i in 0..DIM {
        let d = (h_doc[i] as f64) - p[i];
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
            let p = code_basis.project(&v);
            let pv = crate::vsa::norm(&p);
            let nv = crate::vsa::norm(&v.iter().map(|&x| x as f64).collect::<Vec<f64>>());
            let align = if nv > 0.0 { pv / nv } else { 0.0 };
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
