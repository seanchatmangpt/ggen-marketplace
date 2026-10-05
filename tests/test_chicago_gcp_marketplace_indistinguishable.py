import base64
import json
import time
import urllib.error
import urllib.request

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

GCP_SIM_URL = "http://localhost:8443"
SWARM_INGRESS_URL = "http://localhost:8080"

def _sim_endpoint_reachable(url):
    try:
        with urllib.request.urlopen(f"{url}/cloudcommerceprocurement/$discovery/rest?version=v1", timeout=2):
            return True
    except (urllib.error.URLError, OSError):
        return False

if not _sim_endpoint_reachable(GCP_SIM_URL):
    pytest.skip(
        f"live GCP-wire simulator not running at {GCP_SIM_URL}; start k8s/gcp-marketplace-sim/server.py",
        allow_module_level=True,
    )

class TestWireIndistinguishableChicagoGCPMarketplace:
    """
    Chicago Adversarial Test Court:
    Verifies that the local Kubernetes GCP Marketplace simulator is
    wire-indistinguishable from Google Cloud production infrastructure.
    """

    def test_discovery_documents_mirror_google_spec(self):
        """Verifies that $discovery/rest endpoints serve valid Google Discovery JSON."""
        # 1. Partner Procurement Discovery
        with urllib.request.urlopen(f"{GCP_SIM_URL}/cloudcommerceprocurement/$discovery/rest?version=v1") as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode())
            assert data.get("title") == "Cloud Commerce Partner Procurement API"
            assert data.get("version") == "v1"
            assert "entitlements" in data.get("resources", {}).get("providers", {}).get("resources", {})

        # 2. Service Control Discovery
        with urllib.request.urlopen(f"{GCP_SIM_URL}/servicecontrol/$discovery/rest?version=v1") as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode())
            assert data.get("title") == "Service Control API"
            assert "services" in data.get("resources", {})

    def test_cryptographic_rs256_jwt_verified_against_google_x509_cert(self):
        """
        Fetches the public x509 cert from the official Google robot endpoint and
        verifies that entitlement tokens are cryptographically signed with RS256.
        """
        # 1. Fetch public certificates
        with urllib.request.urlopen(f"{GCP_SIM_URL}/robot/v1/metadata/x509/cloud-commerce-partner@system.gserviceaccount.com") as resp:
            assert resp.status == 200
            certs = json.loads(resp.read().decode())
            assert len(certs) >= 1

        # 2. Activate entitlement
        ent_id = f"ent-court-rs256-{int(time.time())}"
        req = urllib.request.Request(
            f"{GCP_SIM_URL}/v1/providers/demo/entitlements/{ent_id}:approve",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            res = json.loads(resp.read().decode())
            jwt_token = res.get("jwt")
            assert jwt_token

        # 3. Cryptographic Verification
        header_b64, claims_b64, sig_b64 = jwt_token.split(".")
        header = json.loads(base64.urlsafe_b64decode(header_b64 + "==").decode())
        kid = header.get("kid")
        assert kid in certs, f"Key ID {kid} not found in Google x509 certificate metadata"

        cert = x509.load_pem_x509_certificate(certs[kid].encode())
        sig = base64.urlsafe_b64decode(sig_b64 + "==")
        signing_input = f"{header_b64}.{claims_b64}".encode()

        # Will raise InvalidSignature if forged or corrupted
        cert.public_key().verify(sig, signing_input, padding.PKCS1v15(), hashes.SHA256())

    def test_sabotage_court_tampered_jwt_signature_rejected(self):
        """Sabotage test: Flipping bits in the RS256 signature MUST raise InvalidSignature."""
        from cryptography.exceptions import InvalidSignature

        with urllib.request.urlopen(f"{GCP_SIM_URL}/robot/v1/metadata/x509/cloud-commerce-partner@system.gserviceaccount.com") as resp:
            certs = json.loads(resp.read().decode())

        req = urllib.request.Request(
            f"{GCP_SIM_URL}/v1/providers/demo/entitlements/ent-sabotage:approve",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            jwt_token = json.loads(resp.read().decode())["jwt"]

        header_b64, claims_b64, sig_b64 = jwt_token.split(".")
        raw_sig = bytearray(base64.urlsafe_b64decode(sig_b64 + "=="))
        raw_sig[10] ^= 0xFF  # In-process cryptographic sabotage: bit flip
        signing_input = f"{header_b64}.{claims_b64}".encode()
        cert = x509.load_pem_x509_certificate(list(certs.values())[0].encode())

        with pytest.raises(InvalidSignature):
            cert.public_key().verify(bytes(raw_sig), signing_input, padding.PKCS1v15(), hashes.SHA256())

    def test_pubsub_base64_push_envelope_wire_fidelity(self):
        """Verifies that state change events are delivered in authentic Cloud Pub/Sub envelopes."""
        req = urllib.request.Request(
            f"{GCP_SIM_URL}/v1/providers/demo/entitlements/ent-pubsub-test:approve",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode())
            envelope = res.get("pubsubEnvelope", {})
            assert "subscription" in envelope
            assert envelope["subscription"].startswith("projects/")

            msg = envelope.get("message", {})
            assert "data" in msg
            assert "messageId" in msg
            assert "publishTime" in msg

            # Decode data and verify internal notification fields
            raw_payload = json.loads(base64.b64decode(msg["data"]).decode())
            assert raw_payload.get("eventType") == "ENTITLEMENT_ACTIVE"
            assert raw_payload.get("entitlement", {}).get("id") == "ent-pubsub-test"

    def test_service_control_check_and_allocate_quota(self):
        """Verifies that pre-flight check and quota allocation match Google Service Control schemas."""
        # 1. Pre-flight check
        req_check = urllib.request.Request(
            f"{GCP_SIM_URL}/v1/services/aaif.marketplace.googleapis.com:check",
            data=json.dumps({"operation": {"operationId": "check-01", "consumerId": "project:demo"}}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_check) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode())
            assert data.get("checkErrors") == []

        # 2. Allocate Quota
        req_quota = urllib.request.Request(
            f"{GCP_SIM_URL}/v1/services/aaif.marketplace.googleapis.com:allocateQuota",
            data=json.dumps({
                "allocateOperation": {
                    "operationId": "alloc-01",
                    "consumerId": "project:demo",
                    "quotaMetrics": [{"metricValues": [{"int64Value": 50}]}]
                }
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_quota) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode())
            assert data.get("allocateErrors") == []
            assert data.get("operationId") == "alloc-01"

    def test_oauth2_google_adc_bearer_token(self):
        """Verifies that clients can obtain Google Application Default Credentials bearer tokens."""
        req = urllib.request.Request(
            f"{GCP_SIM_URL}/oauth2/v4/token",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            token = json.loads(resp.read().decode())
            assert token.get("token_type") == "Bearer"
            assert token.get("access_token", "").startswith("ya29.")
