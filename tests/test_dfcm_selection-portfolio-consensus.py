"""Absorbed family tests: dfcm-selection-portfolio-consensus-pack algorithms preserved under families/selection-portfolio-consensus.

Runs the family's preserved suite in a subprocess with cwd=the family module
root: identical sys.path/sys.modules semantics to the satellite's own
`python -m unittest discover` (families share module names like
scripts.receipt; one pytest process must not shadow them).
"""
import subprocess
import sys
from pathlib import Path

FAMILY = Path(__file__).resolve().parents[1] / "packs" / "dfcm-pack" / "families" / "selection-portfolio-consensus"


def test_family_algorithm_court():
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
        cwd=FAMILY, capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
