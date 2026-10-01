"""Lifecycle registry (lifecycle.toml): real files, real subprocess, no mocks."""

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


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "marketplace.py"), *args],
        cwd=root, capture_output=True, text=True, check=False,
    )


def write_pack(root: Path, name: str, extra_toml: str = "") -> None:
    d = root / "packs" / name
    d.mkdir(parents=True)
    (d / "pack.toml").write_text(
        f'[pack]\nname = "{name}"\nversion = "1.0.0"\ndescription = "Pack {name} for rust cli"\n{extra_toml}',
        encoding="utf-8",
    )
    (d / "ontology.ttl").write_text("@prefix ex: <http://example.org/> .\n", encoding="utf-8")


def write_registry(root: Path, body: str) -> None:
    (root / "lifecycle.toml").write_text(f'schema_version = "1.0.0"\n{body}', encoding="utf-8")


def refusals(root: Path) -> str:
    result = run(root, "validate")
    assert result.returncode == 2, result.stdout
    return result.stderr


@pytest.fixture()
def mini(tmp_path: Path) -> Path:
    """A self-contained marketplace with three packs and no registry."""
    shutil.copytree(REPO / "scripts", tmp_path / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(REPO / "marketplace.toml", tmp_path / "marketplace.toml")
    for rel in marketplace.REQUIRED_DOCS:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("stub\n", encoding="utf-8")
    (tmp_path / "packs").mkdir()
    for name in ("old-pack", "new-pack", "peer-pack"):
        write_pack(tmp_path, name)
    return tmp_path


def catalog(root: Path) -> dict[str, dict]:
    result = run(root, "catalog", "--scope", "all")
    assert result.returncode == 0, result.stderr
    return {p["name"]: p for p in json.loads(result.stdout)["packs"]}


def test_absent_registry_is_empty_and_projects_null_lifecycle(mini: Path) -> None:
    assert run(mini, "validate").returncode == 0
    recs = catalog(mini)
    assert all(r["lifecycle"] is None and r["status"] == "active" for r in recs.values())
    assert run(mini, "lifecycle").stdout == ""


def test_states_and_intents_project_into_catalog(mini: Path) -> None:
    write_registry(
        mini,
        '''
[packs.old-pack]
state = "superseded"
successors = ["new-pack"]
reason = "absorbed by new-pack"
since = "v1.0.0"

[packs.new-pack]
intent = "consolidate"
related = ["peer-pack"]
reason = "same target paths as peer-pack"

[packs.peer-pack]
intent = "upgrade"
reason = "pinned toolchain drifted"
''',
    )
    assert run(mini, "validate").returncode == 0
    recs = catalog(mini)
    assert recs["old-pack"]["status"] == "superseded" and recs["old-pack"]["deprecated"] is True
    assert recs["old-pack"]["successors"] == ["new-pack"]
    assert recs["new-pack"]["status"] == "active" and recs["new-pack"]["deprecated"] is False
    assert recs["new-pack"]["lifecycle"]["intent"] == "consolidate"
    assert recs["new-pack"]["lifecycle"]["related"] == ["peer-pack"]
    listing = run(mini, "lifecycle", "--intent", "upgrade").stdout.splitlines()
    assert listing == ["peer-pack active upgrade - pinned toolchain drifted"]
    assert run(mini, "lifecycle", "--state", "superseded").stdout.startswith("old-pack superseded - new-pack ")


@pytest.mark.parametrize(
    ("body", "code"),
    [
        ('[packs.ghost-pack]\nintent = "review"\nreason = "x"\n', "LIFECYCLE_PACK_UNKNOWN:ghost-pack"),
        ('[packs.old-pack]\nstate = "zombie"\nreason = "x"\n', "LIFECYCLE_STATE_UNKNOWN:old-pack"),
        ('[packs.old-pack]\nintent = "delete"\nreason = "x"\n', "LIFECYCLE_INTENT_UNKNOWN:old-pack"),
        ('[packs.old-pack]\nintent = "review"\n', "LIFECYCLE_REASON_MISSING:old-pack"),
        ('[packs.old-pack]\nstate = "active"\nreason = "x"\n', "LIFECYCLE_ENTRY_EMPTY:old-pack"),
        ('[packs.old-pack]\nintent = "review"\nreason = "x"\nbogus = 1\n', "LIFECYCLE_KEY_UNKNOWN:old-pack:bogus"),
        ('[packs.old-pack]\nstate = "superseded"\nreason = "x"\n', "LIFECYCLE_SUCCESSOR_REQUIRED:old-pack"),
        ('[packs.old-pack]\nintent = "replace"\nreason = "x"\n', "LIFECYCLE_SUCCESSORS_REQUIRED:old-pack"),
        ('[packs.old-pack]\nintent = "consolidate"\nreason = "x"\n', "LIFECYCLE_RELATED_REQUIRED:old-pack"),
        ('[packs.old-pack]\nstate = "deprecated"\nsuccessors = ["old-pack"]\nreason = "x"\n', "LIFECYCLE_SUCCESSOR_SELF:old-pack"),
        ('[packs.old-pack]\nstate = "deprecated"\nsuccessors = ["nope"]\nreason = "x"\n', "LIFECYCLE_SUCCESSOR_UNKNOWN:old-pack:nope"),
        ('[packs.old-pack]\nintent = "consolidate"\nrelated = ["nope"]\nreason = "x"\n', "LIFECYCLE_RELATED_UNKNOWN:old-pack:nope"),
        ('[packs.old-pack]\nintent = "review"\nreason = "x"\nsince = "26.9.1"\n', "LIFECYCLE_SINCE_FORMAT:old-pack"),
        ('[packs.old-pack]\nintent = "review"\nreason = "x"\nevidence = ["docs/nope.md"]\n', "LIFECYCLE_EVIDENCE_MISSING:old-pack:docs/nope.md"),
        ('[packs.old-pack]\nintent = "keep-separate"\nrelated = ["peer-pack"]\nstate = "deprecated"\nsuccessors = ["new-pack"]\nreason = "x"\n', "LIFECYCLE_KEEP_SEPARATE_STATE:old-pack"),
    ],
)
def test_malformed_entries_are_refused_with_typed_codes(mini: Path, body: str, code: str) -> None:
    write_registry(mini, "\n" + body)
    assert f"REFUSED:{code}" in refusals(mini)


def test_successor_must_be_live(mini: Path) -> None:
    write_registry(
        mini,
        '''
[packs.old-pack]
state = "superseded"
successors = ["new-pack"]
reason = "x"

[packs.new-pack]
state = "retired"
successors = ["peer-pack"]
reason = "x"
''',
    )
    assert "REFUSED:LIFECYCLE_SUCCESSOR_NOT_LIVE:old-pack:new-pack" in refusals(mini)


def test_registry_cannot_contradict_legacy_manifest_keys(mini: Path) -> None:
    shutil.rmtree(mini / "packs" / "old-pack")
    write_pack(mini, "old-pack", "deprecated = true\n")
    write_registry(mini, '\n[packs.old-pack]\nintent = "review"\nreason = "x"\n')
    assert "REFUSED:LIFECYCLE_MANIFEST_CONFLICT:old-pack" in refusals(mini)


def test_bad_schema_version_and_invalid_toml(mini: Path) -> None:
    (mini / "lifecycle.toml").write_text('schema_version = "9.9.9"\n', encoding="utf-8")
    assert "REFUSED:LIFECYCLE_SCHEMA_VERSION" in refusals(mini)
    (mini / "lifecycle.toml").write_text("not = [valid\n", encoding="utf-8")
    assert "REFUSED:LIFECYCLE_TOML_INVALID" in refusals(mini)


def test_repository_registry_is_admitted_and_cannot_change_generation_inputs() -> None:
    """The committed registry validates, and flagging never touches archive bytes or fingerprints."""
    assert run(REPO, "validate").returncode == 0
    packs = {p.name: p for p in marketplace.require_admitted()}
    for name, entry in marketplace.lifecycle_registry().items():
        assert name in packs
        record = packs[name].catalog_record()
        assert record["status"] == entry.get("state", "active")
        assert record["digest"].startswith("sha256:")
