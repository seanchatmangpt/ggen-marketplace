#!/usr/bin/env python3
"""Fail-closed materializer for public semantic sources.

Only entries explicitly marked mode=vendor and carrying a retrieval_url are copied.
Public accessibility alone never grants redistribution standing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import time
import urllib.request

try:
    import tomllib
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Python 3.11+ required (tomllib)") from exc


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="sources.lock.toml")
    ap.add_argument("--dest", default="vendor")
    ap.add_argument("--timeout", type=int, default=30)
    args = ap.parse_args()

    manifest_path = pathlib.Path(args.manifest)
    doc = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    dest = pathlib.Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    receipt = {
        "manifest": str(manifest_path),
        "started_unix": int(time.time()),
        "sources": [],
        "standing": "ALIVE",
    }

    for source in doc.get("source", []):
        sid = source["id"]
        mode = source.get("mode", "reference")
        item = {
            "id": sid,
            "mode": mode,
            "canonical": source.get("canonical"),
            "license": source.get("license"),
            "standing": "UNSUPPORTED",
        }

        if mode != "vendor":
            item["reason"] = "source is registered for reference/projection, not vendoring"
            receipt["sources"].append(item)
            continue

        url = source.get("retrieval_url")
        if not url:
            item["standing"] = "REFUSED"
            item["reason"] = "vendor entry has no exact retrieval_url"
            receipt["standing"] = "PARTIAL_ALIVE"
            receipt["sources"].append(item)
            continue

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "ggen-marketplace-public-semantics/1",
                "Accept": source.get("format", "text/turtle") + ", application/rdf+xml;q=0.8, application/ld+json;q=0.7, */*;q=0.1",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=args.timeout) as response:
                body = response.read()
                final_url = response.geturl()
                content_type = response.headers.get("Content-Type", "")
        except Exception as exc:  # deliberate fail-closed boundary
            item["standing"] = "BLOCKED"
            item["reason"] = f"retrieval failed: {exc.__class__.__name__}: {exc}"
            receipt["standing"] = "PARTIAL_ALIVE"
            receipt["sources"].append(item)
            continue

        digest = sha256(body)
        expected = source.get("sha256")
        if expected and digest != expected:
            item["standing"] = "REFUSED"
            item["reason"] = "sha256 mismatch"
            item["observed_sha256"] = digest
            item["expected_sha256"] = expected
            receipt["standing"] = "PARTIAL_ALIVE"
            receipt["sources"].append(item)
            continue

        suffix = ".ttl"
        ctype = content_type.lower()
        if "rdf+xml" in ctype or url.endswith(".rdf") or url.endswith(".owl"):
            suffix = ".rdf"
        elif "json" in ctype or url.endswith(".json") or url.endswith(".jsonld"):
            suffix = ".json"

        out_dir = dest / sid
        out_dir.mkdir(parents=True, exist_ok=True)
        payload_path = out_dir / ("source" + suffix)
        payload_path.write_bytes(body)
        meta = {
            "id": sid,
            "canonical": source.get("canonical"),
            "retrieval_url": url,
            "resolved_url": final_url,
            "kind": source.get("kind"),
            "steward": source.get("steward"),
            "version": source.get("version"),
            "license": source.get("license"),
            "content_type": content_type,
            "bytes": len(body),
            "sha256": digest,
            "retrieved_unix": int(time.time()),
            "standing": "ALIVE" if expected else "PARTIAL_ALIVE",
            "digest_pin": "verified" if expected else "observed-not-yet-admitted",
        }
        (out_dir / "receipt.json").write_text(
            json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        item.update(meta)
        receipt["sources"].append(item)
        if not expected:
            receipt["standing"] = "PARTIAL_ALIVE"

    receipt["finished_unix"] = int(time.time())
    (dest / "materialization-receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["standing"] == "ALIVE" else 2


if __name__ == "__main__":
    sys.exit(main())
