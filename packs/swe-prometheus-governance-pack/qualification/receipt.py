#!/usr/bin/env python3
"""Emit a content-addressed source receipt for the SPG qualification surface."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = (
    ROOT / "pack.toml",
    ROOT / "ontology.ttl",
    ROOT / "gate-court.toml",
)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    paths = list(INCLUDE)
    paths.extend(sorted((ROOT / "gates").glob("*.rq")))
    paths.extend(sorted((ROOT / "templates").glob("*.tmpl")))
    paths.extend(
        sorted((ROOT / "qualification" / "fixtures").glob("*.ttl"))
    )
    files = {
        str(path.relative_to(ROOT)): sha256(path)
        for path in paths
    }
    payload = {
        "schema": "ggen.swe-prometheus-governance-qualification/1",
        "pack": "swe-prometheus-governance-pack",
        "version": "0.2.0",
        "files": files,
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    payload["receipt_id"] = (
        "sha256:" + hashlib.sha256(canonical).hexdigest()
    )
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
