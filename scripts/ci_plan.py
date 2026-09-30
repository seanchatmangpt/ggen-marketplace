#!/usr/bin/env python3
"""CI planner and court runner (stdlib only).

``ci/courts.json`` is the declarative index of per-pack verification courts;
each court's body is ``ci/courts/<name>.sh``. A court runs when a changed path
matches one of its globs (GitHub ``paths:`` semantics), when CI infrastructure
itself changed, or when a full run is requested (nightly / dispatch / new
branch). Nothing here mutates the subject; a dirty tree after the run is a
refusal.

  ci_plan.py plan --base SHA [--head SHA] [--all]   JSON plan on stdout
  ci_plan.py run  --base SHA [--head SHA] [--all]   run selected courts in parallel
  ci_plan.py list                                   court names
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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURTS_JSON = ROOT / "ci" / "courts.json"
COURT_DIR = ROOT / "ci" / "courts"

# Changes here can alter what every court means: run them all.
INFRA = ("ci/", ".github/actions/", ".github/workflows/ci.yml", "scripts/ci_plan.py")
# Changes that can alter pack manufacture/qualification; docs-only diffs skip the ggen lane.
QUALIFY_INPUTS = (
    "packs/", "scripts/", "tools/", "ci/", ".github/", "marketplace.toml",
    "rust-toolchain.toml", "ggen.toml", "ggen.lock",
)
ZERO_SHA = "0" * 40


def glob_to_regex(glob: str) -> re.Pattern[str]:
    """GitHub path-filter semantics: ``**`` crosses ``/``; ``*`` and ``?`` do not."""
    out, i = [], 0
    while i < len(glob):
        c = glob[i]
        if glob.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif glob.startswith("**", i):
            out.append(".*")
            i += 2
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile("".join(out) + r"\Z")


def load_courts() -> list[dict]:
    return json.loads(COURTS_JSON.read_text(encoding="utf-8"))


def changed_files(base: str | None, head: str) -> list[str] | None:
    """Changed paths, or None when the change set is unknowable (=> full run)."""
    if not base or base == ZERO_SHA:
        return None
    # Prefer the merge base (what the PR changed); a shallow clone may not reach
    # it, in which case the two-dot diff only over-selects, never under-selects.
    mb = subprocess.run(["git", "merge-base", base, head], cwd=ROOT, capture_output=True, text=True)
    anchor = mb.stdout.strip() if mb.returncode == 0 and mb.stdout.strip() else base
    proc = subprocess.run(
        ["git", "diff", "--name-only", "--no-renames", anchor, head],
        cwd=ROOT, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    return [line for line in proc.stdout.splitlines() if line]


def plan(files: list[str] | None, courts: list[dict], everything: bool = False) -> dict:
    full = everything or files is None or any(f.startswith(INFRA) for f in files)
    selected = []
    for court in courts:
        if full:
            selected.append(court["name"])
            continue
        regexes = [glob_to_regex(p) for p in court["paths"]]
        if any(r.match(f) for f in files for r in regexes):
            selected.append(court["name"])
    qualify = full or any(f.startswith(QUALIFY_INPUTS) for f in files or [])
    return {
        "full": full,
        "changed_files": None if files is None else len(files),
        "courts": selected,
        "qualify": qualify,
    }


def _run_court(court: dict, tmp_root: Path) -> dict:
    name = court["name"]
    scratch = tmp_root / name
    scratch.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, RUNNER_TEMP=str(scratch), TMPDIR=str(scratch), PYTHONDONTWRITEBYTECODE="1")
    started = time.monotonic()
    try:
        proc = subprocess.run(
            ["bash", str(COURT_DIR / f"{name}.sh")], cwd=ROOT, env=env,
            capture_output=True, text=True, timeout=court["timeout_minutes"] * 60,
        )
        rc, out = proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired as exc:
        rc = 124
        out = f"REFUSED:COURT_TIMEOUT:{name}:{court['timeout_minutes']}m\n{exc.stdout or ''}"
    return {"name": name, "rc": rc, "seconds": round(time.monotonic() - started, 2), "log": out}


def _porcelain() -> str:
    return subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                          cwd=ROOT, capture_output=True, text=True).stdout


def run(names: list[str], jobs: int, receipt: Path | None) -> int:
    by_name = {c["name"]: c for c in load_courts()}
    missing = [n for n in names if n not in by_name]
    if missing:
        print(f"REFUSED:UNKNOWN_COURT:{missing}", file=sys.stderr)
        return 2
    results: list[dict] = []
    before = _porcelain()
    wall = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="courts-") as tmp, ThreadPoolExecutor(max_workers=jobs) as pool:
        for res in pool.map(lambda n: _run_court(by_name[n], Path(tmp)), names):
            results.append(res)
            tag = "ok" if res["rc"] == 0 else f"FAIL rc={res['rc']}"
            print(f"::group::court {res['name']} [{tag}] {res['seconds']}s")
            print(res["log"].rstrip())
            print("::endgroup::")
            if res["rc"] != 0:
                print(f"::error title=COURT_FAILED::{res['name']} rc={res['rc']}")
    dirty = "\n".join(sorted(set(_porcelain().splitlines()) - set(before.splitlines())))
    failed = [r["name"] for r in results if r["rc"] != 0]
    wall_s = round(time.monotonic() - wall, 2)
    summary = {
        "courts": len(results), "failed": failed, "wall_seconds": wall_s,
        "sum_court_seconds": round(sum(r["seconds"] for r in results), 2),
        "slowest": sorted(({"name": r["name"], "seconds": r["seconds"]} for r in results),
                          key=lambda r: -r["seconds"])[:5],
        "mutated_subject": bool(dirty),
    }
    if receipt:
        receipt.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as fh:
            fh.write(f"### Courts\n{len(results)} run, {len(failed)} failed, wall {wall_s}s "
                     f"(sum {summary['sum_court_seconds']}s)\n\n")
            for s in summary["slowest"]:
                fh.write(f"- `{s['name']}` {s['seconds']}s\n")
    print(json.dumps(summary))
    if dirty:
        print(f"::error title=REFUSED:COURT_MUTATED_SUBJECT::{dirty}")
        return 2
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["plan", "run", "list"])
    ap.add_argument("--base")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--all", action="store_true", help="select every court")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--receipt", type=Path)
    args = ap.parse_args(argv)
    courts = load_courts()
    if args.cmd == "list":
        print("\n".join(c["name"] for c in courts))
        return 0
    p = plan(changed_files(args.base, args.head), courts, args.all)
    if args.cmd == "plan":
        print(json.dumps(p))
        return 0
    print(f"plan: full={p['full']} changed={p['changed_files']} courts={len(p['courts'])}/{len(courts)}")
    return run(p["courts"], args.jobs, args.receipt) if p["courts"] else 0


if __name__ == "__main__":
    sys.exit(main())
