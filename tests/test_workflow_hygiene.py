"""Workflow supply-chain hygiene: parseable, SHA-pinned, least-privilege."""
import re
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import pin_actions  # noqa: E402

WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.y*ml"))
SHA = re.compile(r"^[0-9a-f]{40}$")


def _load(path):
    return yaml.safe_load(path.read_text())


def _uses(doc):
    for job in doc["jobs"].values():
        if "uses" in job:
            yield job["uses"]
        for step in job.get("steps", []) or []:
            if "uses" in step:
                yield step["uses"]


def test_workflows_exist():
    assert WORKFLOWS


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_parses_and_has_jobs(path):
    doc = _load(path)
    assert isinstance(doc, dict) and doc.get("jobs")


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_every_uses_is_sha_pinned(path):
    for ref in _uses(_load(path)):
        if ref.startswith("./") or ref.startswith("docker://"):
            continue
        assert "@" in ref and SHA.match(ref.rsplit("@", 1)[1]), f"{path.name}: {ref}"


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_has_permissions(path):
    doc = _load(path)
    assert "permissions" in doc or all("permissions" in j for j in doc["jobs"].values()), path.name


def test_pin_actions_check_agrees():
    assert list(pin_actions.scan()) == []
    assert pin_actions.main(["--check"]) == 0


def test_pin_actions_check_detects_unpinned(tmp_path):
    (tmp_path / "w.yml").write_text(
        "jobs:\n  a:\n    runs-on: x\n    steps:\n"
        "      - uses: actions/checkout@v7\n      - uses: ./local\n      - uses: docker://alpine:3\n"
    )
    found = list(pin_actions.scan(tmp_path))
    assert [(t, r) for _p, _n, _m, t, r in found] == [("actions/checkout", "v7")]
    assert pin_actions.main(["--check", "--workflows", str(tmp_path)]) == 1


def test_publish_attests_provenance():
    doc = _load(ROOT / ".github/workflows/publish.yml")
    perms = doc["jobs"]["release"]["permissions"]
    assert perms["id-token"] == "write" and perms["attestations"] == "write"
    steps = doc["jobs"]["release"]["steps"]
    att = [s for s in steps if s.get("uses", "").startswith("actions/attest-build-provenance@")]
    assert att and "catalog.json" in att[0]["with"]["subject-path"]
    assert any("release-check" in s.get("run", "") for s in steps)
