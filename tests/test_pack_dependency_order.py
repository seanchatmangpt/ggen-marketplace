"""Chicago-style tests for scripts/pack_dependency_order.py.

No mocks: real file reads, real recursive DFS execution, real subprocess CLI
invocations, asserted on real returned state.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pack_dependency_order import (  # noqa: E402
    DependencyCycleError,
    DependencyNotFoundError,
    dependency_order,
    load_graph_from_ontology,
)


def test_load_graph_from_ontology_reads_the_real_reactor_spark_edge():
    graph = load_graph_from_ontology()
    assert "reactor" in graph
    assert "spark" in graph
    assert graph["reactor"] == ["spark"]
    assert graph["spark"] == []


def test_dependency_order_puts_the_real_dependency_before_its_dependent():
    graph = load_graph_from_ontology()
    order = dependency_order(graph)
    assert order.index("spark") < order.index("reactor")


def test_dependency_order_is_deterministic_across_repeated_calls():
    graph = load_graph_from_ontology()
    first = dependency_order(graph)
    second = dependency_order(graph)
    assert first == second


def test_dependency_order_handles_a_diamond_shape():
    # Synthetic test fixture (not marketplace data): a -> b, a -> c, b -> d, c -> d.
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    order = dependency_order(graph)
    assert order.index("d") < order.index("b")
    assert order.index("d") < order.index("c")
    assert order.index("b") < order.index("a")
    assert order.index("c") < order.index("a")


def test_dependency_order_refuses_a_real_cycle():
    # Synthetic test fixture: a -> b -> c -> a.
    graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
    with pytest.raises(DependencyCycleError) as exc_info:
        dependency_order(graph)
    assert exc_info.value.node_id in graph


def test_dependency_order_refuses_a_missing_dependency():
    graph = {"a": ["nonexistent"]}
    with pytest.raises(DependencyNotFoundError) as exc_info:
        dependency_order(graph)
    assert exc_info.value.node_id == "nonexistent"


def test_dependency_order_self_loop_is_a_cycle():
    graph = {"a": ["a"]}
    with pytest.raises(DependencyCycleError):
        dependency_order(graph)


def test_dependency_order_empty_graph_returns_empty_order():
    assert dependency_order({}) == []


def test_cli_matrix_flag_real_subprocess():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "pack_dependency_order.py"), "--matrix"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert result.returncode == 0
    assert "reactor: depends on ['spark']" in result.stdout


def test_cli_from_ontology_flag_real_subprocess():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "pack_dependency_order.py"), "--from-ontology"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert result.returncode == 0
    assert "spark" in result.stdout
    assert result.stdout.index("spark") < result.stdout.index("reactor")
