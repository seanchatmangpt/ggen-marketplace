#!/usr/bin/env python3
"""Append-only paid-delivery receipt chain (ggen-receipt/v2 field triplet).

Layout under <receipts_dir>:
  receipts/paid-delivery/<slug>.json   one envelope per paid delivery
  receipts/paid-delivery/chain.jsonl   one compact JSON envelope per line, append-only

Chain rule ("paid-delivery-chain/v1"): plain fold
  chain_hash_hex = sha256((prev_chain_hash_hex + payload_hash_hex).encode())
with genesis prev_chain_hash_hex = 64 x "0". payload_hash_hex is sha256 over the
canonical JSON (sorted keys, compact separators) of the embedded payload.

No wall clock: ts_ns is always 0 (receipts are replayable, not timestamped).

Exit codes: 0 = ok, 2 = REFUSED / verification failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCHEMA = "ggen-receipt/v2"
CHAIN_RULE = "paid-delivery-chain/v1"
GENESIS = "0" * 64
ACTIVITY = "aaif.paid-delivery"
SUBDIR = Path("receipts") / "paid-delivery"


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha256_hex(text: str | bytes) -> str:
    data = text.encode("utf-8") if isinstance(text, str) else text
    return hashlib.sha256(data).hexdigest()


def _chain_path(receipts_dir: Path) -> Path:
    return receipts_dir / SUBDIR / "chain.jsonl"


def _read_chain(receipts_dir: Path) -> list[dict]:
    p = _chain_path(receipts_dir)
    if not p.is_file():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def append(receipts_dir: Path, slug: str, payload: dict) -> dict:
    """Append a paid-delivery receipt for `slug`. Returns the written envelope."""
    receipts_dir = Path(receipts_dir)
    receipts_dir.mkdir(parents=True, exist_ok=True)
    chain = _read_chain(receipts_dir)
    prev = chain[-1]["chain_hash_hex"] if chain else GENESIS
    payload_hash = sha256_hex(canonical_json(payload))
    envelope = {
        "schema": SCHEMA,
        "activity": ACTIVITY,
        "slug": slug,
        "ts_ns": 0,
        "payload": payload,
        "payload_hash_hex": payload_hash,
        "prev_chain_hash_hex": prev,
        "chain_hash_hex": sha256_hex((prev + payload_hash).encode("utf-8")),
        "chain_rule": CHAIN_RULE,
    }
    dest = receipts_dir / SUBDIR / f"{slug}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with _chain_path(receipts_dir).open("a", encoding="utf-8") as f:
        f.write(canonical_json(envelope) + "\n")
    return envelope


def verify(receipts_dir: Path) -> tuple[bool, list[str]]:
    """Re-walk the chain. Returns (ok, problems); problems are typed strings."""
    receipts_dir = Path(receipts_dir)
    problems: list[str] = []
    chain = _read_chain(receipts_dir)
    if not chain:
        return True, []
    prev = GENESIS
    for i, env in enumerate(chain):
        where = f"chain[{i}]"
        slug = env.get("slug", "<missing>")
        for field in ("schema", "payload_hash_hex", "prev_chain_hash_hex", "chain_hash_hex", "chain_rule", "payload"):
            if field not in env:
                problems.append(f"{where}:{slug}:REFUSED_MISSING_FIELD:{field}")
        if env.get("schema") != SCHEMA:
            problems.append(f"{where}:{slug}:REFUSED_BAD_SCHEMA:{env.get('schema')}")
        if env.get("chain_rule") != CHAIN_RULE:
            problems.append(f"{where}:{slug}:REFUSED_BAD_CHAIN_RULE:{env.get('chain_rule')}")
        if env.get("ts_ns") != 0:
            problems.append(f"{where}:{slug}:REFUSED_NONZERO_TS_NS")
        recomputed = sha256_hex(canonical_json(env["payload"])) if "payload" in env else None
        if recomputed is not None and env.get("payload_hash_hex") != recomputed:
            problems.append(f"{where}:{slug}:REFUSED_PAYLOAD_HASH_MISMATCH")
        if env.get("prev_chain_hash_hex") != prev:
            problems.append(f"{where}:{slug}:REFUSED_PREV_CHAIN_MISMATCH")
        if recomputed is not None and env.get("prev_chain_hash_hex") == prev:
            expect = sha256_hex((prev + recomputed).encode("utf-8"))
            if env.get("chain_hash_hex") != expect:
                problems.append(f"{where}:{slug}:REFUSED_CHAIN_FOLD_MISMATCH")
        if env.get("chain_hash_hex"):
            prev = env["chain_hash_hex"]
    # per-slug files must match their chain lines exactly
    for i, env in enumerate(chain):
        slug = env.get("slug")
        f = receipts_dir / SUBDIR / f"{slug}.json"
        if not f.is_file():
            problems.append(f"chain[{i}]:{slug}:REFUSED_MISSING_SLUG_FILE")
            continue
        on_disk = json.loads(f.read_text(encoding="utf-8"))
        if on_disk != env:
            problems.append(f"chain[{i}]:{slug}:REFUSED_SLUG_FILE_DRIFT")
    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Paid-delivery receipt chain (append/verify).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a_append = sub.add_parser("append", help="append a receipt from a JSON payload file")
    a_append.add_argument("receipts_dir")
    a_append.add_argument("slug")
    a_append.add_argument("--payload", required=True, help="path to payload JSON file")

    a_verify = sub.add_parser("verify", help="verify the whole chain")
    a_verify.add_argument("receipts_dir")

    args = ap.parse_args(argv)
    if args.cmd == "append":
        payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
        env = append(Path(args.receipts_dir), args.slug, payload)
        print(canonical_json({"chain_hash_hex": env["chain_hash_hex"], "slug": env["slug"]}))
        return 0
    ok, problems = verify(Path(args.receipts_dir))
    if ok:
        print("ALIVE: paid-delivery chain verified")
        return 0
    for p in problems:
        print(p, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
