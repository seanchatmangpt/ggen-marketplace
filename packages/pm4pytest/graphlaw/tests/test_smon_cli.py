"""Port of tests/smon_cli_court.rs — real subprocess courts over the two smon
CLI binaries (`smon-transcript-to-turtle`, `smon-broaden-topic`): help/usage
surfaces, typed argv refusals and one happy-path transcript run against a real
file on disk. No mocks, no sleeps."""

import os
import subprocess

import pytest


def run_bin(binpath, *args):
    env = dict(os.environ)
    env.pop("RUST_LOG", None)
    return subprocess.run(
        [binpath, *args], capture_output=True, text=True, env=env
    )


# ---------------------------------------------------------------- help surfaces


BIN_MARKERS = [("t2t_bin", "--transcript"), ("broaden_bin", "--in-ttl")]


@pytest.mark.parametrize("bin_fixture,marker", BIN_MARKERS)
def test_help_exits_zero_for_both_bins(request, bin_fixture, marker):
    binpath = request.getfixturevalue(bin_fixture)
    r = run_bin(binpath, "--help")
    assert r.returncode == 0, f"stdout={r.stdout}"
    assert marker in r.stdout, f"help must document {marker}, got:\n{r.stdout}"
    # Anti-vacuity twin: prove the assertion bites — the marker really is on
    # stdout, not only on stderr.
    assert marker not in r.stderr


# ------------------------------------------------------------- argv refusals


@pytest.mark.parametrize("bin_fixture", ["t2t_bin", "broaden_bin"])
def test_unknown_flag_exits_one_pointing_at_help(request, bin_fixture):
    binpath = request.getfixturevalue(bin_fixture)
    r = run_bin(binpath, "--wat", "x")
    assert r.returncode == 1, f"stdout={r.stdout!r} stderr={r.stderr!r}"
    assert "see --help" in r.stderr, r.stderr
    # Anti-vacuity: help text must NOT appear on the failure path's stdout.
    assert "Usage:" not in r.stdout, r.stdout


def test_flag_as_value_is_refused(t2t_bin):
    # `--transcript --out x`: the value slot holds another flag.
    r = run_bin(t2t_bin, "--transcript", "--out", "x")
    assert r.returncode == 1, f"stdout={r.stdout!r} stderr={r.stderr!r}"
    assert "needs a value" in r.stderr and "--out" in r.stderr, r.stderr


def test_missing_transcript_file_names_the_path(tmp_path, t2t_bin):
    missing = tmp_path / "nope.jsonl"
    r = run_bin(t2t_bin, "--transcript", str(missing), "--out", str(tmp_path / "o.ttl"))
    assert r.returncode == 1, f"stdout={r.stdout!r} stderr={r.stderr!r}"
    assert "nope.jsonl" in r.stderr, r.stderr
    assert not (tmp_path / "o.ttl").exists()


# ------------------------------------------------------------------ happy path


def test_tiny_inline_transcript_runs_end_to_end(tmp_path, t2t_bin):
    jsonl = tmp_path / "t.jsonl"
    jsonl.write_text(
        '{"type":"user","message":{"content":"What capability grounds this?'
        ' (what grounds the run)"},"origin":{"kind":"human"}}\n'
        '{"type":"assistant","message":{"id":"a1","content":[{"type":"text",'
        '"text":"Grounded in the real run."}]}}\n'
    )
    ttl = tmp_path / "out.ttl"
    r = run_bin(t2t_bin, "--transcript", str(jsonl), "--out", str(ttl))
    assert r.returncode == 0, f"stdout={r.stdout} stderr={r.stderr}"
    assert (
        "wrote:" in r.stdout and "total extracted turns: 2" in r.stdout
    ), f"expected run summary, got:\n{r.stdout}"
    # Real readback, not just the summary line.
    written = ttl.read_text()
    assert written.strip() and "smon" in written, f"emitted Turtle:\n{written}"
