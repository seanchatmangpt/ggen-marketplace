from pathlib import Path
ROOT=Path(__file__).parents[1]
def test_family_sources_have_queries():
    for p in (ROOT/"families").glob("*.ttl"):
        assert (ROOT/"queries"/"families"/(p.stem+".rq")).exists()
