from pathlib import Path
R=Path(__file__).parents[1]
def test_refusal_queries_fail_closed():
 assert '!= "NONE"' in (R/"queries/refuse_authority_smuggling.rq").read_text()
 assert "FILTER NOT EXISTS" in (R/"queries/refuse_missing_dual.rq").read_text()
