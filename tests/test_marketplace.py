"""Real-filesystem tests for scripts/marketplace.py's pure functions.

Chicago-style: every test exercises real files on a real tmp_path tree and
asserts on real returned state (bytes, hashes, tuples) — no mocking of the
filesystem or of marketplace's own functions.
"""
from __future__ import annotations

import gzip
import importlib.util
import io
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

_spec = importlib.util.spec_from_file_location("marketplace", SCRIPTS / "marketplace.py")
assert _spec is not None and _spec.loader is not None
marketplace = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = marketplace
_spec.loader.exec_module(marketplace)

Pack = marketplace.Pack


def make_pack_dir(tmp_path: Path, name: str = "demo-pack") -> Path:
    pack_dir = tmp_path / name
    pack_dir.mkdir()
    (pack_dir / "pack.toml").write_text(
        f'[pack]\nname = "{name}"\nversion = "0.1.0"\ndescription = "demo"\n',
        encoding="utf-8",
    )
    (pack_dir / "ontology.ttl").write_text("@prefix ex: <urn:ex:> .\n", encoding="utf-8")
    return pack_dir


def make_pack(tmp_path: Path, name: str = "demo-pack") -> Pack:
    pack_dir = make_pack_dir(tmp_path, name)
    ontologies = marketplace.ontology_files(pack_dir)
    templates = marketplace.visible_files(pack_dir / "templates")
    return Pack(name, "0.1.0", "demo", pack_dir, ontologies, templates, (), ())


# --- sha256_file ---------------------------------------------------------

def test_sha256_file_matches_hashlib_on_real_file(tmp_path: Path) -> None:
    import hashlib

    path = tmp_path / "f.txt"
    path.write_bytes(b"hello world" * 10000)  # exceed one read chunk
    expected = hashlib.sha256(path.read_bytes()).hexdigest()
    assert marketplace.sha256_file(path) == expected


# --- fingerprint_paths -----------------------------------------------------

def test_fingerprint_paths_is_order_independent(tmp_path: Path) -> None:
    (tmp_path / "b.txt").write_text("second", encoding="utf-8")
    (tmp_path / "a.txt").write_text("first", encoding="utf-8")
    forward = marketplace.fingerprint_paths(
        [tmp_path / "a.txt", tmp_path / "b.txt"], tmp_path
    )
    reversed_order = marketplace.fingerprint_paths(
        [tmp_path / "b.txt", tmp_path / "a.txt"], tmp_path
    )
    assert forward == reversed_order


def test_fingerprint_paths_changes_when_content_changes(tmp_path: Path) -> None:
    path = tmp_path / "a.txt"
    path.write_text("v1", encoding="utf-8")
    before = marketplace.fingerprint_paths([path], tmp_path)
    path.write_text("v2", encoding="utf-8")
    after = marketplace.fingerprint_paths([path], tmp_path)
    assert before != after


def test_fingerprint_paths_changes_when_relative_name_changes(tmp_path: Path) -> None:
    # Same content, different relative path -> different fingerprint,
    # because the path bytes are folded into the digest.
    (tmp_path / "a.txt").write_text("same", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "a.txt").write_text("same", encoding="utf-8")
    fp1 = marketplace.fingerprint_paths([tmp_path / "a.txt"], tmp_path)
    fp2 = marketplace.fingerprint_paths([sub / "a.txt"], tmp_path)
    assert fp1 != fp2


# --- visible_files ---------------------------------------------------------

def test_visible_files_excludes_dotfiles_and_dotdirs(tmp_path: Path) -> None:
    (tmp_path / "keep.txt").write_text("x", encoding="utf-8")
    (tmp_path / ".hidden.txt").write_text("x", encoding="utf-8")
    dotdir = tmp_path / ".git"
    dotdir.mkdir()
    (dotdir / "config").write_text("x", encoding="utf-8")
    nested = tmp_path / "sub"
    nested.mkdir()
    (nested / "keep2.txt").write_text("x", encoding="utf-8")

    result = marketplace.visible_files(tmp_path)
    names = sorted(p.relative_to(tmp_path).as_posix() for p in result)
    assert names == ["keep.txt", "sub/keep2.txt"]


def test_visible_files_missing_directory_returns_empty(tmp_path: Path) -> None:
    assert marketplace.visible_files(tmp_path / "does-not-exist") == ()


# --- ontology_files ---------------------------------------------------------

def test_ontology_files_collects_top_level_and_nested_ontology_dir(tmp_path: Path) -> None:
    (tmp_path / "top.ttl").write_text("x", encoding="utf-8")
    (tmp_path / "not-ttl.txt").write_text("x", encoding="utf-8")
    nested = tmp_path / "ontology" / "deep"
    nested.mkdir(parents=True)
    (nested / "nested.ttl").write_text("x", encoding="utf-8")

    result = marketplace.ontology_files(tmp_path)
    names = sorted(p.relative_to(tmp_path).as_posix() for p in result)
    assert names == ["ontology/deep/nested.ttl", "top.ttl"]


def test_ontology_files_empty_when_none_present(tmp_path: Path) -> None:
    assert marketplace.ontology_files(tmp_path) == ()


# --- build_pack_archive ---------------------------------------------------------

def test_build_pack_archive_is_byte_identical_across_calls(tmp_path: Path) -> None:
    pack = make_pack(tmp_path)
    first = marketplace.build_pack_archive(pack)
    second = marketplace.build_pack_archive(pack)
    assert first == second


def test_build_pack_archive_contains_real_extractable_contents(tmp_path: Path) -> None:
    pack = make_pack(tmp_path)
    data = marketplace.build_pack_archive(pack)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        names = sorted(tar.getnames())
        assert names == ["demo-pack/ontology.ttl", "demo-pack/pack.toml"]
        extracted = tar.extractfile("demo-pack/ontology.ttl")
        assert extracted is not None
        assert extracted.read() == (pack.path / "ontology.ttl").read_bytes()


def test_build_pack_archive_gzip_mtime_is_zeroed(tmp_path: Path) -> None:
    pack = make_pack(tmp_path)
    data = marketplace.build_pack_archive(pack)
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as gz:
        gz.read()
        assert gz.mtime == 0


# --- Pack.profile ---------------------------------------------------------

def test_pack_profile_is_semantic_without_templates_or_ggen_toml(tmp_path: Path) -> None:
    pack = make_pack(tmp_path)
    assert pack.profile == "semantic"


def test_pack_profile_is_projection_with_templates(tmp_path: Path) -> None:
    pack_dir = make_pack_dir(tmp_path)
    templates_dir = pack_dir / "templates"
    templates_dir.mkdir()
    (templates_dir / "a.tmpl").write_text("x", encoding="utf-8")
    templates = marketplace.visible_files(templates_dir)
    pack = Pack("demo-pack", "0.1.0", "demo", pack_dir, marketplace.ontology_files(pack_dir), templates, (), ())
    assert pack.profile == "projection"


def test_pack_profile_is_project_when_ggen_toml_present(tmp_path: Path) -> None:
    pack_dir = make_pack_dir(tmp_path)
    (pack_dir / "ggen.toml").write_text("", encoding="utf-8")
    pack = Pack("demo-pack", "0.1.0", "demo", pack_dir, marketplace.ontology_files(pack_dir), (), (), ())
    assert pack.profile == "project"


# --- inspect_marketplace (via a synthetic PACKS directory) ---------------------------------------------------------

def test_inspect_marketplace_flags_missing_manifest(tmp_path: Path, monkeypatch) -> None:
    packs_dir = tmp_path / "packs"
    packs_dir.mkdir()
    (packs_dir / "broken-pack").mkdir()
    monkeypatch.setattr(marketplace, "PACKS", packs_dir)
    monkeypatch.setattr(marketplace, "REQUIRED_DOCS", ())

    packs, issues = marketplace.inspect_marketplace()
    assert packs == []
    assert any("MANIFEST_MISSING" in issue and "broken-pack" in issue for issue in issues)


def test_inspect_marketplace_admits_well_formed_pack(tmp_path: Path, monkeypatch) -> None:
    packs_dir = tmp_path / "packs"
    packs_dir.mkdir()
    make_pack_dir(packs_dir, "good-pack")
    monkeypatch.setattr(marketplace, "PACKS", packs_dir)
    monkeypatch.setattr(marketplace, "REQUIRED_DOCS", ())

    packs, issues = marketplace.inspect_marketplace()
    assert issues == []
    assert len(packs) == 1
    assert packs[0].name == "good-pack"
    assert packs[0].profile == "semantic"
