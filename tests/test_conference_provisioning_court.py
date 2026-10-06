"""CG3 conference-commerce provisioning court: every AGNTCon customer who
purchased gets their AAIF solution deployed via the REAL
scripts/deploy_aaif_solution.py (10-step fail-closed pay-before-manufacture).

Customers come from the CG1 bridge fixture
(tests/test_conference_commerce_fixture.py): a real GCP-marketplace-sim HTTP
subprocess approves 25 accounts + entitlements; this court then runs the real
deployer subprocess once per customer.

Courts:
  1. Artifact set: every deployment's dist/ carries the full AAIF artifact
     set -- k8s/ namespace manifest, agent card (agent.json), MCP server
     surface (mcp_servers.json), AGENTS.md, actuation_plan.json.
  2. Uniqueness: every deployment's consequence digest (deployer graph_hash)
     is unique per customer -- no cross-customer manifest bleed.
  3. Determinism: redeploying the same customer is byte-identical (same
     graph_hash, byte-cmp of the dist tree, same receipt chain hash).
  4. Receipt chain: the shared paid-delivery chain grows by exactly 25 links
     (one per customer, no forks); the idempotent redeploy appends nothing.

Bounded scale: 25 customers in CI. The conference floor is 1,000 orgs
(CG1: 10 named sponsors/exhibitors + 990 smaller orgs); the CI run is the
1:40 scaled sample of the same machinery -- the real event runs the identical
fixture at n=1,000 with no code change.

Chicago discipline: no mocks. Real sim subprocess, real deployer subprocess,
real ggen manufacture, real filesystem dist/ trees, real hash-chained
paid-delivery receipts.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

from test_conference_commerce_fixture import (  # noqa: E402
    CI_BOUND,
    fixture_singleton,
    setup_customers,
)

DEPLOYER = ROOT / "scripts" / "deploy_aaif_solution.py"

AAIF = "https://aaif.io/ontology#"

QUERY = (
    f"PREFIX aaif: <{AAIF}>\n"
    "SELECT ?deployment WHERE { ?deployment a aaif:Deployment }\n"
    "ORDER BY ?deployment\n"
)


def _build_solution(root: Path, cid: str) -> Path:
    """Per-customer AAIF solution: namespace manifest + agent card + MCP
    server surface + AGENTS.md, all ggen-manufactured into dist/."""
    ns = cid.replace("-", "")
    solution_dir = root / f"solution-{cid}"
    solution_dir.mkdir(exist_ok=True)
    (solution_dir / "profile.json").write_text(json.dumps({
        "slug": cid,
        "namespace": ns,
        "replicas": 2,
        "finops_monthly_budget_usd": 5000.0,
        "siem_egress_endpoint": f"https://siem.{cid}.example.com/hec",
        "spiffe_trust_domain": f"{ns}.io",
    }, sort_keys=True, indent=2), encoding="utf-8")
    (solution_dir / "ontology.ttl").write_text(
        f"@prefix aaif: <{AAIF}> .\naaif:{ns}Deployment a aaif:Deployment .\n",
        encoding="utf-8")

    pack = solution_dir / "packs" / "tiny-pack"
    (pack / "queries").mkdir(parents=True, exist_ok=True)
    (pack / "templates").mkdir(parents=True, exist_ok=True)
    (pack / "queries" / "deployment.rq").write_text(QUERY, encoding="utf-8")
    templates = {
        "namespace.yaml.tmpl": (
            "apiVersion: v1\nkind: Namespace\nmetadata:\n"
            f"  name: {ns}\n"),
        "agent_card.json.tmpl": (
            "{\n"
            f'  "name": "agents/{cid}",\n'
            '  "description": "AAIF solution agent for AGNTCon customer '
            f'{cid}",\n'
            '  "version": "1.0.0",\n'
            '  "protocol_version": "1.0"\n'
            "}\n"),
        "mcp_servers.json.tmpl": json.dumps({
            "mcpServers": {
                f"{ns}-aaif": {
                    "command": "aaif-agent",
                    "args": ["serve", "--namespace", ns],
                },
            },
        }, indent=2) + "\n",
        "AGENTS.md.tmpl": (
            f"# AGENTS.md -- {cid}\n\n"
            "AAIF solution agent instructions, ggen-manufactured from the "
            "solution ontology.\n"),
    }
    for name, body in templates.items():
        (pack / "templates" / name).write_text(body, encoding="utf-8")

    (solution_dir / "ggen.toml").write_text(
        f'[project]\nname = "aaif-solution-{cid}"\nversion = "1.0.0"\n'
        '\n[ontology]\nsource = "ontology.ttl"\n'
        '\n[generation]\noutput_dir = "dist"\n'
        + "".join(
            f'\n[[generation.rules]]\nname = "{rule}"\nmode = "Overwrite"\n'
            'query = { file = "packs/tiny-pack/queries/deployment.rq" }\n'
            f'template = {{ file = "packs/tiny-pack/templates/{tmpl}" }}\n'
            f'output_file = "{out}"\n'
            for rule, tmpl, out in (
                ("namespace_manifest", "namespace.yaml.tmpl", "k8s/namespace.yaml"),
                ("agent_card", "agent_card.json.tmpl", "agent/agent.json"),
                ("mcp_servers", "mcp_servers.json.tmpl", "mcp/mcp_servers.json"),
                ("agents_md", "AGENTS.md.tmpl", "AGENTS.md"),
            ))
    )

    # Lock: solution.json last, digests over the inputs.
    from marketplace import fingerprint_paths
    pack_files = sorted(p for p in pack.rglob("*") if p.is_file())
    input_files = [
        p for p in solution_dir.rglob("*") if p.is_file()
        and p.name != "solution.json"
        and "dist" not in p.relative_to(solution_dir).parts]
    (solution_dir / "solution.json").write_text(json.dumps({
        "profile_sha256": fingerprint_paths(input_files, solution_dir),
        "packs": [{"name": "tiny-pack",
                   "path": "packs/tiny-pack",
                   "content_hash": fingerprint_paths(pack_files, pack)}],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return solution_dir


def _deploy(fx, solution_dir: Path, receipts_dir: Path) -> tuple[subprocess.CompletedProcess, str]:
    """Run the REAL deployer subprocess against the fixture's live sim.
    Returns (proc, slug)."""
    slug = solution_dir.name
    registry = solution_dir.parent / "monetization.toml"
    registry.write_text(
        'schema_version = "1.0.0"\n\n'
        '[monetization]\nbackend = "sim"\n'
        'billing_authorities = ["GOOGLE_CLOUD_MARKETPLACE"]\n'
        'provider_id = "demo-provider"\nunit_price_usd = 0.05\n\n'
        f"[solutions.{slug}]\nbackend = \"sim\"\n"
        'billing_authorities = ["GOOGLE_CLOUD_MARKETPLACE"]\n'
        "unit_price_usd = 0.05\n", encoding="utf-8")
    env = dict(os.environ)
    env["AAIF_ENTITLEMENT_ENDPOINT"] = fx.base
    proc = subprocess.run(
        [sys.executable, str(DEPLOYER),
         "--solution", str(solution_dir),
         "--out", str(solution_dir / "dist"),
         "--receipts-dir", str(receipts_dir),
         "--config", str(registry),
         "--target", "kind",
         "--entitlement-id", solution_dir.name.removeprefix("solution-")],
        env=env, capture_output=True, text=True, timeout=600)
    return proc, slug


def _tree_digest(d: Path) -> dict[str, str]:
    import hashlib
    out: dict[str, str] = {}
    for p in sorted(d.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(d))] = hashlib.sha256(
                p.read_bytes()).hexdigest()
    return out


# ---------------------------------------------------------------------------
# Shared wave state: one sim, 25 entitled customers, 25 real deploys
# ---------------------------------------------------------------------------
_WAVE: dict | None = None


def _wave() -> dict:
    global _WAVE
    if _WAVE is not None:
        return _WAVE
    if shutil.which("ggen") is None:
        pytest.skip("ggen not on PATH")
    fx = fixture_singleton()
    customers = setup_customers(CI_BOUND)
    receipts_dir = fx.tmp_root / "provisioning-receipts"
    deployments: dict[str, dict] = {}
    try:
        for rec in customers:
            cid = rec["cid"]
            solution_dir = _build_solution(fx.tmp_root, cid)
            proc, slug = _deploy(fx, solution_dir, receipts_dir)
            assert proc.returncode == 0, (
                f"deploy {cid} refused rc={proc.returncode}\n"
                f"stdout={proc.stdout}\nstderr={proc.stderr}")
            payload = json.loads(proc.stdout)
            dist = solution_dir / "dist"
            deployments[cid] = {
                "slug": slug,
                "solution_dir": solution_dir,
                "dist": dist,
                "graph_hash": payload["graph_hash"],
                "receipt_chain_hash": payload["receipt_chain_hash"],
                "files": payload["files"],
            }
    except Exception:
        fx.teardown()
        raise
    _WAVE = {"fx": fx, "receipts_dir": receipts_dir,
             "deployments": deployments,
             "cids": [r["cid"] for r in customers]}
    return _WAVE


@pytest.fixture(scope="module")
def wave():
    try:
        yield _wave()
    except Exception:
        fixture_singleton().teardown()
        raise


def teardown_module(module):
    fixture_singleton().teardown()


# ---------------------------------------------------------------------------
# Court 1: artifact set
# ---------------------------------------------------------------------------
class TestArtifactSet:
    def test_every_deployment_produces_full_artifact_set(self, wave):
        for cid, dep in wave["deployments"].items():
            dist = dep["dist"]
            for rel in ("k8s/namespace.yaml", "agent/agent.json",
                        "mcp/mcp_servers.json", "AGENTS.md",
                        "actuation_plan.json"):
                assert (dist / rel).is_file(), f"{cid}: missing {rel}"
            card = json.loads((dist / "agent/agent.json").read_text())
            assert card["name"] == f"agents/{cid}"
            mcp = json.loads((dist / "mcp/mcp_servers.json").read_text())
            assert f"{cid.replace('-', '')}-aaif" in mcp["mcpServers"]
            agents_md = (dist / "AGENTS.md").read_text()
            assert cid in agents_md

    def test_actuation_plan_targets_customer_solution(self, wave):
        for cid, dep in wave["deployments"].items():
            plan = json.loads((dep["dist"] / "actuation_plan.json").read_text())
            assert plan["slug"] == dep["slug"], (
                f"{cid}: actuation plan targets the wrong solution")
            ns = cid.replace("-", "")
            ns_manifest = (dep["dist"] / "k8s" / "namespace.yaml").read_text()
            assert f"name: {ns}" in ns_manifest, (
                f"{cid}: namespace manifest lost the customer namespace")


# ---------------------------------------------------------------------------
# Court 2: uniqueness (no cross-customer manifest bleed)
# ---------------------------------------------------------------------------
class TestConsequenceUniqueness:
    def test_graph_hash_unique_per_customer(self, wave):
        hashes = {cid: dep["graph_hash"] for cid, dep in wave["deployments"].items()}
        assert len(set(hashes.values())) == CI_BOUND, (
            "cross-customer consequence-digest collision")

    def test_no_cross_customer_bleed_in_manifests(self, wave):
        # No customer's dist mentions another customer's identity.
        for cid, dep in wave["deployments"].items():
            ns = cid.replace("-", "")
            for p in dep["dist"].rglob("*"):
                if p.is_file():
                    body = p.read_text(encoding="utf-8", errors="replace")
                    for other in wave["cids"]:
                        if other == cid:
                            continue
                        other_ns = other.replace("-", "")
                        assert other not in body and other_ns not in body, (
                            f"{cid}/{p.name}: bleed from {other}")


# ---------------------------------------------------------------------------
# Court 3: determinism (idempotent redeploy is byte-identical)
# ---------------------------------------------------------------------------
class TestRedeployDeterminism:
    def test_redeploy_same_customer_is_byte_identical(self, wave):
        cid = wave["cids"][0]
        dep = wave["deployments"][cid]
        before = _tree_digest(dep["dist"])
        chain_before = (wave["receipts_dir"] / "receipts" / "paid-delivery" / "chain.jsonl"
                        ).read_text(encoding="utf-8")

        proc, _ = _deploy(wave["fx"], dep["solution_dir"],
                          wave["receipts_dir"])
        assert proc.returncode == 0, (
            f"redeploy refused rc={proc.returncode}\n"
            f"stdout={proc.stdout}\nstderr={proc.stderr}")
        after = _tree_digest(dep["dist"])
        assert before == after, "redeploy manufactured a different dist tree"
        assert json.loads(proc.stdout)["graph_hash"] == dep["graph_hash"]
        # idempotent replay: the chain did NOT grow (no fork)
        assert (wave["receipts_dir"] / "receipts" / "paid-delivery" / "chain.jsonl"
                ).read_text(encoding="utf-8") == chain_before


# ---------------------------------------------------------------------------
# Court 4: receipt chain (25 links, one per customer, no forks)
# ---------------------------------------------------------------------------
class TestReceiptChain:
    def test_chain_grows_by_exactly_25_links(self, wave):
        import paid_delivery_receipt as pdr
        receipts_dir = wave["receipts_dir"]
        ok, problems = pdr.verify(receipts_dir)
        assert ok, problems
        chain = (receipts_dir / "receipts" / "paid-delivery" / "chain.jsonl").read_text(
            encoding="utf-8").splitlines()
        assert len(chain) == CI_BOUND
        slugs = [json.loads(line)["slug"] for line in chain]
        assert sorted(slugs) == sorted("solution-" + c for c in wave["cids"])
        assert len(set(slugs)) == CI_BOUND, "chain fork: duplicate slug links"
        # head anchor matches the chain head
        head = pdr.head_anchor_path(receipts_dir).read_text().strip()
        assert head == json.loads(chain[-1])["chain_hash_hex"]

    def test_redeploy_appends_no_link(self, wave):
        import paid_delivery_receipt as pdr
        receipts_dir = wave["receipts_dir"]
        chain_path = receipts_dir / "receipts" / "paid-delivery" / "chain.jsonl"
        n_before = len(chain_path.read_text(encoding="utf-8").splitlines())
        cid = wave["cids"][1]
        proc, _ = _deploy(wave["fx"],
                          wave["deployments"][cid]["solution_dir"],
                          receipts_dir)
        assert proc.returncode == 0, proc.stderr
        n_after = len(chain_path.read_text(encoding="utf-8").splitlines())
        assert n_after == n_before
        ok, problems = pdr.verify(receipts_dir)
        assert ok, problems
