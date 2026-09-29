"""The first-pack tutorial must execute for real: real ggen, real files, no mocks."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_quickstart.py"

needs_ggen = pytest.mark.skipif(shutil.which("ggen") is None, reason="ggen not installed (scripts/install-ggen.sh)")


@needs_ggen
def test_quickstart_runs_end_to_end() -> None:
    result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, timeout=600)
    assert result.returncode == 0, result.stdout[-1500:] + result.stderr[-1500:]
    assert "QUICKSTART_OK" in result.stdout


def test_example_pack_manifest_admits_only_allowed_keys() -> None:
    import tomllib

    manifest = tomllib.loads((ROOT / "examples/hello-pack/pack/pack.toml").read_text(encoding="utf-8"))
    assert set(manifest) == {"pack"}
    assert set(manifest["pack"]) <= {"name", "version", "description", "deprecated", "superseded_by"}


def test_tutorial_blocks_match_example() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import run_quickstart

    blocks = run_quickstart.tutorial_blocks()
    for name, relative in run_quickstart.TUTORIAL_FILES.items():
        assert blocks[name] == (ROOT / "examples/hello-pack" / relative).read_text(encoding="utf-8")


def test_quickstart_fails_when_ggen_absent(tmp_path: Path) -> None:
    import os

    env = {**os.environ, "PATH": str(tmp_path)}
    result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, env=env)
    assert result.returncode != 0
    assert "ggen not on PATH" in result.stderr
