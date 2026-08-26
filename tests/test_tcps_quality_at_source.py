from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_r75_throughput_generation_is_deterministic_at_source():
    query = ROOT / "packs/epistemic-sensor-factory-pack/queries/r75-throughput-learning/039_throughput_learning_projection.rq"
    text = query.read_text()
    assert "SELECT " in text
    assert "ORDER BY " in text, "POKAYOKE_NONDETERMINISTIC_SELECT:r75-throughput-learning-plan"


def test_r76_structural_census_generation_is_deterministic_at_source():
    query = ROOT / "packs/portfolio-epistemic-observability-pack/queries/r76-structural-census/050_clean_structural_frontier.rq"
    text = query.read_text()
    assert "SELECT " in text
    assert "ORDER BY " in text, "POKAYOKE_NONDETERMINISTIC_SELECT:r76-portfolio-structural-census"


def test_r77_repository_universe_generation_is_deterministic_at_source():
    query = ROOT / "packs/portfolio-epistemic-observability-pack/queries/r77/50-clean-repository-universe-frontier.rq"
    text = query.read_text()
    assert "SELECT " in text
    assert "ORDER BY " in text, "POKAYOKE_NONDETERMINISTIC_SELECT:r77-exact-repository-universe-frontier"


def test_structural_factory_workflows_are_temporally_bounded():
    workflows = [
        ROOT / ".github/workflows/measure-r75-throughput-learning.yml",
        ROOT / ".github/workflows/measure-r76-portfolio-structural-census.yml",
        ROOT / ".github/workflows/measure-r77-repository-universe.yml",
    ]
    for workflow in workflows:
        text = workflow.read_text()
        assert "runs-on:" in text
        assert "timeout-minutes:" in text, f"ANDON_WORKFLOW_TIMEOUT_MISSING:{workflow.name}"
