//! Multiply–add–permute (MAP) hypervectors over {-1,+1}^D (i64 lanes).

pub mod encode;

use crate::DIM;

/// A bipolar hypervector.
pub type Hv = Vec<i64>;

/// FNV-1a 64-bit string hash — the deterministic seed source.
fn fnv1a(s: &str) -> u64 {
    let mut h: u64 = 0xcbf2_9ce4_8422_2325;
    for b in s.as_bytes() {
        h ^= *b as u64;
        h = h.wrapping_mul(0x0000_0100_0000_01b3);
    }
    h
}

/// SplitMix64 — deterministic, platform-independent stream.
fn splitmix(state: &mut u64) -> u64 {
    *state = state.wrapping_add(0x9E37_79B9_7F4A_7C15);
    let mut z = *state;
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}

/// Deterministic seeded basis vector: one stable vector per identifier,
/// reproducible across runs and platforms (no float RNG).
pub fn basis(ident: &str) -> Hv {
    let mut state = fnv1a(ident);
    (0..DIM)
        .map(|_| {
            let z = splitmix(&mut state);
            if z.count_ones() & 1 == 0 {
                1
            } else {
                -1
            }
        })
        .collect()
}

/// Bind: elementwise multiplication (self-inverse, distributes over bundle).
pub fn bind(a: &Hv, b: &Hv) -> Hv {
    a.iter()
        .zip(b.iter())
        .map(|(x, y)| x * y)
        .collect()
}

/// Bundle: elementwise sum then sign-of-majority. Ties (sum == 0) are broken
/// deterministically and *unbiasedly* by dimension parity (popcount parity of
/// the dimension index), so bundling an even number of near-orthogonal vectors
/// stays symmetric — no fixed-sign bias toward +1.
pub fn bundle(vs: &[Hv]) -> Hv {
    let mut acc = vec![0i64; DIM];
    for v in vs {
        for (a, x) in acc.iter_mut().zip(v.iter()) {
            *a += x;
        }
    }
    acc.iter()
        .enumerate()
        .map(|(j, &s)| match s.cmp(&0) {
            std::cmp::Ordering::Less => -1,
            std::cmp::Ordering::Greater => 1,
            std::cmp::Ordering::Equal => {
                if j.count_ones() & 1 == 0 {
                    1
                } else {
                    -1
                }
            }
        })
        .collect()
}

/// Permute: cyclic rotation by k.
pub fn permute(v: &Hv, k: usize) -> Hv {
    let k = k % DIM;
    let mut out = vec![0i64; DIM];
    out[..DIM - k].copy_from_slice(&v[k..]);
    out[DIM - k..].copy_from_slice(&v[..k]);
    out
}

/// Cosine similarity between two hypervectors.
pub fn cosine(a: &Hv, b: &Hv) -> f64 {
    let dot: i64 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    dot as f64 / DIM as f64
}

/// L2 norm (always sqrt(D) for bipolar vectors, provided for generality).
pub fn norm(v: &[f64]) -> f64 {
    v.iter().map(|x| x * x).sum::<f64>().sqrt()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn basis_is_deterministic() {
        assert_eq!(basis("foo"), basis("foo"));
        assert_ne!(basis("foo"), basis("bar"));
    }

    #[test]
    fn bind_is_self_inverse() {
        let a = basis("a");
        let b = basis("b");
        assert_eq!(bind(&bind(&a, &b), &b), a);
    }

    #[test]
    fn permute_rotates() {
        let v = basis("p");
        assert_eq!(permute(&v, 1)[0], v[1]);
        assert_eq!(permute(&v, 0), v);
    }
}
