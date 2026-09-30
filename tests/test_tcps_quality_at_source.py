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
    # The R75-R77 structural-factory courts run as rows of ci/courts.toml inside the
    # `courts` job of ci.yml; the job owns the temporal bound (ANDON_WORKFLOW_TIMEOUT_MISSING).
    import tomllib

    courts = {c["id"] for c in tomllib.loads((ROOT / "ci/courts.toml").read_text())["court"]}
    for court in (
        "measure-r75-throughput-learning",
        "measure-r76-portfolio-structural-census",
        "measure-r77-repository-universe",
    ):
        assert court in courts, f"ANDON_COURT_MISSING:{court}"
    ci = (ROOT / ".github/workflows/ci.yml").read_text()
    jobs = ci.split("\n  courts:\n", 1)[1].split("\n  tests:\n", 1)[0]
    assert "runs-on:" in jobs and "timeout-minutes:" in jobs, "ANDON_WORKFLOW_TIMEOUT_MISSING:courts"
