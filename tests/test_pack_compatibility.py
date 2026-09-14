"""Chicago-style tests for scripts/check_pack_compatibility.py.

No mocks: loads the real ontology.ttl on disk, calls the real
packaging.specifiers/packaging.version machinery, and asserts on real
returned/raised state -- never on "was this called."
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_pack_compatibility import (  # noqa: E402
    IncompatibleError,
    check,
    check_one,
    load_matrix,
)


def test_load_matrix_reads_real_ontology_individuals():
    matrix = load_matrix()
    assert "ggen_runtime" in matrix
    assert "reactor" in matrix
    assert "spark" in matrix
    assert matrix["reactor"].requirement == ">=1.0.6,<2.0.0"
    assert matrix["reactor"].bound_by_pack == "ash-runtime-integration-contract-pack"


def test_check_one_accepts_a_real_compatible_version():
    matrix = load_matrix()
    # Must not raise.
    check_one("reactor", "1.0.6", matrix)
    check_one("reactor", "1.5.0", matrix)


def test_check_one_refuses_a_real_incompatible_version():
    matrix = load_matrix()
    with pytest.raises(IncompatibleError) as exc_info:
        check_one("reactor", "2.0.0", matrix)
    assert exc_info.value.component == "reactor"
    assert "does not satisfy requirement" in exc_info.value.reason


def test_check_one_refuses_an_unknown_component():
    matrix = load_matrix()
    with pytest.raises(IncompatibleError) as exc_info:
        check_one("some_totally_unknown_component", "1.0.0", matrix)
    assert "unknown component" in exc_info.value.reason


def test_check_one_refuses_an_unparseable_version_string():
    matrix = load_matrix()
    with pytest.raises(IncompatibleError) as exc_info:
        check_one("reactor", "not-a-version", matrix)
    assert "unparseable version string" in exc_info.value.reason


def test_ggen_runtime_bound_normalizes_the_real_v_prefixed_release_tag():
    # marketplace.toml's own real [ggen].version = "v26.8.11" convention.
    matrix = load_matrix()
    check_one("ggen_runtime", "v26.8.11", matrix)  # must not raise
    with pytest.raises(IncompatibleError):
        check_one("ggen_runtime", "v27.0.0", matrix)


def test_check_multiple_components_first_violation_wins_deterministically():
    matrix = load_matrix()
    with pytest.raises(IncompatibleError) as exc_info:
        # "reactor" sorts before "spark" -- the reactor violation must be
        # the one raised, matching BeamPM.Pro.Compatibility.check/1's
        # documented sorted-order, first-violation-halt behavior.
        check({"spark": "3.5.0", "reactor": "9.9.9"}, matrix)
    assert exc_info.value.component == "reactor"


def test_check_all_compatible_returns_none():
    matrix = load_matrix()
    assert check({"reactor": "1.0.6", "spark": "2.7.2"}, matrix) is None


def test_cli_check_flag_real_subprocess_compatible():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check_pack_compatibility.py"),
         "--check", "reactor=1.0.6"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert result.returncode == 0
    assert "compatible: reactor=1.0.6" in result.stdout


def test_cli_check_flag_real_subprocess_incompatible():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check_pack_compatibility.py"),
         "--check", "reactor=99.0.0"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert result.returncode == 1
    assert "REFUSED:INCOMPATIBLE:reactor:" in result.stderr


def test_cli_matrix_flag_real_subprocess():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check_pack_compatibility.py"), "--matrix"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert result.returncode == 0
    assert "reactor: >=1.0.6,<2.0.0" in result.stdout
