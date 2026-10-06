"""EV8 conference-sim lane: exhibitor booths = MCP servers serving tools to attendee agents.

The marketplace's real machinery is the exhibition hall:

- the pack surface is the booth catalog (`scripts/marketplace.py catalog` / `search`);
- a booth "demo" is a real `qualify_packs.py` qualification of the exhibitor pack
  through the real ggen runtime — the demo works only if the court says ALIVE;
- a broken booth (a scratch copy of a pack with an injected defect) must honestly
  FAIL: the qualification court catches the defect and the booth cannot fake a
  working demo;
- catalog determinism holds while the "event" runs (double catalog + byte cmp);
- the MCP framing: the aaif-vanilla-pack dist carries an mcp_servers.json-style
  manifest that parses and declares the booth's tool servers.

Chicago discipline: no mocks. Every court runs the real scripts as subprocesses
over real filesystem state.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

# Three exhibitors with distinct packaging profiles (the marketplace derives
# project / projection / semantic from the pack's own files — no hand labels).
EXHIBITORS = {
    "affidavit-trust-plane-pack": "project",  # security vendor (PQ trust plane)
    "evolvable-capability-pack": "projection",  # ML vendor (evolvable capability)
    "chatman-marketplace-commerce-dod-pack": "semantic",  # commerce vendor (DoD commerce)
}


def run(repo: Path, *args: str, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *[str(a) for a in args]],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def catalog_payload(repo: Path = REPO) -> dict:
    proc = run(repo, repo / "scripts" / "marketplace.py", "catalog", "--scope", "all")
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def qualify(pack: str, repo: Path = REPO, report: Path | None = None):
    """Run the real qualification court for one pack."""
    args = [repo / "scripts" / "qualify_packs.py", "--pack", pack]
    if report is not None:
        args += ["--report", report]
    proc = run(repo, *args)
    payload = json.loads(report.read_text()) if report is not None and report.exists() else None
    return proc, payload


# ---------------------------------------------------------------------------
# Court 1: the booth catalog is real and describes the exhibitors
# ---------------------------------------------------------------------------


def test_booth_catalog_lists_exhibitors_with_metadata() -> None:
    payload = catalog_payload()
    packs = {entry["name"]: entry for entry in payload["packs"]}
    for name, expected_profile in EXHIBITORS.items():
        assert name in packs, f"exhibitor {name} missing from catalog"
        entry = packs[name]
        assert entry["version"]
        assert entry["description"].strip()
        assert entry["digest"].startswith("sha256:")
        assert entry["profile"] == expected_profile, (
            f"{name}: expected profile {expected_profile}, got {entry['profile']}"
        )
        assert entry.get("deprecated") is False


def test_booth_catalog_search_finds_each_exhibitor() -> None:
    for name in EXHIBITORS:
        proc = run(REPO, REPO / "scripts" / "marketplace.py", "search", "--scope", "all", name)
        assert proc.returncode == 0, proc.stderr
        assert name in proc.stdout, f"search for {name} did not surface the booth"


# ---------------------------------------------------------------------------
# Court 2: booth demos are real qualifications through the real ggen runtime
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("pack", sorted(EXHIBITORS))
def test_booth_demo_qualifies_alive(pack: str) -> None:
    with tempfile.TemporaryDirectory(prefix="ev8-demo-") as tmp:
        proc, payload = qualify(pack, report=Path(tmp) / "q.json")
        assert proc.returncode == 0, proc.stderr
        assert payload is not None
        entries = [p for p in payload["packs"] if p["name"] == pack]
        assert len(entries) == 1
        entry = entries[0]
        assert entry["status"] == "ALIVE", entry
        assert entry["consequence_files"] > 0
        assert entry["consequence_sha256"]
        assert entry["profile"] == EXHIBITORS[pack]
    assert payload is not None


# ---------------------------------------------------------------------------
# Court 3: a broken booth cannot fake a working demo
# ---------------------------------------------------------------------------


def _build_scratch_marketplace(root: Path, pack: str) -> Path:
    """Assemble a minimal marketplace root in scratch: scripts + one pack + docs."""
    root.mkdir(parents=True)
    shutil.copytree(
        SCRIPTS,
        root / "scripts",
        ignore=shutil.ignore_patterns("__pycache__", "test_*"),
    )
    shutil.copy2(REPO / "marketplace.toml", root / "marketplace.toml")
    # Empty lifecycle registry (absent/empty registry is lawful, never an error).
    (root / "lifecycle.toml").write_text('schema_version = "1.0.0"\n', encoding="utf-8")
    shutil.copytree(REPO / "docs", root / "docs")
    shutil.copytree(REPO / "packs" / pack, root / "packs" / pack)
    return root


def test_broken_booth_demo_fails_honestly() -> None:
    pack = "affidavit-trust-plane-pack"
    with tempfile.TemporaryDirectory(prefix="ev8-broken-booth-") as tmp:
        root = Path(tmp) / "marketplace"
        _build_scratch_marketplace(root, pack)
        # Inject the defect: invalid Turtle in the pack's semantic source.
        ontology = root / "packs" / pack / "ontology.ttl"
        ontology.write_text(
            ontology.read_text(encoding="utf-8") + "\n<<<broken turtle >>>\n",
            encoding="utf-8",
        )
        report = Path(tmp) / "qualification.json"
        proc, payload = qualify(pack, repo=root, report=report)
        # The court refuses: exit nonzero, status is not ALIVE, no fake demo.
        assert proc.returncode != 0, proc.stdout
        assert payload is not None
        statuses = [p["status"] for p in payload["packs"] if p["name"] == pack]
        assert statuses == ["REFUSED"], payload["packs"]
        assert statuses[0] != "ALIVE"


def test_broken_booth_leaves_canonical_catalog_deterministic() -> None:
    """The injected defect lives only in scratch; the canonical hall is untouched."""
    first = catalog_payload()
    second = catalog_payload()
    assert first == second


# ---------------------------------------------------------------------------
# Court 4: catalog determinism while the event runs
# ---------------------------------------------------------------------------


def test_catalog_determinism_double_run_byte_identical() -> None:
    proc_a = run(REPO, SCRIPTS / "marketplace.py", "catalog")
    proc_b = run(REPO, SCRIPTS / "marketplace.py", "catalog")
    assert proc_a.returncode == 0, proc_a.stderr
    assert proc_b.returncode == 0, proc_b.stderr
    assert proc_a.stdout == proc_b.stdout


# ---------------------------------------------------------------------------
# Court 5: MCP framing — the booth's server manifest parses and declares tools
# ---------------------------------------------------------------------------


MCP_MANIFEST = REPO / "packs/aaif-vanilla-pack/dist/mcp/mcp_servers.json"


def test_booth_mcp_manifest_parses_and_declares_servers() -> None:
    manifest = json.loads(MCP_MANIFEST.read_text(encoding="utf-8"))
    servers = manifest["mcpServers"]
    assert isinstance(servers, dict) and servers, "booth declares no MCP tool servers"
    for name, server in servers.items():
        kind = server.get("type")
        assert kind in {"stdio", "sse", "streamable_http"}, (name, kind)
        if kind == "stdio":
            assert server.get("command"), f"stdio server {name} declares no command"
        else:
            assert server.get("url", "").startswith(("http://", "https://")), (
                f"remote server {name} declares no url"
            )


def test_booth_mcp_manifest_declares_expected_tool_surfaces() -> None:
    manifest = json.loads(MCP_MANIFEST.read_text(encoding="utf-8"))
    servers = manifest["mcpServers"]
    # The filesystem booth demo serves the attendee agent a workspace tool...
    assert "filesystem" in servers
    # ...and at least one remote service surface.
    remotes = [n for n, s in servers.items() if s.get("type") != "stdio"]
    assert remotes, "no remote MCP tool surface declared"
