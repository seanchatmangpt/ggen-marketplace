from pathlib import Path

PACK = Path(__file__).parents[1]
GENERATION_QUERIES = (
    "queries/20-five-axis-realization-plan.rq",
    "queries/21-consumer-realization-cross-product.rq",
    "queries/22-reversible-cross-product.rq",
    "queries/24-authority-transition-frontier.rq",
    "queries/25-frontier-cardinality.rq",
)


def test_generation_select_queries_have_deterministic_ordering():
    missing = []
    for relative in GENERATION_QUERIES:
        text = (PACK / relative).read_text()
        if "SELECT" in text.upper() and "ORDER BY" not in text.upper():
            missing.append(relative)
    assert missing == [], f"generation SELECT queries missing ORDER BY: {missing}"
