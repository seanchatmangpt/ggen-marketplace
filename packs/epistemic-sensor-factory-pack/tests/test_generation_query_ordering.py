from pathlib import Path

PACK = Path(__file__).parents[1]
GENERATION_QUERIES = (
    "queries/010_sensor_specs.rq",
    "queries/260_replication_targets.rq",
    "queries/400_evidence_return_protocol.rq",
    "queries/610_causal_propagation_plan.rq",
)


def test_generation_select_queries_have_deterministic_ordering():
    missing = []
    for relative in GENERATION_QUERIES:
        text = (PACK / relative).read_text()
        if "SELECT" in text.upper() and "ORDER BY" not in text.upper():
            missing.append(relative)
    assert missing == [], f"generation SELECT queries missing ORDER BY: {missing}"
