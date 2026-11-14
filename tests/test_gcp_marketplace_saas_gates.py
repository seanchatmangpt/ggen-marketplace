"""Court: gcp-marketplace-saas-pack gates execute, and are non-vacuous."""
import os
import re
import subprocess
import sys
import tempfile

import pytest

PACK = os.path.join(os.path.dirname(__file__), "..", "packs", "gcp-marketplace-saas-pack")
GATES = os.path.join(PACK, "gates")
sys.path.insert(0, GATES)
import run_gates  # noqa: E402

STEMS = sorted(os.path.splitext(f)[0] for f in os.listdir(GATES) if f.endswith(".rq"))


def _gate(stem):
    return os.path.join(GATES, stem + ".rq")


def _w(kind, stem):
    return os.path.join(PACK, "witnesses", kind, stem + ".ttl")


def test_three_gates_present():
    assert len(STEMS) == 3


@pytest.mark.parametrize("stem", STEMS)
def test_gate_passes_real_ontology(stem):
    assert run_gates.rows_for(_gate(stem), os.path.join(PACK, "ontology.ttl")) == []


@pytest.mark.parametrize("stem", STEMS)
def test_gate_pass_witness_clean(stem):
    assert run_gates.rows_for(_gate(stem), _w("pass", stem)) == []


@pytest.mark.parametrize("stem", STEMS)
def test_gate_fail_witness_refused(stem):
    assert run_gates.rows_for(_gate(stem), _w("fail", stem)) != []


def test_runner_exit_zero():
    assert run_gates.main(["--witnesses"]) == 0


def test_mutation_removing_filter_flips_020():
    src = open(_gate("020_entitlement_states")).read()
    mutated, n = re.subn(r"FILTER\(\?s != \?s2\)", "", src)
    assert n == 1
    with tempfile.NamedTemporaryFile("w", suffix=".rq", delete=False) as fh:
        fh.write(mutated)
    try:
        # with the FILTER gone, a self-join matches every state: real ontology now refused
        assert run_gates.rows_for(fh.name, os.path.join(PACK, "ontology.ttl")) != []
    finally:
        os.unlink(fh.name)
