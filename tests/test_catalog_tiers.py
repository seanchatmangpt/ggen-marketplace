"""Catalog tiers, lifecycle, discovery: real files, real subprocess, no mocks."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import marketplace  # noqa: E402
import marketplace_tiers as tiers  # noqa: E402


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "marketplace.py"), *args],
        cwd=root, capture_output=True, text=True, check=False,
    )


def write_pack(root: Path, name: str, extra_toml: str = "", files: tuple[str, ...] = ()) -> Path:
    d = root / "packs" / name
    d.mkdir(parents=True)
    (d / "pack.toml").write_text(
        f'[pack]\nname = "{name}"\nversion = "1.0.0"\ndescription = "Pack {name} for rust cli"\n{extra_toml}',
        encoding="utf-8",
    )
    (d / "ontology.ttl").write_text("@prefix ex: <http://example.org/> .\n", encoding="utf-8")
    for rel in files:
        f = d / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x\n", encoding="utf-8")
    return d


@pytest.fixture()
def mini(tmp_path: Path) -> Path:
    """A self-contained marketplace: real scripts copy, real docs stubs, no packs yet."""
    shutil.copytree(REPO / "scripts", tmp_path / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(REPO / "marketplace.toml", tmp_path / "marketplace.toml")
    for rel in marketplace.REQUIRED_DOCS:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("stub\n", encoding="utf-8")
    (tmp_path / "packs").mkdir()
    return tmp_path


def test_tier_classification_from_structure(tmp_path: Path) -> None:
    thin = write_pack(tmp_path, "thin-pack")
    doc = write_pack(tmp_path, "doc-pack", files=("README.md", "a.txt", "b.txt"))
    ver = write_pack(tmp_path, "ver-pack", files=("README.md", "gates/g.rq", "witnesses/w.ttl"))
    assert tiers.tier(tiers.signals(thin), tiers.file_count(thin)) == "thin"
    assert tiers.tier(tiers.signals(doc), tiers.file_count(doc)) == "documented"
    assert tiers.tier(tiers.signals(ver), tiers.file_count(ver)) == "verified"
    assert tiers.signals(ver) == {"gates": True, "readme": True, "verify": False, "witnesses": True}


def test_lifecycle_status_and_dangling_supersession(mini: Path) -> None:
    write_pack(mini, "old-pack", 'superseded_by = "new-pack"\n')
    write_pack(mini, "new-pack")
    write_pack(mini, "dep-pack", "deprecated = true\n")
    assert run(mini, "validate").returncode == 0
    recs = {p["name"]: p for p in json.loads(run(mini, "catalog", "--scope", "all").stdout)["packs"]}
    assert recs["old-pack"]["status"] == "superseded" and recs["old-pack"]["successors"] == ["new-pack"]
    assert recs["dep-pack"]["status"] == "deprecated" and recs["dep-pack"]["deprecated"] is True
    assert recs["new-pack"]["status"] == "active"
    shutil.rmtree(mini / "packs" / "new-pack")
    bad = run(mini, "validate")
    assert bad.returncode == 2
    assert "REFUSED:PACK_SUPERSEDED_BY_MISSING:old-pack:superseded_by=new-pack" in bad.stderr


def test_baseline_only_when_committed(mini: Path) -> None:
    write_pack(mini, "a-pack")
    rec = json.loads(run(mini, "catalog", "--scope", "all").stdout)["packs"][0]
    assert "qualification" not in rec
    (mini / "qualification").mkdir()
    (mini / "qualification" / "baseline.json").write_text(json.dumps({"packs": {"a-pack": "ALIVE"}}))
    rec = json.loads(run(mini, "catalog", "--scope", "all").stdout)["packs"][0]
    assert rec["qualification"] == "ALIVE"


def test_search_show_browse_and_determinism(mini: Path) -> None:
    write_pack(mini, "alpha-pack")
    write_pack(mini, "beta-pack", files=("README.md",))
    hits = run(mini, "search", "--scope", "all", "ALPHA", "cli").stdout.split("\n")
    assert hits[0].startswith("alpha-pack 1.0.0 thin active") and hits[1] == ""
    assert run(mini, "search", "--scope", "all", "nomatchterm").stdout == ""
    shown = json.loads(run(mini, "show", "beta-pack").stdout)
    assert shown["name"] == "beta-pack" and shown["tier"] == "thin" and shown["status"] == "active"
    assert run(mini, "show", "missing-pack").returncode == 2
    assert run(mini, "browse").returncode == 0
    first = (mini / tiers.BROWSE_RELATIVE).read_bytes()
    run(mini, "browse")
    assert (mini / tiers.BROWSE_RELATIVE).read_bytes() == first
    text = first.decode()
    assert text.startswith("# Pack Catalog") and "| alpha-pack | 1.0.0 | semantic | - | thin |" in text
    assert run(mini, "catalog", "--scope", "all").stdout == run(mini, "catalog", "--scope", "all").stdout


def test_real_repo_catalog_deterministic_and_browse_current() -> None:
    a = run(REPO, "catalog").stdout
    assert a == run(REPO, "catalog").stdout
    for p in json.loads(a)["packs"]:
        assert p["tier"] in {"thin", "documented", "verified"}
        assert p["status"] in {"active", "deprecated", "superseded"}
