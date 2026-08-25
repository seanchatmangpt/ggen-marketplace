from pathlib import Path

TEMPLATE = Path(__file__).parents[1] / "templates" / "replication-plan.json.tera"


def test_replication_plan_uses_admitted_results_context():
    text = TEMPLATE.read_text()
    assert "for row in results" in text
    assert "for row in rows" not in text
