"""Strata sabotage-twin corpus court (lane L92).

Corpus-level proof that every strata pack carrying a sabotage twin stays
caught: for ONE representative twin per pack, the generated module is
compiled standalone (``rustc --test`` for the Rust packs; a real
``elixirc`` compile + real ``elixir`` KEY=VALUE harness for the one Elixir
pack, strata-valve-pack) in a tmp dir and the twin-catching test is
executed for real (Chicago: real compiler, real subprocess, no mocks).

Also a fail-closed inventory gate: every pack in the strata family must
have >= 1 sabotage twin OR be in the documented coverage-hole set. A pack
gaining its first twin (or a pack losing its only twin) flips the gate, so
the inventory cannot silently drift.

Pattern provenance: tests/test_strata_family_pack.py (family inventory),
tests/test_state_transition_fsm.py (real rustc subprocess court).

Skips carry a "BLOCKED:" reason prefix when rustc is unavailable.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKS_DIR = ROOT / "packs"

# Family inventory mirrors tests/test_strata_family_pack.py.
STRATA_FAMILY = (
    "strata-audit-pack",
    "strata-cas-pack",
    "strata-chain-pack",
    "strata-consensus-pack",
    "strata-governance-pack",
    "strata-hash-pack",
    "strata-ledger-pack",
    "strata-net-pack",
    "strata-pn64-pack",
    "strata-protocol-pack",
    "strata-signer-pack",
    "strata-store-pack",
    "strata-stratus-pack",
    "strata-temprun-pack",
    "strata-tx-pack",
    "strata-valve-pack",
)

# (pack) -> (generated module, representative twin test path, all twin tests).
# Inventory from grep of generated/ for sabotage/twin/discriminat markers,
# confirmed against `--list` output of the compiled binaries.
TWIN_INVENTORY: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "strata-consensus-pack": (
        "consensus_engine.rs",
        "tests::sabotage_block_count_fork_choice_is_caught",
        ("tests::sabotage_block_count_fork_choice_is_caught",),
    ),
    "strata-net-pack": (
        "net_engine.rs",
        "fuzz_tests::fuzz_sabotage_twin_discrimination",
        ("fuzz_tests::fuzz_sabotage_twin_discrimination",),
    ),
    "strata-protocol-pack": (
        "pdu_constants.rs",
        "tests::sabotage_mutated_constant_trips_abutment",
        ("tests::sabotage_mutated_constant_trips_abutment",),
    ),
    "strata-signer-pack": (
        "signing.rs",
        "tests::sabotage_twin_skipping_domain_sep_is_caught",
        ("tests::sabotage_twin_skipping_domain_sep_is_caught",),
    ),
    "strata-store-pack": (
        "store_engine.rs",
        "tests::sabotaged_tail_skip_recovery_is_caught",
        (
            "tests::sabotaged_tail_skip_recovery_is_caught",
            "tests::sabotaged_unguarded_rollback_is_caught",
        ),
    ),
    "strata-tx-pack": (
        "tx_model.rs",
        "tests::sabotage_twin_nonce_skip_is_caught",
        (
            "tests::replay_guard_distinguishes_nonce_twin",
            "tests::sabotage_twin_nonce_skip_is_caught",
            "tests::sabotage_twin_reserved_skip_is_caught",
        ),
    ),
    "strata-hash-pack": (
        "hash_merkle.rs",
        "tests::sabotage_twin_leaf_tag_skip_is_caught",
        ("tests::sabotage_twin_leaf_tag_skip_is_caught",),
    ),
    "strata-ledger-pack": (
        "ledger_state.rs",
        "tests::sabotage_twin_mutate_before_conservation_is_caught",
        ("tests::sabotage_twin_mutate_before_conservation_is_caught",),
    ),
    "strata-pn64-pack": (
        "pn64_masks.rs",
        "tests::sabotage_twin_unmasked_fire_is_caught",
        ("tests::sabotage_twin_unmasked_fire_is_caught",),
    ),
    "strata-temprun-pack": (
        "arena.rs",
        "tests::sabotage_twin_fuel_decrement_skip_is_caught",
        ("tests::sabotage_twin_fuel_decrement_skip_is_caught",),
    ),
    "strata-cas-pack": (
        "cas.rs",
        "tests::sabotage_twin_digest_copying_verify_is_caught",
        ("tests::sabotage_twin_digest_copying_verify_is_caught",),
    ),
    "strata-chain-pack": (
        "chain_engine.rs",
        "tests::sabotage_twin_chain_fold_skip_prev_is_caught",
        (
            "tests::shared_kat_chain_fold_head_pinned",
            "tests::sabotage_twin_chain_fold_skip_prev_is_caught",
        ),
    ),
    "strata-governance-pack": (
        "governance_report.rs",
        "tests::sabotage_twin_unframed_seal_digest_is_caught",
        ("tests::sabotage_twin_unframed_seal_digest_is_caught",),
    ),
    # The one Elixir pack. Exec-shape difference (honest, not mocked): the
    # valve twin is a test-only module inside generated/refusals.ex, exercised
    # by a real elixirc compile + real elixir harness subprocess (the KEY=VALUE
    # court in tests/test_strata_valve_runtime.py), NOT by rustc --test. The
    # corpus court below dispatches valve through that elixir path and the
    # rust packs through rustc --test.
    "strata-valve-pack": (
        "refusals.ex",
        "Strata.Valve.Refusals.SabotageTwinSkipClassLabel",
        ("Strata.Valve.Refusals.SabotageTwinSkipClassLabel",),
    ),
}

# Packs with NO sabotage twin today (fail-closed: the gate below asserts
# this set exactly; adding or removing a twin flips the gate and forces
# this documentation to be updated in the same dependency-closed change).
#
# Justifications (evaluated L124 2026-10-13):
# - strata-audit-pack: N/A — its generated audit_corpus.rs IS the
#   twin-holder surface (falsifier corpus + merkle helpers); a twin inside
#   the twin-holder court would be circular.
# - strata-stratus-pack: no real twin surface — generated/registers.rs
#   (31 lines) and generated/valves.rs (24 lines) are pure const-table
#   projections with no verifying function to twin.
# - strata-valve-pack: HAS a twin since L155 — the class-label-skipping
#   sabotage twin in generated/refusals.ex, caught by the cross-class-
#   distinctness leg of the elixirc/elixir runtime court
#   (tests/test_strata_valve_runtime.py::...sabotage_twin_skipping_class_label_is_caught).
DOCUMENTED_COVERAGE_HOLES = frozenset({
    "strata-audit-pack",
    "strata-stratus-pack",
})

RUSTC_TIMEOUT = 90  # per-module compile; each module self-contained


def _rustc_available() -> bool:
    return shutil.which("rustc") is not None


def _run_valve_elixir_twin_court() -> None:
    """Real elixirc + real elixir subprocess court for the one Elixir pack.

    Reuses the runtime court in tests/test_strata_valve_runtime.py (no mocks,
    no reimplementation): compiles generated/refusals.ex and proves the
    twin-discrimination leg — the class-label-skipping twin must produce
    IDENTICAL receipts across the four refusal classes (caught by the
    cross-class-distinctness court) while the honest derivation produces
    4 distinct.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "valve_runtime_court",
        ROOT / "tests" / "test_strata_valve_runtime.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not mod.have("elixir", "elixirc"):
        pytest.skip("BLOCKED: elixir/elixirc not installed")
    obs = mod.run_court(mod.SOURCE)
    assert obs.get("TWIN_DISTINCT") == "false", (
        "valve twin NOT caught: TWIN_DISTINCT=%r (twin receipts were "
        "distinct across classes — discrimination leg vacuous)"
        % obs.get("TWIN_DISTINCT")
    )
    assert obs.get("REFUSE_DISTINCT") == "true", obs.get("REFUSE_DISTINCT")
    bad = mod.violations(obs)
    assert not any("TWIN_DISTINCT" in v for v in bad), bad


def _compile_module(pack: str, outdir: Path) -> Path:
    """Compile pack's generated module standalone via rustc --test."""
    module = TWIN_INVENTORY[pack][0]
    src = PACKS_DIR / pack / "generated" / module
    if not src.is_file():
        pytest.fail("BLOCKED: generated module missing: %s" % src)
    exe = outdir / src.stem
    proc = subprocess.run(
        ["rustc", "--test", "-O", "-o", str(exe), str(src)],
        capture_output=True,
        text=True,
        timeout=RUSTC_TIMEOUT,
    )
    if proc.returncode != 0:
        pytest.fail(
            "BLOCKED: rustc --test failed for %s:\n%s" % (src, proc.stderr[-2000:])
        )
    return exe


def _assert_passed(proc: subprocess.CompletedProcess, label: str) -> None:
    out = proc.stdout + proc.stderr
    if proc.returncode != 0 or "0 failed" not in out or "1 passed" not in out:
        pytest.fail(
            "sabotage twin NOT caught (or run failed) for %s:\n%s" % (label, out[-2000:])
        )


def test_inventory_gate_fail_closed() -> None:
    """Every strata pack has >=1 twin OR is a documented coverage hole."""
    holes = set(STRATA_FAMILY) - set(TWIN_INVENTORY)
    assert holes == set(DOCUMENTED_COVERAGE_HOLES), (
        "sabotage-twin inventory drift: %s"
        % sorted(holes ^ set(DOCUMENTED_COVERAGE_HOLES))
    )


def test_inventory_names_are_real_and_unique() -> None:
    """Every documented twin test name exists in the compiled module
    (rust packs) / compiled Elixir surface (valve pack)."""
    if not _rustc_available():
        pytest.skip("BLOCKED: rustc not on PATH")
    outdir = Path("/tmp/l92-corpus") / "inventory"
    outdir.mkdir(parents=True, exist_ok=True)
    for pack in sorted(TWIN_INVENTORY):
        if pack == "strata-valve-pack":
            # Exec-shape difference: Elixir pack — the elixirc/elixir court
            # exercises the twin module by name, proving it is real.
            _run_valve_elixir_twin_court()
            continue
        exe = _compile_module(pack, outdir)
        listing = subprocess.run(
            [str(exe), "--list"], capture_output=True, text=True, timeout=60
        )
        assert listing.returncode == 0, listing.stderr
        names = {
            line.rsplit(":", 1)[0].strip()
            for line in listing.stdout.splitlines()
            if ": test" in line
        }
        module, _rep, all_tests = TWIN_INVENTORY[pack]
        for t in all_tests:
            assert t in names, "%s: twin test %s not in %s" % (pack, t, module)


def test_each_pack_representative_twin_is_caught() -> None:
    """Re-run ONE representative twin per pack (real rustc + real binary for
    Rust packs; real elixirc + real elixir for the valve pack)."""
    if not _rustc_available():
        pytest.skip("BLOCKED: rustc not on PATH")
    outdir = Path("/tmp/l92-corpus") / "twins"
    outdir.mkdir(parents=True, exist_ok=True)
    for pack in sorted(TWIN_INVENTORY):
        if pack == "strata-valve-pack":
            _run_valve_elixir_twin_court()
            continue
        exe = _compile_module(pack, outdir)
        rep = TWIN_INVENTORY[pack][1]
        proc = subprocess.run(
            [str(exe), "--exact", rep],
            capture_output=True,
            text=True,
            timeout=60,
        )
        _assert_passed(proc, "%s :: %s" % (pack, rep))
