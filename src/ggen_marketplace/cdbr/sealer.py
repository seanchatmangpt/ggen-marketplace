"""In-container Sealing & Ephemeral HTTP Exporter for CDBR-v1."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
import uuid

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from ggen_marketplace.cdbr.schema import (
    Attestation,
    CDBRReceipt,
    ContainerEnclosure,
    DiskBinding,
    ProcessConformanceMetadata,
    jcs_canonical_bytes,
)


class EphemeralExtractHandler(BaseHTTPRequestHandler):
    expected_token: str = ""
    receipt_bytes: bytes = b""

    def do_GET(self) -> None:
        if self.path == f"/extract/{self.expected_token}":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(self.receipt_bytes)))
            self.end_headers()
            self.wfile.write(self.receipt_bytes)
            # Signal server shutdown in a separate thread so response finishes cleanly
            threading.Thread(target=self.server.shutdown).start()
        else:
            self.send_response(403)
            self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress noisy HTTP logs in test output
        pass


class CDBRSealer:
    """Mints ephemeral Ed25519 keypair, signs receipt, commits to disk, and serves once."""

    def __init__(self, private_key: Optional[ed25519.Ed25519PrivateKey] = None) -> None:
        self.priv_key = private_key or ed25519.Ed25519PrivateKey.generate()
        self.pub_key = self.priv_key.public_key()
        self.pub_bytes_hex = self.pub_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        ).hex()
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None

    def seal_to_disk(
        self,
        disk_path: Path | str,
        ocel2_sha256: str,
        fitness: float = 1.0,
        events_committed: int = 8,
        petri_net_spec: str = "normative_lifecycle.pnml",
        user_context: Optional[Dict[str, Any]] = None,
    ) -> CDBRReceipt:
        disk_path = Path(disk_path)
        disk_path.parent.mkdir(parents=True, exist_ok=True)

        user_ctx = user_context or {
            "uid": 10001,
            "gid": 10001,
            "read_only_rootfs": True,
            "dropped_caps": ["ALL"],
        }

        # Ephemeral container enclosure metadata
        enclosure = ContainerEnclosure(
            hostname=os.uname().nodename if hasattr(os, "uname") else "container-sandbox",
            boot_nonce=secrets.token_hex(8),
            cgroup_inode=4026532841,
            user_context=user_ctx,
        )

        conformance = ProcessConformanceMetadata(
            ocel2_sha256=ocel2_sha256,
            petri_net_spec=petri_net_spec,
            token_replay_fitness=fitness,
            events_committed=events_committed,
            violations_detected=0,
        )

        receipt_id = f"cdbr-{uuid.uuid4()}"
        ts = datetime.now(timezone.utc).isoformat()

        # Temporary disk binding placeholder
        disk_binding = DiskBinding(
            device_path=str(disk_path),
            file_stat={"size_bytes": 0, "inode": 0, "sha256": ""},
        )

        attestation = Attestation(
            public_key=self.pub_bytes_hex,
            signature_algorithm="Ed25519",
            signature="",
        )

        receipt = CDBRReceipt(
            receipt_version="CDBR-v1",
            receipt_id=receipt_id,
            timestamp=ts,
            container_enclosure=enclosure,
            process_conformance=conformance,
            disk_binding=disk_binding,
            attestation=attestation,
        )

        # 1. Compute unsigned payload bytes for signing
        unsigned_bytes = jcs_canonical_bytes(receipt.unsigned_payload_dict())
        sig_bytes = self.priv_key.sign(unsigned_bytes)
        receipt.attestation.signature = sig_bytes.hex()

        # 2. Commit to disk
        canonical_receipt_bytes = jcs_canonical_bytes(receipt.to_dict())
        disk_path.write_bytes(canonical_receipt_bytes)

        # 3. Update file_stat in memory
        stat = disk_path.stat()
        file_sha256 = hashlib.sha256(canonical_receipt_bytes).hexdigest()
        receipt.disk_binding.file_stat = {
            "size_bytes": stat.st_size,
            "inode": stat.st_ino,
            "sha256": file_sha256,
        }

        return receipt

    def advertise_and_serve_single_use(
        self,
        receipt_path: Path | str,
        port: int = 8099,
        termination_log: Optional[Path | str] = None,
    ) -> Dict[str, Any]:
        receipt_path = Path(receipt_path)
        raw_bytes = receipt_path.read_bytes()
        file_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        access_token = secrets.token_hex(16)

        capability_link = {
            "extraction_uri": f"http://127.0.0.1:{port}/extract/{access_token}",
            "disk_path": str(receipt_path),
            "expected_sha256": file_sha256,
            "public_key": self.pub_bytes_hex,
        }

        if termination_log:
            term_path = Path(termination_log)
            term_path.parent.mkdir(parents=True, exist_ok=True)
            term_path.write_text(json.dumps(capability_link), encoding="utf-8")

        # Configure handler
        EphemeralExtractHandler.expected_token = access_token
        EphemeralExtractHandler.receipt_bytes = raw_bytes

        self.server = HTTPServer(("0.0.0.0", port), EphemeralExtractHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

        return capability_link
