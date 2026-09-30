#!/usr/bin/env python3
"""Run the declarative pack courts in ci/courts.toml that a change touches.

Replaces ~90 single-purpose `<family>-<round>-*.yml` workflows (each paid for a
runner, a checkout and a setup-python) with one table and one job.

  python3 scripts/ci_courts.py --base <sha>   # courts whose paths intersect `git diff base...HEAD`
  python3 scripts/ci_courts.py --all          # every court (push to main, manual runs)
  python3 scripts/ci_courts.py --list         # print selection, run nothing
  python3 scripts/ci_courts.py --check        # table is well formed (stdlib only)

Courts may set `advisory = true` (reported, non-gating), `main_only = true` (skipped on PR
diffs) and `ggen = true` (runner provides $GGEN_BIN).
A change to ci/courts.toml, ci/requirements-courts.txt or this script selects
every court. Courts run in parallel; each gets its own TMPDIR.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "ci" / "courts.toml"
INFRA = ("ci/courts.toml", "ci/requirements-courts.txt", "scripts/ci_courts.py")


def load() -> list[dict]:
    courts = tomllib.loads(TABLE.read_text(encoding="utf-8")).get("court", [])
    seen: set[str] = set()
    for court in courts:
        cid = court.get("id")
        if not cid or cid in seen:
            raise SystemExit(f"REFUSED:COURT_ID_MISSING_OR_DUPLICATE:{cid}")
        seen.add(cid)
        if not court.get("paths") or not court.get("run", "").strip():
            raise SystemExit(f"REFUSED:COURT_INCOMPLETE:{cid}")
    return courts


def glob_re(pattern: str) -> re.Pattern[str]:
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out + r"\Z")


def changed_files(base: str) -> list[str]:
    diff = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    return [line for line in diff.stdout.splitlines() if line]


def select(courts: list[dict], files: list[str] | None) -> list[dict]:
    """None means "every court" (push to main / manual); `main_only` courts skip PR diffs."""
    if files is None:
        return courts
    pool = courts if any(f in INFRA for f in files) else [
        c for c in courts if any(glob_re(p).match(f) for p in c["paths"] for f in files)
    ]
    return [c for c in pool if not c.get("main_only")]


def provide_ggen(env: dict[str, str]) -> None:
    """Admit marketplace.toml and install the pinned ggen once, for courts that declare `ggen = true`."""
    if env.get("GGEN_BIN"):  # the setup-marketplace action already installed (and cached) it
        return
    admitted = Path(env.get("RUNNER_TEMP") or tempfile.gettempdir()) / "courts-admitted-config.json"
    subprocess.run(["bash", "scripts/admit-config.sh", "marketplace.toml", str(admitted)],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    installed = subprocess.run(["bash", "scripts/install-ggen.sh", str(admitted)],
                               cwd=ROOT, check=True, capture_output=True, text=True)
    env["GGEN_BIN"] = installed.stdout.strip().splitlines()[-1]


def run_court(court: dict, base_env: dict[str, str]) -> dict:
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix=f"court-{court['id']}-") as tmp:
        env = {**base_env, "TMPDIR": tmp, "RUNNER_TEMP": tmp, "PYTHONDONTWRITEBYTECODE": "1"}
        proc = subprocess.run(
            ["bash", "-euo", "pipefail", "-c", court["run"]],
            cwd=ROOT, env=env, capture_output=True, text=True,
        )
    return {
        "id": court["id"], "ok": proc.returncode == 0, "advisory": bool(court.get("advisory")), "seconds": round(time.monotonic() - start, 1),
        "output": proc.stdout + proc.stderr,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument("--base", help="diff base commit; select courts touched since it")
    scope.add_argument("--all", action="store_true", help="run every court")
    ap.add_argument("--list", action="store_true", help="list selected courts and exit")
    ap.add_argument("--check", action="store_true", help="validate the table and exit")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--report", help="write a JSON report here")
    args = ap.parse_args(argv)

    courts = load()
    if args.check:
        print(f"ci_courts: {len(courts)} courts well formed")
        return 0
    if not args.base and not args.all:
        ap.error("one of --base, --all, --check is required")

    chosen = select(courts, None if args.all else changed_files(args.base))
    print(f"ci_courts: {len(chosen)}/{len(courts)} courts selected")
    if args.list:
        print("\n".join(c["id"] for c in chosen))
        return 0

    env = dict(os.environ)
    if any(c.get("ggen") for c in chosen):
        provide_ggen(env)
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        results = list(pool.map(lambda c: run_court(c, env), chosen))
    for r in results:
        verdict = "PASS" if r["ok"] else "ADVISORY-FAIL" if r["advisory"] else "FAIL"
        print(f"::group::{verdict} {r['id']} ({r['seconds']}s)")
        print(r["output"].rstrip())
        print("::endgroup::")
    failed = [r["id"] for r in results if not r["ok"] and not r["advisory"]]
    for r in results:
        if not r["ok"] and r["advisory"]:
            print(f"::warning title=ADVISORY_COURT_RED::{r['id']}")
    if args.report:
        Path(args.report).write_text(json.dumps(
            [{k: r[k] for k in ("id", "ok", "advisory", "seconds")} for r in results], indent=1) + "\n")
    if failed:
        for cid in failed:
            print(f"::error title=COURT_FAILED::{cid}")
        return 1
    print(f"ci_courts: all {len(results)} selected courts passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
