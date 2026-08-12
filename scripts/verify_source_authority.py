#!/usr/bin/env python3
"""Fail-closed source-authority court for the ggen Marketplace.

Pack bytes admitted in this repository are canonical marketplace source.
Historical import repositories and byte mirrors remain provenance only. The
pinned ggen release is a manufacturer/qualifier, not a second pack authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"
CANONICAL_REPOSITORY = "seanchatmangpt/ggen-marketplace"
CANONICAL_BRANCH = "main"
GGEN_REPOSITORY = "seanchatmangpt/ggen"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")


def refuse(code: str, detail: str) -> "NoReturn":  # type: ignore[name-defined]
    raise SystemExit(f"REFUSED:{code}:{detail}")


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        refuse("SOURCE_AUTHORITY_SCHEMA", f"{name}=not-object")
    return value


def _visible_pack_files() -> tuple[Path, ...]:
    if not PACKS.is_dir():
        refuse("PACKS_DIRECTORY_MISSING", "packs")
    symlinks = sorted(
        path.relative_to(ROOT).as_posix()
        for path in PACKS.rglob("*")
        if path.is_symlink()
    )
    if symlinks:
        refuse("PACK_SYMLINK", ",".join(symlinks))
    return tuple(
        sorted(
            (
                path
                for path in PACKS.rglob("*")
                if path.is_file()
                and not any(
                    part.startswith(".")
                    for part in path.relative_to(PACKS).parts
                )
            ),
            key=lambda path: path.relative_to(ROOT).as_posix(),
        )
    )


def corpus_fingerprint() -> tuple[str, int, int]:
    digest = hashlib.sha256()
    files = _visible_pack_files()
    pack_names = sorted(
        path.name
        for path in PACKS.iterdir()
        if path.is_dir() and (path / "pack.toml").is_file()
    )
    for path in files:
        relative = path.relative_to(ROOT).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest(), len(files), len(pack_names)


def observed_head() -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = result.stdout.strip()
    return value if HEX40.fullmatch(value) else None


def verify(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("q_config") != 1 or payload.get("standing") != "ADMITTED":
        refuse("MARKETPLACE_CONFIG_NOT_ADMITTED", "q_config/standing")

    config = _require_mapping(payload.get("config"), "config")
    source = _require_mapping(config.get("source_authority"), "source_authority")
    if source.get("repository") != CANONICAL_REPOSITORY:
        refuse(
            "SOURCE_AUTHORITY_REPOSITORY",
            f"actual={source.get('repository')!r},expected={CANONICAL_REPOSITORY}",
        )
    if source.get("canonical_branch") != CANONICAL_BRANCH:
        refuse(
            "SOURCE_AUTHORITY_BRANCH",
            f"actual={source.get('canonical_branch')!r},expected={CANONICAL_BRANCH}",
        )
    if source.get("mirrors_are_provenance_only") is not True:
        refuse("MIRROR_AUTHORITY_ESCALATION", "mirrors_are_provenance_only!=true")

    ggen = _require_mapping(config.get("ggen"), "ggen")
    if ggen.get("repository") != GGEN_REPOSITORY:
        refuse(
            "GGEN_REPOSITORY_IDENTITY",
            f"actual={ggen.get('repository')!r},expected={GGEN_REPOSITORY}",
        )
    if ggen.get("repository") == source.get("repository"):
        refuse("SOURCE_MANUFACTURER_AUTHORITY_COLLISION", GGEN_REPOSITORY)

    version = ggen.get("version")
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        refuse("GGEN_VERSION_IDENTITY", repr(version))
    release_commit = ggen.get("release_commit")
    if not isinstance(release_commit, str) or not HEX40.fullmatch(release_commit):
        refuse("GGEN_RELEASE_COMMIT_IDENTITY", repr(release_commit))

    assets = _require_mapping(ggen.get("assets"), "ggen.assets")
    required_assets = {
        "linux_x86_64",
        "linux_aarch64",
        "darwin_aarch64",
        "darwin_x86_64",
    }
    if set(assets) != required_assets:
        refuse(
            "GGEN_ASSET_MATRIX",
            f"actual={sorted(assets)},expected={sorted(required_assets)}",
        )
    for name in sorted(required_assets):
        asset = _require_mapping(assets.get(name), f"ggen.assets.{name}")
        archive = asset.get("archive")
        digest = asset.get("sha256")
        if not isinstance(archive, str) or not archive.strip():
            refuse("GGEN_ASSET_ARCHIVE", name)
        if not isinstance(digest, str) or not HEX64.fullmatch(digest):
            refuse("GGEN_ASSET_DIGEST", f"{name}:{digest!r}")

    corpus_sha256, file_count, pack_count = corpus_fingerprint()
    return {
        "schema": "https://ggen.dev/marketplace/source-authority/v1",
        "standing": "ADMITTED",
        "canonical_repository": CANONICAL_REPOSITORY,
        "canonical_branch": CANONICAL_BRANCH,
        "subject_sha": observed_head(),
        "pack_corpus_sha256": corpus_sha256,
        "pack_file_count": file_count,
        "pack_count": pack_count,
        "ggen_repository": GGEN_REPOSITORY,
        "ggen_version": version,
        "ggen_release_commit": release_commit,
        "mirrors_are_provenance_only": True,
        "do_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("admitted_config", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    try:
        payload = json.loads(args.admitted_config.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        refuse("ADMITTED_CONFIG_READ", str(exc))

    receipt = verify(_require_mapping(payload, "admitted-config"))
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(encoded, encoding="utf-8")
    sys.stdout.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
