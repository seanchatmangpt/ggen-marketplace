"""Chicago-style deployment court for scripts/deploy_aaif_solution.py (AAIF-DEPLOY-2026).

Disciplines (per ~/.claude/rules/testing-chicago-style.md):
- Real collaborators only: real subprocess deployer, real GCP commerce sim
  (k8s/gcp-marketplace-sim/server.py) on an ephemeral port, real ggen sync,
  real filesystem dist/ trees, real hash-chained paid-delivery receipts.
- No mocks, stubs, or monkeypatches. The sim is a real HTTP subprocess, not a fake.
- Pay-before-manufacture law: no dist/ may exist unless the entitlement gate
  (scripts/entitlement.py decide()) returned ALIVE first.
- Refusal ladder: typed exit codes per the deployer's house scheme
  (2=config / 6=registry / 8=scope / 9=digest).

Landed deployer interface this court pins (Lane 10):
- CLI: `python scripts/deploy_aaif_solution.py --solution <dir> --out <dir>
  --receipts-dir <dir> --config <monetization.toml> [--target kind|gke]`
- Solution dir: `solution.json` lock with {"profile_sha256", "packs":
  [{"name", "path", "content_hash"}, ...]} -- profile_sha256 is the
  fingerprint_paths fold over every solution input file except solution.json
  and dist/; each pack content_hash is the fold over that pack's files.
- Registry seam: `--config` pointing at a file literally named
  `monetization.toml` with [monetization] / [solutions.<slug>] tables.
- Entitlement seam: env `AAIF_ENTITLEMENT_ENDPOINT` (read by scripts/entitlement.py).
- Scope gate: importable `check_namespace_scope(dist_dir)` refusing
  cluster-scoped manifests with `REFUSED:MANIFEST_CLUSTER_SCOPED` (exit 8).
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

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "scripts" / "deploy_aaif_solution.py"
SIM = ROOT / "k8s" / "gcp-marketplace-sim" / "server.py"

AAIF = "https://aaif.io/ontology#"

PROFILE_BODY: dict = {
    "slug": "acme-corp",
    "namespace": "acme",
    "replicas": 2,
    "cmek_key": "projects/acme/locations/us/keyRings/kr/cryptoKeys/k",
    "finops_monthly_budget_usd": 5000.0,
    "siem_egress_endpoint": "https://siem.acme.com/hec",
    "spiffe_trust_domain": "acmecorp.io",
    "pqc_seal": True,
}

VALID_REGISTRY = """\
schema_version = "1.0.0"

[monetization]
backend = "sim"
billing_authorities = ["GOOGLE_CLOUD_MARKETPLACE"]
provider_id = "demo-provider"
unit_price_usd = 0.05

[solutions.acme-corp]
backend = "sim"
billing_authorities = ["GOOGLE_CLOUD_MARKETPLACE"]
unit_price_usd = 0.05
"""


def _scripts_on_path() -> None:
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)


def _import_deploy():
    """Lazy import of the deployer module; skip (not fail) while Lane 10 is in flight."""
    if not DEPLOY.is_file():
        pytest.skip("scripts/deploy_aaif_solution.py not on disk yet (Lane 10)")
    _scripts_on_path()
    import importlib
    return importlib.import_module("deploy_aaif_solution")


def _import_monetization():
    _scripts_on_path()
    import marketplace_monetization
    return marketplace_monetization


def _fingerprint(files: list[Path], base: Path) -> str:
    from marketplace import fingerprint_paths
    return fingerprint_paths(files, base)


def _write_registry(tmp_path: Path, toml_text: str) -> Path:
    """The deployer's --config must be a file literally named monetization.toml."""
    reg = tmp_path / "monetization.toml"
    reg.write_text(toml_text, encoding="utf-8")
    return reg


def _deploy(tmp_path: Path, solution_dir: Path, receipts_dir: Path,
            config: Path | None = None, env_extra: dict | None = None,
            target: str = "kind", entitlement_id: str | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.pop("AAIF_ENTITLEMENT_ENDPOINT", None)
    env.update(env_extra or {})
    cmd = [sys.executable, str(DEPLOY), "--solution", str(solution_dir),
           "--out", str(solution_dir / "dist"),
           "--receipts-dir", str(receipts_dir), "--target", target]
    if entitlement_id is not None:
        cmd += ["--entitlement-id", entitlement_id]
    if config is not None:
        cmd += ["--config", str(config)]
    return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True,
                          timeout=300)


def _write_solution(tmp_path: Path, profile_sha256: str | None = None) -> Path:
    """Build a solution dir per the landed lock schema.

    Layout:
      solution-acme/
        profile.json                    customer profile body
        ontology.ttl                    minimal graph (one aaif:Deployment)
        ggen.toml                       generation contract -> dist/k8s/namespace.yaml
        packs/tiny-pack/{queries,templates}/   local pack (content_hash locked)
        solution.json                   lock (written last: digests cover inputs)
    """
    solution_dir = tmp_path / "solution-acme"
    solution_dir.mkdir(exist_ok=True)
    (solution_dir / "profile.json").write_text(
        json.dumps(PROFILE_BODY, sort_keys=True, indent=2), encoding="utf-8")
    (solution_dir / "ontology.ttl").write_text(
        f"@prefix aaif: <{AAIF}> .\n"
        "aaif:acmeDeployment a aaif:Deployment .\n",
        encoding="utf-8",
    )
    pack_dir = solution_dir / "packs" / "tiny-pack"
    (pack_dir / "queries").mkdir(parents=True, exist_ok=True)
    (pack_dir / "templates").mkdir(parents=True, exist_ok=True)
    (pack_dir / "queries" / "namespace.rq").write_text(
        f"PREFIX aaif: <{AAIF}>\n"
        "SELECT ?deployment WHERE { ?deployment a aaif:Deployment }\n"
        "ORDER BY ?deployment\n",
        encoding="utf-8",
    )
    (pack_dir / "templates" / "namespace.yaml.tmpl").write_text(
        "apiVersion: v1\n"
        "kind: Namespace\n"
        "metadata:\n"
        "  name: acme\n",
        encoding="utf-8",
    )
    (solution_dir / "ggen.toml").write_text(
        '[project]\n'
        'name = "aaif-solution-acme-corp"\n'
        'version = "0.1.0"\n'
        '\n'
        '[ontology]\n'
        'source = "ontology.ttl"\n'
        '\n'
        '[generation]\n'
        'output_dir = "dist"\n'
        '\n'
        '[[generation.rules]]\n'
        'name = "namespace_manifest"\n'
        'mode = "Overwrite"\n'
        'query = { file = "packs/tiny-pack/queries/namespace.rq" }\n'
        'template = { file = "packs/tiny-pack/templates/namespace.yaml.tmpl" }\n'
        'output_file = "k8s/namespace.yaml"\n',
        encoding="utf-8",
    )

    # Pack content hashes: fingerprint_paths fold over each pack's files.
    pack_files = sorted(p for p in pack_dir.rglob("*") if p.is_file())
    packs = [{
        "name": "tiny-pack",
        "path": "packs/tiny-pack",
        "content_hash": _fingerprint(pack_files, pack_dir),
    }]

    # profile_sha256: fold over every input file except solution.json and dist/.
    input_files = [
        p for p in solution_dir.rglob("*")
        if p.is_file() and p.name != "solution.json"
        and "dist" not in p.relative_to(solution_dir).parts
    ]
    (solution_dir / "solution.json").write_text(
        json.dumps({
            "profile_sha256": profile_sha256 or _fingerprint(input_files, solution_dir),
            "packs": packs,
        }, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return solution_dir


def _import_entitlement_paths():
    import paid_delivery_receipt
    return paid_delivery_receipt


class _Sim:
    """Real sim subprocess lifecycle: ephemeral port + temp discovery dir."""

    def __init__(self, tmp_path: Path):
        self.port = _free_port()
        self.discovery_dir = tmp_path / "sim-discovery"
        self.discovery_dir.mkdir()
        self.proc: subprocess.Popen | None = None

    def __enter__(self):
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
                raise RuntimeError("sim exited early")
            try:
                with urllib.request.urlopen(
                        f"http://127.0.0.1:{self.port}/healthz", timeout=2) as r:
                    if r.status == 200:
                        return self
            except Exception:
                time.sleep(0.1)
        raise RuntimeError("sim did not become healthy")

    def __exit__(self, *exc):
        if self.proc and self.proc.poll() is not None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        return False

    def seed(self, account_id: str = "acc-001", entitlement_id: str = "ent-001") -> None:
        base = f"http://127.0.0.1:{self.port}"
        for path, body in (
            (f"/v1/accounts/{account_id}:approve", {}),
            (f"/v1/entitlements/ent-001:approve",
             {"account": f"providers/demo-provider/accounts/{account_id}",
              "plan": "enterprise-unlimited"}),
        ):
            req = urllib.request.Request(
                base + path, data=json.dumps(body).encode(), method="POST",
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                assert r.status == 200

    @property
    def endpoint(self) -> str:
        return f"http://127.0.0.1:{self.port}"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# ---------------------------------------------------------------------------
# Pay-before-manufacture
# ---------------------------------------------------------------------------

class TestPayBeforeManufacture:
    def test_deploy_without_entitlement_refuses_and_manufactures_nothing(self, tmp_path):
        """Sim down => entitlement gate BLOCKED => nonzero exit, NO dist/, names entitlement."""
        solution_dir = _write_solution(tmp_path)
        receipts_dir = tmp_path / "receipts-root"
        # No sim running: nothing listens on the endpoint; point at a dead port.
        result = _deploy(tmp_path, solution_dir, receipts_dir,
                         config=_write_registry(tmp_path, VALID_REGISTRY),
                         env_extra={"AAIF_ENTITLEMENT_ENDPOINT":
                                    f"http://127.0.0.1:{_free_port()}"})
        assert result.returncode != 0
        assert not (solution_dir / "dist").exists()
        assert "entitlement" in (result.stdout + result.stderr).lower()
        # and no receipt minted for an unpaid delivery
        assert not any(receipts_dir.rglob("chain.jsonl"))


# ---------------------------------------------------------------------------
# Refusal ladder
# ---------------------------------------------------------------------------

class TestRefusalLadder:
    def test_missing_solution_lock_exit_2(self, tmp_path):
        solution_dir = tmp_path / "empty-solution"
        solution_dir.mkdir()
        result = _deploy(tmp_path, solution_dir, tmp_path / "receipts-root",
                         config=_write_registry(tmp_path, VALID_REGISTRY))
        assert result.returncode == 2
        assert "solution.json" in (result.stdout + result.stderr)

    def test_tampered_profile_digest_exit_9(self, tmp_path):
        solution_dir = _write_solution(tmp_path, profile_sha256="f" * 64)
        result = _deploy(tmp_path, solution_dir, tmp_path / "receipts-root",
                         config=_write_registry(tmp_path, VALID_REGISTRY))
        assert result.returncode == 9
        assert "REFUSED" in (result.stdout + result.stderr)

    def test_dual_billing_authorities_exit_6(self, tmp_path):
        reg = _write_registry(tmp_path, """\
schema_version = "1.0.0"

[monetization]
backend = "sim"
billing_authorities = ["GOOGLE_CLOUD_MARKETPLACE"]
unit_price_usd = 0.05

[solutions.acme-corp]
billing_authorities = ["GOOGLE_CLOUD_MARKETPLACE", "AWS_MARKETPLACE"]
""")
        solution_dir = _write_solution(tmp_path)
        result = _deploy(tmp_path, solution_dir, tmp_path / "receipts-root", config=reg)
        assert result.returncode == 6
        assert "REFUSED" in (result.stdout + result.stderr)

    def test_unknown_backend_exit_6(self, tmp_path):
        reg = _write_registry(tmp_path, """\
schema_version = "1.0.0"

[monetization]
backend = "sim"
billing_authorities = ["GOOGLE_CLOUD_MARKETPLACE"]
unit_price_usd = 0.05

[solutions.acme-corp]
backend = "carrier-pigeon"
""")
        solution_dir = _write_solution(tmp_path)
        result = _deploy(tmp_path, solution_dir, tmp_path / "receipts-root", config=reg)
        assert result.returncode == 6
        assert "REFUSED" in (result.stdout + result.stderr)

    def test_budget_guard_refused_budget_exceeded(self, tmp_path):
        """unit_price_usd <= 0 => REFUSED_BUDGET_EXCEEDED (closes Lane 18 drift c)."""
        reg = _write_registry(tmp_path, """\
schema_version = "1.0.0"

[monetization]
backend = "sim"
billing_authorities = ["GOOGLE_CLOUD_MARKETPLACE"]
unit_price_usd = 0.05

[solutions.acme-corp]
unit_price_usd = 0.0
""")
        solution_dir = _write_solution(tmp_path)
        result = _deploy(tmp_path, solution_dir, tmp_path / "receipts-root", config=reg)
        assert result.returncode != 0
        assert "BUDGET_EXCEEDED" in (result.stdout + result.stderr)


# ---------------------------------------------------------------------------
# Happy path: kind rail, live sim, real ggen sync, byte-identical replay
# ---------------------------------------------------------------------------

def _snapshot(dist: Path) -> dict[str, bytes]:
    return {str(p.relative_to(dist)): p.read_bytes()
            for p in sorted(dist.rglob("*")) if p.is_file()}


class TestHappyPathKindRail:
    def test_happy_path_kind_rail(self, tmp_path):
        if shutil.which("ggen") is None:
            pytest.skip("ggen binary not on PATH")
        solution_dir = _write_solution(tmp_path)
        receipts_dir = tmp_path / "receipts-root"
        with _Sim(tmp_path) as sim:
            sim.seed()
            first = _deploy(tmp_path, solution_dir, receipts_dir,
                            config=_write_registry(tmp_path, VALID_REGISTRY),
                            env_extra={"AAIF_ENTITLEMENT_ENDPOINT": sim.endpoint},
                            entitlement_id="ent-001")
            assert first.returncode == 0, first.stdout + first.stderr
            dist = solution_dir / "dist"
            assert dist.is_dir() and any(dist.iterdir())
            assert (dist / "actuation_plan.json").is_file()
            manifests = [p for p in dist.rglob("*") if p.suffix in {".yaml", ".yml", ".json"}]
            assert manifests
            # receipt appended to the tmp receipts-dir chain
            chain = receipts_dir / "receipts" / "paid-delivery" / "chain.jsonl"
            assert chain.is_file()
            lines = [json.loads(line)
                     for line in chain.read_text(encoding="utf-8").splitlines() if line.strip()]
            assert len(lines) == 1
            assert lines[0]["chain_rule"] == "paid-delivery-chain/v1"
            # byte-identical replay: redeploy from identical inputs. The deployer
            # is fail-closed on an existing dist/, and ggen sync drops runtime
            # state (.ggen, .ggen-v2, .clap-noun-verb) into the solution dir, so
            # restore pristine inputs (remove dist + ggen runtime state) and
            # compare the dist snapshots.
            before = _snapshot(dist)
            shutil.rmtree(dist)
            for state in (".ggen", ".ggen-v2", ".clap-noun-verb"):
                shutil.rmtree(solution_dir / state, ignore_errors=True)
            second = _deploy(tmp_path, solution_dir, receipts_dir,
                             config=_write_registry(tmp_path, VALID_REGISTRY),
                             env_extra={"AAIF_ENTITLEMENT_ENDPOINT": sim.endpoint},
                             entitlement_id="ent-001")
            assert second.returncode == 0, second.stdout + second.stderr
            assert _snapshot(dist) == before


# ---------------------------------------------------------------------------
# Idempotent redeploy
# ---------------------------------------------------------------------------


def _relock(solution_dir: Path) -> None:
    """Recompute solution.json over the CURRENT inputs (after a profile edit)."""
    pack_dir = solution_dir / "packs" / "tiny-pack"
    pack_files = sorted(p for p in pack_dir.rglob("*") if p.is_file())
    input_files = [
        p for p in solution_dir.rglob("*")
        if p.is_file() and p.name != "solution.json"
        and "dist" not in p.relative_to(solution_dir).parts
    ]
    (solution_dir / "solution.json").write_text(
        json.dumps({
            "profile_sha256": _fingerprint(input_files, solution_dir),
            "packs": [{
                "name": "tiny-pack",
                "path": "packs/tiny-pack",
                "content_hash": _fingerprint(pack_files, pack_dir),
            }],
        }, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _clear_runtime_state(solution_dir: Path) -> None:
    for state in (".ggen", ".ggen-v2", ".clap-noun-verb"):
        shutil.rmtree(solution_dir / state, ignore_errors=True)


def _chain_lines(receipts_dir: Path) -> list[dict]:
    chain = receipts_dir / "receipts" / "paid-delivery" / "chain.jsonl"
    return [json.loads(line) for line in chain.read_text(encoding="utf-8").splitlines()
            if line.strip()]


class TestIdempotentRedeploy:
    def test_dist_exists_without_prior_receipt_refused_exit_2(self, tmp_path):
        """No prior receipt => the original DIST_ALREADY_EXISTS refusal holds."""
        deploy = _import_deploy()
        solution_dir = _write_solution(tmp_path)
        dist = solution_dir / "dist"
        dist.mkdir()
        (dist / "stale.txt").write_text("orphan", encoding="utf-8")
        with pytest.raises(deploy.Refused) as ei:
            deploy.entitlement_gate("ent-001", {}, dist, allow_existing=False)
        assert ei.value.exit_code == 2
        assert "DIST_ALREADY_EXISTS" in str(ei.value)

    def test_redeploy_over_existing_dist_unchanged_inputs_exit_0_byte_identical(self, tmp_path):
        """Second deploy with dist/ present + matching prior receipt => exit 0,
        byte-identical dist, chain NOT forked (replay returns existing envelope)."""
        if shutil.which("ggen") is None:
            pytest.skip("ggen binary not on PATH")
        solution_dir = _write_solution(tmp_path)
        receipts_dir = tmp_path / "receipts-root"
        with _Sim(tmp_path) as sim:
            sim.seed()
            env = {"AAIF_ENTITLEMENT_ENDPOINT": sim.endpoint}
            reg = _write_registry(tmp_path, VALID_REGISTRY)
            first = _deploy(tmp_path, solution_dir, receipts_dir, config=reg,
                            env_extra=env, entitlement_id="ent-001")
            assert first.returncode == 0, first.stdout + first.stderr
            dist = solution_dir / "dist"
            before = _snapshot(dist)
            first_chain_hash = json.loads(first.stdout)["receipt_chain_hash"]

            # Redeploy WITHOUT deleting dist/ -- but ggen drops runtime state
            # into the solution dir, which would trip the lock digest check.
            _clear_runtime_state(solution_dir)
            second = _deploy(tmp_path, solution_dir, receipts_dir, config=reg,
                             env_extra=env, entitlement_id="ent-001")
            assert second.returncode == 0, second.stdout + second.stderr
            assert _snapshot(dist) == before
            assert json.loads(second.stdout)["receipt_chain_hash"] == first_chain_hash
            # replay must not fork the chain
            assert len(_chain_lines(receipts_dir)) == 1

    def test_redeploy_changed_profile_exit_9_non_monotonic_grant(self, tmp_path):
        """Changed inputs under an already-paid slug => NON_MONOTONIC_GRANT (exit 9)."""
        if shutil.which("ggen") is None:
            pytest.skip("ggen binary not on PATH")
        solution_dir = _write_solution(tmp_path)
        receipts_dir = tmp_path / "receipts-root"
        with _Sim(tmp_path) as sim:
            sim.seed()
            env = {"AAIF_ENTITLEMENT_ENDPOINT": sim.endpoint}
            reg = _write_registry(tmp_path, VALID_REGISTRY)
            first = _deploy(tmp_path, solution_dir, receipts_dir, config=reg,
                            env_extra=env, entitlement_id="ent-001")
            assert first.returncode == 0, first.stdout + first.stderr

            _clear_runtime_state(solution_dir)
            # Change a real generation input: the manifest template (the
            # namespace name flows into the manufactured dist, so the
            # consequence digest changes). profile.json alone does not reach
            # the dist under this solution's ggen.toml generation contract.
            tmpl = solution_dir / "packs" / "tiny-pack" / "templates" / "namespace.yaml.tmpl"
            tmpl.write_text(tmpl.read_text(encoding="utf-8").replace("acme", "acme-v2"),
                            encoding="utf-8")
            _relock(solution_dir)

            second = _deploy(tmp_path, solution_dir, receipts_dir, config=reg,
                             env_extra=env, entitlement_id="ent-001")
            out = second.stdout + second.stderr
            assert second.returncode == 9, out
            assert "NON_MONOTONIC_GRANT" in out
            # the chain still holds exactly the original grant
            assert len(_chain_lines(receipts_dir)) == 1


# ---------------------------------------------------------------------------
# Forged prior receipt (AE2 finding 3): redeploy is never granted from an
# unverified receipt; the dist/ must survive the refusal untouched.
# ---------------------------------------------------------------------------


def _forge_prior_receipt(receipts_dir: Path, slug: str, payload_hash: str) -> Path:
    """A structurally valid JSON envelope with a WRONG payload_hash and no
    chain line (or: appended to a tampered chain in the caller)."""
    pdr = _import_paid_delivery_receipt()
    sub = receipts_dir / pdr.SUBDIR
    sub.mkdir(parents=True, exist_ok=True)
    env = {
        "schema": "ggen-receipt/v2",
        "activity": "aaif.paid-delivery",
        "slug": slug,
        "ts_ns": 0,
        "payload": {"schema": "https://ggen.dev/marketplace/paid-delivery/v1"},
        "payload_hash_hex": payload_hash,
        "prev_chain_hash_hex": pdr.GENESIS,
        "chain_hash_hex": "e" * 64,
        "chain_rule": "paid-delivery-chain/v1",
    }
    path = sub / f"{slug}.json"
    path.write_text(json.dumps(env, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _import_paid_delivery_receipt():
    _scripts_on_path()
    import paid_delivery_receipt
    return paid_delivery_receipt


class TestForgedPriorReceipt:
    def test_prior_receipt_unit_forged_payload_hash_refused_exit_13(self, tmp_path):
        deploy = _import_deploy()
        receipts_dir = tmp_path / "receipts-root"
        _forge_prior_receipt(receipts_dir, "solution-acme", "0" * 64)
        with pytest.raises(deploy.Refused) as ei:
            deploy.prior_receipt(receipts_dir, "solution-acme")
        assert ei.value.exit_code == 13
        assert "PRIOR_RECEIPT_INVALID" in str(ei.value)

    def test_deploy_with_forged_prior_receipt_exit_13_dist_preserved(self, tmp_path):
        """The attack: drop a forged 'paid' receipt next to an existing dist/
        to trick the deployer into rmtree'ing the dist. Must refuse exit 13
        BEFORE the rmtree, leaving the dist byte-for-byte intact."""
        if shutil.which("ggen") is None:
            pytest.skip("ggen binary not on PATH")  # noqa: unreachable guard keeps court uniform
        solution_dir = _write_solution(tmp_path)
        receipts_dir = tmp_path / "receipts-root"
        dist = solution_dir / "dist"
        dist.mkdir()
        sentinel = dist / "sentinel.txt"
        sentinel.write_text("do-not-delete", encoding="utf-8")
        _forge_prior_receipt(receipts_dir, "solution-acme", "f" * 64)
        result = _deploy(tmp_path, solution_dir, receipts_dir,
                         config=_write_registry(tmp_path, VALID_REGISTRY))
        out = result.stdout + result.stderr
        assert result.returncode == 13, out
        assert "PRIOR_RECEIPT_INVALID" in out
        assert sentinel.is_file() and sentinel.read_text() == "do-not-delete"
        assert not any(receipts_dir.rglob("HEAD"))

    def test_deploy_with_tampered_chain_refused_exit_13(self, tmp_path):
        """Honest chain, then tampered mid-payload: full-chain verify fails =>
        redeploy refused even though the slug file itself looks clean."""
        deploy = _import_deploy()
        pdr = _import_paid_delivery_receipt()
        receipts_dir = tmp_path / "receipts-root"
        env = pdr.append(receipts_dir, "solution-acme", {"legit": True})
        # tamper the slug file in place (payload no longer folds to payload_hash)
        path = receipts_dir / pdr.SUBDIR / "solution-acme.json"
        forged = json.loads(path.read_text(encoding="utf-8"))
        forged["payload"]["injected"] = True
        path.write_text(json.dumps(forged, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with pytest.raises(deploy.Refused) as ei:
            deploy.prior_receipt(receipts_dir, "solution-acme")
        assert ei.value.exit_code == 13
        assert "PRIOR_RECEIPT_INVALID" in str(ei.value)
        assert env["chain_hash_hex"]  # sanity: chain existed before tamper

    def test_honest_prior_receipt_still_honored(self, tmp_path):
        """The precondition TestIdempotentRedeploy relies on: an honest chain +
        matching payload hash => prior_receipt returns the envelope."""
        deploy = _import_deploy()
        pdr = _import_paid_delivery_receipt()
        receipts_dir = tmp_path / "receipts-root"
        env = pdr.append(receipts_dir, "solution-acme", {"legit": True})
        got = deploy.prior_receipt(receipts_dir, "solution-acme")
        assert got is not None
        assert got["chain_hash_hex"] == env["chain_hash_hex"]


# ---------------------------------------------------------------------------
# AE2 finding 7: post-manufacture input re-verification. ggen sync re-reads
# inputs under its own process; a file changed between the pre-check and the
# sync is manufactured without digest coverage. The deployer must re-fold the
# inputs after manufacture, quarantine dist/ on drift, and refuse typed.
# ---------------------------------------------------------------------------


class TestPostManufactureInputDrift:
    def test_drifted_input_refused_exit_9_dist_quarantined(self, tmp_path):
        """(a) Capture the lock over clean inputs, mutate a generation input
        AFTER the pre-check would have run, then run the post-manufacture
        verify: REFUSED:INPUT_DRIFT_DURING_MANUFACTURE (exit 9) and the dist/
        is quarantined (deleted) -- no artifact manufactured from unadmitted
        inputs survives."""
        deploy = _import_deploy()
        solution_dir = _write_solution(tmp_path)
        lock = deploy.read_solution_lock(solution_dir)
        # dist exists as if ggen sync had just manufactured it
        dist = solution_dir / "dist"
        (dist / "k8s").mkdir(parents=True)
        (dist / "k8s" / "namespace.yaml").write_text(
            "apiVersion: v1\nkind: Namespace\nmetadata:\n  name: acme\n",
            encoding="utf-8",
        )
        # mutate a real input, leaving the lock stale (the mid-manufacture edit)
        tmpl = solution_dir / "packs" / "tiny-pack" / "templates" / "namespace.yaml.tmpl"
        tmpl.write_text(tmpl.read_text(encoding="utf-8").replace("acme", "acme-evil"),
                        encoding="utf-8")
        with pytest.raises(deploy.Refused) as ei:
            deploy.verify_inputs_post(solution_dir, lock, dist)
        assert ei.value.exit_code == 9
        assert "INPUT_DRIFT_DURING_MANUFACTURE" in str(ei.value)
        # quarantine: the artifact is gone
        assert not dist.exists()

    def test_unchanged_inputs_post_check_passes_receipt_caries_closure(self, tmp_path):
        """(b) Happy path: unchanged inputs -> post-check returns the folds;
        the receipt payload's closure block carries
        input_digest_verified_post: true."""
        deploy = _import_deploy()
        solution_dir = _write_solution(tmp_path)
        lock = deploy.read_solution_lock(solution_dir)
        dist = solution_dir / "dist"
        dist.mkdir()
        profile, pack_folds = deploy.verify_inputs_post(solution_dir, lock, dist)
        assert profile == lock["profile_sha256"]
        assert len(pack_folds) == len(lock["packs"])

        receipts_dir = tmp_path / "receipts-root"
        receipt = deploy.write_receipt(
            receipts_dir,
            "solution-acme",
            {"backend": "sim"},
            {"target": "kind", "target_standing": "SIMULATED"},
            graph_hash="a" * 64,
        )
        assert receipt["payload"]["closure"] == {"input_digest_verified_post": True}


# ---------------------------------------------------------------------------
# Namespace-scope gate
# ---------------------------------------------------------------------------

class TestScopeGate:
    def test_cluster_role_manifest_refused_exit_8(self, tmp_path):
        deploy = _import_deploy()
        dist = tmp_path / "dist"
        (dist / "k8s").mkdir(parents=True)
        (dist / "k8s" / "clusterrole.yaml").write_text(
            "apiVersion: rbac.authorization.k8s.io/v1\n"
            "kind: ClusterRole\n"
            "metadata:\n  name: aaif-scope-probe\n"
            "rules:\n- apiGroups: [\"*\"]\n  resources: [\"*\"]\n  verbs: [\"*\"]\n",
            encoding="utf-8",
        )
        with pytest.raises(deploy.Refused) as ei:
            deploy.check_namespace_scope(dist)
        assert ei.value.exit_code == 8
        assert "MANIFEST_CLUSTER_SCOPED" in str(ei.value)
