"""Resolve graphlaw binaries from /Users/sac/graphlaw/target/debug/ (build if missing).

Chicago: everything below runs real subprocesses against real on-disk fixtures.
No mocks, no sleeps.
"""

import os
import subprocess
import sys

# Env overrides let CI (and any lane) point at a different checkout /
# CARGO_TARGET_DIR without editing this file. Local default: the canonical
# graphlaw checkout at target/debug.
REPO = os.environ.get("GRAPHLAW_REPO", "/Users/sac/graphlaw")
TARGET = os.environ.get("GRAPHLAW_TARGET_DIR", os.path.join(REPO, "target", "debug"))

BINS = {
    "graphlaw-verify": ["--bins"],
    "graphlaw_ocel_export": ["--bins"],
    "smon-transcript-to-turtle": ["--bins", "--features", "pack-tools"],
    "smon-broaden-topic": ["--bins", "--features", "pack-tools"],
}
FIXTURE_EXAMPLE = "blackbox_fixture"


def bin_path(name):
    return os.path.join(TARGET, name)


def _built(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)


def pytest_configure(config):
    # Always run the incremental cargo build: a stale binary on disk is not a
    # fresh one, and mtime sniffing rust artifacts is a trap (cargo handles
    # freshness correctly and a no-op build is cheap). Missing binaries are
    # still detected so the error message names what was absent.
    missing = [n for n in BINS if not _built(bin_path(n))]
    cmds = [
        ["cargo", "build", "--bins", "--features", "pack-tools"],
        ["cargo", "build", "--example", FIXTURE_EXAMPLE],
    ]
    if missing:
        sys.stderr.write(
            "conftest: missing binaries (building all): %s\n" % ", ".join(missing)
        )
    for args in cmds:
        r = subprocess.run(
            args, cwd=REPO, capture_output=True, text=True
        )
        if r.returncode != 0:
            sys.stderr.write(r.stdout + r.stderr)
            raise SystemExit(f"conftest: build failed: {' '.join(args)}")


def _features_for(name):
    if name in ("smon-transcript-to-turtle", "smon-broaden-topic"):
        return ["pack-tools"]
    return []


def make_fixture(outdir):
    """Run the blackbox_fixture example: a real admitted plan + signed receipt
    store on disk. Prints the trusted public key hex as its last stdout line."""
    r = subprocess.run(
        [os.path.join(TARGET, "examples", FIXTURE_EXAMPLE), outdir],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"fixture build failed: {r.stdout} {r.stderr}"
    return r.stdout.strip().splitlines()[-1].strip()


# ---------------------------------------------------------------- fixtures
# Pytest-visible fixtures wrapping the helpers above, so test modules never
# need a bare `from conftest import ...` (unresolvable to static analysis).

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def verify_bin():
    """Path to the real graphlaw-verify binary (built in pytest_configure)."""
    return bin_path("graphlaw-verify")


@pytest.fixture(scope="session")
def ocel_trace(tmp_path_factory):
    """Export a real graphlaw law session as an OCEL v2 SQLite trace.

    Runs the real graphlaw_ocel_export binary (built in pytest_configure via
    `cargo build --bins`) against the canonical law fixtures, producing a
    pm4py-readable OCEL2 SQLite database on disk. Activities are exactly
    {admit, receipt, refuse}; the session replays DeriveN3 + AdmitShacl
    admissions, receipts, and one SHACL refusal through the real
    LawState::transition path.

    Returns the path to the exported .sqlite file."""
    out = tmp_path_factory.mktemp("gl-ocel") / "law_session.ocel.sqlite"
    r = subprocess.run(
        [bin_path("graphlaw_ocel_export"), str(out)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"graphlaw_ocel_export failed: {r.stdout} {r.stderr}"
    assert out.is_file() and out.stat().st_size > 0, f"no trace written: {out}"
    return out


@pytest.fixture(scope="session")
def t2t_bin():
    """Path to the real smon-transcript-to-turtle binary."""
    return bin_path("smon-transcript-to-turtle")


@pytest.fixture(scope="session")
def broaden_bin():
    """Path to the real smon-broaden-topic binary."""
    return bin_path("smon-broaden-topic")


@pytest.fixture()
def store_factory():
    """Factory: build a real admitted plan + signed receipt store in a dir.

    Returns the trusted public key hex for the store it produced."""
    return make_fixture
