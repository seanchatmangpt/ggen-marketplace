from pathlib import Path
import hashlib
ROOT = Path(__file__).resolve().parents[1]
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def test_one_relation_drives_three_artifacts():
    cfg=(ROOT/"ggen.toml").read_text()
    assert cfg.count('query = { file = "queries/ash-gen-commands.rq" }') == 3
def test_namespace_is_projection_only():
    q=(ROOT/"queries/ash-gen-commands.rq").read_text()
    t=(ROOT/"templates/gen-commands.sh.tmpl").read_text()
    assert "ASH_PROJECTION_NAMESPACE" not in q
    assert "REFUSED:INVALID_ASH_PROJECTION_NAMESPACE" in t
def test_exact_subject_provenance():
    assert "# exact-subject: {{ row.class }}" in (ROOT/"templates/gen-commands.sh.tmpl").read_text()
    assert "dct:source <{{ row.class }}>" in (ROOT/"templates/semantic-map.ttl.tera").read_text()
def test_template_inputs_byte_stable():
    ps=sorted((ROOT/"templates").glob("*"))
    assert [(p.name,digest(p)) for p in ps] == [(p.name,digest(p)) for p in ps]
def test_codegen_names_fail_closed():
    assert "^[A-Za-z][A-Za-z0-9_]*$" in (ROOT/"gates/050_projection_names_safe.rq").read_text()
    assert "COALESCE" in (ROOT/"gates/040_resource_name_collisions.rq").read_text()
