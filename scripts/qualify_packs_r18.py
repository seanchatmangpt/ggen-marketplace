#!/usr/bin/env python3
"""R18 bounded qualification runner with explicit marketplace scope."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import qualify_packs as q
from marketplace import require_admitted
from marketplace_scope import select_packs

MAX_TIMEOUT_SECONDS = 30.0
MAX_WORKERS = 16


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ggen", default=os.environ.get("GGEN_BIN") or shutil.which("ggen"))
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--shard-index", type=int, default=None)
    parser.add_argument("--shard-count", type=int, default=None)
    parser.add_argument("--scope", choices=("active", "all"), default="active")
    args = parser.parse_args()

    if (args.shard_index is None) != (args.shard_count is None):
        print("REFUSED:GGEN_PACK_SHARD_ARGS", file=sys.stderr); return 2
    if not args.ggen:
        print("REFUSED:GGEN_BINARY_REQUIRED", file=sys.stderr); return 2
    if args.timeout_seconds <= 0 or args.timeout_seconds > MAX_TIMEOUT_SECONDS:
        print("REFUSED:GGEN_PACK_TIMEOUT_BOUND:must_be_gt_0_and_lte_30", file=sys.stderr); return 2
    if args.workers <= 0 or args.workers > MAX_WORKERS:
        print("REFUSED:GGEN_PACK_WORKER_BOUND:must_be_1_to_16", file=sys.stderr); return 2

    version = subprocess.run([args.ggen, "--version"], check=False, capture_output=True, text=True, timeout=5)
    if version.returncode != 0:
        print(f"REFUSED:GGEN_VERSION_FAILED:exit={version.returncode}", file=sys.stderr); return 2

    try:
        packs = select_packs(require_admitted(), args.scope)
    except ValueError as error:
        print(str(error), file=sys.stderr); return 2
    if args.shard_index is not None:
        try:
            packs = q.shard(packs, args.shard_index, args.shard_count)
        except q.QualificationContractError as error:
            print(f"REFUSED:GGEN_PACK_SHARD_INVALID:{error}", file=sys.stderr); return 2

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        records = list(executor.map(lambda pack: q.qualify_pack(pack, args.ggen, args.timeout_seconds), packs))
    records.sort(key=lambda item: item["name"])
    failures = [record for record in records if record["status"] == "REFUSED"]
    skipped = [record for record in records if record["status"] == "SKIPPED"]
    warned = [record for record in records if record["status"] == "WARN"]
    payload = {
        "ggen": (version.stdout or version.stderr).strip(),
        "pack_count": len(records),
        "packs": records,
        "schema": "https://ggen.dev/marketplace/qualification/v1",
        "scope": args.scope,
        "shard_count": args.shard_count,
        "shard_index": args.shard_index,
        "timeout_seconds": args.timeout_seconds,
        "qualification_runner": "r18-headroom",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if skipped:
        for record in skipped:
            print(f"{record['code']}:{record['name']}", file=sys.stderr)
    if warned:
        for record in warned:
            print(f"{record['code']}:{record['name']} (non-blocking, CARGO_BUILD_CHECK_BLOCKING=False)", file=sys.stderr)
    if failures:
        for record in failures:
            print(f"{record['code']}:{record['name']}:{record['detail']}", file=sys.stderr)
        print(f"REFUSED:GGEN_PACK_QUALIFICATION_FAILED:failed={len(failures)} total={len(records)} scope={args.scope}", file=sys.stderr)
        return 2
    print(f"qualified packs={len(records)} scope={args.scope} timeout_seconds={args.timeout_seconds:g} runner=r18-headroom")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
