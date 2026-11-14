"""Non-vacuity court: typer-azure-pack gates pass on the committed ontology
and refuse a copy with a required-option property removed."""
import pathlib
import re
import subprocess
import sys

PACK = pathlib.Path(__file__).resolve().parent.parent / "packs" / "typer-azure-pack"
RUNNER = PACK / "gates" / "run_gates.py"
ONTO = PACK / "ontology.ttl"


def run(onto):
    return subprocess.run([sys.executable, str(RUNNER), str(onto)],
                          capture_output=True, text=True)


def test_committed_passes():
    r = run(ONTO)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ALL_GATES_PASS" in r.stdout


def test_mutated_required_option_refused(tmp_path):
    text = ONTO.read_text()
    mutated, n = re.subn(r'\n\s*typer:required "true"\^\^xsd:boolean ;', "", text, count=1)
    assert n == 1
    m = tmp_path / "ontology.ttl"
    m.write_text(mutated)
    r = run(m)
    assert r.returncode != 0, r.stdout
    assert "GATE_REFUSAL" in r.stdout


def test_mutated_subapp_field_refused(tmp_path):
    text = ONTO.read_text()
    mutated, n = re.subn(r'\n\s*typer:apiVersion\s+"[^"]*"\s*[;.]?', "", text, count=1)
    assert n == 1, "no apiVersion literal pattern to mutate"
    m = tmp_path / "ontology.ttl"
    m.write_text(mutated)
    r = run(m)
    assert r.returncode != 0
    assert "GATE_REFUSAL" in r.stdout, r.stdout + r.stderr
