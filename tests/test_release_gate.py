"""Release gate and preflight: real git repo, real subcommand, no doubles."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import marketplace  # noqa: E402


def run(*args):
    return subprocess.run([sys.executable, str(ROOT / "scripts/marketplace.py"), *args],
                          cwd=ROOT, capture_output=True, text=True)


def test_version_tag_shape():
    assert marketplace.VERSION_TAG.fullmatch("v26.9.29")
    assert not marketplace.VERSION_TAG.fullmatch("26.9.29")
    assert not marketplace.VERSION_TAG.fullmatch("v26.9.29-rc1")


def test_pack_table_allowlist_is_the_ggen_loader_set():
    assert marketplace.PACK_TABLE_KEYS == {"name", "version", "description", "deprecated", "superseded_by"}


def test_release_check_refuses_an_existing_tag():
    current = marketplace.marketplace_version()
    tags = {t for _, t in marketplace.release_tags()}
    result = run("release-check")
    if current in tags:
        assert result.returncode != 0
        assert "RELEASE_TAG_EXISTS" in result.stderr + result.stdout


def test_diff_against_latest_tag_reports_sections():
    tags = marketplace.release_tags()
    if not tags:
        return
    result = run("diff", tags[-1][1])
    assert result.returncode == 0
    for key in ("added=", "removed=", "changed=", "unbumped="):
        assert key in result.stdout


def test_check_refuses_unknown_pack():
    result = run("check", "no-such-pack", "--no-qualify")
    assert result.returncode != 0
    assert "UNKNOWN_PACK" in result.stderr + result.stdout
