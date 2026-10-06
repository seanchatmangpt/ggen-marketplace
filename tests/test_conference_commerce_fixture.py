"""Conference-commerce bridge fixture (CG1) — AGNTCon exhibitor floor as
GCP Marketplace customers over the REAL commerce sim.

Chicago style (per ~/.claude/rules/testing-chicago-style.md):
- Real HTTP sim subprocess (k8s/gcp-marketplace-sim/server.py), real account
  :approve and entitlement :approve calls, real deploy_aaif_solution.py
  subprocess for deploys, real temp dirs. No mocks.

Exposed API for other CG lanes:
    from test_conference_commerce_fixture import (
        COMPANIES, TIERS, setup_customers, entitle, deploy, fixture_singleton,
    )
    customers = setup_customers(25)          # (n, sim_port=None)
    entitle("akamai")                        # idempotent re-approve
    deploy("akamai")                         # real deployer subprocess (ggen)

Teardown: fixture_singleton().teardown() kills the sim and removes temp dirs.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
DEPLOYER = SCRIPTS / "deploy_aaif_solution.py"
SIM = ROOT / "k8s" / "gcp-marketplace-sim" / "server.py"

AAIF = "https://aaif.io/ontology#"

# ---------------------------------------------------------------------------
# AGNTCon sponsor/exhibitor floor: 10 named orgs + 990 smaller orgs = 1,000
# total. CI bounds the floor to 25 customers.
# ---------------------------------------------------------------------------
COMPANIES: list[tuple[str, str]] = [
    ("akamai", "sponsor"),
    ("anthropic", "sponsor"),
    ("aws", "sponsor"),
    ("google-cloud", "sponsor"),
    ("block", "platinum"),
    ("solo-io", "platinum"),
    ("temporal", "platinum"),
    ("neo4j", "platinum"),
    ("red-hat", "gold"),
    ("datadog", "gold"),
]

# tier -> Marketplace solution profile (plan name on the wire).
TIERS: dict[str, str] = {
    "sponsor": "enterprise-aaif",
    "platinum": "enterprise-aaif",
    "gold": "team-aaif",
    "small": "team-aaif",
}

CI_BOUND = 25


def company_floor(n: int) -> list[tuple[str, str]]:
    """The exhibitor floor bounded to n customers: named orgs first, then
    smaller orgs (of the 990) as `small` tier."""
    if n > 1000:
        raise ValueError("conference floor is 1,000 orgs; n must be <= 1000")
    floor = list(COMPANIES)
    for i in range(len(COMPANIES), n):
        floor.append((f"org-{i:03d}", "small"))
    return floor[:n]


# ---------------------------------------------------------------------------
# Real sim lifecycle
# ---------------------------------------------------------------------------
def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class ConferenceCommerceFixture:
    """Owns one real sim subprocess and the customer/entitlement state."""

    def __init__(self) -> None:
        self.port = _free_port()
        self.tmp_root = Path(
            __import__("tempfile").mkdtemp(prefix="cg1-fixture-"))
        self.discovery_dir = self.tmp_root / "discovery"
        self.discovery_dir.mkdir()
        self.proc: subprocess.Popen | None = None
        self.customers: dict[str, dict] = {}
        self.deploy_state: dict[str, dict] = {}

    # -- lifecycle ------------------------------------------------------
    def start(self) -> "ConferenceCommerceFixture":
        if self.proc is not None and self.proc.poll() is None:
            return self
        env = dict(os.environ)
        env["AAIF_SIM_PORT"] = str(self.port)
        env["AAIF_SIM_DISCOVERY_DIR"] = str(self.discovery_dir)
        self.proc = subprocess.Popen(
            [sys.executable, str(SIM)], cwd=ROOT, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        deadline = time.time() + 30
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError("sim subprocess exited before serving")
            try:
                with urllib.request.urlopen(
                        f"{self.base}/healthz", timeout=2) as r:
                    if r.status == 200:
                        return self
            except Exception:
                time.sleep(0.1)
        raise RuntimeError("sim did not become healthy in 30s")

    def teardown(self) -> None:
        if self.proc is not None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
            self.proc = None
        shutil.rmtree(self.tmp_root, ignore_errors=True)

    @property
    def base(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    # -- wire helpers ---------------------------------------------------
    def _post(self, path: str, body: dict) -> dict:
        req = urllib.request.Request(
            self.base + path, data=json.dumps(body).encode(), method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())

    def _get(self, path: str) -> dict:
        with urllib.request.urlopen(self.base + path, timeout=10) as resp:
            return json.loads(resp.read())

    def approve_account(self, cid: str) -> dict:
        return self._post(f"/v1/accounts/{cid}:approve", {})

    def approve_entitlement(self, cid: str, plan: str) -> dict:
        return self._post(
            f"/v1/entitlements/{cid}:approve",
            {"account": f"providers/demo-provider/accounts/{cid}",
             "plan": plan})

    # -- public fixture API ---------------------------------------------
    def setup_customers(self, n: int = CI_BOUND,
                        sim_port: int | None = None) -> list[dict]:
        """Create n customer accounts via the real sim approve flow, each with
        an active entitlement. If sim_port is given, an EXTERNAL sim on that
        port is used (fixture does not spawn or own it); otherwise the fixture
        spawns its own sim on an ephemeral port."""
        if sim_port is not None:
            self.port = sim_port
            self.proc = None  # external sim: teardown() will not kill it
            self.tmp_root = Path(
                __import__("tempfile").mkdtemp(prefix="cg1-fixture-ext-"))
        self.start()
        floor = company_floor(n)
        out = []
        for cid, tier in floor:
            account = self.approve_account(cid)
            plan = TIERS[tier]
            entitlement = self.approve_entitlement(cid, plan)
            rec = {
                "cid": cid,
                "tier": tier,
                "plan": plan,
                "account": account,
                "entitlement": entitlement,
            }
            self.customers[cid] = rec
            out.append(rec)
        return out

    def entitle(self, cid: str) -> dict:
        """Idempotent entitlement re-approve; asserts the record is ACTIVE."""
        rec = self.customers[cid]
        ent = self.approve_entitlement(cid, rec["plan"])
        assert ent["state"] == "ENTITLEMENT_ACTIVE", ent
        rec["entitlement"] = ent
        return ent

    def deploy(self, cid: str) -> dict:
        """Real deploy_aaif_solution.py subprocess for this customer.

        Builds a per-customer solution dir (profile + tiny local pack +
        solution.json lock) in the fixture temp root, points
        AAIF_ENTITLEMENT_ENDPOINT at the sim, and runs the real deployer.
        Requires `ggen` on PATH. Returns the paid-delivery receipt payload.
        """
        if shutil.which("ggen") is None:
            raise RuntimeError("REFUSED:GGEN_NOT_FOUND (ggen not on PATH)")
        rec = self.customers[cid]
        ns = cid.replace("-", "")
        solution_dir = self.tmp_root / f"solution-{cid}"
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
        pack_dir = solution_dir / "packs" / "tiny-pack"
        (pack_dir / "queries").mkdir(parents=True, exist_ok=True)
        (pack_dir / "templates").mkdir(parents=True, exist_ok=True)
        (pack_dir / "queries" / "namespace.rq").write_text(
            f"PREFIX aaif: <{AAIF}>\n"
            "SELECT ?deployment WHERE { ?deployment a aaif:Deployment }\n"
            "ORDER BY ?deployment\n", encoding="utf-8")
        (pack_dir / "templates" / "namespace.yaml.tmpl").write_text(
            f"apiVersion: v1\nkind: Namespace\nmetadata:\n  name: {ns}\n",
            encoding="utf-8")
        (solution_dir / "ggen.toml").write_text(
            '[project]\nname = "aaif-solution-' + cid + '"\nversion = "0.1.0"\n'
            '\n[ontology]\nsource = "ontology.ttl"\n'
            '\n[generation]\noutput_dir = "dist"\n'
            '\n[[generation.rules]]\nname = "namespace_manifest"\n'
            'mode = "Overwrite"\n'
            'query = { file = "packs/tiny-pack/queries/namespace.rq" }\n'
            'template = { file = "packs/tiny-pack/templates/namespace.yaml.tmpl" }\n'
            'output_file = "k8s/namespace.yaml"\n', encoding="utf-8")
        sys.path.insert(0, str(SCRIPTS))
        from marketplace import fingerprint_paths
        pack_files = sorted(p for p in pack_dir.rglob("*") if p.is_file())
        input_files = [
            p for p in solution_dir.rglob("*") if p.is_file()
            and p.name != "solution.json"
            and "dist" not in p.relative_to(solution_dir).parts]
        (solution_dir / "solution.json").write_text(json.dumps({
            "profile_sha256": fingerprint_paths(input_files, solution_dir),
            "packs": [{"name": "tiny-pack",
                       "path": "packs/tiny-pack",
                       "content_hash": fingerprint_paths(pack_files, pack_dir)}],
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        registry = self.tmp_root / "monetization.toml"
        registry.write_text(
            'schema_version = "1.0.0"\n\n'
            "[monetization]\nbackend = \"sim\"\n"
            'billing_authorities = ["GOOGLE_CLOUD_MARKETPLACE"]\n'
            'provider_id = "demo-provider"\nunit_price_usd = 0.05\n\n'
            f"[solutions.{cid}]\nbackend = \"sim\"\n"
            'billing_authorities = ["GOOGLE_CLOUD_MARKETPLACE"]\n'
            "unit_price_usd = 0.05\n", encoding="utf-8")

        receipts_dir = self.tmp_root / "receipts" / cid
        out_dir = solution_dir / "dist"
        env = dict(os.environ)
        env["AAIF_ENTITLEMENT_ENDPOINT"] = self.base
        proc = subprocess.run(
            [sys.executable, str(DEPLOYER),
             "--solution", str(solution_dir),
             "--out", str(out_dir),
             "--receipts-dir", str(receipts_dir),
             "--config", str(registry),
             "--target", "kind",
             "--entitlement-id", cid],
            env=env, capture_output=True, text=True, timeout=600)
        assert proc.returncode == 0, (
            f"deploy {cid} refused rc={proc.returncode}\n"
            f"stdout={proc.stdout}\nstderr={proc.stderr}")
        receipt_files = sorted(receipts_dir.rglob("*.json"))
        assert receipt_files, "deployer wrote no paid-delivery receipt"
        receipt = json.loads(receipt_files[-1].read_text(encoding="utf-8"))
        self.deploy_state[cid] = {"solution_dir": solution_dir,
                                  "receipt": receipt,
                                  "rc": proc.returncode}
        return receipt


_SINGLETON: ConferenceCommerceFixture | None = None


def fixture_singleton() -> ConferenceCommerceFixture:
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = ConferenceCommerceFixture()
    return _SINGLETON


def setup_customers(n: int = CI_BOUND,
                    sim_port: int | None = None) -> list[dict]:
    return fixture_singleton().setup_customers(n, sim_port)


def entitle(cid: str) -> dict:
    return fixture_singleton().entitle(cid)


def deploy(cid: str) -> dict:
    return fixture_singleton().deploy(cid)


# ---------------------------------------------------------------------------
# Self-test court (Chicago): real sim, real approves, 25 ACTIVE customers
# ---------------------------------------------------------------------------
class TestConferenceCommerceFixture:
    def test_25_customers_all_active(self):
        fx = fixture_singleton()
        try:
            customers = fx.setup_customers(CI_BOUND)
        except Exception:
            fx.teardown()
            raise
        assert len(customers) == CI_BOUND
        summary = fx._get("/v1/billing/summary")
        accounts = summary["accounts"]
        entitlements = summary["entitlements"]
        cids = {r["cid"] for r in customers}
        # the sim pre-seeds a default ent-001; scope to the fixture's floor
        assert cids <= set(accounts) and set(entitlements) >= cids
        assert len(accounts) >= CI_BOUND
        for rec in customers:
            cid, tier = rec["cid"], rec["tier"]
            assert accounts[cid]["state"] == "ACCOUNT_ACTIVE"
            ent = entitlements[cid]
            assert ent["state"] == "ENTITLEMENT_ACTIVE"
            assert ent["plan"] == TIERS[tier]
            assert ent["account"] == f"providers/demo-provider/accounts/{cid}"
        # tier mapping: named sponsors/platinum -> enterprise-aaif
        assert rec_of("akamai")["plan"] == "enterprise-aaif"
        assert rec_of("datadog")["plan"] == "team-aaif"
        # idempotent re-entitle
        ent = entitle("anthropic")
        assert ent["state"] == "ENTITLEMENT_ACTIVE"

    def test_1000_bound_refused(self):
        with pytest.raises(ValueError):
            company_floor(1001)

    def test_importable_helper_api(self):
        # Other CG lanes import these module-level names.
        import test_conference_commerce_fixture as m
        assert callable(m.setup_customers)
        assert callable(m.entitle)
        assert callable(m.deploy)
        assert len(m.COMPANIES) == 10


def rec_of(cid: str) -> dict:
    return fixture_singleton().customers[cid]


def teardown_module(module):
    fixture_singleton().teardown()
