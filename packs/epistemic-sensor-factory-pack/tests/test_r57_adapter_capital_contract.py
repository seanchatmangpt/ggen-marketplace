from pathlib import Path

PACK = Path(__file__).parents[1]
QUERY_DIR = PACK / "queries"


def test_r57_query_family_is_contiguous_and_exactly_fifty():
    queries = sorted(
        p for p in QUERY_DIR.glob("*_r57_*.rq")
        if p.name[:3].isdigit() and 751 <= int(p.name[:3]) <= 800
    )
    assert len(queries) == 50
    assert [int(p.name[:3]) for p in queries] == list(range(751, 801))


def test_r57_queries_are_public_semantic_and_non_actuating():
    forbidden = ("kubectl apply", "terraform apply", "aws create", "gcloud create", "az create")
    for path in QUERY_DIR.glob("*_r57_*.rq"):
        text = path.read_text()
        assert "https://ggen.dev/ontology/epistemic-sensor-factory#" in text
        lowered = text.lower()
        assert not any(token in lowered for token in forbidden)
