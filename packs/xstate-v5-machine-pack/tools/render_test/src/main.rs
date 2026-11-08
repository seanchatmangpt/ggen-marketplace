//! render_test — real tera render court for the xstate-v5-machine-pack templates.
//!
//! Renders both pack templates with the documented test variables (the same
//! var surface S2's mental render test enumerated) and writes the output to
//! disk so the construct gate can consume the machine. Exit 0 = both templates
//! rendered; any tera parse/render error exits non-zero.

use std::path::PathBuf;

use serde_json::Value;

fn main() {
    let pack_dir = std::env::args()
        .nth(1)
        .expect("usage: render_test <pack-dir> <vars.json> <out-dir>");
    let vars_path = std::env::args()
        .nth(2)
        .expect("usage: render_test <pack-dir> <vars.json> <out-dir>");
    let out_dir = std::env::args()
        .nth(3)
        .expect("usage: render_test <pack-dir> <vars.json> <out-dir>");

    let pack_dir = PathBuf::from(pack_dir);
    let out_dir = PathBuf::from(&out_dir);
    std::fs::create_dir_all(&out_dir).expect("create out dir");

    let vars: Value =
        serde_json::from_str(&std::fs::read_to_string(&vars_path).expect("read vars")).expect("parse vars");
    let obj = vars.as_object().expect("vars must be a JSON object");
    let ctx =
        tera::Context::from_serialize(&vars).expect("vars must serialize into tera Context");

    for tmpl in ["machine.tera.tmpl", "smoke.tera.tmpl"] {
        let src = pack_dir.join("templates").join(tmpl);
        let mut tera = tera::Tera::default();
        tera.add_template_file(&src, Some(tmpl))
            .unwrap_or_else(|e| panic!("tera parse {tmpl}: {e}"));
        let rendered = tera
            .render(tmpl, &ctx)
            .unwrap_or_else(|e| panic!("tera render {tmpl}: {e}"));
        let out_path = out_dir.join(tmpl.trim_end_matches(".tera.tmpl")).with_extension("ts");
        std::fs::write(&out_path, &rendered).expect("write rendered");
        println!(
            "RENDERED {} -> {} ({} bytes)",
            tmpl,
            out_path.display(),
            rendered.len()
        );
        let _ = obj;
    }
    println!("render_test: exit 0 (both templates rendered)");
}
