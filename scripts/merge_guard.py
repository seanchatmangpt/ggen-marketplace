#!/usr/bin/env python3
"""Detect hunks silently dropped by a merge commit (e.g. resolved with -X ours).

For a merge commit M with parents P1..Pn: for each ordered parent pair (Pi, Pj),
base = merge-base(Pi, Pj). Every added hunk in `git diff base Pi` is a change Pi
contributed. It is DROPPED when its lines do not appear contiguously in the
merge result's version of the file AND do not appear in Pj's version of the file
(if Pj also carries it, it was not lost to one side only). Read-only git.

Exit 1 if drops are found, unless every dropped file is listed in --allow FILE
(one path per line; blank lines and # comments ignored).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HUNK = re.compile(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@")


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=repo, capture_output=True, text=True, check=False,
    )
    if check and result.returncode != 0:
        raise SystemExit(f"REFUSED:GIT_FAILED git {' '.join(args)}: {result.stderr.strip()}")
    return result


def file_lines(repo: Path, rev: str, path: str) -> list[str]:
    result = git(repo, "show", f"{rev}:{path}", check=False)
    return result.stdout.splitlines() if result.returncode == 0 else []


def contains_run(haystack: list[str], needle: list[str]) -> bool:
    n = len(needle)
    if n == 0:
        return True
    return any(haystack[i:i + n] == needle for i in range(len(haystack) - n + 1))


def added_hunks(repo: Path, base: str, tip: str) -> dict[str, list[list[str]]]:
    """path -> list of contiguous added-line runs in diff base..tip."""
    out = git(repo, "diff", "-U0", "--no-renames", "--no-color", base, tip).stdout
    hunks: dict[str, list[list[str]]] = {}
    path: str | None = None
    run: list[str] = []

    def flush() -> None:
        nonlocal run
        if run and path is not None:
            hunks.setdefault(path, []).append(run)
        run = []

    for line in out.splitlines():
        if line.startswith("+++ "):
            flush()
            target = line[4:]
            path = target[2:] if target.startswith("b/") else None
        elif line.startswith("--- ") or line.startswith("diff "):
            flush()
        elif line.startswith("@@"):
            flush()
        elif line.startswith("+"):
            run.append(line[1:])
        elif line.startswith("-"):
            flush()
    flush()
    return hunks


def find_drops(repo: Path, merge: str) -> dict[str, list[tuple[str, list[str]]]]:
    parents = git(repo, "rev-list", "--parents", "-n", "1", merge).stdout.split()[1:]
    if len(parents) < 2:
        raise SystemExit(f"REFUSED:NOT_A_MERGE {merge} has {len(parents)} parent(s)")
    merge_sha = git(repo, "rev-parse", merge).stdout.strip()
    drops: dict[str, list[tuple[str, list[str]]]] = {}
    for pi in parents:
        for pj in parents:
            if pi == pj:
                continue
            base = git(repo, "merge-base", pi, pj, check=False).stdout.strip()
            if not base:
                continue
            for path, runs in added_hunks(repo, base, pi).items():
                result = file_lines(repo, merge_sha, path)
                other = file_lines(repo, pj, path)
                for hunk in runs:
                    if not contains_run(result, hunk) and not contains_run(other, hunk):
                        entry = (pi[:12], hunk)
                        if entry not in drops.setdefault(path, []):
                            drops[path].append(entry)
    return drops


def read_allow(path: str | None) -> set[str]:
    if not path:
        return set()
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return {ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("merge_commit")
    parser.add_argument("--repo", default=".", help="repository directory (default: cwd)")
    parser.add_argument("--allow", help="file listing paths whose dropped hunks are accepted")
    args = parser.parse_args()
    repo = Path(args.repo)
    drops = find_drops(repo, args.merge_commit)
    allowed = read_allow(args.allow)
    blocking = {p: d for p, d in drops.items() if p not in allowed}
    for path, entries in sorted(drops.items()):
        tag = "ALLOWED" if path in allowed else "DROPPED"
        for parent, hunk in entries:
            print(f"{tag} {path} (from parent {parent}): {hunk[0]!r}{' ...' if len(hunk) > 1 else ''}")
    if blocking:
        print(f"REFUSED:MERGE_DROPPED_HUNKS files={len(blocking)}", file=sys.stderr)
        return 1
    print(f"merge_guard: ok ({len(drops)} allowed file(s))" if drops else "merge_guard: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
