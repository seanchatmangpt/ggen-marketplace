"""Runner-side Retrieval & Verification Client for CDBR-v1."""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any, Dict

from cryptography.hazmat.primitives.asymmetric import ed25519

from ggen_marketplace.cdbr.schema import jcs_canonical_bytes


class CDBRExtractor:
    """Retrieves CDBR-v1 receipts across capability URIs and verifies disk & crypto proofs."""

    @staticmethod
    def extract_and_verify(capability_descriptor: Dict[str, Any], timeout: float = 5.0) -> Dict[str, Any]:
        extraction_uri = capability_descriptor["extraction_uri"]
        expected_sha256 = capability_descriptor["expected_sha256"]
        public_key_hex = capability_descriptor["public_key"]

        # 1. Pull raw receipt bytes across air-gap HTTP boundary
        req = urllib.request.Request(extraction_uri)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Container refused extraction with HTTP status {resp.status}")
            raw_bytes = resp.read()

        # 2. Check transit digest fidelity against container disk commitment
        actual_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        if actual_sha256 != expected_sha256:
            raise ValueError(
                f"Receipt tampered in transit: actual SHA-256 {actual_sha256} != expected {expected_sha256}"
            )

        receipt = json.loads(raw_bytes.decode("utf-8"))

        # 3. Verify Ed25519 signature with container's ephemeral boot key
        sig_hex = receipt["attestation"]["signature"]
        unsigned_receipt = dict(receipt)
        unsigned_receipt["attestation"] = dict(receipt["attestation"])
        unsigned_receipt["attestation"]["signature"] = ""

        canonical_unsigned_bytes = jcs_canonical_bytes(unsigned_receipt)
        pub_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))

        # Verify signature; raises InvalidSignature on error
        pub_key.verify(bytes.fromhex(sig_hex), canonical_unsigned_bytes)

        # 4. Enforce process conformance & sandbox invariants
        conf = receipt["process_conformance"]
        if conf["token_replay_fitness"] < 1.0:
            raise ValueError(f"Process conformance violation: fitness {conf['token_replay_fitness']} < 1.0")

        u_ctx = receipt["container_enclosure"]["user_context"]
        if u_ctx.get("uid") == 0:
            raise PermissionError("Security violation: container execution ran as root (UID 0)")

        return receipt
