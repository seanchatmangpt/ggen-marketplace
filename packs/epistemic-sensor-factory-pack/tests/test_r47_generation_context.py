from pathlib import Path

PACK = Path(__file__).parents[1]


def _assert_results_context(template_name: str):
    text = (PACK / "templates" / template_name).read_text()
    assert "for row in results" in text
    assert "for row in rows" not in text


def test_replication_plan_uses_admitted_results_context():
    _assert_results_context("replication-plan.json.tera")


def test_causal_propagation_plan_uses_admitted_results_context():
    _assert_results_context("causal-propagation-plan.json.tera")
