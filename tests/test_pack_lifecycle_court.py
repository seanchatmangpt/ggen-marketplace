"""Pack lifecycle court (real files, no mocks).

Guards the wasi-json-abi-pack / beam-wasmex-host-pack -> rust-wasi-wasmex-pack
deprecation:
  1. lifecycle.toml records both precursor packs with state="deprecated" and
     successor rust-wasi-wasmex-pack.
  2. Each pack named in rust-wasi-wasmex-pack's deprecated_precursors has a
     DEPRECATED.md at the pack root pointing at the successor (repo-relative,
     no absolute file:/// links).
  3. The capability-closure index repoints the wasm-abi capabilities at the
     successor pack.
"""
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUCCESSOR = "rust-wasi-wasmex-pack"


def _precursors() -> list[str]:
    return tomllib.loads(
        (ROOT / "packs" / SUCCESSOR / "pack.toml").read_text(encoding="utf-8")
    )["metadata"]["deprecated_precursors"]


def test_deprecated_precursors_have_lifecycle_deprecated_state() -> None:
    registry = tomllib.loads(
        (ROOT / "lifecycle.toml").read_text(encoding="utf-8")
    )["packs"]
    for pack in _precursors():
        entry = registry[pack]
        assert entry["state"] == "deprecated", pack
        assert SUCCESSOR in entry["successors"], pack


def test_deprecated_precursors_have_deprecated_md_pointing_at_successor() -> None:
    for pack in _precursors():
        dep = ROOT / "packs" / pack / "DEPRECATED.md"
        assert dep.is_file(), pack
        text = dep.read_text(encoding="utf-8")
        assert "DEPRECATED" in text, pack
        assert SUCCESSOR in text, pack
        assert "file:///Users/sac" not in text, pack


def test_capability_index_repoints_wasm_abi_to_successor() -> None:
    index = (ROOT / "packs/capability-closure-pack/index/declared.ttl").read_text(
        encoding="utf-8"
    )
    assert "wasi-json-abi-pack" not in index
    assert "cp:rust-wasi-wasmex-pack a cc:Pack" in index
