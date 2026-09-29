"""Standing generator and merge guard, against real files and a real temp git repo."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STANDING = ROOT / "scripts/standing.py"
GUARD = ROOT / "scripts/merge_guard.py"


def run(*cmd: str, cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
        cwd=repo, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / "f.txt").write_text("".join(f"line{i}\n" for i in range(1, 11)))
    git(repo, "add", "."); git(repo, "commit", "-qm", "base")
    return repo


def edit(repo: Path, changes: dict[int, str]) -> None:
    lines = (repo / "f.txt").read_text().splitlines()
    for n, text in changes.items():
        lines[n - 1] = text
    (repo / "f.txt").write_text("\n".join(lines) + "\n")


def test_standing_check_fresh_and_detects_staleness(tmp_path):
    # Isolated: operate on temp copies so other lanes changing the pack tree cannot flake this.
    copy = tmp_path / "standing.md"
    copy.write_text((ROOT / "docs/context/standing.md").read_text())
    assert run(sys.executable, str(STANDING), "--target", str(copy)).returncode == 0
    assert run(sys.executable, str(STANDING), "--target", str(copy), "--check").returncode == 0
    text = copy.read_text()
    assert "<!-- GENERATED:standing -->" in text and "Pack count:" in text
    assert "Historical" in text
    copy.write_text(text.replace("Pack count:", "Pack count: 1", 1))
    res = run(sys.executable, str(STANDING), "--target", str(copy), "--check")
    assert res.returncode == 1 and "STANDING_STALE" in res.stderr


def test_standing_committed_docs_have_markers():
    for rel in ("docs/context/standing.md", "docs/reference/standing.md"):
        text = (ROOT / rel).read_text()
        assert "<!-- GENERATED:standing -->" in text and "<!-- /GENERATED:standing -->" in text


def test_standing_is_deterministic():
    a = run(sys.executable, str(STANDING), "--check", "--sha", "0" * 40)
    # a differing explicit SHA is compared and must be reported stale
    assert a.returncode == 1 and "STANDING_STALE" in a.stderr


def test_merge_guard_flags_ours_drop(tmp_path):
    repo = make_repo(tmp_path)
    git(repo, "checkout", "-qb", "theirs")
    edit(repo, {2: "theirs-change", 8: "theirs-eight"})
    git(repo, "commit", "-qam", "theirs")
    git(repo, "checkout", "-q", "main")
    edit(repo, {2: "ours-change"})
    git(repo, "commit", "-qam", "ours")
    git(repo, "merge", "-q", "-X", "ours", "theirs", "-m", "merge")
    merged = (repo / "f.txt").read_text()
    assert "theirs-eight" in merged and "theirs-change" not in merged
    res = run(sys.executable, str(GUARD), "HEAD", "--repo", str(repo))
    assert res.returncode == 1, res.stdout + res.stderr
    assert "DROPPED f.txt" in res.stdout and "theirs-change" in res.stdout
    allow = tmp_path / "allow.txt"
    allow.write_text("# accepted\nf.txt\n")
    ok = run(sys.executable, str(GUARD), "HEAD", "--repo", str(repo), "--allow", str(allow))
    assert ok.returncode == 0 and "ALLOWED f.txt" in ok.stdout


def test_merge_guard_passes_clean_merge(tmp_path):
    repo = make_repo(tmp_path)
    git(repo, "checkout", "-qb", "theirs")
    edit(repo, {8: "theirs-eight"})
    git(repo, "commit", "-qam", "theirs")
    git(repo, "checkout", "-q", "main")
    edit(repo, {2: "ours-two"})
    git(repo, "commit", "-qam", "ours")
    git(repo, "merge", "-q", "theirs", "-m", "merge")
    res = run(sys.executable, str(GUARD), "HEAD", "--repo", str(repo))
    assert res.returncode == 0, res.stdout + res.stderr


def test_merge_guard_refuses_non_merge(tmp_path):
    repo = make_repo(tmp_path)
    res = run(sys.executable, str(GUARD), "HEAD", "--repo", str(repo))
    assert res.returncode != 0 and "NOT_A_MERGE" in res.stderr
