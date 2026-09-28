from pathlib import Path
ROOT=Path(__file__).parents[1]
def test_templates_are_authority_fenced():
    for p in (ROOT/"templates").glob("*.tera"):
        assert "authority=NONE" in p.read_text()
