#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tomllib
from pathlib import Path


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_sha256(root: Path) -> tuple[str, int, int]:
    h = hashlib.sha256()
    files = 0
    total = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        digest = file_sha256(path)
        size = path.stat().st_size
        h.update(rel.encode())
        h.update(b"\0")
        h.update(digest.encode())
        h.update(b"\0")
        h.update(str(size).encode())
        h.update(b"\n")
        files += 1
        total += size
    return h.hexdigest(), files, total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--admitted-config", type=Path, required=True)
    parser.add_argument("--marketplace-sha", required=True)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    admitted = json.loads(args.admitted_config.read_text(encoding="utf-8"))
    if admitted.get("q_config") != 1 or admitted.get("standing") != "ADMITTED":
        raise SystemExit("REFUSED:MARKETPLACE_CONFIG_NOT_ADMITTED")
    if len(args.marketplace_sha) != 40 or any(c not in "0123456789abcdef" for c in args.marketplace_sha):
        raise SystemExit("REFUSED:MARKETPLACE_SHA_INVALID")
    config = admitted["config"]
    packs_root = args.root / "packs"

    packs = []
    for pack_dir in sorted(p for p in packs_root.iterdir() if p.is_dir()):
        manifest = pack_dir / "pack.toml"
        if not manifest.is_file():
            continue
        raw = tomllib.loads(manifest.read_text(encoding="utf-8"))
        pack = raw.get("pack") or {}
        name = pack.get("name")
        version = pack.get("version")
        if not name or name != pack_dir.name:
            raise SystemExit(f"REFUSED:PACK_IDENTITY_DRIFT:{pack_dir.name}:{name}")
        if not version:
            raise SystemExit(f"REFUSED:PACK_VERSION_MISSING:{name}")
        digest, file_count, size_bytes = tree_sha256(pack_dir)
        packs.append({
            "name": name,
            "version": str(version),
            "path": f"packs/{name}",
            "manifest_sha256": file_sha256(manifest),
            "source_tree_sha256": digest,
            "file_count": file_count,
            "size_bytes": size_bytes,
        })

    packs_projection = json.dumps(packs, sort_keys=True, separators=(",", ":")).encode()
    packs_digest = hashlib.sha256(packs_projection).hexdigest()
    marketplace = config["marketplace"]
    ggen = config["ggen"]
    payload = {
        "schema": "ggen.factory/1",
        "marketplace": {
            "repository": config["source_authority"]["repository"],
            "sha": args.marketplace_sha,
            "version": marketplace["version"],
            "packs_digest": packs_digest,
            "pack_count": len(packs),
        },
        "ggen": {
            "repository": ggen["repository"],
            "version": ggen["version"],
            "release_commit": ggen["release_commit"],
            "assets": ggen["assets"],
        },
        "packs": packs,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["factory_id"] = f"sha256:{hashlib.sha256(canonical).hexdigest()}"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
