"""Chicago-Style Integration Test Court for CDBR-v1 (Container-Disk-Bound Receipt).

Verifies:
1. In-container ephemeral Ed25519 key minting and disk-bound receipt sealing.
2. Single-use capability descriptor emission and air-gapped HTTP extraction.
3. Anti-vacuity: Burn-after-reading single-use daemon refuses replay attempts.
4. Anti-vacuity: In-transit payload tampering triggers immediate digest/signature failure.
5. Anti-vacuity: Unauthorized key substitution fails cryptographic verification.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from ggen_marketplace.cdbr import CDBRExtractor, CDBRSealer


class TestCDBRIsolationCourt:
    """Court verifying Proof of Execution Isolation via Container-Disk-Bound Receipts."""

    def test_cdbr_in_container_minting_and_extraction_roundtrip(self, tmp_path: Path) -> None:
        """Prove that a container-minted receipt can be extracted and cryptographically verified."""
        disk_receipt = tmp_path / "sealed-receipts" / "cdbr-test.json"
        term_log = tmp_path / "termination-log"

        sealer = CDBRSealer()
        sealer.seal_to_disk(
            disk_path=disk_receipt,
            ocel2_sha256="8f4a12bc90e87d3a2b1c0d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a",
            fitness=1.0,
            events_committed=8,
            user_context={"uid": 10001, "gid": 10001, "read_only_rootfs": True, "dropped_caps": ["ALL"]},
        )

        # Advertise capability descriptor
        descriptor = sealer.advertise_and_serve_single_use(
            receipt_path=disk_receipt,
            port=8101,
            termination_log=term_log,
        )

        assert descriptor["expected_sha256"] != ""
        assert descriptor["public_key"] == sealer.pub_bytes_hex

        # Extract across boundary
        verified_receipt = CDBRExtractor.extract_and_verify(descriptor)

        assert verified_receipt["receipt_version"] == "CDBR-v1"
        assert verified_receipt["process_conformance"]["token_replay_fitness"] == 1.0
        assert verified_receipt["container_enclosure"]["user_context"]["uid"] == 10001

    def test_cdbr_burn_after_reading_tripwire(self, tmp_path: Path) -> None:
        """Anti-vacuity witness: Single-use extraction daemon immediately terminates after first pull."""
        disk_receipt = tmp_path / "burn-receipt.json"
        sealer = CDBRSealer()
        sealer.seal_to_disk(disk_path=disk_receipt, ocel2_sha256="deadbeef" * 8, fitness=1.0)
        descriptor = sealer.advertise_and_serve_single_use(receipt_path=disk_receipt, port=8102)

        # First request succeeds
        verified = CDBRExtractor.extract_and_verify(descriptor)
        assert verified["receipt_version"] == "CDBR-v1"

        # Anti-vacuity witness: Second request MUST be refused (connection refused or closed)
        with pytest.raises(Exception):
            CDBRExtractor.extract_and_verify(descriptor, timeout=1.0)

    def test_cdbr_tampered_payload_in_transit_fails_verification(self, tmp_path: Path) -> None:
        """Anti-vacuity witness: Modifying the expected digest or payload triggers immediate refusal."""
        disk_receipt = tmp_path / "tamper-receipt.json"
        sealer = CDBRSealer()
        sealer.seal_to_disk(disk_path=disk_receipt, ocel2_sha256="1234abcd" * 8, fitness=1.0)
        descriptor = sealer.advertise_and_serve_single_use(receipt_path=disk_receipt, port=8103)

        # In-transit tamper: Alter expected SHA256 in descriptor
        tampered_descriptor = dict(descriptor)
        tampered_descriptor["expected_sha256"] = "0000000000000000000000000000000000000000000000000000000000000000"

        with pytest.raises(ValueError, match="Receipt tampered in transit"):
            CDBRExtractor.extract_and_verify(tampered_descriptor)

    def test_cdbr_unauthorized_key_substitution_fails(self, tmp_path: Path) -> None:
        """Anti-vacuity witness: Substituting an external public key causes signature verification to fail."""
        disk_receipt = tmp_path / "keyswap-receipt.json"
        sealer = CDBRSealer()
        sealer.seal_to_disk(disk_path=disk_receipt, ocel2_sha256="beefcafe" * 8, fitness=1.0)
        descriptor = sealer.advertise_and_serve_single_use(receipt_path=disk_receipt, port=8104)

        # Generate a rogue external key
        rogue_key = ed25519.Ed25519PrivateKey.generate().public_key()
        from cryptography.hazmat.primitives import serialization
        rogue_pub_hex = rogue_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        ).hex()

        tampered_descriptor = dict(descriptor)
        tampered_descriptor["public_key"] = rogue_pub_hex

        with pytest.raises(InvalidSignature):
            CDBRExtractor.extract_and_verify(tampered_descriptor)
