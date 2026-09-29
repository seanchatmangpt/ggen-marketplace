#!/usr/bin/env python3
"""Consume-side pack integrity: lock, verify, fetch.

  fetch_pack.py lock <catalog.json> <pack>... [--out packs.lock.json]
  fetch_pack.py verify <archive.tar.gz> <name> [--lock FILE | --catalog FILE]
  fetch_pack.py fetch <name> --catalog <file-or-url> [--lock FILE] [--out DIR]

Exit 0 on success; exit 2 with a REFUSED:<CODE> line on stderr on refusal.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import tarfile
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pack_lock import LockError, build_lock, lock_entry, read_lock, write_lock  # noqa: E402


def load_url_or_file(ref: str) -> bytes:
    try:
        if "://" in ref:
            with urllib.request.urlopen(ref, timeout=60) as resp:  # noqa: S310
                return resp.read()
        return Path(ref).read_bytes()
    except (OSError, ValueError) as exc:
        raise LockError(f"REFUSED:FETCH_FAILED {ref}: {exc}") from exc


def load_catalog(ref: str) -> dict[str, Any]:
    try:
        return json.loads(load_url_or_file(ref))
    except ValueError as exc:
        raise LockError(f"REFUSED:CATALOG_UNREADABLE {ref}: {exc}") from exc


def catalog_record(catalog: dict[str, Any], name: str) -> dict[str, Any]:
    for rec in catalog.get("packs", []):
        if rec.get("name") == name:
            return rec
    raise LockError(f"REFUSED:PACK_NOT_IN_CATALOG {name}")


def check_digest(data: bytes, expected: str, name: str) -> None:
    actual = f"sha256:{hashlib.sha256(data).hexdigest()}"
    if actual != expected:
        raise LockError(f"REFUSED:DIGEST_MISMATCH {name} expected={expected} actual={actual}")


def safe_extract(data: bytes, name: str, out: Path) -> list[str]:
    """Extract only regular files/dirs under <name>/; refuse anything else before writing."""
    try:
        tar = tarfile.open(fileobj=io.BytesIO(data), mode="r:gz")
    except (tarfile.TarError, OSError, EOFError) as exc:
        raise LockError(f"REFUSED:ARCHIVE_UNREADABLE {name}: {exc}") from exc
    with tar:
        members = tar.getmembers()
        for m in members:
            p = PurePosixPath(m.name)
            if p.is_absolute() or m.name.startswith(("/", "\\")) or ".." in p.parts:
                raise LockError(f"REFUSED:UNSAFE_PATH {m.name}")
            if m.issym() or m.islnk():
                raise LockError(f"REFUSED:LINK_MEMBER {m.name}")
            if not (m.isreg() or m.isdir()):
                raise LockError(f"REFUSED:SPECIAL_MEMBER {m.name}")
            if not p.parts or p.parts[0] != name:
                raise LockError(f"REFUSED:OUTSIDE_PACK_ROOT {m.name}")
        out.mkdir(parents=True, exist_ok=True)
        root = out.resolve()
        written = []
        for m in members:
            dest = (out / m.name).resolve()
            if root != dest and root not in dest.parents:
                raise LockError(f"REFUSED:UNSAFE_PATH {m.name}")
            if m.isdir():
                dest.mkdir(parents=True, exist_ok=True)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            src = tar.extractfile(m)
            assert src is not None
            dest.write_bytes(src.read())
            written.append(m.name)
    return written


def expected_digest(name: str, lock: str | None, catalog: str | None) -> str:
    if lock:
        return lock_entry(read_lock(Path(lock)), name)["digest"]
    if catalog:
        return catalog_record(load_catalog(catalog), name)["digest"]
    raise LockError("REFUSED:NO_DIGEST_SOURCE pass --lock or --catalog")


def cmd_lock(args: argparse.Namespace) -> int:
    lock = build_lock(load_catalog(args.catalog), args.packs)
    write_lock(Path(args.out), lock)
    print(f"locked {len(lock['packs'])} pack(s) -> {args.out}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    data = Path(args.archive).read_bytes()
    expected = expected_digest(args.name, args.lock, args.catalog)
    check_digest(data, expected, args.name)
    print(f"verified {args.name} {expected}")
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    rec = catalog_record(load_catalog(args.catalog), args.name)
    expected = rec["digest"]
    if args.lock:
        pinned = lock_entry(read_lock(Path(args.lock)), args.name)["digest"]
        if pinned != expected:
            raise LockError(f"REFUSED:LOCK_CATALOG_DRIFT {args.name} lock={pinned} catalog={expected}")
    data = load_url_or_file(rec["download_url"])
    check_digest(data, expected, args.name)
    written = safe_extract(data, args.name, Path(args.out))
    print(f"fetched {args.name} {rec.get('version')} files={len(written)} -> {args.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("lock")
    p.add_argument("catalog")
    p.add_argument("packs", nargs="+")
    p.add_argument("--out", default="packs.lock.json")
    p.set_defaults(fn=cmd_lock)
    p = sub.add_parser("verify")
    p.add_argument("archive")
    p.add_argument("name")
    p.add_argument("--lock")
    p.add_argument("--catalog")
    p.set_defaults(fn=cmd_verify)
    p = sub.add_parser("fetch")
    p.add_argument("name")
    p.add_argument("--catalog", required=True)
    p.add_argument("--lock")
    p.add_argument("--out", default="packs")
    p.set_defaults(fn=cmd_fetch)
    args = parser.parse_args(argv)
    try:
        return args.fn(args)
    except LockError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
