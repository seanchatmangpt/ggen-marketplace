"""Cross-check court for insa-law-pack (Chicago): the projected VOW_ORDER
chain must equal the eight-vow typestate order taken from the insa source.
Provenance for the pinned chain:
insa-replaw/src/eight_vow.rs L172-321 (VowEngine typestate advance fns
confirm_source .. seal) and eight_vow_bridge.rs L9-10 + L172-321 (chain),
eight_vow_bridge.rs L129-544 (edge fns).
Real files, real subprocess — no mocks."""

import re
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PACK = REPO / "packs" / "insa-law-pack"

# The typestate chain, read from the insa source (eight_vow.rs L172-321) and
# mirrored in packs/insa-law-pack/pinned/insa_eight_vow_chain.txt.
TYPESTATE_CHAIN = [
    (1, "source", "pattern", "edge_source_to_pattern"),
    (2, "pattern", "field", "edge_pattern_to_field"),
    (3, "field", "motion", "edge_field_to_motion"),
    (4, "motion", "receiver", "edge_motion_to_receiver"),
    (5, "receiver", "fruit", "edge_receiver_to_fruit"),
    (6, "fruit", "receipt", "edge_fruit_to_receipt"),
    (7, "receipt", "rest", "edge_receipt_to_rest"),
    (8, "rest", "rest", "edge_rest_seal"),
]


def _projected_rows() -> list[tuple[int, str, str, str]]:
    """Parse generated/vow_order.rs's VOW_ORDER table."""
    text = (PACK / "generated" / "vow_order.rs").read_text(encoding="utf-8")
    rows = re.findall(
        r'ordinal:\s*(\d+),\s*from_state:\s*"([^"]+)",\s*to_state:\s*"([^"]+)",'
        r'\s*edge_fn:\s*"([^"]+)"',
        text,
    )
    return [(int(o), f, t, e) for o, f, t, e in rows]


def test_projected_chain_equals_typestate_order() -> None:
    assert _projected_rows() == [tuple(r) for r in TYPESTATE_CHAIN]


def test_projected_chain_equals_pinned_snapshot() -> None:
    pinned = [
        line.split("#", 1)[0].strip()
        for line in (PACK / "pinned" / "insa_eight_vow_chain.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.split("#", 1)[0].strip()
    ]
    rows = _projected_rows()
    assert len(pinned) == len(rows) == 8
    for row, entry in zip(rows, pinned):
        ord_, chain, edge = entry.split(None, 2)
        f, t = chain.split("->")
        assert row == (int(ord_), f, t, edge)


def test_verify_py_zero_rows_exit_zero() -> None:
    result = subprocess.run(
        ["python3", str(PACK / "verify.py")],
        capture_output=True,
        text=True,
        cwd=PACK,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "FAIL" not in result.stdout
    assert "all gates zero-rows" in result.stdout


def test_generated_rust_gate_suite_passes() -> None:
    rustc = shutil.which("rustc")
    assert rustc is not None, "rustc required for the generated gate suite court"
    generated = PACK / "generated" / "vow_order.rs"
    result = subprocess.run(
        [rustc, "--test", str(generated), "-o", "/tmp/insa_law_pack_vow_order_test"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    run = subprocess.run(["/tmp/insa_law_pack_vow_order_test"], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "test result: ok" in run.stdout
