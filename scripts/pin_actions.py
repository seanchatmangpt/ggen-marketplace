#!/usr/bin/env python3
"""Supply-chain hygiene for GitHub workflows: SHA-pin every `uses:` reference.

  pin_actions.py --check   list unpinned `uses:` refs; exit 1 if any
  pin_actions.py --apply   resolve ref -> commit SHA via `gh api` and rewrite
                           the line as `uses: o/r@<sha> # <ref>`

Exempt: local `./` paths and `docker://` references. Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
USES_RE = re.compile(r"^(?P<pre>\s*(?:-\s+)?uses:\s*)(?P<q>['\"]?)(?P<ref>[^\s'\"#]+)(?P=q)(?P<post>\s*(?:#.*)?)$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def parse_ref(value: str):
    """Return (repo_path, ref) or None when exempt/unparseable."""
    if value.startswith("./") or value.startswith("docker://") or "@" not in value:
        return None
    target, ref = value.rsplit("@", 1)
    return target, ref


def scan(workflows: Path = WORKFLOWS):
    """Yield (path, lineno, match, target, ref) for every unpinned uses: line."""
    for path in sorted(workflows.glob("*.y*ml")):
        for no, line in enumerate(path.read_text().splitlines(), 1):
            m = USES_RE.match(line)
            if not m:
                continue
            parsed = parse_ref(m.group("ref"))
            if parsed is None or SHA_RE.match(parsed[1]):
                continue
            yield path, no, m, parsed[0], parsed[1]


def resolve(target: str, ref: str) -> str | None:
    owner, repo = target.split("/")[:2]
    r = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/commits/{ref}", "--jq", ".sha"],
        capture_output=True, text=True,
    )
    sha = r.stdout.strip()
    return sha if r.returncode == 0 and SHA_RE.match(sha) else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    ap.add_argument("--workflows", type=Path, default=WORKFLOWS)
    args = ap.parse_args(argv)

    found = list(scan(args.workflows))
    if args.check:
        for path, no, _m, target, ref in found:
            print(f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}:{no}: {target}@{ref} is not SHA-pinned")
        print(f"{len(found)} unpinned uses: reference(s)")
        return 1 if found else 0

    cache: dict[tuple[str, str], str | None] = {}
    blocked: list[str] = []
    edits: dict[Path, dict[int, str]] = {}
    for path, no, m, target, ref in found:
        key = (target.split("/")[0] + "/" + target.split("/")[1], ref)
        if key not in cache:
            cache[key] = resolve(*key)
        sha = cache[key]
        if sha is None:
            blocked.append(f"{path.name}:{no}: {target}@{ref}")
            continue
        edits.setdefault(path, {})[no] = f"{m.group('pre')}{target}@{sha} # {ref}"
    for path, per in edits.items():
        lines = path.read_text().split("\n")
        for no, new in per.items():
            lines[no - 1] = new
        path.write_text("\n".join(lines))
    print(f"pinned {sum(len(v) for v in edits.values())} reference(s) in {len(edits)} file(s)")
    for b in blocked:
        print(f"BLOCKED: {b}", file=sys.stderr)
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
