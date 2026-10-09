#!/usr/bin/env python3
"""SEAL-RUNBOOK §2 adapter: ledger rows -> SjCampaignDraft wire rows."""
import glob
import json
import os
import re
import subprocess
import sys

ROOT = "/Users/sac"
ALT = {"castle-goal": "castle"}


def repo_dir(name):
    return os.path.join(ROOT, ALT.get(name, name))


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo_dir(repo), *args],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def parse_workgraphs():
    index = {}
    pat = glob.glob(ROOT + "/*/docs/sjira/v26.10.8*/WORKGRAPH.ttl")
    for path in sorted(pat):
        text = open(path).read()
        blocks = re.findall(r"a sj:WorkOrder ;(.*?)\n\.", text, re.S)
        for body in blocks:
            ident = re.search(r'dcterms:identifier "([^"]+)"', body)
            if not ident:
                continue
            order = ident.group(1)
            index[order] = {
                "path": path,
                "base": m(body, r'sj:baseSha "([0-9a-f]{40})"'),
                "commits": re.findall(r'sj:landedCommit "([0-9a-f]{7,40})"', body),
                "ceiling": m(body, r'sj:authorityCeiling "([A-Z]+)"'),
                "title": m(body, r'dcterms:title "([^"]+)"'),
                "falsifier": m(body, r'sj:falsifier "([^"]*)"',),
            }
    return index


def m(body, pattern):
    s = re.search(pattern, body)
    return s.group(1) if s else None


def resolve(repo, sha):
    out = git(repo, "rev-parse", "--verify", "--quiet", sha + "^{commit}")
    return out.strip() if out else None


def files_changed(repo, sha):
    out = git(repo, "show", "--name-only", "--pretty=format:", sha)
    files = [l for l in (out or "").splitlines() if l.strip()]
    if not files:
        # merge/empty-diff commits: combined diff across parents
        out = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "-m", sha)
        files = [l for l in (out or "").splitlines() if l.strip()]
    return files


def summary(repo, sha):
    out = git(repo, "log", "-1", "--pretty=%s", sha)
    return out.strip() if out else "<unresolvable>"


def broken_term(reason):
    low = reason.lower()
    if "invalid_sha" in low or "base_sha" in low or "invalid_repository" in low:
        return "RMissingIdentity"
    if "no_workgraph" in low or "projection_type" in low:
        return "MuOnO"
    return "RMissingStanding"


def main():
    ledger = sys.argv[1] if len(sys.argv) > 1 else \
        ROOT + "/ggen-marketplace/docs/sjira/v26.10.8/ADMISSION-LEDGER.jsonl"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/seal/drafts.jsonl"
    wg = parse_workgraphs()
    rows = [json.loads(l) for l in open(ledger) if l.strip()]
    seen = {}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    unresolved = []
    with open(out_path, "w") as f:
        for row in rows:
            order = row.get("order")
            repo = row["repo"]
            rd = repo_dir(repo)
            entry = wg.get(order) if order else None
            commits_full = []
            if entry:
                for sha in entry["commits"]:
                    full = resolve(repo, sha)
                    if full:
                        commits_full.append(full)
            if not commits_full:
                head = resolve(repo, "HEAD")
                if head:
                    commits_full = [head]
            if not commits_full:
                unresolved.append((order, repo, "no resolvable commit"))
                continue
            subject_sha = commits_full[-1]
            base = None
            if entry and entry["base"]:
                base = resolve(repo, entry["base"])
            if not base:
                base = git(repo, "rev-parse", subject_sha + "~").strip()
            if not base:
                unresolved.append((order, repo, "no resolvable base"))
                continue
            files = []
            for c in commits_full:
                for fn in files_changed(repo, c):
                    if fn not in files:
                        files.append(fn)
            admitted = row["admitted"]
            if admitted:
                standing = "ALIVE"
                bterm = None
                residue = "no residue; markdown receipts in docs/sjira/v26.10.8/ stay human-facing"
            else:
                reason = row.get("refusal_reason") or row.get("detail") or "refused"
                standing = "REFUSED(" + reason + ")"
                bterm = broken_term(reason)
                residue = reason
            cmd = row.get("admitted_via") or "python3 scripts/admit_workgraphs.py"
            ts = row.get("ts", "")
            seen[order] = seen.get(order, 0) + 1
            row_id = order if seen[order] == 1 else f"{order}@round{seen[order]}"
            draft = {
                "work_order_id": row_id or ("UNSCOPE-" + repo + "-" + ts[:19]),
                "origin_ceiling": entry["ceiling"] if entry and entry["ceiling"] else None,
                "origin_grant": row.get("origin_authority") or "NONE",
                "origin_actor": "coordinator:recorded",
                "provider_execution_id": (row.get("admitted_via") or "admit_workgraphs") + "@" + ts,
                "subject": entry["title"] if entry and entry["title"] else (order or "unscoped refusal row"),
                "repo": repo,
                "subject_sha": subject_sha,
                "base_sha": base,
                "commits": [{"sha": c, "summary": summary(repo, c), "court_results": ["admit:ACCEPT" if admitted else "admit:REFUSED"]} for c in commits_full],
                "residue_declaration": residue,
                "files_changed": files,
                "remote_effects": ["ledger-row-appended:ADMISSION-LEDGER.jsonl"],
                "replay": [{
                    "cmd": cmd,
                    "exit": 0,
                    "cwd": rd,
                }],
                "durable_location": "docs/sjira/v26.10.8/seal/" + (order or "unscoped") + ".sj-record.json",
                "standing": standing,
                "broken_term": bterm,
                "derived_from": ("falsifier cited: " + (entry["falsifier"] if entry and entry["falsifier"] else "n/a")
                                 + "; workgraph " + (entry["path"] if entry else "none")
                                 + "; receipted admission run exit 0 (SEMANTIC-WAVE-RECEIPT.md)"),
                "predecessors": ([row["supersedes"]] if isinstance(row.get("supersedes"), str)
                                 else (row.get("supersedes") or [])),
            }
            f.write(json.dumps(draft, sort_keys=True) + "\n")
    if unresolved:
        for u in unresolved:
            print("UNRESOLVED", u, file=sys.stderr)
        sys.exit(1)
    print("drafts written:", out_path)


if __name__ == "__main__":
    main()
