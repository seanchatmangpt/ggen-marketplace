//! doc-hdit: VSA (MAP holographic reduced representations) + discrete
//! information-theory verification core for documentation quality courts.
//!
//! Layers:
//! - [`vsa`]: deterministic bipolar hypervectors (D=10000), bind/bundle/permute/cosine.
//! - [`vsa::encode`]: code-surface and doc-claim encoders.
//! - [`info_theory`]: coverage similarity, projection residual (Phi), residual
//!   unbinding (phantom-claim ranking), Shannon entropy + v1 discrete mutual
//!   information estimator, Q_density.
//! - [`bin`]: `doc-hdit vectorize` and `doc-hdit audit` CLI (no std::process in lib;
//!   wasm32-wasip1 compatible).

pub mod info_theory;
pub mod scaffold;
pub mod vsa;

/// Dimensionality of all hypervectors.
pub const DIM: usize = 10_000;

/// A code-surface module with its items (functions, structs, traits, ...).
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct CodeModule {
    pub name: String,
    pub items: Vec<CodeItem>,
}

/// A single code item.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct CodeItem {
    pub kind: String,
    pub ident: String,
    pub signature: String,
}

/// A documentation claim as an EAV triple.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Claim {
    pub id: String,
    pub subject: String,
    pub predicate: String,
    pub object: String,
}
