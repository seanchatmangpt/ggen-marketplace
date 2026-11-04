"""PM6 port: README "First 10 minutes" CLI walkthrough (Rust
tests/readme_first_ten_minutes.rs) translated to pytest.

Drives the REAL built example binaries (Chicago: real collaborators, no
mocks) per the README's own ten-minute flow and asserts the exact outputs
the README quotes. If this fails, either an example's output changed (update
the README *and* this test in the same change) or the README's credibility
claim ("expected outputs are real") has rotted.

Binaries: $GRAPHLAW_EXAMPLES (default /Users/sac/graphlaw/target/debug/examples),
built via `cargo build --examples`.
"""

import os
import subprocess

import pytest

EXAMPLES = os.environ.get(
    "GRAPHLAW_EXAMPLES", "/Users/sac/graphlaw/target/debug/examples"
)

README_QUICKSTART_HASHES = [
    "blake3:8a0d0202",
    "blake3:c66ea90e",
    "blake3:3be6530b",
]
README_FINAL_STATE = (
    "final state: blake3:3be6530bdf3597afdcc5f60a2a7a0c15a952a1e8f8dd440e0a0bf49082e05896"
)


def run_example(name: str) -> str:
    exe = os.path.join(EXAMPLES, name)
    if not os.path.isfile(exe):
        pytest.skip(f"loud SKIP: example binary missing at {exe} (cargo build --examples)")
    proc = subprocess.run([exe], capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, f"{name} failed rc={proc.returncode}: {proc.stderr}"
    return proc.stdout


def test_quickstart_plan_matches_readme_hashes():
    out = run_example("quickstart_plan")
    for h in README_QUICKSTART_HASHES:
        assert h in out, f"missing {h} in output:\n{out}"
    assert README_FINAL_STATE in out, f"missing final state line in output:\n{out}"


def test_refused_plan_matches_readme_text():
    out = run_example("refused_plan")
    assert "REFUSED at index 1, action `paint`" in out, f"unexpected output:\n{out}"
    assert "<urn:d:door> <urn:p:has> <urn:v:key> ." in out, f"unexpected output:\n{out}"


def test_receipt_feedback_matches_readme_lines():
    out = run_example("receipt_feedback")
    assert (
        "before record: receipt required: no recorded receipt for step `derive:rdfs`"
        in out
    ), f"unexpected output:\n{out}"
    assert "after record:  admitted by `admit:require-receipt`" in out, (
        f"unexpected output:\n{out}"
    )


def test_example_binaries_present():
    """The README flow presupposes built binaries; a missing one is a loud
    skip, not a silent pass."""
    for name in ("quickstart_plan", "refused_plan", "receipt_feedback"):
        assert os.path.isfile(os.path.join(EXAMPLES, name)), (
            f"example binary {name} missing (cargo build --examples)"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
