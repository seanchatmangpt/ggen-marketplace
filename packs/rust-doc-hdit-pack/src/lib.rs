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

#[cfg(feature = "blake3")]
pub mod certify;
pub mod info_theory;
pub mod scaffold;
pub mod vsa;

/// Dimensionality of all hypervectors.
pub const DIM: usize = 10_000;

/// Serde default for `is_public` so pre-P2 code-surface JSON (no flag) still
/// loads as the full public surface — backward compatible, never silent-empty.
fn default_public() -> bool {
    true
}

/// A code-surface module with its items (functions, structs, traits, ...).
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct CodeModule {
    pub name: String,
    #[serde(default = "default_public")]
    pub is_public: bool,
    pub items: Vec<CodeItem>,
}

/// A single code item.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct CodeItem {
    pub kind: String,
    pub ident: String,
    pub signature: String,
    #[serde(default = "default_public")]
    pub is_public: bool,
}

/// P2 scope: restrict the code surface to the public/documented items.
/// A module survives with only its public items; modules with no public items
/// are dropped. The full surface stays available for S_coverage_raw.
pub fn public_modules(modules: &[CodeModule]) -> Vec<CodeModule> {
    modules
        .iter()
        .filter(|m| m.is_public)
        .filter_map(|m| {
            let items: Vec<CodeItem> = m
                .items
                .iter()
                .filter(|it| it.is_public)
                .cloned()
                .collect();
            if items.is_empty() {
                None
            } else {
                Some(CodeModule {
                    name: m.name.clone(),
                    is_public: m.is_public,
                    items,
                })
            }
        })
        .collect()
}

/// A documentation claim as an EAV triple.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Claim {
    pub id: String,
    pub subject: String,
    pub predicate: String,
    pub object: String,
}
