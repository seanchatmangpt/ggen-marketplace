"""Final anti-incest court: graphlaw emits, pm4pytest judges.

The graphlaw OCEL export (real binary, real law session replayed through
LawState::transition) produces an OCEL v2 SQLite trace with activities
{admit, receipt, refuse}. The external pm4pytest CLI judges it — this file
asserts only on real subprocess exit codes and TAP output, never on
graphlaw's own claims.

Trace shape (measured, frozen): one trace of five events,
    admit, receipt, admit, receipt, refuse
so the conformant FSM is the full five-step sequence.

No mocks, no sleeps: real export binary, real pm4pytest subprocess, real
TAP on stdout, real exit codes.
"""

import os
import subprocess
import sys

import pytest

CLI = os.path.join(os.path.dirname(sys.executable), "pm4pytest")

# The export session: two admitted transitions each carrying a receipt,
# then one refusal. Pinned so a silent emitter change fails loudly here.
EXPECTED_SEQUENCE = ["admit", "receipt", "admit", "receipt", "refuse"]

MUTATED_SEQUENCE = ["admit", "receipt", "admit", "receipt", "shipped"]


def run_cli(*args):
    return subprocess.run(
        [CLI, *args], capture_output=True, text=True
    )


@pytest.fixture(scope="module")
def tap_ok(tap_text):
    return "ok 1 -" in tap_text


@pytest.fixture(scope="module")
def tap_text(ocel_trace):
    """Real TAP output of the conformant FSM run against the real trace."""
    fsm = ",".join(EXPECTED_SEQUENCE)
    r = run_cli(
        "check-conformance", "-l", str(ocel_trace), "-f", fsm, "-m", "1.0"
    )
    assert r.returncode == 0, f"conformance failed: {r.stdout} {r.stderr}"
    return r.stdout


def test_export_produced_expected_activities(ocel_trace):
    """The trace on disk carries exactly the pinned activity vocabulary."""
    import sqlite3

    conn = sqlite3.connect(str(ocel_trace))
    try:
        kinds = [
            row[0]
            for row in conn.execute(
                "SELECT ocel_type FROM event ORDER BY ocel_id"
            )
        ]
    finally:
        conn.close()
    assert kinds == EXPECTED_SEQUENCE


def test_conformance_ok(tap_ok, tap_text):
    """pm4pytest judges the real trace conformant: TAP ok, fitness 1.0."""
    assert tap_ok
    assert "fitness: 1.0" in tap_text
    assert "violations: []" in tap_text


def test_conformance_mutation_twin_fails(ocel_trace):
    """Anti-vacuity: swapping 'refuse' for 'shipped' must violate and exit 1."""
    fsm = ",".join(MUTATED_SEQUENCE)
    r = run_cli(
        "check-conformance", "-l", str(ocel_trace), "-f", fsm, "-m", "1.0"
    )
    assert r.returncode == 1
    assert "not ok 1 -" in r.stdout
    assert "PETRI_NET_FITNESS_VIOLATION" in r.stdout


def test_sla_receipt_to_admit_within_bound(ocel_trace):
    """SLA leg: the trace carries real timestamps; receipt -> next admit is
    immediate (same/next second), well inside a 60s bound."""
    r = run_cli("check-sla", "-l", str(ocel_trace), "-s", "receipt:admit:60")
    assert r.returncode == 0, f"SLA check failed: {r.stdout} {r.stderr}"
    assert "ok 1 -" in r.stdout
    assert "violations: []" in r.stdout
