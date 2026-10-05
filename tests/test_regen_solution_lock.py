"""Chicago tests for scripts/regen_solution_lock.py.

Real collaborators only: each test copies the real solution tree plus the
real pack dirs into a tmp dir (mirroring the repo layout the lock's relative
pack paths expect) and runs the real CLI as a subprocess.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import marketplace  # noqa: E402

SCRIPT = REPO / "scripts" / "regen_solution_lock.py"
SOLUTION_REL = Path("solutions/enterprise-aaif")
PACK_RELS = [
    Path("packs/aaif-vanilla-pack"),
    Path("packs/aaif-profile-tailoring-pack"),
]


def _make_tmp_solution(tmp_path: Path) -> Path:
    """Copy the real solution + its pack inputs into tmp, repo layout."""
    for rel in [SOLUTION_REL, *PACK_RELS]:
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(REPO / rel, dest)
    return tmp_path / SOLUTION_REL


def _run(solution_dir: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--solution", str(solution_dir), *extra],
        capture_output=True,
        text=True,
    )


def _pack_files(pack_dir: Path) -> list[Path]:
    return sorted(p for p in pack_dir.rglob("*") if p.is_file())


def test_fresh_solution_check_ok(tmp_path: Path) -> None:
    solution_dir = _make_tmp_solution(tmp_path)
    # The committed hand lock is stale (see test_regen_detects_stale_committed_lock);
    # mint a fresh lock with the tool, then check.
    assert _run(solution_dir).returncode == 0
    result = _run(solution_dir, "--check")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK lock fresh" in result.stdout


def test_stale_lock_refused(tmp_path: Path) -> None:
    solution_dir = _make_tmp_solution(tmp_path)
    assert _run(solution_dir).returncode == 0
    lock_path = solution_dir / "solution.json"
    lock = json.loads(lock_path.read_text())
    lock["packs"][0]["content_hash"] = "sha256:" + "0" * 64
    lock_path.write_text(json.dumps(lock, indent=2) + "\n")
    result = _run(solution_dir, "--check")
    assert result.returncode == 9
    assert "REFUSED:LOCK_STALE" in result.stdout
    assert "pack aaif-vanilla-pack:" in result.stdout


def test_pack_drift_check_refuses_with_diff(tmp_path: Path) -> None:
    solution_dir = _make_tmp_solution(tmp_path)
    assert _run(solution_dir).returncode == 0
    pack_dir = solution_dir / "../../packs/aaif-vanilla-pack"
    target = pack_dir / "fixtures" / "enterprise_agent.ttl"
    target.write_text(target.read_text() + "\n# drifted\n")
    result = _run(solution_dir, "--check")
    assert result.returncode == 9
    assert "REFUSED:LOCK_STALE" in result.stdout
    assert "pack aaif-vanilla-pack:" in result.stdout


def test_regen_writes_fresh_lock(tmp_path: Path) -> None:
    solution_dir = _make_tmp_solution(tmp_path)
    (solution_dir / "ontology.ttl").write_text(
        (solution_dir / "ontology.ttl").read_text() + "\n# drifted\n"
    )
    result = _run(solution_dir)
    assert result.returncode == 0, result.stdout + result.stderr
    new_lock = json.loads((solution_dir / "solution.json").read_text())
    assert new_lock["schema"] == "aaif-solution-lock/v1"
    assert [p["name"] for p in new_lock["packs"]] == [
        "aaif-vanilla-pack",
        "aaif-profile-tailoring-pack",
    ]
    # Independent recomputation: profile via the deployer fold, pack hashes
    # via fingerprint_paths over pack inputs with the same exclusion law.
    from deploy_aaif_solution import input_folds

    profile, _ = input_folds(solution_dir, new_lock)
    assert new_lock["profile_sha256"] == profile
    state = {".ggen", ".ggen-v2", ".clap-noun-verb"}
    for pack in new_lock["packs"]:
        pack_path = (solution_dir / pack["path"]).resolve()
        files = [
            f
            for f in pack_path.rglob("*")
            if f.is_file()
            and "dist" not in f.relative_to(pack_path).parts
            and not (set(f.relative_to(pack_path).parts) & state)
        ]
        assert pack["content_hash"] == "sha256:" + marketplace.fingerprint_paths(
            files, pack_path
        )
    # idempotent: a regen over a fresh lock is a no-op diff
    again = _run(solution_dir)
    assert again.returncode == 0
    assert "no changes" in again.stdout


def test_runtime_state_dirs_excluded(tmp_path: Path) -> None:
    solution_dir = _make_tmp_solution(tmp_path)
    assert _run(solution_dir).returncode == 0
    # runtime state in BOTH the solution dir and the pack trees must not move
    # the lock: mint the lock, create runtime state, check stays fresh.
    for state in (".ggen", ".ggen-v2", ".clap-noun-verb"):
        (solution_dir / state / "cache.bin").parent.mkdir()
        (solution_dir / state / "cache.bin").write_bytes(b"runtime")
    (solution_dir / "dist" / "out.yaml").parent.mkdir()
    (solution_dir / "dist" / "out.yaml").write_bytes(b"out")
    pack_dir = solution_dir / "../../packs/aaif-vanilla-pack"
    (pack_dir / "dist" / "artifact.yaml").parent.mkdir(parents=True, exist_ok=True)
    (pack_dir / "dist" / "artifact.yaml").write_bytes(b"out")
    (pack_dir / ".clap-noun-verb" / "ocel.json").parent.mkdir(parents=True, exist_ok=True)
    (pack_dir / ".clap-noun-verb" / "ocel.json").write_bytes(b"{}")
    result = _run(solution_dir, "--check")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK lock fresh" in result.stdout


def test_check_does_not_write(tmp_path: Path) -> None:
    solution_dir = _make_tmp_solution(tmp_path)
    assert _run(solution_dir).returncode == 0
    before = (solution_dir / "solution.json").read_bytes()
    pack_dir = solution_dir / "../../packs/aaif-profile-tailoring-pack"
    target = pack_dir / "fixtures" / "marketplace_agent.ttl"
    if not target.exists():
        target = _pack_files(pack_dir)[0]
    target.write_text(target.read_text() + "\n# drifted\n")
    assert _run(solution_dir, "--check").returncode == 9
    assert (solution_dir / "solution.json").read_bytes() == before
