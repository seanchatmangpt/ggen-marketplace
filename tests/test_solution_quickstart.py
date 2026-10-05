"""Chicago-style court for scripts/run_solution_quickstart.py.

Real collaborators only: the real commerce sim subprocess on an ephemeral
port, the real deployer subprocess (real ggen sync, real SPARQL gates, real
hash-chained paid-delivery receipts), real capsule files. No mocks.

Pins:
- enterprise profile exits 0 with a receipt chain hash in the summary;
- team profile exits 0 too (its enum values are inside the tailoring pack's
  closed enumeration);
- the sim is killed in teardown;
- the repo tree is untouched (solutions/ stays git-clean across the run).
"""
from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_solution_quickstart.py"

needs_ggen = pytest.mark.skipif(
    shutil.which("ggen") is None, reason="ggen not installed (scripts/install-ggen.sh)"
)


def _git_status_solutions() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain", "--", "solutions"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout


def _run_quickstart(*cli_args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *cli_args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=600,
    )


def _summary(stdout: str) -> dict:
    return json.loads(stdout)


@needs_ggen
def test_happy_path_enterprise_exits_zero_with_chain_hash():
    before = _git_status_solutions()
    result = _run_quickstart("--profile", "enterprise")
    after = _git_status_solutions()
    assert result.returncode == 0, result.stderr[-1500:]
    summary = _summary(result.stdout)
    assert summary["slug"] == "enterprise-aaif"
    assert len(summary["receipt_chain_hash"]) == 64
    assert summary["dist_files"] >= 1
    assert isinstance(summary["sim_port"], int)
    assert after == before, "solutions/ mutated"


@needs_ggen
def test_team_profile_also_exits_zero():
    before = _git_status_solutions()
    result = _run_quickstart("--profile", "team")
    after = _git_status_solutions()
    assert result.returncode == 0, result.stderr[-1500:]
    summary = _summary(result.stdout)
    assert len(summary["receipt_chain_hash"]) == 64
    assert after == before, "solutions/ mutated"


@needs_ggen
def test_sim_is_killed_in_teardown():
    result = _run_quickstart("--profile", "enterprise")
    assert result.returncode == 0, result.stderr[-1500:]
    port = _summary(result.stdout)["sim_port"]
    # The ephemeral listener must be gone: connecting must now be refused.
    deadline = time.time() + 10
    last = None
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                last = "still listening"
        except OSError:
            return  # connection refused = teardown witnessed
        time.sleep(0.2)
    pytest.fail(f"sim still listening on {port} after exit: {last}")


@needs_ggen
def test_missing_ggen_is_typed_refusal():
    """Without ggen on PATH the run fails with a typed REFUSED line, never a
    bare traceback."""
    import os

    stripped = {k: v for k, v in os.environ.items() if k != "PATH"}
    stripped["PATH"] = ""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        env=stripped,
    )
    assert result.returncode == 7
    assert "REFUSED:GGEN_NOT_FOUND" in result.stderr
    assert "Traceback" not in result.stderr
