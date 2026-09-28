from pathlib import Path
ROOT=Path(__file__).parents[1]
def test_family_template_boundary(): assert sorted(p.stem for p in (ROOT/"families").glob("*.ttl"))==sorted(p.stem.replace(".tera","") for p in (ROOT/"templates").glob("*.tera"))
