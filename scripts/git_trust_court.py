#!/usr/bin/env python3
"""git-trust-root court: resolve every 40-hex SHA cited in fleet WORKGRAPH.ttl files.

For each workgraph (WORKGRAPH.ttl) the court:
  1. extracts every 40-hex SHA literal (sj:baseSha literals, prov:wasDerivedFrom
     / rdfs:seeAlso citation IRIs, and any other 40-hex string on a cited line),
  2. resolves each SHA in the OWNING repo via `git -C <repo> cat-file -t`,
  3. checks ancestry against the repo's pushed default branch (trust root) via
     `git merge-base --is-ancestor <sha> origin/HEAD`.

Verdicts per SHA:
  RESOLVED-ROOTED   object exists and is an ancestor of the default branch
  RESOLVED-UNROOTED object exists but is NOT an ancestor of the default branch
  UNRESOLVED        object does not exist in the owning repo (pseudo-SHA)

Usage:
  python3 scripts/git_trust_court.py --fleet ~/ggen-marketplace/docs/sjira/v26.10.8/WORKGRAPH.ttl ... [--json OUT]
  python3 scripts/git_trust_court.py --file <repo>/WORKGRAPH.ttl
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HEX40 = re.compile(r"\b[0-9a-f]{40}\b")

# citation predicates: only SHAs on a line carrying one of these count as citations;
# 40-hex strings inside dcterms:description prose are not citations.
CITATION_PREDICATE = re.compile(
    r"(sj:baseSha|sj:landedCommit|sj:subjectSha|prov:wasDerivedFrom|rdfs:seeAlso)"
)
# vendored gitlink citation inside acceptance prose: `vendor/<name> <sha>`
VENDOR_GITLINK = re.compile(r"\bvendor/([\w-]+)\s+([0-9a-f]{40})")

# citation IRI forms that embed owner/repo/commit/<sha>
COMMIT_IRI = re.compile(
    r"https?://[^/\s\"]+/([^/\s\"]+)/([^/\s\"]+)/(?:commit|blob|tree)/([0-9a-f]{7,40})"
)
REPO_LITERAL = re.compile(r"sj:repository\s+\"([^\"]+)\"")

DEFAULT_BRANCH_CACHE: dict[str, str] = {}


def run(args: list[str], cwd: str | None = None) -> tuple[int, str]:
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def default_branch(repo_path: str) -> str | None:
    if repo_path in DEFAULT_BRANCH_CACHE:
        return DEFAULT_BRANCH_CACHE[repo_path]
    rc, out = run(["git", "-C", repo_path, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD"])
    branch = out.strip() if rc == 0 else None
    if branch:
        branch = branch.removeprefix("origin/")
    if not branch:
        # fallback: remote HEAD badge
        rc, out = run(["git", "-C", repo_path, "remote", "show", "origin"])
        m = re.search(r"HEAD branch:\s*(\S+)", out)
        branch = m.group(1) if m else None
    DEFAULT_BRANCH_CACHE[repo_path] = branch
    return branch


def local_repo(owner_slash_name: str) -> Path | None:
    name = owner_slash_name.split("/")[-1]
    p = Path.home() / name
    return p if (p / ".git").exists() or (p / ".git").is_file() else None


def extract_shas(ttl_text: str) -> list[dict]:
    """Return [{sha, repo_hint, line_no, context}] for every 40-hex SHA."""
    found: list[dict] = []
    repo_hint = None
    for line_no, line in enumerate(ttl_text.splitlines(), 1):
        m = REPO_LITERAL.search(line)
        if m:
            repo_hint = m.group(1)
        # a commit IRI names its own repo — that wins over the last-seen sj:repository
        ci = COMMIT_IRI.search(line)
        line_repo = ci.group(2) if ci else None
        cited = bool(CITATION_PREDICATE.search(line))
        for hm in HEX40.finditer(line):
            if not (cited or line_repo):
                continue  # bare prose SHA, not a citation
            found.append(
                {
                    "sha": hm.group(0),
                    "repo_hint": line_repo or repo_hint,
                    "line_no": line_no,
                    "context": line.strip()[:160],
                }
            )
        for vm in VENDOR_GITLINK.finditer(line):
            found.append(
                {
                    "sha": vm.group(2),
                    "repo_hint": vm.group(1),
                    "line_no": line_no,
                    "context": ("vendor gitlink: " + line.strip())[:160],
                }
            )
    return found


def court_one(sha: str, repo_path: str | None, branch: str | None) -> tuple[str, str]:
    """Return (verdict, detail)."""
    if repo_path is None:
        return "UNRESOLVED", "no local checkout for owning repo"
    rc, out = run(["git", "-C", repo_path, "cat-file", "-t", sha])
    if rc != 0:
        return "UNRESOLVED", f"cat-file: {out.splitlines()[0] if out else 'not found'}"
    obj_type = out.splitlines()[0]
    if branch is None:
        return "RESOLVED-UNROOTED", f"type={obj_type}; no default branch on remote"
    rc, _ = run(["git", "-C", repo_path, "merge-base", "--is-ancestor", sha, f"origin/{branch}"])
    verdict = "RESOLVED-ROOTED" if rc == 0 else "RESOLVED-UNROOTED"
    return verdict, f"type={obj_type}; vs origin/{branch}"


def court_workgraph(wg_path: Path) -> dict:
    text = wg_path.read_text()
    # owning repo of the workgraph itself = first path component of docs/sjira parent
    wg_repo = wg_path.parent.parent.parent.parent.name
    repo_hint = None
    m = REPO_LITERAL.search(text)
    shas = extract_shas(text)
    results = []
    seen = set()
    for s in shas:
        key = (s["sha"], s["repo_hint"] or wg_repo)
        if key in seen:
            continue
        seen.add(key)
        owner = s["repo_hint"] or f"x/{wg_repo}"
        local = local_repo(owner)
        branch = default_branch(str(local)) if local else None
        verdict, detail = court_one(s["sha"], str(local) if local else None, branch)
        results.append(
            {
                "sha": s["sha"],
                "owning_repo": owner,
                "local_path": str(local) if local else None,
                "line_no": s["line_no"],
                "context": s["context"],
                "verdict": verdict,
                "detail": detail,
            }
        )
    return {
        "workgraph": str(wg_path),
        "repo": wg_repo,
        "sha_count": len(results),
        "results": results,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", action="append", default=[], help="WORKGRAPH.ttl path (repeatable)")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args()

    if not args.file:
        print("no --file given", file=sys.stderr)
        return 2

    reports = [court_workgraph(Path(f)) for f in args.file]
    totals = {"RESOLVED-ROOTED": 0, "RESOLVED-UNROOTED": 0, "UNRESOLVED": 0}
    for r in reports:
        for x in r["results"]:
            totals[x["verdict"]] += 1

    out = {"totals": totals, "workgraphs": reports}
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(out, indent=2) + "\n")
    else:
        print(json.dumps(out, indent=2))

    print(
        f"\nCOURT VERDICT: {totals['RESOLVED-ROOTED']} RESOLVED-ROOTED, "
        f"{totals['RESOLVED-UNROOTED']} RESOLVED-UNROOTED, "
        f"{totals['UNRESOLVED']} UNRESOLVED "
        f"across {len(reports)} workgraphs",
        file=sys.stderr,
    )
    return 0 if totals["UNRESOLVED"] == 0 else 1


if __name__ == "__main__":
    main()
