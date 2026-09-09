#!/usr/bin/env python3
"""Bind a generated GGEN Ecosystem OCEL artifact to its generated Project2 request.

HANDWRITTEN_IRREDUCIBLE_REASON: the digest is a function of the exact post-render OCEL bytes.
It cannot truthfully exist as an RDF input fact before GGEN renders those bytes. This adapter
only computes the SHA-256 binding and replaces the pack-owned sentinel in the generated
Project2 request. It never constructs or mutates OCEL and performs no process analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SENTINEL = "__GGEN_OCEL_SHA256__"
DIGEST_PREFIX = "sha256:"


def digest_bytes(payload: bytes) -> str:
    return f"{DIGEST_PREFIX}{hashlib.sha256(payload).hexdigest()}"


def replace_sentinel(value: Any, digest: str) -> tuple[Any, int]:
    if isinstance(value, str):
        count = value.count(SENTINEL)
        return value.replace(SENTINEL, digest), count
    if isinstance(value, list):
        output = []
        total = 0
        for item in value:
            transformed, count = replace_sentinel(item, digest)
            output.append(transformed)
            total += count
        return output, total
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        total = 0
        for key, item in value.items():
            transformed, count = replace_sentinel(item, digest)
            output[key] = transformed
            total += count
        return output, total
    return value, 0


def finalize(ocel_path: Path, request_path: Path) -> str:
    ocel_bytes = ocel_path.read_bytes()
    before = ocel_bytes
    digest = digest_bytes(ocel_bytes)

    request = json.loads(request_path.read_text(encoding="utf-8"))
    metadata = request.get("payload", {}).get("record", {}).get("metadata", {})
    if metadata.get("ocel_digest") != SENTINEL:
        raise ValueError("REFUSED[OCEL_DIGEST_SENTINEL_MISSING_OR_PREBOUND]")

    finalized, replacements = replace_sentinel(request, digest)
    if replacements < 2:
        raise ValueError("REFUSED[OCEL_DIGEST_BINDING_INCOMPLETE]")
    if SENTINEL in json.dumps(finalized, sort_keys=True):
        raise ValueError("REFUSED[OCEL_DIGEST_SENTINEL_REMAINS]")

    final_metadata = finalized["payload"]["record"]["metadata"]
    if final_metadata.get("process_analysis_owner") != "wasm4pm":
        raise ValueError("REFUSED[PROCESS_ANALYSIS_OWNER_DRIFT]")
    if final_metadata.get("ggen_first") is not True:
        raise ValueError("REFUSED[GGEN_FIRST_DRIFT]")
    if final_metadata.get("manufacturing_ladder") != "U->G->O->Q->M":
        raise ValueError("REFUSED[MANUFACTURING_LADDER_DRIFT]")

    request_path.write_text(
        json.dumps(finalized, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if ocel_path.read_bytes() != before:
        raise RuntimeError("REFUSED[OCEL_ARTIFACT_MUTATED]")
    return digest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ocel", type=Path)
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    print(finalize(args.ocel, args.request))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
