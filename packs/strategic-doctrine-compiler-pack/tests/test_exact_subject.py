from pathlib import Path
R=Path(__file__).parents[1]
def test_all_operator_files_use_canonical_subject_namespace():
 for p in (R/"operators").glob("*.ttl"):
  t=p.read_text(); assert "https://ggen.dev/ontology/strategic-doctrine#" in t; assert 'sd:authority "NONE"' in t
