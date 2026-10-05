"""Commerce-seam integration court: one real flow across four modules.

sim subprocess (ephemeral port, temp discovery dir) -> monetization registry
-> entitlement decision -> paid-delivery receipt chain -> tamper refusal.

Chicago style: real HTTP subprocess, real files, no mocks.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
SIM_SERVER = ROOT / "k8s" / "gcp-marketplace-sim" / "server.py"

DEP_FILES = [
    SCRIPTS / "marketplace_monetization.py",
    SCRIPTS / "entitlement.py",
    SCRIPTS / "paid_delivery_receipt.py",
]


def _deps_compilable() -> tuple[bool, str]:
    for f in DEP_FILES:
        if not f.is_file():
            return False, f"missing dependency file: {f}"
        try:
            compile(f.read_text(encoding="utf-8"), str(f), "exec")
        except SyntaxError as exc:
            return False, f"syntax error in {f.name}: {exc}"
    return True, ""


DEPS_OK, DEPS_WHY = _deps_compilable()

pytestmark = pytest.mark.skipif(not DEPS_OK, reason=DEPS_WHY)

# cryptography is imported by the sim server process (subprocess, not this
# interpreter), but a missing module there means the sim never serves.
CRYPTO_OK = (
    subprocess.run(
        [sys.executable, "-c", "import cryptography"],
        capture_output=True,
    ).returncode
    == 0
)
if not CRYPTO_OK:
    pytest.skip("cryptography not importable by the sim subprocess", allow_module_level=True)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class CommerceSim:
    """Real sim subprocess on an ephemeral port with a temp discovery dir."""

    def __init__(self, tmp_path: Path) -> None:
        self.port = _free_port()
        self.discovery_dir = tmp_path / "discovery"
        self.discovery_dir.mkdir()
        env = dict(os.environ)
        env["AAIF_SIM_PORT"] = str(self.port)
        env["AAIF_SIM_DISCOVERY_DIR"] = str(self.discovery_dir)
        self.proc = subprocess.Popen(
            [sys.executable, str(SIM_SERVER)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.base = f"http://127.0.0.1:{self.port}"

    def wait_ready(self, timeout: float = 15.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError("sim subprocess exited before becoming ready")
            try:
                with urllib.request.urlopen(f"{self.base}/healthz", timeout=1) as r:
                    if r.status == 200:
                        return
            except Exception:
                time.sleep(0.1)
        raise RuntimeError("sim did not become ready in time")

    def approve(self, entitlement_id: str) -> dict:
        url = f"{self.base}/v1/providers/demo-provider/entitlements/{entitlement_id}:approve"
        req = urllib.request.Request(
            url, data=json.dumps({}).encode(), method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())

    def stop(self) -> None:
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=5)


def _get(url: str) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, b""


@pytest.fixture()
def sim(tmp_path):
    s = CommerceSim(tmp_path)
    try:
        s.wait_ready()
        yield s
    finally:
        s.stop()


def _load_monetization():
    sys.path.insert(0, str(SCRIPTS))
    import marketplace_monetization as mm

    return mm


def test_commerce_seam_end_to_end(tmp_path, sim):
    mm = _load_monetization()
    import entitlement
    import paid_delivery_receipt as pdr

    ent_id = "ent-seam-e2e-001"

    # (1) monetization registry loads from the repo root; config is valid.
    config, problems = mm.load(ROOT)
    assert problems == []
    assert "_defaults" in config
    commerce = mm.effective_for(config, "seam-e2e")
    assert commerce["backend"] == "sim"
    assert commerce["billing_authorities"] == ["GOOGLE_CLOUD_MARKETPLACE"]

    # seed: real POST :approve against the running sim
    record = sim.approve(ent_id)
    assert record["state"] == "ENTITLEMENT_ACTIVE"

    # point the entitlement seam at the ephemeral sim
    os.environ["AAIF_ENTITLEMENT_ENDPOINT"] = sim.base

    # (2) entitlement.decide -> ALIVE + backend_standing SIMULATED
    decision = entitlement.decide(ent_id, commerce)
    assert decision["standing"] == "ALIVE", decision
    assert decision["backend_standing"] == "SIMULATED"
    assert decision["entitlement"]["state"] == "ENTITLEMENT_ACTIVE"

    # (3) append a paid-delivery receipt embedding the entitlement record
    receipts_dir = tmp_path / "receipts-root"
    slug = "seam-e2e"
    payload = {
        "solution": slug,
        "entitlement_id": ent_id,
        "entitlement": decision["entitlement"],
        "backend_standing": decision["backend_standing"],
        "consequence_digest": "sha256:" + "ab" * 32,
    }
    env = pdr.append(receipts_dir, slug, payload)
    chain = receipts_dir / "receipts" / "paid-delivery" / "chain.jsonl"
    assert chain.is_file()
    lines = [l for l in chain.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
    assert json.loads(lines[0])["chain_hash_hex"] == env["chain_hash_hex"]

    # (4) verify walks clean
    ok, problems2 = pdr.verify(receipts_dir)
    assert ok, problems2

    # (5) tamper the entitlement state field inside the chain payload -> refusal
    # naming the slug. Rewrite the stored entitlement state, leaving the hashes
    # untouched so payload re-hash catches it.
    tampered_env = json.loads(lines[0])
    tampered_env["payload"]["entitlement"]["state"] = "ENTITLEMENT_SUSPENDED"
    chain.write_text(json.dumps(tampered_env, sort_keys=True, separators=(",", ":")) + "\n")

    ok3, problems3 = pdr.verify(receipts_dir)
    assert not ok3
    joined = "\n".join(problems3)
    assert slug in joined
    assert "REFUSED_PAYLOAD_HASH_MISMATCH" in joined


def test_unapproved_entitlement_is_refused_before_any_receipt(tmp_path, sim):
    """Negative twin: an entitlement the sim never approved must not mint a receipt."""
    mm = _load_monetization()
    import entitlement
    import paid_delivery_receipt as pdr

    config, problems = mm.load(ROOT)
    assert problems == []
    commerce = mm.effective_for(config, "seam-e2e")

    os.environ["AAIF_ENTITLEMENT_ENDPOINT"] = sim.base
    decision = entitlement.decide("ent-never-approved", commerce)
    assert decision["standing"] == "BLOCKED"
    assert decision["refusal"] == entitlement.REFUSED_NOT_FOUND

    receipts_dir = tmp_path / "receipts-root"
    ok, problems2 = pdr.verify(receipts_dir)
    assert ok and problems2 == []  # empty chain, nothing paid, nothing delivered
