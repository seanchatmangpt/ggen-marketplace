import json
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


def test_r78_ready_set_generation_is_deterministic_at_execution_edge():
    query = ROOT / "packs/portfolio-epistemic-observability-pack/queries/r78-tcps-ready-set/050_clean_allocation_crown.rq"
    text = query.read_text()
    assert "SELECT " in text
    assert "ORDER BY " in text, "POKAYOKE_NONDETERMINISTIC_SELECT:r78-tcps-ready-set-capital-plan"
    assert "DESC(?score)" in text, "POKAYOKE_LINEAR_EXTENSION_MUST_USE_SELECTION_SCORE"


def test_structural_factory_courts_are_temporally_bounded():
    # These courts run inside ci.yml's `verify` job via ci/courts.json; each
    # entry carries its own bound, enforced by scripts/ci_plan.py.
    courts = {c["name"]: c for c in json.loads((ROOT / "ci/courts.json").read_text())}
    for name in (
        "measure-r75-throughput-learning",
        "measure-r76-portfolio-structural-census",
        "measure-r77-repository-universe",
    ):
        assert name in courts, f"ANDON_COURT_MISSING:{name}"
        assert courts[name]["timeout_minutes"] > 0, f"ANDON_COURT_TIMEOUT_MISSING:{name}"
        assert (ROOT / "ci/courts" / f"{name}.sh").is_file(), f"ANDON_COURT_SCRIPT_MISSING:{name}"
