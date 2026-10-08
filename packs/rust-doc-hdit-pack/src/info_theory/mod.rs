//! Coverage similarity, projection residual (Phi), phantom ranking.

pub mod entropy;

use crate::vsa::{cosine, encode::encode_claim, Hv};
use crate::{public_modules, Claim, CodeModule, DIM};

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

/// P3 prose-artifact classifier (core-side defense; the extractor
/// (`gen_doc_surface.py`) is the primary filter and stops emitting such claims
/// at all). A claim object is a `prose_artifact` — not a symbol reference,
/// excluded from Phi like `external_documented` but reported as a count — when
/// it is a version string (`1.2.3`, `v26.8.23`), a path fragment
/// (`release/v26.8.23`, `stream/metrics.ex`), a CLI flag (`--mem-gb`), or
/// non-identifier prose (whitespace / punctuation outside the symbol charset).
fn looks_like_version(seg: &str) -> bool {
    let t = seg.trim_start_matches(['v', 'V']);
    if t.is_empty() || !t.contains('.') {
        return false;
    }
    t.split('.').all(|p| !p.is_empty() && p.chars().all(|c| c.is_ascii_digit()))
}

/// Source-file extensions that mark a slash-span as a path fragment, not a
/// symbol (Elixir arity forms like `verify/0` do not match and stay symbols).
pub const SOURCE_EXTS: &[&str] = &[
    ".ex", ".exs", ".rs", ".py", ".ts", ".tsx", ".js", ".json", ".jsonl", ".toml", ".yaml",
    ".yml", ".md", ".ttl", ".sql", ".sh", ".wasm",
];

/// Classify a claim object as a prose artifact (see module docs). Deterministic.
pub fn is_prose_artifact(object: &str) -> bool {
    let s = object.trim();
    if s.is_empty() {
        return true;
    }
    // CLI flags are extractor noise, never symbols.
    if s.starts_with("--") {
        return true;
    }
    // Bare version strings: `1.2.3`, `v26.8.23`.
    if looks_like_version(s) {
        return true;
    }
    if s.contains('/') {
        let segs: Vec<&str> = s.split('/').collect();
        // Version-tagged path fragments: `release/v26.8.23`.
        if segs.iter().any(|seg| looks_like_version(seg)) {
            return true;
        }
        // Source-file path fragments: `stream/metrics.ex`.
        if segs.len() > 1 {
            if let Some(last) = segs.last() {
                let last = last.trim_end_matches("()");
                if SOURCE_EXTS.iter().any(|e| last.ends_with(e)) {
                    return true;
                }
            }
        }
    }
    // Non-identifier prose: whitespace outside a signature form (signature
    // quotes like `ignite(fuel: Fuel) -> Spark` are real symbol references),
    // or prose punctuation outside the symbol charset.
    let core = if s.contains('(') {
        s.chars().filter(|c| !c.is_whitespace()).collect::<String>()
    } else {
        s.to_string()
    };
    if core.chars().any(|c| {
        !(c.is_alphanumeric()
            || matches!(c, '_' | '.' | '/' | ':' | '-' | '!' | '?' | '(' | ')' | '>' | '{' | '}' | ','))
    }) {
        return true;
    }
    false
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
    /// Object is a version string, path fragment, or other non-identifier
    /// prose (extractor over-extraction residue; P3 filter class).
    ProseArtifact,
    /// Object matches neither — a phantom.
    Phantom,
}

pub fn claim_status(
    claim: &Claim,
    tokens: &std::collections::HashSet<String>,
    external: &[String],
) -> ClaimStatus {
    if is_prose_artifact(&claim.object) {
        return ClaimStatus::ProseArtifact;
    }
    if crate::info_theory::entropy::claim_grounded(claim, tokens) {
        return ClaimStatus::Grounded;
    }
    if is_external_documented(&claim.object, external) {
        return ClaimStatus::ExternalDocumented;
    }
    ClaimStatus::Phantom
}

/// Scoped Phi (P2, P3): phantom_claims / scored_claims. `external_documented`
/// claims are excluded from the phantom count (reported separately);
/// `prose_artifact` claims are extractor noise carrying no bits — excluded
/// from both numerator and denominator.
pub fn phi_scoped(
    claims: &[Claim],
    tokens: &std::collections::HashSet<String>,
    external: &[String],
) -> f64 {
    let scored: Vec<&Claim> = claims
        .iter()
        .filter(|c| claim_status(c, tokens, external) != ClaimStatus::ProseArtifact)
        .collect();
    if scored.is_empty() {
        return 0.0;
    }
    let phantoms = scored
        .iter()
        .filter(|c| claim_status(c, tokens, external) == ClaimStatus::Phantom)
        .count();
    phantoms as f64 / scored.len() as f64
}

/// Scoped Q_density (P2, P3): (grounded + external_documented) / scored. A
/// claim referencing documented dep surface is verified information — it
/// grounds against the dependency's own docs, so it counts as density, not
/// residue. Prose artifacts are excluded from both numerator and denominator.
pub fn q_density_scoped(
    claims: &[Claim],
    tokens: &std::collections::HashSet<String>,
    external: &[String],
) -> f64 {
    let scored: Vec<&Claim> = claims
        .iter()
        .filter(|c| claim_status(c, tokens, external) != ClaimStatus::ProseArtifact)
        .collect();
    if scored.is_empty() {
        return 0.0;
    }
    let ok = scored
        .iter()
        .filter(|c| claim_status(c, tokens, external) != ClaimStatus::Phantom)
        .count();
    ok as f64 / scored.len() as f64
}

// ------------------------------------------------------- set coverage (P3) ---

/// Set-coverage result: the court-gated S_coverage per the court's stated
/// definition (P3), plus the remediation surface.
#[derive(Debug, Clone)]
pub struct CoverageReport {
    /// covered_public_items / total_public_items.
    pub coverage: f64,
    pub covered: usize,
    pub total: usize,
    /// (module_name, uncovered_public_item_count), descending by count.
    pub uncovered_modules: Vec<(String, usize)>,
}

/// Claim-object variant token set (dual of `code_token_set`).
pub fn claim_token_set(claims: &[Claim]) -> std::collections::HashSet<String> {
    claims
        .iter()
        .flat_map(|c| symbol_variants(&c.object))
        .collect()
}

/// An item is covered iff its ident — in bare, qualified (`Module.ident`),
/// or arity (`ident/2`) form — appears in any claim object, or the claim
/// quotes the item's full signature (the arity-form's stricter sibling).
fn item_covered(
    ident: &str,
    signature: &str,
    module_name: &str,
    claimed: &std::collections::HashSet<String>,
) -> bool {
    let mut variants: Vec<String> = symbol_variants(ident).into_iter().collect();
    if !signature.is_empty() {
        variants.extend(symbol_variants(signature));
    }
    variants.push(format!("{}.{}", module_name, ident));
    variants.push(format!("{}::{}", module_name, ident));
    variants.iter().any(|v| claimed.contains(v))
}

/// S_coverage (set semantics, P3, the GATED metric): fraction of public items
/// whose ident (or qualified name, or arity form) appears in any non-prose
/// claim object. Replaces the VSA projection cosine, which is kept
/// report-only as `s_coverage_vsa`.
pub fn s_coverage_set(modules: &[CodeModule], claims: &[Claim]) -> f64 {
    s_coverage_set_report(modules, claims).coverage
}

/// Full set-coverage report including the top uncovered public modules
/// (remediation list: module name + count of uncovered public items).
pub fn s_coverage_set_report(modules: &[CodeModule], claims: &[Claim]) -> CoverageReport {
    let public = public_modules(modules);
    let claimed = claim_token_set(claims);
    let mut covered = 0usize;
    let mut total = 0usize;
    let mut uncovered: Vec<(String, usize)> = Vec::new();
    for m in &public {
        let mut miss = 0usize;
        for it in m.items.iter().filter(|it| it.is_public) {
            total += 1;
            if item_covered(&it.ident, &it.signature, &m.name, &claimed) {
                covered += 1;
            } else {
                miss += 1;
            }
        }
        if miss > 0 {
            uncovered.push((m.name.clone(), miss));
        }
    }
    uncovered.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));
    let coverage = if total == 0 { 0.0 } else { covered as f64 / total as f64 };
    CoverageReport { coverage, covered, total, uncovered_modules: uncovered }
}
