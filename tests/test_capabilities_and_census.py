"""Chicago-style tests: real files in a tempdir, real subprocess invocations."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAP = ROOT / "scripts" / "pack_capabilities.py"
CEN = ROOT / "scripts" / "workflow_census.py"


def run(script, *args, check=True):
    p = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
    if check:
        assert p.returncode == 0, p.stderr
    return p


def make_pack(root: Path, name: str, files: dict[str, str]) -> None:
    for rel, body in files.items():
        f = root / name / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(body, encoding="utf-8")


def allow(path: Path, entries):
    path.write_text(json.dumps({"network_in_gates": entries}), encoding="utf-8")


def test_capability_scan_classifies(tmp_path):
    packs = tmp_path / "packs"
    make_pack(packs, "a-pack", {
        "pack.toml": "",
        "gates/g.py": "import subprocess, os\nopen('x','w')\nos.environ.get('A')\n",
        "scripts/verify.py": "from pathlib import Path\nPath('f').write_text('x')\n",
    })
    p = run(CAP, "--packs-dir", str(packs))
    r = json.loads(p.stdout)
    files = r["packs"]["a-pack"]["files"]
    assert set(files["gates/g.py"]["capabilities"]) == {"exec", "fs-write", "env"}
    assert files["gates/g.py"]["role"] == "gate"
    assert files["scripts/verify.py"]["role"] == "verifier"
    assert p.stdout == run(CAP, "--packs-dir", str(packs)).stdout  # deterministic


def test_check_fails_only_on_new_gate_network(tmp_path):
    packs = tmp_path / "packs"
    make_pack(packs, "b-pack", {"gates/n.py": "import urllib.request\n", "scripts/t.py": "import socket\n"})
    al = tmp_path / "allow.json"
    allow(al, [])
    bad = run(CAP, "--check", "--packs-dir", str(packs), "--allowlist", str(al), check=False)
    assert bad.returncode == 1 and "packs/b-pack/gates/n.py" in bad.stderr.replace("\\", "/") or "b-pack/gates/n.py" in bad.stderr
    allow(al, ["packs/b-pack/gates/n.py"])
    assert run(CAP, "--check", "--packs-dir", str(packs), "--allowlist", str(al)).returncode == 0


def test_repo_passes_check_and_is_deterministic():
    assert run(CAP, "--check").returncode == 0
    assert run(CAP).stdout == run(CAP).stdout


def test_license_state(tmp_path):
    packs = tmp_path / "packs"
    make_pack(packs, "l-pack", {"LICENSE": "MIT"})
    make_pack(packs, "s-pack", {"x.md": "SPDX-License-Identifier: MIT"})
    make_pack(packs, "n-pack", {"x.md": "nothing"})
    r = json.loads(run(CAP, "--packs-dir", str(packs)).stdout)["packs"]
    assert r["l-pack"]["license"] == {"license_file": True, "spdx": False}
    assert r["s-pack"]["license"] == {"license_file": False, "spdx": True}
    assert r["n-pack"]["license"] == {"license_file": False, "spdx": False}


WF = """name: {name}
on:
  pull_request:
    paths:
      - 'packs/x/**'
  schedule:
    - cron: '1 2 * * 3'
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - run: echo {tag}
"""


def test_census_over_temp_workflows(tmp_path):
    d = tmp_path / "wf"
    d.mkdir()
    (d / "develop-thing-r5.yml").write_text(WF.format(name="Dev", tag="a"))
    (d / "misc.yml").write_text("name: Misc\non: push\njobs:\n  j:\n    runs-on: ubuntu-latest\n    steps:\n      - run: ls\n")
    (d / "ci.yml").write_text("name: CI\non: [pull_request]\njobs:\n  a:\n    runs-on: x\n    steps:\n      - run: echo misc.yml\n")
    c = json.loads(run(CEN, "--workflows-dir", str(d)).stdout)
    rows = {r["file"]: r for r in c["workflows"]}
    dev = rows["develop-thing-r5.yml"]
    assert dev["family"] == "develop" and dev["round"] == 5
    assert dev["pull_request"] and dev["on_schedule"] and not dev["push"]
    assert dev["path_filters"] == ["pull_request:packs/x/**"] and dev["schedule"] == ["1 2 * * 3"]
    assert rows["misc.yml"]["triggers"] == ["push"] and rows["misc.yml"]["in_ci_yml"]
    assert rows["ci.yml"]["triggers"] == ["pull_request"]
    assert c["ci_jobs"] == ["a"]


def test_consolidation_candidate_over_threshold(tmp_path):
    d = tmp_path / "wf"
    d.mkdir()
    for i in range(11):
        (d / f"measure-thing-r{i}.yml").write_text(WF.format(name=f"M{i}", tag=f"r{i}").replace("packs/x", f"packs/p{i}"))
    (d / "measure-odd.yml").write_text(WF.format(name="odd", tag="z").replace("echo", "python3 -c pass;"))
    c = json.loads(run(CEN, "--workflows-dir", str(d)).stdout)
    assert [x["count"] for x in c["consolidation_candidates"]] == [11]
    assert c["consolidation_candidates"][0]["family"] == "measure"


def test_census_repo_deterministic_and_readonly():
    before = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    mtimes = [f.stat().st_mtime_ns for f in before]
    a = run(CEN).stdout
    assert a == run(CEN).stdout
    assert json.loads(a)["total"] == len(before)
    assert mtimes == [f.stat().st_mtime_ns for f in before]


def test_generated_docs_match_scripts():
    # CANARY: when a new pack lands, regenerate docs/reference/*.md via the
    # scripts (--markdown) in the same commit — docs must track pack counts.
    for script, page in ((CAP, "pack-capabilities.md"), (CEN, "workflow-map.md")):
        assert (ROOT / "docs" / "reference" / page).read_text() == run(script, "--markdown").stdout


def test_check_refuses_unparseable_gate(tmp_path):
    packs = tmp_path / "packs"
    make_pack(packs, "p1", {"gates/bad.py": "import socket\ndef (:\n"})
    (packs / "p3" / "gates").mkdir(parents=True)
    (packs / "p3" / "gates" / "b.py").write_bytes(b"import socket\n\xff\xfe\n")
    al = tmp_path / "allow.json"
    allow(al, [])
    p = run(CAP, "--check", "--packs-dir", str(packs), "--allowlist", str(al), check=False)
    assert p.returncode == 1
    assert "UNPARSEABLE_GATE" in p.stderr and "p1/gates/bad.py" in p.stderr and "p3/gates/b.py" in p.stderr


def test_check_refuses_dynamic_import_in_gate(tmp_path):
    packs = tmp_path / "packs"
    make_pack(packs, "d", {"gates/g.py": "import importlib\nimportlib.import_module('soc'+'ket')\n"})
    al = tmp_path / "allow.json"
    allow(al, [])
    p = run(CAP, "--check", "--packs-dir", str(packs), "--allowlist", str(al), check=False)
    assert p.returncode == 1 and "UNDECLARED_DYNAMIC_CODE" in p.stderr


def test_check_typed_refusal_on_missing_inputs(tmp_path):
    al = tmp_path / "allow.json"
    allow(al, [])
    p = run(CAP, "--check", "--packs-dir", str(tmp_path / "nope"), "--allowlist", str(al), check=False)
    assert p.returncode == 2 and "REFUSED:PACKS_DIR_MISSING" in p.stderr and "Traceback" not in p.stderr
    (tmp_path / "packs").mkdir()
    q = run(CAP, "--check", "--packs-dir", str(tmp_path / "packs"), "--allowlist", str(tmp_path / "no.json"), check=False)
    assert q.returncode == 2 and "REFUSED:ALLOWLIST_UNREADABLE" in q.stderr and "Traceback" not in q.stderr
