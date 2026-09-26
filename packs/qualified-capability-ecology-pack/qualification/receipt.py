#!/usr/bin/env python3
"""Manufacture a canonical exact-subject provenance receipt for this pack."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SHA40 = re.compile(r"^[0-9a-f]{40}$")
INCLUDED = (
    "pack.toml",
    "ontology.ttl",
    "shapes.ttl",
    "gates",
    "queries",
    "templates",
    "qualification/fixtures",
    "qualification/verify.py",
)

def digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()

def source_manifest() -> list[dict[str, object]]:
    paths: list[Path] = []
    for rel in INCLUDED:
        p = ROOT / rel
        if p.is_dir():
            paths.extend(x for x in p.rglob("*") if x.is_file())
        elif p.is_file():
            paths.append(p)
    out = []
    for p in sorted(set(paths), key=lambda x: x.relative_to(ROOT).as_posix()):
        data = p.read_bytes()
        out.append({
            "path": p.relative_to(ROOT).as_posix(),
            "bytes": len(data),
            "digest": digest_bytes(data),
            "ownership": "handwritten",
        })
    return out

def manufacture(repository: str, commit: str) -> dict[str, object]:
    if not SHA40.fullmatch(commit):
        raise ValueError("REFUSED:MUTABLE_OR_INVALID_GIT_SUBJECT")
    files = source_manifest()
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema": "ggen.qualified-capability-pack-receipt/1",
        "subject": {"repository": repository, "commit": commit},
        "authority": "none",
        "files": files,
        "source_digest": digest_bytes(canonical),
        "generated_outputs": [
            {
                "path": "runtime_manifest.json",
                "generator": "templates/runtime_manifest.json.tmpl",
                "authority": "none",
            }
        ],
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        receipt = manufacture(args.repository, args.commit)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    payload = json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
