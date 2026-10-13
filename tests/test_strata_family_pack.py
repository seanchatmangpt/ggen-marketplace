"""Strata family sync/content courts (lane L8).

Self-contained pytest module over the seven strata-* generation packs:
sync courts (real `ggen sync run` in a tmp copy, run twice, byte-identical
outputs), content courts asserting rdflib-derived ground-truth constants,
a drift guard against committed generated/ files, and pure string-level
sabotage twins.

Chicago style: real ggen subprocess, real files, no mocks. Skips carry a
"BLOCKED:" reason prefix when ggen is unavailable.

Model patterns: tests/test_ash_extension_install_template.py,
tests/test_industry_closure_pack.py (real ggen subprocess court).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKS_DIR = ROOT / "packs"

EXPECTED_STRATA_GENERATION_PACKS = frozenset({
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
})

# Packs with committed generated/ files guarded against drift (court 3).
# Every strata pack now commits its rendered generated/ tree, so the drift
# guard covers all fifteen: the fresh render must be byte-identical to the
# committed outputs in the real repo, not just to a second fresh render.
DRIFT_GUARDED: dict[str, tuple[str, ...]] = {
    "strata-audit-pack": ("audit_corpus.rs",),
    "strata-governance-pack": ("governance_report.rs",),
    "strata-cas-pack": ("cas.rs",),
    "strata-chain-pack": ("chain_consts.rs", "chain_engine.rs"),
    "strata-consensus-pack": ("consensus_consts.rs", "consensus_engine.rs"),
    "strata-hash-pack": ("hash_consts.rs", "hash_merkle.rs"),
    "strata-ledger-pack": ("ledger_consts.rs", "ledger_state.rs",
                           "kernel_laws.rs"),
    "strata-net-pack": ("net_consts.rs", "net_engine.rs", "pdu_envelope.rs"),
    "strata-pn64-pack": ("pn64_masks.rs",),
    "strata-protocol-pack": ("pdu_constants.rs", "wire_constants.rs"),
    "strata-signer-pack": ("signer.rs", "signing.rs"),
    "strata-store-pack": ("store_consts.rs", "store_engine.rs"),
    "strata-stratus-pack": ("registers.rs", "valves.rs"),
    "strata-temprun-pack": ("arena.rs", "fuel_refusal_binding.rs"),
    "strata-tx-pack": ("tx_consts.rs", "tx_model.rs"),
    "strata-valve-pack": ("refusals.ex", "window_capacity.rs"),
}


def _ggen_binary() -> str | None:
    return os.environ.get("GGEN_BIN") or shutil.which("ggen")


def _copy_pack(name: str, dest: Path) -> Path:
    src = PACKS_DIR / name
    if not src.is_dir():
        pytest.fail(
            "BLOCKED: pack source missing: packs/%s (sibling-lane migration not landed?)"
            % name
        )
    shutil.copytree(src, dest / name)
    return dest / name


def _run_sync(pack_dir: Path) -> subprocess.CompletedProcess:
    binary = _ggen_binary() or "ggen"
    return subprocess.run(
        [binary, "sync", "run"],
        cwd=pack_dir, capture_output=True, text=True, timeout=300,
    )


def _generated_state(pack_dir: Path) -> dict[str, bytes]:
    """Map of generated/<rel> -> bytes for one pack copy."""
    gen = pack_dir / "generated"
    if not gen.is_dir():
        return {}
    return {
        str(f.relative_to(pack_dir)): f.read_bytes()
        for f in sorted(gen.rglob("*"))
        if f.is_file()
    }


# The four child module names of Strata.Valve.Refusals (verified against a
# real `ggen sync run` render of the current pack source).
VALVE_CHILD_MODULES = (
    "Strata.Valve.Refusals.ArenaFailure",
    "Strata.Valve.Refusals.FuelExhausted",
    "Strata.Valve.Refusals.MalformedFrame",
    "Strata.Valve.Refusals.ParentDiscontinuity",
)


def _stratus_decl_lines(text: str) -> list[str]:
    """Stripped struct/impl/const declaration lines of a stratus render."""
    return [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip().startswith(("pub struct ", "pub enum ", "impl ", "pub const "))
    ]


def _content_court(pack: str, rel: str, text: str) -> None:
    """Pure content check for one generated file (sync-court expectations)."""
    if pack == "strata-pn64-pack":
        _pn64_verb_count_check(text)
        assert "// REFUSED" not in text, "pn64_masks.rs must not contain '// REFUSED'"
        return
    if pack == "strata-valve-pack":
        # Per-file dispatch: refusals.ex keeps the child-module court; the
        # window-capacity table (L86, knhk guard atoms) is a second output.
        if rel.endswith("refusals.ex"):
            missing = [m for m in VALVE_CHILD_MODULES if m not in text]
            assert not missing, "refusals.ex missing child modules: %r" % missing
        elif rel.endswith("window_capacity.rs"):
            assert "CHATMAN_K: u32 = 8" in text
            assert "pub struct WindowCapacityRefusal" in text
            assert "pub fn window_capacity_closure" in text
            assert "WINDOW_CAPACITY_REFUSALS" in text
        else:
            raise AssertionError(
                f"unexpected generated file for valve pack: {rel}")
        return
    if pack == "strata-protocol-pack":
        # Per-file expectations: pdu side and wire side are separate outputs
        # (wire_constants.rs landed via the wire-constants rule).
        if rel.endswith("pdu_constants.rs"):
            assert "REFUSAL_RECEIPT_LEN: usize = 32" in text
            assert "PDU_MAGIC" in text
        elif rel.endswith("wire_constants.rs"):
            assert "pub mod wire" in text
            assert "32" in text
        else:
            raise AssertionError(f"unexpected generated file for protocol pack: {rel}")
        return
    if pack == "strata-cas-pack":
        # Per-file expectations. The old "// REFUSED: empty ontology
        # projection" marker was legitimately removed when the cas ontology
        # gained real content (sibling lane L93's witnessed-removal; twins
        # landed in e1ee25fa2 "twins for cas/chain/governance"). The court
        # now tracks the current real projection, not the old empty marker.
        if rel.endswith("cas.rs"):
            assert "pub struct MerkleCommit" in text
            assert "pub struct KnowledgeWormhole" in text
            assert "pub struct Snapshot" in text
            assert "pub fn genesis" in text
            assert "pub fn child_of" in text
            assert "pub fn depth" in text
            assert "// REFUSED" not in text, (
                "cas.rs renders real content; must not carry REFUSED markers")
        else:
            raise AssertionError(f"unexpected generated file for cas pack: {rel}")
        return
    if pack == "strata-temprun-pack":
        # Per-file dispatch (mirrors the protocol/valve/signer packs):
        # arena.rs keeps the fuel-table court; the fuel-refusal binding
        # module (temprun<->valve composition) is a second output.
        if rel.endswith("arena.rs"):
            assert "ARENA_DEFAULT_MAX_FUEL: u64 = 1000000" in text
        elif rel.endswith("fuel_refusal_binding.rs"):
            assert (
                'FUEL_EXHAUSTED_REFUSAL_IRI: &str = '
                '"https://strata.chatman.ai/ontology/valve#FuelExhaustedRefusal"'
            ) in text
            assert "REFUSAL_RECEIPT_LEN: usize = 32" in text
        else:
            raise AssertionError(
                f"unexpected generated file for temprun pack: {rel}")
        return
    if pack == "strata-signer-pack":
        # Per-file expectations (like the protocol pack's pdu/wire split):
        # signer.rs owns the detached-signature constants; signing.rs is the
        # payload/tx signing surface with its own ground truth.
        if rel.endswith("signer.rs"):
            assert "SIGNATURE_LEN: usize = 3309" in text
            assert "PUBLIC_KEY_LEN: usize = 1952" in text
        elif rel.endswith("signing.rs"):
            assert "PAYLOAD_SIGNATURE_LEN: usize = 3309" in text
            assert "pub trait PayloadSigner" in text, (
                "signing.rs must define the PayloadSigner trait")
            assert "pub fn bind_tx_digest" in text, (
                "signing.rs must define TxSigner::bind_tx_digest (SHA-256 "
                "digest binding)")
            assert "FIPS 180-4" in text and "vectors" in text, (
                "signing.rs must carry the SHA-256 FIPS 180-4 test-vector "
                "provenance note")
        else:
            raise AssertionError(
                f"unexpected generated file for signer pack: {rel}")
        return
    if pack == "strata-stratus-pack":
        # VALVE_DEFAULT lives in valves.rs, MAIN_NAME in registers.rs.
        if rel.endswith("valves.rs"):
            assert "VALVE_DEFAULT" in text, "valves.rs must contain VALVE_DEFAULT"
        elif rel.endswith("registers.rs"):
            assert "MAIN_NAME" in text, "registers.rs must contain MAIN_NAME"
        else:
            raise AssertionError(
                f"unexpected generated file for stratus pack: {rel}")
        decls = _stratus_decl_lines(text)
        dupes = sorted({d for d in decls if decls.count(d) > 1})
        assert not dupes, "stratus declarations defined more than once: %r" % dupes
        return
    if pack == "strata-audit-pack":
        if rel.endswith("audit_corpus.rs"):
            assert "AUDIT_TARGETS" in text
            assert "DIGEST_LEN: usize = 32" in text
        else:
            raise AssertionError(
                f"unexpected generated file for audit pack: {rel}")
        return
    if pack == "strata-chain-pack":
        if rel.endswith("chain_consts.rs"):
            assert "GENESIS_HEIGHT: u64 = 0" in text
            assert "MAX_BLOCK_TXS: u64 = 256" in text
        elif rel.endswith("chain_engine.rs"):
            assert "pub fn tx_merkle_root_for" in text
            assert "pub struct Block" in text
        else:
            raise AssertionError(
                f"unexpected generated file for chain pack: {rel}")
        return
    if pack == "strata-consensus-pack":
        if rel.endswith("consensus_consts.rs"):
            assert 'TIE_BREAK: &str = "lower-nonce"' in text
            assert 'WORK_UNIT: &str = "sha256-double-tick"' in text
        elif rel.endswith("consensus_engine.rs"):
            assert "pub struct Block" in text
            assert "pub fn header_bytes" in text
        else:
            raise AssertionError(
                f"unexpected generated file for consensus pack: {rel}")
        return
    if pack == "strata-hash-pack":
        if rel.endswith("hash_consts.rs"):
            assert "HASH_ALGO_COUNT: usize = 2" in text
        elif rel.endswith("hash_merkle.rs"):
            assert "pub fn merkle_root" in text
            assert "pub fn merkle_verify" in text
        else:
            raise AssertionError(
                f"unexpected generated file for hash pack: {rel}")
        return
    if pack == "strata-ledger-pack":
        if rel.endswith("ledger_consts.rs"):
            assert "MAX_ACCOUNTS: usize = 65536" in text
            assert "STATE_ROOT_LEN: usize = 32" in text
        elif rel.endswith("ledger_state.rs"):
            assert "pub enum LedgerRefusal" in text
            assert "pub struct StateTransitionReceipt" in text
        elif rel.endswith("kernel_laws.rs"):
            # Kernel-law projection (ledger ontology lg:KERNEL_LAWS);
            # invariants reuse-adapted from unibit-kernel @ 3bb4347f
            # (compile-fail courts 82033542d, ledger boundary-replay L137).
            assert 'LAW_SPARSE_DELTA: &str = "SPARSE_DELTA"' in text
            assert 'LAW_BITFENWICK_SUM: &str = "BITFENWICK_SUM"' in text
            assert 'LAW_MULTI_STEP_EXECUTION: &str = "MULTI_STEP_EXECUTION"' in text
            assert "pub fn sparse_delta_emit" in text
            assert "pub fn sparse_delta_apply" in text
            assert "pub struct Bitfenwick8" in text
            assert "pub struct MultiStepWork" in text
        else:
            raise AssertionError(
                f"unexpected generated file for ledger pack: {rel}")
        return
    if pack == "strata-net-pack":
        if rel.endswith("net_consts.rs"):
            assert "HEADER_LEN: usize = 8" in text
            assert "MAX_MSG_LEN: usize = 65536" in text
        elif rel.endswith("net_engine.rs"):
            assert "pub fn encode" in text
            assert "pub fn decode" in text
        elif rel.endswith("pdu_envelope.rs"):
            assert "pub const NET_MAX_MSG_LEN: usize = 65536" in text
            assert "pub const PDU_HEADER_LEN: usize = 64" in text
            assert "pub const REFUSAL_RECEIPT_LEN: usize = 32" in text
        else:
            raise AssertionError(
                f"unexpected generated file for net pack: {rel}")
        return
    if pack == "strata-store-pack":
        if rel.endswith("store_consts.rs"):
            assert "DEFAULT_CAPACITY: usize = 1048576" in text
            assert "KEY_LEN: usize = 32" in text
        elif rel.endswith("store_engine.rs"):
            assert "pub enum StoreRefusal" in text
            assert "pub struct StoreMarker" in text
        else:
            raise AssertionError(
                f"unexpected generated file for store pack: {rel}")
        return
    if pack == "strata-governance-pack":
        # Constitutional-diff projection (constants vs sealed commitments;
        # lane T11/X5 candidate 1, twins in e1ee25fa2). Any projected value
        # drifting from its sealed commitment is a ConstitutionalDrift.
        if rel.endswith("governance_report.rs"):
            assert "pub struct ConstantDiffRow" in text
            assert "pub struct ConstitutionalDrift" in text
            assert "pub const DIFF_TABLE" in text
            assert "pub fn verify_constitution" in text
        else:
            raise AssertionError(
                f"unexpected generated file for governance pack: {rel}")
        return
    if pack == "strata-tx-pack":
        if rel.endswith("tx_consts.rs"):
            assert "TX_MAGIC: u32 = 0x5354_5831" in text
            assert "TX_HEADER_LEN: usize = 56" in text
        elif rel.endswith("tx_model.rs"):
            assert "pub struct" in text
        else:
            raise AssertionError(
                f"unexpected generated file for tx pack: {rel}")
        return
    pytest.fail("no content court defined for %s/%s" % (pack, rel))


# ---------------------------------------------------------------------------
# Court 1: set guard — exactly the seven strata generation packs
# ---------------------------------------------------------------------------

def test_strata_generation_packs_set_guard() -> None:
    found = {
        d.name
        for d in PACKS_DIR.iterdir()
        if d.name.startswith("strata-") and (d / "ggen.toml").is_file()
    }
    missing = EXPECTED_STRATA_GENERATION_PACKS - found
    extra = found - EXPECTED_STRATA_GENERATION_PACKS
    assert not missing, (
        "BLOCKED: strata packs missing ggen.toml (sibling-lane migrations not "
        "landed?): " + ", ".join(sorted(missing))
    )
    assert not extra, (
        "unexpected strata packs with ggen.toml: " + ", ".join(sorted(extra))
    )


# ---------------------------------------------------------------------------
# Courts 2+3: real ggen sync twice, determinism, content, drift guard
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    _ggen_binary() is None,
    reason="BLOCKED: ggen binary not found (set GGEN_BIN); sync courts blocked",
)
@pytest.mark.parametrize("name", sorted(EXPECTED_STRATA_GENERATION_PACKS))
def test_real_ggen_sync_determinism_content_and_drift(
    name: str, tmp_path: Path
) -> None:
    pack_dir = _copy_pack(name, tmp_path)

    # Cold-render hardening: strip any committed generated/ copy so the first
    # sync provably renders from scratch (also strengthens the drift guard:
    # state1 is unambiguously a fresh render, not a leftover).
    shutil.rmtree(pack_dir / "generated", ignore_errors=True)

    first = _run_sync(pack_dir)
    assert first.returncode == 0, (first.stdout + first.stderr)[-1500:]
    state1 = _generated_state(pack_dir)
    assert state1, "%s: no generated/ files produced by first sync" % name

    second = _run_sync(pack_dir)
    assert second.returncode == 0, (second.stdout + second.stderr)[-1500:]
    state2 = _generated_state(pack_dir)
    assert state1 == state2, (
        "%s: generated/ files differ between two real ggen sync runs "
        "(nondeterministic render): %s"
        % (name, sorted(set(state1) ^ set(state2)))
    )

    # Content courts against the fresh render.
    for rel, data in state1.items():
        _content_court(name, rel, data.decode("utf-8"))

    # Court 3: drift guard — committed generated/ bytes == fresh render bytes,
    # for every committed output of every pack (not just protocol+valve).
    for rel in DRIFT_GUARDED.get(name, ()):
        committed = (PACKS_DIR / name / "generated" / rel).read_bytes()
        _drift_check(name, rel, state1["generated/" + rel], committed)


# ---------------------------------------------------------------------------
# Court 4: sabotage twins — pure string-level helpers, no ggen rerun
# ---------------------------------------------------------------------------

def _pn64_verb_count_check(text: str) -> None:
    """The pn64 VERB_COUNT expectation as a pure function."""
    assert "VERB_COUNT: usize = 6" in text, (
        "pn64_masks.rs must contain VERB_COUNT: usize = 6")


def _valve_receipt_len_check(text: str) -> None:
    """The valve receipt-length expectation as a pure function."""
    assert "REFUSAL_RECEIPT_LEN: usize = 32" in text


def _drift_check(pack: str, rel: str, fresh_render: bytes,
                 committed_bytes: bytes) -> None:
    """One drift-guard comparison as a pure function (court 3 + twin)."""
    assert committed_bytes == fresh_render, (
        "%s: committed generated/%s has drifted from a fresh `ggen sync run`"
        % (pack, rel)
    )


def test_sabotage_twin_receipt_len_check_detects_mutation() -> None:
    good = "pub const REFUSAL_RECEIPT_LEN: usize = 32;\n"
    _valve_receipt_len_check(good)
    with pytest.raises(AssertionError):
        _valve_receipt_len_check(good.replace("= 32", "= 31"))


def test_sabotage_twin_pn64_verb_count_check_detects_mutation() -> None:
    good = "pub const VERB_COUNT: usize = 6;\n"
    _pn64_verb_count_check(good)
    bad = good.replace("= 6", "= 5")
    with pytest.raises(AssertionError, match="VERB_COUNT: usize = 6"):
        _pn64_verb_count_check(bad)


def test_sabotage_twin_extended_drift_guard_detects_committed_mutation(
    tmp_path: Path,
) -> None:
    """The extended drift guard must fire on a mutated committed byte.

    Copy a real pack with committed generated/ output into tmp, flip one
    committed byte, and prove the guard detects the drift against the
    (unmutated) fresh render.
    """
    name = "strata-signer-pack"
    rel = "signer.rs"
    pack_dir = _copy_pack(name, tmp_path)
    committed = pack_dir / "generated" / rel
    original = committed.read_bytes()

    # Guard passes on the pristine copy (bytes identical to themselves).
    _drift_check(name, rel, original, original)

    # Sabotage: mutate one committed byte in the tmp copy.
    mutated = original.replace(b"SIGNATURE_LEN", b"SIGNATURE_LENXX", 1)
    assert mutated != original
    committed.write_bytes(mutated)

    with pytest.raises(AssertionError, match="has drifted from a fresh"):
        _drift_check(name, rel, original, committed.read_bytes())


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
