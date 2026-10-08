//! Encoders: code surface and doc claims into hypervectors.

use crate::vsa::{bind, bundle, basis, permute, Hv};
use crate::{Claim, CodeModule};

/// Number of item codewords kept in the code basis for projection.
pub const MAX_BASIS_ITEMS: usize = 256;

/// H_code = bundle over modules of
/// ( v(module_name) (X) bundle over items of (P1 v(kind) (X) P2 v(ident) (X) P3 v(signature)) ).
pub fn encode_code(modules: &[CodeModule]) -> (Hv, Vec<Hv>) {
    let mut module_vecs = Vec::with_capacity(modules.len());
    for m in modules {
        let mut item_vecs = Vec::with_capacity(m.items.len());
        for it in &m.items {
            let v = bind(
                &bind(&permute(&basis(&it.kind), 1), &basis(&it.ident)),
                &permute(&basis(&it.signature), 3),
            );
            item_vecs.push(v);
        }
        let items = if item_vecs.is_empty() {
            basis(&format!("__empty_module__{}", m.name))
        } else {
            bundle(&item_vecs)
        };
        module_vecs.push(bind(&basis(&m.name), &items));
        module_vecs.extend(item_vecs.into_iter().take(MAX_BASIS_ITEMS));
    }
    let h = bundle(&module_vecs);
    (h.clone(), module_vecs)
}

/// H_doc = bundle over claims of
/// ( P1 v(subject) (X) P2 v(predicate) (X) P3 v(object) ) — EAV triples.
pub fn encode_doc(claims: &[Claim]) -> Hv {
    let vs: Vec<Hv> = claims
        .iter()
        .map(encode_claim)
        .collect();
    bundle(&vs)
}

/// Per-claim hypervector.
pub fn encode_claim(c: &Claim) -> Hv {
    bind(
        &bind(&permute(&basis(&c.subject), 1), &basis(&c.predicate)),
        &permute(&basis(&c.object), 3),
    )
}
