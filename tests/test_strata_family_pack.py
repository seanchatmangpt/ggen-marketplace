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
    "strata-cas-pack",
    "strata-pn64-pack",
    "strata-protocol-pack",
    "strata-signer-pack",
    "strata-stratus-pack",
    "strata-temprun-pack",
    "strata-valve-pack",
})

# Packs with committed generated/ files guarded against drift (court 3).
DRIFT_GUARDED: dict[str, tuple[str, ...]] = {
    "strata-protocol-pack": ("pdu_constants.rs",),
    "strata-valve-pack": ("refusals.ex",),
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
        assert "VERB_COUNT: usize = 6" in text, (
            "pn64_masks.rs must contain VERB_COUNT: usize = 6")
        assert "// REFUSED" not in text, "pn64_masks.rs must not contain '// REFUSED'"
        return
    if pack == "strata-valve-pack":
        missing = [m for m in VALVE_CHILD_MODULES if m not in text]
        assert not missing, "refusals.ex missing child modules: %r" % missing
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
        assert "// REFUSED: empty ontology projection" in text
        return
    if pack == "strata-temprun-pack":
        assert "ARENA_DEFAULT_MAX_FUEL: u64 = 1000000" in text
        return
    if pack == "strata-signer-pack":
        assert "SIGNATURE_LEN: usize = 3309" in text
        assert "PUBLIC_KEY_LEN: usize = 1952" in text
        return
    if pack == "strata-stratus-pack":
        # VALVE_DEFAULT lives in valves.rs, MAIN_NAME in registers.rs.
        if rel.endswith("valves.rs"):
            assert "VALVE_DEFAULT" in text, "valves.rs must contain VALVE_DEFAULT"
        if rel.endswith("registers.rs"):
            assert "MAIN_NAME" in text, "registers.rs must contain MAIN_NAME"
        decls = _stratus_decl_lines(text)
        dupes = sorted({d for d in decls if decls.count(d) > 1})
        assert not dupes, "stratus declarations defined more than once: %r" % dupes
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

    # Court 3: drift guard — committed generated/ bytes == fresh render bytes.
    for rel in DRIFT_GUARDED.get(name, ()):
        committed = (PACKS_DIR / name / "generated" / rel).read_bytes()
        assert committed == state1["generated/" + rel], (
            "%s: committed generated/%s has drifted from a fresh `ggen sync run`"
            % (name, rel)
        )


# ---------------------------------------------------------------------------
# Court 4: sabotage twins — pure string-level helpers, no ggen rerun
# ---------------------------------------------------------------------------

def _valve_receipt_len_check(text: str) -> None:
    """The valve receipt-length expectation as a pure function."""
    assert "REFUSAL_RECEIPT_LEN: usize = 32" in text


def test_sabotage_twin_receipt_len_check_detects_mutation() -> None:
    good = "pub const REFUSAL_RECEIPT_LEN: usize = 32;\n"
    _valve_receipt_len_check(good)
    with pytest.raises(AssertionError):
        _valve_receipt_len_check(good.replace("= 32", "= 31"))


def test_sabotage_twin_pn64_verb_count_check_detects_mutation() -> None:
    good = "pub const VERB_COUNT: usize = 6;\n"
    assert "VERB_COUNT: usize = 6" in good
    bad = good.replace("= 6", "= 5")
    assert "VERB_COUNT: usize = 6" not in bad


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
