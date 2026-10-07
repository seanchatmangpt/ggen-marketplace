"""Container-Disk-Bound Receipt (CDBR-v1) Schema & Models."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


def jcs_canonical_bytes(data: dict) -> bytes:
    """RFC 8785 JSON Canonicalization Scheme."""
    return json.dumps(data, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")


@dataclass
class ContainerEnclosure:
    hostname: str
    boot_nonce: str
    cgroup_inode: int
    user_context: Dict[str, Any]  # uid, gid, read_only_rootfs, dropped_caps


@dataclass
class ProcessConformanceMetadata:
    ocel2_sha256: str
    petri_net_spec: str
    token_replay_fitness: float
    events_committed: int
    violations_detected: int = 0


@dataclass
class DiskBinding:
    device_path: str
    file_stat: Dict[str, Any]  # size_bytes, inode, sha256


@dataclass
class Attestation:
    public_key: str
    signature_algorithm: str
    signature: str


@dataclass
class CDBRReceipt:
    receipt_version: str
    receipt_id: str
    timestamp: str
    container_enclosure: ContainerEnclosure
    process_conformance: ProcessConformanceMetadata
    disk_binding: DiskBinding
    attestation: Attestation

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def unsigned_payload_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["attestation"]["signature"] = ""
        return d
