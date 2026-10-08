//! Shannon entropy and the v1 discrete mutual-information estimator.

use crate::info_theory::code_token_set;
use crate::{Claim, CodeModule};

/// Shannon entropy H (bits) over a token distribution.
pub fn shannon(tokens: &[&str]) -> f64 {
    let mut counts: std::collections::HashMap<&str, usize> = std::collections::HashMap::new();
    for t in tokens {
        *counts.entry(t).or_insert(0) += 1;
    }
    let n = tokens.len();
    if n == 0 {
        return 0.0;
    }
    counts
        .values()
        .map(|&c| {
            let p = c as f64 / n as f64;
            -p * p.log2()
        })
        .sum()
}

/// A claim is grounded iff every EAV token appears in the code-surface token set.
pub fn claim_grounded(claim: &Claim, tokens: &std::collections::HashSet<String>) -> bool {
    tokens.contains(&claim.subject)
        && tokens.contains(&claim.predicate)
        && tokens.contains(&claim.object)
}

/// v1 discrete estimator (documented approximation):
/// I(D;C) = H(D) - H(D|C) where H(D) = log2(n) (uniform over n claims) and
/// H(D|C) = (1/n) * sum of per-claim surprisal in bits:
/// grounded claim => 0 surprisal, ungrounded claim => log2(2) = 1 bit.
/// This is a discrete, court-friendly lower bound, not a continuous MI estimate.
pub fn mutual_information(claims: &[Claim], modules: &[CodeModule]) -> f64 {
    let n = claims.len();
    if n == 0 {
        return 0.0;
    }
    let tokens = code_token_set(modules);
    let h_d = (n as f64).log2();
    let h_dc: f64 = claims
        .iter()
        .map(|c| if claim_grounded(c, &tokens) { 0.0 } else { 1.0 })
        .sum::<f64>()
        / n as f64;
    h_d - h_dc
}

/// Q_density = I(D;C) / L where L = number of claims (v1: doc length in claims).
pub fn q_density(claims: &[Claim], modules: &[CodeModule]) -> f64 {
    let l = claims.len();
    if l == 0 {
        return 0.0;
    }
    mutual_information(claims, modules) / l as f64
}
