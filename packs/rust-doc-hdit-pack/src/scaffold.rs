//! `doc-hdit:scaffold` — deterministic skeleton rendering with commentary merge.
//!
//! Renders the pack's Tera templates from a code-surface JSON (as produced by
//! `scripts/gen_doc_surface.py code REPO`) into a docs directory. Reference
//! bodies are AGENT-FORBIDDEN-fenced (rigid rows from the code surface);
//! commentary slots are delimited by AGENT-COMMENTARY markers and survive
//! re-scaffolding via marker-based merge.

use serde_json::{json, Value};
use std::path::Path;

/// Exact marker strings delimiting agent commentary slots.
pub const COMMENTARY_BEGIN: &str = "<!-- AGENT-COMMENTARY-BEGIN -->";
pub const COMMENTARY_END: &str = "<!-- AGENT-COMMENTARY-END -->";

/// Outputs produced by a scaffold run.
pub const OUTPUTS: [&str; 3] = ["reference.md", "how_to.md", "explanation.md"];

/// Typed scaffold failures. `MarkerMissing` is the refusal raised when an
/// existing, non-empty output file carries no AGENT-COMMENTARY marker set —
/// hand-written prose the merge cannot preserve (ex4pm incident, backlog [63]).
#[derive(Debug)]
pub enum ScaffoldError {
    /// Existing file has content but no `COMMENTARY_BEGIN`; scaffold refused.
    MarkerMissing { path: std::path::PathBuf },
    /// Any other failure (I/O, template parse, render).
    Other(String),
}

impl std::fmt::Display for ScaffoldError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ScaffoldError::MarkerMissing { path } => write!(
                f,
                "REFUSED:SCAFFOLD_MARKER_MISSING:{} exists but has no {} marker; \
                 scaffolding would overwrite hand-written prose (use --force to overwrite)",
                path.display(),
                COMMENTARY_BEGIN
            ),
            ScaffoldError::Other(s) => write!(f, "{}", s),
        }
    }
}

impl std::error::Error for ScaffoldError {}

/// Build the deterministic Tera context from a code-surface JSON value.
///
/// The JSON shape follows `scripts/gen_doc_surface.py code`:
/// `{"repo", "path", "version": {...}, "modules": [{"name", "file", "items":
/// [{"kind", "ident", "signature"}]}]}`. Missing/extra fields are tolerated;
/// everything is sorted so re-renders are byte-identical.
pub fn build_context(surface: &Value) -> Value {
    let crate_name = surface
        .get("repo")
        .and_then(Value::as_str)
        .unwrap_or("crate")
        .to_string();

    let mut modules: Vec<Value> = Vec::new();
    let mut reference_rows: Vec<Value> = Vec::new();
    let mut facts: Vec<String> = Vec::new();
    let mut steps: Vec<String> = Vec::new();
    let mut verified_snippet = String::new();

    let mut mod_list: Vec<&Value> = surface
        .get("modules")
        .and_then(Value::as_array)
        .map(|a| a.iter().collect())
        .unwrap_or_default();
    mod_list.sort_by_key(|m| m.get("name").and_then(Value::as_str).unwrap_or("").to_string());

    for m in mod_list {
        let mname = m.get("name").and_then(Value::as_str).unwrap_or("").to_string();
        let mut items: Vec<&Value> = m
            .get("items")
            .and_then(Value::as_array)
            .map(|a| a.iter().collect())
            .unwrap_or_default();
        items.sort_by_key(|i| {
            (
                i.get("kind").and_then(Value::as_str).unwrap_or("").to_string(),
                i.get("ident").and_then(Value::as_str).unwrap_or("").to_string(),
            )
        });
        let mut rendered_items: Vec<Value> = Vec::new();
        for it in items {
            let kind = it.get("kind").and_then(Value::as_str).unwrap_or("").to_string();
            let ident = it.get("ident").and_then(Value::as_str).unwrap_or("").to_string();
            let signature = it
                .get("signature")
                .and_then(Value::as_str)
                .unwrap_or("")
                .to_string();
            // The code surface carries no param/default/error/invariant facts;
            // those columns stay empty rather than being invented.
            let row = json!({
                "item": ident,
                "itemType": kind,
                "signature": signature,
                "params": "",
                "defaults": "",
                "errors": "",
                "invariants": "",
            });
            rendered_items.push(row.clone());
            let mut flat = row.clone();
            flat["module"] = json!(mname);
            reference_rows.push(flat);

            if !ident.is_empty() {
                facts.push(format!("{}::{} ({})", mname, ident, kind));
                if steps.len() < 12 {
                    steps.push(format!("Use `{}` from `{}`.", ident, mname));
                }
            }
            if verified_snippet.is_empty() && kind == "function" && !signature.is_empty() {
                verified_snippet = format!("// {} :: {}\n{}", mname, ident, signature);
            }
        }
        modules.push(json!({ "name": mname, "items": rendered_items }));
    }

    facts.sort();
    facts.truncate(40);

    let n_items: usize = reference_rows.len();
    json!({
        "crate_name": crate_name,
        "modules": modules,
        "reference_rows": reference_rows,
        "task_name": format!("Using {}", crate_name),
        "verified_facts": facts,
        "steps": steps,
        "verified_snippet": verified_snippet,
        "concept_name": crate_name,
        "concept_summary": format!(
            "{} is a crate with {} modules and {} public items on its code surface.",
            crate_name, modules.len(), n_items
        ),
    })
}

/// Merge rendered scaffolds with existing agent commentary.
///
/// For each commentary slot (BEGIN/END marker pair), if the existing file has
/// one at the same ordinal position, its inner content (agent elaboration) is
/// carried over verbatim; fresh template boilerplate is otherwise kept.
/// Byte-identical when run twice with no agent edits between.
pub fn merge_commentary(fresh: &str, existing: &str) -> String {
    fn blocks(text: &str) -> Vec<&str> {
        let mut out = Vec::new();
        let mut rest = text;
        while let Some(b) = rest.find(COMMENTARY_BEGIN) {
            let after = &rest[b + COMMENTARY_BEGIN.len()..];
            match after.find(COMMENTARY_END) {
                Some(e) => {
                    out.push(&after[..e]);
                    rest = &after[e + COMMENTARY_END.len()..];
                }
                None => break,
            }
        }
        out
    }
    let existing_blocks = blocks(existing);
    if existing_blocks.is_empty() {
        return fresh.to_string();
    }
    let mut out = String::with_capacity(fresh.len());
    let mut rest = fresh;
    let mut idx = 0usize;
    while let Some(b) = rest.find(COMMENTARY_BEGIN) {
        let after = &rest[b + COMMENTARY_BEGIN.len()..];
        let Some(e) = after.find(COMMENTARY_END) else { break };
        out.push_str(&rest[..b]);
        out.push_str(COMMENTARY_BEGIN);
        if let Some(carried) = existing_blocks.get(idx) {
            out.push_str(carried);
        } else {
            out.push_str(&after[..e]);
        }
        out.push_str(COMMENTARY_END);
        rest = &after[e + COMMENTARY_END.len()..];
        idx += 1;
    }
    out.push_str(rest);
    out
}

/// Render the templates in `templates_dir` against `surface` and write the
/// outputs (merged over any existing files) into `out_dir`.
///
/// Returns the list of written file paths. Deterministic: same inputs yield
/// byte-identical outputs (with identical existing-state).
pub fn scaffold(
    surface: &Value,
    templates_dir: &Path,
    out_dir: &Path,
    force: bool,
) -> Result<Vec<std::path::PathBuf>, ScaffoldError> {
    // Refuse before rendering/writing anything: any existing non-empty output
    // file whose template carries an AGENT-COMMENTARY slot but whose current
    // content has none is hand-written prose the marker merge would silently
    // drop. Outputs whose template is fully rigid (no slot, e.g.
    // reference.md) are deterministic overwrites by design and always pass
    // the guard. All-or-nothing across OUTPUTS.
    let pattern = templates_dir.join("*.tera");
    let pattern = pattern.to_str().ok_or_else(|| {
        ScaffoldError::Other("templates dir is not valid UTF-8".to_string())
    })?;
    let tera = tera::Tera::parse(&pattern)
        .map_err(|e| ScaffoldError::Other(format!("tera parse: {}", e)))?;
    let has_slot: Vec<(&str, bool)> = OUTPUTS
        .iter()
        .map(|name| {
            let template = name.replace(".md", ".md.tera");
            let body = std::fs::read_to_string(templates_dir.join(&template))
                .unwrap_or_default();
            (*name, body.contains(COMMENTARY_BEGIN))
        })
        .collect();
    if !force {
        for (name, slot) in &has_slot {
            if !slot {
                continue;
            }
            let out_path = out_dir.join(name);
            if let Ok(existing) = std::fs::read_to_string(&out_path) {
                if !existing.is_empty() && !existing.contains(COMMENTARY_BEGIN) {
                    return Err(ScaffoldError::MarkerMissing { path: out_path });
                }
            }
        }
    }
    let context = tera::Context::from_serialize(build_context(surface))
        .map_err(|e| ScaffoldError::Other(e.to_string()))?;

    std::fs::create_dir_all(out_dir)
        .map_err(|e| ScaffoldError::Other(format!("mkdir {}: {}", out_dir.display(), e)))?;
    let mut written = Vec::new();
    for name in OUTPUTS {
        let template = name.replace(".md", ".md.tera");
        let rendered = tera
            .render(&template, &context)
            .map_err(|e| ScaffoldError::Other(format!("render {}: {}", template, e)))?;
        let out_path = out_dir.join(name);
        let merged = match std::fs::read_to_string(&out_path) {
            Ok(existing) => merge_commentary(&rendered, &existing),
            Err(_) => rendered,
        };
        std::fs::write(&out_path, merged).map_err(|e| {
            ScaffoldError::Other(format!("write {}: {}", out_path.display(), e))
        })?;
        written.push(out_path);
    }
    Ok(written)
}

/// Convenience used by the binary: run scaffold from CLI flag triples.
pub fn scaffold_cli(
    code_path: &str,
    templates: &str,
    out: &str,
    force: bool,
) -> Result<Vec<std::path::PathBuf>, ScaffoldError> {
    let raw = std::fs::read_to_string(code_path).map_err(|e| {
        ScaffoldError::Other(format!("cannot read {}: {}", code_path, e))
    })?;
    let surface: Value = serde_json::from_str(&raw)
        .map_err(|e| ScaffoldError::Other(format!("invalid JSON in {}: {}", code_path, e)))?;
    scaffold(&surface, Path::new(templates), Path::new(out), force)
}

/// Exposed for tests: run scaffold twice and assert byte-identical outputs.
#[cfg(test)]
mod tests {
    use super::*;

    fn surface() -> Value {
        json!({
            "repo": "demo",
            "modules": [
                {"name": "b.rs", "items": [
                    {"kind": "function", "ident": "go", "signature": "go(x: u32)"},
                    {"kind": "struct", "ident": "S", "signature": ""}
                ]},
                {"name": "a.rs", "items": [
                    {"kind": "function", "ident": "hi", "signature": "hi()"}
                ]}
            ]
        })
    }

    #[test]
    fn context_is_sorted_and_deterministic() {
        let c1 = build_context(&surface());
        let c2 = build_context(&surface());
        assert_eq!(c1, c2);
        assert_eq!(c1["crate_name"], "demo");
        assert_eq!(c1["modules"][0]["name"], "a.rs");
    }

    #[test]
    fn scaffold_is_idempotent_and_merges_commentary() {
        let dir = std::env::temp_dir().join(format!("doc-hdit-scaffold-test-{}", std::process::id()));
        let tdir = dir.join("templates");
        let odir = dir.join("docs");
        std::fs::create_dir_all(&tdir).unwrap();
        let templates =
            std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("templates");
        for f in ["reference.md.tera", "how_to.md.tera", "explanation.md.tera"] {
            std::fs::copy(templates.join(f), tdir.join(f)).unwrap();
        }
        let run = || scaffold(&surface(), &tdir, &odir, false).unwrap();
        run();
        let snap: Vec<_> = OUTPUTS
            .iter()
            .map(|n| (n, std::fs::read(odir.join(n)).unwrap()))
            .collect();
        run();
        for (n, bytes) in &snap {
            assert_eq!(
                &std::fs::read(odir.join(n)).unwrap(),
                bytes,
                "{} not byte-identical on re-run",
                n
            );
        }
        // Agent elaborates commentary in how_to.md; re-scaffold must not clobber.
        let howto_path = odir.join("how_to.md");
        let elaborated = std::fs::read_to_string(&howto_path)
            .unwrap()
            .replace(
                "<!-- court fails Phi_halluc > 0.001 otherwise). No tables, no         -->",
                "<!-- court fails Phi_halluc > 0.001 otherwise). My note: use `go`.   -->",
            );
        std::fs::write(&howto_path, elaborated).unwrap();
        run();
        let after = std::fs::read_to_string(&howto_path).unwrap();
        assert!(after.contains("My note: use `go`."), "commentary clobbered");
        // And re-running after merge is still byte-identical.
        let before = std::fs::read_to_string(&howto_path).unwrap();
        run();
        assert_eq!(std::fs::read_to_string(&howto_path).unwrap(), before);
        std::fs::remove_dir_all(&dir).ok();
    }

    #[test]
    fn reference_table_identifiers_are_backtick_wrapped() {
        let dir = std::env::temp_dir().join(format!("doc-hdit-bt-test-{}", std::process::id()));
        let tdir = dir.join("templates");
        let odir = dir.join("docs");
        std::fs::create_dir_all(&tdir).unwrap();
        let templates =
            std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("templates");
        for f in ["reference.md.tera", "how_to.md.tera", "explanation.md.tera"] {
            std::fs::copy(templates.join(f), tdir.join(f)).unwrap();
        }
        scaffold(&surface(), &tdir, &odir, false).unwrap();
        let reference = std::fs::read_to_string(odir.join("reference.md")).unwrap();
        // Identifier cells must be claim-visible (backtick spans) for the
        // doc-claim scanner, including arity forms if the surface carries them.
        assert!(reference.contains("| `go` |"), "missing backticked `go`");
        assert!(reference.contains("| `hi` |"), "missing backticked `hi`");
        assert!(reference.contains("| `S` |"), "missing backticked `S`");
        // Every data-row item cell opens with a backtick (no bare identifiers).
        for line in reference.lines() {
            if !line.starts_with("| ") || line.starts_with("| Item") || line.starts_with("|--") {
                continue;
            }
            assert!(line.starts_with("| `"), "bare identifier cell: {}", line);
        }
        std::fs::remove_dir_all(&dir).ok();
    }

    #[test]
    fn merge_keeps_fresh_when_no_existing_blocks() {
        assert_eq!(merge_commentary("A <!-- X --> B", "no markers"), "A <!-- X --> B");
    }

    /// Incident corpus (backlog [63], ex4pm): an existing, marker-free,
    /// hand-written prose file must be refused, not silently overwritten.
    #[test]
    fn scaffold_refuses_marker_free_existing_prose() {
        let dir = std::env::temp_dir().join(format!("doc-hdit-missing-marker-{}", std::process::id()));
        let tdir = dir.join("templates");
        let odir = dir.join("docs");
        std::fs::create_dir_all(&tdir).unwrap();
        let templates =
            std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("templates");
        for f in ["reference.md.tera", "how_to.md.tera", "explanation.md.tera"] {
            std::fs::copy(templates.join(f), tdir.join(f)).unwrap();
        }
        // Simulate the ex4pm incident shape: hand-written Diátaxis prose with
        // no AGENT-COMMENTARY markers anywhere, in a slot-carrying output.
        std::fs::create_dir_all(&odir).unwrap();
        let prose = "# How-to\n\nHand-written prose, no commentary markers.\n";
        std::fs::write(odir.join("how_to.md"), prose).unwrap();

        let err = scaffold(&surface(), &tdir, &odir, false).unwrap_err();
        match &err {
            ScaffoldError::MarkerMissing { path } => {
                assert_eq!(path.file_name().unwrap(), "how_to.md");
            }
            other => panic!("existing marker-free prose must be refused, got {:?}", other),
        }
        // Typed refusal message carries the stable error string.
        assert!(err.to_string().contains("REFUSED:SCAFFOLD_MARKER_MISSING"));
        // Refusal is all-or-nothing: the pre-existing prose is byte-identical.
        assert_eq!(std::fs::read(odir.join("how_to.md")).unwrap(), prose.as_bytes());
        assert!(!odir.join("reference.md").exists(), "partial write on refusal");

        // --force escape hatch overwrites (reference.md is fully rigid — no
        // slot — so the marker lives in how_to.md).
        let written = scaffold(&surface(), &tdir, &odir, true).unwrap();
        assert_eq!(written.len(), OUTPUTS.len());
        assert!(std::fs::read_to_string(odir.join("how_to.md"))
            .unwrap()
            .contains(COMMENTARY_BEGIN));
        std::fs::remove_dir_all(&dir).ok();
    }

    #[test]
    fn scaffold_empty_existing_file_is_treated_as_fresh() {
        let dir = std::env::temp_dir().join(format!("doc-hdit-empty-existing-{}", std::process::id()));
        let tdir = dir.join("templates");
        let odir = dir.join("docs");
        std::fs::create_dir_all(&tdir).unwrap();
        let templates =
            std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("templates");
        for f in ["reference.md.tera", "how_to.md.tera", "explanation.md.tera"] {
            std::fs::copy(templates.join(f), tdir.join(f)).unwrap();
        }
        std::fs::create_dir_all(&odir).unwrap();
        std::fs::write(odir.join("how_to.md"), "").unwrap();
        scaffold(&surface(), &tdir, &odir, false).unwrap();
        assert!(std::fs::read_to_string(odir.join("how_to.md"))
            .unwrap()
            .contains(COMMENTARY_BEGIN));
        std::fs::remove_dir_all(&dir).ok();
    }
}
